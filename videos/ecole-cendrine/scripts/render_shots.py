"""Rend tous les plans photo de scripts/shots.json avec cam.py (ignore ceux déjà rendus).
Usage : python3 scripts/render_shots.py [id ...]"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
only = set(sys.argv[1:])
for sid, ph, a, b, c0, c1, opts in json.load(open(os.path.join(ROOT, "scripts/shots.json")))["shots"]:
    dst = os.path.join(ROOT, f"assets/shots/{sid}.mp4")
    if (only and sid not in only) or (not only and os.path.exists(dst)):
        continue
    src = os.path.join(ROOT, f"assets/up/{ph}.png")
    if not os.path.exists(src):
        print("attente agrandissement :", sid, ph, flush=True)
        continue
    if opts == "framed":   # photo presque carrée : image entière encadrée sur fond flou
        subprocess.run(["python3", os.path.join(ROOT, "scripts/framed.py"), src, dst, f"{b - a + 0.3:.2f}"], check=True, stdout=subprocess.DEVNULL)
        print("ok", sid, flush=True)
        continue
    subprocess.run(["python3", os.path.join(ROOT, "scripts/cam.py"), src, dst, f"{b - a + 0.3:.2f}", c0, c1] + opts.split(),
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("ok", sid, flush=True)
