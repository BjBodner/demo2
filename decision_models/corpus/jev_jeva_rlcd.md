# Corpus slice: TypeSafe Jev, the Jeva architecture, RLCD, and the "System One model" concept

Compiled 2026-11-18.

## Access notes (read first)

- **Network limits in this session:** WebFetch and curl could not reach arxiv.org, typesafe.ai, docs.typesafe.ai, nexos.ai, edenai.co, runware.ai, zapier.com, wavect.io, levelup.gitconnected.com/medium.com, emergentmind.com, huggingface.co or web.archive.org. All failed with DNS errors or proxy CONNECT 403. **None of the eight seed URLs could be fetched directly.**
- **What could be read in full:** GitHub was reachable via `git clone`, so I read these primary artifacts completely:
  - the official Jeva code and project site (`LiQiiiii/Jeva`), which holds the paper's headline numbers;
  - TypeSafe's official agent skill (`typesafe-ai/skills`);
  - TypeSafe's official Python SDK (`typesafe-ai/typesafe-sdk-python`);
  - the OpenJev-RLCD code/README (`ZimmyGao/openjev-rlcd`);
  - two unofficial reconstructions/showcases (`kyegomez/open-jev`, `cobusgreyling/Jev`).
- **What comes only from search snippets:** Content for the seed blog URLs, the arXiv PDFs and the TypeSafe announcement comes only from WebSearch result summaries. These are second-hand, so they are tagged **[search-snippet only]** and should be re-verified once the hosts are allowed.
- **Date correction:** Multiple sources (TypeSafe-derived model cards, reviews) date Jev's launch to **15 September 2026**, not Oct–Nov. The Jeva paper (arXiv 2610.18773) is listed by an aggregator as published 13 Oct 2026.
- **Tag legend:** **[official]** is TypeSafe-authored. **[verified-code]** I read the code myself. **[vendor claim]** is a marketing or performance claim from TypeSafe. **[author-reported]** is a paper's own number, not independently replicated. **[third-party]** is outside commentary or testing.

---

## Sources

### 1. Jeva: System One Models from First Principles (arXiv:2610.18773)
- **URL:** https://arxiv.org/abs/2610.18773 (not fetchable here). Project page and code: https://github.com/LiQiiiii/Jeva (read in full: README, `site/index.html`, `src/`). Weights: https://huggingface.co/LIQIIIII/Jeva-4B (not fetchable).
- **Date:** arXiv listing 13 Oct 2026 (per aggregator). Repo last commit 17 Oct 2026.
- **Type / author:** Paper plus official code. Qi Li and Xinchao Wang, National University of Singapore. Not affiliated with TypeSafe; it is an open "native" System One architecture positioned against Jev.
- **Problem framing:** It names four structural requirements for a decision model: **permutation invariance**, **option scalability**, **null awareness** and **computational reuse (cacheability)**. Slogan: "Encode independently. Decide collectively. Reuse what stays the same."
- **Architecture [verified-code]:**
  - **Encoder:** a shared encoder (Qwen3.5-4B with LoRA r=64, last-token pooling, projected to 768-d) embeds the request state and **each option independently**.
  - **Decision stack:** one matrix decision block by default (`decision_depth=1`, 8 heads). Only the state vector is updated. It cross-attends over the set of option vectors with L2-normalised queries/keys (cosine attention), a learned set temperature τ_set, and a residual gate α = τ_set·σ(γ)/√depth. It uses identity-initialised Q/K/V/O, a zero-initialised SwiGLU FFN, and has **no positional input on options**.
- **Readout [verified-code]:**
  - Candidate scores are the dot product of the refined state with each option's read vector.
  - Conditional choice is `q = softmax(scores/τ_dec)`.
  - **Coverage** = `sigmoid((max_score − b)/τ_cov)`, so `p_null = 1 − coverage` and `p_candidates = coverage·q`. "Competition is not coverage": relative preference and answer availability are modelled as separate quantities.
- **Typed interface [verified-code]:**
  - `Choice(criteria, allow_null)` returns a key or `None` with an explicit null probability.
  - `Noul` is implemented internally as a two-option Choice over `["false","true"]`.
  - `Score` is a Choice over rubric levels, with the returned score being the expectation over user-supplied `values`.
  - All three reuse one decision head.
