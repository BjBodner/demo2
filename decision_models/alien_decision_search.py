#!/usr/bin/env python3
"""Exhaustive Alien-style search for research directions anchored on decision models.

Uses the released Alien models (https://github.com/alejandrohdez00/alien-space-of-science):
  * coherence  = -mean NLL of a 3-atom set under the atom-level causal LM,
                 averaged over all 3! orderings (same definition as the repo);
  * unavailability = -(median of the top-10 author cosine similarities)
                 under the author/atom two-tower model.

Speed trick: for k=3 the coherence LM only ever sees prefixes of length <= 3
(BOS, a, b), so we cache log p(. | BOS), log p(. | BOS a) and log p(. | BOS a b)
for every ordered pair (74k short forward passes) and then read the coherence of
all C(273,3) = 3.36M triplets out of a 273^3 table. That makes the *exhaustive*
pool cheap on a CPU.

Run from anywhere with the alien repo on PYTHONPATH:
  PYTHONPATH=/path/to/alien-space-of-science python alien_decision_search.py \
      --alien-root /path/to/alien-space-of-science --out results.json
"""

import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from generation.scoring import (
    load_author_embeddings,
    load_availability_model,
    load_model,
    score_sequences_batched,
)

# Atoms (cluster IDs in papers/clusters_80.json) that are about decision making:
# sequential decisions, planning/search, RL, preference & choice models, utility,
# bandits, game theory, risk control. Hand-picked from the 273-atom catalogue.
DECISION_ATOMS = {
    0: "MBR / expected-utility decoding",
    15: "Predictive routing / gating decisions",
    16: "GRPO critic-free RL",
    25: "Shapley value / cooperative game theory",
    42: "Active learning / information-theoretic acquisition",
    54: "Lagrangian constrained optimization",
    70: "MCTS / state-space search",
    71: "Multi-armed bandits for AI workflow decisions",
    94: "Inference-time scaling as search",
    95: "Tree-search reasoning",
    115: "Active retrieval as sequential decision loop",
    155: "Pairwise comparison / choice models",
    162: "Conformal prediction & risk control",
    180: "MDP / POMDP framing of agents",
    203: "Theory of mind / recursive belief tracking",
    231: "Group-relative RL over trajectories",
    232: "Trajectory-driven agent self-improvement",
    240: "Direct preference optimization",
    241: "KL-regularized policy updates",
    244: "Noisy-preference robust alignment",
    249: "LLM priors inside RL",
    251: "Process supervision with look-ahead value",
    252: "Process reward models",
    256: "Reward hacking",
    257: "Relative / variance-reduced RL objectives",
    258: "Sparse reward & temporal credit assignment",
}


