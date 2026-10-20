# Scoped audit and pruning

An audit is read-only unless changes are authorized. Pruning requires evidence for a coherent
batch, not a removal quota. A sweeping campaign needs its own scope and regression-risk boundary.
Preserve independently useful coverage and the project's required test/CI membership.

Start with a bounded owner and its production entrypoints, contracts, test configuration,
fixtures and existing evidence. Inspect callers, related tests and relevant history only as
needed to establish why a candidate exists and what would survive its removal.

For each material candidate, identify its exact path/test, protected behavior and plausible
regression; what assertions actually establish; mock or fixture limitations; independent owner;
surviving evidence; rationale; risk; and focused validation. Classify as retain, rewrite at a
stronger boundary, remove, or investigate further. State uncertainty and false positives.

Signals to investigate include self-comparisons or empty assertions; source/import greps that
break under behavior-preserving edits; repeated contract checks without a distinct defect class;
white-box call assertions; copied inventories; oversized incidental snapshots; fake persistence
that never produces the claimed state; capability flags without the promised delivery/acknowledgment;
test-only production machinery; negative cases rejected by an unrelated early guard; and test
titles stronger than the scenario. None is an automatic deletion rule.

Protect consequential security, data-integrity, lifecycle, concurrency, retry/idempotency,
migration and historical-compatibility coverage according to this project's actual contracts.
When moving coverage, establish the stronger surviving check before retiring its predecessor.

Use current owner commands and prerequisites, with checks focused on the affected defect class.
If test classification, CI routing or isolation changes, validate that mechanism separately.
Report retained valuable cases, meaningful production/test changes, exact evidence, missing
hosted/service observations and material uncertainty. Do not turn line-count reporting into
the success criterion or grant merge/deployment authority through a test audit.
