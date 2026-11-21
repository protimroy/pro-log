# R09 · Compile a natural-text next-character predictor

R09 tests whether a predictive function estimated from real text can be installed in fresh Transformer weights with no optimizer updates to the target. It also compares the assistant-authored function with standard statistical estimators and a randomly initialized decoder with the same architecture and parameter count.

## Protocol

- Corpus: Karpathy's Tiny Shakespeare. Lowercase the text, preserve spaces, newlines and selected punctuation, and map remaining characters to one unknown symbol. The 37-symbol alphabet is fixed in the script. The script verifies the source bytes against SHA-256.
- Partition the corpus into contiguous 80% training, 10% validation and 10% test blocks. In this CPU pilot, use only the first 100,000 normalized training characters. Score 111,537 validation and 111,538 test next-character predictions. Context windows never cross partition boundaries.
- All estimators receive the same training trigrams. The count models marginalize those counts to obtain lower orders. AdamW takes full-batch gradients of the empirical cross-entropy, weighted by trigram count. Grouping identical examples gives the same mathematical objective as enumerating every training window.
- The Transformer has two input positions, a single causal self-attention head with a residual connection, a ReLU feedforward block with a residual connection, and a linear readout. Both installation and backprop use the same 220,510-parameter decoder, including the trainable embeddings and position embeddings. The compiler uses one gate per observed pair and one fallback gate per symbol. The 693 seen pairs determine width for both arms.
- Discounted baselines select a single discount from a five-value grid on validation. The Kneser–Ney comparison uses interpolated single-discount continuation counts with a positive floor for the lowest order. AdamW uses learning rate 0.005, three random starts, 600 updates per seed and validation selection every 25 steps, including step zero. Hyperparameter tuning for AdamW was limited to checkpoint selection.

## Teacher proposal and compilation

The in-session assistant authored a single smoothing rule before running this experiment. For history `h`, let `N` be the number of occurrences, `T` the number of distinct continuations and `S` the number of continuations seen exactly once. Use the distribution

```text
P(next | h) = [count(h, next) + (T + S) P(next | last(h))] / (N + T + S)
```

Use interpolated Witten–Bell smoothing for the lower-order bigram. Unseen histories use the bigram directly. Setting `S` to zero gives the matched Witten–Bell trigram control. The teacher proposed the estimator from the problem specification. The experiment runner computed its parameters from training data. There was one in-session proposal, with no separate logged inference call, teacher cost measurement or held-out example feedback.

The compiler sets queries and keys to zero so that causal attention at the second position takes an exact uniform mean of the two token vectors. The position's residual carries the current one-hot, so doubling the mean and subtracting the current vector recovers the previous one-hot. The ReLU MLP detects pairs and adds their corrections to bigram log probabilities. The compiler checks all 1,369 contexts, including unseen contexts, against each direct predictor. As a follow-up after the initial comparison, the same compiler was used to install Kneser–Ney with the validation-selected discount. This checks whether the gap comes from the proposed predictor or its implementation in the Transformer.

## Results

| Predictor | Test bits per normalized character |
| --- | ---: |
| Witten–Bell bigram | 3.608881 |
| Witten–Bell trigram | 3.219215 |
| Absolute-discount trigram | 3.251104 |
| In-session rule, direct | 3.212652 |
| In-session rule, compiled | 3.212652 |
| Same architecture, AdamW mean across three seeds | 3.208662 |
| Interpolated Kneser–Ney, direct | 3.192476 |
| Interpolated Kneser–Ney, compiled | 3.192476 |

The compiled teacher's maximum absolute probability error was 6.34e-8 across every output symbol and context. Compiled Kneser–Ney's error was 4.50e-8. Both ran at zero optimizer steps. The teacher improved on its matched Witten–Bell control by 0.00656 BPC, trailed the mean of three AdamW seeds by 0.00399 BPC, and trailed Kneser–Ney by 0.02018 BPC. Validation selected steps 250, 225 and 225 for AdamW. The three seeds share one fixed holdout.

Counting splits, fitting the proposed rule after counting, and compiling it took about 4.60, 0.81 and 2.94 ms respectively on this two-thread CPU run. AdamW took 7.08–7.93 s per seed, including validation and checkpoints selected in memory. These local component timings exclude corpus acquisition and tokenization, the assistant's proposal time and disk output. The direct n-gram predictor can also be evaluated on its own. The comparison establishes paired functional equivalence on this finite input domain and performance on one text split. A GPT-2-scale model and general language-model pretraining remain untested.

## Related work

Targeted review, November 21, 2026. The search covered n-gram smoothing comparisons and program-to-Transformer compilation.

- Chen and Goodman compare smoothing estimators empirically. Their work motivates the Witten–Bell control and validation-selected Kneser–Ney comparison. [ACL 1996](https://aclanthology.org/P96-1041/)
- Lindner et al. compile readable programs into decoder-only Transformers. Their work motivates comparing a direct execution oracle with the compiled decoder and checking every input in this bounded domain. [Tracr, NeurIPS 2023](https://arxiv.org/abs/2301.05062)
- Karpathy's char-rnn repository supplies the corpus. The corpus checksum and exact preprocessing are recorded in the runner. [Source](https://github.com/karpathy/char-rnn/tree/master/data/tinyshakespeare)

## Replay

From the research repository root:

```sh
uv sync
uv run python experiments/r09_character_model.py \
  --output runs/r09/replay/metrics.json \
  --checkpoint-dir runs/r09/replay/checkpoints
```

For the public evidence snapshot, change to its `evidence/function-space-programming` directory and use the same command with a PyTorch environment. The first run fetches the corpus. Use `--corpus /path/to/input.txt` for an existing verified copy. The default produces three AdamW checkpoints and two compiled checkpoints. Each run's BPC, validation curve, seed, compilation error and timings are in [metrics.json](metrics.json). Two compressed compiled checkpoints are archived in the research repository. The public script regenerates them with the same corpus and settings.
