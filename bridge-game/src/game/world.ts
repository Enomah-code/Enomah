import type { LevelDef } from "./types";

export const ANCHOR_MARGIN = 130;
export const BUILD_HEIGHT_ABOVE = 240;
export const FALL_DEPTH = 480;
export const SNAP_GRID = 20;

export interface WorldGeometry {
  width: number;
  height: number;
  leftAnchor: { x: number; y: number };
  rightAnchor: { x: number; y: number };
  failY: number;
  groundTopY: number;
}

export function computeWorldGeometry(level: LevelDef): WorldGeometry {
  const width = level.gapWidth + ANCHOR_MARGIN * 2;
  const groundTopY = Math.min(level.anchorLeftY, level.anchorRightY);
  const failY = Math.max(level.anchorLeftY, level.anchorRightY) + FALL_DEPTH;
  return {
    width,
    height: BUILD_HEIGHT_ABOVE + FALL_DEPTH + (Math.max(level.anchorLeftY, level.anchorRightY) - groundTopY),
    leftAnchor: { x: ANCHOR_MARGIN, y: level.anchorLeftY },
    rightAnchor: { x: ANCHOR_MARGIN + level.gapWidth, y: level.anchorRightY },
    failY,
    groundTopY,
  };
}

/** Transforme les coordonnées "monde" (jeu) en coordonnées écran (canvas), avec zoom + centrage. */
export class Camera {
  scale = 1;
  offsetX = 0;
  offsetY = 0;

  fit(world: WorldGeometry, canvasWidth: number, canvasHeight: number, padding = 60): void {
    const usableW = canvasWidth - padding * 2;
    const usableH = canvasHeight - padding * 2;
    const worldTop = world.groundTopY - BUILD_HEIGHT_ABOVE;
    const worldBottom = world.failY;
    const worldH = worldBottom - worldTop;
    this.scale = Math.min(usableW / world.width, usableH / worldH, 1.15);
    this.offsetX = padding + (usableW - world.width * this.scale) / 2;
    this.offsetY = padding + (usableH - worldH * this.scale) / 2 - worldTop * this.scale;
  }

  toScreenX(x: number): number {
    return x * this.scale + this.offsetX;
  }
  toScreenY(y: number): number {
    return y * this.scale + this.offsetY;
  }
  toWorldX(x: number): number {
    return (x - this.offsetX) / this.scale;
  }
  toWorldY(y: number): number {
    return (y - this.offsetY) / this.scale;
  }
}

export function snap(value: number, grid = SNAP_GRID): number {
  return Math.round(value / grid) * grid;
}
