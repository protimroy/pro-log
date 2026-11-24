---
slug: /agent-dynamics-literature-review
title: "Agent Dynamics: From Orchestration to Computational Control"
description: "A critical literature review of agent architectures, failure attribution, causal replay and adaptive verification."
canonical_url: "https://www.protimroy.com/pro-log/agent-dynamics-literature-review/"
allow_html: true
options_toc: true
template: article.html
---

Literature review · November 24, 2026

An agent is more than a language model invoked repeatedly. Its behaviour emerges from the interaction between a policy, its available observations, tools, memory, environment and the computational decisions made by its harness. This distinction suggests a research program: study the dynamics of execution, rather than treating orchestration patterns as fixed recipes.

The difficulty is that many appealing research questions are already being answered. This review examines where existing evidence constrains the research program, what remains uncertain, and which claims are worth testing. It is a focused narrative review, not a systematic review or meta-analysis. No original performance results are presented.

## 1. Reasoning and action are established primitives

[ReAct (Yao et al., 2022)](https://arxiv.org/abs/2210.03629) interleaves reasoning with actions, allowing observations to inform subsequent decisions. It supplies a natural minimal tool-using baseline. [Reflexion (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366) instead uses feedback and retained verbal reflections to improve subsequent attempts without updating weights. These approaches establish mechanisms for feedback, not a universal guarantee that more deliberation improves execution.

[When Can LLMs Actually Correct Their Own Mistakes? (2024)](https://doi.org/10.1162/tacl_a_00713) critically surveys self-correction and distinguishes conditions in which external feedback is available from those in which models must correct themselves unaided. This distinction matters: a check that merely asks the original model to reconsider may share its blind spots. Independent evidence, such as a test result or a state invariant, has a different information content.

The appropriate experimental comparison is therefore not simply reflection versus no reflection. It must separate the availability of new information, the reliability of the verifier and the extra inference devoted to using that information. An extra direct reasoning call is a necessary control.

## 2. Architecture and cost

[AI Agents That Matter (Kapoor et al., 2024)](https://arxiv.org/abs/2407.01502) shows why agent comparisons should account for both performance and cost, and warns about benchmark-specific shortcuts. A sophisticated harness that loses to a simple policy on the cost–accuracy frontier has not established a computational advantage.

The strongest architectural precedent is [Towards a Science of Scaling Agent Systems (Kim et al., 2025; v3, April 2026)](https://arxiv.org/abs/2512.08296v3). The revised paper reports 260 configurations across six benchmarks, five architectures and three model families. Its predictive model reports cross-validated R² of 0.373 (0.413 with a task-grounded capability metric), and identifies the strongest architecture in 87% of held-out configurations. The reported relative changes span a large benefit on decomposable financial reasoning and a large loss on sequential planning. These are results for the evaluated systems, not universal laws. The earlier [Google research summary](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) discusses 180 configurations; the revision and earlier summary should not be conflated.

The implications are substantial. Architecture selection is already a predictive research problem, not a new idea. In addition, substantial unexplained variation in aggregate performance remains. A new study needs to specify what additional measurements explain or predict, with out-of-sample evidence.

[AgentBoard (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/877b40688e330a0e2a3fc24084208dfa-Abstract-Datasets_and_Benchmarks_Track.html) complements outcome metrics with measures of progress through multi-turn tasks. This motivates trajectory-level instrumentation, but recording progress is not equivalent to explaining why it changes.

## 3. Failures, dependencies and causal attribution

[Why Do Multi-Agent LLM Systems Fail? (Cemri et al., 2025)](https://arxiv.org/abs/2503.13657) introduces a taxonomy of failures involving system specification, coordination, and verification or termination. Taxonomies are useful for defining what to measure; a label attached to a failed trace does not, by itself, establish that changing the labelled event would improve the outcome.

[Causal Agent Replay (Shah, 2026)](https://arxiv.org/abs/2606.08275) addresses that distinction through interventions followed by stochastic re-execution. The work explicitly considers the confounding effect of re-sampling subsequent decisions and validates attribution against synthetic causal models with known mechanisms. This is direct prior art for checkpointing, counterfactual rollouts and multi-step attribution. These mechanisms cannot be claimed as new merely because they are reimplemented.

[EDGE (Hou et al., 2026)](https://arxiv.org/abs/2609.01360) builds dependency graphs of errors and uses counterfactual rollouts to validate subsets of explanatory events. [DeFA (2026)](https://arxiv.org/abs/2610.01256) reconstructs event dependencies to localize decisive failures and reports that diagnostic feedback can improve subsequent skill evolution. Both narrow the plausible gap: dependency-aware diagnosis and downstream repair are already research topics.

Attribution and intervention selection remain distinguishable. An event may have been decisive in a completed failure while offering little actionable evidence before the failure occurred. Conversely, a cheap check of an uncertain intermediate result can be worthwhile even if no error was present in one particular trace. A prospective policy must use only the information available at decision time.

## 4. The value of computation

This problem predates language models. [Principles of Metareasoning (Russell and Wefald, 1991)](https://doi.org/10.1016/0004-3702(91)90015-C) develops a decision-theoretic basis for choosing computational actions under resource constraints. Verification, planning and additional sampling are metalevel decisions: they consume resources now in the hope of improving subsequent actions.

[Learning When to Plan (Paglieri et al., 2025)](https://arxiv.org/abs/2509.03581) studies selective planning in sequential decision tasks. Its premise already challenges the idea that planning should be uniformly invoked. [Anytime Verified Agents (2026)](https://openreview.net/forum?id=JMDCMf7mlF) describes an adaptive budget allocator for search, sampling and verification, with uncertainty estimation and early exits. The associated [implementation](https://github.com/llmsresearch/AVA) is a candidate reference for reproduction. Its reported evaluation must be examined before transferring claims to state-changing tool environments.

The closest conceptual competitor is [Strategic Verification for Long-Running LLM Agents (Adeli, 2026, v2)](https://www.preprints.org/manuscript/202608.2057/v2). This unreviewed preprint proposes budgeted selective verification using risk, reliability, action criticality and resource constraints. In a reported campus-information experiment, its adaptive method matched the dense-verification correct-and-safe rate with fewer judge calls. The narrow setting and preprint status limit the strength of general claims; nevertheless, it directly overlaps with the proposed verification policy.

Finally, [Uncertainty Quantification for LLM Agents (Lin et al., 2026)](https://arxiv.org/abs/2609.07395) studies calibration along trajectories. Its reported results caution against treating verbal confidence as a reliable error probability and against assuming that per-step calibration ensures trajectory calibration.

## 5. A formal distinction: causal sensitivity versus risk

Consider a frozen policy, a history h, remaining budget b, and an available computational intervention v. Let Y be terminal utility, including task success and path violations. Define the prospective benefit of v as:

<pre>Delta(v, h, b) = E[Y | h, choose v, b] - E[Y | h, continue, b]</pre>

The two branches must be evaluated under explicitly specified continuation policies and budget accounting. If utility excludes computational costs, subtract a cost term in common utility units; if cost is already included, do not subtract it twice. This is a standard decision-theoretic quantity, not a novel equation.

A simplified diagnostic separates the probability that an error exists, the ability of a verifier to correct it, and the loss caused by leaving it uncorrected. Their product is only an approximation: errors can interact, verifiers can introduce new mistakes, and recovery can depend on the remaining trajectory.

A retrospective intervention with access to the true error estimates causal sensitivity under privileged information. It is not a deployable policy. The research question is whether offline interventional data can predict the incremental value of a real verification action prospectively, with no access to future outcomes, at an acceptable amortized cost.

## 6. Candidate hypothesis and competitive tests

**H01 (revised):** a predictor trained on controlled downstream intervention effects provides incremental decision value over risk-only and dependency-only verification policies, under matched end-to-end inference budgets and held-out task structures.

This is a candidate gap, not an established novelty claim. Causal attribution, graph-based repair, adaptive verification and metareasoning each have direct precedents. The combination must be evaluated against their strongest feasible representatives.

The comparison must include no verification, uniform verification, random selection, direct extra reasoning, uncertainty-only selection, dependency-only selection, a risk-and-structure heuristic and a reproducible adaptive allocation baseline. An oracle that sees hidden errors is a diagnostic upper reference, never a fair operational competitor. Include an equivalent-information deterministic workflow where possible.

The first experiment should isolate one known dependency structure and one reversible injected observation error, with a sham intervention and multiple stochastic continuations. Record paired terminal utility and path integrity. Subsequently compare prospective selection policies on held-out graph families and models. Randomize intervention placement independently of difficulty; group splits by generator family and topology, not only by task identifier. Keep calibration, policy selection and confirmation disjoint. Count attribution rollouts, fitting, inference tokens, tool calls, latency and verification overhead; report offline costs separately and amortize them explicitly. Use paired uncertainty intervals over task clusters rather than treating correlated rollouts as independent observations.

Reject the hypothesis if causal features fail to improve prospective prediction and matched-budget utility over the strongest simple heuristic, or if gains disappear after accounting for intervention costs. Choose a practically meaningful effect threshold before confirmation, using pilot variance only to plan sample size. A null or negative result is informative; it does not justify continuously adding complexity to rescue a hypothesis.

## 7. From abstract environments to applied evidence

A synthetic generator should vary depth, width, coupling, hidden information, tool reliability, reversibility and verifier cost independently wherever possible. A reference solver and planted ground truth help validate causal estimators. They can also make agents unnecessary; that is a desirable control. Synthetic success alone cannot establish external validity.

For software engineering, [SWE-bench (Jimenez et al., 2023)](https://arxiv.org/abs/2310.06770) offers real repository issues with executable evaluation. Start with a bounded, reproducible subset and report task selection. For scientific investigation, [AstaBench (Bragg et al., 2025)](https://arxiv.org/abs/2510.21652) provides scientific tasks and standardized research tools. Use representative tasks with independently checkable outcomes before attempting open-ended discovery. The same policy must transfer without tuning on the final test split.

Only after these two application areas establish useful transfer should an industry-specific setting be chosen. This sequence protects the research from becoming a domain-specific demonstration.

## 8. Visual exposition

Time-dependent phenomena are particularly suitable for programmatic animation. [Manim Community](https://docs.manim.community/en/stable/tutorials/output_and_config.html) can render standalone scenes in web-compatible video formats. Future articles will distinguish conceptual animations from empirical animations derived from recorded trajectories, with scene code, trace identifiers and provenance.

The first planned scene will compare two continuations from a common checkpoint: an unmodified branch and a branch with a verified correction. The animation must not imply a measured benefit until the data exist. The final presentation will preserve Pro-log's existing typography and layout, use user-controlled playback, static alternatives and compressed video. This review does not yet include a rendered animation.

## 9. Review scope and conclusion

Sources were selected from targeted searches of arXiv, conference and journal pages, institutional research releases, OpenReview-indexed material and recent preprints, using terms including agent scaling, dependency-aware failure attribution, causal replay, uncertainty calibration, adaptive verification and metareasoning. Foundational work and close competitors were prioritized over broad catalogs of frameworks. The review is current to November 24, 2026, and relies substantially on abstracts and accessible summaries; it is not an exhaustive full-text or implementation audit. The recent preprints require independent scrutiny. No cross-paper numerical comparison is implied by differing evaluation protocols.

The conclusion is narrower than the original project proposal. We should not build another orchestration framework or claim that error-aware verification is new. We should first determine whether offline causal evidence buys measurable prospective control value beyond simpler alternatives. The literature makes this a difficult question, which is precisely why a bounded falsification experiment is preferable to a large implementation program.

[Agent Dynamics research program](/pro-log/agent-dynamics/) · [Pro-log index](/pro-log/)
