# The 26 options in detail: contributions and expected results

Companion to [RANKED.md](RANKED.md), in the same order. Each entry has:
- **Problem:** what is broken today, citing the corpus.
- **Approach:** what you would build.
- **Contributions:** what the paper would claim.
- **Expected results:** the headline table or figure, stated as a *hypothesis*.
- **If it fails:** why a negative result would still be informative.
- **Baselines and risks.**

> Nothing under "Expected results" has been run. These are predictions to test,
> grounded in the corpus and in one measured baseline: Qwen3-0.6B letter-logit
> readout on BANKING77 with 8 options.
>
> | accuracy | ECE | mean confidence | order flip rate |
> |---|---|---|---|
> | 78.5% | 0.138 | 0.92 | 28.5% |
>
> Numbers quoted from papers are as *reported* by them.

Shared setup unless stated otherwise:
- Testbed: `laptop_testbed/bench_letter_logit.py`.
- Datasets: BANKING77, CLINC150 (with out-of-scope items) and MASSIVE.
- Models: Qwen3-0.6B / 1.7B. Optionally, cheap calls to a hosted decision API (Jev,
  Decision-1) as the "real-world" check.

---

# Tier 1: inference only or post-hoc

## 1. G: Probability fingerprints for silent model changes
**Problem.**
- Hosted decision models change under rolling aliases (`jev-latest`).
- Gateways may serve something other than what they claim. Corpus evidence:
  gateway p50 latency is 2–3× the vendor figure.
- Calibration and conformal thresholds tuned last month silently stop being valid.
- No paper measures calibration under version drift.

**Approach.**
- A canary set of about 300 decision states, each with about 3 meaning-preserving
  perturbations.
- The vector of returned probabilities, plus how much they move under perturbation
  (a "probability-curvature" profile), is a fingerprint.
- A conformal exchangeability test (a permutation test on fingerprint distances)
  decides "same model or not" at a controlled false-alarm rate.
- On an alarm, refit temperature scaling and recompute conformal thresholds from a
  small labelled buffer.

**Contributions.**
1. The first drift-detection protocol for typed decision APIs, with a guaranteed
   false-alarm rate.
2. Evidence that the *perturbation-sensitivity* features detect changes that raw
   output agreement misses.
3. A detect-then-re-calibrate procedure that restores the user's coverage guarantee.
4. An audit tool: does the gateway serve the model it claims?

**Expected results.**
- *Detection power against canary size*, one curve per type of change: precision
  change (fp32→int8), LoRA nudge, size change (0.6B→1.7B), prompt-template change.
- *Hypothesis:* size or template changes are detected with about 50 canaries.
  Quantisation needs about 300 and is only caught by the curvature features.
- *Coverage before and after drift:* conformal sets built for 90% coverage on version
  1 fall noticeably below 90% on version 2, and re-calibration restores 90% ± 1%.

**If it fails.** If quantisation-level changes can't be detected at reasonable canary
sizes, that is an upper bound on how auditable hosted decision APIs are. Also worth
reporting.

**Baselines.** Top-1 agreement rate, mean KL between versions, and output-hash
comparison.

**Risk.** Hosted APIs may be non-deterministic run to run. Measure that noise floor
first; it becomes part of the test.

## 2. N5: Choosing which items to label for conformal calibration
**Problem.**
- Conformal risk control gives distribution-free guarantees, but needs a labelled
  calibration set.
