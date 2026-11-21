---
slug: /function-space-programming
title: "Function Space Programming"
description: "An exact XOR construction, a fixed-feature MNIST baseline, and a controlled experiment for LLM-proposed behavior edits."
canonical_url: "https://www.protimroy.com/pro-log/function-space-programming/"
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

| Feature map | Dimensions | Test correct | Accuracy |
| --- | ---: | ---: | ---: |
| Raw pixels | 784 | 8,606 / 10,000 | 86.06% |
| Designed | 217 | 9,606 / 10,000 | 96.06% |
| Random ReLU | 217 | 8,838 / 10,000 | 88.38% |

The designed map uses ink statistics, center of mass, spatial pooling, image gradients, symmetry, and fixed directional stroke filters. The random ReLU arm uses a frozen Gaussian projection with seed 42 and matches the designed map's feature count. The designed map scored 7.68 percentage points higher than that particular projection. The raw-pixel arm provides a reference at a different dimensionality. Multiple projection seeds would be needed to estimate how much the dimension-matched comparison varies.

The full CPU reference and the WSL2 workstation run agreed on every correct count. I independently replayed the workstation artifacts, checked their hashes, and matched the checkpoint tensors within numerical tolerance. The source revision and the two run revisions were `cf1de5c`, `572bec2`, and `7eeb5cb`, respectively, in the research repository. These are baseline experiments with fixed computations and, on MNIST, a fitted readout. Neither run tests an LLM proposing or applying an edit.

###### Next experiment: test locality on continuous XOR

I will freeze the XOR score function and define a local behavior change near one corner. The evaluation will include target samples, protected samples from across the square, and a separately reported band near the edit boundary. A wider patch can improve target accuracy while changing unrelated scores, so I will measure output drift even when the predicted class stays the same.

The candidate patch will be an additive residual from a bounded grammar shared by the language model and the controls. The first comparison will include the unedited predictor, a hand-designed patch, and search over the same grammar with the same development-evaluation budget as the language model. The patch will be selected on development examples before evaluating the fixed held-out split. The main outcomes are target success, protected-region prediction agreement, mean and maximum protected score drift, and patch size. A hand-designed patch that solves the task is a useful calibration point. To make a case for LLM assistance, the experiment needs to show when proposals use the search budget better than the non-LLM control.

If the XOR protocol can distinguish a good local edit from one that spills into the protected region, I will carry it to a predefined MNIST confusion slice. That experiment will measure correction of the selected errors alongside collateral changes to other classes and examples of the same classes that were already correct.
