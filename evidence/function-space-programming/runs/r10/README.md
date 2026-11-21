# R10 · Longer context under a fixed Transformer parameter budget

R10 tests whether a data-estimated program can use more input context without installing a separate detector for every long history. The context grows from two to eight characters while the dense target stays within R09's 220,510-parameter budget.

## Method

Reuse R09's Tiny Shakespeare checksum, 37-symbol alphabet and normalization. Train on the first 100,000 characters of the training partition. All R10 comparisons use 99,992 training, 111,531 validation and 111,532 test windows, with eight characters of history available in each window. Every arm uses the same prediction positions, including the two-character reference. The reference was refit and rescored on R10's windows.

The in-session assistant authored one program family from the task specification. The runner fits its statistics using the training windows. Start with two-character interpolated Kneser–Ney. For the 957 most frequent three-character suffixes, estimate a smoothed conditional using the short-context predictions as a prior, with strength 16. Add the difference between the suffix and base log probabilities. For each symbol at lags 3–8, separately estimate the conditional with an unconditional prior of strength 64. Add the centered log probabilities (log conditional minus log marginal), scaled by a single nonnegative weight. Softmax normalizes the final logits. The program pools distant evidence across contexts, without a table over eight-character histories. There was one in-session proposal, with no logged standalone teacher call or teacher cost.

Validation chooses between the short base, suffix-only, lag-only and combined programs. The lag weight grid is 0.125, 0.25, 0.5, 0.75 and 1.0. Kneser–Ney independently selects history length (one through eight) and single discount on validation. Table entries count observed joint keys summed across its conditional levels. This count is a descriptive measure, with units different from neural parameters. No memory budget was imposed on the count control.

The 220,483-parameter decoder uses eight heads to read the eight source positions at the causal final query. The compiler encodes symbols in six bits. Position-controlled attention recovers those bits, and each ReLU fires at one minus the Hamming distance from its assigned symbol or suffix, clipped at zero. The output sums those gates' logit contributions. The compiled model has 37 last-character gates, 693 pair gates, 957 suffix gates and 222 lag-by-symbol gates. It uses no pretrained weights or optimizer steps.

Backprop uses the identical architecture, with trainable token and position embeddings, random initialization and AdamW at learning rate 0.003. Each seed runs 1,500 steps using shuffled batches of up to 256, and chooses its checkpoint on 8,192 evenly spaced validation windows every 100 steps. Final scores use full validation and test splits. One seed selected step 1,500, so the neural comparison is a bounded training run rather than a convergence result.

## Results

| Predictor | Test bits per normalized character |
| --- | ---: |
| Two-character Kneser–Ney base | 3.192652 |
| Base plus lag features | 3.171620 |
| Base plus three-character suffix corrections | 3.080894 |
| Combined program, direct | 3.077781 |
| Combined program, compiled | 3.077781 |
| Same decoder trained with AdamW, three-seed mean | 3.027555 |
| Kneser–Ney with six-character history, selected on validation | 2.804546 |

The larger program improved on the short base by 0.114872 BPC. The incremental lag gain over suffix-only was 0.003113 BPC at weight 0.125. The compiled result trailed AdamW by 0.050226 BPC and the six-character Kneser–Ney model by 0.273235 BPC. The latter stored 172,824 conditional entries across six levels. The same test split is shared by all seeds and methods.

Maximum absolute probability error compared with direct execution was 2.38e-7 over all test positions and 8.48e-8 over 4,096 seeded random histories. The combined program leaves no optimizer state. Fitting its corrections after count models were available took 9.8 ms and installing the weights took 64.5 ms on this CPU run. The recorded count timing includes tuning all Kneser–Ney orders and discounts. The component timings omit corpus preparation, program validation selection and teacher time. AdamW fitting and checkpoint selection took 7.7–9.4 s per seed. These measurements do not establish an end-to-end speedup.

## Related work

Targeted review, November 21, 2026. Chen and Goodman's comparison of smoothing methods motivates the Kneser–Ney control. Goodman's evaluation of skipping models motivates separate suffix-only and distant-evidence ablations. The distant factors here combine in logit space. Tracr establishes the precedent for checking a weight compiler against reference execution. [Chen and Goodman, ACL 1996](https://aclanthology.org/P96-1041/) · [Goodman, 2001](https://www.microsoft.com/en-us/research/publication/a-bit-of-progress-in-language-modeling-extended-version/) · [Tracr, NeurIPS 2023](https://arxiv.org/abs/2301.05062)

## Replay

Run from the research repository root. In the public snapshot, run the Python command from its `evidence/function-space-programming` directory using a PyTorch environment with NumPy. The first run fetches and verifies the corpus or you can point `--corpus` at an existing copy.

```sh
uv sync --locked --python 3.12
uv run --locked python experiments/r10_long_context.py \
  --output runs/r10/replay/metrics.json \
  --checkpoint-dir runs/r10/replay/checkpoints
```

The runner saves all validation sweeps, test losses, training seeds, and probability parity checks in JSON. The research repository archives the compressed installed checkpoint. Replay also produces a checkpoint for every gradient seed. See [the protocol](PROTOCOL.md) and [raw results](metrics.json).
