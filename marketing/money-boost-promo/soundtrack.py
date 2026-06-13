#!/usr/bin/env python3
"""
Build the full soundtrack for the Money Boost promo:
  - French neural voice-over per scene (Piper, offline)
  - quiet, professional music bed with accents synced to scene cuts
  - sidechain ducking of music under the voice
Also writes timeline.js consumed by promo.html / render.js so the visuals
match the voice-over timing exactly.
"""
import os, wave, subprocess, json
import numpy as np
from scipy.signal import resample_poly
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 44100
MODEL = os.path.join(ROOT, 'build', 'tts', 'fr_FR-siwis-medium.onnx')
VO_DIR = os.path.join(ROOT, 'build', 'vo')
os.makedirs(VO_DIR, exist_ok=True)
rng = np.random.default_rng(7)

# ---------------- scenes : (min_dur, vo_text) ----------------
SCENES = [
    (3.2, "Et si ton téléphone…"),
    (3.6, "pouvait te rapporter bien plus que ton salaire ?"),
    (5.4, "En Afrique, des milliers de personnes gagnent de cinquante mille à cinq cent mille francs par mois, avec un simple téléphone."),
    (5.2, "Sans capital. Sans diplôme. Sans expérience. Juste la bonne méthode."),
    (5.2, "Voici le Pack Money Boost, l'accélérateur de revenus."),
    (8.8, "Quinze services digitaux prêts à vendre. Cinquante scripts WhatsApp. Cent idées de produits. Et le plan complet, de zéro à un million de francs."),
    (6.6, "Et ça marche déjà. Voici les premiers revenus de ceux qui sont passés à l'action."),
    (10.5, "Aujourd'hui, c'est moins cinquante pour cent. Quatre mille quatre cent cinquante francs au lieu de neuf mille cinq cents. Offre limitée. Télécharge ton pack maintenant, le lien est juste en dessous."),
]
LEAD = 0.40   # voice starts this long after the scene begins
TAIL = 0.65   # silence kept after the voice before the next scene

# ---------------- 1. synthesise voice-over ----------------
from piper import PiperVoice, SynthesisConfig
voice = PiperVoice.load(MODEL)
cfg = SynthesisConfig(length_scale=1.02, noise_scale=0.667, noise_w_scale=0.8, volume=1.0, normalize_audio=True)

def synth(text, path):
    with wave.open(path, 'wb') as wf:
        voice.synthesize_wav(text, wf, syn_config=cfg)

