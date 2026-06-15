#!/usr/bin/env python3
"""Build the video's audio spot AND the per-line timeline used to sync the visuals.

Synthesises the (corrected) Money Boost script in the cloned voice, records the
start time of every line, masters the voice, lays the background music under it
with ducking, and writes:
    build/narration.wav, build/narration_master.mp3, build/spot.mp3
    timeline.js   ->  window.TIMELINE = [line start times], window.DURATION
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
NAT_GAP = 0.45
MUSIC_VOL = 0.40
TAIL = 3.2

# Pronunciation of the brand, chosen by ear (see pmb_* tests).
PMB = "Pack Mauni Bouste"

# (spoken text, pause after this line in seconds or None for the natural gap)
SEGMENTS = [
    ("Deux mille vingt-sept, c'est dans quelques mois.", 1.0),
    ("Qu'est-ce que tu auras changé dans ta vie financière ?", 1.5),
    ("Tu te poses cette question chaque année.", None),
    ("Et chaque année… tu te retrouves exactement au même endroit.", None),
    ("À attendre une opportunité… qui ne vient pas d'elle-même.", 1.0),
    ("Tu as le téléphone.", None),
    ("Tu as la connexion.", None),
    ("Il te manque juste… la méthode.", 1.5),
    (f"Avec le {PMB} deux mille vingt-six, tu vas apprendre de nouvelles compétences et proposer des services.", 1.0),
    ("Quinze services digitaux que tu peux lancer immédiatement.", None),
    ("Cinquante scripts prêts à copier-coller sur WhatsApp.", None),
    ("Un plan concret… pour aller de zéro à cinq cent mille francs céfa avant le trente et un décembre.", 1.0),
    ("Et en plus… tu rejoins mon canal WhatsApp personnel.", None),
    ("Je t'accompagne directement. Tu n'es pas seul.", 1.5),
    ("Chaque jour où tu attends… est un jour de revenus perdus.", 1.0),
    ("Le lien est juste en bas.", None),
    ("Accès instantané.", None),
    ("Paiement mobile accepté.", 0.5),
    ("Le changement commence aujourd'hui.", None),
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
    starts = []
    for i, (txt, pause) in enumerate(SEGMENTS):
        if i > 0:
            gap = SEGMENTS[i - 1][1]
            gap = NAT_GAP if gap is None else gap
            out = np.concatenate([out, np.zeros(int(gap * SR), dtype=np.float32)])
        starts.append(round(len(out) / SR, 3))
        clip = say(tts, txt, REF, NATURAL)
        clip = clip / (np.max(np.abs(clip)) + 1e-9) * 0.97
        out = np.concatenate([out, clip])
        print(f"  [{i:02d}] start={starts[-1]:6.2f}s  dur={len(clip)/SR:4.2f}s  {txt[:48]}")

    out = out / (np.max(np.abs(out)) + 1e-9) * 0.97
    narr = os.path.join(BUILD, "narration.wav")
    sf.write(narr, out, SR)
    narr_dur = len(out) / SR
    print(f"narration: {narr_dur:.2f}s -> {narr}")

    fb = ffmpeg_bin()
    # master the voice (no length change)
    master = os.path.join(BUILD, "narration_master.mp3")
    subprocess.run([fb, "-y", "-loglevel", "error", "-i", narr, "-af", FX_FILTER,
                    "-ar", "44100", "-b:a", "192k", master], check=True)

    # pad voice + duck music under it -> finished spot
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
    spot_dur = duration(spot)

    with open(os.path.join(ROOT, "timeline.js"), "w", encoding="utf-8") as f:
        f.write("window.TIMELINE = " + json.dumps(starts) + ";\n")
        f.write(f"window.DURATION = {spot_dur:.3f};\n")
    print(f"spot: {spot_dur:.2f}s -> {spot}")
    print(f"timeline.js written ({len(starts)} lines)")


if __name__ == "__main__":
    main()
