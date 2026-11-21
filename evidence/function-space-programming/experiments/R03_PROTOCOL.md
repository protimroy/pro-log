# R03 proposal · Transfer compositional structure before compilation

R02 established compiler parity. The matched follow-up removes the main confound in the original comparison. L-BFGS on the same expression family reaches lower median error than direct LLM compilation.

## Question

Can an LLM use textual semantics to route sparse observations to the right composition of frozen, previously learned modules? Measure the gain from routing independently of module capacity and numerical fitting.

## Comparison

Build development and evaluation families from the same synthetic module library. Freeze the learned modules before splitting held-out composition graphs. Give all arms the same module descriptions, labeled points, grammar and budget. Include intentionally ambiguous eight-point packets, a larger observation budget, and challenge inputs where admissible compositions disagree.

Compare LLM-proposed graphs, typed enumeration with coefficient fitting, and a learned router over the same frozen modules. Include an oracle graph, a label-only version, and shuffled descriptions as a causal control. Use the same coefficient fitter and compiler for every selected graph. Report held-out error, composition recovery up to equivalence, cost, and semantic-ablation deltas across independent graphs. The claim of interest is a gain over typed search and the learned router that disappears when descriptions are shuffled.

## Prior art and scope

DreamCoder already learns reusable program libraries and search policies. LaSR already uses a language model to discover and evolve symbolic concepts. Tracr already compiles supplied programs into neural weights. Any contribution here would need to come from a measured effect of semantic information on recovering held-out compositions under matched controls.

- [DreamCoder](https://arxiv.org/abs/2006.08381)
- [Symbolic Regression with a Learned Concept Library](https://mlanthology.org/icmlw/2024/grayeli2024icmlw-symbolic/)
- [Tracr](https://arxiv.org/abs/2301.05062)
