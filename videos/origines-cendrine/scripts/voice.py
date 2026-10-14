"""Construit la piste voix du montage (assets/audio/voice.wav) + scripts/timeline.json.

- Voix off (voixoff.aac) : débruitage, coupe-bas, compression douce, niveau homogène.
- Passages en son direct (rushs) : même traitement + égalisation pour se rapprocher de la voix off.
Chaque segment de scripts/edl.json est posé bout à bout ; la durée vidéo d'un segment = durée de son audio
(ou `dur` pour les segments sans voix).
Usage : python3 scripts/voice.py <dossier_rushs>
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
CLEAN = "highpass=f=80,afftdn=nr=14:nf=-48:tn=1,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.5:g=2,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2"


def load(path, t0, t1, extra=""):
    af = CLEAN + ("," + extra if extra else "")
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", path, "-af", af,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


SYNC_CHAIN = ("highpass=f=90,equalizer=f=320:t=q:w=1.2:g=-3,equalizer=f=2800:t=q:w=1.4:g=3.5,"
              "equalizer=f=9000:t=q:w=1.5:g=2,deesser=i=0.35,"
              "acompressor=threshold=-24dB:ratio=3.5:attack=6:release=110:makeup=3,alimiter=limit=0.9")


def sync_voice(path, t0, t1):
    """Son direct d'un rush : réduction de bruit spectrale (profil pris sur le passage le plus calme du rush),
    puis égalisation « voix » (présence, clarté), de-esser et compression pour l'amener au niveau de la voix off."""
    import noisereduce as nr
    full = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-af", "highpass=f=80",
                           "-f", "f32le", "-"], capture_output=True, check=True).stdout
    full = np.frombuffer(full, np.float32).astype(np.float64)
    win = int(0.6 * SR)
    hop = int(0.1 * SR)
    rms = [np.sqrt(np.mean(full[i:i + win] ** 2)) for i in range(0, len(full) - win, hop)]
    i0 = int(np.argmin(rms)) * hop
    noise = full[i0:i0 + win]
    seg = full[int(t0 * SR):int(t1 * SR)]
    den = nr.reduce_noise(y=seg, sr=SR, y_noise=noise, stationary=True, prop_decrease=0.85, n_fft=2048)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", SYNC_CHAIN,
                          "-f", "f32le", "-"], input=den.astype(np.float64).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def loud(x):
    """niveau RMS des passages parlés (dBFS) — pour aligner voix off et son direct"""
    win = int(0.05 * SR)
    r = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
    sp = r[r > np.percentile(r, 60)]
    return 20 * np.log10(np.sqrt(np.mean(sp ** 2)) + 1e-9)


def fade(x, a=0.03, b=0.06):
    na, nb = int(a * SR), int(b * SR)
    x = x.copy()
    x[:na] *= np.linspace(0, 1, na)
    x[-nb:] *= np.linspace(1, 0, nb)
    return x


def main():
    rush = sys.argv[1]
    edl = json.load(open(os.path.join(ROOT, "scripts/edl.json")))
    target = -20.0
    t = 0.0
    segs, track = [], []
    for seg in edl["segments"]:
        if seg.get("audio") == "vo":
            x = load(os.path.join(rush, "voixoff.aac"), *seg["vo"])
        elif seg.get("audio") == "sync":
            sh = seg["shots"][0]
            x = sync_voice(os.path.join(rush, sh["src"]), sh["in"], sh["out"])
        else:
            x = None
        if x is not None:
            # son direct un peu plus présent que la voix off (+2 dB), comme demandé
            tgt = target + (2.0 if seg.get("audio") == "sync" else 0.0)
            x = fade(x * 10 ** ((tgt - loud(x)) / 20))
            dur = len(x) / SR
        else:
            dur = seg["dur"]
            x = np.zeros(int(dur * SR))
        segs.append({"id": seg["id"], "start": round(t, 3), "dur": round(dur, 3), "audio": seg.get("audio")})
        track.append(x)
        t += dur
    voice = np.concatenate(track)
    voice /= max(1.0, np.abs(voice).max() / 0.95)
    os.makedirs(os.path.join(ROOT, "assets/audio"), exist_ok=True)
    sf.write(os.path.join(ROOT, "assets/audio/voice.wav"), voice, SR)
    json.dump({"duration": round(t, 3), "segments": segs}, open(os.path.join(ROOT, "scripts/timeline.json"), "w"), indent=1)
    for s in segs:
        print(s)
    print("total", round(t, 2))


if __name__ == "__main__":
    main()
