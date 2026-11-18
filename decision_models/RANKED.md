# System One research options, ranked for a laptop

> For each option's problem, approach, contributions and expected results, see
> [IDEAS_DETAILED.md](IDEAS_DETAILED.md).

26 options: the 11 from [README.md](README.md) plus 15 new ones, taken from deeper in
the same Alien rankings ([`results/round2_triplets.json`](results/round2_triplets.json)).

They are ranked by:
1. **Laptop feasibility** (primary).
2. **How well-defined the metric to optimise is** (secondary).
3. **Novelty**, used only to break ties. It comes from an arXiv keyword check
   ([`results/novelty_log.txt`](results/novelty_log.txt),
   [`results/novelty_log_round2.txt`](results/novelty_log_round2.txt)).

## The laptop testbed (measured)
Almost every option below runs on one shared harness:
[`laptop_testbed/bench_letter_logit.py`](laptop_testbed/bench_letter_logit.py). It is the
"Inner-Jev" recipe (arXiv 2610.17205): a small open LM answers Choice questions by
reading its option-letter logits. That gives one forward pass and a probability per
option.

Measured here on a **4-core x86 CPU with no GPU**: Qwen3-0.6B, BANKING77, 8 options,
200 items. A modern laptop should match or beat this.

| accuracy | ECE | mean confidence | order-flip rate (options reversed) | ms / decision (p50) | LoRA step (batch 8, r=16) |
|---|---|---|---|---|---|
| 78.5% | 0.138 | 0.92 | **28.5%** | 370 ms | 5.2 s |

This baseline is overconfident and very order-sensitive, which leaves large, clean
headroom for the calibration and robustness options. On this CPU, about 1,000
decisions take roughly 6 minutes, and about 1,000 LoRA steps take roughly 1.5 hours.

**Scales.**
- **Laptop:**
  - **L5:** inference only, or post-hoc on cached probabilities. Under 1 hour.
  - **L4:** small fine-tunes (≤0.6B LoRA or ModernBERT), a few hours, or a few dollars
    of API calls.
  - **L3:** several training runs or custom architecture work. Overnight.
- **Metric:**
  - **M5:** one standard scalar you can optimise directly.
  - **M4:** a scalar you have to construct, or two metrics traded off.
- **Novelty:**
  - **New:** no close arXiv match.
  - **Partial:** adjacent work exists.
  - **Taken:** largely done already.

---

## Tier 1: L5, inference only or post-hoc (start here)

| # | Option | Metric to optimise | Laptop | Metric | Novelty | Alien z (coh / unavail) |
|---|---|---|---|---|---|---|
| 1 | **G. Probability fingerprints for silent model changes** | detection power at 5% FPR vs canary size; conformal coverage error after re-calibration | L5 | M5 | New | +4.08 / +0.70 |
| 2 | **N5. Choosing which items to label for conformal calibration** | prediction-set size at 90% coverage for a label budget *n* (and the coverage gap) | L5 | M5 | New | +1.93 / +1.19 |
| 3 | **N1. "Hub" options in large option sets** | accuracy at K=150 (CLINC150, all intents); skew of how often each option is chosen | L5 | M5 | New | +1.32 / +1.61 |
| 4 | **N10. Anytime decisions by sequential evidence accumulation** | tokens read before deciding at matched accuracy, or AUC of the accuracy-vs-tokens curve | L5 | M5 | New | +1.17 / +1.61 |
| 5 | **N11. Option-definition length bias** | slope of P(option) against definition length, at fixed accuracy (target 0) | L5 | M5 | New | +1.10 / +1.76 |
| 6 | **N3. Where the evidence sits in a long state** | accuracy spread across evidence positions (max minus min; target 0) | L5 | M5 | Partial | +1.23 / +1.67 |
| 7 | **N2. Numeric and date boundary minimal pairs** | accuracy on pairs one unit either side of a threshold | L5 | M5 | Partial | +1.20 / +1.70 |
| 8 | **C. Per-layer "decision lens"** | layer at which the decision settles; share of errors that are overwritten | L5 | M4 | Partial | +1.01 / +1.90 |
| 9 | **N15. Small IRT evaluation sets for decision models** | rank correlation / MAE of predicted full-benchmark score from ≤100 items | L4–5 | M5 | Partial | +1.36 / +1.70 |

