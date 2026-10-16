"""Mix final : voix (voice.wav) + musique baissée sous la voix (ducking). Hook sans musique : elle entre à MUSIC_IN.
Sortie : assets/audio/mix.wav (-14 LUFS). Les bruitages sont posés dans la composition HyperFrames.
Usage : python3 scripts/mix.py [début_dans_le_morceau_s]
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
DUR = 110.6
MUSIC_IN = 11.0       # la musique entre sur « Alors, laissez-moi vous raconter… »


def load(path, ss=0.0, t=None, ch=2):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(ss)] + (["-t", str(t)] if t else []) + ["-i", path, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"]
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).astype(np.float64)
    return x.reshape(-1, ch)


def main():
    m0 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    dur = DUR
    n = int(dur * SR)
    voice = load(os.path.join(ROOT, "assets/audio/voice.wav"), ch=1)[:n, 0]
    voice = np.pad(voice, (0, n - len(voice)))
    k = int(MUSIC_IN * SR)
    mus = load(os.path.join(ROOT, "assets/audio/music.mp3"), m0, dur - MUSIC_IN + 1)[:n - k]
    mus = np.pad(mus, ((k, n - k - len(mus)), (0, 0)))
    rms = lambda x: np.sqrt(np.mean(x ** 2)) + 1e-9
    vr = rms(voice[np.abs(voice) > 0.02])
    mus_ref = mus[k:k + int(60 * SR)]
    mus *= (vr * 10 ** (-9 / 20)) / rms(mus_ref)          # musique ~9 dB sous la voix hors ducking
    # enveloppe de parole → ducking supplémentaire de 9 dB (attaque 80 ms, relâche 450 ms)
    e = np.abs(voice)
    w = int(0.05 * SR)
    e = np.convolve(e, np.ones(w) / w, mode="same")
    talk = np.clip(e / (vr * 0.25), 0, 1)
    g = np.empty_like(talk)
    a_up, a_dn = np.exp(-1 / (0.08 * SR)), np.exp(-1 / (0.45 * SR))
    acc = 0.0
    for i, v in enumerate(talk):
        acc = a_up * acc + (1 - a_up) * v if v > acc else a_dn * acc + (1 - a_dn) * v
        g[i] = acc
    duck = 10 ** (-9 * g / 20)
    t = np.arange(n) / SR
    fade = np.clip((t - MUSIC_IN) / 1.5, 0, 1) * np.clip((dur - t) / 2.5, 0, 1)
    mix = voice[:, None] * 1.0 + mus * (duck * fade)[:, None]
    tmp = os.path.join(ROOT, "assets/audio/mix-pre.wav")
    sf.write(tmp, mix / max(1, np.abs(mix).max() / 0.97), SR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-af", "alimiter=limit=0.93,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000",
                    os.path.join(ROOT, "assets/audio/mix.wav")], check=True)
    os.remove(tmp)
    print("mix ok", round(dur, 2), "s")


if __name__ == "__main__":
    main()