- **Training objective [verified-code, fine-tune path]:** supervised soft-target cross-entropy over candidates, `−Σ target·log q`, plus binary cross-entropy on the coverage logit when `allow_null`. Labels can be `target_index`, `target_probs` (null first), `p_true` or `score`. **There is no RL here.** Jeva does not use RLCD.
- **Reported results [author-reported, from project site]:**
  - Accuracy: Typed Test 78.30% (Jev-1.13.0: 74.10). BANKING77 K=16: 91.62 (Jev 82.50). MASSIVE K=16: 90.22 (Jev 81.61). Mind2Web cross-task: 79.99 (Jev 66.26).
  - Null detection: AUROC 98.66% on BANKING77 K=16. Search snippets add ~5% false negatives on answer-present requests and ~94% detection of answer-absent requests.
  - Order stability: "**0 flips** under tested permutations" on 600 Choice items, versus "Jev-1.13.0 flips on 17.00% of Choice items and achieves 66.67% all-order accuracy."
  - Scaling: 2,048 options in one set (ToolRet diagnostic) at 69.88% all-size accuracy and 12.04 s p50 latency.
  - Cache reuse: p50 falls from 93.1 → 46.6 ms (~2×) on 2,000 Typed requests, and 99.2% of candidate encodings are avoided. On MLDR, p50 drops 2,102.0 → 75.1 ms at full reuse (27.98×), with priming excluded.
- **Stated limitations / notes:** Timings exclude separately measured priming. The evaluation datasets are "to be released separately". The numbers have not been independently replicated. Score items are excluded from permutation metrics because rubrics are ordinal.
- **Use cases:** intent classification, tool/policy retrieval-as-choice, web-action selection (Mind2Web), long-document decisions.

### 2. TypeSafe official agent skill, "Build with TypeSafe" (SKILL.md)
- **URL:** https://github.com/typesafe-ai/skills/blob/main/skills/typesafe-ai/SKILL.md (read in full)
- **Date / type / author:** last commit 23 Oct 2026. Official docs (agent skill), TypeSafe AI.
- **Definition:** "TypeSafe's **Jev**, the first public **System One model**, answers typed questions about state your application supplies."
- **Primitives:** **Choice** (among options), **Noul** ("the probability that a statement is true"), **Score** (levels you describe) and **Box** (locates something in an image; newer, image-capable). Every answer is "typed data with calibrated probabilities."
- **Design philosophy:** "Judgments from Jev, decisions in code." Treat each decision as a **truth table** whose inputs Jev supplies and whose logic lives in code. A question like "Should this ticket be escalated?" is "at the wrong layer".
- **Independence of questions:** "Questions in a request can't see each other or each other's answers." The state is read and paid for once, and questions "run in parallel". It recommends **speculative fan-out**: ask conditional follow-ups up front and let code read them only when needed.
- **Null handling:** "A Box always returns a location and a Choice always picks an option, even when nothing fits." The skill says to pair either with a Noul ("As of Jev 1.14, this companion Noul usually works better than a 'none of the above' option").
- **Calibration semantics [official]:**
  - "Confidence measures how concentrated an answer's probability distribution is, which is not the same as how likely the answer is to be correct."
  - "A probability is the likelihood that an answer is correct."
  - Default Noul thresholds are 0.7 and 0.3, with the middle band treated as "not settled". A Noul near 0.5 "usually means the state doesn't settle the question".
  - The Score expectation "can get pulled toward the middle and hide two-peaked answers", so inspect the level distributions.
- **Option naming:** "Option names are sent to the model; question IDs are not." Positional names (`A`, `option_1`) "can bias the answer". Shared wording between options "can pull probability toward those options".
- **Anti-patterns ("prompt gymnastics"):** criteria naming test items, thresholds fitted to cases, tests asserting exact probabilities. Do arithmetic, dates and exact lookups in code.
- **Use cases (cookbooks):** route and fill arguments; "select instead of generate" (code proposes candidate spans, the model picks one); find and judge evidence (re-ranking, RAG passage classification); composite scoring and feature discovery; verify-and-escalate cascades.

### 3. TypeSafe Python SDK (wire schema)
- **URL:** https://github.com/typesafe-ai/typesafe-sdk-python (read `README.md` and `_schemas/models.py`)
- **Date / type / author:** last commit 14 Oct 2026. Official SDK/docs, TypeSafe AI.
- **Interface [verified-code]:** `client.system_one(state=..., questions={name: Choice|Noul|Score|Box})` maps to `POST /v1/systemone`. State can be a JSON object, text or images.
- **ChoiceAnswer:** `choice` ("name of the choice with the highest probability"), `confidence` (0–1, "use lower values to flag uncertain selections for review") and probabilities.
- **NoulAnswer:** only `noul`, the "Probability of a yes answer or a true statement ... values near 0.5 indicate uncertainty." **There is no confidence field.**
- **ScoreAnswer:** `score`, the "Expected score: the probability-weighted average of the rubric levels. May fall between integer levels". It also returns `confidence` and an integer-keyed probability map.
- **BoxAnswer:** box edges as image fractions, plus `confidence` (nullable).
- **Usage:** reports `input_tokens` and `output_tokens`, with "Output tokens are currently free of charge". The existence of an output-token count hints that some token-level decoding exists internally; this is not documented.
- **NoulCriteria:** optional `true`/`false` descriptions, so a "no" can be defined as a concrete situation.

