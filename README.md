# codex-workflow

[![scripts-ci](https://github.com/abocha/codex-workflow/actions/workflows/scripts-ci.yml/badge.svg)](https://github.com/abocha/codex-workflow/actions/workflows/scripts-ci.yml)

A portable, evidence-driven workflow for choosing the lightest safe control loop: bounded one-off work, exploratory campaigns, or quota-conscious multi-agent implementation.

> Independent experimental project. This repository is not an official OpenAI or Codex workflow, and model-specific defaults are expected to evolve.

Choose the workflow mode before choosing agents:

| Mode                     | Shape                                                                                                         | Default controller                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Atomic task**          | One bounded question, investigation, edit, or report.                                                         | One capable model/thread -> one result.                                                                |
| **Exploratory campaign** | Related questions under one umbrella where each answer determines the next useful probe.                      | Maintainer + ChatGPT steer; Codex threads are bounded probes/implementers.                             |
| **Goal execution**       | A stable desired outcome requiring several dependent implementation steps; the path may be known or adaptive. | Plan-backed by default; optionally an approved Goal Contract -> GPT-6.1 Sol primary orchestrator. |

For substantial Goal execution, plan-backed execution remains the normal path:

```text
ChatGPT / strong interactive reasoning
interactive design + detailed planning
        |
        v
approved design + implementation plan
        |
        v
Codex / GPT-6.1 Sol, effort matched to the task
primary orchestrator
        |
        +--> GPT-6 Luna xhigh: bounded coherent implementation
        +--> GPT-6.1 Sol medium: conditional exploration
        +--> GPT-6.1 Sol high: integration-heavy implementation
        +--> GPT-6.1 Sol medium: ordinary coherent review
        +--> GPT-6.1 Sol high: exceptional-risk review only
        |
        v
primary integration + repository validation
```

Goal execution also has one optional adaptive variant, not a fourth top-level mode:

```text
contained known-path change
  -> approved plan
  -> plan-backed primary agent

broad adaptive but verifiable objective
  -> approved Goal Contract + current plan/evidence
  -> goal-backed primary agent
```

In goal-backed orchestration, the goal is the durable completion boundary and the implementation plan is revisable strategy. The primary agent owns one root goal; children remain ordinary coherent ownership-boundary workers, not durable subgoals. Ordinary bounded work should not use goal mode.

The goal is not to maximize the number of agents. It is to match the control loop to the problem shape, keep a strong primary agent in control when orchestration is actually needed, preserve useful hot context when rediscovery would dominate the work, and avoid repeated exploration, giant inherited histories, duplicate review, and micro-step ceremony.

Model defaults are revisable: see `standard/WORKFLOW_MODES.md` for selective Astra use and planning where local evidence is available. Primary ownership does not depend on a model name.

## Repository layout

- `standard/WORKFLOW_MODES.md` — when to use atomic work, an exploratory campaign, or the plan-backed/goal-backed variants of Goal execution.
- `standard/ORCHESTRATION.md` — portable execution rules for the Codex primary agent during Goal execution.
- `standard/PLANNING_HANDOFF.md` — how ChatGPT should write implementation plans that hand off cleanly to Codex.
- `skills/complexity-discipline/SKILL.md` — situational reasoning procedure for structural-complexity decisions.
- `.codex/agents/*.toml` — reusable custom role definitions.
- `templates/AGENTS-delegation.md` — delegation/routing section to merge into a target repository's existing `AGENTS.md`.
- `templates/PROJECT.md` — repository-specific adapter template for docs, validation gates, risk surfaces, and manual checks.
- `scripts/install-into-repo.ps1` — copies the portable workflow into another repository without rewriting its `AGENTS.md`.
- `scripts/list-codex-root-tasks.ps1` — lists recent root Codex tasks and turn IDs from local rollout files.
- `scripts/export-rollout-metrics.ps1` — extracts role/model/token traces for local analysis.
- `scripts/test-rollout-metrics.ps1` — synthetic smoke test for whole-thread and turn-scoped measurement.
- `case-studies/` — public-safe summaries of the observations that changed the workflow.
- `ADOPTION.md` — practical confidence-building path from pilot repo to large repo.

### Public evidence policy

The workflow was developed against real Codex runs, but this public repository intentionally does **not** publish raw rollout JSONL, session identifiers, private-repository snapshots, prompts, local worktree dumps, or other forensic telemetry. The `case-studies/` directory keeps the useful engineering conclusions without turning a workflow repository into an archive of private execution state.

Raw telemetry is best treated as local analysis input: inspect it, derive the smallest durable conclusion, then keep only the sanitized conclusion in version control.

## Quick start

Clone this repository somewhere stable, then install the workflow into a target repository:

```powershell
pwsh ./scripts/install-into-repo.ps1 -TargetRepo C:\path\to\your-project
```

The installer copies the five role definitions plus the workflow-mode guide, orchestration standard, planning handoff, project-adapter template, and AGENTS delegation fragment into the target repository's `.codex/` directory. It also installs the situational `complexity-discipline` skill under `.agents/skills/complexity-discipline/` so current Codex project-local skill discovery can index it.

It intentionally does **not** edit the target repository's real `AGENTS.md`. Merge the relevant parts of `.codex/AGENTS-delegation.md` manually so existing repository policy remains authoritative.

### Updating an existing installation

Without `-Force`, existing workflow files are intentionally left untouched. If an existing installation receives the new `complexity-discipline` skill while its existing AGENTS delegation fragment is skipped, the installer prints a targeted warning. Reconcile the current portable workflow fragment from `templates/AGENTS-delegation.md` into the target repository's real `AGENTS.md`; pay particular attention to Complexity Discipline routing when the skill was newly installed.

Do not use `-Force` as a blanket upgrade mechanism unless all local workflow customizations have been reviewed. A repository may intentionally have adapted copies of the portable files, so upgrades remain a manual reconciliation step rather than an overwrite operation.

An existing installation with the old model-named role files requires manual role reconciliation. `compare-installation.ps1` reports them as `retired-role-present`, and the installer stops before copying new roles while they remain. Update any target-repository role references and remove the retired definitions there before running the installer; `-Force` does not perform this migration. A fresh Codex session may be needed for changed role registrations to load.

Then fill in `.codex/PROJECT.md` with that repository's real documentation routes, validation commands, known ownership boundaries, and exceptional-risk surfaces.

Before starting work, use `.codex/WORKFLOW_MODES.md` to choose the lightest safe control loop. The merged AGENTS routing should invoke `$complexity-discipline` in Codex only when structural-complexity judgment is genuinely non-trivial; routine pattern-following work should not pay the ceremony cost. ChatGPT-side planning applies the same reasoning procedure from the installed skill source when available rather than assuming Codex `$skill-name` invocation semantics.

For a substantial Goal execution change:

1. Design it interactively in ChatGPT.
2. Ask ChatGPT to produce an approved design and implementation plan following `standard/PLANNING_HANDOFF.md` (or the copied `.codex/PLANNING_HANDOFF.md`).
3. Start Codex with GPT-6.1 Sol at an effort proportionate to the task and point it at the approved plan, the target repository's `AGENTS.md`, `.codex/ORCHESTRATION.md`, and `.codex/PROJECT.md`.
4. Let the Codex primary agent choose the smallest useful set of custom roles from the actual repository state and diff.
5. After completion, optionally measure the run and compare orchestration cost/quality with earlier evidence.

For an exploratory campaign, keep the maintainer + ChatGPT conversation as the controller/notebook and use bounded Codex prompts for the next evidence-producing question or direct low-risk consequence. Promote to the planned/orchestrated path only when a concrete end state and dependent implementation have emerged.

Use the optional goal-backed path only when the outcome is approved, verifiable, and expected to outlast a fixed current task list while the strategy adapts. Treat the first naturally suitable goal-shaped run as evidence about the policy before adding more machinery or ceremony.

See `ADOPTION.md` for the recommended pilot -> measured run -> large-repository rollout.

## Measuring a run

First find recent root tasks. `-CwdContains` is optional but useful when several repositories share the same Codex sessions directory.

```powershell
pwsh ./scripts/list-codex-root-tasks.ps1 -CwdContains med-checkin
```

For a root thread used for only one task, the original whole-thread export remains available:

```powershell
pwsh ./scripts/export-rollout-metrics.ps1 -RootThread <thread-id>
```

If the same root thread was reused for later work, list its turns and export only the one being evaluated:

```powershell
pwsh ./scripts/export-rollout-metrics.ps1 -RootThread <thread-id> -ListTurns
pwsh ./scripts/export-rollout-metrics.ps1 -RootThread <thread-id> -TurnNumber 1
```

You can use `-TurnId <turn-id>` instead of `-TurnNumber`. Turn-scoped export subtracts the root session's cumulative token counters from immediately before that `task_started` event and includes only descendant sessions spawned during the selected turn. This prevents a later release, follow-up, or unrelated task in the same root thread from contaminating the measured run.

The exporter writes per-thread summary and token-event CSVs. Use uncached input, reasoning output, duration, token-event count, actual role/model routing, and review findings together; raw token totals alone are often dominated by cached context reuse.

## Current portable role defaults

These are defaults for **Goal execution**, not universal truths:

| Role | Model | Launch effort | Purpose |
| --- | --- | --- | --- |
| Primary | GPT-6.1 Sol | task-dependent | decomposition, integration, final accountability |
| `bounded_implementer` | GPT-6 Luna | xhigh | specified, pattern-following implementation |
| `explorer` | GPT-6.1 Sol | medium | conditional read-only repository tracing |
| `integration_workhorse` | GPT-6.1 Sol | high | predetermined implementation with coupled contracts |
| `ordinary_reviewer` | GPT-6.1 Sol | medium | coherent correctness and integration review |
| `exceptional_risk_reviewer` | GPT-6.1 Sol | high | narrow high-consequence review |

These are portable launch defaults, not fixed ceilings or authorization rules. For the primary, medium fits a typical coherent task; lower it for clear bounded coordination or raise it for substantial uncertainty and consequence. A bounded Luna assignment starts at xhigh; its effort may be adjusted when the actual task warrants it without expanding that role's authority. Sol roles may also use a supported different effort when the actual task warrants it. Use Astra selectively for especially difficult repository-grounded reasoning as described in `standard/WORKFLOW_MODES.md`. Target repositories can deliberately adapt the defaults.

## Design principles

- Choose Atomic task, Exploratory campaign, or Goal execution before choosing agent choreography.
- Keep Goal execution plan-backed by default; use goal-backed orchestration only for an explicitly approved stable outcome with an adaptive execution path.
- Detailed plans are parent-facing contracts for Goal execution. Child prompts are compressed deliverables.
- Delegate by coherent ownership boundary, not mechanically by numbered plan task.
- Exploration is conditional when the plan already contains a fresh repository map.
- In exploratory campaigns, one prompt -> one result is often the correct shape; do not invent a primary orchestrator before the end state is known.
- Reuse a hot thread when it already owns expensive evidence and the next step is a direct bounded consequence; continuation prompts should be deltas, not restated specifications.
- Structural complexity needs a concrete necessity chain. Use the situational complexity discipline for non-trivial judgments, considering reuse, reversibility, known constraints, and retrofit cost rather than applying YAGNI mechanically.
- Prefer the simplest adequate design, not the smallest diff, fewest files, or cleverest one-liner.
- Luna handles specified bounded implementation; Sol handles repository and integration judgment. Choose effort for the actual uncertainty and consequence, not task size alone.
- Review follows residual semantic risk, not the mere existence of a diff; fold a proportional complexity check into an already-justified review rather than creating a dedicated complexity reviewer by default.
- A single coherent final whole-branch review can be useful for substantial multi-boundary changes where cumulative cross-boundary risk is plausible.
- KEEP and DEFER are successful investigation outcomes when evidence does not justify churn.
- Use fresh child contexts when independence, a new ownership boundary, or a different capability materially warrants them; reuse an existing owner when rediscovery would dominate.
- The primary owns integration and repository-level validation even when children test their own work.
- Measure occasionally, and scope metrics to the actual root turn when a thread is reused.
- Do not turn runtime-specific token numbers into hard policy.

This repository is intentionally project-agnostic. Project-specific architecture, commands, deployment rules, and risk invariants belong in each target repository, not here.
