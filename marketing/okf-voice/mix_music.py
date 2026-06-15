#!/usr/bin/env python3
"""Mix a voice-over with background music, ducking the music under the voice.

The music is looped to cover the voice plus a short tail, level-dropped, faded
in/out, then side-chain compressed by the voice so it dips while you speak and
rises in the gaps. Output is loudness-normalised.

Examples:
    python3 mix_music.py --voice build/money_boost_myvoice_master.mp3
    python3 mix_music.py --voice vo.mp3 --music assets/music_bg.m4a --out build/spot.mp3
    python3 mix_music.py --voice vo.mp3 --music-vol 0.30 --tail 4
"""
import argparse
import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))


def ffmpeg_bin():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1", path]).decode().strip()
    return float(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, help="voice-over (the mastered VO)")
    ap.add_argument("--music", default=os.path.join(ROOT, "assets", "music_bg.m4a"))
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "money_boost_spot.mp3"))
    ap.add_argument("--music-vol", type=float, default=0.40, help="base music level (0-1)")
    ap.add_argument("--tail", type=float, default=3.2, help="music tail after the voice (s)")
    ap.add_argument("--duck", type=float, default=7.0, help="ducking ratio (higher = music dips more)")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    vdur = duration(args.voice)
    total = vdur + args.tail
    fade_out = max(0.0, total - 3.0)
    fb = ffmpeg_bin()

    # 1) pad the voice with trailing silence so the music can ring out and fade
    padded = os.path.join(os.path.dirname(args.out), "_voice_padded.wav")
    subprocess.run([fb, "-y", "-loglevel", "error", "-i", args.voice,
                    "-af", f"apad=pad_dur={args.tail}", "-ar", "44100", padded], check=True)

    # 2) loop + duck the music under the (padded) voice, then mix and normalise
    flt = (
        f"[0:a]aresample=44100,atrim=0:{total:.2f},volume={args.music_vol},"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out:.2f}:d=3.0[mus];"
        f"[mus][1:a]sidechaincompress=threshold=0.035:ratio={args.duck}:"
        f"attack=5:release=320:makeup=1[duck];"
        f"[1:a][duck]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[mix];"
        f"[mix]loudnorm=I=-14:TP=-1.0:LRA=11[out]"
    )
    subprocess.run([fb, "-y", "-loglevel", "error", "-stream_loop", "1",
                    "-i", args.music, "-i", padded, "-filter_complex", flt,
                    "-map", "[out]", "-ar", "44100", "-b:a", "192k", args.out], check=True)
    os.remove(padded)
    print(f"spot: {duration(args.out):.2f}s -> {args.out}")


if __name__ == "__main__":
    main()