### 4. TypeSafe launch announcement, "Introducing System One models and Jev" [not fetched; search-snippet only]
- **URL:** https://typesafe.ai/blog/introducing-system-one-models-and-jev
- **Date / type / author:** 15 Sep 2026. Official blog, TypeSafe AI. Co-founder Diogo Almeida, described in coverage as a ChatGPT co-creator. A $40M seed round led by DCVC was reported.
- **Concept:** "System One" refers to Kahneman's fast/intuitive System 1. Jev is positioned as **complementary** to LLMs (System 2), not a replacement.
- **Claims [vendor claim]:**
  - 70–500 ms end-to-end. 40–200× faster on "System One-shaped" queries.
  - Headline "193.6× faster / 444.6× cheaper", which TypeSafe itself calls "on the higher end" of real-world gains.
  - "Cannot hallucinate" and 0% type errors, meaning by construction it cannot output a label outside the schema.
- **Mechanism as described in secondary coverage:**
  - It is "non-autoregressive", with a "parallel sampler" evaluating all questions against one state in a single pass.
  - Choice cardinality goes up to 255. Higher cardinality uses a "two-stage score-then-choose" system.
  - Training method: **RLCD (Reinforcement Learning for Calibrated Decisions)**, positioned against RLHF (preferences) and RLVR (mechanically verifiable answers), aiming at "epistemically honest probabilities".
- **Not disclosed (per multiple critics):** no paper, no architecture details, no reliability diagram or ECE, and no ablation separating RLCD from the architecture.

### 5. Jev model card and "jaggedness" page, as mirrored by a community showcase (cobusgreyling/Jev)
- **URL:** https://github.com/cobusgreyling/Jev (read `README.md`, `docs/WHAT-PEOPLE-MISS.md`, `data/model-card.json`, `data/jaggedness.json`, `data/claims.json`). It cites https://docs.typesafe.ai/models and https://docs.typesafe.ai/model-jaggedness/jev-1.13.
- **Date / type / author:** last commit 10 Oct 2026. Third-party "unofficial" repo by Cobus Greyling that transcribes official docs, so treat it as second-hand official content.
- **Model specs (Jev 1.13):**
  - ID `jev-1.13.0`, with aliases `jev-latest` and `jev-preview`.
  - 64k tokens per request, of which 32k is for state plus the longest question.
  - Text/JSON input only (images arrived later with Box).
  - $0.042 per million input tokens; output free. Rate limits 250k tokens/s and 1,200 requests/min.
  - **No fine-tuning**: "Same RLCD weights for every account."
- **Official "jaggedness" (known weak spots) for Jev 1.13:**
  - literal reading;
  - math, counting and numeric precision;
  - date comparison;
  - multi-hop indirection;
  - context rot from large irrelevant state;
  - adversarial content;
  - criteria that contradict the instructions;
  - **structural invariants are not guaranteed**: "Do not assume P(yes)+P(not yes)=1 across two Nouls";
  - generation.
- **Fan-out economics [vendor claim, via cookbook]:** 13 questions in one call versus 13 calls was "12.2× cheaper, 10× faster, same answers."
- **Claim nuance:** latency evals were "generally run from West Coast laptops". Workflow-eval reference answers are averages of GPT-6 Astra and Fable 5.1.

### 6. Open Jev: an unofficial from-first-principles reconstruction (kyegomez/open-jev)
- **URL:** https://github.com/kyegomez/open-jev (read README and `open_jev/main.py` in full)
- **Date / type / author:** 20 Sep 2026. Third-party code (Kye Gomez), random weights. "Details such as the encoder design, query slots, ordinal head, confidence objective, and training recipe are **hypotheses**, not disclosed details."
- **Hypothesised architecture:**
  - The decoder is deleted. The design is a **bidirectional state encoder** with structural path embeddings for nested JSON, a cached state, learned **query slots** per question that cross-attend into the frozen state, and typed heads.
  - Attention rules: questions attend to the state, but the state does not attend to questions and questions do not attend to each other.
  - Cost: state is O(T²d), paid once; each question is O(M·T·d) with M ≈ 8 slots, "~free".
  - Trade-off: "the state representation cannot anticipate the question, which is a real accuracy ceiling on long states with narrow questions."
- **Heads:**
  - Noul is a sigmoid with a learned temperature.
  - Choice is a **bi-encoder over runtime options**: "the softmax support IS the declared option set", so type errors are impossible.
  - Score is a **CORAL ordinal head** with monotone cumulative thresholds, and the reported score is the expectation.
  - A separate **evidential (Dirichlet) confidence head** computes confidence = 1 − K/S. The design separates aleatoric probability from epistemic confidence.
