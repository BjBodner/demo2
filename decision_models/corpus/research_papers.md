# System One / Typed Decision Models: Research Literature Corpus

Compiled 2026-11-18. Scope: arXiv papers (Sept–Nov 2026) that study, evaluate, attack, or propose methods for "System One" (a.k.a. System-1 or typed decision) models (single-forward-pass models that return a typed choice, score or probability over developer-defined options, e.g. TypeSafe Jev, open Laya, Jeva), plus a few older fast/slow foundations.

## Provenance and reliability note (read first)

- **Direct fetches failed.** `arxiv.org` (abs/pdf/html), `papers.cool` and `opentrain.ai` could not be reached from this session (DNS failure / proxy 403 CONNECT tunnel refusal). So I **could not read the starting paper 2610.18579 in full**, and I could not read any paper's full text. To read the primary sources, `arxiv.org` has to be allowed in the session's network settings.
- Everything below comes from **web-search result excerpts**: arXiv abstract/HTML/PDF snippets that the search engine indexed, plus aggregator pages (alphaxiv, papers.cool, opentrain, emergentmind, hyper.ai, deeplearn.org, prismix.dev, aiweekly). Where a figure came only from a secondary summary, or sources disagreed, I say so inline. Check all numbers against the PDFs before citing them.
- Every paper listed came up as an arXiv hit (title plus ID) in the search results. I made up no IDs, authors or numbers. Where a field is unknown it is marked "not seen".

---

## A. Directly about System One models in agent loops

### Reading Right, Acting Wrong: Diagnosing Decision Failures of System One Models in Agent Loops
- URL: https://arxiv.org/abs/2610.18579 (html: https://arxiv.org/html/2610.18579v1)
- Date: submitted 13 Oct 2026 (v1; listing marks it as an initial version, with more open-model evaluations ongoing)
- Authors: Yubo Li, Ramayya Krishnan, Rema Padman (Carnegie Mellon University, the same group as JEV-as-a-Judge)
- **Problem:** When a fast single-pass decision model picks the wrong next action in an agent loop, is it misreading the state (perception) or failing to turn correctly read facts into an action (composition / sub-goal)?
- **Method (paired probes):** Each next-action question is paired with independently answered factual probes about the same state. An error is classed as "read right, acted wrong" when every probe is answered correctly but the decision is wrong. Further conditions append (a) the system's own probe answers, (b) the next sub-goal, or (c) both to the decision prompt. A further condition composes the probe answers with code where the facts fully determine the action.
- **Setup:** 17 fast systems (14 System One models plus 3 likelihood readouts of open-weight LMs) and one reasoning model as reference. Note: the snippets also refer to "14 competent fast systems", so the counts are not fully consistent. The frozen benchmark has 65,228 records (59,234 test / 5,994 dev) of agent decision states from simulated environments, customer service (tau^2-bench airline and retail), tool use, web navigation and coding (SWE-smith repository traces, 300 test states).
- **Key findings:** Most wrong actions follow correct reading, and the more accurate a system, the larger the share of its errors that take this form. For the hosted APIs, 73% (JEV) and 70% (OpenAI Decisions) of errors follow correct reading. Snippets give Eikos-27B (most accurate System One model, 0.795) 78% and Torchcast-27B 79%.
- **Repair:** Appending the system's own probe answers closes most of the gap: JEV goes from 0.791 to 0.968. Where facts fully determine the action, composing the model's own answers with code repairs the failure.
- **Sub-goal failure:** On real states the missing piece is often the next sub-goal rather than a fact. Torchcast-27B answers the sub-goal question correctly in only 60% of states, and 53% of its decision-alone errors have every fact right but the sub-goal wrong. Adding the sub-goal gives it +27.5 points, and facts plus sub-goal reach 0.832. Snippets disagree on its decision-alone accuracy (0.486 in one excerpt, "decides correctly on only 0.678 of paired states" in another), so check before citing. Eikos-27B gains 18.5 points from facts plus sub-goal (excerpt).
- **Calibration:** A section titled "Calibration differs more than accuracy" reports that calibration varies much more across systems than accuracy does.
- **Relation to System One:** This is the main diagnostic paper for the reading-vs-composition gap. It suggests that System One errors in loops are mostly integration and planning failures, and that harness-side decomposition (probes, sub-goal hints, code composition) can recover most of the lost accuracy.
- **Limitations (as visible):** It uses a frozen, offline state benchmark rather than live episodes. It is v1 with additional model evaluations pending. I could not see the full limitations section.

