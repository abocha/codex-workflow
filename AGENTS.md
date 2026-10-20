# Codex Workflow repository

This repository is the canonical source of the Codex Workflow ChatGPT/Codex plugin.
Keep shared methods in `skills/`; project facts and mandatory policy belong to each consumer.
`plugin.json` owns package identity/version; `.codex/agents/` owns optional role defaults;
`templates/` contains integration assets. Installed plugin caches and archives are build outputs.

Preserve unrelated work. Use short-lived `codex/` branches; do not push to main. Task authorization
persists within scope; plugin creation does not authorize public sharing, CI/policy changes in a
consumer, user-level configuration edits or production actions. Do not include raw private rollout
evidence, secrets, session identifiers or local data in distributable archives.

Use the smallest adequate evidence: parse changed scripts, run their focused smoke checks, validate
skill metadata and internal routes, and inspect the built archive. `README.md` owns current commands.
Structural checks do not prove semantic preservation; trace moved requirements to their owners.
Before more probing, name the unresolved decision or failure it can resolve. Reuse valid evidence,
then finalize when acceptance and applicable gates are satisfied. Report unperformed hosted/manual
checks explicitly. Do not manufacture goals, agents or benchmark runs for this migration.

Create/update a private plugin only when requested, using Plugin Creator. Keep returned plugin
identity and release information in ignored local state; no account-specific IDs belong in the
portable manifest. Verify saved component files before claiming the upload is complete.
