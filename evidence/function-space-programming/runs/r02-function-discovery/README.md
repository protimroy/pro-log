# R02 · Function discovery and direct compilation

Run from the repository or public evidence snapshot root with the pinned CPU dependencies.

```sh
uv sync --locked --python 3.12
work="$(mktemp -d)"
cp runs/r02-function-discovery/{packet,proposals,seed}.json "$work/"
uv run --locked python experiments/r02_discovery.py score "$work"
```

The JSON stores each task, checkpoint parameters and held-out metric, along with input hashes and aggregate gradient-training wall time per task and sample budget. Compare the `scores` arrays after excluding `mlp_seconds`. Replay uses saved proposals. Generation for a fresh pilot uses the `packet` command in an empty directory.

## Results

The table gives the median normalized RMSE across 12 sampled functions. For the MLP, average five starts within each function before taking the median. Each split has 2,048 points per task. Normalization divides RMSE by the observed label standard deviation with a 0.01 floor.

| Method | 8 in-domain | 8 extrapolation | 32 in-domain | 32 extrapolation |
| --- | ---: | ---: | ---: | ---: |
| LLM direct compilation | 0.0000117 | 0.0000127 | 0.0000153 | 0.0000136 |
| LLM knots, coefficients refit | 0.00000937 | 0.0000130 | 0.00000964 | 0.0000169 |
| Algebraic fit | 0.00000796 | 0.00000950 | 0.00000916 | 0.0000106 |
| Symbolic grid and least squares | 0.0138 | 0.0227 | 0.0146 | 0.0293 |
| Two-unit MLP, Adam and backpropagation | 0.370 | 0.801 | 0.249 | 0.833 |

Compiler parity passed at the declared absolute tolerance of 1e-12. The analytical oracle's median normalized error was below 2e-16. The 120 MLP fits consumed approximately 27 seconds on the measured CPU run. The grid tested 441 candidates per task and sample budget. One in-session LLM batch provided 12 expressions and was reused across both sample budgets. Inference timing and token counts were unavailable.

## What the pilot tested

Each target was a sum of two axis-aligned ReLU hinges plus an intercept. The first five labeled rows identify all parameters algebraically up to label rounding. They isolate the intercept and give two active points per axis. The LLM was shown those labels and the sample design in the same session that authored the harness. The seed and test outputs stayed unread until its numerical proposals were saved. The 32-example arm added 24 random points and reused the same proposals, so changes in direct normalized error across budgets reflect the normalization scale. There was no optimizer tuning on separate development tasks. Adam used fixed settings and the MLP had the same width with all nine parameters trainable. The expressions use five free parameters with fixed input directions. This comparison therefore measures the effect of the known structural prior as well as the fitting method.

The grid's knot resolution limits its accuracy. The algebraic fit uses the same labels and structural knowledge as the LLM, and achieves slightly lower median error. The pilot establishes end-to-end discovery and compilation for the fixed design. The next comparison needs random sample locations and a grammar with multiple plausible structures, with independently generated tasks and a separate proposer session. Include an optimizer fitted to the same constrained grammar as a control.

See the original protocol and prior work in the [public evidence guide](https://github.com/protimroy/pro-log/tree/500c12999a40d4486df578d41d5671925c9fbbda/evidence/function-space-programming).
