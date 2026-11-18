"""Pilot for option 3 (N1): hub options in embedding-scored decision models.

Decision rule (Jeva-style "encode options independently"): embed the state and each option
independently, pick the option with the highest similarity. Dataset: CLINC150 ("plus"),
150 intents, 30 test queries per intent, plus 1,000 out-of-scope (OOS) test queries.
Option text = the intent name. Unlabelled query pool for corrections = CLINC train utterances
(stands in for "past traffic"; their labels are never used).

Hubness metrics (prediction side):
  N1[o]     = how many test queries pick option o; the true count is exactly 30 for every o
  skew      = skewness of N1 (0 = no hubs)
  top10     = share of all predictions taken by the 10 most-picked options (uniform = 6.7%)
  err_top10 = share of *errors* that land on those 10 options
  oos_top10 = share of OOS queries absorbed by the 10 most-picked options
  oos_auroc = in-scope vs OOS separability of the max score (higher = better)

Corrections (all training-free, all use only unlabelled queries):
  raw       cosine
  center    subtract mean option / mean pool-query embedding, renormalise
  prior     subtract each option's mean similarity to the pool (a PMI-like option prior)
  csls      2cos - r_o - r_q, r = mean sim to 10 nearest neighbours on the other side
  invsoft   inverted softmax / querybank normalisation over the pool (beta=20)

  python hub_options_pilot.py --model BAAI/bge-small-en-v1.5 --out hub_pilot_small.json
"""
import argparse, json
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

QP = "Represent this sentence for searching relevant passages: "


def skew(x):
    x = np.asarray(x, float); s = x.std()
    return float(((x - x.mean()) ** 3).mean() / s ** 3) if s > 0 else 0.0


def auroc(pos, neg):
    s = np.concatenate([pos, neg]); y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    r = s.argsort().argsort() + 1
    return float((r[y == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def scorers(Q, O, P, k=10, beta=20.0):
    """Return {name: fn(Qx) -> scores [n, K]} for queries Qx against options O."""
    mo, mp = O.mean(0), P.mean(0)
    Oc = O - mo; Oc /= np.linalg.norm(Oc, axis=1, keepdims=True)
    po = (P @ O.T)                                    # pool x options
    prior = po.mean(0)
    r_o = np.sort(po, axis=0)[-k:].mean(0)            # option's mean sim to its k nearest pool queries
    Z = np.exp(beta * (po - po.max(0))).sum(0)        # column normaliser (stable)
    shift = po.max(0)

    def center(Qx):
        Qc = Qx - mp; Qc /= np.linalg.norm(Qc, axis=1, keepdims=True); return Qc @ Oc.T

    def csls(Qx):
        s = Qx @ O.T; r_q = np.sort(s, axis=1)[:, -k:].mean(1, keepdims=True)
        return 2 * s - r_o[None] - r_q

    def invsoft(Qx):
        s = Qx @ O.T; return np.exp(beta * (s - shift[None])) / Z[None]

    return {"raw": lambda Qx: Qx @ O.T, "center": center,
            "prior": lambda Qx: Qx @ O.T - prior[None], "csls": csls, "invsoft": invsoft}


def evaluate(S_in, y, S_oos):
    K = S_in.shape[1]; pred = S_in.argmax(1); n1 = np.bincount(pred, minlength=K)
    hubs = np.argsort(-n1)[:10]; err = pred != y
    return {"accuracy": float((~err).mean()), "skew_N1": skew(n1), "max_N1": int(n1.max()),
            "top10_share": float(n1[hubs].sum() / len(pred)),
            "err_top10_share": float(np.isin(pred[err], hubs).mean()) if err.any() else 0.0,
            "oos_top10_share": float(np.isin(S_oos.argmax(1), hubs).mean()),
            "oos_auroc": auroc(S_in.max(1), S_oos.max(1)),
            "hub_options": [int(h) for h in hubs[:5]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-small-en-v1.5")
    ap.add_argument("--pool", type=int, default=5000)
    ap.add_argument("--subsets", type=int, default=30)
    ap.add_argument("--out", default="hub_pilot.json")
    a = ap.parse_args()
    test = load_dataset("clinc/clinc_oos", "plus", split="test")
    train = load_dataset("clinc/clinc_oos", "plus", split="train")
    names = test.features["intent"].names
    oos_id = names.index("oos")
    in_ids = [i for i in range(len(names)) if i != oos_id]
    remap = {c: j for j, c in enumerate(in_ids)}
    X_in = [t for t, c in zip(test["text"], test["intent"]) if c != oos_id]
    y = np.array([remap[c] for c in test["intent"] if c != oos_id])
    X_oos = [t for t, c in zip(test["text"], test["intent"]) if c == oos_id]
    rng = np.random.default_rng(0)
    pool_txt = [train["text"][i] for i in rng.choice(len(train), a.pool, replace=False)]
    m = SentenceTransformer(a.model, device="cpu")
    enc = lambda xs, p="": m.encode([p + x for x in xs], normalize_embeddings=True, batch_size=64)
    O = enc([names[c].replace("_", " ") for c in in_ids])
    Q_in, Q_oos, P = enc(X_in, QP), enc(X_oos, QP), enc(pool_txt, QP)

    res = {"model": a.model, "n_options": len(in_ids), "n_test": len(y), "n_oos": len(X_oos),
           "pool": a.pool, "full_K": {}, "by_K": {}}
    for name, f in scorers(Q_in, O, P).items():
        r = evaluate(f(Q_in), y, f(Q_oos)); r["hub_names"] = [names[in_ids[h]] for h in r.pop("hub_options")]
        res["full_K"][name] = r
    # scaling with the number of options K: random option subsets, queries of those classes
    for K in [8, 32, 75, 150]:
        acc = {n: [] for n in ["raw", "center", "prior", "csls", "invsoft"]}; sk = {n: [] for n in acc}
        for s in range(a.subsets if K < 150 else 1):
            opts = np.sort(rng.choice(len(in_ids), K, replace=False)) if K < 150 else np.arange(150)
            msk = np.isin(y, opts); yy = np.searchsorted(opts, y[msk])
            for name, f in scorers(Q_in, O[opts], P).items():
                S = f(Q_in[msk]); pred = S.argmax(1)
                acc[name].append((pred == yy).mean()); sk[name].append(skew(np.bincount(pred, minlength=K)))
        res["by_K"][K] = {n: {"accuracy": float(np.mean(acc[n])), "skew_N1": float(np.mean(sk[n]))} for n in acc}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["full_K"], indent=1)); print(json.dumps(res["by_K"], indent=1))


if __name__ == "__main__":
    main()
