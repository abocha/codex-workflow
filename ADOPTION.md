# Adoption checklist

This is the shortest path from "workflow repository exists" to "I can trust it on a large codebase."

## Phase 1: Install into a pilot repository

Use a repository where mistakes are recoverable and the implementation surface is understood.

```powershell
pwsh ./scripts/install-into-repo.ps1 -TargetRepo D:\code\pilot-repo
```

Then:

- [ ] inspect the copied `.codex/agents/*.toml` files;
- [ ] merge the relevant content from `.codex/AGENTS-delegation.md` into the repository's real `AGENTS.md`;
- [ ] fill in `.codex/PROJECT.md` with real documentation routes and commands;
- [ ] confirm `.codex/WORKFLOW_MODES.md`, `.codex/ORCHESTRATION.md`, and `.codex/PLANNING_HANDOFF.md` are present;
- [ ] confirm `.agents/skills/complexity-discipline/SKILL.md` is present; restart Codex if needed before relying on project-local skill discovery;
- [ ] if this is an existing installation and the installer reports that the portable skill was copied while the AGENTS delegation fragment was skipped, reconcile the current portable workflow fragment into the repository's real AGENTS.md before relying on it; pay particular attention to the Complexity Discipline routing when the skill is newly installed;
- [ ] inspect `git diff` and commit only after the repository-specific adapter is accurate.

Do not use `-Force` as a blanket upgrade mechanism. Existing installed workflow files may contain repository-specific adaptations, so review and manually reconcile upstream changes before overwriting them.

Use `scripts/compare-installation.ps1 -TargetRepo <path>` to distinguish missing, identical, formatting-only, and substantive differences before reconciliation. Adapted copies require semantic review; matching hashes are not required for declared repository adaptations.

If comparison reports `retired-role-present`, reconcile target-repository references and remove the old model-named role files before installing the semantic roles. The installer stops before copying while those files remain, including with `-Force`.

Do not replace good existing repository instructions wholesale. Integrate the portable delegation rules into the repository's current authority chain.

Before testing multi-agent orchestration, read `WORKFLOW_MODES.md`. The workflow should also make Atomic tasks and Exploratory campaigns cheaper, not turn every repository task into Goal execution.

## Phase 2: Harmless role-routing smoke test

Before important Goal execution implementation, run one fresh Codex task that delegates harmless read-only or no-op probes to the configured roles.

Verify through rollout metadata that:

- [ ] `bounded_implementer` actually routes to GPT-6 Luna / xhigh;
- [ ] `explorer` and `ordinary_reviewer` route to GPT-6.1 Sol / medium;
- [ ] `integration_workhorse` and `exceptional_risk_reviewer` route to GPT-6.1 Sol / high;
- [ ] children have parent linkage and fresh task contexts;
- [ ] no silent generic/default-model substitution occurred.

Do not use a production change as the first test of custom-role routing.

## Phase 3: One real bounded Goal execution task

Choose a task with:

- an approved design;
- observable acceptance criteria;
- a known validation path;
- recoverable local changes;
- enough substance to exercise delegation, but not enough blast radius to make the workflow itself the dominant risk.

Have ChatGPT produce the design and implementation plan using `standard/PLANNING_HANDOFF.md`.

Start Codex with the repository instructions and approved artifacts. The primary should:

- group work by coherent ownership boundary;
- skip redundant exploration when the plan map is fresh;
- use the bounded implementer at its xhigh launch default for specified, pattern-following implementation; adjust effort when justified within that boundary;
- use the Sol integration workhorse when semantic coupling or repository judgment warrants it, not merely because a task is large;
- use ordinary review proportionately to residual semantic risk;
- invoke exceptional-risk review only for a concrete high-consequence surface in the actual diff;
- keep one final coherent whole-branch review when substantial multi-boundary changes make cross-boundary regressions plausible.

When current repository policy already calls for a broad local gate and it is proportionate to the change, prefer obtaining that evidence before expensive semantic review. Do not introduce a broad local gate solely because delegated work or review occurred.

