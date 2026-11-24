---
slug: /function-space-programming-conclusion
title: "Function Space Programming: A Partial Negative Result"
description: "What explicit neural function construction achieved, where stronger controls prevailed, and why the training-replacement investigation is concluding."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming-conclusion/"
allow_html: true
options_toc: true
template: article.html
---

[Research thread](/pro-log/function-space-programming-thread/) · [Previous chapter](/pro-log/function-space-programming-frozen-functions/)

Research conclusion · November 23, 2026

## The original hypothesis

Can a language model discover useful functions from data, compile them into neural parameters, and replace or reduce the target model's training? We investigated this through behavioral edits, exact constructions, statistical language prediction, feature synthesis and initialization. The experiments established several bounded capabilities, but did not establish an LLM-specific advantage or a general reduction in end-to-end training cost. This is a partial negative result, not evidence that explicit neural computation is impossible.

## What worked

| Experiment | Result | Scope |
| --- | --- | --- |
| XOR | All four Boolean cases correct with zero updates | Analytic construction of a known function |
| R01 | 100% target edit success, zero protected-score drift | Structured search matched the LLM on three local edits |
| R04 | 312/312 held-out subtraction predictions after injection into a frozen Transformer | Used learned operand representations, calibrated probes and a gated residual write |
| R06–R08 | Correct unseen arithmetic compositions at zero optimizer updates | Restricted grammars and finite-domain compilation; symbolic controls matched |
| R09–R11 | Statistical text predictors executed in compiled Transformer weights | Short-context character prediction, not general language competence |
| R32 | 40/40 validation and 41/41 audit predictions | Blind affine modular discovery; a matched symbolic solver also achieved every answer |

The R11 compiled decoder achieved 3.009211 test bits per character, versus 3.036408 for the mean of three AdamW starts at the matched decoder parameter budget. Its maximum probability discrepancy from the direct predictor was 1.17e-7. Compilation worked; that does not establish that the underlying statistical function was novel or cheaper than the best alternatives.

## Where the hypothesis failed to gain support

### Discovery

R02's known structural grammar allowed algebraic fitting and matched L-BFGS to outperform direct LLM proposals. R03's semantic lookup and ridge router matched the LLM. In R06–R08 and R32, symbolic controls recovered the functions. These results support explicit structural priors, not a distinctive LLM discovery advantage.

### Sharing and representation

R12's suffix clustering degraded test loss. R13 reduced accounted storage to 33.69% of the independent-context reference, but test loss increased from 3.5342 to 3.6719 bits per character, missing the prespecified 3.55 threshold. Sharing can save capacity while losing predictive distinctions.

R22's ten synthesized frozen MNIST features reached 36.46% development accuracy with a fitted ridge readout, versus 41.01% averaged over three random controls. R25's final candidates all fell below their respective mean position-permutation controls. A plausible feature description is not sufficient evidence of useful neural representation.

### Initialization: a modest benefit, ambiguous mechanism

R29 repeats the small pooled-MNIST 49→32→10 ReLU experiment with ten paired seeds and additional structure-matched controls. Values below are arithmetic means recomputed from the recorded run artifact.

| First-layer initialization | Steps to 85% validation accuracy | Terminal audit accuracy |
| --- | ---: | ---: |
| Standard random | 250 | 91.044% |
| Norm-matched random | 227.5 | 91.311% |
| Activation-matched random | 237.5 | 91.331% |
| Original synthesized functions | 215 | 91.913% |
| Function weights, zero biases | 212.5 | 91.797% |
| Shuffled spatial positions | 210 | 91.769% |
| Support-shuffled | 225 | 91.628% |
| Support-signed | 227.5 | 91.573% |
| Support-randomized | 225 | 91.427% |

The original program has the highest mean terminal accuracy in this comparison. Several variants retain much of its improvement, and two reach the threshold sooner. These are descriptive paired-run means, not a demonstration of statistical significance or of the causal benefit of the precise synthesized functions. All weights were trained after initialization; the official test split was not used in this protocol.

### Cost and language-model scale

In R11, compilation and selection took 2.42 seconds; the three AdamW starts reached the common validation target in 2.21–5.51 seconds. The direct count-model workflow took 0.028 seconds after shared data preparation. Total LLM synthesis cost and energy were unavailable. No general end-to-end cost advantage follows from zero target-model updates.

Later language-model transfer work and the Noise integration pilot did not establish a validated training-cost advantage. Structured Hadamard initialization in Noise is not a data-discovered function. These exploratory efforts are not treated as a test of the full synthesis hypothesis. R30–R31 and R33–R34 are retained as research branches; no new quantitative claims from them are made in this conclusion without checked result artifacts.

## Conclusion and scope

The strong training-replacement claim remains unsupported by these experiments. The tested LLM proposals frequently failed to outperform structural, symbolic or statistical controls. A few useful compiled functions and initialization priors were demonstrated, but their discovery cost, composition in learned representations, and transfer to realistic language modelling were not established.

We are concluding the training-replacement and speedrun phase rather than claiming impossibility. We retain exact construction, function editing, compilation, and the negative evidence as research tools. The next program asks a different question: what distinguishes a deliberately constructed computation from the computation a neural network actually learns?

The [Mechanisms of Neural Computation](/pro-log/mechanisms-of-neural-computation/) overview introduces that question. It does not retroactively reinterpret FSP as a successful mechanistic interpretability result.

## Evidence

[Public R29/R32 evidence extract](https://github.com/protimroy/pro-log/blob/master/evidence/function-space-programming/runs/fsp-conclusion/r29-r32-extract.json) includes per-seed R29 threshold and terminal results, R32 counts, source blob identifiers, and limitations. The figures were recomputed from archived artifacts, not independently rerun. The original research-repository links below may require access.

- [Part I — exact construction, edits and language prediction](/pro-log/function-space-programming/)
- [Part II — representation sharing](/pro-log/function-space-programming-shared-functions/)
- [Part III — protocols and evidence status](/pro-log/function-space-programming-r14-r18/)
- [Part IV — frozen features and initialization](/pro-log/function-space-programming-frozen-functions/)
- [R29 recorded results](https://github.com/protimroy/function_space_programming/blob/research/r29-structure-matched-controls/runs/r29/results.json)
- [R32 recorded results](https://github.com/protimroy/function_space_programming/blob/research/r32-blind-function-discovery/runs/r32/results.json)

[Research thread](/pro-log/function-space-programming-thread/) · [Next research program](/pro-log/mechanisms-of-neural-computation/)
