"""Assemble index.html + compositions/captions.html à partir des rushs préparés.

Chaque rush (assets/aroll/cXX.mp4) est posé bout à bout ; son overlay
(compositions/ov-cXX.html) démarre en même temps que lui et utilise le temps
LOCAL du rush. Ajouter un rush manquant = le préparer (prep_aroll.py), le
transcrire, puis relancer ce script.

Usage : python3 scripts/build.py
"""
import html
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AROLL = os.path.join(ROOT, "assets", "aroll")

ORDER = ["c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09",
         "c10", "c11", "c12", "c13", "c14"]
OUTRO = 2.2

# Corrections de transcription (Whisper) → texte affiché
FIX = {
    "c03": {"celles": "celle", "proposées.": "proposée."},
    "c11": {"faturer": "facturer", "ses": "ces", "soucis": "source"},
    "c14": {"parcer": "passer"},
}
# Mots mis en valeur (or) dans les sous-titres
KEYWORDS = {
    "formations", "intelligence", "artificielle", "ceci", "preuve", "novice", "agencé",
    "professionnel", "fier", "élie", "aucune", "pourquoi", "complète", "meilleures",
    "marché", "satisfaits", "100", "100%", "positifs", "unanimité", "programme", "prompt",
    "engineering", "payer", "bref", "temps", "change", "créer", "facturer", "revenus",
    "8", "10", "minutes", "codage", "certificat", "ai", "business", "builder", "certifié",
    "monétisable", "portfolio", "dimanche", "normal", "offre", "clique", "maintenant",
    "23h59", "semaine", "automatisations", "agent", "whatsapp", "application", "site",
    "4", "999", "35", "000", "francs", "gratuit",
}
# Fenêtres (temps local du rush) où les sous-titres s'effacent devant un gros titre
HIDE = {
    "c03": [(9.45, 10.6)],
    "c05": [(5.0, 7.3)],
    "c10": [(0.0, 0.75)],
}
# Bruitages : (temps local, fichier, volume)
SFX = {
    "c01": [(0.0, "impact-bass-1", 0.55), (4.3, "whoosh-short", 0.5), (5.62, "pop", 0.6),
            (6.2, "notification", 0.7), (8.45, "impact-bass-2", 0.45), (10.8, "whoosh-cinematic", 0.55)],
    "c02": [(0.62, "pop", 0.55), (2.14, "pop", 0.5), (3.4, "pop", 0.5), (4.1, "whoosh", 0.45),
            (5.9, "sparkle", 0.45), (6.6, "pop", 0.5), (8.3, "pop", 0.5), (9.55, "chime", 0.5)],
    "c03": [(1.8, "click-soft", 0.6), (2.6, "whoosh-short", 0.45), (5.6, "error", 0.45),
            (6.3, "pop", 0.5), (7.7, "ping", 0.45), (9.95, "riser", 0.5), (9.95, "impact-bass-1", 0.6)],
    "c04": [(1.85, "pop", 0.55), (3.9, "whoosh-short", 0.45), (4.2, "impact-bass-2", 0.5),
            (5.3, "click-soft", 0.5)],
    "c05": [(0.35, "whoosh", 0.5), (0.9, "sparkle", 0.4), (4.75, "whoosh-short", 0.5),
            (6.2, "riser", 0.35), (6.2, "chime", 0.6), (6.25, "impact-bass-1", 0.45), (7.0, "pop", 0.45)],
    "c06": [(1.0, "whoosh-short", 0.45), (3.9, "pop", 0.55), (4.9, "whoosh-cinematic", 0.5),
            (6.7, "whoosh", 0.45), (8.35, "impact-bass-2", 0.4), (9.0, "typing", 0.35),
            (9.7, "pop", 0.45), (11.6, "ping", 0.45)],
    "c10": [(0.0, "impact-bass-1", 0.6), (0.9, "click", 0.4), (1.1, "click", 0.4), (1.3, "click", 0.4),
            (1.5, "click", 0.4), (1.7, "click", 0.4), (3.0, "whoosh-short", 0.45), (5.0, "glitch-1", 0.4)],
    "c11": [(0.45, "impact-bass-1", 0.5), (2.6, "pop", 0.5), (4.3, "pop", 0.55), (6.6, "ping", 0.5),
            (7.3, "whoosh", 0.5), (7.7, "key-press", 0.4), (10.1, "error", 0.3), (11.6, "sparkle", 0.45)],
    "c12": [(0.9, "whoosh-cinematic", 0.5), (1.5, "sparkle", 0.5), (5.85, "impact-bass-2", 0.55),
            (6.8, "whoosh", 0.45), (9.3, "glitch-3", 0.35), (11.5, "pop", 0.55), (12.9, "pop", 0.55)],
    "c14": [(0.2, "whoosh", 0.5), (0.8, "pop", 0.5), (3.3, "impact-bass-1", 0.55), (4.3, "whoosh-short", 0.45),
            (8.1, "whoosh", 0.45), (8.45, "click", 0.7), (9.4, "pop", 0.45), (12.42, "riser", 0.4),
            (12.45, "impact-bass-2", 0.55)],
}
# Les cues ci-dessus = instant du « coup ». Pour les sons à montée, on démarre
# avant le pic et on coupe la queue : nom → (préroll avant le pic, début dans le fichier, durée)
SHAPE = {
    "riser": (1.4, 1.6, 2.4),
    "whoosh-cinematic": (0.7, 1.8, 2.0),
    "glitch-1": (0.3, 0.5, 1.6),
}
OUTRO_SFX = [(0.3, "whoosh-cinematic", 0.5), (0.35, "chime", 0.5)]


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return round(float(out.strip()), 3)


