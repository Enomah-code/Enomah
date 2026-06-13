#!/usr/bin/env python3
"""Synthesise a cinematic soundtrack for the Money Boost promo (deterministic, no samples)."""
import numpy as np
from scipy.io import wavfile

SR = 44100
DUR = 43.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

# scene cut times (s)
CUTS = [3.6, 7.2, 11.8, 16.2, 21.6, 29.4, 33.6]
REVEAL = 16.2      # product reveal impact
CTA = 33.6         # cta impact

master = np.zeros(N)

def adsr(start, dur, a, d, s_level, r, peak=1.0):
    """envelope array over full timeline"""
    env = np.zeros(N)
    s0 = int(start * SR)
    L = int(dur * SR)
    if s0 >= N:
        return env
    L = min(L, N - s0)
    seg = np.zeros(L)
    ai = int(a * SR); di = int(d * SR); ri = int(r * SR)
    ai = min(ai, L)
    seg[:ai] = np.linspace(0, peak, ai, endpoint=False)
    di2 = min(di, L - ai)
    seg[ai:ai+di2] = np.linspace(peak, s_level*peak, di2, endpoint=False)
    sus_end = max(L - ri, ai+di2)
    seg[ai+di2:sus_end] = s_level*peak
    rl = L - sus_end
    if rl > 0:
        seg[sus_end:] = np.linspace(s_level*peak, 0, rl)
    env[s0:s0+L] = seg
    return env

def tone(freq, start, dur, env, detune=0.0, kind='saw_soft'):
    s0 = int(start*SR); L = int(dur*SR)
    L = min(L, N-s0)
    if L <= 0: return np.zeros(N)
    tt = np.arange(L)/SR
    ph = 2*np.pi*freq*tt
    if kind == 'sine':
        w = np.sin(ph)
    elif kind == 'tri':
        w = 2/np.pi*np.arcsin(np.sin(ph))
    else:  # soft saw (sum of few harmonics)
        w = np.sin(ph) + 0.5*np.sin(2*ph) + 0.28*np.sin(3*ph) + 0.16*np.sin(4*ph)
        w /= 1.94
    if detune:
        w = 0.5*w + 0.5*(np.sin(2*np.pi*(freq*(1+detune))*tt))
    out = np.zeros(N)
    out[s0:s0+L] = w
    return out * env

# ---- note frequencies ----
def nf(semis_from_a4):
    return 440.0 * 2**(semis_from_a4/12)
# A minor-ish palette
A2, A3, C4, E4, G3, E3, D4, F4 = nf(-24), nf(-12), nf(3), nf(7), nf(-2), nf(-5), nf(5), nf(8)

# ============ 1. PAD BED (evolving) ============
# Section 1: brooding (0 -> reveal): Am  (A, C, E)
pad1_env = adsr(0.0, REVEAL+0.6, a=1.4, d=2.0, s_level=0.85, r=1.2, peak=0.16)
# slow tremolo
trem = 1 + 0.12*np.sin(2*np.pi*0.18*t)
for f,det in [(A3,0.004),(C4,0.005),(E4,0.004),(A2,0.0)]:
    master += tone(f,0.0,REVEAL+0.6,pad1_env,detune=det,kind='tri')*trem*0.55

# Section 2: uplifting (reveal -> end): C major add9 (C,E,G,D) warmer/brighter
pad2_env = adsr(REVEAL-0.2, DUR-REVEAL+0.5, a=0.8, d=1.5, s_level=0.9, r=2.2, peak=0.18)
trem2 = 1 + 0.08*np.sin(2*np.pi*0.22*t)
for f,det in [(C4,0.004),(E4,0.005),(G3,0.003),(D4,0.004),(A2,0.0)]:
    master += tone(f,REVEAL-0.2,DUR-REVEAL+0.5,pad2_env,detune=det,kind='tri')*trem2*0.5

# shimmer high layer in section 2
sh_env = adsr(REVEAL, DUR-REVEAL, a=1.2, d=1.0, s_level=0.7, r=2.0, peak=0.05)
master += tone(nf(19),REVEAL,DUR-REVEAL,sh_env,kind='sine')*0.6
master += tone(nf(24),REVEAL,DUR-REVEAL,sh_env,kind='sine')*0.4

# ============ 2. SUB BASS pulse (from reveal) ============
BPM = 100
beat = 60.0/BPM
def kick(start, gain=0.9):
    s0=int(start*SR)
    L=int(0.32*SR)
    if s0>=N: return
    L=min(L,N-s0)
    tt=np.arange(L)/SR
    f=110*np.exp(-tt*22)+45
    env=np.exp(-tt*9)
    w=np.sin(2*np.pi*np.cumsum(f)/SR)*env*gain
    master[s0:s0+L]+=w

