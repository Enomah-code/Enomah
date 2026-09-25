#!/usr/bin/env bash
# Stone Edits — final render + delivery encode.
# usage: _shared/render.sh <project-dir> <OutputBaseName> [--clean] [--fps N] [--draft]
#   --clean   version without the Stone Edits end card / watermark (length = data-main-duration)
set -euo pipefail
PROJ=$(cd "$1" && pwd); NAME=$2; shift 2
CLEAN=0; FPS=60; Q=high
while [ $# -gt 0 ]; do case $1 in --clean) CLEAN=1;; --fps) FPS=$2; shift;; --draft) Q=draft;; esac; shift; done
HERE=$(cd "$(dirname "$0")" && pwd); OUT=$(cd "$HERE/.." && pwd)/livrables; mkdir -p "$OUT"
python3 "$HERE/build.py" "$PROJ" >/dev/null
SRC=$PROJ; VARS='{}'
if [ $CLEAN = 1 ]; then
  SRC=$(mktemp -d)/$(basename "$PROJ"); cp -r "$PROJ" "$SRC"; rm -rf "$SRC/renders"
  python3 - "$SRC/index.html" <<'PY'
import re,sys
p=sys.argv[1]; s=open(p).read()
m=re.search(r'data-main-duration="([\d.]+)"',s)
s=re.sub(r'(id="root"[^>]*?data-duration=")[\d.]+(")', lambda x: x.group(1)+m.group(1)+x.group(2), s, count=1)
open(p,'w').write(s)
PY
  VARS='{"SIGNATURE_ENDCARD":false,"SIGNATURE_WATERMARK":false}'; NAME="${NAME}_clean"
fi
TMP=$(mktemp -d)/raw.mp4
(cd "$SRC" && npx --yes hyperframes render -o "$TMP" -f "$FPS" -q "$Q" --video-bitrate 16M --variables "$VARS" --quiet >/dev/null)
# delivery: H.264 stream kept, audio re-encoded AAC 320 kb/s 48 kHz, metadata stripped
ffmpeg -v error -y -i "$TMP" -map 0 -map_metadata -1 -c:v copy -bsf:v filter_units=remove_types=6 -c:a aac -b:a 320k -ar 48000 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
  -metadata title="$NAME" -metadata artist="Stone Edits" -movflags +faststart "$OUT/$NAME.mp4"
echo "$OUT/$NAME.mp4"
