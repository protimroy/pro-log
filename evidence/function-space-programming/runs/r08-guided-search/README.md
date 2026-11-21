# R08 · Teacher-guided search with an algebraic control

## Question

Can a teacher LLM reduce search while preserving zero-update task acquisition? R07 compared teacher proposals with exhaustive search. R08 adds structured solvers to test whether a reduction in candidate checks reflects teacher guidance or the algebra of the grammar.

## Protocol

Twelve synthetic tasks share a grammar of cubic polynomials over integers modulo seven, with either no extra term, a nonzero parity term, or a nonzero step at x=2. The grammar has 31,213 coefficient tuples. A saved seed generates four cases of each family and shuffles their order. Each task supplies six labels at x=0 through 5. Each arm evaluates the hidden seventh value and 21 composition prompts involving the inferred function and a supplied plus-one function. The unchanged R06 compiler installs each solution in a fresh 6,563-parameter Transformer at zero optimizer updates.

The in-session teacher nominated one family per packet before test scoring. Modular Gaussian elimination then fitted its coefficients. Fixed-order search used the same fitter over the cubic, parity, and step families in that order. The strongest symbolic control selected a family using two fourth differences, then used the shared fitter. The exhaustive arm tested explicit coefficient candidates in fixed enumeration order until its first fit, and an additional offline uniqueness check confirmed one fit per packet. That check sits outside the counted search. The oracle received the generating expression. Tests used no teacher dialogue after the proposals.

## Results

| Method | Exact functions | Correct held-out predictions | Search work across 12 tasks |
| --- | ---: | ---: | --- |
| Exhaustive first match | 12/12 | 264/264 | 128,728 coefficient tuples checked |
| Fixed-order algebraic search | 12/12 | 264/264 | 24 family fits |
| Teacher-guided algebraic search | 12/12 | 264/264 | 12 family fits |
| Deterministic finite-difference routing | 12/12 | 264/264 | 12 family fits plus two fourth differences per task |
| Oracle | 12/12 | 264/264 | Generating functions supplied |

The teacher halved family fits versus fixed ordering. The deterministic selector matched the teacher. Fourth differences eliminate the cubic term, leaving distinct signatures for the parity and step terms. The teacher used the same reasoning to nominate its families. A family fit and a coefficient-tuple check are different operations, so their counts do not yield a time or compute ratio. Teacher latency and token cost were unavailable. These results use one in-session batch and a balanced synthetic sample.

The result confirms that selecting a family before solving its coefficients can reduce search in this grammar. The strongest deterministic control leaves no measured LLM-specific advantage. Follow-up experiments should use grammars whose structure cannot be identified by a single handcrafted signature, with a separately blinded teacher session and measured end-to-end search costs.

[LLM-SR](https://arxiv.org/abs/2404.18400) motivates separating structural suggestions from numerical coefficient fitting. [Tracr](https://arxiv.org/abs/2301.05062) motivates checking whether supplied programs execute correctly after compilation.

## Replay

From the research repository or public evidence root:

```sh
node experiments/r08_guided_search.mjs > /tmp/r08-results.json
cmp /tmp/r08-results.json runs/r08-guided-search/results.json
```

Replay uses archived proposals and deterministically regenerates the task draw for verification.
