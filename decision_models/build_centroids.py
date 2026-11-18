"""Embed Alien atoms with BGE-large (same model as Alien's clustering) and build per-cluster centroids.

Centroid = normalized mean of (canonical cluster name + up to N member atoms).
"""
import json, random, sys
import numpy as np
from sentence_transformers import SentenceTransformer

clusters_path, out_path = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 30
d = json.load(open(clusters_path))
members = {}
for a in d["atom_assignments"]:
    if a["cluster"] >= 0:
        members.setdefault(a["cluster"], []).append(a["text"])
random.seed(0)
ids = sorted(int(k) for k in d["clusters"])
texts, owner = [], []
for c in ids:
    pool = members.get(c, [])
    for t in [d["clusters"][str(c)]["name"]] + random.sample(pool, min(N, len(pool))):
        texts.append(t); owner.append(c)
model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
E = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
owner = np.array(owner)
C = np.stack([E[owner == c].mean(0) for c in ids]); C /= np.linalg.norm(C, axis=1, keepdims=True)
np.savez_compressed(out_path, ids=np.array(ids), centroids=C)
print("saved", C.shape)
