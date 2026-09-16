import Matter from "matter-js";
import type { BuildEditor } from "./editor";
import { MATERIALS } from "./materials";
import { VEHICLES } from "./vehicles";
import type { MaterialId, SimResult, VehicleType } from "./types";

const { Engine, World, Bodies, Body, Constraint, Composite, Vector } = Matter;

const CAT_TERRAIN = 0x0001;
const CAT_JOINT = 0x0002;
const CAT_ROAD = 0x0004;
const CAT_VEHICLE = 0x0008;

const ROAD_PIN_MAX_STRETCH = 24;
const VEHICLE_SPAWN_OFFSET_X = 70;
const VEHICLE_CROSS_MARGIN = 30;
const SIM_TIMEOUT_MS = 45000;
const GRAVITY_Y = 1.05;

interface StructConstraint {
  beamId: string;
  material: MaterialId;
  constraint: Matter.Constraint;
  restLength: number;
  broken: boolean;
}

interface RoadPlank {
  beamId: string;
  body: Matter.Body;
  pinA: Matter.Constraint;
  pinB: Matter.Constraint;
  broken: boolean;
}

interface ScheduledSpawn {
  type: VehicleType;
  atMs: number;
}

interface VehicleInstance {
  type: VehicleType;
  chassis: Matter.Body;
  wheels: Matter.Body[];
  crossed: boolean;
  removed: boolean;
}

export interface SimCallbacks {
  onBeamBroken?: (beamId: string) => void;
  onVehicleSpawned?: (index: number, total: number) => void;
  onVehicleCrossed?: (index: number, total: number) => void;
  onCollapse?: () => void;
  onEnd?: (result: SimResult) => void;
}

export class Simulation {
  readonly editor: BuildEditor;
  readonly engine: Matter.Engine;
  readonly callbacks: SimCallbacks;

  private nodeBodies = new Map<string, Matter.Body>();
  private structConstraints: StructConstraint[] = [];
  private roadPlanks: RoadPlank[] = [];
  private schedule: ScheduledSpawn[] = [];
  private vehicles: VehicleInstance[] = [];
  private spawnCursor = 0;
  private elapsedMs = 0;
  private finished = false;
  private crossedCount = 0;

  constructor(editor: BuildEditor, callbacks: SimCallbacks = {}) {
    this.editor = editor;
    this.callbacks = callbacks;
    this.engine = Engine.create();
    this.engine.gravity.y = GRAVITY_Y;
    this.buildTerrain();
    this.buildStructure();
    this.schedule = buildSchedule(editor.level);
  }

  get totalVehicles(): number {
    return this.schedule.length;
  }

  private buildTerrain(): void {
    const { world } = this.editor;
    const thickness = 400;
    const leftCliff = Bodies.rectangle(
      world.leftAnchor.x - thickness / 2 + 24,
      world.leftAnchor.y + thickness / 2,
      thickness,
      thickness,
      { isStatic: true, friction: 0.95, collisionFilter: { category: CAT_TERRAIN, mask: CAT_ROAD | CAT_VEHICLE } },
    );
    const rightCliff = Bodies.rectangle(
      world.rightAnchor.x + thickness / 2 - 24,
      world.rightAnchor.y + thickness / 2,
      thickness,
      thickness,
      { isStatic: true, friction: 0.95, collisionFilter: { category: CAT_TERRAIN, mask: CAT_ROAD | CAT_VEHICLE } },
    );
    World.add(this.engine.world, [leftCliff, rightCliff]);
  }

  private buildStructure(): void {
    for (const node of this.editor.nodes.values()) {
      const isAnchor = node.kind === "anchor";
      const body = Bodies.circle(node.x, node.y, isAnchor ? 10 : 7, {
        isStatic: isAnchor,
        friction: 0.6,
        frictionAir: 0.01,
        density: 0.0025,
        collisionFilter: { category: CAT_JOINT, mask: 0 },
      });
      this.nodeBodies.set(node.id, body);
      World.add(this.engine.world, body);
    }

    for (const beam of this.editor.beams.values()) {
      const bodyA = this.nodeBodies.get(beam.nodeA);
      const bodyB = this.nodeBodies.get(beam.nodeB);
      if (!bodyA || !bodyB) continue;
      const restLength = Vector.magnitude(Vector.sub(bodyB.position, bodyA.position));

      if (beam.material === "road") {
        this.addRoadPlank(beam.id, bodyA, bodyB, restLength);
      } else {
        const constraint = Constraint.create({
          bodyA,
          bodyB,
          length: restLength,
          stiffness: 0.9,
          damping: 0.18,
        });
        World.add(this.engine.world, constraint);
        this.structConstraints.push({
          beamId: beam.id,
          material: beam.material,
          constraint,
          restLength,
          broken: false,
        });
      }
    }
  }

