import { Config } from "@remotion/cli/config";

// Chrome headless déjà présent dans l'environnement (évite le téléchargement)
Config.setBrowserExecutable(
  "/root/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/chrome-headless-shell-linux64/chrome-headless-shell",
);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setCodec("h264");
Config.setCrf(16);
