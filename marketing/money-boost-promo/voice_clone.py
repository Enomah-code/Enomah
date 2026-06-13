#!/usr/bin/env python3
"""
Exact voice-clone of the reference promo voice-over → build/vo/scene_*.wav.

Uses Coqui XTTS-v2 (zero-shot multilingual cloning) to reproduce the *timbre*
of the reference speaker, while keeping the exact same script and posed cadence
as the Piper path (short phrases re-assembled with GAP silences, from script_vo).

Requires HuggingFace access (the XTTS-v2 weights live there). This repo's default
environment network policy blocks HuggingFace; run this from a session whose
environment allows huggingface.co, then mix with:

    COQUI_TOS_AGREED=1 python3 voice_clone.py --ref /path/to/reference.wav
    VO_USE_EXISTING=1  python3 soundtrack.py
    bash build.sh

--ref may be an audio file (wav/mp3) or a video; video audio is auto-extracted.
A clean 6–20s speech excerpt makes the best clone, so by default we pick the
loudest ~16s speech window from the reference.
"""
import os, sys, argparse, subprocess, wave
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 44100
VO_DIR = os.path.join(ROOT, 'build', 'vo')
os.makedirs(VO_DIR, exist_ok=True)
sys.path.insert(0, ROOT)
from script_vo import SCENES, GAP

os.environ.setdefault('COQUI_TOS_AGREED', '1')


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def to_wav_mono(path, out, sr=SR):
    """Decode any audio/video file to mono wav at `sr`."""
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-i', path,
                    '-vn', '-ac', '1', '-ar', str(sr), out], check=True)


def load_mono(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32)
    if x.dtype == np.int16 or x.max() > 1.5:
        x = x / 32768.0
    if x.ndim > 1:
        x = x.mean(axis=1)
    return sr, x


def best_speech_window(x, sr, win=16.0):
    """Pick the loudest contiguous `win`-second region (skips silence/music gaps)."""
    if len(x) <= int(win * sr):
        return x
    hop = int(0.2 * sr)
    fl = int(win * sr)
    energies = [(np.mean(x[i:i+fl] ** 2), i) for i in range(0, len(x) - fl, hop)]
    _, i0 = max(energies)
    return x[i0:i0 + fl]


def prepare_reference(ref_path):
    """Return a clean 24kHz speaker reference wav path for XTTS."""
    tmp = os.path.join(VO_DIR, '_ref_full.wav')
    to_wav_mono(ref_path, tmp, sr=24000)
    sr, x = load_mono(tmp)
    x = best_speech_window(x, sr, win=16.0)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.97
    out = os.path.join(VO_DIR, '_speaker_ref.wav')
    wavfile.write(out, sr, (x * 32767).astype(np.int16))
    print(f"speaker reference: {len(x)/sr:.1f}s @ {sr}Hz -> {out}")
    return out


def trim(clip, sr):
    thr = 0.012 * np.max(np.abs(clip) + 1e-9)
    idx = np.where(np.abs(clip) > thr)[0]
    if len(idx):
        clip = clip[max(0, idx[0]-int(0.03*sr)): idx[-1]+int(0.06*sr)]
    return clip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', required=True, help='reference audio or video file')
    ap.add_argument('--model', default='tts_models/multilingual/multi-dataset/xtts_v2')
    args = ap.parse_args()

    speaker_wav = prepare_reference(args.ref)

    from TTS.api import TTS
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"loading {args.model} on {dev} …")
    tts = TTS(args.model).to(dev)

    gap = np.zeros(int(GAP * SR), dtype=np.float32)
    for i, (_, phrases) in enumerate(SCENES):
        if isinstance(phrases, str):
            phrases = [phrases]
        parts = []
        for ph in phrases:
            wav = np.asarray(tts.tts(text=ph, speaker_wav=speaker_wav, language='fr'),
                             dtype=np.float32)
            # XTTS outputs 24kHz -> resample to project SR
            wav = resample_poly(wav, SR, 24000)
            parts.append(trim(wav, SR))
        out = parts[0]
        for p in parts[1:]:
            out = np.concatenate([out, gap, p])
        out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
        path = os.path.join(VO_DIR, f'scene_{i}.wav')
        wavfile.write(path, SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
        print(f"  cloned VO scene {i}: {len(out)/SR:.2f}s -> {path}")

    print("\nDone. Now run:\n  VO_USE_EXISTING=1 python3 soundtrack.py\n  bash build.sh")


if __name__ == '__main__':
    main()
