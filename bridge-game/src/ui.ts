import type { LevelDef, MaterialId } from "./game/types";
import { LEVELS } from "./game/levels";
import { MATERIALS, MATERIAL_ORDER } from "./game/materials";
import type { Progress } from "./persistence";

export type BuildTool = MaterialId | "road" | "joint" | "delete";

function clear(root: HTMLElement): void {
  root.innerHTML = "";
}

export function renderMenu(root: HTMLElement, handlers: { onPlay: () => void }): void {
  clear(root);
  const screen = document.createElement("div");
  screen.className = "screen";
  screen.innerHTML = `
    <h1 class="title">🌉 Architecte de Ponts</h1>
    <p class="subtitle">
      Concevez des ponts avec du bois, de l'acier et des câbles, puis regardez marchands, voitures et
      camions les traverser. Chaque niveau exige une structure plus solide pour un trafic plus lourd.
    </p>
  `;
  const playBtn = document.createElement("button");
  playBtn.className = "btn";
  playBtn.textContent = "Jouer";
  playBtn.onclick = handlers.onPlay;
  screen.appendChild(playBtn);
  root.appendChild(screen);
}

export function renderLevelSelect(
  root: HTMLElement,
  progress: Progress,
  handlers: { onSelect: (levelId: number) => void; onBack: () => void },
): void {
  clear(root);
  const screen = document.createElement("div");
  screen.className = "screen";

  const title = document.createElement("h1");
  title.className = "title";
  title.style.fontSize = "2rem";
  title.textContent = "Choisir un niveau";
  screen.appendChild(title);

  const grid = document.createElement("div");
  grid.className = "level-grid";

  for (const level of LEVELS) {
    const locked = level.id > progress.unlockedLevel;
    const card = document.createElement("div");
    card.className = `level-card${locked ? " locked" : ""}`;
    const stars = progress.stars[level.id] ?? 0;
    card.innerHTML = `
      <div class="num">${level.id}</div>
      <div class="name">${locked ? "🔒" : level.name}</div>
      <div class="stars">${starString(stars)}</div>
    `;
    if (!locked) card.onclick = () => handlers.onSelect(level.id);
    grid.appendChild(card);
  }
  screen.appendChild(grid);

  const backBtn = document.createElement("button");
  backBtn.className = "btn secondary";
  backBtn.textContent = "Retour au menu";
  backBtn.onclick = handlers.onBack;
  screen.appendChild(backBtn);

  root.appendChild(screen);
}

function starString(stars: number): string {
  let out = "";
  for (let i = 0; i < 3; i++) out += `<span class="${i < stars ? "on" : ""}">★</span>`;
  return out;
}

export interface BuildHudRefs {
  spentEl: HTMLElement;
  budgetEl: HTMLElement;
  barFillEl: HTMLElement;
  paletteButtons: Map<BuildTool, HTMLElement>;
  connectionEl: HTMLElement;
  testBtn: HTMLButtonElement;
}

export function renderBuildHud(
  root: HTMLElement,
  level: LevelDef,
  handlers: { onTool: (tool: BuildTool) => void; onTest: () => void; onMenu: () => void; onReset: () => void },
): BuildHudRefs {
  clear(root);

  const hud = document.createElement("div");
  hud.className = "hud";
  hud.innerHTML = `
    <div class="hud-panel">
      <div class="hud-title">Niveau ${level.id} — ${level.name}</div>
      <div style="max-width:280px;color:var(--text-dim);font-size:0.8rem;margin-top:4px;">${level.description}</div>
      <div style="margin-top:8px;">Budget : <span id="spent">0</span> / <span id="budget">${level.budget}</span> 🪙</div>
      <div class="budget-bar"><div class="budget-bar-fill" id="bar-fill" style="width:0%"></div></div>
      <div id="connection" style="margin-top:8px;font-size:0.78rem;color:var(--text-dim);">Reliez les deux falaises avec une route 🛣️</div>
    </div>
  `;
  const topActions = document.createElement("div");
  topActions.className = "top-actions";
  const resetBtn = mkBtn("Effacer", "btn secondary small", handlers.onReset);
  const menuBtn = mkBtn("Menu", "btn secondary small", handlers.onMenu);
  topActions.append(resetBtn, menuBtn);
  hud.appendChild(topActions);
  root.appendChild(hud);

  const palette = document.createElement("div");
  palette.className = "palette";
  const paletteButtons = new Map<BuildTool, HTMLElement>();

  const jointBtn = mkPaletteBtn("🔩", "Joint", () => handlers.onTool("joint"));
  palette.appendChild(jointBtn);
  paletteButtons.set("joint", jointBtn);

  const roadBtn = mkPaletteBtn("🛣️", "Route", () => handlers.onTool("road"), MATERIALS.road.color);
  palette.appendChild(roadBtn);
  paletteButtons.set("road", roadBtn);

  for (const matId of MATERIAL_ORDER) {
    if (!level.unlockedMaterials.includes(matId)) continue;
    const mat = MATERIALS[matId];
    const btn = mkPaletteBtn(materialIcon(matId), mat.label, () => handlers.onTool(matId), mat.color);
    palette.appendChild(btn);
    paletteButtons.set(matId, btn);
  }

  const deleteBtn = mkPaletteBtn("🗑️", "Supprimer", () => handlers.onTool("delete"));
  palette.appendChild(deleteBtn);
  paletteButtons.set("delete", deleteBtn);

  root.appendChild(palette);

  const testBtn = document.createElement("button");
  testBtn.className = "btn";
  testBtn.textContent = "▶ Tester le pont";
  testBtn.style.position = "absolute";
  testBtn.style.bottom = "14px";
  testBtn.style.right = "14px";
  testBtn.onclick = handlers.onTest;
  root.appendChild(testBtn);

  return {
    spentEl: hud.querySelector("#spent")!,
    budgetEl: hud.querySelector("#budget")!,
    barFillEl: hud.querySelector("#bar-fill")!,
    paletteButtons,
    connectionEl: hud.querySelector("#connection")!,
    testBtn,
  };
}

