---
slug: /function-space-programming
title: "Function Space Programming"
description: "An exact XOR construction, a fixed-feature MNIST baseline, and a controlled experiment for LLM-proposed behavior edits."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming/"
allow_html: true
options_toc: true
template: article.html
---

**Protim Roy · November 21, 2026**

###### Specify the change in behavior

Suppose a classifier works on most inputs, but I want to change its answer in one part of the input space. I can describe the edit as a function: what should change, where it should change, and which behavior should be preserved. Can a language model translate that specification into a small executable patch?

I call this research direction **LLM-assisted function space programming**. Given a frozen predictor `f`, the language model proposes an explicit correction `delta`, and the edited predictor computes `f(x) + delta(x)`. A patch can be evaluated directly on a target slice and on inputs whose predictions should be preserved. This is a choice of interface. The correction can still be represented by neural-network weights.

The project was prompted by Takehi, Teoh, Zhang, and Khattab's [Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/), which explores language models reading and editing weights as a program. My experiment asks what happens when the language model receives a behavior specification and emits a function in a constrained grammar. The name identifies the research direction. A broader comparison with prior model editing, symbolic regression, and program synthesis is still open.

###### XOR: construct a function exactly

On Boolean inputs, XOR has a two-unit ReLU representation:

```text
f(x1, x2) = ReLU(x1 - x2) + ReLU(x2 - x1) = |x1 - x2|
```

The two hidden units each compute one direction of the difference, and the output adds them. I assigned the weights and biases to implement that expression directly. The network returned `[0, 1, 1, 0]` in lexicographic input order, matching all four cases exactly. The expression also defines a continuous score on the unit square, which gives a later editing experiment room to test nearby behavior.

###### MNIST: compare three fixed feature maps

The next baseline asks how much a specified feature map can do before any learned feature extractor enters the experiment. I used the standard 60,000 training and 10,000 test images. Each arm standardizes features using its training split and fits a ten-output ridge head with regularization coefficient 100 and an unpenalized intercept. The predicted class is the largest output score.

<div role="region" aria-label="MNIST held-out accuracy" tabindex="0" style="max-width:100%;overflow-x:auto">
<table class="table is-striped is-fullwidth">
<caption>MNIST held-out accuracy</caption>
<thead><tr><th scope="col">Feature map</th><th scope="col">Dimensions</th><th scope="col">Test correct</th><th scope="col">Accuracy</th></tr></thead>
<tbody>
<tr><th scope="row">Raw pixels</th><td>784</td><td>8,606 / 10,000</td><td>86.06%</td></tr>
<tr><th scope="row">Designed</th><td>217</td><td>9,606 / 10,000</td><td>96.06%</td></tr>
<tr><th scope="row">Random ReLU</th><td>217</td><td>8,838 / 10,000</td><td>88.38%</td></tr>
</tbody>
</table>
</div>

The designed map uses ink statistics, center of mass, spatial pooling, image gradients, symmetry, and fixed directional stroke filters. The random ReLU arm uses a frozen Gaussian projection with seed 42 and matches the designed map's feature count. The designed map scored 7.68 percentage points higher than that particular projection. The raw-pixel arm provides a reference at a different dimensionality. Multiple projection seeds would be needed to estimate how much the dimension-matched comparison varies.

The full CPU reference and the WSL2 workstation run agreed on every correct count. I independently replayed the workstation artifacts, checked their hashes, and matched the checkpoint tensors within numerical tolerance. The source revision and the two run revisions were `cf1de5c`, `572bec2`, and `7eeb5cb`, respectively, in the research repository. These are baseline experiments with fixed computations and, on MNIST, a fitted readout. Neither run tests an LLM proposing or applying an edit.

###### R01: local edits on continuous XOR

I froze the XOR score and tested three edit locations on the unit square, near (0, 0), (1, 0), and (0.28, 0.28). A patch had to flip the thresholded class within Chebyshev distance 0.10 of the task center and preserve the score outside distance 0.25. I measured the intervening band separately. The patches were additive signed tents with bounded center offsets, radii, and amplitudes.

ChatGPT proposed eight parameter tuples from the task specification before seeing any sampled points or scores. Structured search and uniform random search also scored eight proposals per task on development samples. A closed-form patch served as an analytic reference. Each task used 256 development and 4,096 held-out points per region. Random search was repeated 20 times per task. The table averages held-out metrics across tasks and, for random search, across repetitions.

<div role="region" aria-label="Continuous XOR pilot results" tabindex="0" style="max-width:100%;overflow-x:auto">
<table class="table is-striped is-fullwidth">
<caption>Continuous XOR pilot results</caption>
<thead><tr><th scope="col">Method</th><th scope="col">Target success</th><th scope="col">Protected agreement</th><th scope="col">Protected mean drift</th><th scope="col">Boundary mean drift</th></tr></thead>
<tbody>
<tr><th scope="row">Unedited</th><td>0%</td><td>100%</td><td>0</td><td>0</td></tr>
<tr><th scope="row">Analytic reference</th><td>100%</td><td>100%</td><td>0</td><td>0.140</td></tr>
<tr><th scope="row">Structured search</th><td>100%</td><td>100%</td><td>0</td><td>0.122</td></tr>
<tr><th scope="row">ChatGPT proposals</th><td>100%</td><td>100%</td><td>0</td><td>0.133</td></tr>
<tr><th scope="row">Uniform random search</th><td>88.53%</td><td>96.82%</td><td>0.0169</td><td>0.386</td></tr>
</tbody>
</table>
</div>

The selected ChatGPT patch reached 100% target success with zero protected score drift across all three tasks. Structured search matched both outcomes and had lower average drift in the band between the edit and protected regions. Giving every method the exact task center made this a useful locality check, and the structured control shows why uniform random search alone would overstate the evidence for LLM assistance. These were three tasks and one ChatGPT proposal batch.

###### Next experiment: infer an edit from examples

The next test will give the model and controls labeled examples of the desired changes and preservation constraints, with the location and shape of the edit left to infer. I will compare the language model with a fitted geometric control and budget-matched search before carrying the protocol to a predefined MNIST confusion slice.
