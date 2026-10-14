"""Sujet détouré (WebM VP9 avec transparence) à poser AU-DESSUS des grands mots, pour que le texte passe derrière elle.
Utilise le plan traité + son masque (cine.py). Le bord du masque est légèrement resserré puis adouci.
Usage : python3 scripts/make_fg.py p05 [p10 ...]
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for sid in sys.argv[1:]:
    s = os.path.join(ROOT, "assets/shots")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", f"{s}/{sid}.mp4", "-i", f"{s}/{sid}-alpha.mkv", "-filter_complex",
        "[0:v]scale=1080:1920[c];[1:v]scale=1080:1920:flags=bicubic,format=gray,"
        "lutyuv=y='clip((val-40)*1.25,0,255)',gblur=sigma=1.2[a];[c][a]alphamerge,format=yuva420p[o]",
        "-map", "[o]", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M", "-auto-alt-ref", "0", "-row-mt", "1",
        "-deadline", "good", "-cpu-used", "4", f"{s}/{sid}-fg.webm"], check=True)
    print(sid, "→", f"{sid}-fg.webm")
