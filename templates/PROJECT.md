# Project workflow adapter (optional)

Use this template only when project routing is substantial enough to justify a separate file.
Replace prompts with verified local routes; omit irrelevant sections. Do not create a second
workflow manual or copy mutable inventories that already have owners.

## Authorities and useful entrypoints

Identify repository instructions, architecture/contracts, implementation owners, validation
and operational routes. Link existing owners and state any non-obvious precedence rule.

## Evidence and environment

Point to focused execution recipes, prerequisites, required hosted checks and manual/environment
evidence. Record a command only if this is its actual owner. Missing CI is a fact, not a reason
to invent a gate. Specify suitable disposable environments for destructive tests where applicable.

## Material risks and action boundaries

Record unusual project-specific contracts, persistence/concurrency concerns, protected data,
external actions and release/deployment authorization routes. Shared review and evidence methods
belong in the plugin; actual project requirements remain local.

## Useful execution facts

Keep only information that materially changes work here and is expensive to rediscover, such as
a non-obvious generated artifact owner or unavailable local service. Omit generic workflow advice.