function materialIcon(id: MaterialId): string {
  if (id === "wood") return "🪵";
  if (id === "steel") return "🔗";
  if (id === "cable") return "🧵";
  return "🛣️";
}

function mkPaletteBtn(icon: string, label: string, onClick: () => void, swatchColor?: string): HTMLElement {
  const btn = document.createElement("button");
  btn.className = "palette-btn";
  btn.innerHTML = `<div style="font-size:1.2rem;">${icon}</div><div>${label}</div>${
    swatchColor ? `<div class="palette-swatch" style="background:${swatchColor}"></div>` : ""
  }`;
  btn.onclick = onClick;
  return btn;
}

function mkBtn(text: string, className: string, onClick: () => void): HTMLButtonElement {
  const btn = document.createElement("button");
  btn.className = className;
  btn.textContent = text;
  btn.onclick = onClick;
  return btn;
}

export interface SimHudRefs {
  progressEl: HTMLElement;
  bannerEl: HTMLElement;
}

export function renderSimHud(root: HTMLElement, level: LevelDef, total: number, handlers: { onMenu: () => void; onStop: () => void }): SimHudRefs {
  clear(root);
  const hud = document.createElement("div");
  hud.className = "hud";
  hud.innerHTML = `
    <div class="hud-panel">
      <div class="hud-title">Niveau ${level.id} — ${level.name}</div>
      <div style="margin-top:6px;">Trafic : <span id="progress">0</span> / ${total} 🚚</div>
    </div>
  `;
  const topActions = document.createElement("div");
  topActions.className = "top-actions";
  topActions.append(mkBtn("⏸ Retour à la construction", "btn secondary small", handlers.onStop), mkBtn("Menu", "btn secondary small", handlers.onMenu));
  hud.appendChild(topActions);
  root.appendChild(hud);

  const banner = document.createElement("div");
  banner.className = "banner";
  banner.textContent = "Le pont s'effondre !";
  root.appendChild(banner);

  return { progressEl: hud.querySelector("#progress")!, bannerEl: banner };
}

export function renderResult(
  root: HTMLElement,
  level: LevelDef,
  success: boolean,
  stars: 0 | 1 | 2 | 3,
  crossed: number,
  total: number,
  spent: number,
  hasNext: boolean,
  handlers: { onRetry: () => void; onNext: () => void; onLevels: () => void },
): void {
  clear(root);
  const screen = document.createElement("div");
  screen.className = "screen";

  const card = document.createElement("div");
  card.className = "result-card";
  card.innerHTML = `
    <h2 class="title" style="font-size:1.8rem;color:${success ? "var(--success)" : "var(--danger)"};">
      ${success ? "Pont solide !" : "Le pont a cédé"}
    </h2>
    <div class="result-stars">${success ? starString(stars) : "💥"}</div>
    <div class="result-stats">
      Véhicules ayant traversé : ${crossed} / ${total}<br/>
      Budget utilisé : ${spent} / ${level.budget} 🪙
    </div>
  `;

  const actions = document.createElement("div");
  actions.className = "actions-row";
  actions.appendChild(mkBtn("↺ Réessayer", "btn secondary", handlers.onRetry));
  if (success && hasNext) actions.appendChild(mkBtn("Niveau suivant →", "btn", handlers.onNext));
  actions.appendChild(mkBtn("Niveaux", "btn secondary", handlers.onLevels));
  card.appendChild(actions);

  screen.appendChild(card);
  root.appendChild(screen);
}
