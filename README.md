# Codex Workflow

One maintained ChatGPT/Codex plugin for evidence-led engineering and project integration.
This repository is its canonical source. It is an independent project, not an official OpenAI workflow.

## Capabilities

| Skill | Use when |
| --- | --- |
| [codex-workflow](skills/codex-workflow/SKILL.md) | Choosing an uncertain control loop, substantial planning/handoffs, coordination, context, review or closure |
| [codex-workflow-setup](skills/codex-workflow-setup/SKILL.md) | Explicitly integrating or reconciling a project |
| [pr-ci](skills/pr-ci/SKILL.md) | PR metadata, hosted failure diagnosis, authorized fixes or requested monitoring |
| [test-audit](skills/test-audit/SKILL.md) | Test value, scoped audits/pruning or fixture diagnosis |
| [docs-gardening](skills/docs-gardening/SKILL.md) | Consequential documentation drift, consolidation and lifecycle cleanup |
| [complexity-discipline](skills/complexity-discipline/SKILL.md) | Non-trivial structural-complexity judgment |

Skills load relevant references progressively. Ordinary bounded work follows the project's sources
directly. No server, connector or new MCP service is required. Actual repository access, hosted
credentials and custom-role registration depend on the host; the plugin does not provide them.

## Install and integrate

Create the private account/workspace plugin from the validated archive using Plugin Creator, then
install/select it through the host's plugin interface. This is separate from building a ZIP.
Creation alone does not establish installation or skill discovery in a running session. Use
`codex-workflow-setup` in the project to connect shared methods to its existing instructions and tools.
See [adoption and migration](ADOPTION.md).

Keep mandatory authority, scope, evidence and stopping rules in personal/project instructions.
Projects retain their actual contracts, commands, CI gates and operational procedures. They do not
receive customized copies of the portable methods. A separate adapter is optional.

## Source and releases

- [plugin.json](plugin.json): portable package identity, version and presentation.
- [skills/](skills/): canonical skills and conditional references.
- [.codex/agents/](.codex/agents/): optional portable custom-role source definitions, unchanged by packaging.
- [templates/](templates/): small operating fragment and optional project adapter.
- [scripts/](scripts/): archive building, integration staging/comparison and optional metrics tools.
- [case-studies/](case-studies/): historical public-safe observations, not current procedure.

Author changes here, validate, build, inspect and update the same private plugin identity through
Plugin Creator. Installed caches and release archives are outputs, not editing locations. Update
existing plugins with their observed current release ID; do not create a second plugin for an upgrade.
Keep returned account-specific IDs/release metadata in ignored `.local-evidence/`, outside the portable
package. Private creation does not authorize public sharing or directory submission.

## Validation and packaging

Maintainer tooling needs PowerShell and Python 3.11+ with PyYAML. A disposable virtual environment
keeps that validation dependency separate from projects and the plugin runtime:

```powershell
python -m venv .local-evidence/validation-venv
./.local-evidence/validation-venv/Scripts/python.exe -m pip install PyYAML==6.0.3
./.local-evidence/validation-venv/Scripts/python.exe scripts/build-plugin.py
pwsh ./scripts/test-project-integration.ps1
pwsh ./scripts/test-rollout-metrics.ps1
./.local-evidence/validation-venv/Scripts/python.exe scripts/build-plugin.py --output C:/temp/codex-workflow-0.1.0.zip
```

Write the archive outside the source checkout. The builder parses manifest/YAML/TOML, checks
package-relative links and anchors, rejects linked/unexpected components, and reopens the archive
to verify file names and bytes. It packages only `plugin.json`, `skills/`, `templates/` and
`.codex/agents/`. Scripts, case studies, Git metadata and local evidence are excluded.

The integration smoke check exercises preservation of existing policy/adaptations and repeatability
in a disposable directory. Hosted checks remain separate evidence. Structural green does not prove
method quality or runtime discovery; verify saved component files after account creation and try
naturally useful requests after installation. Do not manufacture A/B benchmarks or agent campaigns.

## Public evidence policy

Do not publish raw rollout JSONL, session identifiers, private-repository snapshots, prompts,
worktree dumps, credentials or forensic telemetry. Metrics tools consume local evidence; preserve
only sanitized conclusions in public case studies. Do not encode runtime token counts or quota
formulas as permanent execution rules.

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
