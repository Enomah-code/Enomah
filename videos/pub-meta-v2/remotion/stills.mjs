// Rend des images-clés pour la vérification visuelle (un seul bundle)
// Usage : node stills.mjs 36 102 129 ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const frames = process.argv.slice(2).map(Number);
const browserExecutable =
  "/root/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/chrome-headless-shell-linux64/chrome-headless-shell";
const serveUrl = await bundle({ entryPoint: "src/index.ts" });
const composition = await selectComposition({ serveUrl, id: "PubMeta", browserExecutable });
for (const f of frames) {
  await renderStill({ composition, serveUrl, frame: f, output: `out/stills/f${String(f).padStart(4, "0")}.png`, browserExecutable });
  console.log("ok", f);
}
