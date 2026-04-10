---
slug: /sample-research-article
title: Sample Research Article
description: A short research-style note on using synthetic tasks to study reasoning failures in small language models.
allow_html: true
template: page.html
---

###### Abstract

This note sketches a lightweight research program for studying how small language models fail on multi-step reasoning. The core idea is to avoid benchmark sprawl and instead build a narrow family of synthetic tasks where each problem isolates one failure mode: state tracking, tool selection, symbolic consistency, or long-horizon dependency management. With that setup, it becomes easier to tell whether a model is genuinely reasoning or only matching familiar surface patterns.

###### Motivation

A common problem in language-model evaluation is that broad benchmarks mix too many variables together. A single score might reflect pretraining overlap, prompt sensitivity, formatting issues, or true reasoning capability. That makes it difficult to decide what to improve next.

For a smaller research project, a better approach is often to define a controlled problem family with three properties:

- every example can be generated programmatically,
- the ground-truth answer can be checked automatically,
- the tasks can be scaled gradually from easy to hard.

This gives us a clean experimental loop without needing a large annotation budget.

###### Proposed Task Family

Consider a synthetic environment where the model receives:

- a small world state,
- a list of allowed operations,
- a target query about the final state.

An example might look like this:

```text
State:
- Box A contains a red key.
- Box B contains a blue key.
- Drawer C is locked.

Rules:
- A red key opens Drawer C.
- If Drawer C is opened, a note inside says: "Swap the contents of Box A and Box B."

Question:
Which key is in Box A at the end?
```

This kind of task is intentionally simple for a human, but useful for analysis because the model must:

1. infer which action is relevant,
2. update the world state correctly,
3. avoid contradictions in the final answer.

###### Experimental Setup

The study can be split into four tiers.

Tier 1 measures direct answer accuracy.

Tier 2 collects chain-of-thought style reasoning traces, not to optimize for verbosity, but to inspect whether the intermediate updates are consistent.

Tier 3 introduces distractor rules that are locally plausible but globally irrelevant.

Tier 4 adds distribution shift by renaming entities, shuffling presentation order, or converting the same task into a table rather than prose.

If performance collapses mainly under Tier 4, the model may be relying more on formatting regularities than on stable internal state updates.

###### What To Measure

Instead of only logging final accuracy, I would track three additional metrics:

- step consistency: whether each intermediate statement remains compatible with the original rules,
- repair rate: whether a model can recover after making an early mistake when asked to verify its own reasoning,
- distractor sensitivity: how much accuracy drops when irrelevant but believable rules are inserted.

These are more diagnostic than a single aggregate score because they separate different kinds of reasoning failure.

###### Expected Findings

My expectation is that small models will do reasonably well when the required reasoning depth is low and the surface form is familiar, but they will degrade quickly when the same logic is expressed in a less common format or when the number of state transitions grows.

I would also expect self-verification prompts to help only when the model's latent representation already contains the correct state. If the internal representation is wrong, asking for a second pass may only produce a more polished explanation of the same mistake.

###### Why This Matters

A compact synthetic benchmark like this is useful because it helps answer a very practical question: when a model fails, is it because the world model is weak, the prompt format is brittle, or the evaluation itself is noisy?

That distinction matters for both product work and research. If the problem is formatting brittleness, prompt design may be enough. If the problem is unstable state tracking, the fix probably needs to happen at the model or training-data level.

###### Next Steps

The natural extension is to pair these tasks with intervention experiments:

- compare base prompting with tool-assisted execution,
- compare free-form reasoning with structured scratchpads,
- compare answer-only supervision with trace-level supervision.

That would turn this from a toy article into a practical mini-benchmark for studying when reasoning systems are robust and when they are mostly performing pattern completion.

Author: [Protim Roy](https://www.protimroy.com) with help from GPT-5.4 \
Date: 2026-04-10
