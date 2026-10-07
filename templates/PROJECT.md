# Project Orchestration Adapter

This file maps the portable Codex workflow onto repository-specific facts.

Keep it concise and current. Portable workflow mechanics belong in `WORKFLOW_MODES.md` and
`ORCHESTRATION.md`; durable repository policy belongs in the repository's instruction/SSOT layer.
Use this adapter only for facts the orchestrator needs to apply those rules correctly here.

## Authority and routing

List the smallest authoritative routes needed for common work.

- Repository instructions / SSOT: `<path>`
- Architecture / contracts: `<path>`
- Validation / CI: `<path>`
- Release / deployment: `<path>`
- Other subsystem routers: `<path>`

State any important precedence rule that is not already obvious from the repository instruction
chain.

## Validation mapping

Discover commands and gates from current manifests, task runners, documentation, and CI. Do not
invent or preserve remembered commands here after their owner changes.

### Focused local evidence

Typical owning-package or targeted routes:

```text
<command or route>
```

### Broader local evidence

Record only broader local gates that the repository actually uses, including the conditions that make
them proportionate. Use `N/A` when comprehensive local execution is not part of normal workflow.

```text
<command, conditional route, or N/A>
```

### Hosted / CI-owned evidence

- `<required or situational hosted check>`
- `<service-backed or environment-owned check>`

### Manual or environment-owned evidence

- `<manual/runtime check>`
- `<production/service check>`

For destructive install, upgrade, migration, or data checks, state whether a disposable environment
is required. Do not imply that a real user installation or production data is an acceptable test
target.

## Common ownership boundaries

Record coherent repository areas that are expensive to rediscover and often useful for delegation.

- `<subsystem or workflow>`
  - likely files/packages: ...
  - important contracts or authority: ...

- `<subsystem or workflow>`
  - likely files/packages: ...
  - important contracts or authority: ...

These are repository maps, not mandatory child assignments. The primary owns decomposition for the
actual task.

## Exceptional-risk surfaces

Record repository-specific areas whose actual modification can carry unusual semantic consequence.

- `<authorization/security/privacy surface>`
- `<persistent-data/migration/restore surface>`
- `<concurrency/retry/idempotency surface>`
- `<destructive filesystem/production surface>`

Include only repository-specific information that helps identify or understand the risk. Portable
review routing remains owned by `ORCHESTRATION.md`.

For shared mutable state, record durable ordering, fencing, ownership, or mutual-exclusion invariants
when they are important and not cheaply discoverable elsewhere.

## Mutation and operational boundaries

Record repository-specific authorization or operational facts that must not be guessed.

Describe any repository-specific branch practice, external action boundary, protected environment,
or operational route that changes how an authorized task is completed.

Do not duplicate generic portable authorization rules here.

## Repository-specific execution notes

Add only facts that materially change how the portable workflow should operate in this repository,
for example:

- a service unavailable in local development;
- an expensive package boundary that should normally stay with one owner;
- a generated artifact whose owner is non-obvious;
- a hosted validator that substitutes for an impractical local check;
- an environment limitation that changes evidence strategy.

Do not repeat generic advice about role selection, context freshness, review ceremony, or primary
ownership. Those belong to the portable standard.
