# Option 3 in depth: hub options in large option sets

## The idea in one paragraph
Many System One designs make a decision by **embedding the state and each option
separately and picking the most similar option**. Examples:
- Jeva's "encode options independently, decide collectively" design, with its
  2,048-option scaling claim;
- retrieval-as-choice for tool and policy selection;
- intent routers;
- zero-shot classification by label embeddings.

In high-dimensional embedding spaces some points are **hubs**: they sit close to almost
everything. A hub option wins far more often than it should, and it soaks up errors and
out-of-scope queries. Nobody has measured this for decision models. The proposal is to:
1. measure it;
2. show how it grows with the number of options K;
3. fix it with cheap, training-free corrections that use only **unlabelled past
   traffic**.

**Alien provenance.** The triplet was PMI-style prior correction (atom 10) + minimal-pair
diagnostics (56) + anisotropy, i.e. embeddings collapsing into a narrow cone (127).
Coherence z = +1.32, unavailability z = +1.61. The catalogue also has a hubness atom
(128), which is the mechanism tested here.

## Pilot (run in this repo, about 1 minute on a 4-core CPU with no GPU)
Script: [`laptop_testbed/hub_options_pilot.py`](laptop_testbed/hub_options_pilot.py).

**Setup.**
- Data: CLINC150 test split, with 150 intents × 30 queries = 4,500 in-scope queries plus
  1,000 out-of-scope (OOS) queries. Options are the bare intent names.
- Corrections use 5,000 CLINC *training* utterances as unlabelled "past traffic"; their
  labels are never used.
- Prediction rule: argmax of cosine similarity.

Every option's true count is exactly 30. "Max picks" is how often the most-picked option
was chosen.

**BGE-large (335M).** Results at K = 150:

| method | accuracy | max picks (true 30) | top-10 options' share of predictions (even = 6.7%) | share of *errors* on those 10 | OOS absorbed by those 10 | OOS AUROC |
|---|---|---|---|---|---|---|
| raw cosine | 71.9% | 89 | 14.2% | 28.8% | 15.6% | 0.911 |
| centring | 74.1% | 70 | 12.9% | 25.7% | **9.2%** | **0.921** |
| option prior (PMI-like) | 73.4% | 69 | 12.9% | 24.7% | 10.3% | 0.914 |
| CSLS | 74.6% | 83 | 13.3% | 31.0% | 13.1% | 0.898 |
| inverted softmax (querybank norm.) | **76.0%** | **58** | **11.0%** | **21.4%** | 12.2% | 0.907 |

Accuracy against the number of options (random subsets of K intents, 30 subsets each;
BGE-large):

| K | raw | best correction | gain |
|---|---|---|---|
| 8 | 94.3% | 95.9% | +1.6 |
| 32 | 86.8% | 89.9% | +3.1 |
| 75 | 79.5% | 83.2% | +3.7 |
| 150 | 71.9% | 76.0% | **+4.1** |

BGE-small (33M) shows the same pattern with smaller numbers:
- raw 69.4% → 72.8% at K = 150;
- gain +1.6 at K = 8 and +3.3 at K = 150;
- max picks 81.

**What the pilot already says** (one run per model; with 4,500 test queries, a single
accuracy has a 95% interval of about ±1.3 points, and paired comparisons are tighter):
1. **Hubs exist and concentrate errors.** The busiest option is chosen about 3× as often
   as it should be, and the 10 busiest options take about 29% of all errors against a
   6.7% even share.
2. **The penalty grows with K**, and so does the payoff from correcting it. This matters
   because the System One pitch is scaling to hundreds or thousands of options.
3. **A bigger encoder is not immune.** BGE-large is more accurate but shows *more*
   concentration than BGE-small (max picks 89 vs 81).
4. **The metrics disagree.** CSLS, the correction that fixed hubness in this project's
   atom mapping, raises accuracy but *increases* concentration and hurts OOS detection.
   So hub skewness alone is the wrong target, and the paper has to report accuracy,
   concentration and OOS together.
5. **No correction wins everything.** Inverted softmax is best for accuracy and
   concentration; centring is best for OOS. That suggests combining them.

**Caveats.**
- The options are bare intent names. Real decision APIs bind each option to a written
  definition, which may reduce or change hubness. That is the first thing to test.
- Single seed, one dataset, two models from one family.

## Full study design

**Research questions.**
1. How strong is hubness in decision models that score options by embedding, and how
   does it scale with K, with the encoder, and with option text (name vs definition)?
2. Do hubs cause *confident* errors, and do they hurt calibration and OOS ("none fit")
   detection?
3. Which training-free corrections fix it? How much unlabelled traffic do they need, and
   can they run online?

