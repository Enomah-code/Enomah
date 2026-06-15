#!/usr/bin/env bash
# A/B compare the Money Boost 2026 voice-over in two voices:
#   1. your own voice   (assets/my_voice_ref.wav)
#   2. the cloned OKF voice (assets/speaker_ref.wav)
# Produces, for each: a dry mastered VO and a finished spot with ducked music.
#
# Needs HuggingFace access (XTTS-v2 weights) — run from a session whose
# environment network policy is "Full" (or allows *.huggingface.co + *.hf.co).
#
#   bash compare_voices.sh
#
# Outputs in build/:
#   mb_myvoice_master.mp3   mb_myvoice_spot.mp3     <- your voice
#   mb_okfvoice_master.mp3  mb_okfvoice_spot.mp3    <- cloned OKF voice
set -euo pipefail
cd "$(dirname "$0")"

SCRIPT=scripts/money_boost_2026.txt

echo "== installing dependencies (CPU torch + XTTS) =="
pip install -q -U "setuptools<82"
pip install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -q -r requirements.txt

mkdir -p build

echo "== 1/2  your own voice =="
python3 narrate.py --script "$SCRIPT" --ref assets/my_voice_ref.wav \
        --preset natural --out build/mb_myvoice.wav
python3 mix_music.py --voice build/mb_myvoice_master.mp3 --out build/mb_myvoice_spot.mp3

echo "== 2/2  cloned OKF voice =="
python3 narrate.py --script "$SCRIPT" --ref assets/speaker_ref.wav \
        --preset natural --out build/mb_okfvoice.wav
python3 mix_music.py --voice build/mb_okfvoice_master.mp3 --out build/mb_okfvoice_spot.mp3

echo
echo "Done. Compare:"
echo "  your voice  : build/mb_myvoice_master.mp3  /  build/mb_myvoice_spot.mp3"
echo "  OKF clone   : build/mb_okfvoice_master.mp3 /  build/mb_okfvoice_spot.mp3"
