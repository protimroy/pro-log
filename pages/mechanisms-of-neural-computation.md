---
slug: /mechanisms-of-neural-computation
title: "Mechanisms of Neural Computation"
description: "A research program on learned algorithms, neural representations, causal equivalence, and function construction."
canonical_url: "https://www.protimroy.com/pro-log/mechanisms-of-neural-computation/"
allow_html: true
options_toc: true
template: article.html
---

Research program · November 23, 2026

Archived research direction · November 24, 2026. This program is inactive; the original research questions and evidence are preserved. [Research archive](/pro-log/archive/).

How do neural networks implement computations, and what would it take to understand those computations well enough to reproduce or modify them?

This program studies the relationship between mathematical functions, internal representations, and neural parameters. Mechanistic interpretability investigates how learned parameters implement a computation; function construction investigates the reverse direction. Neither behavioral agreement nor a plausible activation description alone establishes that two networks use the same algorithm.

## From function programming to neural mechanisms

The [Function Space Programming thread](/pro-log/function-space-programming-thread/) began with exact neural constructions and LLM-proposed behavioral edits, then explored function discovery, compilation, shared predictive representations, and initialization. These experiments demonstrate bounded instances of function construction, including finite-domain arithmetic and statistical character prediction in small Transformers.

Stronger symbolic and statistical controls often matched or exceeded LLM proposals. Sharing predictive functions incurred a loss penalty in R12–R13, and the initialization studies did not establish that the particular synthesized functions caused the improvement. No general training-cost reduction or speedrun record was demonstrated.

These findings motivate a different question: when learned and constructed networks compute the same input-output function, what determines whether their internal mechanisms are equivalent? The original experiments remain available with their original objectives and limitations. The [concluding chapter](/pro-log/function-space-programming-conclusion/) reports both positive and negative evidence; the training-replacement phase is concluded.

## Research questions

- **Discovery:** What computations do learned networks implement, and which causal interventions support an explanation?
- **Construction:** Can a specified computation be implemented directly in neural parameters?
- **Equivalence:** When two networks agree behaviorally, do their intermediate computations and counterfactual responses also agree under an appropriate correspondence?
- **Organization:** How do computations share representations, compose, interfere, and develop during learning?

Function Space Programming remains a construction methodology. LLM assistance is an experimental variable, not a prerequisite for the broader program.

## First investigation: learned and constructed arithmetic

The proposed starting point is modular addition. Compare trained networks with analytically constructed lookup and Fourier-based solutions, under explicitly matched or reported architectural budgets. An independently synthesized solution can serve as an additional arm if its computational specification can be verified.

The constructed networks provide known mechanisms against which to test interpretation methods. Compare behavioral agreement, representation geometry, causal interventions, and the fidelity of mechanistic explanations on held-out counterfactuals. Circuit exchange is a further test, not by itself proof of identical algorithms.

This is a proposed experiment, not a reported result. The aim is to establish a diagnostic methodology before moving to natural-language models.

## Related work

- [Progress Measures for Grokking via Mechanistic Interpretability](https://arxiv.org/abs/2301.05217) — learned Fourier-based modular arithmetic.
- [Tracr: Compiled Transformers as a Laboratory for Interpretability](https://arxiv.org/abs/2301.05062) — program compilation and known mechanisms.
- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html) — shared neural feature representations.

- [InterpBench](https://proceedings.neurips.cc/paper_files/paper/2024/hash/a8f7d43ae092d9a5295775eb17f3f4f7-Abstract-Datasets_and_Benchmarks_Track.html) — semi-synthetic Transformers with known circuits for testing interpretability methods.
- [MIB](https://arxiv.org/abs/2504.13151) — mechanistic interpretability evaluation.

Known-circuit benchmarks already exist. The proposed arithmetic comparison is a diagnostic starting point, not a novel benchmark claim. A potential research question is whether causal correspondence and exchangeability tests distinguish functionally identical but algorithmically distinct networks, especially when representations are mixed or redundant.

These are precedents for the program, not evidence of its novelty. Any contribution must be established against the relevant literature and empirical controls.

## Research threads

[Function Space Programming](/pro-log/function-space-programming-thread/) — prior experiments in explicit function discovery, compilation, and representation sharing.

[ALOPEX](/pro-log/alopex-thread/) — earlier research into correlative learning and activation-space credit assignment.

[Pro-Log index](/pro-log/)
