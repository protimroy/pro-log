# Independent verification of narrative validation

All 236 artifact checks passed. This was a CPU/read-only verification, not another training run. Source and protocol hashes match the recorded CUDA audit; backend hashes match the benchmark. All 14 saved prediction files reproduce reported accuracy and cross-entropy. Paired runs have identical recorded initialization and full augmented-batch sequence hashes. These records provide consistency evidence, not cryptographic proof of execution.

## Corrected timing status

The benchmark completed: **5.203 ms HFD versus 2.104 ms AdamW**, **+3.099 ms**, **2.473×**. Four windows per method, 512 steps per window, one session. The original report incorrectly maps missing `passed`/`status` fields to failure. Its separate 5% and 10% improvement targets did fail: measured improvement over the previous HFD implementation was only 2.35%. That is distinct from benchmark execution failure. Memory peaks are process-wide and drift across windows; do not claim isolated optimizer-memory savings.

## Quality and statistics

Final width 512, depth 32: HFD **57.86%**, AdamW **62.99%**. Paired gap **5.127 pp**, sample SD **0.406 pp**, exploratory 95% t interval **[4.119, 6.134] pp**. The predeclared mean-gap ≤5 pp criterion fails; ≤2 pp also fails. The interval crossing 5 does not turn the observed mean into a pass, nor establish equivalence. Only three seeds and one shared test set were used.

All six final model checkpoints are tensor-for-tensor identical to their historical batched-training counterparts. The runner constructs the latest cache-ordered backend and uses separate new output paths; exact agreement is consistent with deterministic, arithmetic-preserving changes. Artifacts alone cannot independently establish execution history. These are the same seed/trajectory outcomes, **not six new independent observations**; do not pool historical and new runs to increase sample size. This run documents latest-backend provenance and predictions for those outcomes.

Calibration means: JP 44.14%, AdamW 42.61%, probe C/S 29.70%, forward C/S 28.75%. This 390-step, two-seed pilot demonstrates learning and does not rank final quality. Replacing probes with exact JVPs alone did not consistently improve C/S: changes were +0.04 and −1.94 pp. It does not establish that C/S dynamics caused the final JP gap.

## Mathematical and narrative conclusions

Recorded CPU/CUDA math checks pass. Full-basis JVP/local reconstruction agrees with the diagnostic oracle; sparse directional exactness does not imply exact reconstructed full credit. The implemented S observes updated C squared. Both the generic rotation and the actual aligned-refresh counterexample refute exact second-moment transport; that refresh remains heuristic. A shared-mean Jacobian counterexample establishes an expressivity limitation, not its measured prevalence on CIFAR.

Keep three mechanisms distinct: probes + C/S; the newly constructed JVP + C/S sensor control; and HFD-JP's biased learned prior + AdamW actuator. Historical early HFD remains author-provided lineage without a recovered executable replication. Canonical shallow HFD's historical minimum-criterion pass remains separate from this depth-32 failure.

## Publication assessment and remaining evidence

Publishable as a bounded empirical research report, including negative results; not evidence of AdamW equivalence or a universal backprop replacement. Publish the protocol, frozen sources, retained failures, prediction records, confidence-interval assumptions and the checkpoint-identity finding. Missing for stronger claims: recovered early-HFD sources; full-horizon matched probe/C-S trials; additional predeclared seeds and architectures; independent timing sessions and isolated memory measurements; direct example-conditioned credit diagnostics before attributing the gap to prior expressivity. Saved model tensors were compared, but model inference was not rerun during this review.

Agents/harness optimization, Transformer post-training and continual learning are future work. Exact JVPs require derivative access and do not by themselves support opaque verifier-only objectives. No current result establishes transfer to those settings.

The original source-hashed runner and results are preserved. `verify_results.py` reproduces this independent review; `verified_results.json` records every check.