### System Switch: When Should a Fast Decision Model Stop and Think?
- URL: https://arxiv.org/abs/2610.09683 (code: github.com/dexmac221/system-switch)
- Date: v1 posted 7 Oct 2026. cs.AI. 14 pages, 1 figure, 4 tables.
- Author: Gian Luca Bailo (single author)
- **Problem:** In a closed loop, when should a fast typed-decision actor hand control to a slow reasoning model?
- **Method:** A fast actor makes every decision in closed-loop Doom and calls a reasoning vision-language model only when a gate opens, while the game keeps running (no pausing). Secondary coverage describes the gate as watching recent history for signals such as being unsure, stuck, blocked, looping, or finding no new area. Open System One models are served through a common llama.cpp interface.
- **Framing:** The paper treats System 1 / System 2 as a design template for agents: turn-based agents switch to the slow component on events such as lack of reward, invalid actions or repeated failures. It notes that existing benchmarks score single decisions rather than closed-loop behaviour.
- **Findings (secondary coverage, unverified):** On 900 held-out questions, deferring the least-confident 30% of decisions to the reasoner gained +0.13 [0.08, 0.18] over random deferral. The system still never found the exit (33 games, 3 seeds, 0 exits). Zero-shot decision models over-choose item collection among their errors, and accuracy, calibration and sensitivity are distinct properties.
- **Authors' own caveats:** The gains are over random deferral, not proof that the hybrid beats both components. The saving is fewer reasoner calls than deferring every decision, not lower runtime.
- **Relation:** This is the canonical closed-loop fast/slow switching study for System One models. It shows confidence-gated deferral beating random deferral, and also shows that this is not enough to solve the task.

### Actor, Judge, or Teacher? Understanding Decision Models in Long-Horizon Agents
- URL: https://arxiv.org/abs/2611.17167 (html seen in results: https://arxiv.org/html/2611.17167). Code reported at ZJU-REAL/decision-agents.
- Date: about 12–15 Nov 2026 (sources disagree)
- Authors: Haochen Liu, Qianhao Zhu, Zixuan Wang, et al. (Zhejiang University and Baidu). Details are from secondary write-ups; the arXiv abstract was not read directly.
- **Problem:** Which role suits typed decision models in long-horizon agents: acting, judging, or teaching (as RL reward/supervision)?
- **Setup:** Three decision models and three general LLMs compared as actors and judges on ALFWorld. JEV used as a teacher for GRPO on ALFWorld and WebShop.
- **Key results:** JEV-as-teacher lifts a Qwen2.5-1.5B policy from 72.8% to 82.9% on ALFWorld and from 56.8% to 71.4% on WebShop over GRPO.
- **Failure mode:** As actors, all six models are pulled away from a prerequisite sub-goal by an easier, more salient one, which echoes the sub-goal failure in 2610.18579.
- **Insight:** Weak acting does not imply weak judging. Post-hoc judging sees the consequences that acting must anticipate, so a poor actor can still be a good dense teacher.
- **Relation:** This repositions System One models from controller to reward model or verifier in training loops.

### Code Owns the Simulation, Jev Owns the Evaluation
- URL: https://arxiv.org/abs/2610.01834
- Date: 1 Oct 2026. cs.AI / cs.LG.
- Authors: Yaodong Yang, Hongyao Tang, Yi Ma, Xingyu Fan, Weixun Wang, Jinpeng Li, Tianpei Yang
- **Problem:** Which kinds of decisions can a single-pass model make, and which can it not?
- **Setup:** Jev on reflection tests, one-shot matrix games, ALFWorld, and robot control (including a "Stacker" task).
- **Finding:** Jev succeeds when the right option can be judged from what the input describes ("evaluation"). It fails when the answer depends on "simulation", i.e. predicting something absent from the input, such as an opponent's move.
- **Decomposition evidence:** Asked separately what the opponent will do, Jev usually answers correctly. It fails when one call must both simulate and evaluate.
- **Fix:** Code supplies the simulation (lookahead in ALFWorld, physics simulation in robot control), and Jev then acts as an expert controller through evaluation alone.
- **Limitations (authors):** The lookahead and simulation use an exact environment copy, which real agents may lack. Consequences that appear only after several commands need deeper search, whose cost grows quickly with the number of commands.
- **Relation:** This gives a principled boundary (evaluation vs simulation) and an architecture pattern: a code-side world model plus a System One evaluator.

### Fast Models, Slow Evidence: A Paired and Self-Audited Evaluation of System-1 Decision Models for LLM Agent Harnesses
- URL: https://arxiv.org/abs/2610.02267 (code reported: github.com/David-DL-Space/sys1-eval)
- Date: early Oct 2026. cs.AI.
- Author: Jiawei Li (per aggregator; full author list not seen)
- **Problem:** Can single-pass System-1 classifiers replace costlier LLM calls at routine harness decision points (tool choice, injection detection, RAG gating, routing)?
- **Setup:** Laya (open-weight) vs Jev (hosted) on 11 agent decision points built from 18 public sources: 7,283 base cases and 6,640 robustness variants. Paired comparisons on byte-identical inputs, Wilson intervals, exact McNemar on discordant pairs. Includes a "self-audit" of the authors' own headline claims.
- **Findings:** Jev is significantly more accurate on 9 of 11 decision points (+10.8 to +46.0 pp). Neither model beats chance on zero-shot model routing. They tie on RAG relevance gating. Laya is order-sensitive, collapses with similar candidates, and misses half of the injections embedded in documents.
- **Channel effect:** Benign false positives rise when the same text moves from user input to tool output. The effect is significant for short texts (Laya p<1e-4, Jev p=0.002, LLM p<1e-6) but not for documents (Laya p=0.34), and it vanishes with channel-native content.
- **Self-audit:** One search summary reports that an omitted pre-screen cost had inflated a headline saving (reported 23.9%, actual 4.3%). This appeared in only one summary, so it is unverified.
- **Related repo data (not the paper):** A GitHub issue reports that Laya changed 30.3% of decisions under reversed option order vs Jev 1.8%.
- **Relation:** This is the most methodologically careful harness-level evaluation. It argues for paired designs and self-auditing of cost claims.