- **Hypothesised RLCD (`RLCDLoss`)**, a weighted sum of five terms:
  - soft-target NLL (1.0);
  - Brier (0.5);
  - symmetric-KL **consistency** between augmentations such as paraphrases, shuffled JSON keys and permuted options (0.5);
  - evidential confidence matched to target agreement, **with stop-gradient on the probabilities** (0.2);
  - a differentiable soft-binned ECE penalty (0.1).
  - Targets are soft: "NEVER train on hard labels". They come from a frontier ensemble sampled across paraphrases, option orders and temperatures, as in "If ten samples split 7/3, the target is 0.7."
  - Caveat noted by the author: "distillation caps you at the teacher, and inherits the teacher's biases."
- **Stated limitation:** "typed output prevents schema violations; it does not guarantee that a prediction is correct. Calibration must also be measured again under distribution shift."

### 7. OpenJev-RLCD: A Working RLCD Implementation (arXiv:2609.38850) and PRDO manuscript
- **URL:** https://arxiv.org/abs/2609.38850 (not fetchable). Code: https://github.com/ZimmyGao/openjev-rlcd (README read in full).
- **Date / type / author:** arXiv v1 16 Oct 2026 per the README changelog; last commit 3 Nov 2026. Paper plus code, ZimmyGao. Third-party, not TypeSafe.
- **Operationalisation of RLCD for reasoning LMs:** "calibrate, then reinforce".
  - **Stage 1, PRDO (post-rationale distribution optimisation):** sample M=4 rationales and read the next-token distribution `u` over answer options at `Answer:`. Minimise the negative strictly proper score: Brier `2u_y − ||u||²` or log `log u_y`, averaged over rationales, plus a token-level KL anchor (λ=0.01). "Gradients flow through the readouts and the anchor only. The rationales get no reward."
  - **Stage 2:** REINFORCE on rationales, using the proper score of the model's own readout as reward (score-function weight 0.3, leave-one-out baselines, KL β=0.04 to the stage-1 model).
- **Key argument:** with GRPO/outcome rewards, "expected reward is linear in u, so it is maximized by putting all probability on one answer" (mode-seeking, which destroys calibration). Scoring the *mixture* of readouts would reward inter-rationale disagreement that a single deployed query never shows.
- **Results [author-reported]:** Qwen3-1.7B, 3 seeds, temperature-scaled, comparing GRPO+KL+TS with RLCD two-stage.
  - GSM8K-Verify: accuracy 91.8 → 92.2, Brier 0.150 → 0.135, AURC 0.067 → 0.034, oracle Cov@5% 10% → 81%.
  - MMLU-Pro: accuracy 42.4 → 47.7, Brier 0.753 → 0.658, AURC 0.481 → 0.304, Cov@20% 0% → 28%.
  - PRDO-Brier vs GRPO+TS on 4 backbones (MMLU-Pro): Brier 0.068–0.080 lower, AURC 0.106–0.161 lower, accuracy +2.6–4.1 points (Holm-adjusted p<0.05).
- **Stated limitations:**
  - Coverage numbers are "oracle" (thresholds chosen with test labels).
  - The 0.6B model loses accuracy on some transfers.
  - Collapsed-rationale runs are excluded.
  - Per search snippet: when uncertainty comes from annotator disagreement (ChaosNLI), RLCD "provably cannot beat cross-entropy".

### 8. Evaluating and Benchmarking the System One Model Jev (arXiv:2609.37647) [search-snippet only]
- **URL:** https://arxiv.org/abs/2609.37647
- **Date / type / author:** Sep 2026. Paper (independent evaluation). Tobias Deußer, Rajkumar Ramamurthy, Lorenz Sparrenberg and Rafet Sifa (University of Bonn), per snippet.
- **Setup:** Jev 1.13.0, zero-shot on 37 datasets (classification, routing, moderation, rubric scoring). About 346k requests for under $10, with one frozen template per dataset.
- **Agentic use:** used as a step-wise action chooser, it completes 35% of ALFWorld unseen tasks, 42% of 90 TextWorld games and 21% of BabyAI-Text missions.
- **Calibration:** choice probabilities were "well calibrated and support selective prediction".
- **Weak areas:** all compared models degrade on low-resource languages, fine-grained or noisy labels, and rubric-based quality judgments.
- **Related:** "Jev in Medicine" (arXiv 2609.34024) reports weaker discrimination on DiagnosisArena-MCQ.

