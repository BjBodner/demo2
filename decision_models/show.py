"""Pretty-print rankings from alien_decision_search.py with short atom labels."""
import json, sys
res = json.load(open(sys.argv[1])); clusters = json.load(open(sys.argv[2]))["clusters"]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 15
short = lambda c: clusters[str(c)]["name"][:95].replace("\n", " ")
for name, rows in res["rankings"].items():
    print(f"\n=== {name} ===")
    for r in rows[:n]:
        print(f"[{r['fusion']:+.2f} | zc {r['z_coherence']:+.2f} zu {r['z_unavailability']:+.2f}] {r['cluster_ids']}")
        for c in r["cluster_ids"]:
            print(f"     {'*' if c in r['decision_atoms'] else ' '}{c:>3}: {short(c)}")
