#!/usr/bin/env python3
"""Build a clean speaker reference from a noisy promo (video or audio).

Pipeline:
  1. Decode the source to 44.1 kHz stereo WAV (ffmpeg).
  2. Isolate the voice from the background music with Demucs (htdemucs).
  3. Pick the loudest continuous speech window, normalise, write 24 kHz mono.

The Demucs model is loaded and applied directly (soundfile I/O) so it never
touches the torchcodec backend, which is broken on CPU-only hosts.

Usage:
    python3 prepare_ref.py --src /path/to/promo.mp4 [--out assets/speaker_ref.wav]
    python3 prepare_ref.py --src promo.mp4 --no-isolate   # skip music separation
    python3 prepare_ref.py --src promo.mp4 --window 16     # ref length in seconds
"""
import argparse
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

ROOT = os.path.dirname(os.path.abspath(__file__))


def ffmpeg_bin():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def decode_stereo(src, out, sr=44100):
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", src,
                    "-vn", "-ac", "2", "-ar", str(sr), out], check=True)


def isolate_vocals(wav, sr):
    """Return the Demucs 'vocals' stem for a (samples, ch) float array."""
    import torch
    from demucs.apply import apply_model
    from demucs.pretrained import get_model

    model = get_model("htdemucs")
    model.eval()
    x = torch.from_numpy(wav.T).unsqueeze(0)  # (1, ch, samples)
    with torch.no_grad():
        out = apply_model(model, x, device="cpu", split=True, overlap=0.25,
                          progress=True)[0]  # (sources, ch, samples)
    return out[model.sources.index("vocals")].numpy().T  # (samples, ch)


def best_speech_window(x, sr, win):
    """Loudest contiguous `win`-second region (skips silence / music-only gaps)."""
    fl = int(win * sr)
    if len(x) <= fl:
        return x
    hop = int(0.2 * sr)
    energies = [(float(np.mean(x[i:i + fl] ** 2)), i)
                for i in range(0, len(x) - fl, hop)]
    _, i0 = max(energies)
    return x[i0:i0 + fl]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="reference video or audio file")
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "speaker_ref.wav"))
    ap.add_argument("--window", type=float, default=16.0, help="reference length (s)")
    ap.add_argument("--no-isolate", action="store_true", help="skip music separation")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        stereo = os.path.join(tmp, "stereo.wav")
        decode_stereo(args.src, stereo)
        wav, sr = sf.read(stereo, dtype="float32", always_2d=True)
        print(f"decoded {wav.shape[0] / sr:.1f}s @ {sr}Hz")

        if not args.no_isolate:
            print("isolating vocals with Demucs (htdemucs)…")
            wav = isolate_vocals(wav, sr)

    mono = wav.mean(axis=1)
    seg = best_speech_window(mono, sr, args.window)
    seg = resample_poly(seg, 24000, sr)
    seg = seg / (np.max(np.abs(seg)) + 1e-9) * 0.97

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    sf.write(args.out, seg.astype("float32"), 24000)
    print(f"speaker reference: {len(seg) / 24000:.1f}s @ 24kHz -> {args.out}")


if __name__ == "__main__":
    main()
