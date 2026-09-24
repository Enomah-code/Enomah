"""Prépare les rushs iPhone (HEVC HLG 10 bits) pour la composition.

- supprime les silences de début/fin et resserre les pauses (> 0.25 s) → rythme UGC ;
- convertit HDR (HLG) → SDR BT.709, H.264 1080x1920 30 fps, GOP court (seek rapide) ;
- nettoie et normalise la voix (-14 LUFS) ;
- recale les timestamps mot à mot (Whisper) sur la nouvelle timeline → words.json.

Usage : python3 scripts/prep_aroll.py <transcripts.json> <dossier rushs>
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "aroll")

# ordre du script → rush source
CLIPS = [
    ("c01", "IMG_9860"),  # S1 hook
    ("c02", "IMG_9861"),  # S2 lecture WhatsApp
    ("c03", "IMG_9865"),  # S2 contexte + suspense
    ("c04", "IMG_9867"),  # S3 révélation 1
    ("c05", "IMG_9868"),  # S4 révélation 2 + 100 %
    ("c06", "IMG_9870"),  # S5 transition + semaine 1
    ("c07", "IMG_9877", 1.8, 16.7),    # S6 semaine 2 (un seul rush pour S6-S8)
    ("c08", "IMG_9877", 16.75, 24.35), # S7 semaine 3
    ("c09", "IMG_9877", 24.4, 35.1),   # S8 semaines 4 et 5
    ("c10", "IMG_9878"),  # S9 transition forte
    ("c11", "IMG_9880"),  # S10 différenciateur + S11 facilité
    ("c12", "IMG_9882"),  # S12 certification
    ("c13", "IMG_9887"),  # S13 prix + prolongation
    ("c14", "IMG_9889"),  # S13 fin + S14 CTA
]
PAD_IN, PAD_OUT, MIN_SIL = 0.06, 0.10, 0.25
HDR2SDR = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def silences(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                          f"silencedetect=n=-35dB:d={MIN_SIL}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).group(3)) + \
        60 * float(re.search(r"Duration: (\d+):(\d+):", err).group(2))
    if len(ends) < len(starts):
        ends.append(dur)
    return list(zip(starts, ends)), dur


def keep_segments(sil, dur):
    segs, cur = [], 0.0
    for s, e in sil:
        if s > cur:
            segs.append([max(0.0, cur - (PAD_IN if cur > 0 else 0)), min(dur, s + PAD_OUT)])
        cur = e
    if cur < dur:
        segs.append([max(0.0, cur - PAD_IN), dur])
    # fusionne les chevauchements
    out = []
    for a, b in segs:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(round(a, 3), round(b, 3)) for a, b in out if b - a > 0.12]


def remap(t, segs):
    off = 0.0
    for a, b in segs:
        if t < a:
            return off
        if t <= b:
            return off + (t - a)
        off += b - a
    return off


def main(tr_path, src_dir):
    tr = json.load(open(tr_path))
    words_out = {}
    for cid, stem, *rng in CLIPS:
        dst = os.path.join(OUT, f"{cid}.mp4")
        if os.path.exists(dst) and "--force" not in sys.argv:
            continue
        src = next((os.path.join(src_dir, f) for f in os.listdir(src_dir) if stem in f), None)
        if not src:
            print(f"-- {cid}: rush {stem} absent, ignoré")
            continue
        sil, dur = silences(src)
        segs = keep_segments(sil, dur)
        if rng:
            t0, t1 = rng
            segs = [(round(max(a, t0), 3), round(min(b, t1), 3)) for a, b in segs if b > t0 and a < t1]
            segs = [(a, b) for a, b in segs if b - a > 0.12]
        n = len(segs)
        fc = []
        for i, (a, b) in enumerate(segs):
            fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
            fo = max(0.0, (b - a) - 0.012)
            fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={fo:.3f}:d=0.012[a{i}]")
        fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
        fc.append(f"[vc]{HDR2SDR},scale=1080:1920:flags=lanczos,fps=30,eq=saturation=1.08:contrast=1.03[vo]")
        fc.append("[ac]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                  "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[ao]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", ";".join(fc),
                        "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                        "-g", "15", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                        "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-ac", "2",
                        "-movflags", "+faststart", dst], check=True)
        new_dur = sum(b - a for a, b in segs)
        key = next((k for k in tr if stem in k), None)
        words = [{"w": w["w"].strip(), "s": round(remap(w["s"], segs), 3), "e": round(remap(w["e"], segs), 3)}
                 for w in (tr[key]["words"] if key else []) if not rng or rng[0] <= w["s"] < rng[1]]
        cuts = []
        acc = 0.0
        for a, b in segs[:-1]:
            acc += b - a
            cuts.append(round(acc, 3))
        words_out[cid] = {"src": os.path.basename(src), "duration": round(new_dur, 3), "cuts": cuts, "words": words}
        print(f"{cid} {stem}: {dur:.2f}s → {new_dur:.2f}s  ({n} segments)")
    path = os.path.join(OUT, "words.json")
    merged = json.load(open(path)) if os.path.exists(path) else {}
    merged.update(words_out)
    json.dump(merged, open(path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
