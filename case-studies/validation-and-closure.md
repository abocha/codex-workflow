# Validation and closure

A production-oriented run exposed a subtle failure mode: strong requirements for safety, evidence, rollback, and exact validation can keep an agent proving the same conclusion after the relevant decision is already resolved.

The failure was not insufficient diligence. It was missing closure semantics.

A useful validation probe must resolve a concrete outstanding decision, acceptance criterion, or plausible alternative explanation. Once valid evidence already composes to satisfy the criterion, repeating broader readbacks or reconstructing a benign anomaly is not automatically safer. It can increase cost, expand the live-operation surface, and make completion less legible.

The workflow was tightened around four rules:

- identify the unresolved decision or evidence gap before another probe;
- reuse still-valid evidence instead of demanding ritual re-proof;
- investigate anomalies proportionately to whether an alternative explanation could change the decision;
- treat declared completion as a real phase transition unless a concrete unresolved criterion remains.

This does not weaken authorization, rollback, security review, or repository gates. It makes "strong evidence" finite: evidence is collected to support a decision, not as an open-ended activity.

The public repository keeps this policy consequence but intentionally excludes the original raw prompts, session identifiers, private repository references, and response-level telemetry.
