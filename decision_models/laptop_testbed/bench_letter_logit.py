"""Laptop-scale System One testbed: letter-logit decision readout (the 'Inner-Jev' recipe,
arXiv 2610.17205) on a small open LM, on BANKING77 intent Choice questions.

Measures what a laptop can do: accuracy, ECE, Brier, order-flip rate, ms/decision,
and the time of one LoRA training step. This is the shared harness that most of the
round-2 proposals build on.

  python bench_letter_logit.py --model Qwen/Qwen3-0.6B --n 200 --k 8
"""
import argparse, json, random, time
import numpy as np, torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

LET = "ABCDEFGHIJKLMNOP"

def build(ex, names, k, rng, order=None):
    gold = names[ex["label"]]
    opts = rng.sample([n for n in names if n != gold], k - 1) + [gold]
    rng.shuffle(opts)
    if order is not None:
        opts = [opts[i] for i in order]
    lines = "\n".join(f"{LET[i]}. {o.replace('_', ' ')}" for i, o in enumerate(opts))
    prompt = (f"Customer message: {ex['text']}\n\nWhich intent does the message express?\n{lines}\n"
              f"Answer with the letter only.")
    return prompt, opts.index(gold), opts

@torch.no_grad()
def probs(model, tok, prompt, k):
    msgs = [{"role": "user", "content": prompt}]
    txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False) + "Answer: "
    ids = tok(txt, return_tensors="pt")
    logits = model(**ids).logits[0, -1]
    letter_ids = [tok.encode(LET[i], add_special_tokens=False)[0] for i in range(k)]
    return torch.softmax(logits[letter_ids].float(), -1).numpy()

def ece(conf, correct, bins=10):
    e, edges = 0.0, np.linspace(0, 1, bins + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            e += m.mean() * abs(conf[m].mean() - correct[m].mean())
    return e

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--n", type=int, default=200); ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--out", default="bench_result.json")
    a = ap.parse_args()
    torch.set_num_threads(torch.get_num_threads())
    ds = load_dataset("PolyAI/banking77", split="test")
    names = ds.features["label"].names
    rng = random.Random(0)
    items = rng.sample(range(len(ds)), a.n)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).eval()
    P, G, F, t = [], [], [], []
    for j, i in enumerate(items):
        ex = ds[i]
        r1 = random.Random(j)
        prompt, gold, opts = build(ex, names, a.k, r1)
        t0 = time.perf_counter(); p = probs(model, tok, prompt, a.k); t.append(time.perf_counter() - t0)
        # order flip: reverse the option list, map back
        rev = list(range(a.k))[::-1]
        prompt2, gold2, opts2 = build(ex, names, a.k, random.Random(j), order=rev)
        p2 = probs(model, tok, prompt2, a.k)
        F.append(opts[int(p.argmax())] != opts2[int(p2.argmax())])
        P.append(p); G.append(gold)
    P, G = np.array(P), np.array(G)
    conf, pred = P.max(1), P.argmax(1); correct = (pred == G).astype(float)
    onehot = np.eye(a.k)[G]
    # one LoRA step timing
    from peft import LoraConfig, get_peft_model
    m2 = get_peft_model(AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32),
                        LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM"))
    opt = torch.optim.AdamW([p for p in m2.parameters() if p.requires_grad], lr=1e-4)
    batch = tok([build(ds[i], names, a.k, random.Random(i))[0] for i in items[:8]], return_tensors="pt", padding=True)
    t0 = time.perf_counter()
    for _ in range(2):
        loss = m2(**batch, labels=batch["input_ids"]).loss; loss.backward(); opt.step(); opt.zero_grad()
    lora_step = (time.perf_counter() - t0) / 2
    res = {"model": a.model, "n": a.n, "k": a.k, "threads": torch.get_num_threads(),
           "accuracy": float(correct.mean()), "ece": float(ece(conf, correct)),
           "brier": float(((P - onehot) ** 2).sum(1).mean()), "mean_conf": float(conf.mean()),
           "order_flip_rate": float(np.mean(F)), "ms_per_decision_p50": float(np.median(t) * 1000),
           "lora_step_s_batch8": lora_step}
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main()