### System1-Arena: Which Decisions Can Be Left to System 1?
- URL: https://arxiv.org/abs/2610.21244
- Date: submitted 15 Oct 2026. cs.CL / cs.AI.
- Authors: Tianyu Chen, Xinyang Liu, Ruyi An, Zhendong Wang, Mingyuan Zhou (UT Austin)
- **Setup:** The same typed decision requests go to 30 models: 7 closed LLMs, 13 open LLMs read at the answer token, and 10 System-1 models. About 92k questions across 105 tasks, including an "agent and action" group, plus closed-loop episodes.
- **Static result:** The largest System-1 models match or beat fast closed LLMs on non-agentic accuracy, with better-calibrated probabilities at about a quarter of the latency.
- **Closed-loop result:** Large open LLMs succeed most often (up to 32.9%), while small System-1 models rarely succeed.
- **Interface comparison:** The OpenAI Decisions API (which shares an underlying LLM with GPT-6 Luna) is faster and has a better Brier score, but lower static accuracy (68.6% vs 71.2%) and 6.1 points lower loop success.
- **Argument:** A decision inside a loop must be judged by episode outcomes, under the timing that shapes the state. Written reasoning can be so slow that the world changes before the answer arrives.
- **Relation:** This shows that static accuracy and calibration do not transfer to closed-loop success, and that interface (typed head vs generation) matters even with a shared base model.

### SO-Arena (arXiv 2611.15777): exact title not seen
- URL: https://arxiv.org/abs/2611.15777 (seen only through hyper.ai, AF.NET and aiweekly coverage)
- Date: Nov 2026
- Authors/org: National University of Singapore team (names not seen)
- **Setup:** 11 domains and five capability families, including web judgments and interactive tool-use episodes in which a simulator returns observations after each action. 21 models (16 open-weight System One models) plus two System Two references. aiweekly reports 2,919 tasks.
- **Reliability axes:** Decision stability under controlled changes to the option set, and recognising when no valid option exists (null-awareness).
- **Finding:** Top capability does not guarantee reliability: the best-capability System One model ranks 7th on reliability. System One models roughly match System Two on knowledge, sentiment and retrieval, and trail by a few points on tool use and web interaction.
- **Caveat:** Secondary sources disagree on rankings (JevAny-27B listed as 8th vs 11th; "GLiDE" named as top in one outlet only).

### When to Ask for Help: A Decision-Theoretic Account and Measurement Standard for Slow-Module Scheduling in Dual-System Vision-Language-Action Models
- URL: https://arxiv.org/abs/2610.21160
- Date: Oct 2026
- Authors: not seen
- **Problem:** When should a fast VLA policy call its slow reasoning module?
- **Method:** A router calls the slow module only when the expected Value of Intervention exceeds the query cost. One threshold rule covers fixed-ratio, fixed-budget and history-gated scheduling as special cases. The paper also contributes a measurement standard.
- **Findings:** On 929 RoboICL deployment traces, failed episodes queried the slow module about 25% less often and ran with greater staleness, varying by task category. On FiS-VLA on an RTX 4090, one slow refresh costs about as much as one fast action (52 ms vs 55 ms). Closed-loop tests use 14 arms on LIBERO-Spatial, with a 3-arm replication on LIBERO-Goal.
- **Relation:** This is not about typed-decision LLMs. It is the decision-theoretic counterpart to System Switch: it formalises fast-to-slow escalation as value of information net of cost.

---

## B. Benchmarks, calibration and evidence audits

### TypedBench: A Benchmark for Calibration, Framing Sensitivity, and Cost in System One Decision Models
- URL: https://arxiv.org/abs/2610.11392
- Date: 8–9 Oct 2026 (v2 seen on alphaxiv)
- Authors: Rahul Sharma, Andrew B. Duncan, Gaétan Marceau Caron, Sebastian J. Vollmer
- **Setup:** A hosted model, an open encoder, and several open decoders (six checkpoints) on identical items.
- **Metrics:** Accuracy reported as a median and range across paraphrases. Calibration error measured against the finite-sample noise floor of a matched, perfectly calibrated predictor. Probability quality judged through selective prediction, ordinal proper scoring rules, and realised cost under asymmetric cost matrices.
- **Hosted model:** Follows the stated policy, but is wording-sensitive and systematically underconfident. Under asymmetric costs, acting on its probabilities can be worse than taking its top answer.
- **Decoders:** Route exactly and are unaffected by co-asked questions, but apply policies only partially and slow down as options or questions are added.
- **Encoder:** Least accurate on policy questions and degrades with more options.
- **Context cited:** Independent tests reported a 33-point accuracy swing from rewording a question.
- **Conclusion:** Typed decision models must be evaluated jointly on policy adherence, wording robustness, probability quality, and the decision outcomes those probabilities induce.

