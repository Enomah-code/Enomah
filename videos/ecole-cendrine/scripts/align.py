"""Recale le texte corrigé (scripts/texte.txt, une phrase par ligne) sur les mots horodatés de la transcription
(scripts/timeline.json). Chaque mot corrigé reçoit les temps du mot reconnu correspondant (difflib) ;
les mots sans correspondance sont interpolés entre leurs voisins.
Renvoie [(début, fin, mot, n° de phrase)]."""
import difflib
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def aligned():
    tl = json.load(open(os.path.join(ROOT, "scripts/timeline.json")))
    src = []
    for a, b, w, _ in tl["words"]:      # recolle « d 'un », « -vous »…
        if src and (w.startswith("'") or w.startswith("-")):
            src[-1] = [src[-1][0], b, src[-1][2] + w]
        else:
            src.append([a, b, w])
    lines = [l.strip() for l in open(os.path.join(ROOT, "scripts/texte.txt")) if l.strip()]
    dst = [(w, i) for i, l in enumerate(lines) for w in l.split(" ")]
    sm = difflib.SequenceMatcher(a=[norm(w) for w in (x[2] for x in src)], b=[norm(w) for w, _ in dst], autojunk=False)
    t = [None] * len(dst)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            t[blk.b + k] = (src[blk.a + k][0], src[blk.a + k][1])
    # interpolation des trous
    known = [i for i, v in enumerate(t) if v]
    for i in range(len(t)):
        if t[i] is None:
            p = max([k for k in known if k < i], default=None)
            n = min([k for k in known if k > i], default=None)
            if p is None:
                t[i] = (t[n][0], t[n][0])
            elif n is None:
                t[i] = (t[p][1], t[p][1] + 0.3)
            else:
                f0, f1 = (i - p) / (n - p), (i - p + 1) / (n - p)
                a, b = t[p][1], t[n][0]
                t[i] = (a + (b - a) * f0 * 0.98, a + (b - a) * f1 * 0.98)
    return [(round(t[i][0], 3), round(t[i][1], 3), w, s) for i, (w, s) in enumerate(dst)]


if __name__ == "__main__":
    al = aligned()
    cur = -1
    for a, b, w, s in al:
        if s != cur:
            print(f"\nS{s + 1} {a:7.2f}:", end=" ")
            cur = s
        print(f"{w}@{a:.1f}", end=" ")
    print()