  private addRoadPlank(beamId: string, bodyA: Matter.Body, bodyB: Matter.Body, length: number): void {
    const mid = Vector.mult(Vector.add(bodyA.position, bodyB.position), 0.5);
    const angle = Math.atan2(bodyB.position.y - bodyA.position.y, bodyB.position.x - bodyA.position.x);
    const plank = Bodies.rectangle(mid.x, mid.y, length, MATERIALS.road.thickness, {
      angle,
      friction: 0.85,
      density: MATERIALS.road.density,
      collisionFilter: { category: CAT_ROAD, mask: CAT_TERRAIN | CAT_VEHICLE | CAT_ROAD },
    });
    const half = length / 2;
    const pinA = Constraint.create({
      bodyA,
      bodyB: plank,
      pointB: { x: -half, y: 0 },
      length: 0,
      stiffness: 0.85,
      damping: 0.2,
    });
    const pinB = Constraint.create({
      bodyA: bodyB,
      bodyB: plank,
      pointB: { x: half, y: 0 },
      length: 0,
      stiffness: 0.85,
      damping: 0.2,
    });
    World.add(this.engine.world, [plank, pinA, pinB]);
    this.roadPlanks.push({ beamId, body: plank, pinA, pinB, broken: false });
  }

  private spawnVehicle(type: VehicleType): void {
    const def = VEHICLES[type];
    const { world } = this.editor;
    const startX = world.leftAnchor.x - VEHICLE_SPAWN_OFFSET_X;
    const startY = world.groundTopY - 120;

    const chassis = Bodies.rectangle(startX, startY, def.width, def.height, {
      density: def.weight / (def.width * def.height),
      friction: 0.4,
      frictionAir: 0.015,
      collisionFilter: { category: CAT_VEHICLE, mask: CAT_TERRAIN | CAT_ROAD | CAT_VEHICLE },
    });

    const wheelOffsetX = def.width / 2 - def.wheelRadius * 0.9;
    const wheels = [-1, 1].map((side) =>
      Bodies.circle(startX + side * wheelOffsetX, startY + def.height / 2, def.wheelRadius, {
        density: (def.weight * 0.15) / (Math.PI * def.wheelRadius * def.wheelRadius),
        friction: 1.1,
        frictionAir: 0.015,
        collisionFilter: { category: CAT_VEHICLE, mask: CAT_TERRAIN | CAT_ROAD | CAT_VEHICLE },
      }),
    );

    const axles = wheels.map((wheel, i) =>
      Constraint.create({
        bodyA: chassis,
        bodyB: wheel,
        pointA: { x: (i === 0 ? -1 : 1) * wheelOffsetX, y: def.height / 2 },
        stiffness: 1,
        length: 0,
      }),
    );

    World.add(this.engine.world, [chassis, ...wheels, ...axles]);
    this.vehicles.push({ type, chassis, wheels, crossed: false, removed: false });
  }

  /** Avance la simulation d'un pas fixe (ms). Retourne false une fois terminée. */
  step(deltaMs: number): boolean {
    if (this.finished) return false;
    this.elapsedMs += deltaMs;
    Engine.update(this.engine, deltaMs);
    this.processSpawns();
    this.driveVehicles();
    this.checkBreakage();
    this.checkVictoryAndFailure();
    return !this.finished;
  }

  private processSpawns(): void {
    while (this.spawnCursor < this.schedule.length && this.schedule[this.spawnCursor].atMs <= this.elapsedMs) {
      const spawn = this.schedule[this.spawnCursor];
      this.spawnVehicle(spawn.type);
      this.callbacks.onVehicleSpawned?.(this.spawnCursor + 1, this.schedule.length);
      this.spawnCursor += 1;
    }
  }

  private driveVehicles(): void {
    for (const vehicle of this.vehicles) {
      if (vehicle.removed) continue;
      const def = VEHICLES[vehicle.type];
      for (const wheel of vehicle.wheels) {
        const targetAngular = def.speed;
        Body.setAngularVelocity(wheel, targetAngular);
      }
      Body.applyForce(vehicle.chassis, vehicle.chassis.position, { x: def.weight * 0.000045, y: 0 });
    }
  }

