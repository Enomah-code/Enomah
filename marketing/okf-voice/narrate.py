#!/usr/bin/env python3
"""Narrate a free-form script in a cloned voice, honouring inline pause markers.

A script is a plain text file: one spoken line per line, with pause directions
on their own line as `(pause 1 seconde)` or `(pause 1,5 seconde)`. Blank lines
are ignored. Consecutive spoken lines get a short natural gap.

Examples:
    python3 narrate.py --script scripts/money_boost_2026.txt --ref assets/my_voice_ref.wav
    python3 narrate.py --script my.txt --out build/my.wav --temperature 0.9 --speed 1.05
"""
import argparse
import os
import re

import numpy as np
import soundfile as sf

import ta_shim  # noqa: F401 — routes torchaudio I/O through soundfile
from clone import DYNAMICS, SR, load_tts, say

ROOT = os.path.dirname(os.path.abspath(__file__))
NAT_GAP = 0.45  # natural pause between consecutive spoken lines (s)
PAUSE_RE = re.compile(r"^\(?\s*pause\s+([\d.,]+)\s*seconde", re.IGNORECASE)


def parse_script(path):
    """Yield ('say', text) and ('pause', seconds) items in order."""
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            m = PAUSE_RE.match(line)
            if m:
                yield ("pause", float(m.group(1).replace(",", ".")))
            else:
                yield ("say", line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="text script with (pause N seconde) markers")
    ap.add_argument("--ref", default=os.path.join(ROOT, "assets", "my_voice_ref.wav"))
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "narration.wav"))
    ap.add_argument("--temperature", type=float, default=DYNAMICS["temperature"])
    ap.add_argument("--speed", type=float, default=DYNAMICS["speed"])
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    dyn = dict(DYNAMICS, temperature=args.temperature, speed=args.speed)
    items = list(parse_script(args.script))
    tts = load_tts()

    out = np.zeros(0, dtype=np.float32)
    pending_pause = None  # explicit pause overrides the natural gap
    prev_was_say = False
    for kind, val in items:
        if kind == "pause":
            pending_pause = val
            continue
        if prev_was_say:
            gap = pending_pause if pending_pause is not None else NAT_GAP
            out = np.concatenate([out, np.zeros(int(gap * SR), dtype=np.float32)])
        clip = say(tts, val, args.ref, dyn)
        clip = clip / (np.max(np.abs(clip)) + 1e-9) * 0.97
        out = np.concatenate([out, clip])
        print(f"  {len(clip) / SR:5.2f}s  {val[:55]}")
        pending_pause, prev_was_say = None, True

    out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
    sf.write(args.out, out, SR)
    print(f"\nnarration: {len(out) / SR:.2f}s -> {args.out}")


if __name__ == "__main__":
    main()