**1. G: Probability fingerprints**
- Build a canary set of about 300 states with 3 small perturbations each.
- The returned probability vector is the fingerprint. A conformal exchangeability
  test flags a changed model, then temperature scaling and the conformal thresholds
  are refit.
- *Laptop setup:* the "versions" are free to make: fp32 / bf16 / int8 Qwen3-0.6B, a
  LoRA-nudged copy, and Qwen3-1.7B. About 6k decisions, so about 40 minutes.
- Optionally add real calls to `jev-latest`.

**2. N5: Choosing items to label for conformal calibration**
- Conformal guarantees need labelled calibration data. With a budget of *n* labels,
  pick the states with a diversity criterion (DPP or submodular) or by uncertainty,
  instead of at random.
- Run it on the cached probabilities from one pass over the BANKING77 test set
  (3,080 items, about 20 minutes once). Every later experiment takes seconds.
- *Watch:* selection must not break exchangeability. Weighted conformal fixes that,
  and it's part of the contribution.

**3. N1: Hub options**
- In embedding-scored decision models (Jeva-style: options encoded independently),
  some option embeddings sit near everything and win too often. This happened in
  this very project when mapping atoms with BGE.
- Fixes to compare: CSLS-style hubness correction, centring or whitening the option
  embeddings, and a per-option prior from content-free states.
- *Setup:* BGE-small or ModernBERT embeddings on CLINC150 or ToolRet, scored against
  all options. Minutes on CPU.

**4. N10: Anytime decisions**
- Feed the state in chunks and read the decision distribution after each one.
- Stop when a sequential probability ratio test (integrate-and-fire style) crosses its
  threshold, with the threshold tuned for calibration.
- The trade-off is plain: tokens read against accuracy and ECE.
- About 8 prefixes per item, so about 500 items in 25 minutes.

**5. N11: Option-definition length bias**
- Rewrite each option definition as a short and a long paraphrase with the same
  meaning, and measure how the probability moves.
- Fix it with length-normalised scoring, or a PMI prior (K below).
- The target is a clean regression slope of zero. About 12 minutes per condition.

**6. N3: Evidence position in a long state**
- Put the decisive fact at 0% / 25% / 50% / 75% / 100% of a 1–2k-token distractor
  state, i.e. "lost in the middle" for decision models.
- *Prior art:* the presentation-sensitivity paper (2611.06384) varies *option*
  positions, not *evidence* positions.
- The fix to optimise is chunk-then-aggregate, or putting the question first.

**7. N2: Numeric and date boundary minimal pairs**
- Threshold checks ("refund > $500?", "deadline passed?") with values one unit either
  side of the threshold.
- *Prior art:* 2609.39496 (an arithmetic-dependent rejection bottleneck in Jev) and
  ThinkJev (2610.37732) cover arithmetic.
- *Still open:* boundary calibration, and typed numeric features (as in Beveridge,
  2611.18655) against letter-logit readout.

**8. C: Decision lens**
- Apply the letter readout to every layer's hidden state in one pass
  (`output_hidden_states`), so it costs nothing extra.
- *Prior art:* 2611.16321 already found decision information concentrates in
  intermediate layers.
- *What's new:* using it on items where the model reads right but acts wrong.
- It is more diagnosis than optimisation, hence M4.

**9. N15: Small IRT evaluation sets**
- Fit IRT on an item-by-model correctness matrix from about 5 local variants (sizes
  and quantisations).
- Pick the 50–100 most informative items, and predict the full score for held-out
  variants.
