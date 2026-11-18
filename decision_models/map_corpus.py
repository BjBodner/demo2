"""Map System One corpus atoms onto the Alien catalogue and derive the anchor set.

Each corpus atom votes (similarity-weighted) for its top-3 nearest Alien atoms
(BGE-large cosine to cluster centroids). Anchors = Alien atoms with the highest
vote mass. Also reports corpus atoms that are far from every Alien atom: concepts
the 16k-paper catalogue had no cluster for.
"""
import json, sys
import numpy as np
from sentence_transformers import SentenceTransformer

corpus_json, centroids_npz, clusters_json, out_json = sys.argv[1:5]
n_anchors = int(sys.argv[5]) if len(sys.argv) > 5 else 24
c = json.load(open(corpus_json)); z = np.load(centroids_npz)
ids, C = z["ids"], z["centroids"]
names = json.load(open(clusters_json))["clusters"]
model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
A = model.encode([a["text"] for a in c["atoms"]], normalize_embeddings=True, batch_size=32)
G = model.encode([g["text"] for g in c["gaps"]], normalize_embeddings=True, batch_size=32)
S = A @ C.T
votes = np.zeros(len(ids))
per_atom = []
for i, row in enumerate(S):
    top = np.argsort(-row)[:3]
    for rank, j in enumerate(top):
        votes[j] += row[j] * (1.0, 0.6, 0.3)[rank]
    per_atom.append({"text": c["atoms"][i]["text"][:160], "source_file": c["atoms"][i]["source_file"],
                     "nearest": [[int(ids[j]), round(float(row[j]), 3)] for j in top]})
order = np.argsort(-votes)
anchors = {int(ids[j]): names[str(int(ids[j]))]["name"][:120] for j in order[:n_anchors]}
far = sorted(per_atom, key=lambda p: p["nearest"][0][1])[:15]
np.savez_compressed(out_json.replace(".json", "_emb.npz"), corpus_atoms=A, gaps=G)
json.dump({"anchors": anchors,
           "vote_mass": {int(ids[j]): round(float(votes[j]), 3) for j in order[:40]},
           "corpus_atoms": per_atom,
           "least_covered_corpus_atoms": far}, open(out_json, "w"), indent=1)
for j in order[:40]:
    print(f"{int(ids[j]):>3} {votes[j]:5.2f} {'A' if int(ids[j]) in anchors else ' '} {names[str(int(ids[j]))]['name'][:110]}")
print("\nLeast covered corpus atoms:")
for p in far[:10]:
    print(f"  {p['nearest'][0][1]:.3f} {p['text'][:120]}")