def merge_tokens(words):
    out = []
    for w in words:
        t = w["w"].strip()
        if not t:
            continue
        if out and (t.startswith("'") or t.startswith("-")):
            out[-1]["w"] += t
            out[-1]["e"] = w["e"]
        elif out and t in {"?", "!", "%"}:
            out[-1]["w"] += ("" if t == "%" else "\u00a0") + t
            out[-1]["e"] = w["e"]
        else:
            out.append({"w": t, "s": w["s"], "e": w["e"]})
    return out


def groups_for(words, hide):
    groups, cur = [], []
    for i, w in enumerate(words):
        if any(a <= w["s"] < b for a, b in hide):
            if cur:
                groups.append(cur)
                cur = []
            continue
        cur.append(w)
        chars = sum(len(x["w"]) for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["s"] - w["e"]) if nxt else 1
        if (len(cur) >= 3 or chars >= 14 or re.search(r"[.,?!]$", w["w"]) or gap > 0.3
                or (nxt and chars + len(nxt["w"]) > 16)):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def main():
    wm = json.load(open(os.path.join(AROLL, "words_medium.json")))
    prep = json.load(open(os.path.join(AROLL, "words.json")))
    clips, t = [], 0.0
    for cid in ORDER:
        path = os.path.join(AROLL, f"{cid}.mp4")
        if not os.path.exists(path):
            continue
        dur = probe(path)
        clips.append({"id": cid, "start": round(t, 3), "dur": dur, "cuts": prep.get(cid, {}).get("cuts", [])})
        t += dur
    outro_start = round(t, 3)
    total = round(t + OUTRO, 3)

    # ---- sous-titres (temps global)
    cap_groups = []
    for c in clips:
        fix = FIX.get(c["id"], {})
        words = [{**w, "w": fix.get(w["w"], w["w"])} for w in wm.get(c["id"], [])]
        words = merge_tokens(words)
        for g in groups_for(words, HIDE.get(c["id"], [])):
            cap_groups.append([{"w": w["w"], "s": round(c["start"] + w["s"], 3),
                                "e": round(c["start"] + min(w["e"], c["dur"] - 0.02), 3)} for w in g])
    groups = []
    for i, g in enumerate(cap_groups):
        start = g[0]["s"]
        end = g[-1]["e"] + 0.25
        if i + 1 < len(cap_groups):
            end = min(end if cap_groups[i + 1][0]["s"] - g[-1]["e"] > 0.6 else cap_groups[i + 1][0]["s"],
                      cap_groups[i + 1][0]["s"])
        end = min(end, outro_start)
        words = [{"t": re.sub(r"[.,;:]+$", "", w["w"]), "s": w["s"], "e": w["e"],
                  "k": re.sub(r"[^\wàâçéèêëîïôûùüÿœ%]", "", w["w"].lower()) in KEYWORDS}
                 for w in g]
        groups.append({"s": round(start, 3), "e": round(end, 3), "w": words})
    write_captions(groups, total)

    # ---- index.html
    media, hosts, sfx = [], [], []
    for c in clips:
        cid, s, d = c["id"], c["start"], c["dur"]
        media.append(
            f'      <video id="v-{cid}" class="clip aroll" src="assets/aroll/{cid}.mp4" '
            f'data-start="{s}" data-duration="{d}" data-track-index="0" muted playsinline></video>')
        media.append(
            f'    <audio id="a-{cid}" src="assets/aroll/{cid}.mp4" data-start="{s}" '
            f'data-duration="{d}" data-track-index="{10 + len(media) // 2 % 2}" data-volume="1"></audio>')
        if os.path.exists(os.path.join(ROOT, "compositions", f"ov-{cid}.html")):
            hosts.append(
                f'    <div id="el-ov-{cid}" class="ov-host" data-composition-id="ov-{cid}" '
                f'data-composition-src="compositions/ov-{cid}.html" data-start="{s}" data-duration="{d}" '
                f'data-track-index="2" data-width="1080" data-height="1920"></div>')
        for (lt, name, vol) in SFX.get(cid, []):
            sfx.append((round(s + lt, 3), name, vol))
    for (lt, name, vol) in OUTRO_SFX:
        sfx.append((round(outro_start + lt, 3), name, vol))
    manifest = json.load(open(os.path.join(ROOT, "assets", "sfx", "manifest.json")))
    sfx_tags, lanes = [], []
    for i, (cue, name, vol) in enumerate(sorted(sfx)):
        pre, mstart, d = SHAPE.get(name, (0.0, 0.0, manifest[name]["duration"]))
        st = round(max(0.0, cue - pre), 3)
        d = round(min(d, total - st), 3)
        lane = next((j for j, end in enumerate(lanes) if end <= st), None)
        if lane is None:
            lanes.append(0.0)
            lane = len(lanes) - 1
        lanes[lane] = st + d
        sfx_tags.append(
            f'    <audio id="sfx-{i:02d}" src="assets/sfx/{name}.mp3" data-start="{st}" '
            f'data-media-start="{mstart}" data-duration="{d}" data-track-index="{20 + lane}" '
            f'data-volume="{vol}"></audio>')

    # Punch-in alterné à chaque jump cut + lente poussée caméra
    cam = []
    k = 0
    for c in clips:
        bounds = [0.0] + c["cuts"] + [c["dur"]]
        for a, b in zip(bounds, bounds[1:]):
            base = 1.0 if k % 2 == 0 else 1.13
            cam.append((round(c["start"] + a, 3), round(b - a, 3), base))
            k += 1
    cam_js = ",\n        ".join(f"[{s}, {d}, {b}]" for s, d, b in cam)

    page = INDEX.format(
        total=total, media_video="\n".join(m for m in media if "<video" in m),
        media_audio="\n".join(m for m in media if "<audio" in m), hosts="\n".join(hosts),
        sfx="\n".join(sfx_tags), outro_start=outro_start, outro=OUTRO, cam=cam_js)
    open(os.path.join(ROOT, "index.html"), "w").write(page)
    print(f"{len(clips)} rushs, durée totale {total:.2f}s, {len(groups)} groupes de sous-titres, {len(sfx_tags)} bruitages")
    for c in clips:
        print(f"  {c['id']}  {c['start']:7.2f} → {c['start'] + c['dur']:7.2f}")


