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

###### Prior work and the next test

Compiling a known algorithm into weights has a precedent in Lindner et al.’s Tracr. Inferring the algorithm from examples adds a distinct source of error. Several expressions can agree on a small sample, a central problem in programming by example. R02 scored the inferred expression on fresh inputs and compared the compiled network against the expression itself. [Tracr](https://arxiv.org/abs/2301.05062) · [Programming by Examples](https://www.microsoft.com/en-us/research/publication/programming-examples-applications-ambiguity-resolutions-approach/)

LLM-SR already combines language-model proposals with numerical coefficient fitting. Its benchmark follow-up uses transformed and synthetic tasks to reduce the advantage of recognizing familiar equations. We will give an LLM, a symbolic search procedure and a randomly initialized backpropagation learner the same examples from unnamed piecewise-linear functions. Fitting coefficients on the LLM’s chosen expression adds a fourth comparison that isolates the value of numerical refinement. [LLM-SR](https://arxiv.org/abs/2404.18400) · [LLM-SRBench](https://arxiv.org/abs/2504.10415)

For the editing experiments, Mitchell et al.’s work on the scope of model edits motivates measuring both successful corrections and changes elsewhere. R01 established a tie with structured search when the target location was supplied. A follow-up will withhold the edit geometry and compare against a backpropagation learner with access to the same residual family. [Memory-Based Model Editing at Scale](https://arxiv.org/abs/2206.06520)

###### R02 · Discover and compile a function

A single language-model batch inferred explicit expressions for 12 hidden two-input functions. Each function had two axis-aligned ReLU hinges and an intercept. The fixed input layout made the unknown parameters identifiable from five rounded labels. The language model used those five and reused its proposals in both sample budgets. A separate coefficient-refitting arm used all the labels in each budget.

At eight examples, median normalized test RMSE was 0.0000117 for direct compilation, 0.00000796 for an algebraic fit, 0.0138 for symbolic grid search, and 0.370 for a two-unit MLP trained from scratch. On extrapolation points the corresponding errors were 0.0000127, 0.00000950, 0.0227, and 0.801. We averaged the backpropagation runs over five starts per function before taking the median. The MLP had the same width and could learn the input directions, while direct compilation fixed them using the known grammar. All compiler checks passed at 1e-12 absolute tolerance.

The algebraic control achieved slightly lower median error than the LLM using the same observations. This pilot establishes that the pipeline can recover and compile an expression when the grammar and sample layout determine it. A stronger comparison will use random sample locations and multiple plausible structures, with a separate session for the proposer. [Full results, limitations, and replay instructions](https://github.com/protimroy/pro-log/tree/5998464a2d2564f5b0c9071bb4eed89924158f7a/evidence/function-space-programming/runs/r02-function-discovery)

###### R02 follow-up · Give backpropagation the same structure

The original in-domain gap was about 32,000-fold at eight examples. To test whether it persists under the same structural assumptions, we fixed the input directions and fitted the intercept, amplitudes, and breakpoints by backpropagation. At eight examples, median normalized in-domain and extrapolation RMSE were 0.00000478 and 0.00000672 with L-BFGS, compared with 0.0000117 and 0.0000127 for direct LLM compilation. Matched Adam reached 0.0000461 and 0.0000690. L-BFGS also had the lowest median error at 32 examples. This follow-up reused the R02 tasks and used five starts per optimizer. [Matched-control results and replay](https://github.com/protimroy/pro-log/tree/2a761d382912b8695b8fe5b1ccbb4d1f56cb58b4/evidence/function-space-programming/runs/r02-matched-grammar)

Unknown breakpoints in piecewise-linear models are a longstanding segmented regression problem. Muggeo provides prior work for the regression setup. The specific numerical comparison above comes from the linked experiment. [Muggeo, Estimating regression models with unknown break-points (2003)](https://doi.org/10.1002/sim.1545)

###### R03 · Semantic routing on held-out compositions

With eight deliberately ambiguous observations per task, correct descriptions helped the LLM choose all 12 held-out graphs. Shuffling the descriptions reduced recovery to 2 of 12, matching typed enumeration with a fixed tie rule. Semantic lookup and a ridge router with canonicalized descriptions also recovered all 12. The descriptions helped resolve ambiguity in this grammar, and the simple controls matched the LLM.

Graph recovery and prediction quality differed. The eight inputs set the second coordinate to zero. For six multiplication graphs this left the fitted output gain unidentified, even when the oracle supplied the correct graph. With 32 observations, typed enumeration recovered all 12 graphs and their functions. The pilot used one in-session proposal batch and reused its selections across both sample budgets. [Per-task results, prior work and replay commands](https://github.com/protimroy/pro-log/tree/4eae7d30068aa32f20a157874a830ec4f862891a/evidence/function-space-programming/runs/r03-semantic-routing)

###### R04 · Teach a frozen Transformer a new command

A 20,928-parameter causal Transformer learned to copy either operand and add modulo 17. After freezing it, we used an LLM-authored subtraction expression, linear probes calibrated on old-task operands, and a gated residual write through the existing output head. This reached 312/312 correct predictions across three seeds on the same 104 held-out pairs. Reading both operands from the final position yielded 79/312. Reading from the operand positions recovered both operands throughout the test set. The intervention left all protected logits unchanged.

Full fine-tuning on eight or 32 new-task examples scored 15/312 and 12/312, respectively. The eight examples held the second operand at zero, making addition, subtraction and copying indistinguishable. Label-only symbolic search found subtraction at 32 examples and tied the injected program. The LLM received the intended operation through the task description. Gradient training supplied the base model, and labeled calibration supplied the probes. The residual write directly determines the logits for the new command. The next test will move the insertion upstream and require later Transformer computations to use it. [Code, proposal, results and replay](https://github.com/protimroy/pro-log/tree/581ca1967d62e963a5489a8e5e84f9b901415571/evidence/function-space-programming/runs/r04-transformer-injection)

Tracr provides a precedent for compiling known programs into Transformer weights. SERAC motivates measuring how well an edit preserves behavior outside its intended scope. [Tracr](https://arxiv.org/abs/2301.05062) · [SERAC](https://arxiv.org/abs/2206.06520)

###### R06 · From examples to an untrained Transformer

The objective is to generate the function a target model would otherwise learn from task data, then compile it into a fresh Transformer and evaluate it at zero gradient updates. XOR showed direct installation in an MLP. R05 compiled a supplied arithmetic program. R06 gives the teacher six labeled examples per task and asks it to infer the operations.

Across six tasks, the teacher’s compiled Transformer got 48/48 unseen single-operation inputs and 168/168 unseen compositions correct. A symbolic solver given the same affine family also got every answer right. A randomly initialized Transformer of the same architecture, trained on the same examples for 250 Adam updates from three starts, fit all training labels and got 79/504 composition predictions right. The teacher and symbolic solver knew the affine family, and the compiler enumerated a small finite domain. These results demonstrate zero-update task acquisition for this grammar and show why a matched symbolic control matters. [R06 report, prompts, results, and replay](https://github.com/protimroy/pro-log/tree/3f11994010fce03e8d19259e45312cede503246d/evidence/function-space-programming/runs/r06-zero-training)

###### Code, evidence and reproduction

The public snapshot contains the XOR and MNIST scripts, dependency lock, baseline metrics, R01 proposal batch, evaluator, and per-task results. The replay command evaluates the stored proposals. The R02 release records the executed comparison, including the labeled samples, frozen proposal batch, seed and checkpoint parameters. The original protocol documents the proposed setup and the R02 run notes record deviations. [Reproduction guide, literature review and protocol](https://github.com/protimroy/pro-log/tree/500c12999a40d4486df578d41d5671925c9fbbda/evidence/function-space-programming) · [R01 proposals and raw results](https://github.com/protimroy/pro-log/tree/500c12999a40d4486df578d41d5671925c9fbbda/evidence/function-space-programming/runs/r01-xor-pilot)
