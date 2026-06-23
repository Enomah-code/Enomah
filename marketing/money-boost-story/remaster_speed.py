#!/usr/bin/env python3
"""Speed up the existing storytelling narration (~15%) WITHOUT re-synthesis:
same voice/timbre, pitch preserved, pauses tightened. Rebuild the music spot
and rescale timeline.js so captions/notifications stay in sync.
"""
import json
import os
import re
import subprocess

import imageio_ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
VOICE_DIR = os.path.abspath(os.path.join(ROOT, "..", "okf-voice"))
MUSIC = os.path.join(VOICE_DIR, "assets", "music_bg.m4a")
NARR = os.path.join(BUILD, "narration.wav")
MASTER = os.path.join(BUILD, "narration_master.mp3")
SPOT = os.path.join(BUILD, "spot.mp3")
TL = os.path.join(ROOT, "timeline.js")
FF = imageio_ffmpeg.get_ffmpeg_exe()

TEMPO = 1.16          # global speed-up (pitch preserved by atempo)
MUSIC_VOL = 0.30
TAIL = 2.5

# slight grave pitch (asetrate pair) + the speed-up atempo, then clean + master
PITCH_SPEED = f"asetrate=24000*0.985,atempo=1.015228,atempo={TEMPO},aresample=44100"
CLEAN = "adeclick=window=55:overlap=75,adeclip,afftdn=nf=-26:nr=11"
MASTER_EQ = (
    "highpass=f=60,equalizer=f=115:t=q:w=1.0:g=3,equalizer=f=200:t=q:w=1.2:g=1.5,"
    "equalizer=f=480:t=q:w=1.5:g=-2,equalizer=f=3000:t=q:w=1.1:g=2.5,"
    "equalizer=f=9000:t=q:w=1.0:g=1.3,"
    "acompressor=threshold=-19dB:ratio=3:attack=15:release=200:makeup=3,"
    "alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11"
)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=nk=1:nw=1", p]).decode().strip())


def main():
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", NARR, "-af",
                    PITCH_SPEED + "," + CLEAN + "," + MASTER_EQ, "-ar", "44100",
                    "-b:a", "192k", MASTER], check=True)
    narr_dur = dur(MASTER)

    total = narr_dur + TAIL
    fade_out = max(0.0, total - 2.5)
    padded = os.path.join(BUILD, "_vp.wav")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", MASTER,
                    "-af", f"apad=pad_dur={TAIL}", "-ar", "44100", padded], check=True)
    flt = (
        f"[0:a]aresample=44100,atrim=0:{total:.2f},volume={MUSIC_VOL},"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out:.2f}:d=2.5[mus];"
        f"[mus][1:a]sidechaincompress=threshold=0.035:ratio=7:attack=5:release=320:makeup=1[duck];"
        f"[1:a][duck]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix];"
        f"[mix]loudnorm=I=-14:TP=-1.0:LRA=11[out]"
    )
    subprocess.run([FF, "-y", "-loglevel", "error", "-stream_loop", "1",
                    "-i", MUSIC, "-i", padded, "-filter_complex", flt,
                    "-map", "[out]", "-ar", "44100", "-b:a", "192k", SPOT], check=True)
    os.remove(padded)
    spot_dur = dur(SPOT)

    # rescale timeline: atempo scales all timings uniformly by 1/TEMPO
    txt = open(TL, encoding="utf-8").read()
    seg = json.loads(re.search(r"window\.SEG\s*=\s*(\[.*?\]);", txt, re.S).group(1))
    for s in seg:
        s["t"] = round(s["t"] / TEMPO, 3)
    with open(TL, "w", encoding="utf-8") as f:
        f.write("window.SEG = " + json.dumps(seg, ensure_ascii=False) + ";\n")
        f.write(f"window.DURATION = {spot_dur:.3f};\n")
    print(f"narration {narr_dur:.2f}s  spot {spot_dur:.2f}s  (tempo {TEMPO})")


if __name__ == "__main__":
    main()
