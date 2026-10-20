# Evidence and closure


Across workflow modes, before another probe, identify the concrete unresolved decision, acceptance criterion, failed invariant, or material anomaly its result can resolve. Additional confidence alone is insufficient justification. Stop when evidence is sufficient for that branch; reopen it only when new evidence changes its basis.

Reuse still-valid evidence while its relevant inputs and semantics remain unchanged. Later unrelated execution does not automatically invalidate earlier evidence. Refresh evidence whose validity depends on changed state or time, and follow required repository gates.

Safety, fidelity, rollback, and exact-evidence requirements define what must be established; they do not create an open-ended obligation to strengthen proof after the applicable criteria are satisfied. Preserve the rigor actually required by the completion contract.

Investigate unexpected anomalies in proportion to their possible effect on the decision. An explained benign delta may still warrant direct corroboration; exhaustive forensic reconstruction requires a plausible alternative explanation that could materially change the decision. Close the branch once sufficient evidence resolves it.

Once the completion contract is satisfied, enter closure: record and preserve existing evidence, report the result and limitations, and perform required finalization and cleanup. Treat satisfaction of the required acceptance criteria and repository-required gates as a phase transition, not an invitation to search for further confidence. In closure, do not start new repository-wide searches, adjacent-consumer or provider traces, compatibility audits, repeated validation passes, or other probes unless a newly failed invariant, unexplained material anomaly, or genuinely missing completion criterion gives that work a concrete decision to resolve.

A schema, domain-field, or compatibility change does not by itself justify tracing every downstream consumer or provider after the affected contract and identified material consumers are validated. Broaden that trace only when code evidence, a failed check, or a known dependency makes the adjacent surface material to completion.


## Repository evidence and operational boundaries

Repository policy owns required gates, commands, prerequisites and merge conditions. Choose evidence for the plausible failure at its real owner boundary; do not substitute a passing neighboring suite or a source grep for behavioral evidence. A test-first reproduction is useful for subtle regression risk; existing tests, compilation, direct observations or a working vertical slice may be the right evidence for other tasks. Strict TDD and new tests are not universal requirements.

Distinguish local, hosted, provider, manual and production observations. Report what each result covers, relevant revision/configuration/prerequisites, and what was not performed. Refresh affected evidence after meaningful changes; unrelated changes do not invalidate everything. Infrastructure failures are diagnoses, not invitations to rerun until green.

A purported probe is a mutation if it creates jobs, calls paid services, changes durable/runtime state or recreates services. Follow the project's actual authorization and environment safeguards; never use real data or production merely to close a checklist. For an authorized rollout, bounded corroboration must answer a go/no-go, rollback or completion question. Once criteria pass, preserve evidence, restore required operational state, release locks and finalize tracking as the runbook requires.
