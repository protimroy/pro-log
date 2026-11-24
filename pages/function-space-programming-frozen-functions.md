---
slug: /function-space-programming-frozen-functions
title: "Frozen Functions Before Backpropagation"
description: "R19–R28: frozen function programs, spatial placement, and controlled AdamW initialization studies."
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

## R25 final: independently proposed geometric variants did not beat position controls

The final R25 audit evaluated three deterministic, GPT-6-selected geometric candidates against 45 matched controls (three control families × five seeds × three candidates). The contrast candidate reached **77.50%** frozen-feature ridge-probe accuracy, compared with **73.91%** for norm-matched random programs, but **77.74%** for position permutations. All three candidates fell below their respective mean position-permutation controls. The candidates were feedback-informed, not independent blind LLM generations. This is a negative result for the claim that the particular selected positions confer an advantage. [R25 results](https://github.com/protimroy/function_space_programming/blob/research/r25-independent-synthesis-controls/runs/r25/results.json).

## R26: optimize spatial placement without changing the functions

Using the fixed R25 contrast functions, a 20-evaluation local search reached **79.51%** mean final-audit accuracy across three seeds, versus **78.72%** for equal-budget random placement search and **77.50%** for the original placement. Local search won two of three seeds; this is exploratory evidence for a modest placement-search benefit, not a robustly established advantage. The ridge readout was trained. [R26 results](https://github.com/protimroy/function_space_programming/blob/research/r26-placement-and-function-init/runs/r26/results.json).

## R27–R28: inject functions, then train with AdamW

Unlike R24–R26, these experiments trained **all weights** in the same 49→32→10 ReLU MLP on 7×7 average-pooled MNIST. Compiled R25 contrast functions initialized the first layer; every arm shared AdamW settings, minibatch schedules, and paired readout initialization. The comparison is about the value of an initialization prior, not zero-training performance.

R27's three-seed pilot reached 85% validation accuracy in **200** optimizer steps on average with function injection, versus **267** for standard random initialization. At the predefined 1,000-step audit, mean accuracy was **91.98%** versus **91.04%**. [R27 results](https://github.com/protimroy/function_space_programming/blob/research/r27-function-injection-adamw/runs/r27/results.json).

R28 replicated with ten paired seeds and stronger controls:

| First-layer initialization | Mean steps to 85% validation | Mean terminal-audit accuracy |
| --- | ---: | ---: |
| Standard random | 250 | 91.044% |
| Norm-matched random | 227.5 | 91.311% |
| Activation-matched random | 235 | 91.331% |
| Function weights, zero biases | 212.5 | 91.797% |
| Functions, shuffled spatial positions | 210 | 91.769% |
| **Original function program** | **215** | **91.913%** |

The original function initialization reduced observed steps to 85% by **14%** relative to standard random and improved terminal-audit accuracy by **0.582 percentage points** over activation-matched random. Yet shuffled-position and zero-bias function variants reached 85% slightly faster; exact placement and biases do not explain most of the gain. Activation matching preserved per-channel pre-ReLU means and standard deviations, **not** feature covariance. R28 reported approximately **0.712 s** for 1,000 function-initialized steps versus **0.691 s** for standard random; it does **not** demonstrate lower total run time or end-to-end cost. [R28 results](https://github.com/protimroy/function_space_programming/blob/research/r28-initialization-mechanism/runs/r28/results.json) · [Protocol](https://github.com/protimroy/function_space_programming/blob/research/r28-initialization-mechanism/experiments/R28_README.md).

These experiments used feedback-informed function candidates, a small pooled-MNIST MLP, and no independently measured LLM synthesis cost, electricity, or FLOPs. The official test split remained untouched. They support a narrow initialization advantage, **not** a proven LLM-specific advantage or a speedrun record.

## Open questions and research transition

The original follow-up proposed larger models, sparsity/support-matched controls, and matched time-to-target comparisons. Independent LLM synthesis remains an unresolved novelty test: freeze the prompt, record all candidates and generation costs, and compare with human-designed and algorithmic controls.

No speedrun record or end-to-end cost reduction was demonstrated. The current [Mechanisms of Neural Computation](/pro-log/mechanisms-of-neural-computation/) program instead investigates why constructed and learned computations differ and whether their mechanisms can be compared causally. The initialization experiments remain part of the historical evidence, not proof of mechanistic equivalence.

[Next: Part V — A partial negative result](/pro-log/function-space-programming-conclusion/) · [Research repository](https://github.com/protimroy/function_space_programming) · [Research thread index](/pro-log/function-space-programming-thread/)
