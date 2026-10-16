"""Montage de la voix off (version courte ~1 min 45) à partir des deux enregistrements nettoyés (voice.py).
Chaque segment = suite de morceaux (fichier, début, fin) ; les silences internes > 0,55 s sont ramenés à 0,35 s,
0,45 s de respiration entre segments. Sorties : assets/audio/voice.wav, scripts/timeline.json
(début/durée de chaque segment + mots recalés sur la sortie pour les sous-titres).
"""
import json
import os
import subprocess

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
GAP = 0.45
TEMPO = 1.06          # débit légèrement accéléré (inaudible), voix posée et lente à l'origine

EDL = [  # id, [(fichier, début, fin)], rôle
    ("A", [("wa86", 0.95, 12.75)], "hook : statue d'un ancien esclave ?"),
    ("B", [("wa86", 13.40, 18.45)], "laissez-moi vous raconter"),
    ("C", [("wa86", 58.85, 65.80), ("wa86", 68.00, 72.30)], "né à Agouagon, village mahi des Collines"),
    ("D", [("wa87", 1.15, 13.65)], "vendu comme esclave au Brésil"),
    ("E", [("wa87", 13.85, 26.40)], "abolition 1888, adopté par Branco"),
    ("G", [("wa87", 67.00, 86.70), ("wa87", 87.75, 89.30)], "mai 1927 : l'école"),
    ("I", [("wa87", 281.85, 290.55)], "des centaines d'élèves"),
    ("J", [("wa87", 317.40, 329.40), ("wa87", 334.05, 339.86)], "la statue, 20 avril 2025"),
    ("K", [("wa87", 350.90, 359.50)], "signature"),
]


def squeeze(x, t0):
    """Raccourcit les silences internes ; renvoie l'audio et la table (t_source, t_sortie) pour recaler les mots."""
    hop = int(0.01 * SR)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
    thr = max(1e-4, np.percentile(e, 90) * 10 ** (-38 / 20))
    quiet = e < thr
    out, mp, i, pos = [], [(t0, 0.0)], 0, 0
    while i < len(quiet):
        j = i
        while j < len(quiet) and quiet[j] == quiet[i]:
            j += 1
        a, b = i * hop, min(len(x), j * hop)
        seg = x[a:b]
        if quiet[i] and (b - a) / SR > 0.55 and i > 0 and j < len(quiet):
            k = int(0.175 * SR)
            seg = np.concatenate([seg[:k], seg[-k:]])
        mp.append((t0 + a / SR, pos / SR))
        out.append(seg)
        pos += len(seg)
        i = j
    mp.append((t0 + len(x) / SR, pos / SR))
    return np.concatenate(out), mp


def remap(t, mp):
    for (s0, o0), (s1, o1) in zip(mp, mp[1:]):
        if s0 <= t <= s1:
            return o0 + min(t - s0, o1 - o0)
    return None


def main():
    src = {k: sf.read(os.path.join(ROOT, f"assets/audio/{k}-clean.wav"))[0] for k in ("wa86", "wa87")}
    words = {k: [w for s in json.load(open(os.path.join(ROOT, f"assets/audio/{k}.words.json"))) for w in s["w"]] for k in src}
    fade = int(0.03 * SR)
    ramp = np.linspace(0, 1, fade)
    out, segs, tw, t = [], [], [], 0.0
    for sid, parts, role in EDL:
        s_start = t
        for f, a, b in parts:
            x = src[f][int(a * SR):int(b * SR)].copy()
            x[:fade] *= ramp
            x[-fade:] *= ramp[::-1]
            y, mp = squeeze(x, a)
            for w in words[f]:
                if a <= w[0] and w[1] <= b + 0.05:
                    o0, o1 = remap(w[0], mp), remap(min(w[1], b), mp)
                    if o0 is not None and o1 is not None:
                        tw.append([round(t + o0, 3), round(t + o1, 3), w[2].strip(), sid])
            out.append(y)
            t += len(y) / SR
        segs.append({"id": sid, "start": round(s_start, 3), "dur": round(t - s_start, 3), "role": role})
        out.append(np.zeros(int(GAP * SR)))
        t += GAP
    v = np.concatenate(out)
    raw = os.path.join(ROOT, "assets/audio/voice-raw.wav")
    sf.write(raw, v, SR)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", f"atempo={TEMPO}", "-ar", str(SR),
                    os.path.join(ROOT, "assets/audio/voice.wav")], check=True)
    os.remove(raw)
    t /= TEMPO
    for s in segs:
        s["start"], s["dur"] = round(s["start"] / TEMPO, 3), round(s["dur"] / TEMPO, 3)
    tw = [[round(a / TEMPO, 3), round(b / TEMPO, 3), w, sid] for a, b, w, sid in tw]
    json.dump({"duration": round(t, 3), "segments": segs, "words": tw}, open(os.path.join(ROOT, "scripts/timeline.json"), "w"),
              ensure_ascii=False, indent=1)
    for s in segs:
        print(f'{s["id"]} {s["start"]:7.2f} +{s["dur"]:5.2f}  {s["role"]}')
    print("durée voix", round(t, 2), "s")


if __name__ == "__main__":
    main()
