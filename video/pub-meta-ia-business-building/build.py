import json, re
T = json.load(open("vo/timing.json"))
CUTS = [0, 3.1, 7.1, 9.55, 13.05, 15.9, 19.1, 22.35, 26.4, 34.3, 40.1, 44.4]
s = open("src/template.html.tpl").read()
n = len(CUTS) - 1
for i in range(n):
    st = CUTS[i] - (0.12 if i else 0)
    en = CUTS[-1] if i == n - 1 else CUTS[i + 1] + 0.5
    s = s.replace(f'"@S{i}"', f'"{max(0, round(st, 3)):g}"').replace(f'"@D{i}"', f'"{round(en - max(0, st), 3):g}"')
s = s.replace('"@DUR"', f'"{CUTS[-1]:g}"')
s = s.replace("/*TIMING*/", json.dumps(T, ensure_ascii=False)).replace("/*CUTS*/", json.dumps(CUTS))
assert not re.findall(r'@[SD]\d+|@DUR', s)
open("index.html", "w").write(s); print("built")
