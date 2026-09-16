import { defineConfig } from "vite";

// Servi en tant que "project site" GitHub Pages sous /enomah/bridge-game/.
// GITHUB_PAGES_BASE peut être surchargé par le workflow de déploiement.
export default defineConfig({
  base: process.env.GITHUB_PAGES_BASE ?? "/enomah/bridge-game/",
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
