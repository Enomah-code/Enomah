"""Music bed for the UGC Meta ad: 44.4 s, D minor, soft pulse, ducked under the voice-over.
Deterministic. Whooshes before every scene cut, impacts on key beats."""
import json, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR = 48000; DUR = 44.4; N = int(SR * DUR)
rng = np.random.default_rng(11); t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
CUTS = [3.1, 9.55, 13.05, 15.9, 19.1, 22.35, 26.4, 34.3, 40.1]
BIG = [7.1, 32.4, 40.1]
def at(s): return int(s * SR)
def add(sig, start, g=1.0, pan=0.0):
    i = at(start); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * g; L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi, o=1): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR); sus = max(0, n - a - d - r)
    return np.concatenate([np.linspace(0, 1, a, False), np.linspace(1, s, d, False), np.full(sus, s), np.linspace(s, 0, r)])[:n]
def saw(f, n, ph=0.0): x = (np.arange(n) / SR * f + ph) % 1.0; return 2 * x - 1

# pad — 4 s chords
chords = [[50, 57, 60, 64, 69], [46, 53, 57, 62, 65], [43, 50, 53, 58, 62], [45, 52, 55, 61, 64]]
pad = np.zeros(N); s0 = 0.0; k = 0
while s0 < DUR:
    n = int(5.5 * SR); seg = np.zeros(n)
    for m in chords[k % 4]:
        for det in (-0.1, 0.0, 0.09): seg += saw(midi(m) * 2 ** (det / 12), n, rng.random()) / 15
    seg = lp(seg, 1200) * adsr(n, 1.4, 0.6, 0.85, 1.8)
    i = at(s0); j = min(N, i + n); pad[i:j] += seg[: j - i]; s0 += 4.0; k += 1
pad = lp(pad, 2200) * np.clip(t / 2.0, 0, 1)
add(pad, 0, 0.5, -0.15); add(np.roll(pad, int(0.015 * SR)), 0, 0.5, 0.15)

# soft pulse (kick + bass) — energy sections only
def kick(n=int(0.45 * SR)):
    tt = np.arange(n) / SR; f = 42 + 68 * np.exp(-tt * 38)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)
def hat(n=int(0.06 * SR)): tt = np.arange(n) / SR; return hp(rng.standard_normal(n), 7500) * np.exp(-tt * 70)
def on(s): return 0.0 <= s < 43.6
K = kick(); s = 0.0
while s < 43.6:
    if on(s):
        add(K, s, 0.42)
        add(hat(), s + 0.25, 0.09, 0.3); add(hat(), s + 0.125, 0.04, -0.3)
        if int(round(s * 2)) % 4 == 0:
            n = int(0.9 * SR); f = midi([38, 34, 31, 33][int(s // 4) % 4])
            add(lp(np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.3 * saw(f, n), 380) * adsr(n, 0.005, 0.25, 0.4, 0.5), s, 0.28)
    s += 0.5

def whoosh(d=0.7):
    n = int(d * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        fc = 300 + 5000 * (i / n) ** 2; out[i:i + blk] = bp(x[i:i + blk], max(80, fc * 0.6), fc * 1.4)[:blk]
    return out * (tt / d) ** 2.2
def impact(n=int(2.4 * SR), big=1.0):
    tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (36 + 40 * np.exp(-tt * 12)) * tt) * np.exp(-tt * 2.8)
    shim = hp(rng.standard_normal(n), 5000) * np.exp(-tt * 5) * 0.18
    bell = sum(np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * 2.0) for m in (74, 81, 86)) * 0.07 * big
    return boom + shim + bell
for c in CUTS:
    w = whoosh(); add(w, c - 0.55, 0.22, -0.3); add(w, c - 0.55, 0.16, 0.3); add(impact(), c, 0.18)
for c in BIG: add(impact(int(3.6 * SR), 1.5), c, 0.5)

# riser into the reveal and the outro
for end in (7.1, 40.1):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    add(hp(rng.standard_normal(n), 2000) * (tt / 2.0) ** 3, end - 2.0, 0.12)

def reverb(x, secs=2.6, mix=0.24):
    n = int(secs * SR); tt = np.arange(n) / SR
    ir = lp(rng.standard_normal(n) * np.exp(-tt * 3.0), 5000); ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - mix) + fftconvolve(x, ir)[: len(x)] * mix
L = reverb(L); R = reverb(R)

# sidechain duck under the voice (≈ -8 dB while speaking, smooth)
sr_v, v = wavfile.read("assets/voice.wav"); v = v.astype(np.float64); v = v if v.ndim == 1 else v.mean(1)
v = np.pad(np.abs(v) / (np.abs(v).max() + 1e-9), (0, max(0, N - len(v))))[:N]
env = lp(v, 3.0, 1); env = env / (env.max() + 1e-9)
gate = np.clip(env * 6, 0, 1); gate = lp(gate, 2.0, 1)
duck = 1.0 - 0.62 * np.clip(gate, 0, 1)
L *= duck; R *= duck
fade = np.clip((DUR - t) / 3.0, 0, 1); L *= fade; R *= fade
st = np.stack([L, R], 1); st = np.tanh(st * 1.3) / np.tanh(1.3); st *= 0.5 / np.max(np.abs(st))
wavfile.write("assets/music.wav", SR, (st * 32767).astype(np.int16)); print("ok")
