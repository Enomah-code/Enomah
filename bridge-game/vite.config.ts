import { defineConfig } from "vite";

// Deux cibles de build :
// - GitHub Pages (par défaut) : "project site" servi sous /enomah/bridge-game/.
// - App native (Capacitor) : assets embarqués localement, donc base "/".
//   Déclenché via `npm run build:capacitor` (voir package.json).
const isCapacitorBuild = process.env.CAPACITOR_BUILD === "1";

export default defineConfig({
  base: isCapacitorBuild ? "/" : (process.env.GITHUB_PAGES_BASE ?? "/enomah/bridge-game/"),
  build: {
    outDir: isCapacitorBuild ? "dist-capacitor" : "dist",
    sourcemap: true,
  },
});