def log(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


@torch.no_grad()
def build_logprob_tables(model, tm, atom_ids, batch_size=2048):
    """Return L1[a], L2[a,b], L3[a,b,c] = log p(next atom | prefix) in atom-index space."""
    n = len(atom_ids)
    tok = np.array([int(tm.raw["cluster_to_token_id"][str(c)]) for c in atom_ids])
    tok_t = torch.tensor(tok)
    bos = tm.bos_token_id

    def run(prefixes):
        out = []
        for s in range(0, len(prefixes), batch_size):
            x = prefixes[s:s + batch_size]
            logits = model(x)[:, -1, :]
            lp = F.log_softmax(logits.float(), dim=-1)[:, tok_t]
            out.append(lp)
        return torch.cat(out).numpy()

    L1 = run(torch.tensor([[bos]]))[0]
    p2 = torch.stack([torch.full((n,), bos), tok_t], dim=1)
    L2 = run(p2)
    a_idx, b_idx = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    p3 = torch.stack([
        torch.full((n * n,), bos), tok_t[a_idx.ravel()], tok_t[b_idx.ravel()]
    ], dim=1)
    t0 = time.time()
    L3 = run(p3).reshape(n, n, n)
    log(f"  L3 table: {n*n:,} prefixes in {time.time()-t0:.1f}s")
    return L1, L2, L3


def coherence_triplets(trip, L1, L2, L3):
    """Mean over 6 permutations of mean per-atom log-prob (= -mean NLL)."""
    a, b, c = trip[:, 0], trip[:, 1], trip[:, 2]
    tot = np.zeros(len(trip))
    for x, y, z in itertools.permutations((a, b, c)):
        tot += (L1[x] + L2[x, y] + L3[x, y, z]) / 3.0
    return tot / 6.0


@torch.no_grad()
def availability_triplets(model, tm, atom_ids, trip, author_emb, top_k=10, batch_size=8192):
    tok = torch.tensor([int(tm.raw["cluster_to_token_id"][str(c)]) for c in atom_ids])
    out = np.empty(len(trip))
    t0 = time.time()
    for s in range(0, len(trip), batch_size):
        ids = tok[torch.from_numpy(trip[s:s + batch_size])]
        emb = model.encode_sets(ids, torch.ones_like(ids))
        sc = emb @ author_emb.T
        tk = sc.topk(top_k, dim=1).values
        out[s:s + len(ids)] = ((tk[:, top_k // 2 - 1] + tk[:, top_k // 2]) / 2).numpy()
        if (s // batch_size) % 50 == 0:
            done = s + len(ids)
            rate = done / max(time.time() - t0, 1e-9)
            log(f"    availability {done:,}/{len(trip):,}  ETA {(len(trip)-done)/rate/60:.1f} min")
    return out


def z(x):
    return (x - x.mean()) / x.std()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alien-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--betas", type=float, nargs="+", default=[0.5, 0.7])
    ap.add_argument("--keep", type=int, default=400, help="top sets kept per (beta, bucket)")
    ap.add_argument("--max-per-atom", type=int, default=6, help="diversity cap in kept lists")
    ap.add_argument("--validate", type=int, default=200)
    args = ap.parse_args()
    torch.set_num_threads(torch.get_num_threads())

    root = args.alien_root
    coh_model, coh_tm = load_model(str(root / "models/coherence_model"))
    coh_model.eval()
    av_model, av_tm = load_availability_model(str(root / "models/availability_model"))
    av_model.eval()
    author_emb, _ = load_author_embeddings(str(root / "models/availability_model"))
    atom_ids = sorted(int(c) for c in coh_tm.raw["cluster_to_token_id"])
    n = len(atom_ids)
    pos = {c: i for i, c in enumerate(atom_ids)}
    log(f"{n} atoms, {author_emb.shape[0]:,} authors")

    log("Building coherence log-prob tables...")
    L1, L2, L3 = build_logprob_tables(coh_model, coh_tm, atom_ids)

    # Candidate pool: every triplet with >= 1 decision atom.
    D = np.array([pos[c] for c in DECISION_ATOMS])
    isD = np.zeros(n, bool); isD[D] = True
    all_trip = np.array(list(itertools.combinations(range(n), 3)), dtype=np.int64)
    nD = isD[all_trip].sum(1)
    trip = all_trip[nD >= 1]
    nD = nD[nD >= 1]
    log(f"Pool: {len(trip):,} triplets with >=1 decision atom (of {len(all_trip):,})")

    coh = coherence_triplets(trip, L1, L2, L3)

    # Validate the cached-table coherence against the repo's official scorer.
    rng = np.random.default_rng(0)
    sample = trip[rng.choice(len(trip), args.validate, replace=False)]
    seqs, idx = [], []
    for i, t in enumerate(sample):
        for p in itertools.permutations([atom_ids[j] for j in t]):
            seqs.append(coh_tm.cluster_ids_to_token_ids(list(p)))
    ref = -np.array(score_sequences_batched(coh_model, seqs, coh_tm, device="cpu")).reshape(-1, 6).mean(1)
    mine = coherence_triplets(sample, L1, L2, L3)
    log(f"  coherence check vs official scorer: max |diff| = {np.abs(ref - mine).max():.2e}")

    log("Scoring availability...")
    avail = availability_triplets(av_model, av_tm, atom_ids, trip, author_emb)
    unavail = -avail
    zc, zu = z(coh), z(unavail)
    log(f"  corr(coherence, unavailability) = {np.corrcoef(coh, unavail)[0,1]:.3f}")

    def pack(i, beta):
        t = [atom_ids[j] for j in trip[i]]
        return {
            "cluster_ids": t,
            "decision_atoms": [c for c in t if c in DECISION_ATOMS],
            "coherence": float(coh[i]), "unavailability": float(unavail[i]),
            "z_coherence": float(zc[i]), "z_unavailability": float(zu[i]),
            "fusion": float((1 - beta) * zc[i] + beta * zu[i]),
        }

    results = {"config": {"pool_size": int(len(trip)), "decision_atoms": DECISION_ATOMS,
                          "betas": args.betas, "max_per_atom": args.max_per_atom,
                          "fusion": "(1-beta)*z(coherence) + beta*z(unavailability), z over pool"},
               "rankings": {}}
    buckets = {"bridge (1 decision atom)": nD == 1, "core (2-3 decision atoms)": nD >= 2}
    for beta in args.betas:
        fus = (1 - beta) * zc + beta * zu
        for bname, mask in buckets.items():
            order = np.argsort(-np.where(mask, fus, -np.inf))
            kept, use = [], np.zeros(n, int)
            for i in order:
                if not mask[i] or len(kept) >= args.keep:
                    break
                if (use[trip[i]] >= args.max_per_atom).any():
                    continue
                use[trip[i]] += 1
                kept.append(pack(i, beta))
            results["rankings"][f"beta={beta:g} | {bname}"] = kept
    # Coherence-only reference (what a mainstream researcher would most likely combine).
    order = np.argsort(-coh)[:50]
    results["rankings"]["reference | most coherent (beta=0)"] = [pack(i, 0.0) for i in order]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=1))
    np.savez_compressed(args.out.with_suffix(".npz"), trip=np.array(atom_ids)[trip],
                        coherence=coh, unavailability=unavail)
    log(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
