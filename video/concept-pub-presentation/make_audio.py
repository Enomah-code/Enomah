"""Procedural soundtrack for the Concept Pub film — 48 s, 120 BPM, D minor.
Deterministic (seeded). Pad + sub pulse + hats + whooshes/impacts on scene cuts."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 48.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

def at(sec): return int(sec * SR)
def add(sig, start, gain=1.0, pan=0.0):
    i = at(start); j = min(N, i + len(sig)); sig = sig[: j - i] * gain
    L[i:j] += sig * np.sqrt(0.5 * (1 - pan)); R[i:j] += sig * np.sqrt(0.5 * (1 + pan))
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def env_adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR); sus = max(0, n - a - d - r)
    return np.concatenate([np.linspace(0, 1, a, False), np.linspace(1, s, d, False), np.full(sus, s), np.linspace(s, 0, r)])[:n]

BEAT = 0.5
CUTS = [4.5, 9.0, 15.5, 22.5, 26.5, 31.5, 37.0, 42.5]

# ---------- pad (detuned saws, slow filter) ----------
chords = [[50, 57, 60, 64, 69], [46, 53, 57, 62, 65], [43, 50, 53, 58, 62], [45, 52, 55, 61, 64]]  # Dm9 Bbmaj7 Gm9 A7sus-ish
def saw(f, n, ph=0.0):
    x = (np.arange(n) / SR * f + ph) % 1.0
    return 2 * x - 1
pad = np.zeros(N)
bar = 4.0
k = 0; s0 = 0.0
while s0 < DUR:
    ch = chords[k % 4]; n = int((bar + 1.5) * SR)
    seg = np.zeros(n)
    for m in ch:
        for det in (-0.12, 0.0, 0.11):
            seg += saw(midi(m) * 2 ** (det / 12), n, rng.random()) / 15
    seg = lp(seg, 1400) * env_adsr(n, 1.2, 0.5, 0.85, 1.6)
    i = at(s0); j = min(N, i + n); pad[i:j] += seg[: j - i]
    s0 += bar; k += 1
# filter swell over time
pad = lp(pad, 2600) * (0.55 + 0.25 * np.sin(2 * np.pi * t / 16.0) ** 2)
# duck pad briefly at start (intro flashes) and fade in
pad *= np.clip(t / 1.4, 0, 1)
add(pad, 0, 0.55, -0.1); add(np.roll(pad, int(0.013 * SR)), 0, 0.55, 0.1)

# ---------- sub kick pulse ----------
def kick(n=int(0.45 * SR), f0=110, f1=42):
    tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 38)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 7.5) + 0.06 * rng.standard_normal(n) * np.exp(-tt * 120)
K = kick()
def active(sec):
    return (4.5 <= sec < 22.3) or (26.5 <= sec < 42.3)
sec = 4.5
while sec < 42.5:
    if active(sec):
        add(K, sec, 0.55 if (sec * 2) % 2 == 0 else 0.42)
    sec += BEAT

# ---------- hats / ticks ----------
def hat(n=int(0.07 * SR)):
    tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-tt * 60)
sec = 9.0
while sec < 42.3:
    if active(sec):
        add(hat(), sec + 0.25, 0.10, 0.35)
        if 31.5 <= sec: add(hat(), sec + 0.125, 0.045, -0.35)
    sec += BEAT

# ---------- bass pluck on bar downbeats ----------
roots = [38, 34, 31, 33]
sec = 4.5; k = 0
while sec < 42.5:
    if active(sec):
        n = int(0.9 * SR); f = midi(roots[int(sec // 4) % 4])
        b = np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.35 * saw(f, n)
        add(lp(b, 400) * env_adsr(n, 0.005, 0.25, 0.4, 0.5), sec, 0.32)
    sec += 1.0

# ---------- whoosh + impact on each cut ----------
def whoosh(d=0.75):
    n = int(d * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n); out = np.zeros(n)
    blk = 1024
    for i in range(0, n, blk):
        p = i / n; fc = 300 + 5200 * p ** 2
        out[i:i + blk] = bp(x[i:i + blk + 0], max(80, fc * 0.6), min(SR / 2 - 100, fc * 1.4), 1)[: blk]
    e = (tt / d) ** 2.2
    return out * e
def impact(n=int(2.2 * SR)):
    tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 12)) * tt) * np.exp(-tt * 3.0)
    shimmer = hp(rng.standard_normal(n), 5000) * np.exp(-tt * 5) * 0.22
    bell = sum(np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * 2.2) for m in (74, 81, 86)) * 0.08
    return boom + shimmer + bell
for c in CUTS:
    w = whoosh(); add(w, c - len(w) / SR, 0.35, -0.4); add(w, c - len(w) / SR, 0.25, 0.4)
    add(impact(), c, 0.42)

# intro word flashes: short tonal ticks
for i in range(5):
    tt = np.arange(int(0.18 * SR)) / SR
    tick = np.sin(2 * np.pi * midi(74 + [0, 3, 7, 10, 12][i]) * tt) * np.exp(-tt * 28) + hp(rng.standard_normal(len(tt)), 3000) * np.exp(-tt * 80) * 0.4
    add(tick, 0.1 + i * 0.28, 0.35, -0.3 + 0.15 * i)
# logo reveal + outro hits: big
add(impact(int(3.5 * SR)), 1.55, 0.6)
add(impact(int(4.0 * SR)), 43.0, 0.7)
# riser into outro
n = int(1.8 * SR); tt = np.arange(n) / SR
riser = hp(rng.standard_normal(n), 2000) * (tt / 1.8) ** 3
add(riser, 42.5 - 1.8 + 0.5, 0.18)
# service switches: soft clicks
for i in range(9):
    tt = np.arange(int(0.05 * SR)) / SR
    add(hp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 90), 9.4 + i * 0.62, 0.12, 0.2)
# devis checkmarks: little chimes
for i in range(4):
    tt = np.arange(int(0.6 * SR)) / SR
    add(np.sin(2 * np.pi * midi(81 + [0, 2, 5, 9][i]) * tt) * np.exp(-tt * 9), 37.6 + i * 0.55, 0.12, 0.25)

# ---------- reverb ----------
def reverb(x, secs=2.4, mix=0.22):
    n = int(secs * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.2); ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - mix) + fftconvolve(x, ir)[: len(x)] * mix
L = reverb(L); R = reverb(R)

# end fade + gentle glue
fade = np.clip((DUR - t) / 2.2, 0, 1)
L *= fade; R *= fade
st = np.stack([L, R], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= 0.89 / np.max(np.abs(st))
wavfile.write("assets/soundtrack.wav", SR, (st * 32767).astype(np.int16))
print("ok", st.shape)
