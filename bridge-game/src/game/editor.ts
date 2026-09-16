import { MATERIALS } from "./materials";
import type { EditorBeam, EditorNode, LevelDef, MaterialId, NodeKind } from "./types";
import { computeWorldGeometry, snap, type WorldGeometry } from "./world";

let idCounter = 0;
function nextId(prefix: string): string {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
}

export const MIN_BEAM_LENGTH = 24;
export const JOINT_HIT_RADIUS = 16;
export const BEAM_HIT_TOLERANCE = 10;

export class BuildEditor {
  readonly level: LevelDef;
  readonly world: WorldGeometry;
  nodes = new Map<string, EditorNode>();
  beams = new Map<string, EditorBeam>();
  leftAnchorId: string;
  rightAnchorId: string;

  constructor(level: LevelDef) {
    this.level = level;
    this.world = computeWorldGeometry(level);
    const left: EditorNode = { id: nextId("anchor"), x: this.world.leftAnchor.x, y: this.world.leftAnchor.y, kind: "anchor" };
    const right: EditorNode = { id: nextId("anchor"), x: this.world.rightAnchor.x, y: this.world.rightAnchor.y, kind: "anchor" };
    this.nodes.set(left.id, left);
    this.nodes.set(right.id, right);
    this.leftAnchorId = left.id;
    this.rightAnchorId = right.id;
  }

  get spent(): number {
    let total = 0;
    for (const beam of this.beams.values()) total += this.beamCost(beam);
    return Math.round(total);
  }

  get remaining(): number {
    return this.level.budget - this.spent;
  }

  beamLength(beam: EditorBeam): number {
    const a = this.nodes.get(beam.nodeA);
    const b = this.nodes.get(beam.nodeB);
    if (!a || !b) return 0;
    return Math.hypot(b.x - a.x, b.y - a.y);
  }

  beamCost(beam: EditorBeam): number {
    const mat = MATERIALS[beam.material];
    return (this.beamLength(beam) / 100) * mat.costPerLength;
  }

  isWithinBuildZone(x: number, y: number): boolean {
    const minY = this.world.groundTopY - 240;
    const maxY = this.world.failY - 20;
    return x >= 20 && x <= this.world.width - 20 && y >= minY && y <= maxY;
  }

  findNodeAt(x: number, y: number, radius = JOINT_HIT_RADIUS): EditorNode | null {
    let best: EditorNode | null = null;
    let bestDist = radius;
    for (const node of this.nodes.values()) {
      const d = Math.hypot(node.x - x, node.y - y);
      if (d <= bestDist) {
        best = node;
        bestDist = d;
      }
    }
    return best;
  }

  findBeamAt(x: number, y: number, tolerance = BEAM_HIT_TOLERANCE): EditorBeam | null {
    let best: EditorBeam | null = null;
    let bestDist = tolerance;
    for (const beam of this.beams.values()) {
      const a = this.nodes.get(beam.nodeA);
      const b = this.nodes.get(beam.nodeB);
      if (!a || !b) continue;
      const d = distanceToSegment(x, y, a.x, a.y, b.x, b.y);
      if (d <= bestDist) {
        best = beam;
        bestDist = d;
      }
    }
    return best;
  }

  addJoint(x: number, y: number, kind: NodeKind = "joint"): EditorNode {
    const sx = snap(x);
    const sy = snap(y);
    const node: EditorNode = { id: nextId("joint"), x: sx, y: sy, kind };
    this.nodes.set(node.id, node);
    return node;
  }

  beamExists(nodeA: string, nodeB: string, material: MaterialId): boolean {
    for (const beam of this.beams.values()) {
      const sameEnds =
        (beam.nodeA === nodeA && beam.nodeB === nodeB) || (beam.nodeA === nodeB && beam.nodeB === nodeA);
      if (sameEnds && beam.material === material) return true;
    }
    return false;
  }

  canAffordBeam(nodeA: EditorNode, nodeB: EditorNode, material: MaterialId): boolean {
    const length = Math.hypot(nodeB.x - nodeA.x, nodeB.y - nodeA.y);
    const cost = (length / 100) * MATERIALS[material].costPerLength;
    return cost <= this.remaining + 0.001;
  }

  addBeam(nodeAId: string, nodeBId: string, material: MaterialId): EditorBeam | null {
    if (nodeAId === nodeBId) return null;
    const a = this.nodes.get(nodeAId);
    const b = this.nodes.get(nodeBId);
    if (!a || !b) return null;
    const length = Math.hypot(b.x - a.x, b.y - a.y);
    if (length < MIN_BEAM_LENGTH) return null;
    if (this.beamExists(nodeAId, nodeBId, material)) return null;
    if (!this.canAffordBeam(a, b, material)) return null;
    const beam: EditorBeam = { id: nextId("beam"), nodeA: nodeAId, nodeB: nodeBId, material };
    this.beams.set(beam.id, beam);
    return beam;
  }

  removeBeam(id: string): void {
    this.beams.delete(id);
  }

  removeNode(id: string): void {
    const node = this.nodes.get(id);
    if (!node || node.kind === "anchor") return;
    this.nodes.delete(id);
    for (const [beamId, beam] of this.beams) {
      if (beam.nodeA === id || beam.nodeB === id) this.beams.delete(beamId);
    }
  }

  /** Vérifie qu'un chemin continu de route relie les deux ancrages. */
  isRoadConnected(): boolean {
    const adjacency = new Map<string, string[]>();
    for (const beam of this.beams.values()) {
      if (beam.material !== "road") continue;
      if (!adjacency.has(beam.nodeA)) adjacency.set(beam.nodeA, []);
      if (!adjacency.has(beam.nodeB)) adjacency.set(beam.nodeB, []);
      adjacency.get(beam.nodeA)!.push(beam.nodeB);
      adjacency.get(beam.nodeB)!.push(beam.nodeA);
    }
    const visited = new Set<string>([this.leftAnchorId]);
    const queue = [this.leftAnchorId];
    while (queue.length) {
      const current = queue.shift()!;
      if (current === this.rightAnchorId) return true;
      for (const next of adjacency.get(current) ?? []) {
        if (!visited.has(next)) {
          visited.add(next);
          queue.push(next);
        }
      }
    }
    return visited.has(this.rightAnchorId);
  }

  hasAnyStructure(): boolean {
    return this.beams.size > 0;
  }
}

function distanceToSegment(px: number, py: number, ax: number, ay: number, bx: number, by: number): number {
  const dx = bx - ax;
  const dy = by - ay;
  const lengthSq = dx * dx + dy * dy;
  let t = lengthSq === 0 ? 0 : ((px - ax) * dx + (py - ay) * dy) / lengthSq;
  t = Math.max(0, Math.min(1, t));
  const cx = ax + t * dx;
  const cy = ay + t * dy;
  return Math.hypot(px - cx, py - cy);
}
