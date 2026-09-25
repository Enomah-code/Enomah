"""Download the Google Fonts used by the portfolio (latin subset, woff2) and emit fonts.css per family."""
import re, urllib.request, pathlib
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
FAMILIES = {
    "Montserrat": "wght@400;800",
    "Space Grotesk": "wght@700",
    "JetBrains Mono": "wght@500",
    "Cormorant Garamond": "ital,wght@1,500",
    "Inter": "wght@300;500;600",
    "Archivo Black": "",
    "Sora": "wght@600;800",
    "Manrope": "wght@500;800",
    "Fraunces": "ital,wght@1,400",
    "DM Sans": "wght@500",
}
root = pathlib.Path(__file__).parent / "fonts"
for fam, axes in FAMILIES.items():
    q = fam.replace(" ", "+") + (":" + axes if axes else "")
    req = urllib.request.Request(f"https://fonts.googleapis.com/css2?family={q}&display=block", headers={"User-Agent": UA})
    css = urllib.request.urlopen(req).read().decode()
    slug = fam.lower().replace(" ", "-")
    out = []
    for block in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S):
        subset, face = block
        if subset != "latin":
            continue
        url = re.search(r"url\((https://[^)]+\.woff2)\)", face).group(1)
        style = re.search(r"font-style: (\w+)", face).group(1)
        weight = re.search(r"font-weight: (\d+)", face).group(1)
        name = f"{slug}-{weight}{'i' if style == 'italic' else ''}.woff2"
        (root / name).write_bytes(urllib.request.urlopen(url).read())
        out.append(f"@font-face {{ font-family: '{fam}'; font-style: {style}; font-weight: {weight}; font-display: block; src: url('FONTDIR/{name}') format('woff2'); }}")
        print(name)
    (root / f"{slug}.css").write_text("\n".join(out) + "\n")
