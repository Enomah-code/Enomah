"""Assemble la variante HyperFrames : copie les assets partagés et remplit scripts/hf-template.html
avec les cartes modules, avatars, étoiles et sous-titres (shared/timeline.json + shared/content.json).
Usage : python3 scripts/build_hf.py
"""
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HF = os.path.join(ROOT, "hyperframes")
SH = os.path.join(ROOT, "shared")
TL = json.load(open(os.path.join(SH, "timeline.json")))
CT = json.load(open(os.path.join(SH, "content.json")))
STAR = '<svg viewBox="0 0 24 24"><path fill="#f2c14e" d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z" /></svg>'

for sub in ("img", "audio"):
    os.makedirs(os.path.join(HF, "assets", sub), exist_ok=True)
for f in ("certificat.png", "formation-vignette.png", "logo-formation.svg"):
    shutil.copy(os.path.join(SH, "img", f), os.path.join(HF, "assets/img", f))
shutil.copy(os.path.join(SH, "audio/mix.wav"), os.path.join(HF, "assets/audio/mix.wav"))
os.makedirs(os.path.join(HF, "assets/vendor"), exist_ok=True)
shutil.copy(os.path.join(ROOT, "../pub-ucg-ia-business-builder/assets/vendor/gsap.min.js"), os.path.join(HF, "assets/vendor/gsap.min.js"))

cards = "\n".join(
    f'        <div class="abs card" id="m-c{i + 1}"><div class="n">{c["n"]}</div>'
    f'<div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="#0b1838" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{c["icon"]}" /></svg></div>'
    f'<div class="t">{html.escape(c["t"])}</div><div class="s">{html.escape(c["s"])}</div></div>'
    for i, c in enumerate(CT["cards"]))
avatars = "".join(f'<div class="av" style="left:{i * 75}px;background:{col};z-index:{20 - i}">{l}</div>' for i, (l, col) in enumerate(CT["avatars"]))
caps_html = "\n".join(
    f'        <div class="cap" id="cap{i}">' + "".join(f'<span class="cw" id="cap{i}w{j}">{html.escape(w["w"])}</span>' for j, w in enumerate(c["words"])) + "</div>"
    for i, c in enumerate(TL["captions"]))
caps_js = json.dumps([{"s": c["s"], "e": c["e"], "words": [{"s": w["s"], "hl": w["hl"]} for w in c["words"]]} for c in TL["captions"]])

src = open(os.path.join(ROOT, "scripts/hf-template.html")).read()
src = (src.replace("        <!--CARDS-->", cards).replace("<!--AVATARS-->", avatars).replace("<!--STARS-->", STAR * 5)
       .replace("<!--CAPTIONS-->", "\n" + caps_html + "\n      ").replace("/*CAPS_JSON*/", caps_js))
open(os.path.join(HF, "index.html"), "w").write(src)
print("index.html ok —", len(TL["captions"]), "sous-titres")