### 9. Releasing the Inner Jev: A Simple Recipe for Open Decision Models (arXiv:2610.17205) [search-snippet only]
- **URL:** https://arxiv.org/abs/2610.17205
- **Date / type / author:** Oct 2026. Paper. Authors not captured in snippets.
- **Training-free readout:** reading letter-token logits at the last position of open instruction-tuned LMs gives Gemma 4 31B 79.6 on OpenDecisions, versus Jev 80.1.
- **Simple supervised recipe:** LoRA plus a decision head "initialized from a slice of the LLM head". It reports 84.4 on OpenDecisions and 81.5 on JevBench v1.7, "outperforming Jev by 4.3 and 4.4", with "lower calibration error" than Jev.
- **Implication:** no specialised architecture and no RL are needed for competitive single-pass decisions.
- **Related open work (snippets):** LLM-as-Jev (arXiv 2610.02076) and Large Decision Models (arXiv 2610.15501).

### 10. Benchmark-claim coverage: the vendor multipliers versus outside measurements [search-snippet only]
- **URLs:**
  - https://fourweekmba.com/ai-typesafe-jev-444x-cheaper-193x-faster-claim/
  - https://capitalandcompute.net/blog/typesafe-jev-system-one-models-cost-use-cases/
  - https://pasqualepillitteri.it/en/news/16460/typesafe-jev-chatless-ai-beats-claude
- **Date / type:** Sep–Oct 2026. Third-party blogs.
- **The 193.6×/444.6× figures [vendor claim]:**
  - They come from 4 TypeSafe-built workflows (security incidents, agent-trace observability, invoice processing, customer service), equally weighted.
  - The **reference labels are the average of GPT-6 Astra and Fable 5.1, not ground truth**.
  - TypeSafe acknowledges the workflows were made by its own capabilities team.
  - Reports disagree on whether the baseline is an average or Claude Sonnet 5/Opus 5.
- **Accuracy:** one report puts Jev at 67.8% versus GPT-5.6 Terra at 67.9% on those workflows. Against Terra the advantage is "25× faster, 76× cheaper".
- **Outside measurements:** cost advantages of 8.6×, 45×, 58×, 274× and ~580× in five external tests. In Every's writing check, Jev caught 6/7 planted defects versus 7/7 for Fable 5.1. No independent replication of the headline figures existed as of early Oct 2026.

### 11. Calibration debate: independent ECE measurements [search-snippet only]
- **URLs:**
  - https://wotai.co/blog/typesafe-jev-vs-claude-haiku-tested
  - https://newsletter.victordibia.com/p/how-jev-works-calibrated-decision
  - https://www.dsebastien.net/reinforcement-learning-for-calibrated-decisions-rlcd/
  - https://agentconn.com/blog/jev-typesafe-new-agent-layer-if-calibration-holds
  - https://arxiv.org/pdf/2610.06625
- **Type:** third-party tests, commentary and one paper. Sep–Oct 2026.
- **Reported ECE values (varying test sets):**
  - 0.0588 on 662 prompt-injection messages;
  - 0.121 in another test, about the same as Claude Haiku and roughly 2× Sonnet 5 (0.062);
  - another benchmark: Jev 0.066 vs Gemini 3.1 Flash Lite 0.061 vs Claude Haiku 4.5 0.067.
  - Takeaway: calibration is **not clearly a moat**.
- **Doc-derived caveats (via dsebastien):** Score outputs are "weak in numerical calibration", and a question and its negation can sum to 1.19. TypeSafe docs say calibration is a group-level property and does not guarantee any individual prediction.
- **Third-party descriptions of RLCD (not from TypeSafe):** "replaces the binary (+1/0) rewards with Proper Scoring Rules (like the Brier Score) and a batch calibration penalty."
- **Paper 2610.06625 (political-science replications):** calibration measured on TypeSafe's own data may not transfer.

### 12. What is Jev and how to use it? (nexos.ai) [not fetched; search-snippet only]
- **URL:** https://nexos.ai/blog/what-is-jev/
- **Type:** third-party blog from an AI-gateway vendor. Date not captured.
- **Content:** names the production version as Jev-1.13.0 with a rolling `Jev-latest` alias, and walks through a decision call (typed questions → probabilities) routed through the nexos.ai gateway. Gateway pitch: task-based routing, per-team cost attribution, budgets.
- **Caveat it repeats:** the multipliers cover four selected workflows, and the reference-model choice biases results.

### 13. Jev: a new kind of AI model built for decisions, not conversation (Eden AI) [not fetched; search-snippet only]
- **URL:** https://www.edenai.co/post/jev-a-new-kind-of-ai-model-built-for-decisions-not-conversation (docs: https://www.edenai.co/docs/v3/llms/decisions)
- **Type:** third-party blog and docs from an API aggregator.
- **Content:** "takes program state plus typed questions and returns structured decisions with calibrated probabilities in a single parallel pass." Model ID `typesafe/jev-latest` on a "decisions" endpoint. A worked example uses Jev as a **model router** (Jev classifies the request; Eden runs it on the chosen LLM).

