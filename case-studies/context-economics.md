# Context economics

Context reuse has two competing values.

A hot thread can be extremely efficient when it already owns expensive repository evidence and the next task is a direct bounded consequence. Re-discovering the same architecture, failure mode, or decision history in a fresh session can cost more than carrying the useful context forward.

The opposite failure also appeared in long investigations: once the active context contains large amounts of historical tool output, every subsequent tool cycle can pay for information that is no longer decision-relevant. At that point a fresh context or compaction can be cheaper and clearer, especially at a phase boundary such as moving from planning/rehearsal into live operations.

The workflow therefore avoids a universal "always continue" or "always start fresh" rule. Before reusing a context, ask:

1. Does the current thread own evidence that would be expensive to reconstruct?
2. Is the next action a direct consequence of that evidence?
3. Has the task entered a materially different phase?
4. Is historical output now larger than the working set needed for the next decision?

Continuation prompts should be deltas, not restated specifications. Fresh contexts should be chosen for independence, phase change, or working-set reduction, not merely out of habit.

No raw session telemetry is published with this case study.
