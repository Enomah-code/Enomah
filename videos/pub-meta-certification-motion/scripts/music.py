"""Musique de fond synthétisée (100 % procédurale, libre de droits) — groove afro-pop doux, 104 BPM.
Intro filtrée (problème) puis le beat complet s'ouvre sur la révélation de la solution (6,7 s).
Usage : python3 scripts/music.py  → assets/audio/bgm.wav
"""
import os
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, DUR, BPM = 48000, 41.0, 104
BEAT = 60 / BPM
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(3)
DROP, BREAK0, BREAK1 = 6.7, 26.55, 27.1   # ouverture du beat ; mini-break avant « Plus besoin »


def env(n, a, d):
    e = np.ones(n)
    ka = max(1, int(a * SR))
    e[:ka] = np.linspace(0, 1, ka)
    e[ka:] = np.exp(-np.arange(n - ka) / (d * SR))
    return e


def add(buf, x, at):
    i = int(at * SR)
    if i >= N:
        return
    x = x[: N - i]
    buf[i:i + len(x)] += x


def note(f):
    return 440 * 2 ** ((f - 69) / 12)


drums = np.zeros(N)
bass = np.zeros(N)
pad = np.zeros(N)
pluck = np.zeros(N)

kick_n = int(0.45 * SR)
kt = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * (48 * kt + 90 * (1 - np.exp(-kt * 28)) / 28)) * env(kick_n, 0.002, 0.16)
clap_n = int(0.25 * SR)
clap = sosfilt(butter(2, [900, 5000], "band", fs=SR, output="sos"), rng.standard_normal(clap_n)) * env(clap_n, 0.001, 0.06)
shk_n = int(0.06 * SR)
shk = sosfilt(butter(2, 6000, "high", fs=SR, output="sos"), rng.standard_normal(shk_n)) * env(shk_n, 0.003, 0.018)

# progression : Am – F – C – G (2 temps chacune ×2 = 1 mesure/accord)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
roots = [45, 41, 48, 43]
bars = int(DUR / (4 * BEAT)) + 2
for b in range(bars):
    t0 = b * 4 * BEAT
    ch, rt = chords[b % 4], roots[b % 4]
    # pad (toujours)
    n = int(4 * BEAT * SR) + int(0.4 * SR)
    pt = np.arange(n) / SR
    p = sum(np.sin(2 * np.pi * note(m) * pt + 0.3 * np.sin(2 * np.pi * 0.5 * pt)) +
            0.5 * np.sin(2 * np.pi * note(m) * 2.003 * pt) for m in ch)
    add(pad, p * env(n, 0.35, 2.5) * 0.06, t0)
    for k in range(16):
        st = t0 + k * BEAT / 4
        swing = 0.018 if k % 2 else 0
        if st >= DROP:
            if k in (0, 6, 8, 11):
                add(drums, kick * (1 if k in (0, 8) else 0.55), st)
            if k in (4, 12):
                add(drums, clap * 0.5, st)
            add(drums, shk * (0.22 if k % 2 else 0.12), st + swing)
            # basse syncopée
            if k in (0, 3, 6, 8, 10, 14):
                bn = int(0.32 * SR)
                bt = np.arange(bn) / SR
                f = note(rt + (12 if k == 10 else 0))
                bx = np.tanh(2.2 * np.sin(2 * np.pi * f * bt)) * env(bn, 0.004, 0.14)
                add(bass, bx * 0.32, st)
            # pluck marimba en arpège
            if k % 2 == 0:
                m = ch[(k // 2) % 3] + 12 + (12 if k in (6, 14) else 0)
                pn = int(0.4 * SR)
                ptt = np.arange(pn) / SR
                f = note(m)
                px = (np.sin(2 * np.pi * f * ptt) + 0.3 * np.sin(2 * np.pi * 4 * f * ptt) * np.exp(-ptt * 40)) * env(pn, 0.002, 0.11)
                add(pluck, px * 0.09, st + swing)
        elif k in (0, 8):
            add(drums, kick * 0.35, st)   # intro : pulsation feutrée

mix = drums + bass + pad + pluck
# intro filtrée (passe-bas qui s'ouvre) jusqu'à la révélation
lp = sosfilt(butter(2, 700, "low", fs=SR, output="sos"), mix)
k = np.clip((t - (DROP - 0.6)) / 0.6, 0, 1)
mix = lp * (1 - k) + mix * k
# mini-break : on coupe tout sauf le pad juste avant « Plus besoin… »
br = ((t >= BREAK0) & (t < BREAK1))
mix = np.where(br, pad, mix)
# riser de bruit avant le drop
rn = int(1.6 * SR)
riser = sosfilt(butter(2, [1500, 9000], "band", fs=SR, output="sos"), rng.standard_normal(rn)) * np.linspace(0, 1, rn) ** 2 * 0.12
add(mix, riser, DROP - 1.6)
# fondu de fin
mix *= np.clip((DUR - t) / 1.8, 0, 1)
mix /= np.abs(mix).max() / 0.9
st = np.stack([mix, np.roll(mix, int(0.012 * SR)) * 0.96], 1)
os.makedirs(os.path.join(ROOT, "assets/audio"), exist_ok=True)
sf.write(os.path.join(ROOT, "assets/audio/bgm.wav"), st, SR)
print("ok", DUR)
