import Matter from "matter-js";
import type { BuildEditor } from "./editor";
import { MATERIALS } from "./materials";
import type { Simulation } from "./simulation";
import { VEHICLES } from "./vehicles";
import type { EditorNode, MaterialId, VehicleType } from "./types";
import { Camera, type WorldGeometry } from "./world";

export interface BuildHoverState {
  hoverNode: EditorNode | null;
  dragFrom: EditorNode | null;
  cursorWorld: { x: number; y: number } | null;
  activeMaterial: MaterialId;
  invalidDrag: boolean;
}

const SKY_TOP = "#bfe3f5";
const SKY_BOTTOM = "#eef8ff";
const CLIFF_COLOR = "#7d6a52";
const CLIFF_TOP_COLOR = "#5f8a4a";
const RAVINE_COLOR = "#2a3d52";

export function drawBackground(ctx: CanvasRenderingContext2D, camera: Camera, world: WorldGeometry, canvasW: number, canvasH: number): void {
  const gradient = ctx.createLinearGradient(0, 0, 0, canvasH);
  gradient.addColorStop(0, SKY_TOP);
  gradient.addColorStop(1, SKY_BOTTOM);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvasW, canvasH);

  const ravineGradient = ctx.createLinearGradient(0, camera.toScreenY(world.groundTopY), 0, camera.toScreenY(world.failY + 100));
  ravineGradient.addColorStop(0, "#3c5570");
  ravineGradient.addColorStop(1, RAVINE_COLOR);
  ctx.fillStyle = ravineGradient;
  ctx.fillRect(
    camera.toScreenX(world.leftAnchor.x),
    camera.toScreenY(Math.min(world.leftAnchor.y, world.rightAnchor.y)),
    camera.toScreenX(world.rightAnchor.x) - camera.toScreenX(world.leftAnchor.x),
    canvasH,
  );

  drawCliff(ctx, camera, 0, world.leftAnchor.y, world.leftAnchor.x, canvasH);
  drawCliff(ctx, camera, world.rightAnchor.x, world.rightAnchor.y, world.width - world.rightAnchor.x, canvasH);
}

function drawCliff(ctx: CanvasRenderingContext2D, camera: Camera, x: number, topY: number, width: number, canvasH: number): void {
  const sx = camera.toScreenX(x);
  const sy = camera.toScreenY(topY);
  const sw = width * camera.scale;
  ctx.fillStyle = CLIFF_COLOR;
  ctx.fillRect(sx, sy, sw, canvasH - sy);
  ctx.fillStyle = CLIFF_TOP_COLOR;
  ctx.fillRect(sx, sy, sw, 10 * camera.scale);
}

export function drawBuildMode(
  ctx: CanvasRenderingContext2D,
  camera: Camera,
  editor: BuildEditor,
  hover: BuildHoverState,
): void {
  for (const beam of editor.beams.values()) {
    const a = editor.nodes.get(beam.nodeA);
    const b = editor.nodes.get(beam.nodeB);
    if (!a || !b) continue;
    drawBeamLine(ctx, camera, a, b, beam.material, 1);
  }

  if (hover.dragFrom && hover.cursorWorld) {
    ctx.save();
    ctx.globalAlpha = 0.55;
    drawBeamLine(
      ctx,
      camera,
      hover.dragFrom,
      { ...hover.dragFrom, x: hover.cursorWorld.x, y: hover.cursorWorld.y },
      hover.activeMaterial,
      1,
      hover.invalidDrag ? "#e74c3c" : undefined,
    );
    ctx.restore();
  }

  for (const node of editor.nodes.values()) {
    drawNode(ctx, camera, node, hover.hoverNode?.id === node.id);
  }
}

function drawBeamLine(
  ctx: CanvasRenderingContext2D,
  camera: Camera,
  a: { x: number; y: number },
  b: { x: number; y: number },
  material: MaterialId,
  opacity: number,
  overrideColor?: string,
): void {
  const mat = MATERIALS[material];
  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.strokeStyle = overrideColor ?? mat.color;
  ctx.lineWidth = Math.max(2, mat.thickness * camera.scale * 0.6);
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(camera.toScreenX(a.x), camera.toScreenY(a.y));
  ctx.lineTo(camera.toScreenX(b.x), camera.toScreenY(b.y));
  ctx.stroke();
  ctx.restore();
}

