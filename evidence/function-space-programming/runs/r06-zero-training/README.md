# R06 · Task functions in fresh Transformer weights

## Objective

The project asks whether a teacher LLM can infer a function that a target model would otherwise learn from task data, then compile that function into a fresh target Transformer. The target in the compilation arm receives zero gradient updates. XOR demonstrated direct installation into an MLP. R05 demonstrated installation of a supplied program into a Transformer. R06 tests generation from labeled examples followed by installation and held-out evaluation.

## Design

Six synthetic tasks each use two opaque affine operations modulo seven plus a declared identity. The teacher knows the affine family and receives three examples of each operation paired with identity. It sees zero examples of two non-identity operations composed. Six tasks were independently sampled for this run. The operator arrays and held-out targets were withheld from the proposer, which produced one in-session batch before scoring. This was a bench pilot without a separate blinded model session.

The compiler writes token and position embeddings, attention routing weights, a finite ReLU representation of the composed function, and an output projection into a fresh one-block, 6,563-parameter causal decoder. Prediction goes through a shared forward implementation with no runtime symbolic evaluator. This is a fixed three-token context with last-position prediction. The compiler enumerates the finite grammar, so the result is specific to this small domain.

The oracle uses the hidden coefficients. The symbolic arm infers slope and offset from the first two labels for each operation. The random baseline shares the architecture and the six labeled examples, then takes 250 full-batch Adam updates from each of three fixed seeds per task. The compiler arms have direct access to the supplied affine prior. The random baseline receives no special implementation of that prior. Final comparison is across those settings, with no runtime or compute claim.

## Results

| Arm | Updates | Unseen inputs, single operation | Unseen compositions |
| --- | ---: | ---: | ---: |
| Teacher-generated function compiled | 0 | 48/48 | 168/168 |
| Symbolic identification compiled | 0 | 48/48 | 168/168 |
| Oracle function compiled | 0 | 48/48 | 168/168 |
| Random initialization, one seed per task | 0 | See raw results | 31/168 |
| Backpropagation, three seeds per task | 250 per run | 0/144 | 79/504 |

Backpropagation fit all 108 training predictions across 18 task-seed runs. The composition denominator is 28 prompts per task per seed. Backpropagation's mean composition accuracy is 15.67%. Central differences checked one coordinate per parameter tensor with maximum absolute gradient discrepancy below 2e-11.

R06 demonstrates the requested task-to-function-to-weights pipeline. It does not isolate an advantage unique to the LLM because elementary affine identification ties it on every task. A harder benchmark should provide multiple plausible function families, include examples that make them distinguishable, and keep symbolic search as a matched control. [Tracr, related work on compilation](https://arxiv.org/abs/2301.05062)

## Run

From the repository or evidence root, with Node.js:

```sh
node experiments/r06_zero_training.mjs > /tmp/r06-results.json
```

The runner loads `runs/r06-zero-training/tasks.json` relative to its own location. Compare the aggregate counts or per-task metrics with `runs/r06-zero-training/results.json`. It requires no packages. The reference was executed in V8 and checked by a second execution of the same engine.
