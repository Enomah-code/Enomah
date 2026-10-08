"""Bande son commune aux deux variantes : voix + musique (ducking sous la voix) + bruitages.
Les repères SFX sont ceux des animations (temps absolus, voix décalée de 0,3 s).
Usage : python3 scripts/mix.py → shared/audio/mix.wav (puis normalisation -14 LUFS par ffmpeg)
"""
import json
import os
import subprocess

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
DUR = json.load(open(os.path.join(ROOT, "shared/timeline.json")))["duration"]
N = int(SR * DUR)
SFX = [  # (fichier, temps, gain)
    ("whoosh-cinematic", 0.0, .5), ("notification", 3.05, .7), ("pop", 3.45, .45), ("typing", 3.75, .25),
    ("pop", 4.05, .5), ("chime", 4.45, .55), ("impact-bass-1", 4.65, .5),
    ("whoosh", 5.7, .5), ("glitch-1", 6.35, .35), ("glitch-2", 7.65, .35), ("sparkle", 9.75, .45),
    ("whoosh-short", 10.45, .45), ("impact-bass-1", 12.62, .75), ("whoosh", 12.95, .35), ("pop", 14.1, .4), ("pop", 15.35, .35),
    ("whoosh", 16.65, .45), ("impact-bass-2", 16.85, .5), ("whoosh-short", 18.6, .4), ("whoosh-short", 19.28, .4),
    ("whoosh-short", 20.54, .4), ("whoosh-short", 21.73, .4), ("whoosh-short", 22.88, .4), ("chime", 23.95, .35),
    ("whoosh", 24.7, .45), ("typing", 25.25, .3), ("pop", 26.15, .45), ("whoosh-short", 27.95, .4), ("impact-bass-2", 28.55, .5),
    ("whoosh", 29.25, .45), ("pop", 29.5, .35), ("pop", 29.62, .3), ("pop", 29.74, .3), ("pop", 29.86, .3), ("sparkle", 31.9, .45),
    ("whoosh", 33.65, .5), ("typing", 35.2, .35), ("impact-bass-1", 36.6, .6), ("click", 37.7, .5), ("impact-bass-2", 38.1, .55),
    ("chime", 39.8, .45), ("whoosh", 42.2, .5), ("click", 42.92, .6), ("sparkle", 43.75, .4),
]


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


vo = load(os.path.join(ROOT, "shared/vo/vo.wav"))[:N]
vo = np.pad(vo, (0, N - len(vo)))
bgm = load(os.path.join(ROOT, "shared/audio/bgm.wav"))[:N]
bgm = np.pad(bgm, (0, N - len(bgm)))
# ducking : enveloppe de la voix (lissée) → la musique baisse de ~5 dB (≈ -11 dB sous la voix) quand la voix parle
e = np.abs(vo)
win = int(0.12 * SR)
e = np.convolve(e, np.ones(win) / win, mode="same")
talk = np.clip(e / 0.02, 0, 1)
k = int(0.25 * SR)
talk = np.convolve(talk, np.ones(k) / k, mode="same")
bgm_gain = 0.5 * (1 - 0.45 * talk)
sfx = np.zeros(N)
for name, at, g in SFX:
    x = load(os.path.join(ROOT, "shared/sfx", f"{name}.mp3"))
    i = int(at * SR)
    x = x[: N - i]
    sfx[i:i + len(x)] += x * g * 0.7
mix = vo * 1.0 + bgm * bgm_gain + sfx
mix /= max(1.0, np.abs(mix).max() / 0.97)
tmp = os.path.join(ROOT, "shared/audio/mix-pre.wav")
sf.write(tmp, mix, SR)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-af",
                "alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000", "-ac", "2",
                os.path.join(ROOT, "shared/audio/mix.wav")], check=True)
os.remove(tmp)
print("mix ok")
