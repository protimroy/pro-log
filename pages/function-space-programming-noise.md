---
slug: /function-space-programming-noise
title: "Function Space Programming: Toward a Noise Speedrun"
description: "R32–R33 function discovery and weight compilation results, limitations, and a controlled local-first Noise experiment."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming-noise/"
options_toc: true
template: article.html
---

[← Function Space Programming thread](/pro-log/function-space-programming-thread/)

**Protim Roy · November 23, 2026**

###### From small function experiments to a forward-only training benchmark

The applied goal is to test whether a language-model-proposed function can be compiled into neural parameters cheaply enough to reduce training compute. The first target is the Q Labs Noise forward-only pretraining benchmark; nanoGPT remains a later target. This is a research plan, not a speedrun result.

###### What R32 established

Given 40 observed pairs from a modular-affine mapping, the assistant inferred `f(a,b)=(2a+6b) mod 11`. The candidate predicted all 40 validation and 41 audit pairs correctly. An exhaustive symbolic affine solver also achieved 100%, so the experiment demonstrates feasibility of function inference, not superiority to classical fitting. The function family was disclosed in the protocol, so this was not a fully hypothesis-class-blind synthesis test.

[Candidate and evaluation](https://github.com/protimroy/function_space_programming/tree/research/r32-blind-function-discovery/runs/r32)

###### What R33 established

R33 represented the known mapping as a fixed 11-by-121 linear weight matrix over engineered one-hot input pairs. The compiled arm achieved 100% validation accuracy before training. Position-shuffled, output-permuted and random arms started near chance, but all reached 100% by step 200. Across three seeds, compiled final cross-entropy was approximately 0.000268, compared with approximately 0.006142 for random initialization. There was no demonstrated runtime advantage. Neither synthesis cost nor energy was measured.

[Three-seed R33 evidence](https://github.com/protimroy/function_space_programming/tree/research/r33-function-compiled-weights/runs/r33)

###### The gap to Noise

A 121-entry exact lookup is not an initialization strategy for a 37.7-million-parameter language model. The function must be translated into useful model-compatible structure without access to validation labels, without altering the fixed model architecture, and without violating Noise's forward-only rule. The central question is whether it improves loss reduction per second and per forward compute beyond distribution-matched controls.

###### N-FSP-01: local-first controlled experiment

The [preregistered Noise protocol](https://github.com/protimroy/noise-speedrun-research/blob/research/n-fsp-01-function-initialization/experiments/N_FSP_01_PROTOCOL.md) calls for four paired arms: baseline, function-derived, norm-matched random, and structure-shuffled. First audit the pinned upstream trainer and implement a reversible initialization hook. Then use an RTX 3080 for short 2M-model compatibility runs and three-seed pilots, followed by 7M and 38M only if the mechanism survives controls. Reserve 8×H100 for justified official-scale evaluation.

The repository's pinned October benchmark specification names validation cross-entropy 4.2 as the speedrun threshold; other internal experiments reference 3.5. Those are not interchangeable, and current official eligibility must be verified before a record claim.

###### Current status

As of November 23, 2026, N-FSP-01 has a committed protocol, but no verified initialization-hook implementation or Noise GPU results. A successful synthetic function compilation is not evidence of improved Noise training.

[Noise research repository](https://github.com/protimroy/noise-speedrun-research) · [Linear tracking](https://linear.app/protimroy/issue/B-172/n-fsp-01-local-first-function-derived-noise-initialization-with)
