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
# Script « Le salaire qui disparaît avant la fin du mois ».
SEGMENTS = [
    # --- SCÈNE 1 — LE PROBLÈME (hook) ---
    ("Le moment le plus frustrant pour beaucoup de salariés, ce n'est pas forcément de recevoir un petit salaire.",
     1, "", 0.4),
    ("C'est de voir ce salaire disparaître quelques jours seulement après l'avoir reçu.",
     1, "Le salaire arrive… mais combien de temps tient-il vraiment ?", 0.5),
    ("Parce qu'au fond, le problème n'est pas seulement combien vous gagnez. C'est ce qu'il reste, une fois que tout est payé.",
     1, "", 0.8),

    # --- SCÈNE 2 — LA BOUCLE QUI RECOMMENCE ---
    ("Chaque mois, le même scénario recommence.", 2, "", 0.35),
    ("Le salaire arrive.", 2, "", 0.3),
    ("Vous remboursez les dettes.", 2, "", 0.3),
    ("Vous payez les factures.", 2, "", 0.3),
    ("Vous gérez la nourriture, le transport, les imprévus.", 2, "", 0.35),
    ("Et avant même le milieu du mois, vous commencez déjà à compter.", 2, "", 0.4),
    ("Puis arrive cette question :", 2, "", 0.25),
    ("comment je vais tenir jusqu'à la fin du mois ?", 2, "", 0.45),
    ("Alors parfois, vous empruntez encore.", 2, "", 0.4),
    ("Et le mois suivant, la même boucle recommence.", 2, "", 0.7),

    # --- SCÈNE 3 — LA FAUSSE SOLUTION ---
    ("Pendant longtemps, beaucoup pensent que la seule solution est de travailler plus, ou d'attendre une augmentation.",
     3, "", 0.4),
    ("Mais la réalité, c'est que ces changements n'arrivent pas toujours aussi vite qu'on l'espère.",
     3, "", 0.45),
    ("Alors pendant ce temps, qu'est-ce qu'on fait ?", 3, "", 0.4),
    ("On continue simplement à subir le même cycle ?", 3, "", 0.7),

    # --- SCÈNE 4 — LE DÉCLIC : LES OPPORTUNITÉS DIGITALES ---
    ("Pourtant, aujourd'hui, il existe une autre possibilité.", 4, "", 0.4),
    ("Pas pour remplacer votre travail du jour au lendemain.", 4, "", 0.4),
    ("Mais pour commencer à construire, progressivement, une source de revenus complémentaire.",
     4, "", 0.5),
    ("Avec des outils que vous avez déjà :", 4, "", 0.3),
    ("votre téléphone,", 4, "", 0.25),
    ("votre connexion Internet,", 4, "", 0.25),
    ("et les nouveaux outils d'intelligence artificielle.", 4, "", 0.5),
    ("Le problème, ce n'est pas qu'il n'existe pas d'opportunités.", 4, "", 0.4),
    ("C'est simplement que vous ne savez peut-être pas encore lesquelles saisir.",
     4, "Les opportunités existent. Il faut savoir où regarder.", 0.7),

    # --- SCÈNE 5 — MONEY BOOST : LA SOLUTION CONCRÈTE ---
    ("Aujourd'hui, autour de vous, des personnes et des entreprises recherchent des services simples que vous pouvez leur proposer, et pour lesquels elles sont prêtes à payer.",
     5, "", 0.5),
    ("Il s'agit notamment de créer des flyers professionnels, des catalogues WhatsApp, des menus pour restaurants, des visuels Canva, et plusieurs autres services utiles.",
     5, "", 0.5),
    ("Aujourd'hui, avec les bons outils et l'intelligence artificielle, des tâches qui semblaient compliquées deviennent beaucoup plus accessibles.",
     5, "", 0.5),
    ("Vous pouvez créer, entre deux pauses, un C.V. professionnel, réaliser un flyer pour un commerce, ou préparer un catalogue en quelques minutes, directement depuis votre téléphone.",
     5, "", 0.45),
    ("Et les facturer entre deux mille et cinq mille francs, selon la demande.", 5, "", 0.5),
    ("Vous répondez à un besoin, vous réalisez le service, et vous êtes payé pour la valeur apportée.",
     5, "Apprendre → Créer → Proposer → Être payé", 0.5),
    ("L'objectif n'est pas de quitter votre travail du jour au lendemain.", 5, "", 0.4),
    ("L'objectif est de vous aider à construire progressivement une deuxième source de revenus, avec les outils que vous possédez déjà.",
     5, "", 0.7),

    # --- SCÈNE 6 — POURQUOI CE PACK + CTA ---
    ("Ces méthodes, je les ai utilisées moi-même, et j'ai décidé de les partager.", 6, "", 0.4),
    (f"C'est exactement pour cette raison que le {PMB} a été créé.", 6, "", 0.45),
    (f"J'ai regroupé dans le {PMB} un guide pratique : quinze services à proposer, les outils à utiliser, les scripts pour utiliser les intelligences artificielles comme Chat G.P.T., les stratégies pour trouver vos premiers clients, et une méthode claire pour commencer.",
     6, "", 0.5),
    ("Vous gardez votre travail, mais vous transformez votre téléphone en un outil capable de créer de nouvelles opportunités.",
     6, "", 0.5),
    (f"Découvrez le {PMB}, et commencez votre parcours digital.",
     6, "Votre salaire paie vos charges.\nVos compétences créent de nouvelles opportunités.", 0.4),
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
