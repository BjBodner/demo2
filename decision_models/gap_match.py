"""Attach System One relevance to ranked triplets.

For each kept triplet: triplet vector = normalized mean of its 3 atom embeddings.
  gap_fit   = max cosine to an open-problem statement from the corpus (what it could solve)
  corpus_nn = max cosine to an existing corpus atom (high = already proposed in the literature)
"""
import json, sys
import numpy as np
res_p, emb_p, corpus_p, out_p = sys.argv[1:5]
res = json.load(open(res_p)); e = np.load(emb_p); corpus = json.load(open(corpus_p))
pos = {int(c): i for i, c in enumerate(e["ids"])}
N, G, A = e["names"], e["gaps"], e["corpus_atoms"]
rows = []
for rk, lst in res["rankings"].items():
    if rk.startswith("reference"):
        continue
    for rank, x in enumerate(lst[:150], 1):
        v = N[[pos[c] for c in x["cluster_ids"]]].mean(0); v /= np.linalg.norm(v)
        g, a = G @ v, A @ v
        rows.append({**x, "ranking": rk, "rank": rank,
                     "gap_fit": float(g.max()), "best_gap": corpus["gaps"][int(g.argmax())]["text"][:220],
                     "corpus_nn": float(a.max()), "nearest_corpus_atom": corpus["atoms"][int(a.argmax())]["text"][:160]})
# dedupe across rankings, keep best rank
best = {}
for r in rows:
    k = tuple(r["cluster_ids"])
    if k not in best or r["fusion"] > best[k]["fusion"]:
        best[k] = r
rows = sorted(best.values(), key=lambda r: -r["gap_fit"])
json.dump(rows, open(out_p, "w"), indent=1)
print(len(rows), "unique candidates")