### Benchmarking System One decision models against trained classifiers and language models for automated decision gates
- URL: https://arxiv.org/abs/2610.00346
- Date: 29 Sep 2026 (prismix) / 6 Oct 2026 (alphaxiv v2)
- Authors: Amir Rafe, Subasish Das
- **Setup:** Eight decision-model checkpoints vs small supervised classifiers, a zero-shot entailment classifier, and generative LMs, on intent and workflow tasks.
- **Findings:** With task labels, small trained classifiers are the most accurate on intents and not significantly different from the best decision models on workflows. Without labels, every decision model except the encoder-based checkpoints beats zero-shot NLI, and no decision model is significantly more accurate than Jev.
- **Consistency:** Swapping yes/no flipped answers far more often for Jev and generative models than for fine-tuned decision checkpoints.
- **Cascade:** An intent-trained first stage that escalates to a larger model matches that model's accuracy at 0.43 of its cost at full GPU utilisation.
- **Output:** Condition-dependent design rules for automated decision gates.

### Typed Decision Models: An Early Evidence Audit and Evaluation Checklist
- URL: https://arxiv.org/abs/2609.32160
- Date: Sept 2026 (corpus frozen 25 Sep 2026)
- Authors: not seen
- **Method:** An audit of 28 papers posted in September 2026, plus an evaluation checklist for reproducible comparisons.
- **Findings:** Efficiency gains appear in some workloads. There is no independent general accuracy advantage for the typed readout. Calibration is workload-dependent. The strongest deployment results use these models as a cheap first stage in a cascade.
- **Relation:** This is the meta-evidence baseline that later papers (e.g. TypedBench) build on.

