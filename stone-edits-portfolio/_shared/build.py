"""Sync the shared kit into one project.

usage: python3 _shared/build.py <project-dir>

- compositions/se-endcard.html  <- brand/endcard.template.html + logo paths
- assets/fonts/*                <- fonts/*.woff2
- assets/sfx/*                  <- sfx/*.mp3
- assets/brand/*                <- brand logo files
- assets/vendor/gsap.min.js     <- GSAP, bundled locally (no render-time network)
- assets/shared/polish.js       <- grain / vignette / beat grid / safe zones helpers
"""
import pathlib, re, shutil, sys

SHARED = pathlib.Path(__file__).resolve().parent


def logo_parts():
    svg = (SHARED / "brand" / "stone-edits-logo-blanc.svg").read_text()
    parts = {}
    for pid in ("se-s", "se-e", "se-blade"):
        m = re.search(r'<path id="%s"[^>]*transform="([^"]+)"[^>]*d="([^"]+)"' % pid, svg)
        parts[pid] = " ".join(m.group(2).split())
        parts["tr"] = m.group(1)
    return parts


def main(project):
    project = pathlib.Path(project).resolve()
    p = logo_parts()
    tpl = (SHARED / "brand" / "endcard.template.html").read_text()
    html = (tpl.replace("{{TR}}", p["tr"]).replace("{{S}}", p["se-s"])
               .replace("{{E}}", p["se-e"]).replace("{{BLADE}}", p["se-blade"]))
    idx = (project / "index.html").read_text()
    w = re.search(r'id="root"[^>]*data-width="(\d+)"', idx).group(1)
    h = re.search(r'id="root"[^>]*data-height="(\d+)"', idx).group(1)
    html = html.replace("{{W}}", w).replace("{{H}}", h)
    (project / "compositions").mkdir(parents=True, exist_ok=True)
    (project / "compositions" / "se-endcard.html").write_text(html)
    for sub, pattern in (("fonts", "*.woff2"), ("sfx", "*.mp3"), ("brand", "stone-edits-logo-*"), ("vendor", "*.js")):
        dst = project / "assets" / sub
        dst.mkdir(parents=True, exist_ok=True)
        src_dir = SHARED / sub
        for f in src_dir.glob(pattern):
            shutil.copy2(f, dst / f.name)
    (project / "assets" / "shared").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SHARED / "polish.js", project / "assets" / "shared" / "polish.js")
    print("synced", project.name)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        main(arg)
