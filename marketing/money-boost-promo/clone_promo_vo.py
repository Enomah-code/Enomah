#!/usr/bin/env python3
"""Clone the *promo video* voice-over (script_vo.SCENES) in a chosen voice.

Reuses the robust okf-voice cloning engine (XTTS-v2 with anti-rambling retries
and the calm/faithful NATURAL preset) to synthesise the money-boost-promo
script in the speaker of `--ref`, writing build/vo/scene_*.wav at the project
sample rate. Then mix + render with:

    VO_USE_EXISTING=1 python3 soundtrack.py
    for s in 0 1 2 3; do node render.js 30 63 build/frames $s 4 & done; wait
    bash build.sh

`--ref` defaults to the user's own voice; pass the OKF reference to use the
cloned brand voice instead:

    python3 clone_promo_vo.py --ref ../okf-voice/assets/my_voice_ref.wav   # own voice
    python3 clone_promo_vo.py --ref ../okf-voice/assets/speaker_ref.wav    # cloned OKF

Needs HuggingFace access (XTTS-v2 weights).
"""
import os, sys, argparse
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

ROOT = os.path.dirname(os.path.abspath(__file__))
OKF = os.path.join(ROOT, '..', 'okf-voice')
sys.path.insert(0, ROOT)
sys.path.insert(0, OKF)

from script_vo import SCENES, GAP            # promo script + cadence
import ta_shim                               # noqa: F401 (okf-voice)
from clone import load_tts, say, NATURAL, SR as XSR   # okf-voice engine (XSR=24000)

OUT_SR = 44100
VO_DIR = os.path.join(ROOT, 'build', 'vo')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default=os.path.join(OKF, 'assets', 'my_voice_ref.wav'),
                    help='speaker reference wav (own voice or cloned OKF)')
    args = ap.parse_args()
    os.makedirs(VO_DIR, exist_ok=True)

    tts = load_tts()
    gap = np.zeros(int(GAP * OUT_SR), dtype=np.float32)
    for i, (_, phrases) in enumerate(SCENES):
        parts = []
        for ph in phrases:
            clip = say(tts, ph, args.ref, NATURAL)        # 24 kHz mono
            clip = resample_poly(clip.astype(np.float32), OUT_SR, XSR)
            parts.append(clip)
        out = parts[0]
        for p in parts[1:]:
            out = np.concatenate([out, gap, p])
        out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
        path = os.path.join(VO_DIR, f'scene_{i}.wav')
        wavfile.write(path, OUT_SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
        print(f"  cloned VO scene {i}: {len(out)/OUT_SR:.2f}s -> {path}")

    print("\nDone. Now run:\n  VO_USE_EXISTING=1 python3 soundtrack.py\n"
          "  for s in 0 1 2 3; do node render.js 30 63 build/frames $s 4 & done; wait\n"
          "  bash build.sh")


if __name__ == '__main__':
    main()
