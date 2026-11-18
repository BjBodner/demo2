"""Map System One corpus atoms onto the Alien catalogue and derive the anchor set.

Embeddings: BGE-large-en-v1.5 (the model Alien used for clustering) on each Alien
atom's canonical text (the cluster `name`, which Alien's reconstruction also uses).
(Member-atom centroids were tried first and discarded: they did not separate
clusters - mean self-similarity 0.81 vs 0.80 off-diagonal.)

Similarity is hubness-corrected (CSLS-style): sim'(x, c) = 2 cos(x, c) - r_c, with
r_c the mean cosine of atom c to its 10 nearest catalogue neighbours, so generic
"hub" atoms do not attract every query.

Each corpus atom votes for its top-3 Alien atoms (weights 1, .6, .3 x sim').
Anchors = the Alien atoms with the most vote mass.
"""
import json, sys
import numpy as np
from sentence_transformers import SentenceTransformer

corpus_json, clusters_json, out_json = sys.argv[1:4]
n_anchors = int(sys.argv[4]) if len(sys.argv) > 4 else 24
c = json.load(open(corpus_json))
cl = json.load(open(clusters_json))["clusters"]
ids = sorted(int(k) for k in cl)
model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
N = model.encode([cl[str(i)]["name"] for i in ids], normalize_embeddings=True, batch_size=16)
A = model.encode([a["text"] for a in c["atoms"]], normalize_embeddings=True, batch_size=16)
G = model.encode([g["text"] for g in c["gaps"]], normalize_embeddings=True, batch_size=16)
NN = N @ N.T; np.fill_diagonal(NN, -1)
r = np.sort(NN, axis=1)[:, -10:].mean(1)
S = 2 * (A @ N.T) - r[None, :]
votes = np.zeros(len(ids)); per_atom = []
for i, row in enumerate(S):
    top = np.argsort(-row)[:3]
    for w, j in zip((1.0, 0.6, 0.3), top):
        votes[j] += w * max(row[j], 0)
    per_atom.append({"text": c["atoms"][i]["text"][:200], "source_file": c["atoms"][i]["source_file"],
                     "nearest": [[ids[j], round(float(row[j]), 3)] for j in top]})
order = np.argsort(-votes)
anchors = {ids[j]: cl[str(ids[j])]["name"][:140] for j in order[:n_anchors]}
np.savez_compressed(out_json.replace(".json", "_emb.npz"), ids=np.array(ids), names=N,
                    corpus_atoms=A, gaps=G, hub_r=r)
json.dump({"method": __doc__, "anchors": anchors,
           "vote_mass": {ids[j]: round(float(votes[j]), 3) for j in order[:40]},
           "corpus_atoms": per_atom,
           "least_covered_corpus_atoms": sorted(per_atom, key=lambda p: p["nearest"][0][1])[:15]},
          open(out_json, "w"), indent=1)
for j in order[:40]:
    print(f"{ids[j]:>3} {votes[j]:5.2f} {'A' if ids[j] in anchors else ' '} {cl[str(ids[j])]['name'][:105]}")
print("\nLeast covered corpus atoms (new relative to the 16k-paper catalogue):")
for p in sorted(per_atom, key=lambda p: p["nearest"][0][1])[:12]:
    print(f"  {p['nearest'][0][1]:.3f} {p['text'][:115]}")
