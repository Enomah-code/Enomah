#!/usr/bin/env python3
"""Temps passé par agent, à partir du journal automatique .claude/logs/agents.jsonl.

Usage : python3 docs/saas-createurs/suivi/temps.py [--jour AAAA-MM-JJ]
"""
import json, sys, collections, datetime, pathlib

LOG = pathlib.Path(__file__).resolve().parents[3] / ".claude" / "logs" / "agents.jsonl"


def parse(ts):
    return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


def main():
    jour = sys.argv[sys.argv.index("--jour") + 1] if "--jour" in sys.argv else None
    if not LOG.exists():
        print("Aucun journal pour l'instant :", LOG)
        return
    debut, fin, nom = {}, {}, {}
    for ligne in LOG.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(ligne)
        except ValueError:
            continue
        if jour and not e["ts"].startswith(jour):
            continue
        aid = e.get("agent_id") or "?"
        nom[aid] = e.get("agent") or nom.get(aid, "?")
        if e.get("event") == "SubagentStart":
            debut.setdefault(aid, parse(e["ts"]))
        elif e.get("event") == "SubagentStop":
            fin[aid] = parse(e["ts"])  # garde le dernier arrêt
    total = collections.defaultdict(lambda: [0, datetime.timedelta()])
    for aid, t0 in debut.items():
        if aid in fin:
            total[nom[aid]][0] += 1
            total[nom[aid]][1] += fin[aid] - t0
    en_cours = [nom[a] for a in debut if a not in fin]
    print(f"{'Agent':32} {'Tâches':>7} {'Temps':>10}")
    for agent, (n, d) in sorted(total.items(), key=lambda x: -x[1][1]):
        m, s = divmod(int(d.total_seconds()), 60)
        h, m = divmod(m, 60)
        print(f"{agent:32} {n:>7} {h:>4}h{m:02d}m{s:02d}s")
    if en_cours:
        print("En cours :", ", ".join(en_cours))


if __name__ == "__main__":
    main()