def load_wav_mono(path):
    sr, data = wavfile.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    else:
        data = data.astype(np.float32)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SR:
        from math import gcd
        g = gcd(sr, SR)
        data = resample_poly(data, SR // g, sr // g)
    return data

vo_clips = []
for i, (_, text) in enumerate(SCENES):
    p = os.path.join(VO_DIR, f'scene_{i}.wav')
    synth(text, p)
    clip = load_wav_mono(p)
    # trim leading/trailing near-silence
    thr = 0.012 * np.max(np.abs(clip) + 1e-9)
    idx = np.where(np.abs(clip) > thr)[0]
    if len(idx):
        clip = clip[max(0, idx[0]-int(0.05*SR)): idx[-1]+int(0.12*SR)]
    # normalise clip peak
    clip = clip / (np.max(np.abs(clip)) + 1e-9) * 0.97
    vo_clips.append(clip)
    print(f'  VO scene {i}: {len(clip)/SR:.2f}s')

# ---------------- 2. compute timeline ----------------
cuts = [0.0]
for i, (mind, _) in enumerate(SCENES):
    vo_d = len(vo_clips[i]) / SR
    dur = max(mind, LEAD + vo_d + TAIL)
    cuts.append(round(cuts[-1] + dur, 3))
DURATION = cuts[-1]
N = int(np.ceil(DURATION * SR))
print('TIMELINE cuts:', cuts, 'DURATION', DURATION)

# write timeline.js for the HTML/renderer
with open(os.path.join(ROOT, 'timeline.js'), 'w') as f:
    f.write("window.TIMELINE = %s;\nwindow.DURATION = %s;\n" % (json.dumps(cuts), DURATION))

t = np.arange(N) / SR

# ---------------- 3. assemble voice bus ----------------
voice_bus = np.zeros(N)
for i, clip in enumerate(vo_clips):
    start = int((cuts[i] + LEAD) * SR)
    end = min(start + len(clip), N)
    voice_bus[start:end] += clip[:end-start]
# gentle compression + light reverb
voice_bus = np.tanh(voice_bus * 1.25) * 0.9
def delay_mix(x, ms, g):
    d = int(ms*0.001*SR); o = np.zeros_like(x)
    if d < len(x): o[d:] = x[:-d]*g
    return o
verb = delay_mix(voice_bus,38,0.14)+delay_mix(voice_bus,67,0.10)+delay_mix(voice_bus,110,0.06)
voice_bus = voice_bus + verb*0.6

# voice presence envelope (for ducking) : smoothed magnitude
pres = np.abs(voice_bus)
win = int(0.03*SR)
kernel = np.ones(win)/win
pres = np.convolve(pres, kernel, mode='same')
pres = pres / (np.percentile(pres, 99) + 1e-9)
pres = np.clip(pres, 0, 1)
# attack/release smoothing
duck = np.zeros(N); a_at=np.exp(-1/(0.010*SR)); a_re=np.exp(-1/(0.32*SR)); prev=0.0
for n in range(N):
    target = pres[n]
    coef = a_at if target > prev else a_re
    prev = target + (prev-target)*coef
    duck[n] = prev
duck_gain = 1.0 - 0.80*duck   # music dips to 20% under speech

# ---------------- 4. music bed (quiet, synced to cuts) ----------------
music = np.zeros(N)
def nf(s): return 440.0*2**(s/12)
# warm pad chord progression per "act": brooding -> hopeful at reveal (cut index 4)
def adsr(start,dur,a,d,s,r,peak):
    e=np.zeros(N); s0=int(start*SR); L=int(dur*SR)
    if s0>=N: return e
    L=min(L,N-s0); seg=np.zeros(L)
    ai=min(int(a*SR),L); di=min(int(d*SR),max(L-ai,0)); ri=min(int(r*SR),max(L-ai-di,0))
    seg[:ai]=np.linspace(0,peak,ai,endpoint=False)
    seg[ai:ai+di]=np.linspace(peak,s*peak,di,endpoint=False)
    se=max(L-ri,ai+di); seg[ai+di:se]=s*peak
    if ri>0: seg[se:se+ri]=np.linspace(s*peak,0,ri)[:L-se]
    e[s0:s0+L]=seg; return e
def osc(freq,start,dur,env,kind='tri',det=0.004):
    s0=int(start*SR); L=int(dur*SR)
    if s0>=N or L<=0: return np.zeros(N)
    L=min(L,N-s0); tt=np.arange(L)/SR; ph=2*np.pi*freq*tt
    if kind=='sine': w=np.sin(ph)
    elif kind=='tri': w=2/np.pi*np.arcsin(np.sin(ph))
    else: w=(np.sin(ph)+0.4*np.sin(2*ph)+0.2*np.sin(3*ph))/1.6
    if det: w=0.5*w+0.5*np.sin(2*np.pi*freq*(1+det)*tt)
    o=np.zeros(N); o[s0:s0+L]=w*env[s0:s0+L]; return o

REVEAL_T = cuts[4]
CTA_T = cuts[7]
# Act 1 pad : A minor (A2,A3,C4,E4)
p1=adsr(0,REVEAL_T+0.5,1.4,1.8,0.85,1.0,0.10); trem=1+0.10*np.sin(2*np.pi*0.16*t)
for fr in [nf(-24),nf(-12),nf(3),nf(7)]: music+=osc(fr,0,REVEAL_T+0.5,p1,'tri')*trem*0.5
# Act 2 pad : C add9 (C,E,G,D) warmer
p2=adsr(REVEAL_T-0.2,DURATION-REVEAL_T+0.4,0.8,1.4,0.9,1.8,0.115); trem2=1+0.08*np.sin(2*np.pi*0.2*t)
for fr in [nf(-24),nf(3),nf(7),nf(10),nf(14)]: music+=osc(fr,REVEAL_T-0.2,DURATION-REVEAL_T+0.4,p2,'tri')*trem2*0.46
# shimmer in act2
sh=adsr(REVEAL_T,DURATION-REVEAL_T,1.2,1.0,0.7,2.0,0.03)
music+=osc(nf(19),REVEAL_T,DURATION-REVEAL_T,sh,'sine')*0.7
music+=osc(nf(24),REVEAL_T,DURATION-REVEAL_T,sh,'sine')*0.45

# gentle pluck arpeggio (act2, builds energy) — quiet
def pluck(freq,start,gain=0.06,dur=0.55):
    e=adsr(start,dur,0.003,0.18,0.0,0.12,gain); return osc(freq,start,dur,e,'soft',det=0)
arp_notes=[nf(3),nf(7),nf(10),nf(14),nf(7),nf(10)]
beat=0.5; ti=REVEAL_T; k=0
while ti<DURATION-0.5:
    pluck(arp_notes[k%len(arp_notes)],ti,gain=0.05 if ti<CTA_T else 0.07)
    music+=pluck(arp_notes[k%len(arp_notes)],ti,gain=0.05 if ti<CTA_T else 0.065)
    ti+=beat; k+=1

# ---- accents exactly on each scene cut (the "synced to sunlights") ----
def whoosh(center,gain,length=0.7):
    s0=int((center-length*0.55)*SR); L=int(length*SR)
    if s0<0: L+=s0; s0=0
    if L<=0 or s0>=N: return
    L=min(L,N-s0); tt=np.arange(L)/SR
    n=rng.standard_normal(L); n=np.diff(n,prepend=n[0])
    env=np.sin(np.pi*np.clip(tt/length,0,1))**1.6
    music[s0:s0+L]+=n*env*gain
def impact(start,gain):
    s0=int(start*SR); L=int(1.8*SR)
    if s0>=N: return
    L=min(L,N-s0); tt=np.arange(L)/SR
    f=68*np.exp(-tt*4)+38
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.4)
    n=rng.standard_normal(L)*np.exp(-tt*18)
    music[s0:s0+L]+=(boom*0.9+n*0.18)*gain
