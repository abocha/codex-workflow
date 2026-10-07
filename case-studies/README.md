# Public case studies

This directory records the observations that materially changed `codex-workflow`.

The original investigations used real repositories and local Codex telemetry. Raw rollouts, session identifiers, prompts, private-repository snapshots, worktree dumps, and account-specific paths are intentionally excluded from the public repository. These summaries preserve the decision-relevant engineering lessons instead of the forensic source material.

## Included summaries

- [Orchestration baselines](orchestration-baselines.md) — what measured runs taught about delegation, review, and turn-scoped metrics.
- [Context economics](context-economics.md) — when hot-context reuse helps and when carrying context becomes the larger cost.
- [Validation and closure](validation-and-closure.md) — how repeated proof-seeking can outlive the decision it was meant to support.

The case studies are evidence for defaults, not universal laws. Model behavior, tooling, context windows, and repository shapes change; the workflow is expected to change with them.
