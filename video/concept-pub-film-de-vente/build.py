"""Fill src/template.html.tpl with the voice timing and scene cuts -> index.html."""
import json, re
T = json.load(open("vo/timing.json"))
CUTS = [0, 7.8, 14.7, 20.0, 29.3, 49.45, 54.0, 71.55, 95.95, 101.2, 105.95, 117.95, 128.5, 137]
s = open("src/template.html.tpl").read()
n = len(CUTS) - 1
for i in range(n):
    st = 0 if i == 0 else CUTS[i] - 0.5
    en = CUTS[-1] if i == n - 1 else CUTS[i + 1] + 0.3
    s = s.replace(f'"@S{i}"', f'"{st:g}"').replace(f'"@D{i}"', f'"{round(en - st, 3):g}"')
s = s.replace("/*TIMING*/", json.dumps([{k: l[k] for k in ("id", "start", "end", "text", "words")} for l in T], ensure_ascii=False))
s = s.replace("/*CUTS*/", json.dumps(CUTS))
assert not re.findall(r'@[SD]\d+', s)
open("index.html", "w").write(s); print("built")
