#!/usr/bin/env python3
"""Build the STORYTELLING spot (Script 2 - Enock) audio + per-scene timeline.

First-person male narration in the cloned voice, sincere/natural delivery, with
a light "credible creator" master (subtle warmth + presence, barely any pitch
shift — authentic, not over-produced). Writes:
    build/spot.mp3  +  timeline.js (window.SEG = [{t,scene,cap,fx}], window.DURATION)
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

VOICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "okf-voice"))
sys.path.insert(0, VOICE_DIR)

import ta_shim  # noqa: F401
from clone import NATURAL, SR, load_tts, say     # noqa: E402
from narrate import ffmpeg_bin                    # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
REF = os.path.join(VOICE_DIR, "assets", "my_voice_ref.wav")
MUSIC = os.path.join(VOICE_DIR, "assets", "music_bg.m4a")
NAT_GAP = 0.42
MUSIC_VOL = 0.30
TAIL = 3.0

# Sincere storytelling delivery: calm, natural, believable (not rushed/hyped).
TELL = dict(NATURAL, temperature=0.72, speed=1.0)

# Credible-creator master: gentle body + presence, tame box, firm-but-natural
# glue, and a barely-there pitch drop for a touch of grounded maturity.
PITCH = "asetrate=24000*0.985,atempo=1.015228,aresample=44100"
CLEAN = "adeclick=window=55:overlap=75,adeclip,afftdn=nf=-26:nr=11"
MASTER = (
    "highpass=f=60,"
    "equalizer=f=115:t=q:w=1.0:g=3,"
    "equalizer=f=200:t=q:w=1.2:g=1.5,"
    "equalizer=f=480:t=q:w=1.5:g=-2,"
    "equalizer=f=3000:t=q:w=1.1:g=2.5,"
    "equalizer=f=9000:t=q:w=1.0:g=1.3,"
    "acompressor=threshold=-19dB:ratio=3:attack=15:release=200:makeup=3,"
    "alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11"
)

PMB = "Pack Mauni Bouste deux mille vingt-six"

# (text, scene, on-screen caption or "" if the image already carries text, pause)
SEGMENTS = [
    ("Pendant longtemps, je pensais que pour gagner de l'argent sur Internet, il fallait forcément avoir beaucoup d'argent.",
     1, "Je cherchais une solution…", 0.4),
    ("Jusqu'au jour où j'ai compris que je cherchais au mauvais endroit.",
     1, "…mais pas au bon endroit.", 1.0),

    ("Comme beaucoup de gens, je voyais toutes ces histoires de personnes qui réussissaient grâce à Internet.",
     2, "", 0.35),
    ("Alors moi aussi, j'ai voulu comprendre.", 2, "", 0.35),
    ("J'ai essayé plusieurs choses : le trading, le dropshipping, différentes méthodes.",
     2, "", 0.4),
    ("Mais à chaque fois, je retombais sur les mêmes obstacles : investir beaucoup d'argent, prendre des risques, apprendre des systèmes compliqués.",
     2, "", 0.9),

    ("Puis j'ai réalisé quelque chose d'important.", 3, "", 0.4),
    ("Internet n'était pas seulement un endroit où regarder des vidéos.", 3, "", 0.4),
    ("C'était devenu un immense marché, où des gens cherchent chaque jour des solutions.",
     3, "Un besoin → Une solution → Une valeur", 0.5),
    ("Le principe était simple : trouver un besoin, apporter une solution, et être payé pour la valeur créée.",
     3, "", 0.9),

    ("Comme un réparateur de téléphone, dans un quartier.", 4, "", 0.4),
    ("Il a une compétence. Quelqu'un a un problème.", 4, "", 0.4),
    ("Il apporte une solution, et il est payé.", 4, "", 0.4),
    ("Sur Internet, ton quartier devient beaucoup plus grand.",
     4, "Internet = un marché mondial", 0.9),

    ("J'ai commencé simplement.", 5, "", 0.4),
    ("Quelques jours après, mon premier client m'a contacté.", 5, "WA", 0.4),
    ("Un flyer : cinq mille francs.", 5, "PAY", 0.4),
    ("Puis un C.V. Puis d'autres demandes.", 5, "", 0.4),
    ("Petit à petit, j'ai compris que ce n'était pas une question de chance.", 5, "", 0.35),
    ("J'avais simplement appris à répondre à un besoin réel.", 5, "", 0.9),

    (f"C'est exactement pour ça que j'ai créé le {PMB}.", 6, "", 0.4),
    ("J'ai regroupé ce que j'aurais aimé avoir quand j'ai commencé :", 6, "", 0.35),
    ("les services à apprendre, les outils à utiliser, et les étapes pour démarrer.",
     6, "", 0.9),

    ("Pas de promesse magique.", 7, "", 0.4),
    ("Juste une méthode claire pour apprendre à créer de la valeur avec les outils que tu as déjà.",
     7, "", 0.5),
    (f"Découvre le {PMB}, et commence ton parcours.", 7, "", 0.4),
]


def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=nk=1:nw=1", path]).decode().strip()
    return float(out)


def main():
    os.makedirs(BUILD, exist_ok=True)
    tts = load_tts()
    out = np.zeros(0, dtype=np.float32)
    seg = []
    for i, (txt, scene, cap, pause) in enumerate(SEGMENTS):
        if i > 0:
            gap = SEGMENTS[i - 1][3]; gap = NAT_GAP if gap is None else gap
            out = np.concatenate([out, np.zeros(int(gap * SR), dtype=np.float32)])
        start = round(len(out) / SR, 3)
        clip = say(tts, txt, REF, TELL)
        clip = clip / (np.max(np.abs(clip)) + 1e-9) * 0.97
        out = np.concatenate([out, clip])
        seg.append({"t": start, "scene": scene, "cap": cap})
        print(f"  [{i:02d}] s{scene} start={start:6.2f}s dur={len(clip)/SR:4.2f}s  {txt[:44]}")

    out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
    narr = os.path.join(BUILD, "narration.wav")
    sf.write(narr, out, SR)
    print(f"narration: {len(out)/SR:.2f}s")

    fb = ffmpeg_bin()
    master = os.path.join(BUILD, "narration_master.mp3")
    subprocess.run([fb, "-y", "-loglevel", "error", "-i", narr, "-af",
                    PITCH + "," + CLEAN + "," + MASTER, "-ar", "44100", "-b:a", "192k",
                    master], check=True)
    narr_dur = dur(master)

    total = narr_dur + TAIL
    fade_out = max(0.0, total - 3.0)
    padded = os.path.join(BUILD, "_voice_padded.wav")
    subprocess.run([fb, "-y", "-loglevel", "error", "-i", master,
                    "-af", f"apad=pad_dur={TAIL}", "-ar", "44100", padded], check=True)
    spot = os.path.join(BUILD, "spot.mp3")
    flt = (
        f"[0:a]aresample=44100,atrim=0:{total:.2f},volume={MUSIC_VOL},"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out:.2f}:d=3.0[mus];"
        f"[mus][1:a]sidechaincompress=threshold=0.035:ratio=7:attack=5:release=320:makeup=1[duck];"
        f"[1:a][duck]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix];"
        f"[mix]loudnorm=I=-14:TP=-1.0:LRA=11[out]"
    )
    subprocess.run([fb, "-y", "-loglevel", "error", "-stream_loop", "1",
                    "-i", MUSIC, "-i", padded, "-filter_complex", flt,
                    "-map", "[out]", "-ar", "44100", "-b:a", "192k", spot], check=True)
    os.remove(padded)

    with open(os.path.join(ROOT, "timeline.js"), "w", encoding="utf-8") as f:
        f.write("window.SEG = " + json.dumps(seg, ensure_ascii=False) + ";\n")
        f.write(f"window.DURATION = {dur(spot):.3f};\n")
    print(f"spot: {dur(spot):.2f}s ; timeline.js written ({len(seg)} segments)")


if __name__ == "__main__":
    main()
