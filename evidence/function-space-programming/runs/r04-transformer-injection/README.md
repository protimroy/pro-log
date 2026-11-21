# R04 · Function injection into a frozen Transformer

A 20,928-parameter causal decoder was trained from scratch on next-token prediction for three synthetic commands over 17 symbols. The commands copy the first operand, copy the second operand, and add them modulo 17. The new command returns the result of removing the second quantity from the first, wrapping at 17. Its embedding is copied from ADD before freezing. The proposal is the saved in-session translation of that explicit instruction into modular subtraction.

Train and evaluate on disjoint operand pairs. All 104 held-out pairs are absent from base training, probe calibration, and new-task fine-tuning. Base training uses 177 pairs. The two probes fit to 144 base-training pairs using ridge regression. The function decodes the operands from residual states, computes the integer result and constructs a minimum-norm residual update at the last position using the pseudoinverse of the existing unembedding. The NEW token gates that write. Compare a single final-position dual readout with separate position-local readouts. No target-task labels enter the injected system.

| Method | Correct across three seeds |
| --- | ---: |
| Frozen base, NEW initialized from ADD | 17/312 |
| Injection, read both operands at final position | 79/312 |
| Injection, read operands at their own positions | 312/312 |
| Label-only symbolic search, 8 examples | 12/312 |
| Label-only symbolic search, 32 examples | 312/312 |
| Full fine-tuning, 8 examples | 15/312 |
| Full fine-tuning, 32 examples | 12/312 |

All three seeds use the same data split. These counts summarize runs across three initializations over the same 104 pairs. Final-position operand accuracy was 44.2–49.0%. Position-local probes recovered both operands on all test inputs. The injection kept all 936 protected logits vectors identical, with 733 correct base predictions, and left the frozen checkpoint hash unchanged. Few-shot fine-tuning used 250 AdamW updates per seed and budget, with no replay of protected examples. It reached 681/936 and 637/936 correct on protected tasks at 8 and 32 labels, respectively.

The eight labels hold the second operand at zero and cannot distinguish subtraction from addition or copying the first operand. The 32 labels disambiguate the grammar. The hand-written subtraction rule compiles to the same function as the LLM proposal. The LLM was supplied the specific behavior, slot layout and a callable interface. This is evidence about teaching a capability through explicit function injection. The base still requires gradient training, the probes use labeled operand calibration, and the final write is functionally equivalent to a gated output override for this full-row-rank head. The next depth test is to inject before an existing downstream Transformer block and check whether subsequent autoregressive tokens use the result with the final head left to predict normally.

Related work includes compilation of known functions into Transformers and scoped edits to frozen predictors. [Tracr](https://arxiv.org/abs/2301.05062) · [SERAC](https://arxiv.org/abs/2206.06520)

From the experiment repository or public evidence snapshot root:

```sh
uv sync --locked --python 3.12
uv run --locked python experiments/r04_injection.py runs/r04-transformer-injection/proposal.json > /tmp/r04.json
cmp /tmp/r04.json runs/r04-transformer-injection/results.json
```