function drawNode(ctx: CanvasRenderingContext2D, camera: Camera, node: EditorNode, hovered: boolean): void {
  const x = camera.toScreenX(node.x);
  const y = camera.toScreenY(node.y);
  const r = (node.kind === "anchor" ? 9 : 6) * Math.max(camera.scale, 0.6);
  ctx.beginPath();
  ctx.arc(x, y, hovered ? r * 1.4 : r, 0, Math.PI * 2);
  ctx.fillStyle = node.kind === "anchor" ? "#3a3a3a" : hovered ? "#ffe082" : "#f5f5f5";
  ctx.strokeStyle = "#2a2a2a";
  ctx.lineWidth = 1.5;
  ctx.fill();
  ctx.stroke();
}

export function drawSimulation(ctx: CanvasRenderingContext2D, camera: Camera, simulation: Simulation): void {
  const state = simulation.getRenderState();

  for (const sc of state.structConstraints) {
    if (sc.broken) continue;
    const bodyA = sc.constraint.bodyA!;
    const bodyB = sc.constraint.bodyB!;
    drawBeamLine(ctx, camera, bodyA.position, bodyB.position, sc.material, 1);
  }

  for (const plank of state.roadPlanks) {
    drawPlank(ctx, camera, plank.body);
  }

  for (const [, body] of state.nodeBodies) {
    const x = camera.toScreenX(body.position.x);
    const y = camera.toScreenY(body.position.y);
    ctx.beginPath();
    ctx.arc(x, y, 5 * Math.max(camera.scale, 0.6), 0, Math.PI * 2);
    ctx.fillStyle = "#3a3a3a";
    ctx.fill();
  }

  for (const vehicle of state.vehicles) {
    drawVehicle(ctx, camera, vehicle);
  }
}

function drawPlank(ctx: CanvasRenderingContext2D, camera: Camera, body: Matter.Body): void {
  const mat = MATERIALS.road;
  const w = mat.thickness;
  ctx.save();
  ctx.translate(camera.toScreenX(body.position.x), camera.toScreenY(body.position.y));
  ctx.rotate(body.angle);
  const length = Matter.Vector.magnitude(
    Matter.Vector.sub(body.vertices[1], body.vertices[0]),
  );
  ctx.fillStyle = mat.color;
  ctx.fillRect((-length / 2) * camera.scale, (-w / 2) * camera.scale, length * camera.scale, w * camera.scale);
  ctx.fillStyle = "#2f2f36";
  for (let i = -length / 2 + 8; i < length / 2; i += 22) {
    ctx.fillRect(i * camera.scale, (-w / 2) * camera.scale, 3 * camera.scale, w * camera.scale);
  }
  ctx.restore();
}

function drawVehicle(ctx: CanvasRenderingContext2D, camera: Camera, vehicle: { type: VehicleType; chassis: Matter.Body; wheels: Matter.Body[] }): void {
  const def = VEHICLES[vehicle.type];
  for (const wheel of vehicle.wheels) {
    const x = camera.toScreenX(wheel.position.x);
    const y = camera.toScreenY(wheel.position.y);
    ctx.beginPath();
    ctx.arc(x, y, def.wheelRadius * camera.scale, 0, Math.PI * 2);
    ctx.fillStyle = "#222";
    ctx.fill();
  }

  ctx.save();
  ctx.translate(camera.toScreenX(vehicle.chassis.position.x), camera.toScreenY(vehicle.chassis.position.y));
  ctx.rotate(vehicle.chassis.angle);
  ctx.fillStyle = def.color;
  ctx.fillRect((-def.width / 2) * camera.scale, (-def.height / 2) * camera.scale, def.width * camera.scale, def.height * camera.scale);
  ctx.fillStyle = "rgba(255,255,255,0.35)";
  ctx.fillRect((-def.width / 2) * camera.scale, (-def.height / 2) * camera.scale, def.width * camera.scale, def.height * 0.35 * camera.scale);
  ctx.restore();
}
