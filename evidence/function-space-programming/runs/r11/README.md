# R11 · Matched-budget suffix pruning and cost to target

The task and the 220,483-parameter decoder are unchanged from R10. Fit six-history interpolated Kneser–Ney (discount 0.95) on the same 99,992 training windows. Keep the one- and two-character models. Rank the remaining suffixes by raw frequency, by raw frequency times the KL divergence to the immediate parent, or by the same KL score shrunk by N/(N+4), where N is the suffix's raw count. Each arm retains 1,179 longer suffixes and uses 1,909 gates overall. The nearest retained proper suffix supplies the reference log probabilities for each gate. A chain of matching gates telescopes to the longest retained suffix distribution. The KL criterion ranks whole contexts independently and was inspired by [Stolcke's entropy pruning](https://arxiv.org/abs/cs/0006025), which derives a pruning criterion for individual n-gram parameters.

## Quality

| Predictor | Test bits per character |
| --- | ---: |
| R10 compiled program | 3.077781 |
| Frequency-ranked suffixes | 3.085818 |
| Support-shrunk KL-ranked suffixes | 3.013591 |
| KL-ranked suffixes, selected on validation | **3.009211** |
| Same decoder, AdamW mean of three validation-selected runs | 3.036408 |
| Direct, uncapped six-history Kneser–Ney | **2.804546** |

The selected program reduced loss by 0.068570 BPC versus R10 and beat each R11 AdamW seed (3.021914, 3.049547, and 3.037763). The remaining gap to the uncapped count model was 0.204665. The KL control beat the proposed support shrinkage on validation and test. These results are from one fixed corpus split and one bounded 1,500-step AdamW comparison. The target used zero optimizer steps. Maximum probability difference versus direct longest-retained-suffix execution was 1.17e-7 over 111,532 test windows and 7.09e-8 over 4,096 random histories.

## Cost to a common validation target

The target is at most 3.05 BPC on 8,192 fixed validation windows. The compiled workflow includes all three ranking trials and their validation passes. The training costs include initialization, optimizer updates and scheduled validation every 100 steps. The first checkpoint to pass the validation threshold is then scored on the complete test split. Shared data acquisition, checksum and window preparation took 0.162 s outside the method timers. The default run already had a local copy of the corpus. Test scoring, artifact output, Python startup and in-session design are outside the method timers.

| Path | Wall seconds | Process CPU seconds | Test BPC at the recorded point |
| --- | ---: | ---: | ---: |
| Compiled selection | 2.423 | 2.831 | 3.009211 |
| AdamW seed 17, step 700 | 4.786 | 16.574 | 3.083435 |
| AdamW seed 29, step 1,000 | 5.509 | 21.998 | 3.084662 |
| AdamW seed 43, step 500 | 2.214 | 8.835 | 3.092069 |
| Direct uncapped Kneser–Ney | 0.028 | 0.028 | 2.804546 |

Full AdamW runs took 7.19–9.20 s per seed. The threshold is a shared validation criterion. Two neural seeds reached it later than the compiled selection in this run. The fastest reached it sooner. The validation-selected neural checkpoints were still worse than the compiled model on test. Timing on this host can vary between runs. The direct count model is a stronger quality and build-cost reference for this task, with no decoder parameter or runtime memory cap.

For an operation estimate, the decoder's projections and attention use 548,050 multiply/add FLOPs per prediction with the benchmark's dense execution. Counting a forward plus backward as three such forwards gives about 237–470 GFLOPs for AdamW up to first target, including validation forwards. The compiled workflow uses about 13.47 GFLOPs for its three dense validation passes and zero training forwards or backwards. These estimates omit activation and softmax operations, optimizer arithmetic, count-table construction, sorting and weight installation. Same-architecture dense inference uses the same projection and attention operation count.

The archived standalone design prompt and spec contain 94 and 154 tokens with o200k_base. This is a count of those exact published texts, not total hosted model use. Hidden reasoning, system/context input and provider-side compute or energy are unavailable. The backprop and direct-count controls use no LLM tokens. AdamW processed 127,896–255,792 supervised windows by first target, including repeat training exposures, separate from LLM token usage.

## Energy replay

This host exposed no readable CPU package counters. Package joules and watts are null in the results, and neither utility-bill cost nor hosted LLM energy was estimated. On a supported host the runner reads each readable package or socket counter once per sample. It reports counter deltas in joules and mean watts as joules divided by elapsed seconds. These are gross CPU-package energy readings and exclude other machine components and the assistant service. [Linux power cap interface](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html)

From the research repository, with a consistent power profile and the corpus cached:

```sh
uv sync --locked --python 3.12
uv run --locked --with tiktoken==0.14.0 python experiments/r11_cost_quality.py \
  --output runs/r11/replay/metrics.json --checkpoint runs/r11/replay/compiled.pt
```

Use `--arm compiled`, `--arm adamw --seeds 17` and `--arm direct` to isolate workloads, each with a different output file. Record repeated runs on an otherwise idle machine. For whole-system electricity, measure each arm at the wall and record the meter resolution, elapsed seconds and total Wh. Multiply Wh by 3,600 for joules and divide by elapsed seconds for average watts. For short workloads, aggregate repeated identical invocations until the meter resolves the energy difference. A whole-process wall measurement includes test scoring, imports and disk I/O, so label that scope separately from the within-process package totals. For dollar cost, multiply metered kWh by the actual electricity rate. Provider-side assistant energy remains a separate unavailable quantity.

The public archive has the software and raw JSON. Run from its `evidence/function-space-programming` directory with PyTorch, NumPy and optional tiktoken installed. See [the protocol](PROTOCOL.md) and [raw results](metrics.json).
