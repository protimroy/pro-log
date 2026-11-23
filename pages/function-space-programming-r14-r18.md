---
slug: /function-space-programming-r14-r18
title: "Function Synthesis Between Sharing and Compilation"
description: "R14–R18: Transformer injection, MNIST function proposals, reconstruction, teacher-free synthesis, and control design."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming-r14-r18/"
allow_html: true
options_toc: true
template: article.html
---

[← Research thread](/pro-log/function-space-programming-thread/) · [Next: Frozen Functions →](/pro-log/function-space-programming-frozen-functions/)

**Research note · November 23, 2026**

## Why these experiments matter

R12–R13 examined whether predictive functions can be shared and compressed. R14–R18 shifted toward proposing, reconstructing, and testing explicit functions before the R19–R28 compiled-feature experiments. This is a **protocol and evidence-status record**, not a claim that all five experiments produced successful results.

## R14 — Transformer function injection

The [R14 branch](https://github.com/protimroy/function_space_programming/tree/research/r14-transformer-function-injection) investigates inserting a specified function into a Transformer. The branch exists, but a completed R14 result and its measured comparison have **not yet been independently verified for this article**. No accuracy or training-cost claim is made here.

## R15 — LLM-specified functions on MNIST

[R15 protocol](https://github.com/protimroy/function_space_programming/blob/research/r15-mnist-llm-function-synthesis/experiments/R15_README.md) defines an assistant-authored seven-segment spatial hypothesis. It separates a **zero-fit** rule classifier, a ridge readout fitted on those same features, and a 217-feature designed ridge baseline. The zero-fit program was **not yet a compiled MLP weight tensor** in the documented protocol. The protocol requires recording prompts, candidates, token costs, and interventions before claiming LLM synthesis advantage. No numerical result is reported here without a verified run artifact.

## R16 — Reconstruct learned MNIST functions

[R16 protocol](https://github.com/protimroy/function_space_programming/blob/research/r16-mnist-learned-function-reconstruction/experiments/R16_README.md) trains a 784→128→10 ReLU teacher, then studies hidden-layer reconstruction and rank-8/16/32/64 SVD controls. The proposed LLM reconstruction stage uses a compressed teacher inspection, while reusing the teacher's output layer and hidden biases. **SVD is not LLM synthesis**, and teacher-conditioned reconstruction cannot establish that teacher training was avoided. No unverified numerical reconstruction results are asserted.

## R17 — Teacher-free function synthesis

[R17 protocol](https://github.com/protimroy/function_space_programming/blob/research/r17-teacher-free-function-synthesis/experiments/R17_README.md) specifies one assistant-authored deterministic image-processing classifier: foreground crop, interpolation to a 7×5 grid, and fixed digit-template matching with translation tolerance. It does not fit MNIST weights, but **was not yet compiled into neural-network weights**. Zero fitted parameters also does not mean zero authoring or inference cost.

## R18 — Controlled function-prior pilot

[R18 protocol](https://github.com/protimroy/function_space_programming/blob/research/r18-function-prior-controlled/experiments/R18_README.md) defines a common binary-glyph program schema and a harness for comparing the R17 authored candidate with seeded random glyphs and any externally generated candidates. The checked-in README explicitly says **evaluation harness committed; no R18 results or LLM API calls yet**. Equal evaluation counts would still not match the random candidates' structural prior.

## What the sequence establishes

These branches document a progression in experimental design: function injection, handcrafted or assistant-authored feature proposals, teacher-conditioned reconstruction, teacher-free rule systems, and controlled comparisons. **They do not, by themselves, demonstrate an independent LLM-specific advantage, a compiled training-free MNIST classifier, or lower end-to-end training cost.**

[Next chapter: R19–R28 compiled functions and initialization controls →](/pro-log/function-space-programming-frozen-functions/)
