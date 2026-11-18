# Decision models / System One models: big-lab and other entrants, plus independent benchmarks

Compiled 2026-11-18. Scope: Microsoft-Decision-1, Google DeepMind gemini-decision-1, OpenAI Decisions API, Prism-1, other System One entrants (Turing Post list and others), and independent benchmarks and comparisons. TypeSafe Jev/Jeva/RLCD appear only as comparison points; a separate corpus file covers them.

## Access note (read first)

- **Every WebFetch call failed.** The session's network policy blocks outbound page fetches (DNS `ENOTFOUND`) for pub.towardsai.net, vercel.com and www.gradually.ai, and the proxy log shows CONNECT denials for other hosts such as huggingface.co. None of the six starting-point URLs could be read in full.
- **All content below comes from WebSearch result excerpts**: short snippets plus the search engine's summaries of indexed pages. Nothing here comes from a full-page read. So:
  - numbers and quotes are as relayed in the snippets and may be cut off or out of context;
  - where a page's own text was not visible, the entry says so;
  - an entry marked "official (via secondary)" means the vendor page was cited by coverage, but its text was not seen directly.
- Treat each figure as "reported by X", to be checked against the primary page once fetch access is available.
- **Label conventions:**
  - **[V]** = vendor-reported claim.
  - **[I]** = independent or third-party measurement.
  - **[P]** = platform telemetry, not a controlled test.

---

## Sources

### 1. Introducing Microsoft-Decision-1: Fast AI for Real-Time Decisions (Towards AI)
- URL: https://pub.towardsai.net/introducing-microsoft-decision-1-fast-ai-for-real-time-decisions-e6344144ad25
- Date: Oct 2026 (exact date not visible). Type: third-party blog. Org: Towards AI (Medium publication).
- **Fetch failed** (host blocked). The page appeared only as a search-result title; none of its body text was visible. Nothing is attributed to it here.
- Related Towards AI titles also appeared in results without visible bodies:
  - "Jev's new competitor: it's Microsoft"
  - "Microsoft-Decision-1: stop parsing confidence: 0.8"
  - "Four decision models shipped in three weeks: choose wisely"
  - "How to read OpenAI's new Decisions API score: rounding can pick a level the model gave 0%"

### 2. Microsoft-Decision-1: Foundry model catalog and Tech Community launch post
- URLs:
  - https://ai.azure.com/catalog/models/Microsoft-Decision-1
  - https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-decision-1-in-microsoft-foundry-for-decision-and-classific/4562742
