#!/usr/bin/env python3
"""Synthesise speech in the cloned OKF voice with Coqui XTTS-v2.

Examples:
    # Reproduce the full OKF promo voice-over (one wav per scene + a stitched mix)
    python3 clone.py

    # Say any custom line in the cloned voice
    python3 clone.py --text "Bonjour, votre colis est arrivé."

    # Use a different reference / output dir
    python3 clone.py --ref assets/speaker_ref.wav --out build
"""
import argparse
import os

import numpy as np
import soundfile as sf

import ta_shim  # noqa: F401  — routes torchaudio I/O through soundfile
from script import GAP, SCENES

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 24000  # XTTS-v2 native sample rate
MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

os.environ.setdefault("COQUI_TOS_AGREED", "1")


def trim(clip, sr, thr_ratio=0.008):
    """Trim leading/trailing silence, keeping generous padding so soft consonants
    at phrase edges are never clipped."""
    thr = thr_ratio * (np.max(np.abs(clip)) + 1e-9)
    idx = np.where(np.abs(clip) > thr)[0]
    if len(idx):
        clip = clip[max(0, idx[0] - int(0.05 * sr)): idx[-1] + int(0.12 * sr)]
    return edge_fade(clip, sr)


def edge_fade(clip, sr, ms=12.0):
    """Short linear fade in/out to avoid clicks where clips are concatenated."""
    n = int(ms / 1000 * sr)
    if len(clip) > 2 * n and n > 0:
        ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
        clip = clip.copy()
        clip[:n] *= ramp
        clip[-n:] *= ramp[::-1]
    return clip


# Delivery preset — higher temperature widens intonation (more dynamic), and a
# slightly faster speed adds energy. Defaults are a moderate, stable bump over
# XTTS's calm defaults (temperature 0.65, speed 1.0).
DYNAMICS = dict(temperature=0.85, speed=1.06, top_p=0.90, top_k=60,
                length_penalty=1.0, repetition_penalty=2.0)

# Calm, faithful preset — best for cloning a real person's own voice (keeps the
# timbre stable and avoids the "hollow" drift that high temperature can add).
# Long conditioning (gpt_cond_len) lets XTTS listen to far more of the reference,
# which carries the speaker's accent through better than the 6 s default.
NATURAL = dict(temperature=0.70, speed=1.03, top_p=0.85, top_k=50,
               length_penalty=1.0, repetition_penalty=2.0,
               gpt_cond_len=40, gpt_cond_chunk_len=20, max_ref_len=60,
               sound_norm_refs=True)


def load_tts():
    ta_shim.install()
    from TTS.api import TTS
    print(f"loading {MODEL} on cpu …")
    return TTS(MODEL, progress_bar=False).to("cpu")


def say(tts, text, ref, dynamics=DYNAMICS, max_tries=4):
    """Synthesise one line, retrying if XTTS rambles (a known failure where the
    output runs far longer than the text warrants, with repeated/garbled audio).
    Retries re-roll the sampling and calm the temperature for stability."""
    expected = max(1.0, len(text) / 13.0)   # ~13 chars/sec of French speech
    limit = expected * 2.0 + 1.0
    best = None
    for k in range(max_tries):
        kw = dict(dynamics)
        if k:  # progressively calmer on retries
            kw["temperature"] = max(0.30, kw.get("temperature", 0.70) - 0.15 * k)
        wav = np.asarray(tts.tts(text=text, speaker_wav=ref, language="fr", **kw),
                         dtype=np.float32)
        clip = trim(wav, SR)
        if len(clip) / SR <= limit:
            return clip
        if best is None or len(clip) < len(best):
            best = clip
    return best  # shortest attempt if all overshoot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=os.path.join(ROOT, "assets", "speaker_ref.wav"))
    ap.add_argument("--out", default=os.path.join(ROOT, "build"))
    ap.add_argument("--text", help="synthesise this single line instead of the promo")
    ap.add_argument("--temperature", type=float, default=DYNAMICS["temperature"],
                    help="intonation dynamism (higher = livelier; 0.65 = calm)")
    ap.add_argument("--speed", type=float, default=DYNAMICS["speed"],
                    help="delivery speed (1.0 = neutral)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    dyn = dict(DYNAMICS, temperature=args.temperature, speed=args.speed)
    tts = load_tts()

    if args.text:
        out = say(tts, args.text, args.ref, dyn)
        out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
        path = os.path.join(args.out, "custom.wav")
        sf.write(path, out, SR)
        print(f"  -> {path}  ({len(out) / SR:.2f}s)")
        return

    gap = np.zeros(int(GAP * SR), dtype=np.float32)
    scene_gap = np.zeros(int(0.5 * SR), dtype=np.float32)
    full = []
    for i, phrases in enumerate(SCENES):
        parts = [say(tts, ph, args.ref, dyn) for ph in phrases]
        scene = parts[0]
        for p in parts[1:]:
            scene = np.concatenate([scene, gap, p])
        scene = scene / (np.max(np.abs(scene)) + 1e-9) * 0.97
        path = os.path.join(args.out, f"scene_{i}.wav")
        sf.write(path, scene, SR)
        print(f"  scene {i}: {len(scene) / SR:.2f}s -> {path}")
        full.append(scene)

    mix = full[0]
    for s in full[1:]:
        mix = np.concatenate([mix, scene_gap, s])
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.97
    path = os.path.join(args.out, "okf_voiceover.wav")
    sf.write(path, mix, SR)
    print(f"\nfull voice-over: {len(mix) / SR:.2f}s -> {path}")


if __name__ == "__main__":
    main()