Separately try at least one naturally occurring Atomic task or Exploratory campaign without forcing it through the full Goal execution ceremony. In an exploratory campaign, verify that bounded probes can reuse hot context when useful and that the campaign can legitimately end in KEEP or DEFER without manufacturing implementation work.

## Phase 4: Measure the run

Find the root Codex task and turn:

```powershell
pwsh ./scripts/list-codex-root-tasks.ps1
```

If the root thread contains only the run being measured:

```powershell
pwsh ./scripts/export-rollout-metrics.ps1 -RootThread <thread-id>
```

If the root thread was reused for later work, inspect its turns and export the relevant one:

```powershell
pwsh ./scripts/export-rollout-metrics.ps1 -RootThread <thread-id> -ListTurns
pwsh ./scripts/export-rollout-metrics.ps1 -RootThread <thread-id> -TurnNumber <n>
```

`-TurnId <turn-id>` is also supported. Prefer turn-scoped metrics whenever a root session contains several tasks; Codex token counters are cumulative within the root session, so timestamp filtering without baseline subtraction overcounts later turns.

Review:

- actual role/model routing;
- token-event count;
- uncached input;
- cache rate;
- reasoning output;
- duration;
- whether child prompts caused obvious micro-step churn;
- whether review found defects that justified its cost.

Do not optimize from one number alone. Raw input can look enormous while most of it is cached context reuse.

Exploratory campaigns can also be useful qualitative evidence even when no rollout-metadata pass is justified. Label those conclusions clearly as qualitative rather than mixing them with measured telemetry.

## Phase 5: Adjust one variable at a time

Examples:

- reduce child-prompt choreography while keeping the same model/effort;
- skip a redundant explorer pass when planning evidence is fresh;
- group two adjacent tasks into one ownership boundary;
- narrow exceptional-risk review to the actual high-risk path;
- reuse a hot investigator for a direct bounded implementation consequence instead of paying fresh-context rediscovery;
- when a final whole-branch review is independently justified, skip one dedicated ordinary review only for a small validated non-exceptional-risk child and measure whether later review finds an attributable gap.

Avoid simultaneously changing model, reasoning effort, role boundaries, and validation policy. Otherwise the next trace will not tell you what improved or regressed.

## Phase 6: Move to a large repository

Before adopting the workflow in a large or quota-sensitive repository, make a repository adapter that is actually worthy of the codebase.

At minimum establish:

- [ ] authoritative documentation routes;
- [ ] canonical focused validation routes and any broader local or hosted merge gates the repository actually requires;
- [ ] common subsystem/ownership boundaries;
- [ ] CI-owned evidence and services unavailable locally;
- [ ] migration / authorization / persistence / production risk surfaces;
- [ ] commit, push, PR, release, and deployment authorization rules;
- [ ] rules for preserving concurrent or intentionally dirty worktrees;
- [ ] which destructive/manual checks require a disposable environment rather than the user's real installation or data.

Then run a bounded task before entrusting the orchestrator with a large cross-cutting feature.

## Confidence criteria

The workflow is ready for more consequential work when repeated runs show:

- mode selection is proportionate: Atomic tasks stay atomic, Exploratory campaigns stay steerable, and Goal execution receives orchestration when it actually helps;
- role routing is reliable;
- the primary respects repository policy and approved scope;
- children stay within ownership boundaries;
- hot contexts are reused when rediscovery would dominate, without sacrificing independence where review genuinely needs it;
- Luna completes bounded work without excessive orchestration churn;
- Sol effort rises with integration judgment and consequence rather than staying fixed for every task;
- review catches real defects without becoming universal ceremony;
- final whole-branch review finds cross-boundary defects often enough to justify its cost on substantial work;
- repository-level validation is still owned by the primary;
- destructive/manual validation is not improvised against real user data when a disposable environment is unavailable;
- rollout traces are understandable enough to explain where quota went, including when a root thread is reused.

The goal is not zero overhead. The goal is predictable overhead that buys useful context isolation, uncertainty reduction, implementation throughput, and independent review only where those benefits are real.