### 14. TypeSafe Jev model page (Runware) [not fetched; search-snippet only]
- **URL:** https://runware.ai/models/typesafe-jev (docs: https://runware.ai/docs/models/typesafe-jev.md, plus a separate Jev 1.14 page)
- **Type:** third-party docs from an inference provider.
- **Content:** served through "compatible endpoints" (another provider's request format), with model ID `typesafe:jev@1`. The Jev 1.14 page lists $0.042 per million input tokens. Confirms a **Jev 1.14** release exists.

### 15. Zapier blog, "Jev" [not fetched; search-snippet only]
- **URL:** https://zapier.com/blog/jev.md
- **Type:** third-party blog (Zapier).
- **Content:**
  - "a decision-making AI model that's not an LLM, can't chat, and can't hallucinate".
  - A fast, cheap component for routing, classification steps and safety filters.
  - TypeSafe is a San Francisco lab that came out of stealth on 15 Sep 2026.
  - Zapier exposes Jev actions via Zapier MCP and an SDK.
  - The snippet notes the post was still short and being filled in.

### 16. Jev AI decision model review (Wavect) [not fetched; search-snippet only]
- **URL:** https://wavect.io/blog/jev-ai-decision-model-review.md
- **Type:** third-party review based on reading the Jev 1.13 docs. Explicitly "not an independent latency benchmark or a production deployment".
- **Content:** names **model routing** as the strongest near-term use, with route lanes of deterministic code / fast LLM / reasoning LLM / human review. Recommends pinning the model version because `jev-latest` moves.
- **Related skeptical piece (Amplitude, https://amplitude.com/blog/jev-analysis.md, snippet):** expensive LLMs were more accurate, and Jev **agreed with a frontier model more often than with ground-truth labels**, which is consistent with distillation from LLM references.

### 17. What If AI Stopped Talking? Inside Jev, System One Models, and RLCD (Level Up Coding) [not fetched; search-snippet only]
- **URL:** https://levelup.gitconnected.com/what-if-ai-stopped-talking-inside-jev-system-one-models-and-rlcd-9089d0c265cf
- **Type:** third-party blog (Medium).
- **Content:**
  - Argues software needs decisions, not text.
  - Gives a **thresholding example** where confidence decides automate / verify / human review.
  - Describes RLCD as rewarding that "the probability you give must match your actual hit rate", which is calibration rather than human preference.
  - Another snippet in the same cluster calls Jev "a non-generative 'System One' classifier using parallel constrained decoding and RLCD calibration". That is interpretation, not a disclosed fact.

### 18. Jev and System One Models: Finding Their Place in the Agentic AI Era (Level Up Coding) [not fetched; search-snippet only]
- **URL:** https://levelup.gitconnected.com/jev-and-system-one-models-finding-their-place-in-the-agentic-ai-era-cabd99d5230a
- **Type:** third-party blog (Medium, member-only).
- **Content:** a practical guide to integrating System One models into agents, comparing accuracy, latency and cost with LLMs. Snippets from the result cluster add:
  - an independent 77-intent test (Jev 79.0% vs two OpenAI models at 83.9% and 86.2%);
  - the framing that LLMs are System 2 and Jev handles quick judgment calls;
  - advice against letting Jev alone make irreversible, high-cost decisions.

---

## Idea atoms

1. **Option-set softmax as a type system.** Normalising a classifier's output only over the option set declared at runtime (embedding the options and scoring each one against the state) makes schema-invalid outputs unrepresentable. This removes parse failures by construction rather than by constrained decoding. [2, 3, 6, 1]
2. **Encode options independently, then decide jointly.** Encoding the request and each candidate with a shared encoder, then letting only the request state attend over the set of candidate vectors, keeps option computation reusable across requests. Decisions can still depend on the set, for example when adding an alternative flips the preference between A and B. [1]
3. **Permutation symmetry by construction.** Removing positional information from the candidate pathway and scoring every candidate with one shared function makes output probabilities permutation-equivariant. Position bias is eliminated structurally rather than mitigated by augmentation or debiasing. [1]
4. **Coverage versus competition.** A separate "coverage" probability (whether any acceptable candidate exists, e.g. a sigmoid of the max candidate score) multiplied by a conditional softmax gives an open-set decision. "None apply" becomes a calibrated outcome instead of an extra option that competes for mass. [1, 2]
5. **A companion yes/no probe for null detection.** When a selection head must always pick something, a parallel binary "does anything fit?" question supplies the abstention signal. The official guidance says this works better than appending a "none of the above" option. [2]
6. **Question-blind state caching.** Encoding the context once, question-blind, and answering each query through a few learned slots that cross-attend into the cached representation makes the marginal cost of an extra question nearly constant. The price is that the state cannot specialise to the question, which caps accuracy on long contexts with narrow questions. [6, 5, 2]
7. **Information-flow isolation between parallel queries.** Folding questions into the batch dimension, so they see the shared state but never each other, makes answers order-independent and parallel. Any inter-question dependency must then be handled by explicit multi-call orchestration in code. [6, 2]
8. **Speculative fan-out.** When queries are nearly free relative to encoding the context, asking conditional follow-up questions up front and letting code read them only when a gating answer fires removes round-trips. It is a branch-prediction-style trade of cheap compute for latency. [2, 5]
9. **Model judgments, code decisions.** Decomposing a decision into atomic perceptual judgments that a model answers, and putting the combination logic (truth table, weights, thresholds) in deterministic code, makes the policy auditable and testable. It also lets weights change without re-querying the model. [2, 5]
10. **Proper scoring rules as RL reward.** Rewarding a probabilistic readout with a strictly proper score (Brier or log) makes truthful belief reporting the optimal policy. Outcome-correctness rewards are linear in the predicted distribution and therefore push it to collapse onto one answer. [7, 11, 17]
11. **Calibrate the readout, then reinforce the reasoning.** First optimise the post-rationale answer distribution with a proper score while giving the rationale no gradient, then run policy-gradient on rationales with the calibrated readout's own proper score as reward. This avoids the overconfidence that outcome-reward RL induces. [7]
12. **Score single-sample readouts, not mixtures.** When a deployed system makes one query per item, applying the scoring rule to each per-rationale readout (rather than the average over rationales) aligns training with deployment. It avoids rewarding inter-sample disagreement that a single query never exhibits. [7]
13. **Soft targets from ensemble disagreement.** Training against soft probability targets derived from a teacher ensemble's vote split across paraphrases, option orders and temperatures (7/3 → 0.7) supplies a cheap calibration signal without outcome labels. It caps the student at the teacher's knowledge and biases. [6, 10, 16]
14. **Consistency regularisation over semantic-preserving perturbations.** Penalising divergence (e.g. symmetric KL) between predictions on paraphrased states, shuffled JSON keys and permuted options directly targets order and position bias and input-format sensitivity in discriminative heads. [6]
15. **Separate aleatoric probability from epistemic confidence.** An evidential (Dirichlet) head trained with stop-gradient on the class probabilities distinguishes "genuinely 60/40" from "the model doesn't know". The confidence objective cannot blur the prediction it describes. [6, 2, 3]
16. **Concentration is not correctness.** A confidence score computed from distribution peakedness is a different quantity from the probability of being correct. Gating automation on peakedness alone conflates the two, so routing should use calibrated probabilities and task-specific calculations over them. [2, 3, 5]
17. **Ordinal heads with expectation readout.** Modelling rubric scores with monotone cumulative thresholds (CORAL-style) and reporting the expected level keeps the rubric's ordering in the loss. The expectation can hide bimodal distributions, so downstream code should inspect the level probabilities. [6, 2, 3]
18. **A differentiable calibration penalty.** A soft-binned ECE term added to a proper-scoring loss directly optimises the group-level confidence–accuracy gap. Because ECE is a group statistic, it gives no per-instance guarantee and can be gamed by bin structure. [6, 11]
19. **Single-pass logit readout from instruction-tuned LMs.** Reading the next-token distribution over option letters at the final position turns an off-the-shelf LM into a single-pass decision model. A short LoRA plus a decision head initialised from a slice of the LM head can match a proprietary specialised model. This suggests the capability is latent and the gain comes from the readout, not the architecture. [9, 11]
20. **Selective prediction as the calibration payoff.** Evaluating calibrated decision models by risk–coverage (AURC, coverage at an error budget) measures the operational value of probabilities: how much can be automated at a fixed error rate. Thresholds should be set on a held-out calibration split, not on test labels. [7, 8, 17]
21. **A two-stage score-then-choose design for large option sets.** Scoring candidates independently and then choosing among a shortlist lets a fixed-cost decision head scale to hundreds or thousands of options. It mirrors retrieve-then-rerank with a shared per-candidate scorer. [4, 5, 1]
22. **Reusable option memory with layer-specific K/V caches.** Caching each option's vector and its projected keys/values per decision layer lets newly assembled candidate subsets reuse prior computation. Decisions are still recomputed fresh, giving large latency gains on recurring candidate banks without caching answers. [1]
23. **Model-generated reference labels inflate apparent quality.** Benchmarking a distilled decision model against the averaged judgments of frontier LLMs measures agreement with the teacher rather than correctness. This is evidenced by higher agreement with frontier models than with ground truth. [10, 16]
24. **Select instead of generate.** Converting extraction into choice (code proposes candidate spans or values, the model picks one, code copies or normalises it) keeps a non-generative model useful for extraction tasks while preserving exact-copy fidelity. [2]
25. **Structural invariants do not emerge from independent heads.** Querying a statement and its negation as two independent probability heads does not enforce P(A) + P(¬A) = 1 (observed sums like 1.19). Logical coherence must be imposed architecturally or checked in code. [5, 11]
26. **Fixed compute per query is a System-1 ceiling.** A decision model with constant per-question compute and no scratchpad fails on counting, arithmetic, date comparison and multi-hop indirection. Such sub-tasks should be offloaded to code or escalated to a reasoning model through a confidence-gated cascade. [5, 6, 8]
27. **Identity and zero initialisation for bolt-on decision blocks.** Initialising attention projections to identity, zero-initialising FFN outputs, and gating residual updates by a learned temperature-scaled scalar lets a new decision block start as a near no-op on top of a pretrained encoder. This stabilises LoRA fine-tuning. [1]

---

## Open problems / gaps

- **RLCD is undisclosed.** TypeSafe has published no paper, objective, reward definition, data description or ablation separating RLCD from the architecture. Every concrete RLCD formula in circulation (proper-score rewards with a batch calibration penalty; open-jev's five-term loss; OpenJev-RLCD's PRDO plus REINFORCE) is a third-party interpretation. The word "RL" itself may be loose: the open reconstructions are mostly supervised soft-target training.
- **Jev's architecture is undisclosed.** "Non-autoregressive", "parallel sampler" and "two-stage score-then-choose above 255 options" are second-hand descriptions. The SDK reports `output_tokens`, which hints at some token-level output and may contradict the "no decoding" framing.
- **Calibration evidence is thin and inconsistent.** No official reliability diagram or ECE has been published. Independent ECE figures range from 0.059 to 0.121 and are often no better than small general LLMs. Calibration under distribution shift and model-version drift (`jev-latest`) is unmeasured. ECE is group-level and says nothing about individual decisions.
- **Teacher-capped quality.** Vendor evals use frontier-LLM averages as reference labels, and one outside analysis found Jev agrees with frontier models more than with ground truth. If training targets come from LLM ensembles (a hypothesis), Jev inherits their biases and cannot exceed them without outcome data.
- **Order sensitivity in Jev.** Jeva's authors report Jev-1.13.0 flips on 17% of Choice items under permutation. Official guidance warns that positional option names bias answers. Jeva's structural fix has not been independently replicated.
- **Logical incoherence across questions.** Independent questions break invariants (negation pairs summing above 1). Multi-label questions forced into a Choice split probability mass.
- **Null handling.** Jev's Choice always picks something, and the official workaround is a companion Noul. Jeva's coverage head is a principled alternative (98.66% AUROC on one benchmark) but untested at scale. Open-set calibration of `p_null` is not reported.
- **System-2 gaps:** counting, arithmetic, dates, multi-hop indirection, context rot on large or irrelevant state, adversarial or injected state, and low-resource languages. Rubric-quality judgments and noisy or fine-grained labels degrade for all models (per 2609.37647). There is no mechanism for adaptive compute per question.
- **Question-blind encoding ceiling.** If the state is encoded without seeing the question (as hypothesised for Jev and true for Jeva's option side), narrow questions over long states lose accuracy. How much is unquantified.
- **No customisation path for Jev.** There is no fine-tuning and the same weights serve every account, so domain adaptation happens only through prompt-like `state`/`criteria` engineering. The official docs warn this risks "prompt gymnastics". Open models (Jeva, Inner-Jev recipes) allow fine-tuning but lack a calibration-preserving fine-tune protocol.
- **Benchmark hygiene:**
  - The headline 193.6×/444.6× multipliers come from 4 vendor-built workflows with LLM-generated references and disputed baselines.
  - Latency was measured from the vendor's region.
  - Outside cost ratios range from 8.6× to ~580×.
  - Jeva's comparisons and the Inner-Jev SOTA claims are author-reported on new or partially released benchmarks (OpenDecisions, JevBench, Typed Test).
  - Oracle coverage metrics use test labels.
- **Annotator-disagreement uncertainty.** OpenJev-RLCD reports that RLCD-style training provably cannot beat cross-entropy when uncertainty stems from label disagreement (ChaosNLI). It is unclear what "calibrated" should mean for inherently contested judgments.
- **Moat question.** Training-free logit readouts from open LMs nearly match Jev (79.6 vs 80.1 on OpenDecisions), and simple LoRA recipes exceed it. This suggests the contribution may be productisation (interface, serving, pricing) more than a new learning method. That question is open until TypeSafe publishes technical details.
- **Unverified in this corpus:** none of the eight seed URLs nor the arXiv PDFs could be read directly (network policy). Per-source bullets marked [search-snippet only] need re-verification against the originals.
