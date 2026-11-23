---
slug: /function-space-programming-frozen-functions
title: "Frozen Functions Before Backpropagation"
description: "R19–R25: teacher-free geometric feature programs, trained representation compression, and controls for LLM-assisted synthesis."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming-frozen-functions/"
allow_html: true
options_toc: true
template: article.html
---

[← Function Space Programming research thread](/pro-log/function-space-programming-thread/)

**Research update · November 23, 2026**

## Can predicted functions substitute for learned features?

The central question in function space programming is whether a language model can describe useful computations before a target network learns them through backpropagation. A program of ReLU features can be compiled into conventional weight matrices; exact compilation is not the same as predicting the *right* features. We therefore separate the compiler, frozen-feature utility, and optimization benefit.

## The first ten functions were insufficient

R19 compiled ten task-specific stroke functions into an untrained MNIST network. Its original classifier reached **13.03%** on the development split. With a fitted ridge readout in R22, the same frozen features reached **36.46%**. Three random ten-feature controls averaged **41.01%**. The synthesized functions did not win this comparison.

Across three independently trained 128-hidden-unit teachers, the learned activations were much more consistent: mean teacher-to-teacher linear CKA was approximately **0.972**. The synthesized-to-teacher CKA averaged **0.326**, but higher CKA than the random controls did not imply better classification.

[Read R22 results](https://github.com/protimroy/function_space_programming/blob/research/r22-representation-alignment/runs/r22/results.json).

## A compact teacher representation is possible, but not free

R23 fitted PCA on *trained* teacher activations, then evaluated frozen projected features with a ridge classifier. Ten PCA dimensions retained **87.78%** mean development accuracy, compared with **95.13%** for the full 128-feature teacher. The teachers' effective ranks averaged approximately **15.6**.

This does not imply that ten standalone ReLU neurons can replace the 128-neuron teacher: each PCA coordinate still depends on the teacher's full nonlinear feature computation. PCA is a teacher-conditioned compression reference, not teacher-free function discovery.

[Read R23 results](https://github.com/protimroy/function_space_programming/blob/research/r23-functional-basis-discovery/runs/r23/results.json).

## R24: thirty-two executable local functions

R24 used a more expressive program of **32 spatially positioned 3×3 patch-ReLU detectors** on 7×7 pooled MNIST images. The feature extractor was fixed, and a ridge classifier was fitted using 50,000 training images; evaluation used the remaining 10,000 training images as development data. The official MNIST test split was not accessed.

The exploratory, LLM-authored program reached **77.54%** development accuracy. Five random programs with matched per-atom weight norms and biases averaged **73.56%**. The result supports the utility of geometric structure, not yet an independent LLM-generation advantage: the candidate was authored after exposure to previous results, and the readout was trained.

[Candidate program](https://github.com/protimroy/function_space_programming/blob/research/r24-teacher-free-synthesis/runs/r24/candidate_01.json) · [R24 results](https://github.com/protimroy/function_space_programming/blob/research/r24-teacher-free-synthesis/runs/r24/results.json).

## R25: perturb the structure, not just the weights

The first R25 control audit reused the **same exploratory candidate** and added three five-seed control families.

| Frozen feature program | Mean development accuracy | Best individual control |
| --- | ---: | ---: |
| Original 32-function program | **77.54%** | — |
| Norm-matched random coefficients and positions | 74.32% | 76.04% |
| Position permutation | 73.56% | **78.09%** |
| Within-function coefficient permutation | 72.78% | 76.09% |

The original program beat all three *control means*, but one position permutation exceeded it. These controls do not match the complete activation covariance, and the single feedback-informed candidate is not an independent test of LLM function discovery.

[R25 exploratory results](https://github.com/protimroy/function_space_programming/blob/research/r25-independent-synthesis-controls/runs/r25/exploratory_smoke.json) · [Evaluation protocol](https://github.com/protimroy/function_space_programming/blob/research/r25-independent-synthesis-controls/experiments/R25_README.md).

## What must happen next?

The next experiment must generate multiple function programs in genuinely independent contexts from a frozen prompt, record raw responses, model identity, token usage and intervention history, and evaluate *all* candidates. Human-designed geometric features, a backprop-trained matched architecture, and stronger activation-aware controls are also needed.

Only after independent synthesis succeeds should we test injection into a wider model and measure time-to-target, FLOPs, wall time, and energy. None of the present MNIST results demonstrates a speedrun record or an end-to-end training-cost advantage.

[Research repository](https://github.com/protimroy/function_space_programming) · [Research thread index](/pro-log/function-space-programming-thread/)
