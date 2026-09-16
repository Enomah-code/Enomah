export type MaterialId = "wood" | "steel" | "cable" | "road";

export interface MaterialDef {
  id: MaterialId;
  label: string;
  /** Coût en pièces d'or par unité de longueur (100px = 1 unité). */
  costPerLength: number;
  /** Force de traction/compression maximale avant rupture (unités Matter.js). */
  maxForce: number;
  /** Épaisseur de rendu en pixels. */
  thickness: number;
  color: string;
  breakColor: string;
  /** Une poutre-câble ne résiste qu'à la traction, pas à la compression. */
  cableOnly?: boolean;
  density: number;
}

export type NodeKind = "anchor" | "joint";

export interface EditorNode {
  id: string;
  x: number;
  y: number;
  kind: NodeKind;
}

export interface EditorBeam {
  id: string;
  nodeA: string;
  nodeB: string;
  material: MaterialId;
}

export function isRoadMaterial(material: MaterialId): boolean {
  return material === "road";
}

export type VehicleType = "cart" | "car" | "truck" | "heavyTruck" | "hauler";

export interface VehicleDef {
  type: VehicleType;
  label: string;
  weight: number;
  width: number;
  height: number;
  wheelRadius: number;
  color: string;
  speed: number;
}

export interface VehicleWave {
  type: VehicleType;
  count: number;
  gapMs: number;
}

export interface LevelDef {
  id: number;
  name: string;
  description: string;
  gapWidth: number;
  anchorLeftY: number;
  anchorRightY: number;
  budget: number;
  waves: VehicleWave[];
  unlockedMaterials: MaterialId[];
  starBudgetBonus: [number, number];
}

export type GameScreen = "menu" | "levelSelect" | "build" | "simulate" | "result";

export interface SimResult {
  success: boolean;
  vehiclesCrossed: number;
  vehiclesTotal: number;
  budgetSpent: number;
  budgetTotal: number;
  stars: 0 | 1 | 2 | 3;
}
