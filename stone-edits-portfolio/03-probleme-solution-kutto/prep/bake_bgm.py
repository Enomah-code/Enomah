"""Bake the music bed's dynamics into assets/bgm/track_mix.wav (run after prep_bgm.sh).

Clip-local time t = composition time - 0.85 s.
  t < 4.8   muffled (low-pass), "problem" mood; fades out on "Stop" (3.66 -> 3.74), silent to 4.78
  t >= 4.8  full band from the product reveal
  voice     ducked 8 dB under each voice line (80 ms attack, 250 ms release), full level in between
"""
import re, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
START = 0.85
y, sr = sf.read("assets/bgm/track.wav")
n = len(y); t = np.arange(n) / sr
# muffle: 2nd-order low-pass, crossfaded into the dry signal at the reveal
sos = butter(2, 900, "low", fs=sr, output="sos")
muf = sosfilt(sos, y, axis=0) * 1.6
dry_w = np.clip((t - 4.78) / 0.02, 0, 1)[:, None]
out = muf * (1 - dry_w) + y * dry_w
# stop cut
g = np.interp(t, [0, 3.66, 3.74, 4.78, 4.80], [0.85, 0.85, 0, 0, 1])
# duck under the voice-over, spans merged when lines are < 0.45 s apart
html = open("index.html").read()
vo = sorted((float(a), float(d)) for a, d in re.findall(r'<audio id="vo-\d+"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', html))
spans = []
for s0, d in vo:
    a, b = s0 - START, s0 + d - START
    if spans and a - spans[-1][1] < 0.45: spans[-1][1] = b
    else: spans.append([a, b])
DUCK = 10 ** (-8 / 20)
xs, vs = [0.0], [1.0]
for a, b in spans:
    xs += [a - 0.08, a, b, b + 0.25]; vs += [1, DUCK, DUCK, 1]
g *= np.interp(t, xs, vs)
out = out * g[:, None]
peak = np.abs(out).max()
if peak > 0.89: out *= 0.89 / peak
sf.write("assets/bgm/track_mix.wav", out.astype(np.float32), sr, subtype="PCM_24")
print("spans", [[round(a + START, 2), round(b + START, 2)] for a, b in spans], "peak", round(float(np.abs(out).max()), 3))