### Jev thinks "I don't know", but doesn't say it: Introducing Sys1Cal-v1 Dataset for Probability Calibration
- URL: https://arxiv.org/abs/2609.35342 (code: github.com/little-g-ai/Sys1Cal-v1)
- Date: Sept 2026
- Authors: not seen
- **Method:** True/False questions about propositions whose exact probability P(A) is known by construction: 365 rendered examples from 92 problems, across six problem types (explicit probabilities, frequencies from counts, compound, conditional, Bayes' rule, sequential Bayesian updates), each rendered in several formats (tables, prose, counts).
- **Findings:** Jev and SemIf (an open Choice-style baseline) were benchmarked. Score and expectation-style answers stay near the identity line, while Choice answers skew toward high "True" probabilities.
- **Relation:** Calibration depends on which readout primitive (Choice vs Score) is used. Ground-truth probability targets allow calibration to be tested directly rather than through accuracy proxies.

### Evaluating and Benchmarking the System One Model Jev
- URL: https://arxiv.org/abs/2609.37647
- Date: 29 Sep 2026. cs.CL / cs.AI.
- Authors: Tobias Deußer, Lorenz Sparrenberg, Rafet Sifa
- **Setup:** 37 public datasets mapped onto Jev's three question primitives (choice, rubric position, probability), covering 7 task families and more than 200 language varieties, plus 5 text-based sequential game environments.
- **Findings (secondary summaries):** Choice probabilities are well calibrated and support selective prediction. All models degrade on low-resource languages, fine-grained or noisy labels, and rubric-based quality judgments. One snippet notes that on MMLU Jev answers calculation-heavy questions more accurately than other questions (94% vs 91%).

### Evaluating System One Models for Agent Security Decisions: Reliability, Calibration, and Selective Automation
- URL: https://arxiv.org/abs/2609.33401 (seen only through an opentrain.ai aggregator page)
- Date: Sept 2026. Authors: not seen.
- **Claim:** Classification accuracy alone does not show whether probabilities over labels such as safe/unsafe support reliable automation. High overall accuracy and low average calibration error can hide attacks classified as safe with high confidence inside particular attack groups.
- **Judge comparison:** A language-model judge can catch unsafe inputs that the System One model misses, but it can also repeat that model's confident mistakes and falsely flag benign inputs.
- **Recommendation:** Test candidates on the intended security task and examine errors within each attack group.

---

## C. Decision models as judges / graders

### JEV-as-a-Judge: Accept When Confident, Escalate When Unsure
- URL: https://arxiv.org/abs/2609.26550
- Date: late Sept 2026 (one source: 9 Oct)
- Authors: Yubo Li, Yidi Miao, Ramayya Krishnan, Rema Padman (CMU)
- **Method:** Accept JEV's verdict if the top-label probability is at or above a frozen threshold; otherwise escalate to a stronger judge, whose verdict becomes final.
- **Findings:** On preference and factuality tasks JEV stays within 3 points of GPT-6 at a fraction of the cost (one source: about $0.044 vs $12.182 per 1,000 judgments). It trails on derivation-heavy verdicts (math, code), e.g. by 14.6 points on JudgeBench. The frozen-threshold cascade retains 99% of the comparator's accuracy at lower cost.
- **Failure modes:** Confidence routing weakens on style-adversarial pairs and on reference-free prose.
- **Framing:** The contribution is an empirical operating profile, not a new routing algorithm.

### Decision Models vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places
- URL: https://arxiv.org/abs/2609.29769
- Date: Sept 2026
- Authors: Delip Rao, Chris Callison-Burch (University of Pennsylvania)
- **Setup:** Jev and an open reproduction (Perplexity's Decider) vs three flash-tier LLM judges, on 9 panels from 7 benchmarks with human judgments, with identical criterion texts for every judge.
- **Findings:** The LLM judges cost 16–357x as much and take 5–350x as long, yet each decision model trails them significantly in at most 6 of 27 comparisons.
- **Correlated errors:** More than 85% of flash LLM verdicts on a decision model's most-confident errors repeat those errors, where independent errors would give about 50%.
- **Implication:** A cascade needs a fallback that is right where the first stage is wrong. Future decision models should be designed to complement LLM judges, not to imitate them.

### Cheap, Consistent, Calibrated, but Biased? Typed Decision Models as Judges
- URL: https://arxiv.org/abs/2610.18122
- Date: Oct 2026. Authors: not seen.
- **Setup:** The CALM benchmark's 12 judge-bias tests on 8 typed decision models (TDMs) and 7 LLM judges from 2024 and 2026.
- **Findings:** Every TDM is biased on 3–8 of the 12 tests. Emotional tone has the largest effect: rewriting the better answer in that tone drops a typical TDM from 99% to 42%. TDMs are more biased than the 2026 LLM judges, but more consistent and about 37x cheaper.
- **Recommendation:** Use TDMs as judges only after task-specific bias testing.

---

## D. Robustness, option/label effects, and attacks

### Consider, Then Choose: Order-Invariant Decisions in System One Models
- URL: https://arxiv.org/abs/2610.18233
- Date: 13 Oct 2026. cs.AI / cs.CL.
- Authors: Jianguo Huang, Yao Long Teng, Yanchen Deng, Bo An
- **Problem:** Option order changes System One answers, increasingly so as the option count grows. Averaging over cyclic shifts reduces but does not remove the dependence.
- **Method ("Runoff"):** Training-free and two forward passes. First score each option on its own to shortlist a few candidates, then compare the shortlist in listings where each candidate takes every position.
- **Results:** On 2 open models and 5 datasets, 0% answer changes under shuffling vs 9.3% for cyclic averaging. With 20 options it is about as accurate and 3–4x faster. Wrapped around 8 System One models it removes order dependence, whereas cyclic averaging changes answers by up to 15.4%.

### Jeva: System One Models from First Principles (skimmed for related work only)
- URL: https://arxiv.org/abs/2610.18773 (HF: huggingface.co/LIQIIIII/Jeva-4B)
- Authors: Qi Li, Xinchao Wang (National University of Singapore)
- **Positioning vs prior work:** Prior open System One models encode the request and candidates jointly as text, which makes predictions order-sensitive and limits candidate counts. Jeva encodes the request and each option independently with a shared encoder. A compact decision stack refines only the request state against immutable option memory, and coverage (does any option fit?) is estimated separately from competition between options.
- **Design targets:** Null-awareness, permutation invariance, option scalability, cacheability. Reports no flips under tested permutations and scaling to thousands of candidates. One summary gives 69.88% accuracy at 12.04 s median latency with 2,048 candidates on one H200, on a Qwen3.5-4B backbone.
- **References visible in search snippets:** LoRA (Hu et al., ICLR); Pairwise Ranking Prompting (Qin et al., 2024, "LLMs are effective text rankers with pairwise ranking prompting"); Toolformer (Schick et al., 2023); Laya ("multilingual, non-autoregressive System 1 decision engine", non-archival); SemIf ("Semantic ifs from open models"); Kwok et al., "Contrastive language models"; and a 2026 TypeSafe AI blog post "Introducing System One Models & Jev". I could not reach the full related-work section.

### Type-Safe Is Not Error-Free: Typed Decision Models Follow the Option Name, Not the Definition Bound to It
- URL: https://arxiv.org/abs/2609.26758 (arXiv/papers.cool list the title as "A Constrained Decision Head Follows the Option Name, Not the Rubric Bound to It")
- Date: submitted 23 Sep 2026
- Authors: Yu Sun, Junhao Xu (per papers.cool)
- **Method:** Hold the question, state and rubric fixed, and change only which option name is bound to each rubric. Tested on Jev and two open Jev-like models.
- **Findings:** The type-error rate stays at 0% while accuracy degrades substantially, because models choose the option whose name matches the intended meaning rather than its definition. Names with semantic polarity drive the effect, neutral names barely do, and only yes/no falls below chance.
- **Remedy:** Report a label-free name-invariance flip rate (two extra forward passes per question) alongside the type-error rate.
- **Authors' caveat:** This does not show that names are the only cue, or that every typed model will reverse.

### Labels Override Definitions in Jev-Style Typed Decision Models
- URL: https://arxiv.org/abs/2610.02586
- Date: about 5 Oct 2026
- Authors: Seyedarmin Azizi, Erfan Baghaei Potraghloo, Massoud Pedram
- **Finding:** Removing every definition barely changes accuracy (0.8559 vs 0.8487), although definitions alone support 0.7971. Renaming options to A/B raises accuracy by +0.1511 [+0.1377, +0.1646].
- **Mechanism:** The effect is traced to how options are rendered into the input, not to the constrained decision head that earlier work blamed. Changing the rendering, with no weights changed, makes three Laya checkpoints exactly invariant and induces the effect in another model ("von").
- **Tools:** A two-call label-swap test and four measured mitigations.

### One Word Opens the Gate: The Option-Channel Attack on Typed Decision Models as Agent Guardrails
- URL: https://arxiv.org/abs/2610.12292 (code reported: github.com/ArminAzizi98/option-channel-attack)
- Date: 8 Oct 2026
- Authors: Seyedarmin Azizi, Erfan Baghaei Potraghloo, Massoud Pedram
- **Attack:** Rename the permissive option, leaving its definition and the judged text unchanged. Fail-open rises to 93–100% on the four models that place labels in their input; the two models that do not are unaffected.
- **Context injection:** Six lines of policy-irrelevant server-log text raise a gate's fail-open rate from 0% to 63% on synthetic agent tool calls.
- **Baseline weakness:** Allow/block accuracy on prompt-injection, jailbreak and toxicity screening ranges from 36% to 72% (chance 50%).
- **Defences:** Every tested defence is defeated. A secondary write-up says neutral A/B relabelling at the call site closes the option channel at some cost to fail-closed accuracy (unverified).

### Poisoned into Action: Context Attacks on Typed Decision Workflows
- URL: https://arxiv.org/abs/2610.15537
- Date: Oct 2026
- Authors: Chenkai Wu, Xing Chang, Jun Yan
- **Problem:** A schema-valid typed choice can still trigger a policy-violating state change.
- **Method:** An execution-aware protocol that traces poisoned evidence through retrieval, model choice, automated action and persisted state.
- **Setup:** 1,659 fresh calls to jev-1.13.0 across 20 development tasks in 2 synthetic workflows, with 3 repetitions per condition.
- **Finding:** Distinct gaps between exposure, harm and protection; specific numbers not seen. Related: "Decision Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions" (arXiv 2609.28613, seen but not read).

### Calibrated Decision Models for Autonomous Penetration-Testing Harnesses: JEV and Laya as System One Decision Layers for LLM-Driven Pentest Agents
- URL: https://arxiv.org/abs/2609.28940
- Date: Sept 2026
- Author: Joas Antonio dos Santos (independent researcher, São Paulo)
- **Argument:** Pentest harnesses let the same LLMs that generate findings also judge them. The paper proposes non-generative, calibrated System One verdicts at four decision points: finding adjudication, severity recalibration, agent pruning, and confirmation loops.
- **Content:** A review of published specs for Jev, Jev-Ultrafast and open-source Laya (it does not assume that other benchmarks transfer), and a discussion of training paradigms (RLHF, RLAIF, RLCD, RLHV) and their implications for trust. Mostly a position/framework paper; no experimental results were seen.

---

## E. Surveys / foundations (surfaced alongside; citation links not verified)

### The Hitchhiker's Guide to System 1 Models: Fast Decision-Making Beyond LLMs
- URL: arXiv ID not seen (mirrors: https://deeplearn.org/arxiv/859283/ and /856193/). Posted about 29 Oct 2026. Author: Haggai Roitman.
- Practitioner survey with a five-family taxonomy: encoder classifiers, reward models, non-autoregressive decision engines, contrastive decision models, extraction models. Covers 18 domains, with a checklist, a model zoo and 190 references. Discusses System 1 + System 2 cascades routed on calibrated confidence.

### Reasoning on a Spectrum: Aligning LLMs to System 1 and System 2 Thinking
- URL: https://arxiv.org/abs/2502.12470 (Ziabari et al., Feb 2025)
- 2,000 questions with paired S1/S2 responses grounded in 10 cognitive heuristics. S2-aligned models are better on arithmetic and symbolic tasks; S1-aligned models are better on commonsense tasks and use fewer tokens. S1 models are more decisive while S2 models hedge. Mixing the training data gives a smooth, monotonic trade-off. v3 adds a training-free, entropy-based S1/S2 combination. It surfaced in the System Switch search context; whether System Switch cites it is not verified.

### Think More, Hallucinate Less: Mitigating Hallucinations via Dual Process of Fast and Slow Thinking (HaluSearch)
- URL: https://arxiv.org/abs/2501.01306 (Cheng, Li, Zhao, Wen; Jan 2025)
- Tree search (MCTS) for slow thinking, guided by a self-evaluation step reward model, with a hierarchical fast/slow switch at both the instance and step level. It is an early instance of learned fast/slow switching; citation by 2026 papers not verified.

### Seen in results but not summarised (titles and IDs only)
Prism-1: Position- and Rival-Independent Scoring for System One Models (2610.22066); Calibration and Risk-Budgeted Decisions with System One Models (2610.19811; only a table on test risk/utility at alpha=0.10, FOR/TNR, was visible); System One Models for Wireless Decision-Making (2610.04345); From Retrieval to Typed Decisions: Calibrated System One Models from Biomedical Sentence Encoders (2610.02486); Benchmarking System One Models in Online Moderation (2610.07953); Jev in Medicine: A Benchmark Evaluation (2609.34024); Decision Hijacking (2609.28613); Same Attack, Different Judge (2610.17820; 8 judges including JEV 1.13.0, 5 LLM judges, Llama Guard 3 8B and Prompt Guard 2; results not seen); Is This Evidence Decision-Critical? Learning to Verify Rule-Governed Decisions (2609.39608); Label-Wording Augmentation in a Typed-Decision Encoder (2611.08439); Where Scientific Search Agents Fail: Decision-Checkpoint Auditing (2609.38670); Frozen Judges, Moving Agents (2609.34198); AgentHorizon: Evaluating Agentic Judges for Long-Horizon Computer-Use Tasks (2610.11050).

---

## Idea atoms

1. **Paired fact probes separate perception from composition.** Pairing every decision query with independently answered factual probes about the same state turns an opaque accuracy number into an error taxonomy: errors where all facts were read correctly isolate integration and planning failures from perception failures. [2610.18579]
2. **Self-generated evidence as scaffolding.** Feeding a single-pass model its own probe answers back into the decision prompt recovers most of the read-right/act-wrong gap. The model's latent knowledge is enough; what fails is combining that knowledge within one forward pass. [2610.18579]
3. **Code composition over model-extracted atoms.** When probed facts fully determine the action, extracting the atoms with the model and composing them in deterministic code repairs composition failures. Model judgment is confined to perception, and logic moves to verifiable code. [2610.18579; 2610.01834]
4. **Sub-goal as the missing latent variable.** In agent states, the decisive missing input is often the next sub-goal rather than a fact. Supplying it explicitly (or querying it as a separate decision) converts an implicit planning step into an observable, checkable one. [2610.18579; 2611.17167]
5. **The evaluation/simulation split defines single-pass competence.** A single-pass decision model does well when the correct option can be judged from information in the input, and fails when it must predict unobserved consequences. Supplying simulation externally (lookahead, physics, opponent prediction) turns it into a strong controller. [2610.01834]
6. **Decomposed queries beat fused queries.** A model that answers "what will the opponent do?" correctly in one call can still fail when one call must both predict and evaluate. Splitting a decision into sub-queries routes around the model's limited single-pass composition depth. [2610.01834; 2610.18579]
7. **Post-hoc judging is easier than prospective acting.** A judge that sees a completed episode observes consequences that an actor must anticipate, so weak actors can be strong dense reward providers. Using decision models as RL teachers exploits this asymmetry. [2611.17167]
8. **Confidence-gated escalation as a cascade primitive.** Thresholding the top-label probability of a cheap typed model and escalating only below the threshold keeps near-strong-judge accuracy at a fraction of the cost, provided confidence is informative on that task's distribution. [2609.26550; 2610.00346; 2610.09683]
9. **Cascades need error complementarity, not just confidence.** A cheap-then-expensive cascade only helps if the fallback is right where the first stage is confidently wrong. Measuring how often the fallback repeats the first stage's most-confident errors tests cascade viability directly. [2609.29769; 2609.33401]
10. **Deferral should be benchmarked against random deferral at matched budget.** Comparing confidence-based handoff to random handoff at the same deferral rate isolates the information value of the confidence signal from the benefit of simply calling a stronger model more often. [2610.09683]
11. **Value of Intervention unifies scheduling rules.** Framing fast-to-slow escalation as "call when expected improvement exceeds query cost" makes fixed-ratio, fixed-budget and history-gated schedulers special cases of one threshold rule, and gives a common way to measure them. [2610.21160]
12. **Closed-loop timing changes what a good decision is.** In environments that keep running, latency is part of correctness: a slower, more accurate decision can lose to a faster one because the state drifts. Decisions in loops should be scored by episode outcome under realistic timing. [2610.21244; 2610.09683]
13. **Static accuracy does not transfer to loop success.** Models that match or beat LLMs on isolated typed decisions can still rarely complete episodes. Benchmarks need both static and closed-loop tracks, because compounding errors and sub-goal ordering show up only in the loop. [2610.21244; 2611.15777]
14. **Interface ablation with a shared base model.** Exposing one LLM through both a typed decision head and free generation isolates the effect of the readout interface on accuracy, calibration (Brier) and loop success, separately from model capability. [2610.21244]
15. **Calibration against a finite-sample noise floor.** Reporting calibration error relative to that of a perfectly calibrated predictor on the same sample size prevents small-sample ECE noise from being read as miscalibration. [2610.11392]
16. **Probability quality should be judged by induced cost.** Evaluating probabilities through selective prediction, proper scoring rules and realised cost under asymmetric cost matrices shows cases where acting on the probabilities is worse than taking the argmax. Calibration metrics alone hide this. [2610.11392; 2610.19811]
17. **Constructed ground-truth probabilities isolate calibration.** Items whose true probability is known by construction (counts, Bayes updates), rendered in several surface formats, test calibration directly and expose readout-specific skew (Choice vs Score). [2609.35342]
18. **Accuracy and calibration should be reported per subgroup for safety gates.** Aggregate accuracy and mean calibration error can hide subgroups (attack families) misclassified as safe with high confidence, so security-gate evaluation needs per-subgroup confident-error analysis. [2609.33401]
19. **Label-free invariance flip rates as a reliability metric.** Re-querying with option names swapped, options reordered or questions paraphrased, and counting flips, measures reliability without gold labels at the cost of a few extra forward passes. [2609.26758; 2610.02586; 2610.18233]
20. **Schema validity is not semantic correctness.** Constrained typed outputs drive format errors to zero while semantic errors persist, so a type check gives no signal for errors that come from following the option name rather than its definition. [2609.26758]
21. **Locating a bias by intervening on input rendering.** Changing only how options are serialised into the input, with no weight changes, can switch label-over-definition bias on or off. This attributes the bias to input rendering rather than to the decision head. [2610.02586]
22. **Option labels are an attack channel.** When option names are rendered into the model input, the label set becomes attacker-reachable configuration, and renaming the permissive option alone can open a guardrail. Treat labels as untrusted input or neutralise them (e.g. A/B). [2610.12292]
23. **Two-stage shortlist-then-runoff for order invariance.** Scoring each option alone to shortlist, then comparing the shortlist under all positional placements, gives exact order invariance in two passes and scales better than cyclic averaging. [2610.18233]
24. **Independent option encoding with immutable option memory.** Encoding request and options separately with a shared encoder, refining only the request state against fixed option memory, gives permutation invariance by construction, allows option caching across requests, and scales to thousands of candidates. [2610.18773]
25. **Separating coverage from competition.** Estimating "does any option fit?" separately from "which option fits best?" makes abstention or null-detection a first-class output rather than a low-max-probability heuristic. [2610.18773; 2611.15777]
26. **Paired evaluation on byte-identical inputs.** Comparing two decision models on exactly the same inputs with exact McNemar tests on discordant pairs gives much tighter, more honest comparisons than independent-sample accuracy differences. [2610.02267]
27. **Channel-shift robustness tests.** Moving the same text between channels (user input vs tool output vs document) exposes false-positive shifts that depend on context position rather than content. Channel-native content is the control for this artefact. [2610.02267]
28. **Self-auditing headline cost claims.** Re-deriving one's own efficiency claims with every pipeline cost included (e.g. pre-screens) can shrink a reported saving drastically. Cost accounting belongs in the evaluation protocol. [2610.02267 (secondary report)]
29. **Execution-aware tracing of typed decisions.** Following poisoned evidence through retrieval, choice, action and persisted state separates exposure, harm and protection, so the security of a typed interface is measured by state changes rather than by output validity. [2610.15537]
30. **Bias batteries transfer from LLM judges to typed judges.** Running established judge-bias suites (e.g. CALM) on typed decision models shows that low cost and high consistency coexist with large stylistic biases such as emotional tone, so task-specific bias testing is needed before substitution. [2610.18122]
31. **Supervised small classifiers are the label-rich baseline.** When task labels exist, small trained classifiers match or beat zero-shot decision models. Zero-shot typed models are most valuable in the label-scarce regime and as escalation-capable first stages. [2610.00346; 2609.32160]

---

## Open problems / gaps

**Explicitly left open by the papers**
- **Closed-loop vs static gap.** System1-Arena and SO-Arena show that static decision quality does not predict episode success, and System Switch never reaches the Doom exit. No paper yet shows a System One plus System Two hybrid that beats both components on end-to-end task success, rather than only beating random deferral. [2610.21244, 2610.09683]
- **Learning the sub-goal.** Reading Right shows that supplying sub-goals or facts recovers accuracy, but how to produce the sub-goal cheaply at run time (without a reasoning model) is open. Actor/Judge/Teacher documents the same prerequisite-sub-goal pull. [2610.18579, 2611.17167]
- **Simulation without an oracle environment copy.** Code Owns the Simulation relies on exact environment clones, and multi-step consequences grow search cost quickly. [2610.01834]
- **Cascade fallback complementarity.** Rao & Callison-Burch show correlated errors between decision models and LLM judges. Designing decision models (or fallbacks) for complementary errors is proposed but not done. [2609.29769]
- **Defences against option-channel and context attacks.** Every defence tested in One Word Opens the Gate is defeated; Poisoned into Action reports exposure/harm/protection gaps without a fix. [2610.12292, 2610.15537]
- **Underconfidence and cost-aware use of probabilities.** TypedBench finds hosted-model probabilities can be worse than the argmax under asymmetric costs, so recalibration or decision rules for typed outputs are needed. [2610.11392]
- **Evidence base is immature.** The evidence audit finds no independent accuracy advantage of the typed readout, and many results are v1 preprints with ongoing evaluations. [2609.32160, 2610.18579]

**Gaps noticed across the corpus**
- **Mostly one hosted model.** A large share of the evidence is about Jev (often pinned at jev-1.13.0) plus Laya. I found no arXiv paper evaluating Microsoft-Decision-1 or gemini-decision-1 by name (a targeted search returned none), and OpenAI Decisions appears only as a comparator (2610.18579, 2610.21244).
- **Training is barely studied.** Almost every paper evaluates frozen models. Training objectives for calibrated decision heads (beyond Jeva's architecture and the pentest paper's discussion of RLHF/RLAIF variants), and fine-tuning System One models on loop-specific failure taxonomies, are largely absent.
- **No standard null/abstain evaluation** across papers. Null-awareness appears in Jeva and SO-Arena, but agent-loop papers rarely score "no valid option" states.
- **Interaction of robustness axes.** Order, label-name, paraphrase and channel effects are each studied in isolation. Joint effects (e.g. a renamed label in a shuffled list under injected context) and certified invariance are unexplored.
- **Learned vs heuristic gates.** System Switch uses heuristic history signals and When to Ask for Help derives a VoI rule for VLAs; learned, calibrated escalation policies for text-agent loops with System One actors are not evaluated.
- **Composition depth of a single forward pass.** Several papers show failures when one call must integrate several facts or simulate, but none measures how many compositional steps a single-pass decision head can reliably do.
- **Replication.** Aggregator-reported figures sometimes disagree (dates, rankings, the Torchcast-27B accuracies), and some reported repos have no verified official status. Independent replication is thin.
