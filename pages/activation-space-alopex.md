---
slug: /activation-space-alopex
title: "Activation-Space ALOPEX"
description: What happens when correlative learning measures consequences inside a neural network?
canonical_url: "https://www.protimroy.com/pro-log/activation-space-alopex/"
allow_html: true
options_toc: true
template: article.html
---


<style>
  .research-thread-nav { margin: 0 0 1.5rem; padding: .8rem 1rem; border-left: 3px solid #304d72; background: rgba(35,55,85,.07); font: 14px/1.65 'Inter', sans-serif; }
  .research-thread-nav a { text-decoration: underline; text-underline-offset: 2px; }
  .research-thread-nav .research-thread-meta { display: block; font-size: 12px; opacity: .8; margin-top: .25rem; }
  @media(max-width:600px) { .research-thread-nav { padding: .7rem .8rem; } }
</style>
<nav class="research-thread-nav" aria-label="ALOPEX research series">
  <a href="/pro-log/alopex-thread/">ALOPEX research thread</a> · <a href="/pro-log/alopex-partial-negative-result/">Broader findings</a>
  <span class="research-thread-meta">Research series · Updated November 22, 2026</span>
</nav>

###### The Question

ALOPEX is a family of methods that uses perturbations and their observed consequences to guide learning. In a neural network, the difficult question is not only whether a change improved the loss. It is how to assign that outcome to the parts of the network that caused it.

Activation-Space ALOPEX changes where that question is asked. Instead of perturbing a large vector of weights, it intervenes at a hidden representation, measures the downstream consequence, and uses the input to that layer to construct local parameter evidence. The method retains correlative memory, but it does not eliminate the need for task-relevant measurements or prove that the resulting credit is complete.

The experiments below are a research record, not a claim that ALOPEX has replaced backpropagation. They include a single-seed MNIST reproduction, a short sensor-control pilot, and a separate learned-credit hybrid. Their architectures, budgets, and methods differ.

###### From Global Consequence To Local Credit

The original ALOPEX work used correlations between perturbations and responses to identify visual receptive fields. Later work adapted correlative learning to feedforward and recurrent neural networks. The recovered mini-batch ALOPEX translation is a narrower historical starting point: its default includes gradient-seeded warmup, so it is not strictly gradient-free throughout. The written thesis is available, but equivalence between the recovered translation and the exact submitted notebook is unresolved.

The subsequent recovered branches changed how consequences were attributed:

| Branch | Intervention or measurement | What it addressed | What remained |
| --- | --- | --- | --- |
| Historical-Credit | Credit a previous move using a later loss change | Avoid explicit paired probes | A global, potentially stale signal |
| Same-Batch Replay | Re-evaluate the same examples after the move | Improve loss pairing | Several moving layers can still share one consequence |
| Block-Replay | Restrict a replayed intervention to one block | Make spatial attribution less ambiguous | Local credit is still incomplete |
| Activation-Space | Perturb hidden preactivations and reconstruct local evidence | Change the measurement space | Finite probes still cover only sampled directions |

The archive does not support a complete account of every version between Block-Replay and the recovered Activation-Space branch. Missing versions should not be read as failed experiments.

###### Measuring In Activation Space

Consider a hidden preactivation `a`, an example loss `E`, a direction `u`, and a probe radius `sigma`. A paired measurement compares the loss after opposite interventions:

```text
c = [E(a - sigma u) - E(a + sigma u)] / (2 sigma)
```

The sign convention makes `c u` a favorable-direction signal. Averaging over sampled directions estimates hidden credit; it is not automatically the full gradient. Crucially, the implementation keeps the consequence per example before using cached layer inputs to construct weight evidence. It also scales the probe radius with a running estimate of activation magnitude.

The recovered hybrid-head variant uses a supervised local output signal. Thus, even when the hidden sensor uses function evaluations, a description of the complete method must also specify what happens at the output and how evidence drives updates.

###### Experiments, Kept Separate

:::interactive alopex-family-evidence.js Recorded experiment outcomes
These are different cohorts, not a combined leaderboard. Percentages are accuracy.
:::

The MNIST table is a **single-seed, eight-epoch** frozen reproduction on a shared-initialization 784-to-1024-to-10 model. Its best test accuracies are descriptive, not an uncertainty estimate. In this run the hybrid-head variant took about 206 seconds versus about 30 seconds for AdamW; equal epochs are not equal compute.

The 390-step pilot used two seeds and held-out training validation. Replacing the repaired derivative-free sensor with matched per-example JVPs changed the two outcomes by **+0.04 and -1.94 percentage points**. The mixed result does not show that exact derivatives are generally unhelpful; it says this substitution did not consistently improve the tested learner in this short pilot.

The learned-credit CIFAR-10 cohort is a different method and experiment. Its three paired seeds, 50-epoch horizon, and residual-MLP architecture must not be pooled with either result above. Its practical five-point engineering criterion is not an equivalence test.

###### Exactness Is Not Coverage

An exact directional derivative answers how the loss changes along one chosen direction. A finite difference approximates the same kind of directional measurement, with error that depends on the probe radius and local function. Neither reveals components outside the measured span.

```text
useful credit = credit in the measured span + credit outside it
```

Cleaner coefficients can improve what is measured without recovering what is missing. In the separate 64-hidden parameter-JVP sweep, recorded final accuracy increased from 50.56% at one direction to 85.97% at 64 directions while elapsed time rose from about 34 to 539 seconds. That is one run under one protocol, not a universal monotonicity result or a direct comparison with the 1024-hidden activation-space run. An older finite-difference versus JVP frozen control failed its measurement contract and should not be used as a causal comparison.

###### The Family Branches

**Activation-Space ALOPEX** uses antithetic hidden interventions, per-example consequences, local reconstruction, and persistent correlative state. Its recovered rule is distinct from the later two-timescale branch.

**Activation-JVP ALOPEX** replaces finite hidden-space consequences with exact directional derivatives while retaining a C/S-style state and clipped update. A recovered digits source establishes a mechanism and update ordering; it is not a fresh rerun or complete recovery of the historical program.

**Two-Timescale Activation-Space ALOPEX** uses function evaluations for its sensor, persistent low-rank C/S state, and a separate full transient path for current credit. Basis refresh and state transport are part of the method; the elementwise slower-state transport is a heuristic, not exact covariance transport.

**Matched-JVP Control** changes the repaired branch's sensor while retaining its C/S comparison target and actuator. This is the short pilot above, not a full-horizon final comparison.

**Learned Credit-Map Hybrid** uses sparse directional measurements to train a map from output residuals to hidden credit and applies the reconstructed parameter evidence with AdamW. It changes both persistent representation and actuator, so its complete-method results cannot isolate the effect of a better sensor. It is ALOPEX-inspired, not a purely derivative-free ALOPEX implementation.

###### What The Results Do And Do Not Show

The experiments show a useful way to restructure the credit problem: intervene in a representation, retain example-level consequences, and reconstruct local parameter evidence. They also show that improving a sensor is not the same as acquiring enough directional coverage.

In the recorded learned-credit residual-MLP scaling family, the depth-32 cohort exceeded the project's five-percentage-point gap criterion. An off-policy layerwise oracle diagnostic at width 512, depth 32 (epoch 20, two calibration seeds) clarifies why: hidden-credit cosine alignment falls monotonically from 0.998 immediately below the linear head (stage 31; 99.4% of the oracle single-layer loss drop) to 0.675 at the earliest stage (stage 0; 37.9% of the oracle loss drop), and even a noise-free fresh mean Jacobian (0.721) or oracle ridge-fitted shared matrix (0.732) cannot recover input-conditioned Jacobian variation across 31 nonlinear blocks. A corrected resident-step benchmark measured 5.203 ms for the hybrid and 2.104 ms for AdamW in one session; that is not end-to-end training throughput. In a separate five-seed CIFAR-10 convolutional probe extension, extending training from 390 to 1,170 steps raised validation accuracy from 39.14% to 42.26% while AdamW rose from 51.95% to 58.06%, widening the gap from 12.80 to 15.79 percentage points. A separate 113.3-million-parameter two-timescale result demonstrates execution, not competitive convergence. No recorded autoregressive small-language-model training result establishes transfer to that setting.

The source's separate schema-v2 campaign remains staging. It cannot support new headline performance, causal, or multiseed conclusions until complete and its release checks pass. No experiment was rerun for this article.

###### Sources And Further Reading

- [ALOPEX: A Partial Negative Result](/pro-log/alopex-partial-negative-result/) contains the wider research narrative, derivations, evidence boundaries, references, and reader-data download.
- [Frozen MNIST and parameter-JVP statistics](/pro-log/assets/alopex/family-frozen-statistics-d86e9abd96be.json) are the source reader's frozen single-seed record, including the unexecuted large-model arm.
- [Harth and Tzanakou, 1974](https://doi.org/10.1016/0042-6989(74)90024-8), the original receptive-field ALOPEX record.
- [Unnikrishnan and Venugopal, 1994](https://doi.org/10.1162/neco.1994.6.3.469), ALOPEX for feedforward and recurrent networks.
- [Bia, 2001](https://doi.org/10.1142/S0129065701000928), ALOPEX-B.
- [Roy, 2023](https://hdl.handle.net/10214/27818), *Mini-Batch Alopex-b For Training Neural Networks*.

The pilot and learned-credit values are reader-replay summaries from `src/data/chapterCloseEvidence.js`, included in the wider article's evidence download. These are distinct records, not independent replications performed for this page.