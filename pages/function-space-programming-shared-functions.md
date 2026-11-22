---
slug: /function-space-programming-shared-functions
title: "Shared Functions, Lost Information"
description: "R12 and R13: suffix distribution sharing, KL clustering, and sparse residuals in character prediction."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming-shared-functions/"
allow_html: true
options_toc: true
template: article.html
---

[← Thread index](/pro-log/function-space-programming-thread/) · [Part I: Constructing functions](/pro-log/function-space-programming/)

## Shared Functions, Lost Information

*Function Space Programming · Part II · November 22, 2026*

###### Can one function stand in for many contexts?

A language model needs different next-token predictions in different contexts. If many contexts have similar predictive distributions, perhaps they can reuse a small library of functions instead of each storing an independent distribution. The attraction is straightforward: fewer distinct functions could mean less memory and less work to construct a model. The danger is equally straightforward: superficially similar contexts may differ precisely where prediction quality matters.

R12 tested direct sharing of suffix-conditioned character distributions. R13 replaced Euclidean grouping with a KL-related objective and allowed sparse, context-specific logit corrections. Neither experiment injected these predictors into Transformer weights. They test the representation hypothesis before a neural implementation.

###### The data and what is held constant

Both experiments used Karpathy's Tiny Shakespeare, verified against the SHA-256 checksum in the research loader. The corpus was split contiguously 80/10/10, and the training portion was truncated to its first 100,000 characters. The validation and test portions contained 111,539 and 111,540 characters respectively. The experiments used a four-character history and additive smoothing of 0.5.

These predictors are not directly comparable to the earlier R11 Kneser–Ney compiled Transformer: the smoothing, function family, and evaluation procedure differ. In particular, R11's 3.0092 test BPC is **not** a matched baseline for the R12/R13 numbers.

###### R12: sharing by Euclidean similarity

R12 clustered suffix contexts using squared distance between their smoothed next-character probability vectors. Each cluster pooled its member counts. A hierarchical variant additionally combined shared, local, and shorter-context counts, but did not match the pure clustering arm's storage budget.

| R12 method | Validation BPC | Test BPC |
| --- | ---: | ---: |
| Independent contexts | 3.4445 | **3.5342** |
| 16 shared functions | 3.9209 | 3.9944 |
| 64 shared functions | 3.7297 | 3.8154 |
| 256 shared functions | 3.7222 | 3.8077 |
| Hierarchical, 256 functions | 3.6810 | 3.7665 |

*Lower BPC is better. R12 used 111,536 scored test characters.*

Increasing from 64 to 256 clusters improved the pure shared model by only 0.0077 BPC. Hierarchical correction improved over pure 256-cluster sharing by 0.0412 BPC, but remained 0.2323 BPC worse than independent contexts. This is a negative result for the tested sharing rule, not a proof that reusable predictive functions are impossible.

The reported 64-cluster build took 26.59 seconds; 256 clusters took 105.15 seconds. These are implementation-specific CPU wall times, not FLOP or energy measurements.

###### R13: KL-oriented sharing and sparse residuals

R13 changed the objective to count-weighted assignment by cross-entropy (equivalent to minimizing KL divergence up to a context-dependent constant). It then used a sparse additive correction in logit space:

```text
logits(context, token) =
    log(shared_distribution[cluster(context), token])
    + sparse_context_correction(context, token)
```

Probabilities are renormalized after the correction. R13 searched 16, 64, and 256 clusters, with 0, 1, 2, 4, or 8 corrected token logits per context. Selection used validation loss among candidates satisfying an accounted storage ratio of at most 0.5. The selected candidate was then scored on test.

| R13 result | Measured value |
| --- | ---: |
| Selected clusters | 64 |
| Corrected logits per context | 8 |
| Validation BPC | 3.5892 |
| Test BPC | **3.6719** |
| Independent test BPC | 3.5342 |
| Test degradation | +0.1377 BPC |
| Accounted stored bytes | 891,964 |
| Independent stored bytes | 2,647,476 |
| Storage ratio | 33.69% |
| Cluster fit wall time | 0.246 s |

The selected representation reduced the *accounted* storage by 66.31% while worsening test loss by 0.1377 BPC. It failed the prespecified test-loss target of at most 3.55 BPC.

The storage ledger includes cluster centers, context assignments, context keys, and sparse residual indices and values. It excludes shared backoff tables, code, and runtime buffers. The independent reference uses float32 storage in the ledger, while probabilities are evaluated in float64. Therefore the 66.31% figure is not a complete deployment-memory reduction.

###### What does the negative result mean?

Shared functions are not automatically interchangeable. A function library saves representation capacity only if its corrections retain the distinctions that matter to held-out prediction. The sparse correction partially recovered the gap relative to R12's 64-cluster arm, but that cross-experiment comparison changes more than one variable and does not isolate the effect of KL assignment.

The R13 clustering fit was much faster than R12's Python implementation, but the timings are not a controlled benchmark of the same algorithm. Neither run measured electrical energy, neural inference FLOPs, or language-model proposer tokens.

Most importantly, this work does **not** show that a fresh GPT can acquire language competence by receiving externally compiled functions. That is the next experiment.

###### Where the thread goes next

The next chapter will test actual neural function injection, not another statistical table. Its intended arms are random initialization with AdamW, zero-update function compilation, compilation with trainable residuals, and compilation with full AdamW. Comparisons must include the cost of constructing and installing functions and evaluate generalization on held-out language.

No outcome for that experiment is reported here.

**Sources:** [R12 implementation](https://github.com/protimroy/function_space_programming/blob/research/r12-shared-suffix-2026-11-21/experiments/r12_shared_suffix.py) · [R13 implementation](https://github.com/protimroy/function_space_programming/blob/research/r13-kl-sparse-2026-11-22/experiments/r13_kl_sparse.py) · [Tiny Shakespeare source](https://github.com/karpathy/char-rnn/tree/master/data/tinyshakespeare)

[← Part I](/pro-log/function-space-programming/) · [Thread index](/pro-log/function-space-programming-thread/)
