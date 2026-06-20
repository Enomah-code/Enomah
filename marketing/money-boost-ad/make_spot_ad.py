#!/usr/bin/env python3
"""Build the AD spot (Script 1 - douleur etudiant) audio + per-scene timeline.

Synthesises the 30s ad narration in the cloned male voice, records the start
time of every spoken segment (tagged with its storyboard scene), masters the
voice, lays ducked background music under it, and writes:
    build/narration.wav, build/narration_master.mp3, build/spot.mp3
    timeline.js  ->  window.SEG = [{t, scene, cap}], window.DURATION
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
from clone import NATURAL, SR, load_tts, say  # noqa: E402
from narrate import FX_FILTER, ffmpeg_bin     # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
REF = os.path.join(VOICE_DIR, "assets", "my_voice_ref.wav")
MUSIC = os.path.join(VOICE_DIR, "assets", "music_bg.m4a")
NAT_GAP = 0.40
MUSIC_VOL = 0.34
TAIL = 2.6

PMB = "Pack Mauni Bouste"   # brand pronunciation chosen by ear

# (spoken text, scene index 1..6, caption, pause after in s or None=natural gap)
SEGMENTS = [
    ("C'est déjà les vacances.", 1, "C'est déjà les vacances.", 0.35),
    ("Tu es étudiant, et tu te demandes déjà comment gagner de l'argent ?",
     1, "Comment gagner de l'argent ?", 0.45),
    ("Ou tu penses refaire les mêmes petits jobs fatigants, qui ne te rapportent pas grand-chose ?",
     1, "Les mêmes petits jobs fatigants…", 0.8),

    ("Tu vois les autres, autour de toi, gagner de l'argent avec leur téléphone.",
     2, "Les autres gagnent avec leur téléphone.", 0.4),
    ("Et tu te dis que c'est pour eux, pas pour toi.",
     2, "« C'est pour eux, pas pour moi. »", 0.5),
    ("Tu n'as pas de capital.", 2, "Pas de capital.", 0.3),
    ("Tu n'as pas de compétences techniques particulières.",
     2, "Pas de compétences techniques.", 0.7),

    ("Et tu ne sais même pas quel service tu pourrais proposer aux gens.",
     3, "Quel service proposer ?", 1.0),

    ("Écoute.", 4, "Écoute…", 0.35),
    (f"Le {PMB} t'apprend quinze choses concrètes que les gens autour de toi cherchent, et sont prêts à payer.",
     4, "15 compétences que les gens paient.", 0.5),
    ("Et il te guide, pas à pas, pour faire tes premiers revenus.",
     4, "Guidé pas à pas vers tes 1ers revenus.", 0.6),
    ("Créer des flyers pour les vendeurs sur WhatsApp, des catalogues pour les boutiques en ligne, des menus pour les restaurants.",
     4, "Flyers • Catalogues • Menus", 0.8),

    ("Tu apprends à les réaliser avec Chatt GPT et Canva.",
     5, "Réalisés avec ChatGPT & Canva.", 0.45),
    ("Et tu les proposes à ceux qui en ont besoin, juste à côté de toi.",
     5, "Tu les proposes autour de toi.", 0.9),

    ("Clique sur le lien, télécharge ton guide, et propose ton premier service cette semaine.",
     6, "Clique. Télécharge. Lance-toi.", 0.4),
]


def duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1", path]).decode().strip()
    return float(out)


def main():
    os.makedirs(BUILD, exist_ok=True)
    tts = load_tts()

    out = np.zeros(0, dtype=np.float32)
    seg = []
    for i, (txt, scene, cap, pause) in enumerate(SEGMENTS):
        if i > 0:
            gap = SEGMENTS[i - 1][3]
            gap = NAT_GAP if gap is None else gap
            out = np.concatenate([out, np.zeros(int(gap * SR), dtype=np.float32)])
        start = round(len(out) / SR, 3)
        clip = say(tts, txt, REF, NATURAL)
        clip = clip / (np.max(np.abs(clip)) + 1e-9) * 0.97
        out = np.concatenate([out, clip])
        seg.append({"t": start, "scene": scene, "cap": cap})
        print(f"  [{i:02d}] s{scene} start={start:6.2f}s dur={len(clip)/SR:4.2f}s  {txt[:46]}")

    out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
    narr = os.path.join(BUILD, "narration.wav")
    sf.write(narr, out, SR)
    narr_dur = len(out) / SR
    print(f"narration: {narr_dur:.2f}s -> {narr}")

    fb = ffmpeg_bin()
    master = os.path.join(BUILD, "narration_master.mp3")
    subprocess.run([fb, "-y", "-loglevel", "error", "-i", narr, "-af", FX_FILTER,
                    "-ar", "44100", "-b:a", "192k", master], check=True)

    total = narr_dur + TAIL
    fade_out = max(0.0, total - 2.6)
    padded = os.path.join(BUILD, "_voice_padded.wav")
    subprocess.run([fb, "-y", "-loglevel", "error", "-i", master,
                    "-af", f"apad=pad_dur={TAIL}", "-ar", "44100", padded], check=True)
    spot = os.path.join(BUILD, "spot.mp3")
    flt = (
        f"[0:a]aresample=44100,atrim=0:{total:.2f},volume={MUSIC_VOL},"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out:.2f}:d=2.6[mus];"
        f"[mus][1:a]sidechaincompress=threshold=0.035:ratio=7:attack=5:release=320:makeup=1[duck];"
        f"[1:a][duck]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix];"
        f"[mix]loudnorm=I=-14:TP=-1.0:LRA=11[out]"
    )
    subprocess.run([fb, "-y", "-loglevel", "error", "-stream_loop", "1",
                    "-i", MUSIC, "-i", padded, "-filter_complex", flt,
                    "-map", "[out]", "-ar", "44100", "-b:a", "192k", spot], check=True)
    os.remove(padded)
    spot_dur = duration(spot)

    with open(os.path.join(ROOT, "timeline.js"), "w", encoding="utf-8") as f:
        f.write("window.SEG = " + json.dumps(seg, ensure_ascii=False) + ";\n")
        f.write(f"window.DURATION = {spot_dur:.3f};\n")
    print(f"spot: {spot_dur:.2f}s -> {spot}")
    print(f"timeline.js written ({len(seg)} segments)")


if __name__ == "__main__":
    main()
