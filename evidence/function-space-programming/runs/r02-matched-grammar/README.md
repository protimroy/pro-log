# R02 follow-up · Match the function family

Both methods use the same five-parameter expression with two fixed input directions. We replay the original labels and proposals. Adam and L-BFGS each fit the intercept, two amplitudes, and two breakpoints by backpropagation from five initializations. The data, train/test splits, and error normalization are inherited from R02. We average starts within each function before taking the median across 12 functions.

| Method | 8 in-domain | 8 extrapolation | 32 in-domain | 32 extrapolation |
| --- | ---: | ---: | ---: | ---: |
| Direct LLM compilation | 1.167e-5 | 1.273e-5 | 1.528e-5 | 1.365e-5 |
| Algebraic fit | 7.965e-6 | 9.500e-6 | 9.164e-6 | 1.061e-5 |
| Matched Adam | 4.607e-5 | 6.902e-5 | 6.003e-6 | 1.176e-5 |
| Matched L-BFGS | 4.784e-6 | 6.721e-6 | 3.495e-6 | 6.054e-6 |

The strongest matched control has lower median error on all four comparisons. This is a follow-up on the same tasks, with optimizers chosen after R02. It measures prediction error on this design. It does not establish a compute-matched comparison. The results record gradient closure evaluations and the parameter values for each start. The saved LLM proposals use the five identifying labels and were reused for both budgets. LLM latency and token counts were unavailable.

V. M. R. Muggeo, *Estimating regression models with unknown break-points*, Statistics in Medicine 22(19), 3055–3071 (2003), provides prior work for fitting unknown piecewise-linear breakpoints. The five-point construction in R02 uses a specially chosen sampling design. Its exact error ratios come from our experiment. [Muggeo (2003)](https://doi.org/10.1002/sim.1545)

Run from the evidence or research repository root:

```sh
uv run --locked python experiments/r02_matched_grammar.py runs/r02-function-discovery > /tmp/r02-matched.json
cmp /tmp/r02-matched.json runs/r02-matched-grammar/results.json
```