def subnote(freq,start,dur,gain):
    e=adsr(start,dur,0.01,0.12,0.7,0.2,gain); return osc(freq,start,dur,e,'sine',det=0)

for ci,ct in enumerate(cuts[1:-1], start=1):   # interior cuts
    whoosh(ct, gain=0.10)
    # soft sub thump marking the change
    music+=subnote(nf(-24),ct,0.5,0.10)
# strong (but controlled) impacts at reveal & cta
impact(REVEAL_T,0.55); impact(CTA_T,0.5)
# risers leading into reveal and cta
def riser(end,length,gain):
    s0=int((end-length)*SR); L=int(length*SR)
    if s0<0: L+=s0; s0=0
    if L<=0: return
    tt=np.arange(L)/SR; n=rng.standard_normal(L); n=np.cumsum(n); n-=n.mean(); n/=np.max(np.abs(n))+1e-9
    sw=np.sin(2*np.pi*(200+(tt/length)**2*2600)*tt)*0.5
    env=(tt/length)**2.3
    music[s0:s0+L]+=(n*0.5+sw)*env*gain
riser(REVEAL_T,2.6,0.10); riser(CTA_T,2.0,0.09)

# light four-on-floor sub kick from reveal to cta (very soft)
def kick(start,gain):
    s0=int(start*SR); L=int(0.3*SR)
    if s0>=N: return
    L=min(L,N-s0); tt=np.arange(L)/SR
    f=110*np.exp(-tt*24)+46; env=np.exp(-tt*10)
    music[s0:s0+L]+=np.sin(2*np.pi*np.cumsum(f)/SR)*env*gain
bt=REVEAL_T
while bt<DURATION-0.4:
    kick(bt, gain=0.22 if bt<CTA_T else 0.28)
    bt+=beat

# bell sparkles on counter scene (cut index 2) & testimonial stars (cut 6)
def bell(freq,start,gain,dur=1.1):
    e=adsr(start,dur,0.004,0.4,0.0,0.3,gain)
    return osc(freq,start,dur,e,'sine',det=0)+0.4*osc(freq*2.01,start,dur,e*0.5,'sine',det=0)
for k,off in enumerate([0.5,1.1,1.7,2.3]):
    music+=bell(nf(12+k*3),cuts[2]+off,0.06,0.9)
music+=bell(nf(24),cuts[6]+1.0,0.08,1.3)

# ---------------- 5. master mix ----------------
music = music * duck_gain * 0.5          # duck + overall music level LOW
# soft high-pass on music to leave room for voice (remove low rumble buildup)
mix = voice_bus*1.0 + music
mix = np.tanh(mix*1.05)
mix = mix/(np.max(np.abs(mix))+1e-9)*0.89
fin=int(0.3*SR); fout=int(1.4*SR)
mix[:fin]*=np.linspace(0,1,fin); mix[-fout:]*=np.linspace(1,0,fout)
stereo=np.stack([mix,mix],axis=1)
wavfile.write(os.path.join(ROOT,'build','soundtrack.wav'),SR,(stereo*32767).astype(np.int16))
print('soundtrack.wav written %.2fs' % DURATION)
