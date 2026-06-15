#!/usr/bin/env bash
# Build the final Money Boost promo MP4 with the chosen cloned voice.
#
# Clones the promo voice-over (script_vo.SCENES) in the voice of $1, mixes it
# with music, renders the animation, and encodes money-boost-2026-promo.mp4.
#
#   bash build_promo_video.sh                                   # your own voice (default)
#   bash build_promo_video.sh ../okf-voice/assets/speaker_ref.wav   # cloned OKF voice
#
# Needs HuggingFace access (XTTS-v2) — run from a session whose environment
# network policy is "Full" (or allows *.huggingface.co + *.hf.co).
set -euo pipefail
cd "$(dirname "$0")"

REF="${1:-../okf-voice/assets/my_voice_ref.wav}"
echo "== voice reference: $REF =="

echo "== installing dependencies (CPU torch + XTTS + render deps) =="
pip install -q -U "setuptools<82"
pip install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -q -r ../okf-voice/requirements.txt
pip install -q pymupdf numpy scipy imageio-ffmpeg

echo "== 1/4  clone promo voice-over =="
python3 clone_promo_vo.py --ref "$REF"

echo "== 2/4  mix voice + music + timeline =="
VO_USE_EXISTING=1 python3 soundtrack.py

echo "== 3/4  render frames (4 parallel workers) =="
for s in 0 1 2 3; do node render.js 30 63 build/frames $s 4 & done; wait

echo "== 4/4  encode MP4 =="
bash build.sh

echo "Done -> money-boost-2026-promo.mp4"
