"""Génère index.html (composition HyperFrames) du film « Fière d'Agouagon » — concours Origines.

Entrées : scripts/edl.json, scripts/timeline.json (voice.py), suivis visage/mains (scripts/track/*.json),
plans traités (assets/shots), photos animées (assets/photos).
Variante A (par défaut) : zooms visage sur « voix / regard / valeurs ».
Variante B (VARIANT=B) : à cet endroit, plans de demi-tour / boucles d'oreilles au lieu des zooms.
Usage : python3 scripts/build_hf.py   (MUSIC=assets/audio/music.mp3 pour ajouter la musique)
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
VARIANT = os.environ.get("VARIANT", "A")
MUSIC = os.environ.get("MUSIC", "")

TL = json.load(open(os.path.join(ROOT, "scripts/timeline.json")))
SEG = {s["id"]: s for s in TL["segments"]}
EDL = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "scripts/edl.json")))["segments"]}
DUR = round(SEG["s12"]["start"] + SEG["s12"]["dur"], 3)


def st(sid):
    return SEG[sid]["start"]


# ---------------------------------------------------------------- plans (vidéo / photo) sur la piste image
clips = []   # (id, src, start, dur, kind)


def add(cid, src, start, dur, kind="shot"):
    clips.append({"id": cid, "src": src, "start": round(start, 3), "dur": round(dur, 3), "kind": kind})


add("ph01", "assets/photos/ph01.mp4", 0, SEG["s01"]["dur"] + 0.3, "photo")
add("p02a", "assets/shots/p02a.mp4", st("s02"), SEG["s02"]["dur"])
a3 = (7.7 - 6.1) / 0.6
add("p03a", "assets/shots/p03a.mp4", st("s03"), a3)
add("p03b", "assets/shots/p03b.mp4", st("s03") + a3, SEG["s03"]["dur"] - a3)
add("ph04", "assets/photos/ph04.mp4", st("s04"), SEG["s04"]["dur"], "photo")
add("p05", "assets/shots/p05.mp4", st("s05"), SEG["s05"]["dur"])
add("p06", "assets/shots/p06.mp4", st("s06"), SEG["s06"]["dur"])
add("ph07", "assets/photos/ph07.mp4", st("s07"), 2.0, "photo")
add("p07", "assets/shots/p07.mp4", st("s07") + 2.0, SEG["s07"]["dur"] - 2.0)
add("p08a", "assets/shots/p08a.mp4", st("s08"), 2.0)
add("p08b", "assets/shots/p08b.mp4", st("s08") + 2.0, SEG["s08"]["dur"] - 2.0)
add("p09a", "assets/shots/p09a.mp4", st("s09"), 3.6)
add("p09b", "assets/shots/p09b.mp4", st("s09") + 3.6, SEG["s09"]["dur"] - 3.6)
add("p10", "assets/shots/p10.mp4", st("s10"), SEG["s10"]["dur"])
VILLAGE = (56.75 - 49.7 + st("s10"), 2.2)          # plan de coupe « merci à mon village »
add("ph10", "assets/photos/ph10.mp4", VILLAGE[0], VILLAGE[1], "photo")
TILT = st("s11") + 6.0                             # départ du panoramique vers le ciel
add("p11", "assets/shots/p11.mp4", st("s11"), 6.4)
add("sky", "assets/photos/sky.mp4", TILT - 0.1, DUR - TILT + 0.1, "photo")
FG = [  # sujets détourés (alpha) pour les mots placés DERRIÈRE elle
    {"id": "fg05", "src": "assets/shots/p05-fg.webm", "start": st("s05"), "dur": SEG["s05"]["dur"], "host": "p05", "label": "Fierté"},
    {"id": "fg10", "src": "assets/shots/p10-fg.webm", "start": st("s10"), "dur": SEG["s10"]["dur"], "host": "p10", "label": "ORIGINES"},
]

# ---------------------------------------------------------------- sous-titres (temps de sortie)
CAPS = [
    (3.54, 5.10, "Hello la famille,", []),
    (5.16, 6.50, "j'espère que vous allez très bien,", []),
    (6.56, 8.80, "moi je vais bien, par la grâce de Dieu.", []),
    (9.04, 11.0, "Aujourd'hui, je veux vous partager un petit secret.", ["secret."]),
    (11.7, 13.5, "Oui, je veux vous partager ma fierté,", ["fierté,"]),
    (13.72, 16.5, "la fierté que j'ai d'appartenir à Agouagon.", ["Agouagon."]),
    (16.8, 19.0, "Je n'ai peut-être pas tous les mots pour l'exprimer,", []),
    (19.12, 20.9, "mais je sais ce que je ressens.", []),
    (22.6, 24.85, "De la fierté qui vient du cœur.", ["cœur."]),
    (24.95, 27.4, "Agouagon m'a appris qui j'étais.", ["Agouagon"]),
    (27.95, 29.1, "J'ai appris…", []),
    (32.2, 34.2, "… de ceux qui m'ont précédé.", []),
    (34.5, 36.45, "Et aujourd'hui, tout ce que je suis", []),
    (36.5, 38.6, "a commencé là-bas.", ["là-bas."]),
    (38.96, 40.35, "Et où que j'aille,", []),
    (40.42, 42.3, "Agouagon vient toujours avec moi.", ["Agouagon"]),
    (42.5, 44.5, "Parce qu'à chaque fois qu'on me demande", []),
    (44.6, 46.5, "« Tu viens d'où ? »", []),
    (49.95, 50.95, "dans ma voix,", ["voix,"]),
    (51.3, 52.6, "dans mon regard", ["regard"]),
    (52.62, 53.95, "et dans mes valeurs.", ["valeurs."]),
    (54.04, 56.7, "Alors aujourd'hui, je le dis simplement :", []),
    (56.8, 58.95, "merci à mon village,", ["village,"]),
    (59.0, 60.45, "merci à ma famille", ["famille"]),
    (60.5, 61.75, "et merci à mes origines.", ["origines."]),
    (64.85, 66.55, "fille d'Agouagon, village mahi,", ["Agouagon,"]),
    (66.6, 69.1, "et toujours fière de l'être.", ["fière"]),
]

# ---------------------------------------------------------------- zooms suivant le visage (p10, variante A)
def face_zoom_sets():
    fj = os.path.join(ROOT, "scripts/track/face_p10.json")
    if VARIANT != "A" or not os.path.exists(fj):
        return []
    fr = json.load(open(fj))
    # lissage (moyenne glissante 9 images) du point visé
    import numpy as np
    ex = np.array([f.get("ex", 0.5) for f in fr]); ey = np.array([f.get("ey", 0.25) for f in fr])
    mx = np.array([f.get("mx", 0.5) for f in fr]); my = np.array([f.get("my", 0.32) for f in fr])
    k = np.ones(9) / 9
    sm = lambda a: np.convolve(np.pad(a, 4, mode="edge"), k, mode="valid")
    ex, ey, mx, my = sm(ex), sm(ey), sm(mx), sm(my)
    s0 = st("s10")
    keys = [  # (temps de sortie, zoom, cible) — la cible bascule bouche → yeux → plan large
        (49.7, 1.06, "eyes"), (50.25, 1.06, "eyes"), (50.55, 1.75, "mouth"), (51.35, 1.75, "mouth"),
        (51.75, 2.05, "eyes"), (52.75, 2.05, "eyes"), (53.25, 1.0, "wide"), (54.0, 1.0, "wide"),
        (56.6, 1.18, "eyes"), (59.0, 1.12, "eyes"), (61.75, 1.22, "eyes")]
    out = []
    n = len(fr)
    for i in range(0, n, 1):
        t = s0 + i / 30
        if t >= s0 + SEG["s10"]["dur"]:
            break
        # interpolation du zoom et du mélange de cible
        for j in range(len(keys) - 1):
            if keys[j][0] <= t <= keys[j + 1][0]:
                a, b = keys[j], keys[j + 1]
                u = (t - a[0]) / max(1e-6, b[0] - a[0])
                u = u * u * (3 - 2 * u)
                break
        else:
            a = b = keys[-1]; u = 0
        z = a[1] + (b[1] - a[1]) * u

        def pt(kind):
            if kind == "mouth":
                return mx[i] * W, (my[i] + 0.035) * H
            if kind == "eyes":
                return ex[i] * W, ey[i] * H
            return W / 2, H * 0.45
        (ax, ay), (bx, by) = pt(a[2]), pt(b[2])
        tx, ty = ax + (bx - ax) * u, ay + (by - ay) * u
        cxs, cys = W / 2, H * 0.40               # où placer la cible à l'écran
        x = cxs - z * tx; y = cys - z * ty
        x = min(0, max(W - W * z, x)); y = min(0, max(H - H * z, y))
        if i % 2 == 0:
            out.append((round(t, 3), round(x, 1), round(y, 1), round(z, 4)))
    return out


# ---------------------------------------------------------------- mots qui sortent des mains (p06)
def hand_words():
    hj = os.path.join(ROOT, "scripts/track/hands_p06.json")
    fr = json.load(open(hj)) if os.path.exists(hj) else []
    s0, rush_in = st("s06"), 4.7
    words = [("PARTAGE", 29.27), ("RESPECT", 30.65), ("FORCE", 31.97)]
    slots = [(W * 0.5, H * 0.105), (W * 0.5, H * 0.165), (W * 0.5, H * 0.225)]
    res = []
    for (w, t), (sx, sy) in zip(words, slots):
        lt = t - s0 + rush_in
        best = min(fr, key=lambda f: abs(f["t"] - lt) + (0 if len(f["hands"]) == 2 else 0.2)) if fr else None
        if best and best["hands"]:
            hs = best["hands"]
            px = sum(h["ix"] for h in hs) / len(hs) * W
            py = sum(h["iy"] for h in hs) / len(hs) * H
        else:
            px, py = W * 0.5, H * 0.62
        res.append({"w": w, "t": t, "px": round(px), "py": round(py), "sx": round(sx), "sy": round(sy)})
    return res


SFX = [("whoosh-cinematic", 0.0, 0.35), ("whoosh-short", st("s02") - 0.15, 0.25), ("whoosh-short", st("s04") - 0.12, 0.25),
       ("whoosh-short", st("s05") - 0.12, 0.22), ("impact-bass-1", 21.4, 0.32), ("sparkle", 29.27, 0.3), ("sparkle", 30.65, 0.3),
       ("sparkle", 31.97, 0.3), ("whoosh-short", st("s07") - 0.12, 0.22), ("whoosh-short", st("s09") - 0.12, 0.22),
       ("whoosh-short", VILLAGE[0] - 0.1, 0.22), ("impact-bass-1", 60.9, 0.3), ("whoosh-cinematic", TILT - 0.2, 0.35),
       ("chime", st("s12") + 0.25, 0.3), ("sparkle", st("s12") + 2.6, 0.25)]


def build():
    vids = []
    for c in clips:
        vids.append(
            f'      <div class="wrap" id="w-{c["id"]}"><video id="v-{c["id"]}" class="clip" src="{c["src"]}" data-start="{c["start"]}" '
            f'data-duration="{c["dur"]}" data-track-index="{1 if c["kind"] == "shot" else 2}" muted playsinline></video>'
            + "".join(
                f'<div class="behind" id="txt-{f["id"]}">{f["label"]}</div><video id="v-{f["id"]}" class="clip fg" src="{f["src"]}" data-start="{f["start"]}" '
                f'data-duration="{f["dur"]}" data-track-index="3" muted playsinline></video>' for f in FG if f["host"] == c["id"])
            + ("".join(f'<div class="hw" id="hw{i}"><span>{w["w"]}</span></div><div class="burst" id="bu{i}">' +
                       "".join('<i></i>' for _ in range(10)) + '</div>' for i, w in enumerate(hand_words())) if c["id"] == "p06" else "")
            + "</div>")
    caps = "\n".join(
        f'      <div class="cap" id="cap{i}">' + " ".join(
            f'<span class="{"hl" if w in hl else ""}">{html.escape(w)}</span>' for w in text.split(" ")) + "</div>"
        for i, (a, b, text, hl) in enumerate(CAPS))
    caps_js = json.dumps([[a, b] for a, b, _, _ in CAPS])
    sfx = "\n".join(f'      <audio id="sfx{i}" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + i % 6}" data-volume="{v}"></audio>'
                    for i, (n, t, v) in enumerate(SFX))
    music = (f'      <audio id="music" src="{MUSIC}" data-start="0" data-duration="{DUR}" data-track-index="11" data-volume="0.32"></audio>' if MUSIC else "")
    data = {
        "clips": clips, "dur": DUR, "seg": SEG, "zoom": face_zoom_sets(), "hand": hand_words(),
        "caps": json.loads(caps_js), "village": VILLAGE, "tilt": TILT, "variant": VARIANT,
    }
    tpl = open(os.path.join(ROOT, "scripts/template.html")).read()
    out = (tpl.replace("<!--CLIPS-->", "\n".join(vids)).replace("<!--CAPS-->", caps).replace("<!--SFX-->", sfx)
           .replace("<!--MUSIC-->", music).replace("/*DATA*/", json.dumps(data)).replace("__DUR__", str(DUR)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html —", len(clips), "plans,", len(CAPS), "sous-titres, durée", DUR, "s, variante", VARIANT)


if __name__ == "__main__":
    build()