def shaker(start, gain=0.18):
    s0=int(start*SR); L=int(0.10*SR)
    if s0>=N: return
    L=min(L,N-s0)
    nse=rng.standard_normal(L)
    env=np.exp(-np.arange(L)/SR*40)
    # crude high-pass: differentiate
    nse=np.diff(nse,prepend=nse[0])
    master[s0:s0+L]+=nse*env*gain

# groove starts a bit before reveal builds, full from reveal to ~CTA, lighter after
beat_t = REVEAL
groove_end = DUR-1.0
i=0
while beat_t < groove_end:
    # main kick on each beat
    g = 0.85
    if beat_t < REVEAL+0.01: g=1.0
    kick(beat_t, gain=g)
    # offbeat shaker
    shaker(beat_t+beat/2)
    shaker(beat_t+beat/4, gain=0.10)
    beat_t += beat
    i+=1

# sub bassline following sections (root notes)
def subnote(freq,start,dur,gain=0.22):
    env=adsr(start,dur,a=0.02,d=0.1,s_level=0.8,r=0.15,peak=gain)
    return tone(freq,start,dur,env,kind='sine')
bass_seq = [(A2,REVEAL,4.0),(A2,REVEAL+4,5.4),(nf(-21),REVEAL+9.4,4.0),(A2,REVEAL+13.4,DUR-(REVEAL+13.4))]
for f,s,d in bass_seq:
    master += subnote(f,s,d)

# ============ 3. RISERS before reveal & cta ============
def riser(end, length=3.0, gain=0.18):
    s0=int((end-length)*SR); L=int(length*SR)
    if s0<0:
        L+=s0; s0=0
    if L<=0: return
    tt=np.arange(L)/SR
    nse=rng.standard_normal(L)
    # rising bandpass-ish via increasing high-freq emphasis (cumulative diff)
    nse=np.cumsum(nse); nse-=np.mean(nse); nse/=np.max(np.abs(nse))+1e-9
    swirl=np.sin(2*np.pi*(200+ (tt/length)**2*3000)*tt)*0.5
    env=(tt/length)**2.2
    master[s0:s0+L]+= (nse*0.5+swirl)*env*gain

riser(REVEAL, length=3.2, gain=0.2)
riser(CTA, length=2.4, gain=0.16)

# ============ 4. IMPACTS (boom) at reveal & cta ============
def impact(start, gain=0.95):
    s0=int(start*SR); L=int(2.2*SR)
    if s0>=N: return
    L=min(L,N-s0)
    tt=np.arange(L)/SR
    # low boom
    f=70*np.exp(-tt*4)+38
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.2)
    # noise hit
    nse=rng.standard_normal(L)*np.exp(-tt*16)
    sig=(boom*0.9+nse*0.25)*gain
    master[s0:s0+L]+=sig
impact(REVEAL,0.95)
impact(CTA,0.85)

# ============ 5. WHOOSH at scene transitions ============
def whoosh(center, gain=0.22, length=0.9):
    s0=int((center-length*0.6)*SR); L=int(length*SR)
    if s0<0: L+=s0; s0=0
    if L<=0 or s0>=N: return
    L=min(L,N-s0)
    tt=np.arange(L)/SR
    nse=rng.standard_normal(L)
    # band emphasis sweep down
    nse=np.diff(nse,prepend=nse[0])
    env=np.sin(np.pi*np.clip(tt/length,0,1))**1.5
    master[s0:s0+L]+=nse*env*gain
for c in CUTS:
    whoosh(c, gain=0.20)

# ============ 6. sparkle bells on counter & stars ============
def bell(freq,start,gain=0.12,dur=1.2):
    env=adsr(start,dur,a=0.005,d=0.4,s_level=0.0,r=0.3,peak=gain)
    return tone(freq,start,dur,env,kind='sine')+0.4*tone(freq*2.01,start,dur,env*0.5,kind='sine')
for k,st in enumerate([7.4,8.2,9.0,9.8]):
    master += bell(nf(12+k*3),st,gain=0.10,dur=1.0)
# stars ding (~t 30.6 in scene7 -> abs 29.4+1.2)
master += bell(nf(24),30.6,gain=0.13,dur=1.4)

# ============ master processing ============
# gentle low-shelf warmth via simple one-pole, soft saturation, limiter
# soft saturation
master = np.tanh(master*1.1)
# normalise to -1.5 dBFS
peak = np.max(np.abs(master))+1e-9
master = master/peak*0.84
# fade in/out
fin=int(0.5*SR); fout=int(1.6*SR)
master[:fin]*=np.linspace(0,1,fin)
master[-fout:]*=np.linspace(1,0,fout)

stereo=np.stack([master,master],axis=1)
wavfile.write('build/soundtrack.wav',SR,(stereo*32767).astype(np.int16))
print('soundtrack.wav written', round(DUR,1),'s')
