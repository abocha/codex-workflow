# Fixture and snapshot drift

A failing fixture is a diagnosis, not permission to bless current output. Identify whether
it is representative current input, a deliberate negative/edge case, a generated preview,
or a pinned historical/golden contract. Find its independent authority and the first relevant
failure before editing expectations.

- Unintended behavior: fix implementation and preserve the independent expectation.
- Approved contract change: update the smallest canonical fixture/factory and relevant expectations,
  explaining the new authority. Historical and compatibility baselines remain protected unless
  their requirement was deliberately changed within authorization.
- Incidental churn: assert the meaningful semantic slice or replace redundant large samples with
  compact input. Establish surviving defect coverage before deleting or weakening assertions.
- Unknown cause: trace the owner/callers until the difference can be classified; do not bulk-regenerate
  snapshots or use current production output as the sole oracle.

Normalize variable timestamps, random IDs, unrelated optional fields or unordered collections only
when they are non-contractual. Full bytes or hashes may themselves be the promised contract.
Regenerate previews from their canonical source and inspect the diff rather than hand-editing them.

For each repair, report the changed contract or unchanged behavior, fixture source/expectation changed,
why the old value was obsolete, and the focused observation establishing the desired result.
Check granularity and ownership when the same incidental failures recur.
