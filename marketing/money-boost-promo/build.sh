#!/usr/bin/env bash
# Encode rendered frames + soundtrack into the final promo MP4.
set -euo pipefail
cd "$(dirname "$0")"

FF=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
FPS=30
FRAMES="build/frames/f_%05d.jpg"
AUDIO="build/soundtrack.wav"
OUT="money-boost-2026-promo.mp4"

echo "Encoding $OUT ..."
"$FF" -y -framerate $FPS -i "$FRAMES" -i "$AUDIO" \
  -map 0:v -map 1:a \
  -c:v libx264 -profile:v high -preset slow -crf 18 -pix_fmt yuv420p \
  -movflags +faststart -r $FPS \
  -c:a aac -b:a 192k -shortest \
  "$OUT"

# poster frame (product reveal moment)
"$FF" -y -i "$OUT" -ss 00:00:19.5 -frames:v 1 -q:v 2 money-boost-2026-poster.jpg

echo "Done:"
ls -lh "$OUT" money-boost-2026-poster.jpg