- Date: released 2026-10-09 (per multiple outlets). Type: official (via secondary; neither page's text was directly visible). Org: Microsoft.
- **Base model and recipe:**
  - Post-trained from Alibaba's open-weight **Qwen3.5-9B**, per the Foundry model card as cited by The Next Web and TechJack.
  - The post-training recipe itself (SFT, RL or calibration objective) is not described in any excerpt seen.
  - No standalone technical report or arXiv paper was found.
- **Interface:**
  - Input is a situation/state, a question and a fixed set of answer options. Output is a calibrated probability per option.
  - Question types: yes/no, multiple choice, rating, classification and rubric.
  - Foundry path: `providers/microsoft/v1/systemone`. The request's `model` field is the user's deployment name.
  - Deployment types: Global Standard and Data Zone Standard, version 1, in selected regions.
  - Microsoft suggests pairing it with a generative model when the app also needs an explanation.
- **Probabilities:** the model returns per-option scores, which applications are told to use to act, defer or request review. The mechanism that produces them (option-token logits or a scoring head) is not disclosed in any excerpt seen.
- **Latency [V]:**
  - p50 85 ms and p95 125 ms (as relayed via MarkTechPost).
  - "~35x faster than GPT-6 Sol" at median latency.
  - In Microsoft's chart, the runner-up H2O-Lightning-4B v1.1 sits at 210 ms.
- **Price:** $0.04 to $0.042 per 1M input tokens, $0 output. Sources differ slightly.
- **Accuracy [V]:**
  - 83.5% average accuracy across 36 benchmarks, about 150,000 questions held blind from training.
  - Comparators in Microsoft's table: Jev 1.13.0 at 82.3% and Quyet-1.0-Large at 81.9%.
- **Robustness [V]:** across eight perturbations (rephrased instructions, reordered options, formatting noise), the decision changed in 1.3% of cases on average.
- **Use cases:** agent controls, model routing, intent analysis, data labeling, AI judging, incident-response routing, data validation and content classification.
- **Limitations noted by coverage:**
  - "No independent evaluation exists yet". Epoch AI had none at the time.
  - The full datasets and latency test conditions are not published, so the 36-benchmark sweep cannot be reproduced.
  - The basis of the "35x" claim is ambiguous: a chart shows under 200 ms vs 2.6 to 2.8 s.

### 3. Microsoft-Decision-1: secondary coverage (The Next Web, AI Weekly, ProPakistani, RuntimeWire, Help Net Security)
- URLs:
  - https://thenextweb.com/news/microsoft-decision-1-qwen-decision-model
  - https://aiweekly.co/alerts/microsoft-ships-decision-1-a-qwen35-9b-classifier-model-priced-at-0042m-input
  - https://propakistani.pk/2026/10/12/microsofts-new-ai-model-is-35x-faster-and-up-to-200x-cheaper-than-gpt-6-sol/
  - https://runtimewire.com/article/microsoft-decision-1-achint-srivastava-agent-workflows
  - https://helpnetsecurity.com/2026/10/12/microsoft-decision-1-model
- Date: Oct 9 to 12, 2026. Type: third-party news. Orgs: various.
- **Framing:** Microsoft built on Qwen rather than OpenAI's decision model (The Next Web). Headlines say "up to 200x cheaper than GPT-6 Sol" [V].
- **Origin:** RuntimeWire calls it "a 9B decision model" and quotes a co-founder of an acquired startup on the $0.042/M price. This suggests the model came through an acquisition, but the excerpt does not name the startup.
- **Use cases:** Microsoft lists model routing, but has not said whether the model will power Copilot routing (The New Stack excerpt).
- **Independent-style latency [I, weak]:** one review reports a median of 190 to 270 ms measured from outside Microsoft via OpenRouter, against the vendor's 85 ms. The source of that measurement is not fully identified in the excerpt.

### 4. Microsoft-Decision-1 on OpenRouter and Vercel AI Gateway
- URLs:
  - https://openrouter.ai/microsoft/microsoft-decision-1
  - https://vercel.com/ai-gateway/models/microsoft-decision-1
  - https://vercel.com/i/what-is-microsoft-decision-1 (fetch failed)
- Date: Oct to Nov 2026. Type: model listing / platform. Orgs: OpenRouter, Vercel.
- **Interface:** OpenRouter serves the model through its **Decisions API**, not the OpenAI-compatible chat-completions endpoint, so chat SDKs do not work with it. The OpenRouter request schema was not visible.
- **Telemetry [P]:** OpenRouter's page lists 0.28 s P50 (best provider) and 100.00% 24-hour availability. This is three times Microsoft's 85 ms figure, though it includes network and gateway overhead.
- **Vercel listing:** context window 32,768 tokens, model ID `microsoft/microsoft-decision-1`, $0.042 per 1M input tokens.
- **Request shape:** a Foundry deep-dive (itnext.io) describes a request that combines a *state* with *typed questions*. The response carries a choice, a score and a yes/no probability, so one call answers several question types.

### 5. Gemini Decisions API: Fast, calibrated multimodal decisions (Google blog)
- URL: https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/
- Date: 2026-11-11. Type: official (via secondary: VentureBeat, MarkTechPost, DataCamp, Let's Data Science). Org: Google / Google DeepMind.
- **Model:** Gemini Decision 1 (`gemini-decision-1`).
  - The base model is **not disclosed**; listings say "parameters not disclosed".
  - Hosted API only, no open weights.
  - Available in preview through the Gemini API (v1beta) in Google AI Studio. Google Cloud support is "coming soon".
- **Interface:**
  - One shared multimodal input (text, images, audio, video, PDF), reportedly up to 256K tokens.
  - Up to **1,000 independent questions** per request against that one input.
  - Question types: yes/no, multiple choice, and rubric "score" questions.
  - The model scores all questions in "one forward pass".
  - Rubric questions grade the input against an ordered rubric starting at 0. They return per-level probabilities plus a continuous weighted score.
  - Output tokens are zero.
- **Probabilities:** returned per option, with confidence scores. Google attributes the speed to "scoring options instead of generating text". The scoring mechanism is not disclosed in any excerpt seen.
- **Latency and cost [V]:**
  - 150 to 250 ms end to end.
  - $0.10 per 1M input tokens, $0 output, with a free tier in AI Studio.
  - "Nearly 5x cheaper" across the shared suite than Gemini 3.5 Flash-Lite via the Interactions API.
- **Benchmarks [V]:**
  - Leads 7 of 9 accuracy benchmarks in Google's table, with the lowest expected calibration error (ECE). The exact ECE figures were not visible.
  - JevBench public split: Gemini Decision 1 92.2%, GPT-6 Luna 90.9%, Jev 1.14 90.0%, and an unnamed fourth column at 86.6%.
  - Refusals and safety blocks count as incorrect.
- **Positioning:** tool selection, policy checks, model routing and context grading. Integrations with OpenRouter, LangChain, Vercel and LiteLLM are reported.
- **Caveats from coverage:**
  - Independent reporting has Jev ahead on 2 of 7 shared tests and cheaper on the shared suite ($0.68 vs $0.88).
  - Secondary sources conflict on context window and input limits.

### 6. Gemini Decision 1 and the Decisions API (AI Tools Review)
- URL: https://aitoolsreview.co.uk/insights/gemini-decision-1-decisions-api
- Date: 2026-11-13. Type: third-party editorial comparison. Org: AI Tools Review (UK).
- **Fetch not attempted** (other hosts were blocked). Content is from the search snippet only, and the verdict was not visible.
- Compares Gemini Decision 1 with OpenAI's Decisions API (GA 2026-10-22).
- Reproduces Google's JevBench table: 92.2% vs Jev 1.14 at 90.0% and GPT-6 Luna at 90.9%. These are vendor numbers.
- Notes the model "cannot generate even a single word of text", so it fits routing, policy checks and grading, not chat.
- Price discrepancy: AI/ML API lists $0.1058 per 1M input tokens (checked 2026-11-12), against Google's $0.10.

### 7. Artificial Analysis Decision Index v2 / v2.1 (methodology, leaderboard and per-model pages)
- URLs:
  - https://artificialanalysis.ai/articles/decision-index-v2
  - https://artificialanalysis.ai/methodology/decision-index
  - https://artificialanalysis.ai/evaluations/artificial-analysis-decision-index
  - https://artificialanalysis.ai/decision-models/gemini-decision-1
- Date: v2 published 2026-11-08; the index page now shows v2.1. Type: independent benchmark. Org: Artificial Analysis.
- **Scoring rule:**
  - Each question's **Decision Score** combines accuracy with a Brier penalty, so a confident wrong answer costs more than a hedged one.
  - Over an evaluation, Decision Score = 50 × (1 + Accuracy − Brier).
  - Brier here is the mean squared gap between the chosen answer's probability and its correctness, on a 0 to 1 scale.
- **Index composition:** a weighted average of six evaluations: five Decision Scores plus the **AA-Symmetry** Symmetry Score. Calibration is also reported via reliability bins of width 0.1.
- **Leaderboard at v2 launch [I]:**
  - Drex Max v1.1 (Nace AI) 73 and GLiDE v1.2 (Fastino Labs) 73.
  - Mammoth 27B (Base Labs) 72.
  - Later pages show d1.2-ultra 75, Jev 1.14 66 and Clef 60, possibly from a different snapshot.
- **Calibration example [I]:** on AA-Paperclip, Celeris-1.1 Decision ties Clef on Decision Score despite a lower raw pass rate, because its Brier score is better (0.15 vs 0.27).
- **Gemini Decision 1 [I]:**
  - Decision Index **66**, equal to the decision-model median of 66, which the page describes as "below average".
  - 211 ms per task, slower than average.
  - **$345 per 1M tasks** vs a $135 median.
  - This contrasts with Google's "leads 7 of 9" claim.
- **Microsoft-Decision-1:** AF.NET coverage lists it among 17 evaluated models with Brier reporting, but no AA per-model page or score surfaced in search.
- **OpenAI:** a "GPT-6 Luna (Decisions)" page exists; its score was not visible.

### 8. 37 models without free text: AI decision model comparison (gradually.ai)
- URL: https://www.gradually.ai/en/ai-decision-model-comparison/
- Date: updated after 2026-11-04 (it lists a model first released that day). Type: third-party catalogue/comparison. Org: gradually.ai.
- **Fetch failed** (host blocked). Content is from search summaries only; the full comparison table, licences, sizes and image-input columns were not seen.
- **Taxonomy:** 37 decision models from 17 providers, split into three kinds:
  - 26 **standalone** models with their own weights, which pick from fixed options or fill a fixed schema;
  - 7 **adapters**, LoRA add-ons that run only on their base model;
  - 4 **classifiers** for narrowly scoped operational decisions.
- **Popularity ranking:** AutoTrust JEV-27B-VL ranks first with a popularity score of 70 out of 100. It was first released as v1.0 on 2026-11-04. Its relation to TypeSafe's Jev was not established; the shared name may be coincidental.
- gradually.ai also has a per-model page for gemini-decision-1 (https://www.gradually.ai/en/ai-models/gemini-decision-1/), which lists it as "Google DeepMind, decision model, API available".

### 9. Decision models guide (Product Builder)
- URL: https://www.productbuilder.net/learn/decision-models (plus /de, /fr, /nl and /pt versions)
- Date: Oct to Nov 2026 (not visible). Type: third-party practitioner guide. Org: Product Builder.
- **Not fetched.** Content is from fragments across language versions.
- Deterministic logic belongs in code: arithmetic, dates, permissions and explicit policy stay outside the model. Decision models fit where messy language must be mapped to a bounded judgment.
- **Adoption recipe:**
  - start with one *reversible* decision;
  - label real cases;
  - make uncertainty visible before a score triggers an action;
  - let a labelled evaluation pick the vendor, after access and workload fit.
- **Vendor contrasts:**
  - OpenAI exposes a decision-specific API contract on top of a general model.
  - Microsoft's product is a post-trained Qwen3.5-9B with an interface designed for single-pass scoring.
  - Access, inputs, serving and lifecycle differ even when the user experience looks similar.
- For consequential decisions, use these models only as bounded support, with domain review, escalation and appeal paths, monitoring, and a responsible human decision-maker.
- "The boundary around the decision matters more than the model category."

### 10. Exploring System One AI Models Beyond Jev: 15 Outstanding Models (Turing Post)
- URL: https://www.turingpost.com/p/exploring-system-one-ai-models-beyond-jev-15-outstanding-models
- Date: about Nov 2026 ("within the last few weeks"). Type: third-party survey/listicle. Org: Turing Post.
- **Not fetched.** List and one-line descriptions are from a search summary of the article.
- "System One" comes from Kahneman's System 1: fast, automatic judgment.
- **The 15-model list, with each model's distinguishing idea:**
  - **Prism-1**: per-candidate isolated attention blocks, so ordering does not matter.
  - **Jeva**: candidate scoring for changing candidate sets.
  - **Bongard**: shared encoding that reuses evidence across judgments.
  - **Verdict**: several typed questions answered from one encoded input.
  - **VideoJev**: video decisions.
  - **MJev-Spatial**: spatial and numerical scoring.
  - **AudioJev**: scores answers directly from audio.
  - **Intern-Decision**: several structured fields in one pass.
  - **MetaEncoder**: retrieval over very large candidate sets.
  - **FastJEV**: inference optimisation.
  - **SanSi**: a looped decision model.
  - **StartLux-Decision**: adds reasoning when confidence is low.
  - **System X**: mixes decisions with text replies.
  - **FunDM**: decision distillation for cheaper inference.
  - **LAVOIR**: judges whether asking for missing information would help.
- **Corroboration from other sources:**
  - Intern-Decision (Shanghai AI Lab): open-sourced at 0.8B, 2B and 4B, multimodal (images and interfaces).
  - StartLux-Decision: open-source, released 2026-09-30 by a Shanghai startup under five months old, which claims it beats Jev (36Kr) [V].
  - Bongard: arXiv 2609.39111 reports 78.05% on 23,900 DecisionBench rows (4th of 61) and 59.4% agreement with the teacher's top label vs 72.7% for Jev [V/author].
  - No primary source was found for FunDM or SanSi.

### 11. Prism-1: Position- and Rival-Independent Scoring for System One Models (arXiv 2610.22066)
- URL: https://arxiv.org/pdf/2610.22066 (mirror: https://www.emergentmind.com/papers/2610.22066)
- Date: submitted 2026-10-15 (cs.AI). Type: paper. Authors: Yao Long Teng, Jianguo Huang, Jiayi Cai, Yanchen Deng, Bo An.
- **Content:** from the abstract excerpt only; the full text was not seen.
- **Axioms:** a decision read should satisfy two properties:
  - *position independence*: shuffling the options does not change the answer;
  - *rival independence*: adding an irrelevant option does not move the choice.
- **Theory:** both properties hold only if the read is a softmax over scores that each depend on one option alone. In a transformer, they hold by construction only if no token scoring one option attends to another option.
- **Mechanism:**
  - each option is encoded in its **own block at shared position IDs**, masked so options never attend to each other;
  - all blocks attend to the shared context;
  - a softmax across blocks gives the decision;
  - all of this runs in one forward pass with normal causal attention inside each block.
- **Results [author]:**
  - no shuffle changes any answer, and no added irrelevant option moves the choice;
  - accuracy stays within about 1 point of the baseline;
  - when only answers that survive reordering are counted, Prism-1 is 2 to 4 points more accurate.
- The baselines and benchmarks were not visible in the excerpt.

### 12. TypedBench: A Benchmark for Calibration, Framing Sensitivity, and Cost in System One Decision Models (arXiv 2610.11392)
- URL: https://arxiv.org/pdf/2610.11392 (alphaxiv v2 submitted 2026-10-09)
- Date: Oct 2026. Type: paper / independent benchmark. Authors: Sharma, Duncan, Marceau Caron, Vollmer.
- **Design:**
  - seven policy-labelled generators and nine evaluation suites;
  - identical items run on a hosted model, an open encoder, and open decoders from 0.8B to 9B parameters.
- **Methods:**
  - accuracy reported as the **median and range across paraphrases**;
  - calibration error measured against the **finite-sample noise floor of a perfectly calibrated predictor**;
  - selective prediction and proper scoring rules;
  - **realised cost under asymmetric cost matrices**.
- **Hosted model** (the excerpt implies Jev):
  - follows the stated policy but is wording-sensitive and systematically **underconfident**;
  - under asymmetric costs, its probabilities can give *worse* outcomes than taking its top answer.
- **Open decoders:**
  - route exactly and are unaffected by co-asked questions;
  - apply policies only partially;
  - slow down as options or questions are added.
- **Open encoder:** weakest on policy questions and degrades as options grow.
- **Conclusion:** typed decision models should be judged *jointly* on policy adherence, wording robustness, probability quality and downstream decision outcomes.

### 13. System1-Arena: Which Decisions Can Be Left to System 1? (arXiv 2610.21244)
- URL: https://arxiv.org/pdf/2610.21244
- Date: 2026-10-15. Type: paper / independent benchmark. Org: UT Austin (Chen, Liu, An, Wang, Zhou).
- **Scale:**
  - 92k questions over 105 tasks;
  - four groups: text classification/knowledge, applied decisions, evaluation/control, and agent/action;
  - 30 models: 7 closed LLMs, 13 open LLMs and 10 System-1 models;
  - the same requests go to every model, and the returned probabilities are scored.
- **Static decisions [I]:** the best System-1 models match fast closed LLMs on accuracy, with **better calibration at about a quarter of the latency**.
- **Reasoning LLM [I]:** most accurate overall, at about **70x** the cost of a fast LLM.
- **Closed-loop interactive tasks [I]:** the best open LLM reaches 32.9% success; small System-1 models reach **3.1% at most**.
- **Domain variation [I]:** in forecasting, the OpenAI Decisions API scores 48.3% vs 61.6% for Opus 5.5.

### 14. Benchmarking System One decision models against trained classifiers and language models for automated decision gates (arXiv 2610.00346)
- URL: https://arxiv.org/pdf/2610.00346
- Date: 2026-09-29 (v1) / 2026-10-06 (v2). Type: paper / independent benchmark. Authors: Amir Rafe, Subasish Das.
- **Setup:**
  - one harness;
  - eight decision-model checkpoints from six families (including hosted Jev) and four open generative models;
  - trained and zero-shot classifiers on the same workflow, intent, emotion and social-science items.
- **Findings [I]:**
  - A fine-tuned **DeBERTa-v3-large** had the highest accuracy on every labelled benchmark but one.
  - Small trained classifiers were best on intents and tied with the best decision models on workflows.
  - **A cascade works:** an intent-trained first stage escalating to Jev matched Jev's accuracy at **0.43x its cost** at full GPU utilisation.
  - **Contamination:** the largest lead of one open checkpoint came from exposure to a benchmark's training data, and it vanished on rater-labelled emotions.
- **Conclusion:** condition-dependent design rules, not a single best model.

### 15. Releasing the Inner Jev: A Simple Recipe for Open Decision Models (arXiv 2610.17205)
- URL: https://arxiv.org/pdf/2610.17205 (abstract mirror: https://www.emergentmind.com/papers/2610.17205)
- Date: 2026-10-12. Type: paper (open recipe). Authors: not visible in the excerpt.
- **Training-free baseline:** read the answer from the **option-letter token logits (A, B, C, ...) at the last position** of an instruction-tuned LLM. Untrained, Gemma 4 31B scores 79.6 on OpenDecisions vs Jev's 80.1 [author].
- **Fine-tuning recipe:**
  - LoRA plus a **decision head initialised from a slice of the LM head**, i.e. the rows for the option tokens;
  - applied to Gemma 4 31B, Gemma 4 12B, Qwen3.6-27B and Qwen3.5-4B.
- **Results [author]:**
  - fine-tuned Gemma 4 31B reaches 84.4 on OpenDecisions (claimed SOTA) and 81.5 on JevBench v1.7;
  - on public decision datasets, calibration error is lower than Jev's;
  - models, serving code and the OpenDecisions benchmark are released.
- **Related:** LLM-as-Jev (arXiv 2610.02076) reaches a similar "LLMs already are decision models" conclusion.

### 16. Reading Right, Acting Wrong: Diagnosing Decision Failures of System One Models in Agent Loops (arXiv 2610.18579)
- URL: https://arxiv.org/pdf/2610.18579
- Date: about 2026-10-13. Type: paper / independent diagnostic. Authors: Yubo Li, Ramayya Krishnan, Rema Padman.
- **Method:**
  - each next-action question is paired with independent **factual probes about the same state**;
  - the benchmark is frozen, drawn from simulated environments, customer-service policies, tool use, web navigation and coding;
  - 17 fast systems and one reasoning model are tested.
- **Findings [I]:**
  - **Most wrong actions occur after the model read the state correctly.** The more accurate the system, the larger the share of its errors that are of this kind.
  - For the six strongest systems, that share ranges from 62% to 100% depending on the domain.
  - Torchcast-27B reads best, yet acts correctly on only 0.678 of paired states.
  - On one TextWorld cohort, Gemma and JEV both answered every probe correctly but reached 73.2% vs 95.0% decision accuracy. Probe accuracy does not predict action quality.

### 17. System Switch: When Should a Fast Decision Model Stop and Think? (arXiv 2610.09683)
- URL: https://arxiv.org/pdf/2610.09683
- Date: Oct 2026. Type: paper. Author: Gian Luca Bailo.
- **Content:** mostly via a Towards AI write-up and an AI Weekly summary, not the paper itself.
- **Event-gated thinking:**
  - a fast actor decides every step;
  - a gate watches recent history for signals (unsure, stuck, blocked, looping, no new area);
  - when the gate opens, a slow reasoning VLM takes over;
  - tested closed-loop in ViZDoom ("doomLaya"), with a rule-based expert labelling states.
- **Offline results:**
  - deferring the least-confident 30% on 900 held-out questions gains +0.13 [0.08, 0.18] over random deferral;
  - rank correlation between the fast actor's AUROC and its deferral gain is 0.87;
  - reasoning accounts for about half of the gain.
- **Closed-loop result:** no fast-slow variant reached the exit in 33 games × 3 seeds.
- **Real-time constraint:** the reasoner writes a median of about 1,300 tokens per decision while the fast model decides every 0.5 s, so deferring 30% is impossible in real time.

### 18. OpenAI Decisions API (developer changelog, docs and coverage)
- URLs:
  - https://developers.openai.com/docs/guides/decisions
  - https://developers.openai.com/changelog/
  - https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev
  - https://www.promptfoo.dev/docs/providers/openai-decisions/
- Date: shown at dev day 2026-09-29; public beta 2026-10-06; GA 2026-10-22. Type: official (via search excerpts) plus third-party. Org: OpenAI.
- **Model and endpoint:** runs on **gpt-6-luna** at `/v1/decisions`. One outlet also lists gpt-6-sol; this is unresolved.
- **Output types:**
  - **predicate**: P(true) between 0 and 1;
  - **choice**: per-option probabilities;
  - **score**: a rubric level.
- **GA features:**
  - prompt caching of the shared input;
  - images in question instructions;
  - structured-data input;
  - up to 400 questions per request (TechEnclave);
  - US/EU regional processing, Zero Data Retention and HIPAA eligibility.
- **Price and latency [V]:** $0.10 per 1M uncached input tokens, input-only billing. About 150 ms vs 1.6 s for GPT-6 Luna via the Responses API (not independently reproduced).
- **Mechanism:**
  - not published by OpenAI;
  - Vercel notes the announcement does not even specify the output semantics;
  - one third party *claims* it prompts a general LLM to fill a JSON schema with probabilities.
- **Pitfall:** rounding a continuous rubric score can select a level the model assigned 0% probability (Towards AI title).

### 19. Other entrants: Sarvam Prism, Cloudflare Clef, AWS Strands Decider 2B
- URLs:
  - https://docs.sarvam.ai/api/token-factory/models/sarvam-prism
  - https://sarvam.ai/blogs/sarvam-prism
  - https://developers.cloudflare.com/changelog/post/2026-10-01-clef-workers-ai/
  - https://techcrunch.com/2026/10/01/amazon-releases-its-own-jev-clone-as-decision-models-flood-the-web/
- Dates: Clef and Strands Decider 2026-10-01; Sarvam Prism Oct to Nov 2026 (exact date not visible). Type: official, plus TechCrunch.
- **Sarvam Prism:**
  - built on Sarvam 105B; open weights under Apache 2.0 (per one outlet);
  - input is a state plus typed questions; output is a calibrated probability for every option of every question in one call.
  - Vendor claims [V]:
    - "a 90%-confidence answer is wrong at most about 10% of the time";
    - 44 ms median;
    - 71.8 average over three decision indices and 82.5 on an Indian-language benchmark;
    - changed none of 2,000 answers under option shuffling, after standardising option order.
  - Discrepancies:
    - Sarvam's "Artificial Analysis recreation" is self-run;
    - a third-party table puts Mammoth-1 (75.2) and GLiDE 1.2 above it, though those take 2 to 6x longer;
    - Jev 1.14's average is given as 64.5 in Sarvam's docs vs 60.7 in its blog.
  - Not the same model as the academic Prism-1.
- **Cloudflare Clef:**
  - two open models (Apache 2.0) on Workers AI, plus an RL fine-tuning platform: Clef (27B, precision) and Clef-flash (9B, latency-critical);
  - Clef-omni later added audio and video input.
  - Latency [V]: Clef-flash 38.8 ms p50 / 122.4 ms p95; Clef 209.3 / 238.6 ms; Jev 524.1 / 536.0 ms.
  - Price: $0.24 and $0.09 per 1M input tokens, with no output charge.
  - On AA [I], Clef scores 60.
- **AWS Strands Decider 2B:**
  - open-source 2B model on Hugging Face, small enough to run locally;
  - conceived by Marc Brooker after Jev;
  - reports say 106 ms per decision and briefly top of JevBench in its size class;
  - "third free Jev clone in a week".

### 20. Calibration-coherence audits: Beyond Calibration (arXiv 2609.33209) and label-free calibration certificates (arXiv 2610.21567)
- URLs:
  - https://arxiv.org/pdf/2609.33209
  - https://arxiv.org/pdf/2610.21567
- Date: Sep to Oct 2026. Type: papers. Authors: not visible in the excerpts.
- **2609.33209:** only the title and reference list were visible. It asks whether a typed-decision model's probabilities obey the probability axioms.
- **2610.21567** ("Sharp and Stable Label-Free Calibration Certificates from Logical Coherence"), citing Li et al. 2026a:
  - for Jev, P(label) + P(negation) misses 1 by about 0.064 on average;
  - three mutually exclusive labels asked one at a time sum to 1.14 on average;
  - Jev's documentation once showed a question and its negation summing to 1.19, and a later revision removed those examples.
- **Idea:** logical-coherence constraints provide **label-free** lower bounds on miscalibration.
- **Related:** arXiv 2609.09855 argues a predictor can be calibrated on one forecast yet incoherent across related forecasts, which leads to suboptimal decisions.

### 21. Fast Models, Slow Evidence (arXiv 2610.02267), noted for its protocol
- URL: https://arxiv.org/pdf/2610.02267
- Date: Oct 2026. Type: paper. Author: Jiawei Li.
- **Protocol:**
  - open-weight Laya vs hosted Jev;
  - 11 agent-harness decision points (model choice, tool choice, prompt-injection detection) built from 18 public sources;
  - 7,283 base cases plus 6,640 robustness variants;
  - **byte-identical inputs and paired statistical tests**.
- Results were not visible in the excerpt.

---

## Landscape table

"Org" and "base" are given only where a source states them. "n/d" means not disclosed or not found. "TP" means listed in Turing Post's 15-model article.

| Name | Org | Date | Base | Interface | Distinguishing technique | Availability |
|---|---|---|---|---|---|---|
| Microsoft-Decision-1 | Microsoft (reportedly via an acquired startup) | 2026-10-09 | Qwen3.5-9B, post-trained | state + typed questions (yes/no, MC, rating, rubric) → per-option calibrated probabilities; 32K context | small open-base post-train; 8-perturbation robustness eval (1.3% flip rate) [V] | Foundry (Global/Data Zone Standard), OpenRouter Decisions API, Vercel AI Gateway; $0.042/M in |
| Gemini Decision 1 (`gemini-decision-1`) | Google DeepMind | 2026-11-11 | n/d | one multimodal input (text/image/audio/video/PDF, ~256K reported) + up to 1,000 questions; yes/no, choice, rubric with per-level probabilities + weighted score | many questions answered over one shared encoded input; multimodal | Gemini API v1beta preview (AI Studio), Cloud "soon"; $0.10/M in; hosted only |
| OpenAI Decisions API (gpt-6-luna) | OpenAI | beta 2026-10-06, GA 2026-10-22 | GPT-6 Luna (general model) | `/v1/decisions`: predicate / choice / score; up to 400 questions; image and structured inputs | decision API contract on a general frontier model; prompt caching of the shared input | GA; $0.10/M uncached in |
| Prism-1 | academic (Teng, Huang, Cai, Deng, An) | 2026-10-15 | n/d in excerpt | MC/option scoring in one pass | per-option isolated blocks at shared positions + softmax across blocks: order- and rival-independent by construction | arXiv paper |
| Sarvam Prism | Sarvam AI | ~Oct–Nov 2026 | Sarvam 105B | state + typed questions → probability for every option | Indic-language focus; shuffle-invariance claim | Sarvam token factory; open weights (Apache 2.0, per one outlet) |
| Clef / Clef-flash / Clef-omni | Cloudflare | 2026-10-01 | n/d (27B / 9B) | Jev-compatible decision API | edge-GPU serving; RL fine-tuning platform; omni variant adds audio/video | Workers AI, OpenRouter; Apache 2.0 |
| Strands Decider 2B | AWS (Amazon) | 2026-10-01 | n/d (2B) | bounded choices in agent loops | tiny local model | open source on Hugging Face |
| Intern-Decision (0.8B/2B/4B) | Shanghai AI Lab | ~Oct 2026 | n/d | several structured fields in one pass; image/UI input | small multimodal decision family (TP) | open source |
| StartLux-Decision | StartLux (Shanghai) | 2026-09-30 | n/d | decisions, adding reasoning when confidence is low (TP) | confidence-gated reasoning | open source |
| Bongard | n/d (arXiv 2609.39111) | Sep 2026 | n/d | judgments over a shared encoding | evidence reuse across judgments (TP); distilled against a teacher | paper |
| Drex Max v1.1 / Drex 2.0 | Nace AI | ≤2026-11-08 | n/d | decision API | n/d | AA-listed (73) |
| GLiDE v1.2 | Fastino Labs | ≤2026-11-08 | n/d | decision API | n/d | AA-listed (73) |
| Mammoth 27B / Mammoth-1 | Base Labs | ≤2026-11-08 | n/d (27B) | decision API | n/d | AA-listed (72) |
| Celeris-1.1 Decision | n/d | ≤2026-11-08 | n/d | decision API | strong Brier (0.15 on AA-Paperclip) | AA-listed |
| d1 / d1-ultra / d1.2-ultra | n/d | ≤Nov 2026 | n/d | decision API | n/d | AA-listed (d1.2-ultra 75) |
| Quyet-1.0-Large | n/d | ≤Oct 2026 | n/d | decision | n/d | comparator in Microsoft's table (81.9%) [V] |
| H2O-Lightning-4B v1.1 | n/d (name suggests H2O.ai; not confirmed) | ≤Oct 2026 | n/d (4B) | decision | low latency (210 ms in Microsoft's chart) | comparator |
| pplx-decider v1.2 | n/d (not confirmed) | ≤Nov 2026 | n/d | decision | n/d | cited in a Pinggy roundup |
| AutoTrust JEV-27B-VL | AutoTrust | 2026-11-04 (v1.0) | n/d (27B, VL) | vision-language decisions | n/d | Hugging Face (autotrust/JEV); top of gradually.ai popularity ranking |
| Torchcast-27B | n/d | ≤Oct 2026 | n/d | next-action scoring | best "reader" but large read/act gap (0.678) [I] | evaluated in 2610.18579 |
| Laya | n/d | ≤Oct 2026 | n/d | open-weight System-1 model | used as Jev comparator in agent harnesses | open weights |
| Open recipe models (Gemma 4 31B/12B, Qwen3.6-27B, Qwen3.5-4B) | academic (2610.17205) | 2026-10-12 | Gemma 4 / Qwen | MC option scoring | letter-logit readout + LoRA + decision head initialised from LM-head slice | released weights and code |
| Jev 1.13 / 1.14 (comparison only) | TypeSafe AI | 2026-09-15 onward | n/d | typed decisions with calibrated probabilities | RLCD (covered in a separate file) | hosted API |
| Jeva, Verdict, VideoJev, MJev-Spatial, AudioJev, MetaEncoder, FastJEV, SanSi, System X, FunDM, LAVOIR | various (TP list) | Sep–Nov 2026 | n/d | see Turing Post entry (source 10) | candidate-set scoring / multi-question / modality-specific / retrieval / looped / hybrid text / distillation / ask-for-info | mostly not verified beyond TP |

---

## Idea atoms

1. **Scoring instead of generating.** Treating a closed-set decision as scoring the given options, rather than generating an answer, removes autoregressive decoding. Latency and cost then scale with input tokens only: zero output tokens and no parse failures. [2, 5, 18, 19]
2. **Option-letter logits as a free decision model.** An instruction-tuned LM already holds a usable decision distribution: read the option-letter (A/B/C...) logits at the last position and softmax over them. With no training, this nearly matches a purpose-built model (79.6 vs 80.1). [15]
3. **Initialise the decision head from the LM head.** Starting the head from the LM-head rows for the option tokens, then fine-tuning with LoRA, keeps the pretrained answer prior. The calibration objective only has to sharpen it, which explains why small adapters suffice. [15, 10 (distillation card: "pretraining does most of the work; distillation only sharpens")]
4. **Order invariance by construction.** Encode each option in its own attention block at *shared* position IDs, masked from the other options. The per-option score then depends only on context and that option, so a softmax across blocks is permutation-invariant and immune to irrelevant options, with no augmentation needed. [11]
5. **Independence axioms define what to measure.** Stating decision-read requirements as axioms (position independence, rival independence) gives a diagnostic that ordinary accuracy cannot. Count only answers that survive reordering ("robust accuracy"); this separated models that plain accuracy ranked within 1 point. [11, 2]
6. **Many questions over one encoded input.** Encode one input once and score many independent questions against it (up to 1,000 per call). The encoding cost is amortised across all of them, which suits multi-attribute grading and policy checks. [5, 10 (Verdict, Bongard), 18]
7. **Rubric grading as an ordinal distribution.** Return per-level probabilities over an ordered rubric, plus their expectation as a continuous score. This keeps uncertainty that a single grade discards. Rounding the expectation can pick a level the model gave near-zero probability, so take the argmax or a cost-aware choice instead. [5, 18]
8. **Brier-penalised accuracy.** Defining a score as 50 × (1 + accuracy − Brier) charges confident errors more than hedged ones. Models with lower raw accuracy but better probabilities can tie or win (Brier 0.15 vs 0.27 on AA-Paperclip). [7]
9. **Calibrate against the noise floor.** Measure calibration error relative to the finite-sample noise floor of a perfectly calibrated predictor, not against zero. Small benchmark ECE gaps then don't look significant when they are only sampling noise. [12]
10. **Report accuracy across paraphrases.** Give accuracy as a median and range over paraphrased prompts, plus an explicit symmetry or perturbation test. This exposes wording sensitivity that a single prompt hides: a 1.3% flip rate under 8 perturbations [V], and TypedBench's wording-sensitive hosted model. [2, 7, 12]
11. **Evaluate realised cost, not just calibration.** Score decisions by realised cost under asymmetric cost matrices. This shows that a model's probabilities can give worse outcomes than its top-1 answer when it is systematically underconfident. Calibration quality is necessary but not sufficient for thresholding. [12]
12. **Coherence gives label-free calibration bounds.** Asking a question and its negation, or each exclusive label separately, should yield probabilities that sum to 1. Measured deviations (+0.064 average; 1.14 for a 3-way set) bound miscalibration without ground-truth labels. [20]
13. **Selective prediction with a reasoning fallback.** Route the least-confident fraction of decisions to a slow reasoner. Deferral gain then tracks the fast model's AUROC (rank correlation 0.87) and beats random deferral. The fast model's ranking quality, not just its calibration, determines escalation value. [17, 10 (StartLux-Decision)]
14. **Gate escalation on behaviour signals.** In closed loops, trigger slow reasoning on trajectory events (stuck, looping, blocked), not only per-step confidence. The reasoner's latency budget must match the control rate: about 1,300 reasoning tokens per decision vs a 0.5 s decision cadence makes 30% deferral infeasible. [17]
15. **A cheap specialist in front of the decision model.** Put a cheap task-trained classifier first and escalate only uncertain cases to the general decision model. This matched the decision model's accuracy at 0.43x its cost; with in-domain labels, fine-tuned encoders (DeBERTa-v3-large) still beat zero-shot decision models. [14]
16. **Paired probes separate reading from acting.** Pair each action question with independent factual probes about the same state. This shows whether errors come from perception or from decision policy: most errors happen after a correct read, and the share grows with model accuracy. [16]
17. **Static scores do not transfer to closed loops.** Evaluate single-step decisions and closed-loop agent episodes on the same models. Models that match LLMs on static, well-calibrated decisions can collapse in interactive multi-step settings (≤3.1% vs 32.9% success). [13, 17]
18. **Byte-identical paired comparisons.** Feed byte-identical inputs to each system, use paired tests, and add matched robustness variants (7,283 base + 6,640 variants). This removes prompt-formatting confounds when comparing hosted and open decision models. [21]
19. **Audit for benchmark exposure.** Re-test a model's leads on rater-labelled or held-out splits. A checkpoint's largest lead traced to training-data exposure and vanished on rater-labelled data. [14, 2 (blind-held 150K questions)]
20. **Keep deterministic logic out of the model.** Leave arithmetic, dates, permissions and explicit policy in code, and use the decision model only for the fuzzy mapping from language to a bounded label. This shrinks the error surface and makes thresholds auditable. [9]
21. **Uncertainty-aware deployment loop.** Start with one reversible decision, label real cases, expose uncertainty, and only then let the score trigger actions (act / defer / review). This turns calibrated probabilities into a staged automation policy. [9, 2]
22. **Small open bases are enough.** Post-training an off-the-shelf 2B to 9B open base (Qwen3.5-9B, 2B, 9B flash variants) for single-pass option scoring is enough for competitive decision quality at sub-100 ms. Decision quality relies on pretrained knowledge more than scale. [2, 15, 19]
23. **Size tiers for precision and latency.** Shipping a precision model (27B) and a latency model (9B) under one API contract lets callers trade accuracy for tail latency per decision type. Out-of-scope behaviour of the small tier must be tested separately. [19]
24. **Typed multi-field decisions in one call.** Defining the API as one state plus typed questions (predicate → P(true), choice → per-option distribution, score → rubric distribution) answers several decision types at once. Responses are schema-valid by construction, with no free-text parsing. [2, 4, 18, 19]
25. **Gateway telemetry vs vendor latency.** Measured gateway p50 (0.28 s; 190 to 270 ms external) vs a vendor in-region p50 (85 ms) shows that decision-model latency claims need the measurement point stated. Network and gateway overhead can dominate when inference itself is sub-100 ms. [2, 3, 4, 7]
26. **Cost per task, not per token.** Because these models bill input only, comparing cost per 1M *tasks* (prompt length × questions × price) can reverse token-price rankings. A $0.10/M model cost $345 per 1M tasks against a $135 median. [5, 7]

---

## Open problems / gaps

- **Vendor vs independent disagreement on Gemini Decision 1.**
  - Google says it leads 7 of 9 benchmarks with the lowest ECE and 92.2% on JevBench.
  - Artificial Analysis gives it a Decision Index of 66 (median), 211 ms (slower than average) and $345 per 1M tasks, 2.5x the median.
  - Coverage also has Jev ahead on 2 of 7 shared tests and cheaper on the shared suite ($0.68 vs $0.88).
- **Microsoft-Decision-1 is not independently evaluated.**
  - The 83.5% / 36-benchmark result, 85 ms latency and 1.3% flip rate are all vendor claims, and the datasets and latency conditions are not published.
  - No AA per-model score surfaced in search.
  - Measured gateway latency (0.28 s P50 on OpenRouter; 190 to 270 ms external) is about 2 to 3x the vendor figure.
  - The "35x faster than GPT-6 Sol" claim has an unclear basis.
- **Mechanisms are not disclosed.**
  - Neither Microsoft, Google nor OpenAI says how probabilities are produced: option-token logits, a scoring head, constrained-decoding probabilities, or JSON-schema filling by a general LLM.
  - None says what calibration objective or post-hoc calibration (e.g. temperature scaling) is used.
  - Google does not disclose the base model; Microsoft does not describe its post-training recipe.
- **Calibration is claimed, rarely tested directly.**
  - TypedBench finds a hosted model systematically underconfident.
  - Coherence audits show that a question and its negation, or exclusive labels, do not sum to 1.
  - No coherence audit was found for Microsoft-Decision-1, gemini-decision-1 or the OpenAI Decisions API.
  - Calibration under distribution shift, with new domains or new option sets, is not reported.
- **Order and rival effects.** Only Prism-1 makes order and rival independence hold by construction. Vendors report perturbation flip rates (MS 1.3%; Sarvam 0 of 2,000 after "standardising option order"), but the protocols differ and are not public. Prism-1's own benchmarks and baselines were not visible.
- **Many questions per call is untested for interference.** Gemini scores up to 1,000 questions and OpenAI up to 400 over a shared input. Whether co-asked questions bias each other in these hosted models is unmeasured; TypedBench checked this only for open decoders, which were unaffected.
- **Rubric aggregation pitfall.** The weighted score is the expectation over levels, and rounding it can land on a near-zero-probability level. Vendors give no guidance on cost-aware readout.
- **Closed-loop and agentic failure.**
  - System1-Arena finds small System-1 models at ≤3.1% success vs 32.9% for the best open LLM in interactive tasks.
  - "Reading Right, Acting Wrong" shows most action errors follow correct perception.
  - System Switch's fast-slow agent never finished a Doom level.
  - Vendors market these models for agent control and routing without closed-loop evidence.
- **Specialist baselines are omitted.** Fine-tuned DeBERTa-v3-large beats decision models on most labelled tasks (2610.00346), yet vendor tables compare only against LLMs and other decision models.
- **Training-free baselines are also omitted.** Letter-logit readout from open LLMs nearly matches Jev untrained (2610.17205), and vendor tables do not include this baseline.
- **Contamination and benchmark provenance.**
  - JevBench is the shared yardstick, but it was created around a competitor's model.
  - Sarvam's "Artificial Analysis recreation" is self-run, and its eval set is unreleased.
  - Jev 1.14's average is reported inconsistently (64.5 vs 60.7).
  - One open checkpoint's lead came from training-data exposure.
- **Benchmark churn and inconsistent leaderboards.** AA moved from v2 to v2.1 within days, and per-model pages may come from different snapshots. Pinggy's Decision Index numbers (e.g. 174) use a different scale. Rankings shift with snapshot and weighting.
- **Data gaps in this corpus.**
  - No full text could be fetched. The Towards AI and Vercel Microsoft-Decision-1 pages and the gradually.ai table were unreadable, and Turing Post and Product Builder are known only from search summaries.
  - No primary source was found for FunDM, SanSi, System X or LAVOIR, and no orgs were found for d1, Celeris, Quyet, pplx-decider or Torchcast.
  - Every figure above should be re-verified once fetch access to these hosts is allowed.