  private checkBreakage(): void {
    for (const sc of this.structConstraints) {
      if (sc.broken) continue;
      const posA = Vector.add(sc.constraint.bodyA!.position, sc.constraint.pointA ?? { x: 0, y: 0 });
      const posB = Vector.add(sc.constraint.bodyB!.position, sc.constraint.pointB ?? { x: 0, y: 0 });
      const current = Vector.magnitude(Vector.sub(posB, posA));
      const strain = (current - sc.restLength) / sc.restLength;
      const limit = MATERIALS[sc.material].maxForce;
      const overLimit = MATERIALS[sc.material].cableOnly ? strain > limit : Math.abs(strain) > limit;
      if (overLimit) {
        sc.broken = true;
        World.remove(this.engine.world, sc.constraint);
        this.callbacks.onBeamBroken?.(sc.beamId);
      }
    }

    for (const plank of this.roadPlanks) {
      if (plank.broken) continue;
      const stretchA = pinStretch(plank.pinA);
      const stretchB = pinStretch(plank.pinB);
      if (stretchA > ROAD_PIN_MAX_STRETCH || stretchB > ROAD_PIN_MAX_STRETCH) {
        plank.broken = true;
        World.remove(this.engine.world, [plank.pinA, plank.pinB]);
        this.callbacks.onBeamBroken?.(plank.beamId);
      }
    }
  }

  private checkVictoryAndFailure(): void {
    if (this.finished) return;
    const { world } = this.editor;

    for (const vehicle of this.vehicles) {
      if (vehicle.removed) continue;
      if (vehicle.chassis.position.y > world.failY) {
        this.endSimulation(false);
        this.callbacks.onCollapse?.();
        return;
      }
      if (!vehicle.crossed && vehicle.chassis.position.x > world.rightAnchor.x + VEHICLE_CROSS_MARGIN) {
        vehicle.crossed = true;
        this.crossedCount += 1;
        this.callbacks.onVehicleCrossed?.(this.crossedCount, this.schedule.length);
      }
    }

    if (this.crossedCount >= this.schedule.length && this.schedule.length > 0) {
      this.endSimulation(true);
      return;
    }

    if (this.elapsedMs > SIM_TIMEOUT_MS) {
      this.endSimulation(false);
    }
  }

  private endSimulation(success: boolean): void {
    this.finished = true;
    const spent = this.editor.spent;
    const total = this.editor.level.budget;
    const spentFraction = total > 0 ? spent / total : 1;
    const [tierThree, tierTwo] = this.editor.level.starBudgetBonus;
    let stars: 0 | 1 | 2 | 3 = 0;
    if (success) {
      stars = spentFraction <= tierThree ? 3 : spentFraction <= tierTwo ? 2 : 1;
    }
    const result: SimResult = {
      success,
      vehiclesCrossed: this.crossedCount,
      vehiclesTotal: this.schedule.length,
      budgetSpent: spent,
      budgetTotal: total,
      stars,
    };
    this.callbacks.onEnd?.(result);
  }

  getRenderState() {
    return {
      nodeBodies: this.nodeBodies,
      structConstraints: this.structConstraints,
      roadPlanks: this.roadPlanks,
      vehicles: this.vehicles,
    };
  }

  destroy(): void {
    Composite.clear(this.engine.world, false);
    Engine.clear(this.engine);
  }
}

function pinStretch(pin: Matter.Constraint): number {
  const bodyA = pin.bodyA;
  const bodyB = pin.bodyB;
  if (!bodyA || !bodyB) return 0;
  const worldPointA = Vector.add(bodyA.position, rotatePoint(pin.pointA ?? { x: 0, y: 0 }, bodyA.angle));
  const worldPointB = Vector.add(bodyB.position, rotatePoint(pin.pointB ?? { x: 0, y: 0 }, bodyB.angle));
  return Vector.magnitude(Vector.sub(worldPointB, worldPointA));
}

function rotatePoint(point: Matter.Vector, angle: number): Matter.Vector {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return { x: point.x * cos - point.y * sin, y: point.x * sin + point.y * cos };
}

function buildSchedule(level: BuildEditor["level"]): ScheduledSpawn[] {
  const schedule: ScheduledSpawn[] = [];
  let t = 0;
  for (const wave of level.waves) {
    for (let i = 0; i < wave.count; i++) {
      if (schedule.length > 0) t += wave.gapMs;
      schedule.push({ type: wave.type, atMs: t });
    }
  }
  return schedule;
}
