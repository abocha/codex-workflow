# Adoption and migration

## Personal use across projects

Install the shared plugin in the host, then explicitly invoke `codex-workflow-setup` with project
access. Keep the universal operating minimum in your existing personal instructions if desired;
editing user-level configuration is a separate action, not an incidental setup step. Repository
instructions still need their mandatory policies for other contributors and plugin-unavailable use.

Setup inspects actual local instructions, architecture, manifests, CI and skills; it establishes
routes without inventing missing policy. A small Python project may need only a few additions to
`AGENTS.md`. A larger repository may justify a concise adapter and specialized local skills.

Shared methods are authored once here. Project-specific requirements are authored at their local
owners. Updating the plugin changes available methods; rerunning setup deliberately reconciles
integration. If a team later needs a pinned release, use the same upstream package rather than an
edited project edition. Do not implement another distribution system until that need is concrete.

## Existing copied installations

Start with the real local checkout, including uncommitted and ignored skill files. Compare active
routes, not GitHub main alone. Preserve unrelated work and unique project guidance.

The old `standard/` documents have been replaced by the shared references:

| Previous source | Current owner |
| --- | --- |
| Workflow modes and exploration | [Modes](skills/codex-workflow/references/modes.md) |
| Planning handoff and acceptance | [Planning](skills/codex-workflow/references/planning.md) |
| Delegation, role integrity, review and integration | [Orchestration](skills/codex-workflow/references/orchestration.md) |
| Context selection and continuation | [Context](skills/codex-workflow/references/context.md) |
| Model and effort defaults | [Models](skills/codex-workflow/references/models.md), plus actual role configuration |
| Evidence reuse, operational observations and stopping | [Evidence](skills/codex-workflow/references/evidence.md) |
| Mandatory operating minimum | [AGENTS fragment](templates/AGENTS-workflow.md), adapted to project instructions |

Install/verify the plugin before removing local procedures that rely on it. Transfer unique local
facts to their real owner, replace active links and triggers, and then retire the superseded copies.
Historical records remain history; they do not keep a second active workflow alive.

The deterministic staging helper is deliberately narrower than setup:

```powershell
pwsh ./scripts/install-into-repo.ps1 -TargetRepo C:/path/to/project
pwsh ./scripts/install-into-repo.ps1 -TargetRepo C:/path/to/project -IncludeRoles
pwsh ./scripts/compare-installation.ps1 -TargetRepo C:/path/to/project
```

It stages only `.codex/AGENTS-workflow.md` and optionally missing role definitions, never shared
skills/methods or an overwrite of project `AGENTS.md`. Existing files are left for semantic
reconciliation. The former blanket `-Force` operation is removed. Role staging is optional and
is not runtime registration; inspect current host support before using or claiming a role.
The comparison reports legacy copies and adapted roles; it cannot prove semantic compatibility.
Remove a staged fragment after its useful content has been integrated, rather than preserving it
as a competing owner. The helper never automatically deletes legacy or retired files.

## ESL Pipeline extraction boundary

The initial plugin was derived from current local ESL skills and their referenced owners:

| Local capability | Shared method | Remains with ESL |
| --- | --- | --- |
| PR/CI follow-up | Live-state inspection, failing-job diagnosis, scoped mutations and monitoring | Templates, exactly-one-release-label rule, required jobs and release policy |
| Test audit | Independent oracle, defect-catching value, audit/prune and fixture diagnosis | Protected product contracts, test membership, execution commands and retention policy |
| Docs gardening | Task-based semantic review, disposition and useful-history preservation | Governance, verification dates, lifecycle contract, generators and scheduled triage |
| Validation-system skill | General owner-boundary evidence reasoning in PR/CI/evidence references | Concrete scope classifiers, test projects, isolation and helper evidence maps |
| Deployment checklist | General probe-side-effect, evidence/rollback and closure reasoning | Production topology, image/environment rules, runbooks and authorization |
| Complexity discipline | Existing portable specialized skill | Any justified project-specific application |

Those shared methods do not require empty ESL wrapper skills. Retain a local skill only where it
adds useful local decisions/routes; preserve all binding project gates independently of optional
activation. ESL consumer migration is a separate integration step: building or creating the plugin
does not silently edit ESL policy or prove its setup is complete.

## Completion

Verify available skills, working paths/anchors and clear trigger/authority boundaries. For a project,
verify the actual evidence routes and mandatory policy still work, including when the plugin is
absent. Repeated setup preserves correct local adaptations. Report unresolved access/policy gaps,
local checks, observed hosted results and actions still owned by the operator separately.
