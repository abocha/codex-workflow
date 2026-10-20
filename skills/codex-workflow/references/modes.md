# Workflow Modes

## Purpose

Choose the control loop before choosing agents.

Use the lightest mode that can produce the next useful evidence-backed result.

| Mode | Use when | Default control loop |
| --- | --- | --- |
| **Atomic task** | One bounded question, investigation, edit, or report can produce the useful result. | One coherent task -> one result. |
| **Exploratory campaign** | Several related questions share an umbrella, but each result determines what is worth investigating or changing next. | Maintainer + ChatGPT steer; Codex owns bounded probes or consequences. |
| **Goal execution** | The desired outcome and acceptance boundary are stable enough, and several dependent implementation boundaries need coordination. | Approved handoff -> primary orchestration -> coherent implementation/review boundaries -> integration. |

[Planning](planning.md) and [orchestration](orchestration.md) primarily govern Goal execution.

Do not manufacture a plan, durable goal, primary orchestrator, delegation, or review simply because the workflow supports them.

## Select from uncertainty, not task size

### Atomic task

Use Atomic task when the next useful result is already clear and bounded.

A small diff can require expensive reasoning, while a large mechanical change can be straightforward once uncertainty is removed. Route by discovery cost, semantic coupling, and consequence rather than expected file count or diff size.

Use [evidence selection](evidence.md#repository-evidence-and-operational-boundaries) for the actual risk rather than requiring strict TDD or a new test for every change.

### Exploratory campaign

Use Exploratory campaign when the umbrella is clear but a truthful implementation plan cannot yet be written because the next useful question depends on current evidence.

Typical examples include maintenance triage, repository archaeology, tooling simplification, migration feasibility, elusive bug investigation, or deciding whether suspicious architecture should change at all.

The result of an exploratory probe may be implementation, another investigation, KEEP, or DEFER. Exploration is not required to produce a diff.

### Goal execution

Use Goal execution when the desired outcome and acceptance boundary are stable enough that dependent implementation can proceed without repeatedly reopening WHAT success means.

If WHAT success means or WHETHER to pursue it remains unresolved, stay exploratory.

Goal execution has two variants.

**Plan-backed execution** is the default when the implementation path is sufficiently known and an approved implementation plan is a useful scope and acceptance contract.

**Goal-backed orchestration** is optional and requires explicit approval. Use it when the outcome is stable and verifiable but the implementation strategy is expected to adapt materially from repository evidence, several dependent boundaries or root turns may be needed, durable outcome state is useful, and outcome completion is meaningfully different from exhausting the current task list.

The goal defines the stable completion boundary. Plans and task routing remain revisable strategy beneath it.

See [planning](planning.md) for the handoff contract and [orchestration](orchestration.md) for execution mechanics.

## 2. Change modes when the problem changes

Modes are not sticky.

Promote exploration to Goal execution when:

- a concrete desired outcome and acceptance boundary have emerged;
- dependent implementation boundaries now need coordination;
- integration or shared contracts have become the main execution risk; and
- preserving one approved completion contract is cheaper and safer than continued one-result-at-a-time steering.

Do not keep probing merely because exploration has momentum.

Conversely, when remaining work collapses into one bounded independent action, stop paying orchestration overhead and treat it atomically.

Goal-backed execution does not require perfect knowledge of every future implementation step. It does require stable WHAT and WHY.

## 3. Exploratory campaigns

The stable control plane for an exploratory campaign is normally the maintainer + ChatGPT conversation.

Use it to preserve:

- the umbrella question;
- important evidence already obtained;
- decisions and rejected alternatives;
- deferred items and reconsideration triggers;
- useful repository or branch state;
- which active contexts retain expensive relevant evidence;
- the next question worth spending effort on.

A bounded Codex investigation may own several successive evidence-dependent probes when keeping that local context is cheaper than repeated handoffs.

The maintainer remains part of the scheduler and controls material product, design, scope, and priority decisions.

### KEEP, CHANGE, and DEFER

An investigation succeeds when it reduces uncertainty.

Valid outcomes are:

- **KEEP:** current behavior or tooling remains the best fit;
- **CHANGE:** a bounded improvement is justified;
- **DEFER:** the direction may be valid, but present value, evidence, or risk does not justify implementation.

Preserve counterintuitive or expensive KEEP/DEFER rationale when it is likely to recur. Record concrete reconsideration triggers rather than archiving an entire investigation transcript.

### Stopping rule

Apply [evidence and closure](evidence.md). Stop when available evidence is sufficient for the current decision. Do not turn exploration into permanent repository archaeology.


## Moving premises and proportional review

Verify moving external premises from current authoritative sources before freezing them into a plan. Choose models and supported efforts from [model defaults](models.md) only when that choice matters. Review follows residual semantic risk; [orchestration](orchestration.md#8-review-routing) owns detailed routing. Use [context economics](context.md) when the cost of continuation versus rediscovery materially changes.
