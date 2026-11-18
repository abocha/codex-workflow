---
name: test-audit
description: Use when the choice of assertion, fixture or test boundary could hide a plausible defect, when diagnosing fixture or snapshot drift, or for a requested test audit or authorized pruning. Routine regression tests with clear expected behavior can follow project conventions directly.
---

# Test value and fixture diagnosis

Adapted from OpenClaw's test-audit skill, Copyright 2026 OpenClaw Foundation, MIT licensed.
See [attribution and license](references/openclaw-license.md). Project testing policy,
contracts, commands and protected compatibility baselines remain authoritative.

## Test-value gate

A service can commit a ledger entry and lose its response. A retry test that checks only the final response could pass even if the service writes twice. Check the persisted entries after retrying.

When deciding what evidence a test needs, establish:

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
