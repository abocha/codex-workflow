# Orchestration baselines

Several real implementation runs were used to test whether multi-agent orchestration was actually buying anything over one strong thread.

The useful result was not "more agents are better." The useful result was a routing rule:

- delegate coherent ownership boundaries, not numbered plan steps;
- use a fresh child when independence or a distinct capability is valuable;
- keep integration and repository-level validation with one primary owner;
- review according to residual semantic risk, not automatically because a diff exists;
- treat KEEP and DEFER as valid outcomes when investigation does not justify churn.

The measurements also exposed a reporting trap: a long-lived root thread can be reused for later work, while cumulative token counters keep growing. Whole-thread totals can therefore attribute later release or follow-up work to an earlier implementation. The metrics tooling in this repository supports turn-scoped export so a measured run can be bounded to the task actually being evaluated.

A second lesson was that token totals alone are weak evidence. Cached input can dominate a run, and two tasks with similar totals can have very different defect value, human effort, or integration risk. The workflow therefore treats telemetry as one signal alongside findings, validation results, and the shape of the work.

These observations led to the current distinction between atomic work, exploratory campaigns, and Goal execution. Orchestration is a control-loop choice, not a default decoration.
