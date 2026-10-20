---
name: test-audit
description: Evaluate test value when authoring or reviewing tests, perform a scoped test audit or authorized pruning, or diagnose fixture and snapshot drift. Use independent contracts and plausible defects instead of test-count or coverage targets.
---

# Test value and fixture diagnosis

Adapted from OpenClaw's test-audit skill, Copyright 2026 OpenClaw Foundation, MIT licensed.
See [attribution and license](references/openclaw-license.md). Project testing policy,
contracts, commands and protected compatibility baselines remain authoritative.

## Test-value gate

Before adding, materially rewriting or recommending removal of a test, establish:

1. The observable behavior, invariant or independently owned contract it protects.
2. The plausible defect that makes it fail for the intended reason.
3. Existing evidence at the strongest owner boundary, and the distinct risk this test covers.
4. Whether it needs production exports, toggles, wrappers or injection points used only by tests;
   prefer the real owner boundary when that extra machinery has no independent need.

Expected outcomes need an independent requirement, stable contract example or historical
regression. Computing them with the production helper under test or mocking the promised
outcome weakens the oracle. Demonstrate fail-before/pass-after for a bug regression when
practical; do not require an old-code reconstruction or extra full suite for every change.

Ordinary authoring/review needs this judgment, not a portfolio audit. For fixture failures,
read [fixture diagnosis](references/fixtures.md). For requested audits or pruning, read
[the bounded audit procedure](references/audit.md).

Neither fewer tests, unchanged coverage percentages nor green mocks establish retained reliability.
Do not add tests just because code changed, or remove coverage from a suspicious pattern alone.
