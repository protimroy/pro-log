# R03 · Semantic routing over held-out graphs

Run from the repository or evidence snapshot root:

```sh
uv sync --locked --python 3.12
uv run --locked python experiments/r03_routing.py packet runs/r03-semantic-routing > /tmp/r03-packet.json
cmp /tmp/r03-packet.json runs/r03-semantic-routing/packet.json
uv run --locked python experiments/r03_routing.py score runs/r03-semantic-routing > /tmp/r03-results.json
cmp /tmp/r03-results.json runs/r03-semantic-routing/results.json
```

Four scalar modules are fitted by least squares with a shared piecewise-linear ReLU basis and frozen. A seed splits 48 ordered graphs into 36 development and 12 evaluation graphs. The graph operation is supplied. A graph applies one module to each coordinate and combines them by addition, subtraction, or multiplication. Every selected graph uses the same least-squares output gain. An independent selected-graph evaluator matched the candidate-bank output within 5.33e-15 across held-out inputs.

| Condition and method | Exact graph at 8 | Equivalent at 8 | Mean RMSE at 8 | Exact graph at 32 |
| --- | ---: | ---: | ---: | ---: |
| Labels and typed enumeration | 2/12 | 1/12 | 0.8547 | 12/12 |
| Correct text and LLM nomination | 12/12 | 6/12 | 0.5558 | 12/12 |
| Correct text and semantic lookup | 12/12 | 6/12 | 0.5558 | 12/12 |
| Correct text and learned router | 12/12 | 6/12 | 0.5558 | 12/12 |
| Shuffled text and LLM nomination, with residual tie filtering | 2/12 | 1/12 | 0.8547 | 12/12 |
| Oracle graph with fitted output gain | 12/12 | 6/12 | 0.5558 | 12/12 |

Equivalent means held-out RMSE below 1e-9 on 2,048 points. At 32 examples, all ranked methods above recovered 12/12 equivalent functions. The unfiltered shuffled LLM nomination still recovered 2/12 graphs at 32, as its frozen proposals did not see the additional labels. Typed search scores 16 graphs for the supplied operation. LLM nomination uses one graph, and the tie-filtered arm also scores the search set. Model token counts and latency were unavailable.

The first eight examples intentionally set the second input to zero. The six multiplication tasks then have zero labels and an unidentified output gain even with the oracle graph. The remaining 24 points vary both inputs. This is a stress test of ambiguity, with a nested identifiable condition. The text paraphrases the intended primitive in each slot. One in-session LLM batch saw both the correct and permuted catalogues and was reused for both budgets. The labels-only tie policy is deterministic. The learned router is a ridge classifier on canonicalized descriptions from development graphs. The canonicalization uses a hand-written cue map shared with the semantic lookup. These choices assess semantic routing on a narrow grammar with easy slot descriptions. A blinded LLM replication and a harder test of compositional inference remain open.

The result supports a role for descriptions when sparse observations leave graph structure ambiguous. The simple semantic lookup and learned router match the LLM. See [the protocol and references](../../experiments/R03_PROTOCOL.md) for the DreamCoder, LaSR and Tracr context.
