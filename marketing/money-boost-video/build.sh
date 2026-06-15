#!/usr/bin/env bash
# Render frames (parallel shards) then encode with the spot audio into the MP4.
set -euo pipefail
cd "$(dirname "$0")"

FPS=${FPS:-30}
SHARDS=${SHARDS:-4}
FF=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
FRAMES_DIR="build/frames"
AUDIO="build/spot.mp3"
OUT="money-boost-video.mp4"

rm -rf "$FRAMES_DIR"; mkdir -p "$FRAMES_DIR"
echo "Rendering frames @ ${FPS}fps on ${SHARDS} shards…"
pids=()
for s in $(seq 0 $((SHARDS-1))); do
  node render.js "$FPS" "$FRAMES_DIR" "$s" "$SHARDS" & pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done

echo "Encoding $OUT …"
"$FF" -y -framerate $FPS -i "$FRAMES_DIR/f_%05d.jpg" -i "$AUDIO" \
  -map 0:v -map 1:a \
  -c:v libx264 -profile:v high -preset slow -crf 18 -pix_fmt yuv420p \
  -movflags +faststart -r $FPS \
  -c:a aac -b:a 192k -shortest \
  "$OUT"

"$FF" -y -ss 00:00:10 -i "$OUT" -frames:v 1 -q:v 2 -update 1 money-boost-video-poster.jpg
echo "Done:"; ls -lh "$OUT" money-boost-video-poster.jpg
