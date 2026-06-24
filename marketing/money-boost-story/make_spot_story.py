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
NAT_GAP = 0.30
MUSIC_VOL = 0.30
TAIL = 2.5
SPEED = 1.10          # tighten delivery (atempo, pitch preserved) — script is long

# Sincere storytelling delivery: calm, natural, believable (not rushed/hyped).
TELL = dict(NATURAL, temperature=0.72, speed=1.0)

# Credible-creator master: gentle body + presence, tame box, firm-but-natural
# glue, a barely-there pitch drop, plus the SPEED tighten (atempo keeps pitch).
PITCH = f"asetrate=24000*0.985,atempo=1.015228,atempo={SPEED},aresample=44100"
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
# Script « J'ai arrêté de chercher l'argent facile ». On-screen text is kept
# minimal (storyboard beats only) — several images already carry baked text.
SEGMENTS = [
    # --- SCÈNE 1 — HOOK (s1) ---
    ("Pendant longtemps, je pensais que pour gagner de l'argent sur Internet, il fallait forcément avoir de l'argent au départ.",
     1, "Je cherchais une solution…", 0.4),
    ("Jusqu'au jour où j'ai compris que je cherchais simplement au mauvais endroit.",
     1, "…mais pas au bon endroit.", 0.8),

    # --- SCÈNE 2 — LA RECHERCHE (s2 : montage méthodes / problèmes) ---
    ("Comme beaucoup de personnes, je voyais toutes ces histoires de gens qui réussissaient grâce à Internet.",
     2, "", 0.3),
    ("Des personnes qui créaient des activités, trouvaient des clients en ligne, et travaillaient simplement avec un ordinateur, ou même un téléphone.",
     2, "", 0.35),
    ("Alors moi aussi, j'ai voulu comprendre comment ça fonctionnait.", 2, "", 0.35),
    ("J'ai essayé plusieurs choses : le trading, le dropshipping, différentes méthodes qu'on voyait partout.",
     2, "", 0.35),
    ("Mais à chaque fois, je retrouvais les mêmes problèmes : il fallait souvent beaucoup d'argent pour commencer, prendre des risques, comprendre des systèmes compliqués.",
     2, "", 0.35),
    ("Et parfois, la réalité était très différente de ce qu'on m'avait présenté.", 2, "", 0.7),

    # --- SCÈNE 3 — LE DÉCLIC (s3a/s3b : marché, valeur, bons outils) ---
    ("Puis j'ai compris quelque chose d'important.", 3, "", 0.35),
    ("Le problème, ce n'était pas Internet.", 3, "", 0.3),
    ("Le problème, c'était que je ne savais pas encore comment l'utiliser correctement.", 3, "", 0.45),
    ("Internet n'était pas seulement un endroit pour regarder des vidéos ou passer le temps.", 3, "", 0.35),
    ("C'était devenu un immense marché, où chaque jour, des milliers de personnes recherchent des solutions.",
     3, "", 0.4),
    ("Les personnes qui réussissent en ligne font simplement une chose : elles apportent de la valeur à quelqu'un qui a un besoin.",
     3, "", 0.7),

    # --- SCÈNE 3 (suite) — métaphore du réparateur (s4a/s4b) ---
    ("Comme un réparateur de téléphone dans un quartier :", 4, "", 0.3),
    ("il possède une compétence, quelqu'un a un problème, il apporte une solution, et il est payé.",
     4, "", 0.5),
    ("Sur Internet, ton quartier devient le monde entier.",
     4, "Ton quartier devient le monde entier.", 0.4),
    ("Et aujourd'hui, avec l'intelligence artificielle, il est devenu beaucoup plus simple d'apprendre plus vite, et de créer des services utiles.",
     4, "", 0.7),

    # --- SCÈNE 4 — LA NOUVELLE APPROCHE (s5 : client, design, paiement) ---
    ("Alors j'ai arrêté de chercher des méthodes qui demandaient toujours plus d'argent.", 5, "", 0.35),
    ("Je me suis concentré sur quelque chose de plus solide : apprendre des compétences, et résoudre de vrais problèmes.",
     5, "", 0.45),
    ("Créer un C.V. professionnel. Concevoir des flyers. Réaliser des catalogues pour des entreprises.",
     5, "", 0.4),
    ("Aider des entrepreneurs à mieux présenter leurs activités sur Internet.", 5, "", 0.45),
    ("Des choses qu'on peut apprendre et réaliser avec un téléphone, Internet, et les bons outils.",
     5, "", 0.5),
    ("Et progressivement, les choses ont commencé à changer.", 5, "", 0.35),
    ("Après avoir appris et appliqué ces méthodes, j'ai commencé à recevoir mes premières demandes.",
     5, "WA", 0.45),
    ("Un flyer. Puis un C.V. Puis d'autres projets. Et ça s'est enchaîné.", 5, "PAY", 0.45),
    ("J'ai compris que ce n'était pas une question de chance.", 5, "", 0.3),
    ("Il fallait simplement apprendre à répondre à un besoin réel.", 5, "", 0.7),

    # --- SCÈNE 5 — POURQUOI MONEY BOOST (s6 : révélation du pack) ---
    ("Aujourd'hui, j'ai décidé de partager ces méthodes avec vous.", 6, "", 0.35),
    (f"C'est exactement pour cette raison que j'ai créé le {PMB}.", 6, "", 0.4),
    ("Parce qu'au début, j'aurais aimé avoir quelqu'un qui m'explique simplement : quoi apprendre, quels services proposer, quels outils utiliser, et comment trouver ses premiers clients.",
     6, "", 0.45),
    ("J'ai donc regroupé tout ce parcours dans un guide pratique.", 6, "", 0.4),
    ("Des idées de services digitaux, des outils d'intelligence artificielle, des scripts, des stratégies, et un plan clair pour commencer.",
     6, "", 0.7),

    # --- SCÈNE 5 (CTA) — (s7 : costume + bouton télécharger) ---
    ("Pas de promesse magique. Pas de raccourci.", 7, "", 0.35),
    ("Juste une méthode pour apprendre à créer de la valeur, avec les outils que tu as déjà.", 7, "", 0.5),
    (f"Télécharge le {PMB}, et commence à construire tes premières opportunités en ligne.", 7, "", 0.4),
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

    # the master is sped by SPEED (atempo), so every segment start compresses too
    for s in seg:
        s["t"] = round(s["t"] / SPEED, 3)
    with open(os.path.join(ROOT, "timeline.js"), "w", encoding="utf-8") as f:
        f.write("window.SEG = " + json.dumps(seg, ensure_ascii=False) + ";\n")
        f.write(f"window.DURATION = {dur(spot):.3f};\n")
    print(f"spot: {dur(spot):.2f}s ; timeline.js written ({len(seg)} segments)")


if __name__ == "__main__":
    main()
