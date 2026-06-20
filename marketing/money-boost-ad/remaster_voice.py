#!/usr/bin/env python3
"""Re-master the existing narration into a DEEPER, more assured "mature coach"
voice (no re-synthesis), rebuild the ducked music spot, and re-mux it into the
already-rendered video without re-rendering frames.

    pitch down ~1.1 semitone  ->  graver / chestier timbre
    body 110-210 Hz           ->  fills the "hollow" scoop
    cut 500/900 Hz boxiness    ->  removes boxy hollowness (not the mids)
    presence 3 kHz + firm comp ->  authority / assurance
"""
import os
import subprocess

import imageio_ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
VOICE_DIR = os.path.abspath(os.path.join(ROOT, "..", "okf-voice"))
MUSIC = os.path.join(VOICE_DIR, "assets", "music_bg.m4a")
NARR = os.path.join(BUILD, "narration.wav")
MASTER = os.path.join(BUILD, "narration_master.mp3")
SPOT = os.path.join(BUILD, "spot.mp3")
VIDEO = os.path.join(ROOT, "money-boost-video.mp4")
OUT = os.path.join(ROOT, "money-boost-video_deep.mp4")

TAIL = 2.6
MUSIC_VOL = 0.34
FF = imageio_ffmpeg.get_ffmpeg_exe()

# pitch down (formants travel down too -> bigger, more mature chest) + cleanup + EQ
PITCH = "asetrate=24000*0.935,atempo=1.069519,aresample=44100"
CLEAN = "adeclick=window=55:overlap=75,adeclip,afftdn=nf=-25:nr=12"
DEEP = (
    "highpass=f=55,"
    "equalizer=f=110:t=q:w=1.0:g=4,"      # chest / body
    "equalizer=f=210:t=q:w=1.2:g=2.5,"    # warmth -> kills the hollow feel
    "equalizer=f=500:t=q:w=1.4:g=-2.5,"   # tame boxiness
    "equalizer=f=900:t=q:w=1.4:g=-1.5,"   # tame remaining honk
    "equalizer=f=3000:t=q:w=1.1:g=3,"     # presence / authority
    "equalizer=f=9000:t=q:w=1.0:g=1.5,"   # air
    "acompressor=threshold=-20dB:ratio=3.5:attack=12:release=200:makeup=4,"
    "alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=10"
)


def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=nk=1:nw=1", path]).decode().strip()
    return float(out)


def main():
    # 1. deep master of the voice (pitch + cleanup + EQ), duration preserved
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", NARR, "-af",
                    PITCH + "," + CLEAN + "," + DEEP, "-ar", "44100", "-b:a", "192k",
                    MASTER], check=True)
    narr_dur = dur(MASTER)
    print(f"deep master: {narr_dur:.2f}s")

    # 2. rebuild ducked music spot (same recipe as make_spot_ad.py)
    total = narr_dur + TAIL
    fade_out = max(0.0, total - 2.6)
    padded = os.path.join(BUILD, "_voice_padded.wav")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", MASTER,
                    "-af", f"apad=pad_dur={TAIL}", "-ar", "44100", padded], check=True)
    flt = (
        f"[0:a]aresample=44100,atrim=0:{total:.2f},volume={MUSIC_VOL},"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out:.2f}:d=2.6[mus];"
        f"[mus][1:a]sidechaincompress=threshold=0.035:ratio=7:attack=5:release=320:makeup=1[duck];"
        f"[1:a][duck]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix];"
        f"[mix]loudnorm=I=-14:TP=-1.0:LRA=11[out]"
    )
    subprocess.run([FF, "-y", "-loglevel", "error", "-stream_loop", "1",
                    "-i", MUSIC, "-i", padded, "-filter_complex", flt,
                    "-map", "[out]", "-ar", "44100", "-b:a", "192k", SPOT], check=True)
    os.remove(padded)
    print(f"spot: {dur(SPOT):.2f}s")

    # 3. re-mux into the existing video (no frame re-render)
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", VIDEO, "-i", SPOT,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], check=True)
    os.replace(OUT, VIDEO)
    print(f"re-muxed -> {VIDEO}  ({dur(VIDEO):.2f}s)")


if __name__ == "__main__":
    main()
