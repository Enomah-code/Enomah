import "./style.css";
import { LEVELS, getLevel } from "./game/levels";
import { BuildEditor, JOINT_HIT_RADIUS } from "./game/editor";
import { Simulation } from "./game/simulation";
import { Camera, computeWorldGeometry, type WorldGeometry } from "./game/world";
import { drawBackground, drawBuildMode, drawSimulation, type BuildHoverState } from "./game/renderer";
import { loadProgress, recordLevelResult, type Progress } from "./persistence";
import {
  renderMenu,
  renderLevelSelect,
  renderBuildHud,
  renderSimHud,
  renderResult,
  type BuildTool,
  type BuildHudRefs,
  type SimHudRefs,
} from "./ui";
import type { EditorNode, GameScreen, LevelDef, MaterialId, SimResult } from "./game/types";

const FIXED_STEP_MS = 1000 / 60;
const MAX_STEPS_PER_FRAME = 6;

function materialForTool(tool: BuildTool): MaterialId {
  if (tool === "joint" || tool === "delete") return "road";
  return tool;
}

class App {
  canvas = document.getElementById("game-canvas") as HTMLCanvasElement;
  ctx = this.canvas.getContext("2d")!;
  uiRoot = document.getElementById("ui-root") as HTMLElement;
  camera = new Camera();

  screen: GameScreen = "menu";
  progress: Progress = loadProgress();
  currentLevel: LevelDef = LEVELS[0];
  worldGeom: WorldGeometry = computeWorldGeometry(this.currentLevel);

  editor: BuildEditor | null = null;
  simulation: Simulation | null = null;
  buildHud: BuildHudRefs | null = null;
  simHud: SimHudRefs | null = null;

  activeTool: BuildTool = "road";
  dragFrom: EditorNode | null = null;
  dragFromIsNew = false;
  hoverNode: EditorNode | null = null;
  cursorWorld: { x: number; y: number } | null = null;
  invalidDrag = false;

  lastResult: SimResult | null = null;
  accumulatorMs = 0;
  lastTimestamp = 0;
  bannerTimeout = 0;

  cssWidth = window.innerWidth;
  cssHeight = window.innerHeight;

  constructor() {
    window.addEventListener("resize", () => this.handleResize());
    this.handleResize();
    this.setupPointerEvents();
    this.showMenu();
    requestAnimationFrame((t) => this.loop(t));
  }

  // ---------- Screens ----------

  showMenu(): void {
    this.screen = "menu";
    this.editor = null;
    this.simulation = null;
    renderMenu(this.uiRoot, { onPlay: () => this.showLevelSelect() });
  }

  showLevelSelect(): void {
    this.screen = "levelSelect";
    this.editor = null;
    this.simulation = null;
    renderLevelSelect(this.uiRoot, this.progress, {
      onSelect: (id) => this.startLevel(id),
      onBack: () => this.showMenu(),
    });
  }

  startLevel(id: number): void {
    const level = getLevel(id);
    if (!level) return;
    this.currentLevel = level;
    this.worldGeom = computeWorldGeometry(level);
    this.camera.fit(this.worldGeom, this.cssWidth, this.cssHeight);
    this.editor = new BuildEditor(level);
    this.simulation = null;
    this.activeTool = "road";
    this.dragFrom = null;
    this.screen = "build";
    this.buildHud = renderBuildHud(this.uiRoot, level, {
      onTool: (tool) => this.setTool(tool),
      onTest: () => this.startSimulation(),
      onMenu: () => this.showLevelSelect(),
      onReset: () => this.resetBuild(),
    });
    this.setTool("road");
    this.updateBuildHud();
  }

  resetBuild(): void {
    if (!this.editor) return;
    this.editor = new BuildEditor(this.currentLevel);
    this.updateBuildHud();
  }

  setTool(tool: BuildTool): void {
    this.activeTool = tool;
    this.dragFrom = null;
    if (!this.buildHud) return;
    for (const [key, el] of this.buildHud.paletteButtons) {
      el.classList.toggle("active", key === tool);
    }
  }

  startSimulation(): void {
    if (!this.editor) return;
    if (!this.editor.isRoadConnected()) return;
    this.simulation = new Simulation(this.editor, {
      onVehicleCrossed: (crossed, total) => {
        if (this.simHud) this.simHud.progressEl.textContent = `${crossed}`;
        void total;
      },
      onCollapse: () => this.flashBanner("💥 Le pont s'effondre !"),
      onEnd: (result) => this.finishSimulation(result),
    });
    this.screen = "simulate";
    this.simHud = renderSimHud(this.uiRoot, this.currentLevel, this.simulation.totalVehicles, {
      onMenu: () => this.showLevelSelect(),
      onStop: () => this.backToBuild(),
    });
  }

