import json, re
T = json.load(open("vo/timing.json"))
CUTS = [0, 7.0, 14.9, 23.7, 31.9, 37.9, 40.9, 45.4, 56.4, 60.1, 66.5, 71.7, 76.5, 88.6, 99.3, 108]
s = open("src/template.html.tpl").read()
for i in range(15):
    st = 0 if i == 0 else CUTS[i] - 0.5
    en = 108 if i == 14 else CUTS[i + 1] + 0.3
    s = s.replace(f'"@S{i}"', f'"{st:g}"').replace(f'"@D{i}"', f'"{round(en - st, 3):g}"')
s = s.replace("/*TIMING*/", json.dumps([{k: l[k] for k in ("id", "start", "end", "text", "words")} for l in T], ensure_ascii=False))
s = s.replace("/*CUTS*/", json.dumps(CUTS))
assert "@S" not in s and "@D" not in s
open("index.html", "w").write(s); print("built")
