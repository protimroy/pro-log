---
slug: /function-space-programming-thread
title: "Function Space Programming — Research Thread"
description: "A linked research sequence from exact neural constructions to language-model function compilation."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming-thread/"
allow_html: true
options_toc: true
template: article.html
---

## Function Space Programming

*Research thread · Updated November 23, 2026*

**Can we construct the functions a neural network would otherwise learn, install them into its architecture, and reduce the training required to acquire a capability?**

This thread follows the question through increasingly demanding tests. It distinguishes three claims: a function can be constructed exactly; an externally proposed function can be compiled into a neural network; and doing so can improve generalization or end-to-end compute relative to training. The first two have bounded demonstrations. The third remains unresolved.

## Read the thread

1. **[Part I — From XOR to neural function injection](/pro-log/function-space-programming/)**. Exact Boolean construction, MNIST fixed features, LLM-proposed edits, symbolic controls, and finite-domain Transformer compilation. The experiments demonstrate mechanisms, not GPT-scale language acquisition.
2. **[Part II — Sharing predictive functions: R12 and R13](/pro-log/function-space-programming-shared-functions/)**. A negative result for naive suffix sharing, followed by KL clustering and sparse residual corrections. Compression is substantial; the accuracy threshold is missed.
3. **[Part III — Frozen functions before backpropagation](/pro-log/function-space-programming-frozen-functions/)**. R19–R28: compiled MNIST features, teacher-representation PCA, 32-function synthesis and matched controls, spatial-placement search, and ten-seed AdamW initialization comparisons. The results do not yet demonstrate an LLM-specific advantage or end-to-end training-cost savings.
4. **Part IV — Transformer function injection (planned).** Compare random training, zero-update compilation, residual adaptation, and full fine-tuning in an autoregressive Transformer. No result is claimed yet.

## Reading guide

The chapters are separate pages, not one continuously expanding article. Each page should stand alone with its question, experimental protocol, measured evidence, limitations, and links to adjacent chapters. A later experiment must not retroactively turn an earlier demonstration into evidence for a stronger claim.

The sequence is inspired by the linked, cumulative research exposition of [Distill's Circuits thread](https://distill.pub/2020/circuits/) and [Transformer Circuits](https://transformer-circuits.pub/), rather than a chronological stream of disconnected posts.

## Evidence and status

The [research code](https://github.com/protimroy/function_space_programming) is the primary executable record. R12 and R13 measurements were supplied from a local workstation run; this editorial update did not independently rerun them. The reported CPU timings are not electrical-energy measurements.

**Latest:** [Part III — Frozen functions before backpropagation](/pro-log/function-space-programming-frozen-functions/).
