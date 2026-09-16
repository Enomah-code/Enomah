import type { MaterialDef, MaterialId } from "./types";

export const MATERIALS: Record<MaterialId, MaterialDef> = {
  wood: {
    id: "wood",
    label: "Bois",
    costPerLength: 6,
    maxForce: 0.018,
    thickness: 6,
    color: "#a9743a",
    breakColor: "#5c3a1a",
    density: 0.0016,
  },
  steel: {
    id: "steel",
    label: "Acier",
    costPerLength: 16,
    maxForce: 0.05,
    thickness: 8,
    color: "#8b95a1",
    breakColor: "#4a5058",
    density: 0.003,
  },
  cable: {
    id: "cable",
    label: "Câble",
    costPerLength: 10,
    maxForce: 0.06,
    thickness: 3,
    color: "#d8c98a",
    breakColor: "#7a6f42",
    cableOnly: true,
    density: 0.0006,
  },
  road: {
    id: "road",
    label: "Route",
    costPerLength: 5,
    maxForce: 0.022,
    thickness: 16,
    color: "#4a4a52",
    breakColor: "#2a2a30",
    density: 0.0018,
  },
};

/** Poutres de structure proposées dans la palette (la route est un outil séparé). */
export const MATERIAL_ORDER: MaterialId[] = ["wood", "steel", "cable"];