- Teams adopting decision models usually have few labels. Staged deployment ("label
  real cases first") is the recommended practice.

**Approach.**
- Given unlabelled deployment states and a budget of *n* labels, choose which to
  label. Options: a DPP or submodular coverage of embedding space, uncertainty
  stratification, or stratification by predicted class.
- Correct for the non-random choice with *weighted* conformal prediction, so the
  guarantee survives.

**Contributions.**
1. A label-budgeted conformal procedure for decision models whose coverage guarantee
   is preserved under selective labelling.
2. Evidence that stratified or diverse selection gives smaller prediction sets than
   random selection at the same coverage.
3. Practical guidance: how many labels are needed for a ±2% coverage guarantee on
   K-way intent tasks.

**Expected results.**
- *Set size at 90% coverage against n* (n = 50…1,000), for random vs. uncertainty vs.
  DPP vs. class-stratified selection.
- *Hypothesis:* class-stratified or DPP selection reaches random selection's n=500
  set size with roughly half the labels.
- Coverage stays within ±1–2% of the target for the weighted variants, and pure
  uncertainty sampling *without* weighting under-covers. That is the cautionary
  result.

**If it fails.** If nothing beats random selection, that is a clean recommendation in
itself: label randomly, and here is the n you need.

**Baselines.** Random calibration sets; split conformal with the full labelled set as
an oracle.

**Risk.** Weighted conformal can inflate set sizes. Report both coverage and size.

## 3. N1: "Hub" options in large option sets
**Now worked out in full, with a pilot that has run: see
[OPTION3_HUB_OPTIONS.md](OPTION3_HUB_OPTIONS.md).**

Pilot on CLINC150 with BGE-large, 150 options, on CPU:
- Raw cosine reaches 71.9% accuracy. The busiest option is picked 89 times against a
  true count of 30.
- Training-free corrections that use only unlabelled traffic reach 76.0%.
- The gain grows with the number of options: +1.6 points at 8 options, +4.1 at 150.

## 4. N10: Anytime decisions by sequential evidence accumulation
**Problem.**
- Decision models spend the same compute on every input, and must read the whole
  state before answering.
- Many states are decided by their first sentence. In agent loops and moderation,
  latency is part of correctness (System1-Arena; System Switch).

**Approach.**
- Feed the state in chunks and read the decision distribution after each one.
- Accumulate evidence as a log-likelihood-ratio sum, like an integrate-and-fire
  neuron or a sequential probability ratio test.
- Stop when it crosses a threshold. The threshold is set by conformal or Learn-then-
  Test, so the error of early stopping is controlled.

**Contributions.**
1. A training-free anytime readout for any decision model.
2. Early stopping with a guaranteed error rate.
3. A characterisation of which decision types can be decided early (intent, toxicity)
   and which can't (tasks whose decisive fact comes late).

**Expected results.**
- *Accuracy against tokens read*, with the full-read baseline as a horizontal line.
- *Hypothesis:* for intent tasks, half or fewer of the tokens give accuracy within 1
  point of the full read.
- For constructed states with late evidence, the method correctly *declines* to stop
  early, which shows the guarantee working.

**If it fails.** If early probabilities are too miscalibrated to stop on, that says
the decision probabilities are only meaningful at the end of the input. Worth knowing
for streaming uses.

**Baselines.** Fixed truncation at x% of tokens; confidence thresholding without
accumulation.

**Risk.** Re-scoring each prefix costs compute unless the KV cache is reused. Measure
wall-clock time, not just tokens.

## 5. N11: Option-definition length bias
**Problem.**
- Decision APIs bind each option to a natural-language definition.
- Generative LMs and judges are known to favour longer texts (verbosity bias). Typed
  decision models may also favour options whose definitions are longer, shorter, or
  more detailed, independent of meaning.
- The corpus shows labels already override definitions (2609.26758).

**Approach.**
- For each option, write a short, medium and long definition that mean the same, with
  meaning checked by an NLI model or a manual sample.
- Measure the change in P(option) when only one option's definition length changes.
- Fit P against relative length.
- Fixes: length-normalised scoring, the PMI prior (K), and a definition-length
  augmentation in fine-tuning.

**Contributions.**
1. A controlled measurement of definition-length bias in typed decision models.
2. A simple debiasing method with a clean target (slope 0).
3. Guidance on writing option definitions.

**Expected results.**
- *A slope plot:* the change in log P(option) against the definition-length ratio.
- *Hypothesis:* a non-zero slope (likely positive) for letter-logit readout, and a
  different sign or size for embedding-scored models.
- Fixes bring the slope near 0 with under 1 point of accuracy loss.

**If it fails.** If the slope is about 0, definition length is safe to vary, which is
a useful robustness certificate.

**Baselines.** Uncorrected readout; content-free calibration.

**Risk.** Paraphrases might not mean exactly the same. Use an NLI filter and a human
check on a sample.

## 6. N3: Where the evidence sits in a long state
**Problem.**
- Agent states are long (tool outputs, histories).
- Generative LLMs lose information in the middle of long contexts.
- For decision models, only *option* position has been studied (2611.06384 reports
  up to 6.1 points of second-position advantage). The position of the *evidence*
  inside the state hasn't been.

**Approach.**
- Insert the decisive fact at 0 / 25 / 50 / 75 / 100% of a 0.5–2k-token distractor
  state.
- Measure accuracy and confidence by position.
- Fixes: question-first prompting, chunk-then-aggregate (decide per chunk, combine
  with a noisy-OR or max), and reordering the state by retrieved relevance.

**Contributions.**
1. The first "evidence position" curve for decision models.
2. A demonstration that the *confidence* curve does not dip where *accuracy* dips,
   i.e. errors in the middle are overconfident. That is the most interesting possible
   finding for decision use.
3. A cheap fix.

**Expected results.**
- *A U-shaped accuracy curve over position* for the 0.6B readout, compared with the
  confidence curve.
- *Hypothesis:* a 5–15 point accuracy dip in the middle, with nearly flat confidence,
  so ECE is worst there.
- Chunk-then-aggregate flattens the curve.

**If it fails.** A flat curve would show decision readouts are more robust to
evidence position than generation. That is still a citable result.

**Baselines.** Short-state accuracy as a ceiling; generative answering with the same
model.

**Risk.** A 0.6B model with 2k tokens runs at about 2 s per decision on CPU. Keep it
to about 600 items.

## 7. N2: Numeric and date boundary minimal pairs
**Problem.**
- Many production decisions are threshold checks: refund over a limit, deadline
  passed, age over 18.
- With fixed compute per question, decision models fail at arithmetic, counting and
  dates. 2609.39496 reports 99% accuracy when the right answer is offered but only 7%
  correct rejection when it isn't.
- Nobody has measured *boundary* behaviour: values one unit either side of the
  threshold.

**Approach.**
- Generate threshold questions over amounts, dates, durations and counts.
- Use minimal pairs (x = t−1, t, t+1) in several surface formats ($1,200 vs. 1200 USD;
  dates in ISO vs. US format).
- Measure boundary accuracy and calibration.
- Fixes:
  - (a) Inject typed numeric features: extract the numbers with code and pass the
    comparison result as a fact. This is "model judgments, code decisions".
  - (b) A small fine-tune on boundary pairs.

**Contributions.**
1. A boundary benchmark with exact labels by construction.
2. A measurement of how much accuracy the 0.6B readout loses at the boundary (likely
   chance level).
3. Evidence that code-extracted comparisons recover it almost entirely. This
   quantifies the corpus's "keep deterministic logic out of the model" advice.

**Expected results.**
- *Accuracy against distance from the threshold.*
- *Hypothesis:* near chance (50%) at ±1 unit, rising with distance. Formatting changes
  shift the curve.
- Code-extracted comparisons reach about 100% at every distance.
- The fine-tune helps in-format but transfers poorly to new formats.

**If it fails.** If the model is already accurate at the boundary, the corpus's
fixed-compute ceiling claim is overstated for threshold checks.

**Prior art to cite.** 2609.39496, ThinkJev (2610.37732), Beveridge's typed number and
date features (2611.18655), PACT (2609.35865).

**Risk.** Partly done already, so position it around the *boundary-calibration* angle.

## 8. C: Per-layer "decision lens"
**Problem.**
- Read right, act wrong (2610.18579): models read the facts and still fail to combine
  them.
- Nobody knows *where* in the network the decision forms, or whether the right answer
  appears at some layer and is then overwritten.

**Approach.**
- Apply the letter readout (final norm plus LM head restricted to the option letters)
  to every layer's hidden state, in one forward pass.
- For each item, record the "settling layer" (after which the argmax stops changing).
- Classify errors as *never right*, *right then overwritten*, or *settles late*.

**Contributions.**
1. A layer-wise taxonomy of decision errors.
2. Evidence of whether "act wrong" errors are overwrites (fixable with early exits or
   layer ensembling) or never formed (needing decomposition).
3. A cheap layer-ensemble readout as a practical by-product.

**Expected results.**
- *A histogram of settling layers* for correct vs. incorrect items.
- *Hypothesis:* a substantial share of errors are "right then overwritten" in the last
  layers, consistent with 2611.16321's finding that the final layers can be removed.
- Averaging intermediate-layer probabilities improves calibration.

**If it fails.** If errors are never right at any layer, that supports decomposition
(D, code composition) over depth-based fixes.

**Risk.** Intermediate-layer readouts are noisy. A tuned-lens variant needs a little
training.

## 9. N15: Small IRT evaluation sets for decision models
**Problem.**
- Every model variant (quantisation, LoRA, version) needs re-evaluation.
- Decision benchmarks (JevBench, TypedBench, the AA Decision Index) are large and
  change often.

**Approach.**
- Build an item-by-model correctness matrix from about 5–8 local variants.
- Fit a 2-parameter IRT model.
- Select the 50–100 most informative items.
- Predict full-benchmark accuracy *and* ECE for held-out variants.

**Contributions.**
1. The first IRT analysis of a decision benchmark: which items discriminate between
   models, and which are noise.
2. A small evaluation subset with error bars.
3. The first such subset that predicts *calibration*, not just accuracy. That is the
   new twist relative to tinyBenchmarks.

**Expected results.**
- *MAE of predicted accuracy against subset size*, for IRT vs. random subsets.
- *Hypothesis:* 100 IRT-chosen items predict accuracy within about 2 points, roughly
  matching a random subset 3–5× larger.
- ECE prediction is harder: larger error, but still informative.

**If it fails.** Inconsistent item parameters across variants would mean decision
benchmarks have low item quality. That is worth flagging for the field.

**Prior art.** tinyBenchmarks (2402.14992), MINCE (2606.22826).

**Risk.** Few models means unstable IRT fits. Use quantisations and checkpoints to
reach about 8 models.

---

# Tier 2: small fine-tunes or a few dollars of API calls

## 10. B: Nonsense option names (training for label invariance)
**Problem.**
- Typed models follow the option *name*, not the definition bound to it (2609.26758,
  2610.02586).
- Renaming the permissive option opens guardrails 93–100% of the time on models that
  feed the label to the network (2610.12292).
- That paper's cheapest fix, rewriting labels to A/B at the call site, closes the
  channel, but costs accuracy: on one policy, wrongly blocked actions rose from 25.3%
  to 36.0%. Telling the model to "ignore the names" doesn't work.
- The measured baseline flips its answer on 28.5% of items when the options are only
  reversed.

**Approach.**
- LoRA fine-tune with option labels resampled from nonsense words ("blicket", "dax",
  random strings) and in random order, bound to the real definitions. Only the
  definition carries signal.
- Add a consistency loss: symmetric KL between predictions under two label and order
  renderings.
- Treat the label as a protected attribute and report fairness-style invariance
  metrics.

**Contributions.**
1. Label invariance learned in the *weights*, so labels can stay meaningful for readers
   without being an attack surface. This is an alternative to the A/B-rewrite
   plumbing fix that doesn't cost accuracy.
2. A demonstration that label invariance can be learned cheaply (LoRA on a 0.6B model
   in about 2 hours on a laptop).
3. An invariance audit (flip rate, attack success rate, confidence gap by label
   family) as a reusable evaluation.

**Expected results.**
- *A table of clean accuracy / ECE / order-flip rate / rename-attack success rate*
  for: base model, standard fine-tune, nonsense-label fine-tune, and nonsense-label
  plus consistency loss.
- *Hypothesis:* the order-flip rate falls from 28.5% to under 5%, and rename-attack
  success drops sharply, with clean accuracy within about 1 point.
- A transfer test: fine-tune on BANKING77, evaluate the attack on held-out tasks.

**If it fails.** If invariance doesn't transfer across tasks, you've shown the fix
must be architectural (Prism-1/Jeva-style), which is useful for the field.

**Baselines.** Neutral A/B labels at inference; Runoff (2610.18233); PACT
(2609.35865).

**Risk.** Names *are* informative when definitions are terse. Include a "terse
definitions" condition.

## 11. N8: Membership inference through decision probabilities
**Problem.**
- Vendors fine-tune decision models on customer decisions, and open recipes encourage
  fine-tuning on private data.
- Calibrated probabilities are exactly the signal membership-inference attacks exploit.
- Nobody has measured privacy leakage for this model class.

**Approach.**
- Fine-tune on half of the BANKING77 training set (members); the other half are
  non-members.
- Attacks: loss/confidence thresholding, a calibrated likelihood-ratio attack with 2–3
  shadow models, and a decision-specific attack that uses *minimal-pair sharpness*
  (members' probabilities change more sharply under small perturbations).
- Defences: label smoothing, temperature, early stopping, DP-SGD at small scale.

**Contributions.**
1. The first privacy audit of typed decision models.
2. A new attack signal specific to decision readouts.
3. The privacy–calibration trade-off: does better calibration leak more?

**Expected results.**
- *MIA AUROC per attack and per defence*, plus a privacy/ECE Pareto plot.
- *Hypothesis:* AUROC clearly above 0.5 (for example 0.6–0.7) after a few epochs.
  The minimal-pair attack beats the confidence attack.
- Label smoothing lowers AUROC but hurts ECE. That trade-off is the headline.

**If it fails.** AUROC near 0.5 is a reassuring privacy certificate for small
fine-tunes, and still publishable as an audit.

**Risk.** Shadow models cost training time: about 3 LoRA runs.

## 12. N7: Watermarking a decision model against distillation
**Problem.**
- Decision APIs are cheap to distil. 2610.09188 trained a reranker from 21 minutes of
  Jev calls.
- Probabilities leak far more than text. Vendors have no way to prove a competitor
  distilled their model.

**Approach.**
- The teacher adds a small, keyed bias on a secret family of trigger states, for
  example states containing a rare token pattern, where it boosts a specific option
  by δ.
- A student trained on teacher outputs inherits the bias.
- The vendor tests a suspect model on trigger states with a hypothesis test.
- Vary δ, the trigger rarity and the amount of distillation data.

**Contributions.**
1. The first watermark for *probability-output* models.
2. Its trade-off curve: detection power against the teacher's accuracy or ECE cost.
3. Robustness of detection to student fine-tuning and to paraphrasing the triggers.

**Expected results.**
- *Detection AUROC / p-value against δ and against the size of the distillation set*,
  plus the teacher's accuracy cost.
- *Hypothesis:* detection with p < 0.01 from about 100 trigger queries, with
  under 0.5 points of teacher accuracy cost, once the student saw about 5k teacher
  labels.
- Detection weakens but survives one round of student fine-tuning on clean data.

**If it fails.** If students don't inherit small δ, you have a bound on how much
distillation copies. That's interesting either way.

**Prior art.** Watermarking for generative APIs (2302.03162) exists; not for
probability outputs.

## 13. F: Calibration collapse under recursive distillation
**Problem.**
- Decision models are trained on LLM labels, then used as judges, labellers and RL
  teachers (2609.26550, 2611.17167, 2610.09188).
- The next generation trains on their outputs. Model collapse erodes the tail of
  generative models.
- *Hypothesis:* the decision-model equivalent hides behind good aggregate calibration.

**Approach.**
- Generation 0 is the letter-logit 0.6B teacher.
- Each generation labels a fresh unlabelled pool, and a ModernBERT student is trained
  on the soft labels. Repeat for 5 generations.
- Track aggregate ECE, *class-conditional* ECE, recall and probability mass on the 20%
  rarest classes, and entropy.
- Remedies: anchoring with x% real labels per generation, proper-score training, and
  calibration by class prior.

**Contributions.**
1. Evidence of tail collapse in decision-model pipelines.
2. A diagnostic showing that aggregate ECE fails to detect it.
3. The minimum share of real labels per generation that prevents collapse.

**Expected results.**
- *A two-panel figure over generations:* aggregate ECE roughly flat, and rare-class
  recall and calibration degrading steadily.
- *Hypothesis:* noticeable rare-class recall loss by generation 3–5.
- About 5–10% real labels per generation is enough to stabilise.

**If it fails.** No collapse would be good news for distillation chains, and worth a
short paper.

**Risk.** ModernBERT on CPU takes about 30–40 minutes per generation. Use a smaller
pool if needed.

## 14. J: Bandit-budgeted optimisation of criteria text
**Problem.**
- Hosted decision models (Jev) can't be fine-tuned. Adaptation happens only through
  `state` and `criteria` text, which the docs call "prompt gymnastics".
- Decision quality is very wording-sensitive.

**Approach.**
- An LLM critic proposes edits to the criteria and option definitions.
- A bandit (UCB or successive halving) allocates the evaluation budget among candidate
  wordings.
- The objective is held-out accuracy *minus* a paraphrase-instability penalty
  (probability change under paraphrases of the criteria), so it prefers flat,
  wording-robust prompts.

**Contributions.**
1. A budgeted prompt optimiser designed for decision models, where each evaluation is
   cheap and returns a probability.
2. Evidence that the stability term reduces overfitting to the dev set.
3. A cost analysis: improvement per dollar.

**Expected results.**
- *Accuracy against evaluation budget* for random edits, greedy textual gradients,
  bandit, and bandit plus stability.
- *Hypothesis:* the bandit reaches the greedy result with substantially fewer
  evaluations. The stability term costs a little dev accuracy but gives better test
  accuracy and lower flip rate.

**If it fails.** If optimised criteria don't transfer to held-out data, that shows the
limits of prompt-only adaptation. Useful against vendor claims.

**Risk.** The critic quality matters; a local 1.7B is weak. Budget a little API usage.

## 15. E: IRT routing between fast and slow models
**Problem.**
- Confidence-gated escalation fails when the fast model is confidently wrong. Fast
  models and LLM judges reportedly repeat over 85% of each other's confident errors
  (2609.29769).
- SO-Arena finds capability and reliability disagree.

**Approach.**
- Fit IRT over state × model outcomes.
- Predict item difficulty from features of the decision state: length, position of
  the evidence, presence of numbers, number of options.
- Route each state to the cheapest model whose predicted P(correct) clears the target.
- Compare with confidence gating at the same budget.

**Contributions.**
1. Routing driven by difficulty rather than confidence for System 1/2 pairs.
2. Evidence that it catches the confident-error items that confidence gating misses.
3. An interpretable map of what makes decision states hard.

**Expected results.**
- *Accuracy against cost* for random, confidence gating, IRT routing, and both
  combined.
- *Hypothesis:* the combination dominates. The gain comes from items with high fast-
  model confidence and high predicted difficulty.

**If it fails.** If IRT adds nothing over confidence, that settles the question for
practitioners.

**Prior art.** IRT-Router (2506.01048), for LLM-to-LLM routing.

## 16. N9: Active distillation from a decision API
**Problem.**
- Narrow decision models (NDM, Beveridge) are trained from labels.
- API teachers are cheap but not free, and which states to send them matters.

**Approach.**
- Start a ModernBERT or 0.6B student on a few labels.
- Each round, send the teacher the states with the highest student uncertainty, high
  disagreement between student and teacher prior, or diversity.
- Train on the teacher's *soft* probabilities, not hard labels.

**Contributions.**
1. Acquisition rules for distilling decision models.
2. Evidence that soft probabilities are worth several hard labels each.
3. A cost recipe: dollars to reach x% of the teacher's accuracy.

**Expected results.**
- *Student accuracy and ECE against teacher calls.*
- *Hypothesis:* uncertainty plus diversity acquisition reaches 95% of the teacher's
  accuracy with a fraction of the calls random selection needs, and soft labels beat
  hard ones on ECE.

**Risk.** API cost. Use a local 1.7B teacher as a stand-in, and validate once on the
real API.

## 17. N14: Incremental decisions on edited agent states
**Problem.**
- In agent loops the state grows by small appended observations, but each decision
  re-encodes everything.
- Shared-prefix scoring (SharedKV-BT, 2610.07327) reuses context *across questions*,
  but not *across time*.

**Approach.**
- Keep the KV cache of the state from step t. At step t+1, encode only the appended
  tail, then score.
- Where edits happen mid-state, detect the earliest changed token and recompute from
  there.

**Contributions.**
1. An incremental decision protocol that gives *exactly* the probabilities of full
   recomputation.
2. A latency benchmark on realistic agent trajectories.

**Expected results.**
- *Latency per step against step index* for full vs. incremental, plus maximum
  probability deviation (target about 1e-6).
- *Hypothesis:* per-step latency becomes nearly flat instead of growing linearly.

**Risk.** It's mostly an engineering contribution. Pair it with an agent-loop
evaluation to make it a paper.

## 18. I: Fine-tuning that preserves calibration and "none fit" detection
**Problem.**
- Narrow fine-tuning costs 9–45 points of general decision ability (2611.03755).
- Calibration fails under prevalence shift (2610.26325).
- No fine-tuning protocol preserves the null/coverage behaviour.

**Approach.**
- Restrict LoRA to a subspace orthogonal to directions that matter for the base
  model's calibration set, estimated from gradients.
- Add a differentiable ECE regulariser.
- Train "none fit" on synthetic negative space: generated distractor options and
  states that match nothing.

**Contributions.**
1. A fine-tuning recipe that preserves calibration.
2. Evidence that synthetic negatives keep null detection calibrated out of
   distribution.
3. A three-way trade-off analysis: domain gain, general retention, calibration.

**Expected results.**
- *A Pareto plot of in-domain accuracy against general-benchmark retention,* coloured
  by ECE, for vanilla LoRA, replay mixing and the proposed method.
- *Hypothesis:* the method moves the front outwards. It keeps most general ability and
  calibration for a small in-domain cost, and its null-detection AUROC on held-out
  intents stays high where vanilla LoRA's drops.

**Risk.** Several objectives, so pre-register the primary metric (for example, retention
at matched in-domain accuracy).

## 19. D: Calibrated decision graphs with value-of-information labelling
**Problem.**
- Models read facts correctly but fail to combine them. Composing probe answers with
  code fixes this (2610.18579).
- Staged deployment needs to know which part of a composite decision to label next.

**Approach.**
- Express a decision as a graph of atomic judgments combined in code.
- Calibrate each node against its content-free prior, and propagate uncertainty to the
  final decision.
- Label next the node with the highest value of information *for the final decision*.

**Contributions.**
1. Calibrated composite decisions.
2. A labelling rule driven by value of information.
3. Evidence that graph composition beats a monolithic Choice in accuracy and in labels
   needed.

**Expected results.**
- *Final-decision accuracy against labels spent* for a monolithic question, the graph
  with random labelling, and the graph with value-of-information labelling.
- *Hypothesis:* the graph beats the monolithic question at 0 labels, reproducing the
  read-right/act-wrong repair, and value-of-information labelling reaches a target
  accuracy with fewer labels.

**Risk.** It needs tasks with known decomposition. Synthesise policy tasks whose rules
are known.

## 20. N13: PMI-filtered synthetic decision data
**Problem.**
- Synthetic decision datasets (LLM-generated states with labels) contain shortcuts:
  the answer is often predictable from the options or the question alone. Models then
  learn the shortcut.

**Approach.**
- Score each synthetic item by the PMI between the label and the *state* given the
  options. Low PMI means the answer is predictable without reading the state.
- Drop or down-weight those items, then train students on filtered vs. unfiltered
  data.

**Contributions.**
1. A shortcut filter for decision datasets.
2. Evidence that filtering improves gold-test accuracy and robustness at the same
   data size.

**Expected results.**
- *Gold accuracy and "shortcut accuracy"* (a model given only the options) before and
  after filtering.
- *Hypothesis:* shortcut accuracy falls and gold accuracy rises slightly, with bigger
  gains on adversarial or minimal-pair tests.

**Risk.** It needs a generator LLM to make the synthetic data (API, or slow locally).

---

# Tier 3: overnight runs or custom architecture work

## 21. A: Coherent decisions, enforced by construction
**Problem.**
- Independent heads break probability axioms: negation pairs sum to about 1.19.
- Reconstructing a fine label through its category disagrees with predicting it
  directly (total variation 0.22–0.69), and reconstruction moves CLINC150 accuracy by
  about 23 points (2609.33971, 2609.33209).

**Approach.**
- A small grammar of relationships between questions (NOT, exclusive-OR, IS-A,
  IMPLIES) is compiled into
  - (a) attention masks that share evidence only along those edges, and
  - (b) a readout where derived probabilities are *computed*.
- **Cheap version (L5):** skip the masks; just project the probabilities onto the
  coherent set in code, for example via the category hierarchy.

**Contributions.**
1. The first decision model that is coherent by construction across questions.
2. Grammar-generated coherence tests with exact ground truth.
3. Evidence that projecting onto the coherent set improves accuracy and ECE, not just
   coherence.

**Expected results.**
- *Coherence violation, accuracy and ECE* for independent heads, post-hoc projection
  and the compiled architecture.
- *Hypothesis:* projection alone removes most violations and improves ECE. The
  compiled architecture also improves accuracy on hierarchical tasks such as CLINC150
  domains to intents.

**If it fails.** If coherence and accuracy trade off, that's the deeper finding: the
models' fine-label knowledge is inconsistent with their category knowledge.

## 22. H: Unlearn the teacher so cascades work
**Problem.**
- Fast-then-slow cascades recover errors only if the slow model is right where the
  fast one is confidently wrong.
- Fast models and LLM judges reportedly share over 85% of their confident errors
  (2609.29769). Students inherit the teacher's mistakes.

**Approach.**
- Find regions where the teacher is confidently wrong, using a small gold set.
- Train a proxy classifier that flags them.
- Apply targeted unlearning or re-weighting to the student so it does *not* inherit
  those errors.
- Optimise **error complementarity** with the fallback, not standalone accuracy.

**Contributions.**
1. Complementarity as a training objective for cascade members.
2. Evidence that cascade accuracy at fixed cost improves even when the student's
   standalone accuracy doesn't.
3. A complementarity metric others can reuse.

**Expected results.**
- *Shared-confident-error rate and cascade accuracy-versus-cost curve*, for a standard
  student and a complementarity-trained student.
- *Hypothesis:* the shared error rate drops substantially, and the cascade curve
  shifts up at every budget.

**Risk.** It needs teacher labels, a gold set and several training stages. Probably
the heaviest option on the list.

---

# Quick baselines (prior art exists)

**K. PMI correction of option priors**
- Score log p(option | state) − log p(option | content-free state).
- *Expected:* it lowers order and label bias and improves ECE on the 0.6B readout.
- *Contribution:* mainly a baseline and part of the shared harness.
- *Prior art:* Surface Form Competition (2104.08315).

**N4. Label-shift correction**
- Re-estimate deployment class priors from unlabelled outputs (EM or black-box shift
  estimation) and re-weight the probabilities.
- *Expected:* restores ECE under simulated prevalence shift.
- *Prior art:* SHIFT-JEV (2610.34329) and 2610.26325, so position it as a replication
  or baseline.

**N12. Worst-subgroup calibration**
- ECE by dialect or demographic subgroup on moderation-style decisions.
- *Expected:* worst-group ECE well above average ECE.
- *Prior art:* "Fast, Cheap, and Fair?" (2611.04510) already audits Jev's fairness, so
  the *calibration* angle is what would be new.

**N6. Bandit red-teaming of typed guardrails**
- Black-box search for renamings and suffixes that flip decisions.
- *Prior art:* FlipJev (2610.38895) and JevAdvBench (2609.31142) cover this.
- Use it as the **attack** that evaluates option 10 (B).

---

## Choosing among them

| If you want… | Pick |
|---|---|
| A result in your first week, entirely on cached outputs | **2 (N5)**, **1 (G)** |
| The highest impact for the effort | **10 (B)**: label/order invariance with a crisp metric (28.5% flips); the security case is weaker than first stated, see RANKED.md |
| The cleanest "new phenomenon" paper | **3 (N1)** hub options, **6 (N3)** evidence position, **13 (F)** tail collapse |
| Security and privacy | **11 (N8)** membership inference, **12 (N7)** watermarking, **10 (B)** |
| Something the vendors would use | **1 (G)** drift fingerprints, **14 (J)** criteria optimisation, **2 (N5)** conformal labelling |