  backToBuild(): void {
    this.simulation?.destroy();
    this.simulation = null;
    if (!this.editor) return;
    this.screen = "build";
    this.buildHud = renderBuildHud(this.uiRoot, this.currentLevel, {
      onTool: (tool) => this.setTool(tool),
      onTest: () => this.startSimulation(),
      onMenu: () => this.showLevelSelect(),
      onReset: () => this.resetBuild(),
    });
    this.setTool(this.activeTool);
    this.updateBuildHud();
  }

  finishSimulation(result: SimResult): void {
    this.lastResult = result;
    this.screen = "result";
    const hasNext = LEVELS.some((l) => l.id === this.currentLevel.id + 1);
    this.progress = recordLevelResult(this.currentLevel.id, result.stars, hasNext);
    renderResult(
      this.uiRoot,
      this.currentLevel,
      result.success,
      result.stars,
      result.vehiclesCrossed,
      result.vehiclesTotal,
      result.budgetSpent,
      hasNext,
      {
        onRetry: () => this.startLevel(this.currentLevel.id),
        onNext: () => this.startLevel(this.currentLevel.id + 1),
        onLevels: () => this.showLevelSelect(),
      },
    );
  }

  flashBanner(text: string): void {
    if (!this.simHud) return;
    this.simHud.bannerEl.textContent = text;
    this.simHud.bannerEl.classList.add("show");
    window.clearTimeout(this.bannerTimeout);
    this.bannerTimeout = window.setTimeout(() => this.simHud?.bannerEl.classList.remove("show"), 2200);
  }

  // ---------- Build HUD updates ----------

  updateBuildHud(): void {
    if (!this.buildHud || !this.editor) return;
    const spent = this.editor.spent;
    const budget = this.editor.level.budget;
    this.buildHud.spentEl.textContent = `${spent}`;
    const pct = budget > 0 ? Math.min(100, (spent / budget) * 100) : 0;
    this.buildHud.barFillEl.style.width = `${pct}%`;
    this.buildHud.barFillEl.classList.toggle("over", spent > budget);
    const connected = this.editor.isRoadConnected();
    this.buildHud.connectionEl.textContent = connected
      ? "✅ Route reliée entre les deux falaises"
      : "Reliez les deux falaises avec une route 🛣️";
    this.buildHud.testBtn.disabled = !connected;
  }

  // ---------- Pointer handling (build mode) ----------

  setupPointerEvents(): void {
    this.canvas.addEventListener("pointerdown", (e) => this.onPointerDown(e));
    this.canvas.addEventListener("pointermove", (e) => this.onPointerMove(e));
    window.addEventListener("pointerup", (e) => this.onPointerUp(e));
  }

  private eventWorldPos(e: PointerEvent): { x: number; y: number } {
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    return { x: this.camera.toWorldX(x), y: this.camera.toWorldY(y) };
  }

  private onPointerDown(e: PointerEvent): void {
    if (this.screen !== "build" || !this.editor) return;
    const pos = this.eventWorldPos(e);

    if (this.activeTool === "delete") {
      const beam = this.editor.findBeamAt(pos.x, pos.y);
      if (beam) {
        this.editor.removeBeam(beam.id);
      } else {
        const node = this.editor.findNodeAt(pos.x, pos.y);
        if (node && node.kind !== "anchor") this.editor.removeNode(node.id);
      }
      this.updateBuildHud();
      return;
    }

    if (this.activeTool === "joint") {
      if (this.editor.isWithinBuildZone(pos.x, pos.y) && !this.editor.findNodeAt(pos.x, pos.y)) {
        this.editor.addJoint(pos.x, pos.y);
      }
      return;
    }

    // Material / road tool: start a drag from an existing node or a freshly created joint.
    const existing = this.editor.findNodeAt(pos.x, pos.y);
    if (existing) {
      this.dragFrom = existing;
      this.dragFromIsNew = false;
    } else if (this.editor.isWithinBuildZone(pos.x, pos.y)) {
      this.dragFrom = this.editor.addJoint(pos.x, pos.y);
      this.dragFromIsNew = true;
    } else {
      this.dragFrom = null;
    }
  }

