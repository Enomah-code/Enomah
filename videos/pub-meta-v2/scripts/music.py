"""Musique de fond v2, 100 % synthétisée (libre de droits), 110 BPM, calée sur shared/timeline.json.
0 → 5,75 s : suspense (3 h du matin : nappe grave + tic-tac) ; 5,75 → 12,65 : groove demi-régime ;
12,65 s (révélation du logo) : drop afro-pop complet ; 42,25 s : CTA, coupure + impact puis nappe.
Usage : python3 scripts/music.py → shared/audio/bgm.wav
"""
import json
import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "shared/timeline.json")))
SR, DUR, BPM = 48000, TL["duration"], 110
BEAT = 60 / BPM
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)
SANS, DROP, CTA = 5.75, 12.65, 42.25


def env(n, a, d):
    e = np.ones(n)
    ka = max(1, int(a * SR))
    e[:ka] = np.linspace(0, 1, ka)
    e[ka:] = np.exp(-np.arange(n - ka) / (d * SR))
    return e


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    x = x[: N - i]
    buf[i:i + len(x)] += x * g


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def band(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


kn = int(0.5 * SR); kt = np.arange(kn) / SR
KICK = np.sin(2 * np.pi * (46 * kt + 110 * (1 - np.exp(-kt * 30)) / 30)) * env(kn, 0.002, 0.18)
cn = int(0.25 * SR)
CLAP = band(rng.standard_normal(cn), 900, 5200) * env(cn, 0.001, 0.07)
sn = int(0.06 * SR)
SHK = sosfilt(butter(2, 6500, "high", fs=SR, output="sos"), rng.standard_normal(sn)) * env(sn, 0.003, 0.018)
tn = int(0.05 * SR)
TICK = band(rng.standard_normal(tn), 2500, 8000) * env(tn, 0.0005, 0.008)

CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
RT = [45, 41, 48, 43]
drums, bass, pad, keys = (np.zeros(N) for _ in range(4))
bars = int(DUR / (4 * BEAT)) + 2
for b in range(bars):
    t0 = b * 4 * BEAT
    ch, rt = CH[b % 4], RT[b % 4]
    n = int(4 * BEAT * SR + 0.5 * SR); pt = np.arange(n) / SR
    p = sum(np.sin(2 * np.pi * hz(m) * pt + 0.25 * np.sin(2 * np.pi * 0.4 * pt)) + 0.4 * np.sin(2 * np.pi * hz(m) * 2.004 * pt) for m in ch)
    add(pad, p * env(n, 0.4, 3.0), t0, 0.05)
    for k in range(16):
        st = t0 + k * BEAT / 4
        sw = 0.016 if k % 2 else 0
        if st < SANS:                          # suspense
            if k % 4 == 0:
                add(drums, TICK, st, 0.5)
            if k in (0, 3):
                add(drums, KICK, st, 0.28 if k == 0 else 0.18)
        elif st < DROP or st >= CTA:           # demi-régime / CTA
            if st >= CTA:
                continue
            if k == 0 or k == 10:
                add(drums, KICK, st, 0.8)
            if k == 8:
                add(drums, CLAP, st, 0.45)
            if k % 2 == 0:
                add(drums, SHK, st + sw, 0.12)
            if k in (0, 10):
                bn = int(0.4 * SR); bt = np.arange(bn) / SR
                add(bass, np.tanh(2 * np.sin(2 * np.pi * hz(rt) * bt)) * env(bn, 0.004, 0.2), st, 0.28)
        else:                                  # drop
            if k in (0, 6, 8, 11):
                add(drums, KICK, st, 1 if k in (0, 8) else 0.55)
            if k in (4, 12):
                add(drums, CLAP, st, 0.55)
            add(drums, SHK, st + sw, 0.22 if k % 2 else 0.12)
            if k in (0, 3, 6, 8, 10, 14):
                bn = int(0.32 * SR); bt = np.arange(bn) / SR
                f = hz(rt + (12 if k == 10 else 0))
                add(bass, np.tanh(2.4 * np.sin(2 * np.pi * f * bt)) * env(bn, 0.004, 0.14), st, 0.32)
            if k % 2 == 0:
                m = ch[(k // 2) % 3] + 12 + (12 if k in (6, 14) else 0)
                pn = int(0.4 * SR); pp = np.arange(pn) / SR; f = hz(m)
                x = (np.sin(2 * np.pi * f * pp) + 0.3 * np.sin(2 * np.pi * 4 * f * pp) * np.exp(-pp * 40)) * env(pn, 0.002, 0.11)
                add(keys, x, st + sw, 0.09)

mix = drums + bass + pad + keys
# suspense : tout passe dans un passe-bas
lp = sosfilt(butter(2, 600, "low", fs=SR, output="sos"), mix)
k = np.clip((t - (SANS - 0.3)) / 0.3, 0, 1)
mix = lp * (1 - k) + mix * k
# riser vers le drop + impact
rn = int(1.8 * SR)
add(mix, band(rng.standard_normal(rn), 1200, 9000) * np.linspace(0, 1, rn) ** 2.2, DROP - 1.8, 0.14)
add(mix, KICK * 1.4 + band(rng.standard_normal(kn), 60, 400) * env(kn, 0.001, 0.25) * 0.6, DROP, 0.9)
add(mix, KICK * 1.4, CTA, 0.9)
mix *= np.clip((DUR - t) / 2.0, 0, 1)
mix /= np.abs(mix).max() / 0.9
os.makedirs(os.path.join(ROOT, "shared/audio"), exist_ok=True)
sf.write(os.path.join(ROOT, "shared/audio/bgm.wav"), np.stack([mix, np.roll(mix, int(0.011 * SR)) * 0.96], 1), SR)
print("bgm ok", DUR)
