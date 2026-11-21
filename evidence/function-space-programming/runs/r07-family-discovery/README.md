# R07 · Distinguish competing functions before compilation

## Question

R06 gave the teacher one known affine family. R07 gives a teacher three plausible families and asks it to infer which function to install into a fresh Transformer at zero target-model updates. The scientific question is whether language-model inference helps beyond exact search when the function family is uncertain.

## Design

There are 12 synthetic tasks with one hidden operation per task, four per family. Each operation maps integers modulo seven to integers modulo seven. The grammar contains affine, quadratic, and parity-dependent affine expressions. The quadratic and parity terms have nonzero coefficients. Exhaustive enumeration verifies that the grammar contains 637 distinct functions. The task generator uses a saved seed. The proposer received labels incrementally and recorded each set of choices before seeing the next label. It ran in the experiment author's chat session and saw the grammar. No fresh, independently blinded teacher run was performed.

Both methods receive the same nested observations at x=0,1, then x=2, then x=3. The teacher uses an affine preference and breaks nonlinear ties in favor of quadratic. The symbolic solver searches all 637 candidates and uses the same family ordering for ties. The oracle has the generating function. Keep the teacher's recorded arithmetic slip on task 0 in both early stages. The detailed results flag whether each proposal fits every available label.

Every selected function is compiled into the same 6,563-parameter Transformer used in R06. A task combines the inferred operation with a declared plus-one operation. The held-out test contains all seven values for each of three ordered compositions: unknown then unknown, unknown then plus one, and plus one then unknown. Single-operation test inputs are x=4,5,6 throughout. Exact recovery compares the underlying function across the entire seven-value domain. Predictions are produced by the model's forward pass.

## Results

| Labels per task | Matching functions | Teacher exact functions | Search exact functions | Teacher composed answers | Search composed answers |
| --- | --- | ---: | ---: | ---: | ---: |
| 2 | 13 on each task | 4/12 | 4/12 | 128/252 | 129/252 |
| 3 | 1 on four tasks, 2 on eight | 7/12 | 8/12 | 186/252 | 203/252 |
| 4 | 1 on each task | 12/12 | 12/12 | 252/252 | 252/252 |

The oracle got 252/252 compositions at every budget. At four labels, all methods also got 36/36 unseen single-operation inputs right. At the sparse budgets, the teacher fit 11/12 observation packets. Its arithmetic slip explains the observed gap versus the equivalent tie policy on this run. There is no measured teacher advantage over exact search on this small restricted grammar.

There are 13 consistent programs after two labels because every nonlinear coefficient yields one solution in each nonlinear family, alongside the affine solution. A third label either fixes the affine function or leaves one candidate from each nonlinear family. For a nonzero residual at x=2 relative to the affine line through x=0,1, the residual at x=3 is three times as large for the quadratic candidate and equal for the parity candidate, modulo seven. This makes the fourth label decisive.

This run isolates information and family selection from the quality of the compiler. It extends R06 from one known family to three known alternatives. It does not establish open-ended function discovery or compare pretraining compute. A follow-up can test whether teacher-guided search reduces candidate evaluations in a larger grammar while preserving exact recovery.

## Replay

From the experiment repository or public evidence root:

```sh
node experiments/r07_family_discovery.mjs > /tmp/r07-results.json
cmp /tmp/r07-results.json runs/r07-family-discovery/results.json
```

This replays the recorded proposals. [R06 and the shared compiler](https://github.com/protimroy/pro-log/tree/3f11994010fce03e8d19259e45312cede503246d/evidence/function-space-programming/runs/r06-zero-training) · [Tracr](https://arxiv.org/abs/2301.05062)
