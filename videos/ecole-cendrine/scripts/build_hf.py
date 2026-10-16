"""Génère index.html (composition HyperFrames) du film « L'école de Joachim Branco » — concours Origines.

Entrées : scripts/timeline.json (edit.py : segments + mots recalés), scripts/shots.json (plans photo rendus
par cam.py dans assets/shots), scripts/template.html.
Usage : python3 scripts/build_hf.py
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "scripts/timeline.json")))
SHOTS = json.load(open(os.path.join(ROOT, "scripts/shots.json")))["shots"]
SEG = {s["id"]: s for s in TL["segments"]}
DUR = 110.6


def word_t(seg, prefix, n=0):
    """Temps de sortie du n-ième mot du segment qui commence par prefix."""
    hits = [a for a, b, w, s in TL["words"] if s == seg and w.lower().lstrip("'-").startswith(prefix.lower())]
    return hits[n]


T = {  # repères de synchronisation (s)
    "esclave": word_t("A", "esclave"),
    "change": word_t("B", "changé"),
    "ne": word_t("C", "né"),
    "mahi": word_t("C", "marie"),
    "vendu": word_t("D", "vendu"),
    "bresil": word_t("D", "Brésil"),
    "traite": word_t("D", "traite"),
    "abolition": word_t("E", "évolution"),
    "y1888": word_t("E", "1888"),
    "nomme": word_t("E", "Blanco"),
    "y1927": word_t("G", "1927"),
    "ecole": word_t("G", "école"),
    "centaines": word_t("I", "centaines"),
    "statue": word_t("J", "statue"),
    "y2025": word_t("J", "2025"),
    "cetait": word_t("K", "était"),
}

# ---------------------------------------------------------------- plans
clips = []
for sid, ph, a, b, c0, c1, opts in SHOTS:
    clips.append({"id": sid, "src": f"assets/shots/{sid}.mp4", "start": a, "dur": round(b - a, 3), "retro": "retro=1" in opts})
# paires couleur ↔ rétro : la version rétro est posée au-dessus et fondue à l'instant donné
XFADE = [("s05", "s05r", T["change"] - 0.15, 0.6, "to_retro"), ("s12r", "s12", T["ecole"] - 0.35, 0.7, "to_color")]

# ---------------------------------------------------------------- sous-titres
FIX = {  # corrections de la transcription automatique (noms propres, mots mal reconnus)
    "Joaquin": "Joachim", "Joaquim": "", "Blanco": "Branco", "Blanco,": "Branco,", "Aquacom,": "Agouagon,", "marie": "mahi",
    "courriers.": "Collines.", "durment": "durement", "'évolution": "'abolition", "vieux": "homme", "-fait": "", "entait,": "obtint", "enfin,": "enfin",
    "Aguagón,": "Agouagon,", "profs.": "frais.", "assez": "accès", "stupéfait": "stupéfaction", "Agua": "Agoua", "Edsmo.": "Edmond.",
    "ma": "m'avoir", "voix": "", "Sandrine": "Cendrine", "Tameillon,": "Tamegnon,", "'Agua": "'Agouagon", "Compact": "",
}
DROP_AFTER = {("E", "-fait"): 2}       # « vieux-fait d'un nommé » → « homme nommé »
HL = {"esclave", "Brésil,", "1888,", "Branco", "Branco,", "1927,", "école", "Agouagon,", "statue", "2025", "centaines", "fière", "Agouagon"}


def captions():
    words, skip = [], 0
    for a, b, w, s in TL["words"]:
        if skip:
            skip -= 1
            continue
        if (s, w) in DROP_AFTER:
            skip = DROP_AFTER[(s, w)]
        w2 = FIX.get(w, w) if not (s == "J" and w == "Agua") else "Agoua"
        if s == "A" and w == "-vous":
            w2 = "-vous"
        if not w2:
            continue
        if words and (w2.startswith("'") or w2.startswith("-")) and words[-1][3] == s:
            words[-1][2] += w2
            words[-1][1] = b
            continue
        words.append([a, b, w2, s])
    lines, cur = [], []
    for wd in words:
        if cur and (wd[3] != cur[-1][3] or wd[0] - cur[-1][1] > 1.1 or len(" ".join(x[2] for x in cur + [wd])) > 32):
            lines.append(cur)
            cur = []
        cur.append(wd)
        if wd[2][-1] in ".?," and len(" ".join(x[2] for x in cur)) > 14:
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    weak = {"en", "de", "la", "le", "les", "des", "que", "à", "une", "un", "du", "par", "et", "a", "été", "dans", "ses", "sa", "mis", "avec", "l'honorable", "20"}
    for _ in range(3):   # pas de ligne qui finit sur un mot outil ; pas de mot orphelin
        for k in range(len(lines) - 1):
            if len(lines[k]) > 1 and lines[k][-1][2].lower() in weak and lines[k][-1][3] == lines[k + 1][0][3]:
                lines[k + 1].insert(0, lines[k].pop())
        k = 0
        while k < len(lines):
            ln = lines[k]
            if len(" ".join(x[2] for x in ln)) < 11 and k > 0 and lines[k - 1][-1][3] == ln[0][3] and len(" ".join(x[2] for x in lines[k - 1] + ln)) <= 42:
                lines[k - 1] += ln
                del lines[k]
                continue
            k += 1
    out = []
    for k, ln in enumerate(lines):
        a = ln[0][0]
        b = min(ln[-1][1] + 0.35, lines[k + 1][0][0] if k + 1 < len(lines) else ln[-1][1] + 0.6)
        text = " ".join(x[2] for x in ln)
        out.append((round(a, 2), round(b, 2), text))
    return out


CAPS = captions()

SFX = [("whoosh-cinematic", 0.0, 0.3), ("whoosh-short", 3.2, 0.2), ("whoosh-short", 6.6, 0.2), ("impact-bass-1", 9.4, 0.45),
       ("riser", T["change"] - 1.6, 0.18), ("whoosh-cinematic", 16.3, 0.3), ("whoosh-short", 21.8, 0.18),
       ("whoosh-short", 27.3, 0.2), ("impact-bass-1", T["vendu"] + 0.05, 0.3), ("whoosh-short", 34.8, 0.18),
       ("whoosh-short", 39.6, 0.2), ("impact-bass-1", T["abolition"] + 0.1, 0.3), ("impact-bass-1", T["y1888"], 0.4),
       ("whoosh-short", 45.2, 0.18), ("whoosh-short", 51.6, 0.18), ("impact-bass-1", T["y1927"], 0.35),
       ("whoosh-short", 58.7, 0.18), ("whoosh-cinematic", 64.3, 0.22), ("sparkle", T["ecole"], 0.2),
       ("whoosh-short", 71.7, 0.2), ("whoosh-short", 75.6, 0.18), ("whoosh-short", 79.9, 0.2), ("whoosh-short", 86.5, 0.18),
       ("whoosh-short", 90.5, 0.18), ("impact-bass-1", T["y2025"], 0.35), ("whoosh-cinematic", 96.4, 0.25),
       ("chime", 105.0, 0.3), ("sparkle", 107.6, 0.25)]


def build():
    vids = []
    for c in clips:
        cls = "wrap retro" if c["retro"] else "wrap"
        vids.append(f'      <div class="{cls}" id="w-{c["id"]}"><video id="v-{c["id"]}" class="clip" src="{c["src"]}" data-start="{c["start"]}" '
                    f'data-duration="{c["dur"]}" data-track-index="{2 if c["id"] in ("s05r", "s12") else 1}" muted playsinline></video></div>')
    caps = "\n".join(
        f'      <div class="cap" id="cap{i}">' + " ".join(
            f'<span class="{"hl" if w in HL else ""}">{html.escape(w)}</span>' for w in text.split(" ")) + "</div>"
        for i, (a, b, text) in enumerate(CAPS))
    sfx = "\n".join(f'      <audio id="sfx{i}" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2.5" data-track-index="{20 + i % 6}" data-volume="{v}"></audio>'
                    for i, (n, t, v) in enumerate(SFX))
    data = {"clips": clips, "dur": DUR, "seg": SEG, "t": T, "xfade": XFADE, "caps": [[a, b] for a, b, _ in CAPS]}
    tpl = open(os.path.join(ROOT, "scripts/template.html")).read()
    out = (tpl.replace("<!--CLIPS-->", "\n".join(vids)).replace("<!--CAPS-->", caps).replace("<!--SFX-->", sfx)
           .replace("/*DATA*/", json.dumps(data)).replace("__DUR__", str(DUR)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html —", len(clips), "plans,", len(CAPS), "sous-titres, durée", DUR, "s")
    for a, b, t in CAPS:
        print(f"  {a:6.2f}-{b:6.2f} {t}")


if __name__ == "__main__":
    build()
