# Function Space Programming · Evidence and protocol

## Reproduce the reported experiments

From a clone of protimroy/pro-log, change to `evidence/function-space-programming` and run:

```bash
uv sync --locked --python 3.12
uv run --locked python experiments/xor_function_space.py
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run --locked python experiments/mnist_function_space.py
uv run --locked python experiments/r01_xor.py runs/r01-xor-pilot/proposals.json > /tmp/fsp-r01.json
cmp /tmp/fsp-r01.json runs/r01-xor-pilot/results.json
```

The first MNIST run downloads the official splits. Compare the three correct counts with [the reference manifest](runs/r00-cpu-reference/manifest.json). For R01, inspect [the parameters and task specification](runs/r01-xor-pilot/proposals.json), [the evaluator](experiments/r01_xor.py), and [every selected patch and held-out metric](runs/r01-xor-pilot/results.json). Replay evaluates the recorded proposals. Fresh model inference is a separate replication. This snapshot comes from research revision `e8d540230aefd374e76ab019085d7237fd818f9f`.

## Targeted literature review · November 21, 2026

The search covered primary work on neural compilation, programming by example, LLM symbolic regression, equation-discovery benchmarks, weight-space programming, and edit locality. This selection informs experimental design. It is not an exhaustive novelty review.

| Prior work | What carries over | Consequence for our experiment |
| --- | --- | --- |
| [Gulwani, Programming by Examples (2015)](https://www.microsoft.com/en-us/research/publication/programming-examples-applications-ambiguity-resolutions-approach/) | Several programs in a restricted language can satisfy the same examples. | Give a symbolic search control exactly the same operators and examples. Test disagreement away from those examples. |
| [Lindner et al., Tracr (2023)](https://arxiv.org/abs/2301.05062) | Compiles supplied programs into transformer weights and uses known computational structure as ground truth. | Check predicted expression against its compiled network independently of whether the inferred expression fits the unknown target. |
| [Shojaee et al., LLM-SR (2024)](https://arxiv.org/abs/2404.18400) | An LLM proposes equation structure and numerical optimization estimates coefficients. | Compare direct injection, the same proposed structure with fitted coefficients, and backpropagation from random initialization. |
| [Shojaee et al., LLM-SRBench (2025)](https://arxiv.org/abs/2504.10415) | Transformed and synthetic tasks challenge recognition of familiar equations. | Use unnamed, seeded functions and withhold the generating program and challenge inputs. |
| [Mitchell et al., SERAC (2022)](https://arxiv.org/abs/2206.06520) | Models the intended scope of an edit across related and unrelated inputs. | For edits report target accuracy, protected agreement, and score drift separately, including near the boundary. |
| [Takehi et al., Sparks of Weight-Space Programming (2026)](https://rikiyat.github.io/blog/weight-space-programming/) | Studies direct LLM reading and writing of weights. | Record whether the LLM emits an expression or weights, and record its examples, tools and feedback budget. |

## Proposed R02 · Discover and compile a function from examples

**Question.** At low sample counts, can an LLM recover a function that generalizes after direct compilation, and how much does numerical fitting add? R01 supplied the edit center and structured search tied the LLM. It did not measure inference of the structure.

1. Start with unnamed two-input piecewise-linear functions representable by a small ReLU MLP. Freeze the grammar, architecture capacity, task generator, split policy and budgets before collecting proposals. Use independent development tasks for choosing optimizer settings. Keep evaluation task seeds and generating expressions hidden from the proposer until all submissions are fixed.
2. Pilot 12 independent evaluation functions at 8 and 32 nested labeled examples per function. Give every discovery arm identical input/output pairs, grammar and domain. Compare a direct LLM expression, the same expression with coefficients fitted on those pairs, budgeted symbolic search with coefficient fitting, and a capacity-matched randomly initialized MLP trained by backpropagation across five starts. Give a supplied-expression compiler an oracle row to test implementation correctness.
3. Compare expression and compiled predictions on breakpoint probes and a dense grid. Record maximum discrepancy with a predeclared numerical tolerance. Separately evaluate prediction error against the hidden target on held-out interpolation and extrapolation points. Normalize per task by training-output scale with a fixed floor. Report parameter count, task-wise paired error differences, seed variability, model calls, candidate evaluations, gradient steps and wall time.
4. Archive the task generator, prompts and responses, proposal programs, compiler, optimizer configuration, checkpoints, evaluator and raw per-task results. Keep direct compilation's zero gradient steps distinct from LLM inference cost and from fitted arms. Decide whether to scale based on paired differences across functions, including failures. A tie with symbolic search establishes feasibility and leaves the proposal advantage unresolved.

A parallel editing question freezes an existing predictor, hides an edit region, and compares LLM residuals with the same residual family fitted by backpropagation. Keep its locality metrics separate from the from-scratch discovery results. R02 is a proposed protocol; the public measurements here are R00 and R01.