  private onPointerMove(e: PointerEvent): void {
    if (this.screen !== "build" || !this.editor) return;
    const pos = this.eventWorldPos(e);
    this.cursorWorld = pos;
    this.hoverNode = this.editor.findNodeAt(pos.x, pos.y);

    if (this.dragFrom) {
      const material = materialForTool(this.activeTool);
      const target = this.hoverNode ?? { id: "__preview__", x: pos.x, y: pos.y, kind: "joint" as const };
      if (target.id === this.dragFrom.id) {
        this.invalidDrag = true;
      } else {
        this.invalidDrag = !this.editor.canAffordBeam(this.dragFrom, target, material);
      }
    }
  }

  private onPointerUp(e: PointerEvent): void {
    if (this.screen !== "build" || !this.editor || !this.dragFrom) {
      this.dragFrom = null;
      return;
    }
    const pos = this.eventWorldPos(e);
    const material = materialForTool(this.activeTool);

    let target = this.editor.findNodeAt(pos.x, pos.y);
    if (!target && this.editor.isWithinBuildZone(pos.x, pos.y)) {
      const dist = Math.hypot(pos.x - this.dragFrom.x, pos.y - this.dragFrom.y);
      if (dist > JOINT_HIT_RADIUS) target = this.editor.addJoint(pos.x, pos.y);
    }

    let beamAdded = false;
    if (target && target.id !== this.dragFrom.id) {
      const beam = this.editor.addBeam(this.dragFrom.id, target.id, material);
      beamAdded = !!beam;
    }

    if (!beamAdded && this.dragFromIsNew) {
      this.editor.removeNode(this.dragFrom.id);
    }
    if (!beamAdded && target && target.id !== this.dragFrom.id && target.kind === "joint") {
      // Orphaned target created during a failed drag (no existing beams reference it yet).
      const stillOrphan = ![...this.editor.beams.values()].some((b) => b.nodeA === target!.id || b.nodeB === target!.id);
      if (stillOrphan && target.id !== this.dragFrom.id) this.editor.removeNode(target.id);
    }

    this.dragFrom = null;
    this.invalidDrag = false;
    this.updateBuildHud();
  }

  // ---------- Resize & loop ----------

  handleResize(): void {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.cssWidth = window.innerWidth;
    this.cssHeight = window.innerHeight;
    this.canvas.width = Math.round(this.cssWidth * dpr);
    this.canvas.height = Math.round(this.cssHeight * dpr);
    this.canvas.style.width = `${this.cssWidth}px`;
    this.canvas.style.height = `${this.cssHeight}px`;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (this.screen === "build" || this.screen === "simulate") {
      this.camera.fit(this.worldGeom, this.cssWidth, this.cssHeight);
    }
  }

  loop(timestamp: number): void {
    if (!this.lastTimestamp) this.lastTimestamp = timestamp;
    const delta = Math.min(timestamp - this.lastTimestamp, 250);
    this.lastTimestamp = timestamp;

    if (this.screen === "simulate" && this.simulation) {
      this.accumulatorMs += delta;
      let steps = 0;
      while (this.accumulatorMs >= FIXED_STEP_MS && steps < MAX_STEPS_PER_FRAME) {
        const alive = this.simulation.step(FIXED_STEP_MS);
        this.accumulatorMs -= FIXED_STEP_MS;
        steps += 1;
        if (!alive) break;
      }
    }

    this.render();
    requestAnimationFrame((t) => this.loop(t));
  }

  render(): void {
    const { ctx } = this;
    ctx.clearRect(0, 0, this.cssWidth, this.cssHeight);

    if (this.screen === "build" && this.editor) {
      drawBackground(ctx, this.camera, this.worldGeom, this.cssWidth, this.cssHeight);
      const hover: BuildHoverState = {
        hoverNode: this.hoverNode,
        dragFrom: this.dragFrom,
        cursorWorld: this.cursorWorld,
        activeMaterial: materialForTool(this.activeTool),
        invalidDrag: this.invalidDrag,
      };
      drawBuildMode(ctx, this.camera, this.editor, hover);
    } else if (this.screen === "simulate" && this.simulation) {
      drawBackground(ctx, this.camera, this.worldGeom, this.cssWidth, this.cssHeight);
      drawSimulation(ctx, this.camera, this.simulation);
    } else {
      ctx.fillStyle = "#10151c";
      ctx.fillRect(0, 0, this.cssWidth, this.cssHeight);
    }
  }
}

new App();
