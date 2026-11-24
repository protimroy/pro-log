---
slug: /agent-dynamics
title: "Agent Dynamics"
description: "An empirical research program on agent orchestration, harness control, and execution dynamics."
canonical_url: "https://www.protimroy.com/pro-log/agent-dynamics/"
allow_html: true
options_toc: true
template: article.html
---

Research program · November 24, 2026

How does the design of an agent harness change the behavior of a fixed language model? Agent Dynamics investigates orchestration, state, feedback, verification and inference-time resource allocation through controlled experiments.

## Research questions

- When do planning, reflection and multi-agent coordination improve task completion rather than consume unnecessary computation?
- How do stale observations, incorrect handoffs and tool faults propagate through execution trajectories?
- Can trace-conditioned verification and bounded recovery improve the success-cost frontier?
- Can harness revisions transfer across held-out tasks rather than overfit the tasks used to optimize them?

## First investigation: the cost of unnecessary agent computation

Use a synthetic commerce and customer-service environment with executable ground truth and a shared local 4B model on an RTX 3080. Compare ReAct, plan-and-execute, periodic reflection, hub-and-spoke, and verification-triggered execution under matched model, tool and inference budgets. Include deterministic and direct controls where feasible. Begin with a small smoke test before expanding to 30 tasks and three repetitions per configuration.

Measure exact task success, policy violations, repeated states, model/tool calls, tokens, latency and recovery. Deterministic execution checks are primary; rubric and judge scores are secondary. Record model digest, prompts, configuration, seed, code revision, task splits and event traces.

## Related work

- [ReAct](https://arxiv.org/abs/2210.03629) — interleaved reasoning and action.
- [Reflexion](https://arxiv.org/abs/2303.11366) — feedback and episodic memory.
- [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — failure taxonomy.
- [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) — topology and coordination tradeoffs.
- [OrchestraBench](https://arxiv.org/abs/2608.05263) — failure and recovery metrics.
- [Recursive Harness Self-Improvement](https://arxiv.org/abs/2607.15524) — iterative harness revision.

These precedents motivate the experiments; they do not establish novelty. Pattern comparisons are baselines. A proposed extension is trace-conditioned control followed by bounded, typed graph-level harness optimization with held-out evaluation and optimization-cost accounting.

## Evidence and status

This is a research charter, not a results article. No performance or novelty claim is made. The repository and experiments are in setup. Negative results and limitations will be retained alongside positive results. Synthetic task performance is not evidence of production reliability.

[Pro-Log index](/pro-log/)
