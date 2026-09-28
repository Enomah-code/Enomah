#!/usr/bin/env bash
# Music bed: Mixkit "Sports Highlights" (Mixkit Stock Music Free License), 123.05 BPM.
# Stretched to the edit's 128 BPM grid, then trimmed so the start of a 32-beat phrase
# (source beat 32, 15.51 s) lands on the product reveal at 5.65 s. The bed starts at 0.85 s.
set -euo pipefail
cd "$(dirname "$0")/.."
src=prep/bgm_src.mp3
[ -f "$src" ] || curl -sSfL "https://assets.mixkit.co/music/51/51.mp3" -o "$src"
R=1.04025                       # 0.48762 s source beat -> 0.46875 s (128 BPM)
PHRASE=$(python3 -c "print(15.51/$R)")          # phrase start in stretched time
OFF=$(python3 -c "print(round($PHRASE-5.65+0.85,4))")   # stretched time at video 0.85 s
ffmpeg -nostdin -y -v error -i "$src" -af "rubberband=tempo=$R,atrim=start=$OFF:duration=29.6,asetpts=PTS-STARTPTS,afade=t=in:d=0.25,afade=t=out:st=28.6:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -ac 2 assets/bgm/track.wav
echo "offset $OFF"