- *Prior art:* tinyBenchmarks and MINCE do this for general LLMs, not decision
  models. About 3 hours to build the matrix.

## Tier 2: L4, small fine-tunes or a few dollars of API calls

| # | Option | Metric to optimise | Laptop | Metric | Novelty | Alien z |
|---|---|---|---|---|---|---|
| 10 | **B. Nonsense option names (label-invariance training)** | option-rename attack success rate at matched clean accuracy; order-flip rate | L4 | M5 | New | +0.97 / +1.97 |
| 11 | **N8. Membership inference through decision probabilities** | MIA AUROC (target 0.5 for the defence) at matched accuracy | L4 | M5 | New | +2.24 / +0.60 |
| 12 | **N7. Watermarking a decision model against distillation** | AUROC / p-value for detecting a distilled student; teacher accuracy cost | L4 | M5 | New | +1.44 / +1.81 |
| 13 | **F. Calibration collapse under recursive distillation** | rare-class ECE and tail recall over 5 generations (aggregate ECE as the "looks fine" control) | L4 | M5 | New | +1.50 / +1.72 |
| 14 | **J. Bandit-budgeted optimisation of criteria text** | held-out accuracy and paraphrase flip rate per evaluation-call budget | L4 | M5 | New | +1.90 / +1.46 |
| 15 | **E. IRT routing between fast and slow models** | accuracy at a fixed cost budget (area under the cost–accuracy curve) | L4 | M5 | Partial | +0.99 / +1.61 |
| 16 | **N9. Active distillation from a decision API** | student accuracy per teacher call (or per $) | L4 | M5 | Partial | +3.43 / −0.55 |
| 17 | **N14. Incremental decisions on edited agent states** | latency at an exact-agreement rate of 1.0 with full recomputation | L4 | M5 | Partial | +0.92 / +1.42 |
| 18 | **I. Fine-tuning that preserves calibration and "none fit" detection** | in-domain ECE, null-detection AUROC and general-task retention (traded off) | L4 | M4 | New | +1.53 / +1.79 |
| 19 | **D. Calibrated decision graphs with value-of-information labelling** | final-decision accuracy per label spent | L4 | M4 | New | +0.66 / +2.05 |
| 20 | **N13. PMI-filtered synthetic decision data** | gold-test accuracy minus option-only "shortcut" accuracy | L4 | M4 | New | +1.08 / +1.40 |

**10. B: Nonsense option names**
- LoRA-train Qwen3-0.6B with option labels resampled from nonsense words bound to the
  real definitions, plus an order or label permutation consistency loss.
- *Evaluation:* the option-channel attack (2610.12292) and the testbed's flip rate
  (currently 28.5%).
- Fine-tuning takes about 1–2 hours.
- This is the **highest impact-to-effort option in the list**: every tested defence
  against the attack currently fails.
- *Watch:* PACT (2609.35865) trains with pair and permutation terms, so cite it and
  compare against it.

**11. N8: Membership inference**
- Fine-tune on half of BANKING77's training set; the other half is non-members.
- Attack using the probabilities alone, including minimal-pair sharpness.
- Defend with label smoothing or temperature, and report AUROC against accuracy.
- This matters because vendors fine-tune on customer decisions.

**12. N7: Watermarking against distillation**
- The teacher adds small, keyed biases to its probabilities on a secret family of
  trigger states.
- A student distilled from its outputs inherits the bias, and a hypothesis test
  detects it.
- Motivated by 2610.09188, where Jev labels trained a reranker in 21 minutes.

**13. F: Calibration collapse under recursive distillation**
- Loop: teacher (letter-logit 0.6B) labels data → ModernBERT-base student → that
  student labels the next generation's data, for 5 generations.
- About 30–40 minutes per generation on CPU.
- *Hypothesis:* aggregate ECE stays fine while the tail collapses.