def write_captions(groups, total):
    parts = []
    for gi, g in enumerate(groups):
        spans = "".join(
            f'<span class="cw{" kw" if w["k"] else ""}" id="cw-{gi}-{wi}">{html.escape(w["t"])}</span>'
            for wi, w in enumerate(g["w"]))
        parts.append(f'        <div class="cg" id="cg-{gi}">{spans}</div>')
    data = json.dumps(groups, ensure_ascii=False, separators=(",", ":"))
    out = CAPTIONS.format(total=total, groups="\n".join(parts), data=data)
    open(os.path.join(ROOT, "compositions", "captions.html"), "w").write(out)


INDEX = """<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <!-- Généré par scripts/build.py — modifier le script, pas ce fichier. -->
    <script src="assets/vendor/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/common.css" />
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #050a1d; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #050a1d; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 32%; }}
      #cam video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      #root > div[data-composition-src] {{ position: absolute; inset: 0; }}
      #el-captions {{ z-index: 50; }}
      #el-outro {{ z-index: 60; }}
      #vignette {{
        position: absolute; inset: 0; pointer-events: none;
        background: linear-gradient(180deg, rgba(5,10,29,0.35) 0%, rgba(5,10,29,0) 22%,
          rgba(5,10,29,0) 58%, rgba(5,10,29,0.55) 100%);
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}"
      data-width="1080" data-height="1920">
      <div id="cam">
{media_video}
      </div>
      <div id="vignette"></div>

{hosts}

    <div id="el-captions" data-track-kind="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
      data-start="0" data-duration="{total}" data-track-index="5" data-width="1080" data-height="1920"></div>
    <div id="el-outro" data-composition-id="outro" data-composition-src="compositions/outro.html"
      data-start="{outro_start}" data-duration="{outro}" data-track-index="3" data-width="1080" data-height="1920"></div>

{media_audio}
{sfx}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // [début global, durée, zoom de base] pour chaque plan entre deux jump cuts
      const CAM = [
        {cam}
      ];
      CAM.forEach(([s, d, base]) => {{
        tl.fromTo("#cam", {{ scale: base }}, {{ scale: base + 0.035, duration: d, ease: "none", immediateRender: false }}, s);
      }});
      tl.set("#cam", {{ scale: 1 }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

CAPTIONS = """<!doctype html>
<html>
  <body>
    <template>
      <style>
        #captions-root {{ position: absolute; inset: 0; pointer-events: none; }}
        #captions-root .cg {{
          position: absolute; left: 50px; right: 50px; top: 1300px; height: 190px;
          display: flex; flex-wrap: wrap; align-content: center; justify-content: center;
          gap: 0 26px; opacity: 0;
          font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 72px;
          line-height: 1.05; text-transform: uppercase; text-align: center; color: #ffffff;
        }}
        #captions-root .cw {{
          display: inline-block; position: relative;
          -webkit-text-stroke: 14px #050a1d; paint-order: stroke fill;
          text-shadow: 0 10px 26px rgba(5, 10, 29, 0.75);
        }}
        #captions-root .cw.kw {{ color: #f2b33d; }}
      </style>
      <div id="captions-root" data-composition-id="captions" data-width="1080" data-height="1920"
        data-duration="{total}">
{groups}
      </div>
      <script>
        (function () {{
          const GROUPS = {data};
          const tl = gsap.timeline({{ paused: true }});
          GROUPS.forEach((g, gi) => {{
            const el = document.getElementById("cg-" + gi);
            tl.fromTo(el, {{ opacity: 0, scale: 0.82, y: 26 }},
              {{ opacity: 1, scale: 1, y: 0, duration: 0.16, ease: "back.out(2.2)", immediateRender: false }}, g.s);
            g.w.forEach((w, wi) => {{
              const we = document.getElementById("cw-" + gi + "-" + wi);
              const rest = w.k ? "#f2b33d" : "#ffffff";
              tl.fromTo(we, {{ scale: 1, color: rest }},
                {{ scale: 1.08, color: w.k ? "#ffd98a" : "#f2b33d", duration: 0.08, ease: "power2.out", immediateRender: false }}, w.s);
              tl.fromTo(we, {{ scale: 1.08 }},
                {{ scale: 1, color: rest, duration: 0.12, ease: "power2.inOut", immediateRender: false }},
                Math.min(Math.max(w.e, w.s + 0.1), g.e - 0.02));
            }});
            tl.to(el, {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, Math.max(g.s + 0.2, g.e - 0.08));
            tl.set(el, {{ opacity: 0, visibility: "hidden" }}, g.e);
          }});
          window.__timelines["captions"] = tl;
        }})();
      </script>
    </template>
  </body>
</html>
"""

if __name__ == "__main__":
    main()
