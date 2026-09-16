const STORAGE_KEY = "bridge-architect-progress-v1";

export interface Progress {
  unlockedLevel: number;
  stars: Record<number, 0 | 1 | 2 | 3>;
}

function defaultProgress(): Progress {
  return { unlockedLevel: 1, stars: {} };
}

export function loadProgress(): Progress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultProgress();
    const parsed = JSON.parse(raw) as Progress;
    if (typeof parsed.unlockedLevel !== "number" || typeof parsed.stars !== "object") {
      return defaultProgress();
    }
    return parsed;
  } catch {
    return defaultProgress();
  }
}

export function saveProgress(progress: Progress): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch {
    // Stockage indisponible (mode privé, quota) : la progression reste en mémoire pour la session.
  }
}

export function recordLevelResult(levelId: number, stars: 0 | 1 | 2 | 3, nextLevelExists: boolean): Progress {
  const progress = loadProgress();
  const prevStars = progress.stars[levelId] ?? 0;
  if (stars > prevStars) progress.stars[levelId] = stars;
  if (stars > 0 && nextLevelExists) {
    progress.unlockedLevel = Math.max(progress.unlockedLevel, levelId + 1);
  }
  saveProgress(progress);
  return progress;
}
