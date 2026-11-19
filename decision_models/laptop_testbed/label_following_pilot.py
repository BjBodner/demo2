"""Pilot for option 10 (B): do small decision readouts follow the option NAME or its DEFINITION?

Each option is shown as  "<letter>. [<name>] <definition>". The definition is the true intent
text (BANKING77 intent name with spaces); the bracketed name is a short label. The readout is
the letter-logit distribution (Inner-Jev recipe, Qwen3-0.6B). Conditions per item:

  honest     name = the option's own intent name (name and definition agree)
  neutral    name = option_1 ... option_K
  nonsense   name = a random nonsense word (blicket, dax, ...)
  swap       names of the gold option and one random distractor are exchanged;
             definitions stay put. A model that reads definitions keeps the gold letter;
             a model that follows names moves to the distractor carrying the gold name.

Metrics: accuracy per condition; swap-follow rate = share of items (correct under honest)
whose answer moves to the option wearing the gold NAME under swap.

  python label_following_pilot.py --n 150 --k 8 --out label_pilot_qwen3_0.6b.json
"""
import argparse, json, random, time
import numpy as np, torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

LET = "ABCDEFGHIJKLMNOP"
NONSENSE = ["blicket", "dax", "wug", "toma", "fep", "zorp", "glim", "mipa", "kiki", "bouba", "tufa", "lorp"]


def prompt(text, opts):
    lines = "\n".join(f"{LET[i]}. [{n}] {d}" for i, (n, d) in enumerate(opts))
    return (f"Customer message: {text}\n\nEach option has a short name in brackets and a description. "
            f"Choose the option whose DESCRIPTION matches the message.\n{lines}\nAnswer with the letter only.")


@torch.no_grad()
def probs(model, tok, p, k):
    txt = tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False,
                                  add_generation_prompt=True, enable_thinking=False) + "Answer: "
    logits = model(**tok(txt, return_tensors="pt")).logits[0, -1]
    ids = [tok.encode(LET[i], add_special_tokens=False)[0] for i in range(k)]
    return torch.softmax(logits[ids].float(), -1).numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--n", type=int, default=150); ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--out", default="label_pilot.json")
    a = ap.parse_args()
    ds = load_dataset("PolyAI/banking77", split="test"); names = ds.features["label"].names
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float32).eval()
    rng = random.Random(0); items = rng.sample(range(len(ds)), a.n)
    acc = {c: [] for c in ["honest", "neutral", "nonsense", "swap"]}; follow, conf = [], {c: [] for c in acc}
    t0 = time.time()
    for j, i in enumerate(items):
        ex = ds[i]; r = random.Random(j); gold = names[ex["label"]]
        opt_names = r.sample([n for n in names if n != gold], a.k - 1) + [gold]; r.shuffle(opt_names)
        g = opt_names.index(gold); defs = [n.replace("_", " ") for n in opt_names]
        d = r.choice([x for x in range(a.k) if x != g])
        nons = r.sample(NONSENSE, a.k)
        swapped = list(opt_names); swapped[g], swapped[d] = swapped[d], swapped[g]
        conds = {"honest": list(zip(opt_names, defs)),
                 "neutral": [(f"option_{x+1}", defs[x]) for x in range(a.k)],
                 "nonsense": list(zip(nons, defs)),
                 "swap": list(zip(swapped, defs))}
        preds = {}
        for c, opts in conds.items():
            p = probs(model, tok, prompt(ex["text"], opts), a.k)
            preds[c] = int(p.argmax()); acc[c].append(preds[c] == g); conf[c].append(float(p.max()))
        if preds["honest"] == g:
            follow.append(preds["swap"] == d)
    res = {"model": a.model, "n": a.n, "k": a.k, "seconds": round(time.time() - t0, 1),
           "accuracy": {c: float(np.mean(v)) for c, v in acc.items()},
           "mean_confidence": {c: float(np.mean(v)) for c, v in conf.items()},
           "swap_follow_rate": float(np.mean(follow)), "swap_follow_n": len(follow),
           "chance_follow_rate": 1 / (a.k - 1)}
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
