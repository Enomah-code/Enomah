"""Génère index.html (composition HyperFrames) du film « L'école de Joachim Branco » — concours Origines.
Version intégrale de la voix off.

Entrées : scripts/timeline.json (edit.py), scripts/texte.txt (texte corrigé, recalé par align.py),
scripts/shots.json (plans photo rendus par cam.py), scripts/template.html.
Usage : python3 scripts/build_hf.py [-v]
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align import aligned  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = json.load(open(os.path.join(ROOT, "scripts/shots.json")))["shots"]
WORDS = aligned()
DUR = 369.8
END = 363.6          # début du carton final (logo Origines puis affiche)


def at(sent, prefix, n=0):
    """Temps de début du n-ième mot de la phrase `sent` (1 = première) qui commence par `prefix`."""
    hits = [a for a, b, w, s in WORDS if s == sent - 1 and w.lower().startswith(prefix.lower())]
    return hits[n]


T = {  # repères de synchronisation (s)
    "esclave": at(1, "esclave"), "change": at(2, "changé"),
    "nom1": at(5, "Joachim"), "ne": at(7, "né"), "mahi": at(7, "mahi"),
    "vendu": at(8, "vendu"), "bresil": at(8, "Brésil"), "traite": at(8, "traite"),
    "abolition": at(9, "l'abolition"), "y1888": at(9, "1888"), "nomme": at(9, "Branco"),
    "ascension": at(10, "ascension"), "ancien": at(10, "ancien"),
    "cigarettes": at(11, "cigarettes"), "emigra": at(11, "émigra"), "nigeria": at(11, "Nigeria"), "succes": at(11, "succès"),
    "y1927": at(12, "1927"), "ecole": at(12, "école"),
    "emancip": at(16, "outil"), "y2017": at(19, "2017"), "ans90": at(19, "90e"),
    "ada": at(20, "ADA"), "ajap": at(20, "AJAP"),
    "lien": at(21, "lien"), "conclure": at(24, "Enfin"), "centaines": at(25, "centaines"),
    "dept": at(7, "département"), "adopte": at(9, "adopté"), "societe": at(10, "société"), "economique": at(10, "économique"),
    "alpha": at(18, "d'alphabétisation"), "elite": at(18, "élite"), "identite": at(18, "l'identité"), "voisins": at(22, "élèves"),
    "cles": at(27, "rappelant"), "statue": at(28, "statue"), "y2025": at(29, "2025"), "cetait": at(31, "C'était"),
}

# ---------------------------------------------------------------- plans
clips = []
for sid, ph, a, b, c0, c1, opts in SHOTS:
    clips.append({"id": sid, "src": f"assets/shots/{sid}.mp4", "start": a, "dur": round(b - a, 3), "retro": "retro=1" in opts})
LAYERS = ("s05r", "v14")          # couches posées au-dessus pour les fondus couleur ↔ film ancien
XFADE = [("s05", "s05r", T["change"] - 0.15, 0.6), ("v14r", "v14", T["ecole"] - 0.35, 0.7)]
FLASH = [9.45, 16.4, T["ecole"] - 0.1, 333.1]

T["mahi2"] = T["dept"] + 1.9

# scènes animées (motion design 2D/3D) : id → (début, durée) ; elles comblent les trous entre plans photo
PARCH = {"rewind": (16.4, 3.16), "resil": (40.3, 6.6), "zoom": (58.3, 6.0), "map": (64.3, 12.0), "y1888": (76.3, 12.4),
         "stairs": (88.7, 12.7), "map2": (101.4, 17.4), "net": (118.8, 6.9), "obj": (156.73, 5.48), "pillars": (202.31, 8.76),
         "c2017": (211.07, 7.33), "cada": (228.86, 7.44), "villages": (260.1, 14.85), "ctl": (284.01, 15.56), "cq": (312.85, 15.58)}

# titres posés sur les plans : id, entrée, sortie
TITLES = [("t-name", T["nom1"] - 0.1, 40.1), ("t-ne", T["ne"] - 0.1, 58.1), ("t-1927", T["y1927"] - 0.15, 132.8), ("t-auj", T["ecole"] + 0.1, 146.8),
          ("t-emancip", T["emancip"] - 0.1, 188.8), ("t-cent", T["centaines"] - 0.1, 306.4),
          ("t-2025", T["y2025"] - 0.2, 344.7)]

HL = {"esclave", "esclave.", "Brésil,", "1888,", "Branco", "Branco,", "1927,", "école", "Agouagon,", "statue", "2025,", "centaines",
      "fière", "2017,", "90e", "Nigeria", "cigarettes", "cigarettes.", "ADA,", "AJAP,", "d'émancipation", "lien", "l'éducation."}


def captions():
    words = [[a, b, w, s] for a, b, w, s in WORDS]
    lines, cur = [], []
    for wd in words:
        if cur and (wd[3] != cur[-1][3] or len(" ".join(x[2] for x in cur + [wd])) > 32):
            lines.append(cur)
            cur = []
        cur.append(wd)
        if wd[2][-1] in ".?," and len(" ".join(x[2] for x in cur)) > 14:
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    weak = {"en", "de", "la", "le", "les", "des", "que", "à", "une", "un", "du", "par", "et", "a", "été", "dans", "ses", "sa", "mis",
            "avec", "l'honorable", "20", "aux", "au", "pour", "qui", "son", "sur", "ce", "nous", "il", "elle", "est"}
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
        out.append((round(a, 2), round(max(b, a + 0.5), 2), " ".join(x[2] for x in ln)))
    return out


CAPS = captions()

SFX = [("whoosh-cinematic", 0.0, 0.3), ("impact-bass-1", 9.4, 0.45), ("riser", T["change"] - 1.6, 0.18), ("whoosh-cinematic", 16.3, 0.3),
       ("impact-bass-1", T["vendu"] + 0.05, 0.3), ("impact-bass-1", T["abolition"] + 0.1, 0.3), ("impact-bass-1", T["y1888"], 0.4),
       ("impact-bass-1", T["y1927"], 0.35), ("whoosh-cinematic", 138.7, 0.22), ("sparkle", T["ecole"], 0.2),
       ("impact-bass-1", T["y2017"], 0.3), ("sparkle", T["ans90"], 0.2), ("impact-bass-1", T["y2025"], 0.35),
       ("whoosh-cinematic", 333.0, 0.25), ("riser", 16.0, 0.16), ("impact-bass-1", 88.7 + 8.4, 0.3), ("impact-bass-1", T["nomme"], 0.35),
       ("impact-bass-1", 260.1 + 7.4, 0.3), ("sparkle", T["alpha"], 0.15), ("sparkle", T["elite"], 0.15), ("sparkle", T["identite"], 0.15),
       ("impact-bass-1", T["mahi2"] + 0.4, 0.3), ("chime", END + 0.4, 0.3), ("sparkle", END + 3.0, 0.25)]
# un souffle discret sur chaque coupe
CUTS = sorted({c["start"] for c in clips if c["start"] > 0 and c["id"] not in LAYERS} | {a for a, d in PARCH.values()})
SFX += [("whoosh-short", t - 0.1, 0.14) for t in CUTS if all(abs(t - s[1]) > 0.6 for s in SFX)]


def build():
    vids = []
    for c in clips:
        cls = "wrap retro" if c["retro"] else "wrap"
        vids.append(f'      <div class="{cls}" id="w-{c["id"]}"><video id="v-{c["id"]}" class="clip" src="{c["src"]}" data-start="{c["start"]}" '
                    f'data-duration="{c["dur"]}" data-track-index="{2 if c["id"] in LAYERS else 1}" muted playsinline></video></div>')
    caps = "\n".join(
        f'      <div class="cap" id="cap{i}">' + " ".join(
            f'<span class="{"hl" if w in HL else ""}">{html.escape(w)}</span>' for w in text.split(" ")) + "</div>"
        for i, (a, b, text) in enumerate(CAPS))
    sfx = "\n".join(f'      <audio id="sfx{i}" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2.5" data-track-index="{20 + i % 6}" data-volume="{v}"></audio>'
                    for i, (n, t, v) in enumerate(sorted(SFX, key=lambda x: x[1])))
    data = {"clips": clips, "dur": DUR, "end": END, "t": T, "xfade": XFADE, "flash": FLASH, "parch": PARCH, "titles": TITLES,
            "layers": LAYERS, "caps": [[a, b] for a, b, _ in CAPS]}
    tpl = open(os.path.join(ROOT, "scripts/template.html")).read()
    out = (tpl.replace("<!--CLIPS-->", "\n".join(vids)).replace("<!--CAPS-->", caps).replace("<!--SFX-->", sfx)
           .replace("/*DATA*/", json.dumps(data)).replace("__DUR__", str(DUR)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html —", len(clips), "plans,", len(PARCH), "scènes parchemin,", len(CAPS), "sous-titres,", len(SFX), "bruitages, durée", DUR, "s")


if __name__ == "__main__":
    build()
    if "-v" in sys.argv:
        for a, b, t in CAPS:
            print(f"  {a:6.2f}-{b:6.2f} {t}")
