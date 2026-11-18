# New research directions for System One decision models, found with Alien

> **See also [RANKED.md](RANKED.md):** 26 options (these 11 plus 15 more), ranked by
> whether they run on a laptop and how well-defined their metric is, with a measured
> CPU baseline.

**Question.** What research directions are coherent but unlikely to be pursued for
the new class of *System One / decision models*? These include TypeSafe's Jev,
Jeva, Microsoft‑Decision‑1, gemini‑decision‑1, Prism‑1 and their open relatives.
They return typed decisions with calibrated probabilities in one forward pass,
with no generated text.

**Method.**
1. Collect the literature (papers and blog posts).
2. Extract idea atoms from it.
3. Map the atoms onto the 273-atom catalogue of
   [The Alien Space of Science](https://github.com/alejandrohdez00/alien-space-of-science)
   (arXiv:2603.01092).
4. Score every 3-atom combination that touches the System One anchors with Alien's
   two released models:
   - **coherence:** do these ideas form a methodology?
   - **unavailability:** how unlikely is any real researcher to combine them?
5. Turn the best combinations into proposals aimed at open problems the corpus names.
6. Check each proposal against arXiv for prior art.

Everything here is reproducible from the scripts in this folder (see [Reproduce](#reproduce)).

---

## 1. What the corpus says System One models are (and what is open)

The corpus is in [`corpus/`](corpus/). It has three topical files from about 60
sources, plus [`corpus/arxiv_abstracts.md`](corpus/arxiv_abstracts.md) with 28 primary
arXiv abstracts. All 28 IDs and titles were checked against the arXiv API.

**Interface.** A request is `state + typed questions`: Choice, Noul (yes/no) or Score
(rubric). The answer is a probability per option, with no decoding and no parse
failures. Input-only billing gives latency under 100 ms to a few hundred ms.

**What is known about how they work:**
- **Jeva** (2610.18773): options are encoded independently, then decided jointly by
  cross-attention from the state. It is permutation-invariant by construction, has a
  separate *coverage* head for "none fit", and caches option memory.
- **Prism‑1** (2610.22066) and **Narrow Decision Models** (2610.25553) get order
  invariance from block attention masks.
- **Inner‑Jev** (2610.17205): letter-logit readout plus LoRA nearly matches Jev.
- **RLCD** (TypeSafe's training method) is undisclosed. The only public
  operationalisation is PRDO (2609.38850): proper-score training of the readout,
  then REINFORCE on rationales.

**Main failure findings:**
- *Read right, act wrong* (2610.18579): most wrong actions follow correct perception.
  Code-composed probe answers repair them, and the missing input is often the next
  sub-goal.
- *Static ≠ closed-loop* (System1‑Arena 2610.21244, SO‑Arena 2611.15777).
- *Labels override definitions* and the *option-channel attack* (2609.26758,
  2610.12292): renaming one option opens guardrails. Rewriting labels to A/B in the calling code
  closes that channel; every defence against *injected state text* was defeated.
- *Incoherent probabilities*: P(A)+P(¬A)≠1 (2609.33209), and fine-label versus
  category reconstructions disagree (2609.33971).
- *Same mistakes as LLM judges* (2609.29769), which undermines cascades.
- *Calibration under prevalence shift* (2610.26325) and *specialisation collapse*
  after narrow fine-tuning (2611.03755).

> **Evidence caveat.** While the corpus was being collected, most source pages
> (arxiv.org, the vendor blogs) were blocked from this environment, so the topical
> notes come largely from search-result excerpts. Each file marks what was read in
> full and what was not. After arxiv.org was allowed, the abstracts in
> `arxiv_abstracts.md` and the prior-art abstracts below were read first-hand.
> Treat other numbers as "reported by".

### What is genuinely new relative to the pre-2026 literature
The corpus's 84 idea atoms were embedded and matched against Alien's 16k-paper
catalogue (see [`results/anchors.json`](results/anchors.json)). The atoms with *no*
good match are the conceptual novelties of System One models:
- many questions over one encoded input;
- **coverage versus competition** for null detection;
- encoding options independently, then deciding jointly;
- typed multi-field calls;
- channel-shift robustness;
- rubric grades as ordinal distributions;
- the next **sub-goal** as the missing latent variable.

The best-matched catalogue atoms became the **24 anchors** for the search. The top
ones are: confidence calibration (161), ECE metrics (163), Bradley–Terry pairwise
choice (155), positional bias (82), conformal risk control (162), bandits for workflow
decisions (71), item response theory (2), query decomposition (118), contextual
calibration (72) and noisy-label learning (141).

## 2. The search

The pool was every triplet containing at least one anchor: **811,772 of 3,353,896**,
scored *exhaustively* on a 4-core CPU in about 10 minutes.

**Coherence trick.** For k=3, coherence only needs log p(·|BOS), p(·|BOS a) and
p(·|BOS a b). So 74,529 short forward passes fill a 273³ table, and every triplet's
6-permutation coherence is read from it. This matches the repo's official scorer to
**8.7e‑7** on 200 random sets.

**Availability** uses the released two-tower author/atom model against the
39,791-author bank, taking the median of the top 10 authors.

**Selection.** The score is `(1−β)·z(coherence) + β·z(unavailability)`, normalised over
the pool, at β ∈ {0.5, 0.7}. The pool is split into "bridge" combinations (1 anchor
plus 2 ideas from elsewhere) and "core" combinations (2–3 anchors). Each atom can
appear at most 6 times in a list. Across the pool, coherence and unavailability
correlate at −0.62: the paper's trade-off shows up here too.

Full rankings are in [`results/system_one_search.json`](results/system_one_search.json).
[`results/candidates_with_gaps.json`](results/candidates_with_gaps.json) matches the top
379 to the corpus's 41 open problems.

## 3. Proposals

Eleven combinations were chosen from the top of the Alien rankings. They were chosen
by hand for fit to a named open problem and for diversity; the method itself does not
choose them. Each was then searched on arXiv
([`results/novelty_log.txt`](results/novelty_log.txt)). The "Alien" line gives the
z-scores and list positions.

### Tier 1: no close prior art found

#### A. Coherence by construction: compile typed decision grammars into attention masks
**Alien:** formal grammars (22) + faithfulness via necessity/sufficiency tests (164) +
attention masks as programmable routing (193). Coherence z=+1.73, unavailability
z=+1.88, **#1** bridge at β=0.7.

**Problem.** Independent heads break the probability axioms: negation pairs sum to
1.19, and fine-label versus category reconstructions differ in total variation by
0.22–0.69, with CLINC150 accuracy moving 23 points (2609.33971, 2609.33209). Labels
also override definitions (2609.26758).

**Idea.**
- Define a small grammar of decision types (Choice, Noul, Score) with connectives:
  NOT, exclusive-OR, IS‑A (category to sub-category), IMPLIES.
- A request's questions are parsed into a tree, and the tree is compiled into
  (a) an attention mask over question slots that shares evidence only along grammar
  edges, and (b) a readout in which derived probabilities are *computed* from base
  ones. Examples: P(¬A)=1−P(A); category = sum of its children; exclusive sets share
  one softmax.
- The same grammar generates synthetic coherence suites with exact ground truth.
- Faithfulness is measured with necessity/sufficiency ablations of the *definition*
  text against the *label* text. A faithful model moves with the definition and
  ignores the label.

**First experiment.** Retrofit an open model (Jeva‑4B or an Inner‑Jev recipe) on
CLINC150/MASSIVE with category hierarchies. Compare independent heads with the
grammar-compiled readout on coherence violation, accuracy, ECE and the
definition-versus-label necessity score.

**Prior art.** 2609.33971 and 2609.33209 *diagnose* incoherence. NDM (2610.25553) and
Prism‑1 use block masks, but for *order* invariance within one question. None compiles
relationships *between* questions.

#### B. "Jabberwocky options": option names as a protected attribute
**Alien:** zero-shot semantic matching with definitions (58) + Jabberwocky-style
perturbations (73) + fairness as invariance across subgroups (165). Unavailability
z=+1.97, #5 bridge at β=0.7.

**Problem.** The option-channel attack (2610.12292): renaming the permissive option
opens typed guardrails 93–100% of the time on models whose calling library feeds the
label to the network. Rewriting labels to A/B at the call site closes this channel
completely, at some cost in wrongly blocked actions, and prompt-level "ignore the
names" instructions do not. Models
follow the option name, not its definition (2609.26758, 2610.02586).

**Idea.**
- Treat the option *label* the way fairness work treats a protected attribute: the
  decision must be invariant to it.
- Train with labels resampled from nonsense names ("blicket", "dax", random strings)
  bound to the real definitions, so only the definition carries signal.
- Score options by matching the state to the *definition*, not the label token.
- Report fairness-style metrics: flip rate, and the gap in error rate and confidence
  across label renderings, instead of mean accuracy.

**First experiment.** Reproduce the option-channel attack on an open decision model.
Fine-tune with label randomisation plus an invariance penalty. Report attack success
against clean accuracy, and check for a cost when labels *are* informative.

**Prior art.** None found. The attack papers suggest neutral A/B labels at inference;
this is a training-time invariance with a subgroup audit.

#### F. Calibration collapse under recursive distillation
**Alien:** model collapse (28) + temperature scaling (161) + ECE metrics (163).
Coherence z=+1.50, unavailability z=+1.72, **#2** core at β=0.7.

**Problem.** Decision models are distilled from LLM-ensemble labels; quality is capped
by the teacher, and models agree with frontier LLMs more than with ground truth. They
are then used as judges, labellers and RL teachers (2609.26550, 2611.17167, 2610.09188),
so the next generation trains on their output.

**Idea.**
- Simulate generations: teacher ensemble → decision model → it labels fresh data →
  the next model, and so on.
- Track ECE, *class-conditional* calibration, the probability mass on rare options,
  and entropy.
- Hypothesis: per-generation temperature scaling keeps aggregate ECE looking healthy
  while rare-option recall and calibration collapse. Calibration "looks fine" exactly
  when the long tail is gone.
- Test remedies: anchoring with a fixed fraction of real labels, proper-score
  training, and calibration by class prior.

**Prior art.** None on recursion. 2610.09188 studies single-step multi-teacher
distillation with Jev.

#### G. Probability fingerprints: conformal drift detection for hosted decision APIs
**Alien:** provenance via divergence and perturbation curvature (36) + temperature
scaling (161) + conformal risk control (162). Coherence z=+4.08, unavailability
z=+0.70, **#1** core at both β values.

**Problem.** Hosted models change silently (the `jev-latest` rolling alias; gateway
versus vendor serving). Calibration under version drift has not been measured, and
vendors don't disclose how probabilities are produced.

**Idea.**
- Keep a small canary set of decision states, each with small perturbations.
- The vector of returned probabilities, and their sensitivity to the perturbations
  (a probability-curvature profile), is a fingerprint of the serving model.
- Detect a model change with a conformal exchangeability test on fingerprint
  divergence. On detection, refit temperature scaling and recompute conformal
  thresholds so the user's risk guarantee still holds.
- Bonus: users can check which model a gateway is actually serving.

**First experiment.** Simulate version changes with fine-tuned variants of an open
model and real Jev 1.13→1.14 calls. Measure detection power against canary size, and
conformal coverage before and after drift, with and without re-calibration.

**Prior art.** None found for decision APIs.

#### H. Unlearn the teacher: make fast models fail differently so cascades work
**Alien:** machine unlearning (29) + dataset curation with proxy classifiers (63) +
learning from noisy supervisors (141). Coherence z=+4.36, unavailability z=+0.71,
**#1** bridge at β=0.5.

**Problem.** Decision models and LLM judges are "wrong in the same places": over 85%
of the confident errors repeat (2609.29769). So confidence-gated cascades can't
recover those errors, and student quality is capped by the teacher.

**Idea.**
- Find regions where teacher-ensemble labels are confidently wrong against a small
  gold set.
- Treat teacher labels as noisy (neighbourhood consistency, loss-based filtering).
- Train a proxy classifier that flags error-prone items.
- Apply targeted unlearning to the student to remove the shortcuts it inherited,
  checking the removal in internal probabilities rather than outputs alone.
- The target metric is **error complementarity** with the fallback: how many of the
  fallback's confident errors the student shares. Standalone accuracy is secondary.

**Prediction.** Cascade accuracy at fixed cost rises even if the student's standalone
accuracy is flat.

**Prior art.** None found.

#### D. Calibrated decision graphs with value-of-information labelling
**Alien:** active learning (42) + contextual (content-free) calibration (72) +
decisions as DAGs (132). Unavailability z=+2.05, the highest of any proposal; #3 core
at β=0.7.

**Problem.** Read right, act wrong (2610.18579): models read every fact and still fail
to combine them, and *code*-composed probe answers repair this. Staged deployment
needs to know where to spend labels.

**Idea.**
- Compile a decision into a DAG of atomic typed judgments (perception nodes) combined
  in code.
- Calibrate each node against its *resting prior*, measured with content-masked
  states, and propagate uncertainty to the final decision.
- Choose which node to label next by **value of information on the final decision**,
  not by node entropy.

**First experiment.** Use the customer-service and tool-use states from the
read-right/act-wrong benchmark. Compare a single monolithic Choice with the DAG on
label-budget curves.

**Prior art.** None found.

#### I. Fine-tuning that preserves calibration and coverage for open decision models
**Alien:** ECE metrics (163) + OOD detection via the negative space (174) + low-rank
or orthogonal weight updates (222). Coherence z=+1.53, unavailability z=+1.79, #3
bridge at β=0.7.

**Problem.** Narrow fine-tuning costs 9–45 points of general decision ability
("specialisation collapse", 2611.03755). Calibration breaks under prevalence shift
(2610.26325). There is no fine-tuning protocol that preserves calibration, and
open-set calibration of `p_null` has not been reported.

**Idea.**
- LoRA confined to a subspace orthogonal to the directions that carry the base
  model's calibration and coverage behaviour, estimated on the base model's
  calibration set.
- A differentiable ECE-variant regulariser.
- Train the coverage (null) head on synthetic "negative space": generated distractor
  options and states that fit nothing. This keeps `p_null` calibrated on
  out-of-distribution inputs after domain adaptation.

**First experiment.** Adapt Jeva‑4B to a BANKING77 subset. Measure in-domain accuracy
and ECE, null-detection AUROC on held-out intents, and general decision benchmarks,
against vanilla LoRA.

**Prior art.** Adjacent work exists (Bayesian LoRA 2610.35457; 2611.03755 remediates
by mixing corpora), but nothing on preserving the coverage head.

### Tier 2: promising, but overlapping or prior work exists

#### J. Sharpness-aware criteria optimisation for closed decision models
**Alien:** bandits (71) + textual gradients (97) + curvature and Fisher approximations
(211). #10 bridge at β=0.7.

Jev has no fine-tuning path; adaptation is only through the `state` and `criteria`
text ("prompt gymnastics"). Because calls are cheap and billed on input only, the
criteria and option definitions can be optimised directly:
- an LLM critic proposes edits (textual gradients);
- a bandit (UCB or successive halving) allocates the evaluation budget;
- candidates whose decision probabilities are *flat* under paraphrase and sentence
  ablation, estimated by finite differences, are preferred. This is the prompt
  analogue of preferring flat minima, and it targets wording sensitivity.

**Prior art.** None for decision models. General prompt-optimisation agents exist
(2608.06714).

#### E. Item response theory routing between System 1 and System 2
**Alien:** item response theory (2) + predictive routing (15) + lost-in-the-middle (35).
#8 core at β=0.7.

Fit an IRT model over (decision state × model) outcomes. Item difficulty is predicted
from state features, including *where in a long state the decisive evidence sits*.
Route each state to the cheapest model whose predicted P(correct) clears the target.
This is meant to catch the confidently wrong errors that confidence gating can't
(2609.29769), and to answer the capability-versus-reliability split in SO‑Arena.

**Prior art.** IRT‑Router (2506.01048) does IRT routing between LLMs. What's new here
is the fast/slow pairing and features of the decision state.

#### C. A per-layer "decision lens" to see where composition fails
**Alien:** logit lens (4) + group-relative RL (231) + credit assignment (258). #7
bridge at β=0.7.

Apply the decision head at every layer and track where each decision settles. Do
act-wrong items never settle, or settle and then get overwritten? This gives the
first measurement of how many composition steps a single pass can do. Exits would be
trained with group-relative RL (proper score minus compute).

**Prior art.** 2611.16321 already shows decision information concentrates in
intermediate layers and trains gated early exits. The remaining contribution is the
*diagnostic* use on read-right/act-wrong items.

#### K. PMI-corrected option scoring with minimal-pair audits
**Alien:** PMI (10) + length artifacts (38) + minimal pairs (56). #6 bridge at β=0.7.

For letter-logit open decision models, score log p(o|state) − log p(o|content-free
state), with length-normalised definitions. Audit with minimal pairs that change one
decisive fact, or one word of an option.

**Prior art.** This is domain-conditional PMI (Surface Form Competition, 2104.08315)
applied to System One models. Mostly an application study.

---

## 4. Takeaways
- **Calibration-centred ideas dominate the anchors**, but Alien's least available
  combinations pair them with ideas from *other* communities: formal grammars,
  fairness, model collapse, text forensics, unlearning. Those pairings are where the
  Tier 1 proposals come from.
- The two directions with the most immediate practical value are **B** (it targets an
  name-following that also costs clean accuracy and order stability; see the
  correction in RANKED.md) and **H** (it attacks the
  correlated-error problem that limits every fast/slow cascade).
- **A** and **F** are the cleanest research papers: each has a crisp falsifiable
  hypothesis and an open-model experiment that can be run on one GPU.

## Limitations
- Alien's catalogue comes from about 16k LLM papers that *predate* System One models,
  so the newest concepts can only enter as anchors. The least-covered list above shows
  what the catalogue cannot represent.
- The 11 finalists were chosen by hand from the ranked lists. The scores are the
  models'; the reinterpretation for System One models is the author's.
- The prior-art check is a keyword search of arXiv only, not a full literature review.
- Some corpus numbers are second-hand (see the evidence caveat).

## Reproduce
Requires the Alien repo with its released models and `papers/` in place
(`hf download alejandrohdez/alien-models ...`, see the Alien README), plus `torch` and
`sentence-transformers`.
```bash
python extract_corpus_atoms.py corpus corpus/corpus_atoms.json
python map_corpus.py corpus/corpus_atoms.json $ALIEN/papers/clusters_80.json results/anchors.json 24
PYTHONPATH=$ALIEN python alien_decision_search.py --alien-root $ALIEN \
    --anchors results/anchors.json --out results/system_one_search.json
python gap_match.py results/system_one_search.json results/anchors_emb.npz \
    corpus/corpus_atoms.json results/candidates_with_gaps.json
python arxiv_novelty.py results/novelty_queries.json results/novelty_hits.json
python show.py results/system_one_search.json $ALIEN/papers/clusters_80.json 15
```