**14. J: Optimising criteria text**
- An LLM critic proposes edits to the criteria and option definitions.
- UCB or successive halving allocates the evaluation budget among candidates.
- Candidates that are stable under paraphrase are preferred.
- Use a local Qwen3-1.7B as critic if you don't want API costs, though it is slower.

**15. E: IRT routing**
- *Pool:* 0.6B fast, 1.7B or thinking-mode slow, and optionally one API model.
- *Prior art:* IRT-Router (2506.01048) does this between LLMs.
- *What's new:* fast/slow pairing and features of the decision state.

**16. N9: Active distillation**
- Query the teacher only on the states where the student is most uncertain.
- *Prior art:* 2610.09188 studies how to spend a fixed labelling budget across two
  teachers, not active selection.

**17. N14: Incremental decisions**
- An agent state grows by appended observations. Reuse the KV cache and re-score only
  the new tail.
- *Prior art:* SharedKV-BT (2610.07327) shares prefixes across decisions, but not
  across successive edits.
- Mostly engineering, but the metric is crisp.

**18–20. I, D, N13**
- **I:** see README.md. On a laptop, use Qwen3-0.6B, not Jeva-4B.
- **D:** needs decision states with composable facts. Synthesise them, since the
  read-right/act-wrong benchmark may not be released.
- **N13:** synthetic states need a generator LLM (API, or slow locally). The metric
  difference has to be built yourself.

## Tier 3: L3, overnight runs or custom architecture work

| # | Option | Metric | Laptop | Metric | Novelty | Alien z |
|---|---|---|---|---|---|---|
| 21 | **A. Grammar-compiled masks for coherent decisions** | coherence violation (TV between direct and reconstructed category probabilities; P(A)+P(¬A)−1) at matched accuracy | L3 | M5 | New | +1.73 / +1.88 |
| 22 | **H. Unlearn the teacher so cascades work** | share of the fallback's confident errors that the student repeats, plus cascade accuracy at fixed cost | L3 | M4 | New | +4.36 / +0.71 |

- **A** has a beautiful metric, but needs a custom cross-encoder with block attention
  masks (NDM-style, 2610.25553).
- There is a **cheap L5 version**: skip training and compute the derived probabilities
  in code. P(¬A)=1−P(A); category = sum of its children. Measure how much accuracy and
  calibration that projection costs or gains. That alone is publishable as an
  extension of 2609.33971.

## Quick baselines (prior art exists, but useful as an afternoon's work)

| Option | Why it's low on novelty | Metric | Laptop |
|---|---|---|---|
| **K. PMI correction of option priors** | Surface Form Competition (2104.08315) | accuracy / ECE | L5, minutes |
| **N4. Label-shift correction** | SHIFT-JEV (2610.34329), prevalence shift (2610.26325) | ECE under simulated shift | L5 |
| **N12. Worst-subgroup calibration** | "Fast, Cheap, and Fair?" (2611.04510) audits Jev | worst-group ECE | L5 |
| **N6. Bandit red-teaming of typed guardrails** | FlipJev (2610.38895), JevAdvBench (2609.31142) | attack success per query budget | L5; use it as the *attack* for B |

---

## Suggested path
1. **Day 1:**
   - Run the testbed on BANKING77 and CLINC150.
   - Cache the probabilities for the full test sets.
   - Do **K + N11** together: same harness, same metric family, and it gives you the
     PMI/length-normalised baseline everything else should beat.
2. **Week 1, post-hoc on the cache:** **N5** (conformal selection) and **G**
   (fingerprints). Iterations take seconds, the metrics are standard, and both are new.
3. **Week 2, first fine-tune:** **B** (nonsense labels), using **N6** as the attack
   and the 28.5% flip rate as the number to drive down.

## Re-run the benchmark
```bash
pip install torch transformers peft datasets
python laptop_testbed/bench_letter_logit.py --model Qwen/Qwen3-0.6B --n 200 --k 8 --out bench.json
```