**Models.** All embedding models run on CPU; a 4B model is feasible for inference on a
16 GB laptop.
- BGE-small/large, E5, GTE, and a ModernBERT bi-encoder.
- If feasible: **Jeva-4B** (option memory is cached and order-independent by design),
  scoring with its own decision head instead of plain cosine.

**Data, by number of options.**

| Dataset | Options (K) |
|---|---|
| BANKING77 | 77 |
| HWU64 | 64 |
| MASSIVE | 60 |
| CLINC150 (+ OOS) | 150 |
| A tool-retrieval set (ToolRet or similar) | 1,000 or more, close to Jeva's 2,048-option claim |

**Option-text conditions.**
- bare name;
- name plus one-line definition;
- a long definition (this also links to option 5's length bias).

**Corrections (all training-free).**
- centring and whitening;
- option prior (PMI-like, option 11's family);
- CSLS;
- inverted softmax / querybank normalisation;
- **balanced optimal-transport assignment** (Sinkhorn over a batch of recent traffic, so
  each option's usage matches its expected prior);
- the combination centring + inverted softmax.

**Deployment-realistic variants.**
- **Pool-size curve:** accuracy against the number of unlabelled past queries (100 /
  1k / 10k).
- **Online version:** keep the statistics as an exponential moving average as traffic
  arrives, and test under drift.
- **Cold start:** what to do with a brand-new option that has no traffic yet.

**Metrics.**
- *Primary, to optimise:* **accuracy at the largest K**, and the slope of accuracy
  against log K, i.e. how gracefully the model scales.
- *Secondary:*
  - hub concentration (max picks ÷ expected, and the share of errors on the top 10);
  - OOS AUROC and the share of OOS absorbed by hubs;
  - ECE if a calibrated score is produced (for example via temperature on the corrected
    scores);
  - the confidence of hub-attracted errors, to test whether hubs cause *confident*
    mistakes.

## Contributions
1. **Hubness as a named, measured failure mode of decision models**, with a metric suite,
   and a scaling result showing the penalty grows with K.
2. **Training-free corrections that use only unlabelled traffic.** The pilot shows +4
   points at K = 150 with no labels and no training. This includes online and cold-start
   variants that a deployed router can actually use.
3. **The finding that the metrics come apart**: accuracy, concentration and OOS detection
   prefer different corrections. That shapes how such systems should be evaluated.
4. **A check of whether Jeva-style architectures** (learned decision head over cached
   option memory) inherit the problem or solve it.

## Expected results (hypotheses, beyond what the pilot shows)
- Name-plus-definition options reduce but do not remove hubness.
- At K ≥ 1,000 (tool sets), the gap between raw scoring and the best correction widens
  well beyond the 4 points seen at K = 150.
- A few hundred to a few thousand unlabelled queries are enough for most of the gain,
  and the EMA version tracks drift.
- Hub-attracted errors are as confident as correct answers. That would tie this to
  option 1 (G) and to the "reversed decisions aren't low-confidence" finding in
  2610.12292.
- A learned decision head like Jeva's shows less hubness than plain cosine but not none.

## If it fails
- If definitions or Jeva-style heads remove hubness, the result is "the encode-options-
  independently design is safe at scale", which supports the Jeva/Prism direction.
- If the corrections stop helping at K ≥ 1,000, that exposes a limit of training-free
  fixes and motivates learned option priors.

## Prior art and how this differs
The **correction methods are known** from cross-lingual and cross-modal retrieval:
- hubness in high dimensions (Radovanović et al., JMLR 2010);
- CSLS (Conneau et al., 2018);
- inverted softmax (Smith et al., 2017);
- querybank normalisation (Bogolin et al., 2022).

The arXiv check found nothing on hubness in decision models or tool selection.

**The novelty is the setting and the findings:**
- typed decision models with a growing option set;
- the interaction with OOS ("none fit") detection;
- deployment constraints: unlabelled traffic, online updates, new options;
- evaluating Jeva-style architectures.

Pitch it as an empirical paper with practical recipes, not as a new correction method.

## Laptop plan (about 2–3 days of compute-light work)
1. **Day 1:** add definitions to the options; run the 4 intent datasets × 4 encoders.
   About 1 hour of CPU in total.
2. **Day 2:** add Sinkhorn/OT and the combined correction; produce the pool-size and
   online-EMA curves.
3. **Day 3:** the large-K tool-selection set; Jeva-4B inference if memory allows.

```bash
python laptop_testbed/hub_options_pilot.py --model BAAI/bge-small-en-v1.5 --out hub_small.json   # ~1 min
python laptop_testbed/hub_options_pilot.py --model BAAI/bge-large-en-v1.5 --out hub_large.json   # ~6 min
```
