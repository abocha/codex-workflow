---
name: pr-ci
description: Prepare or update pull request metadata, diagnose a hosted CI failure, perform an authorized fix-and-push pass, or monitor requested checks. Routine local validation before a PR exists follows the project's evidence route.
---

# Pull requests and hosted CI

Read the current PR body, labels, head and checks. Discover the project's actual template,
release policy, required checks and external-action boundaries; do not assume a particular
language, label scheme, hosting provider or merge process. Use available authenticated tools
or CLI. Missing access is a limitation, not an observed hosted result.

A request to inspect or diagnose does not authorize metadata edits, code changes, pushes,
submitted reviews or ongoing monitoring. Carry existing authorization forward within its scope.

## Diagnose the actual failure

Start from the failing job's first relevant error and retained logs/artifacts. Check which
revision, command, configuration and prerequisites it exercised. A neighboring green job or
stale local result does not establish this boundary.

Reproduce locally when the result can resolve a concrete uncertainty. Match the conditions
that matter rather than substituting an unrelated broad gate. Inspect retained evidence
before rerunning unchanged work. Diagnose infrastructure/prerequisite failures instead of
retrying until a green result appears; follow project retry rules.

If the mechanism under test is CI scope, test classification, environment isolation or another
validation mechanism, inspect its implementation and a plausible failure it could introduce.
Use the project's specialized validation-system route when present; fixtures and test quality
have their own `test-audit` method.

## Mutate and finish within scope

Use the current template and policy for authorized PR creation or metadata edits. Validation
text lists evidence actually obtained. After a mutation or push, re-read the relevant live
state and revision before claiming success. Do not infer hosted success from local green.

Monitoring a later result is a separate requested activity; one fix or push does not authorize
continued babysitting. When monitoring is requested, use bounded waits and inspect meaningful
state changes. Stop at the requested completion/failure boundary or required user decision.
Merge, release and deployment retain their own authorization and project gates.

Report PR identity, actions actually taken, exact hosted/local evidence, observed check state,
and remaining maintainer-owned steps. Apply [evidence and closure](../codex-workflow/references/evidence.md)
when evidence reuse or further investigation is in question.
