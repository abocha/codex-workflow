---
name: complexity-discipline
description: Evaluate whether proposed implementation complexity is justified by current requirements, repository contracts, concrete risk, or evidenced future constraints. Use only when the structural-complexity judgment is non-trivial, such as when planning, implementing, or reviewing introduces a new abstraction, dependency, configuration surface, compatibility layer, generic extension point, duplicated platform capability, substantial newly discovered work, or a difficult-to-reverse future-constraint decision. Do not use for routine pattern-following work whose design is already established and unambiguous.
---

# Complexity Discipline

## Purpose

Treat complexity as a cost that needs a concrete reason, not as something to minimize mechanically.

Prefer the **simplest adequate design**: the smallest set of concepts and machinery that satisfies current requirements, repository architecture, concrete correctness/risk needs, and evidenced constraints. Do not optimize for the fewest lines or files.

This skill is a decision procedure. It may conclude that proposed complexity is justified as-is.

## Procedure

### 1. Comprehend the real flow first

Before simplifying or expanding anything:

- read the active repository instructions and relevant source-of-truth docs;
- trace the actual ownership/execution path far enough to know where the responsibility belongs;
- distinguish a root-cause change from a local symptom patch;
- identify existing repository conventions and reusable mechanisms.

Do not minimize a change in the wrong layer merely because that produces a smaller diff.

### 2. Name the proposed complexity

State what is being added or retained. Typical examples:

- abstraction/interface/helper layer;
- dependency;
- configuration or feature-flag surface;
- compatibility or migration mechanism;
- generic extension point;
- duplicated platform/stdlib/repository capability;
- background process/service;
- newly discovered implementation task outside the original decomposition.

If the complexity cannot be named clearly, gather more evidence before judging it.

### 3. Trace the necessity chain

The complexity should connect to at least one concrete reason:

- a current accepted outcome or requirement;
- a necessary enabler for that outcome;
- an existing repository/architecture contract;
- a concrete correctness, security, privacy, data-integrity, concurrency, failure-recovery, operational, or compatibility risk;
- a known external constraint;
- an evidenced future requirement whose retrofit cost or irreversibility makes accounting for it now materially safer or cheaper.

For Goal execution, newly discovered work should normally classify as one of:

- direct outcome work;
- necessary enabler;
- required risk/validation control;
- evidenced constraint.

If it fits none of these, treat it as optional or out of scope rather than silently expanding the goal.

### 4. Check cheaper correct alternatives

Compare the proposal against, in order where relevant:

1. an existing repository capability or pattern;
2. an already-installed dependency;
3. platform or standard-library functionality;
4. a small local implementation;
5. new generalized machinery or a new dependency.

Reuse only when the existing mechanism is semantically correct. Do not preserve a bad abstraction merely because it already exists.

### 5. Consider reversibility and retrofit cost

Do not apply YAGNI mechanically.

Ask:

- Is this cheap and safe to add/change later?
- Would deferring it create a difficult migration, incompatible public contract, data rewrite, security boundary change, or other expensive retrofit?
- Is the future pressure concrete and evidenced, or merely hypothetical?

Prefer deferral when later change is cheap and the requirement is speculative.

Deliberate now when a known constraint materially affects a difficult-to-reverse decision. Often the right answer is to preserve a seam or invariant without implementing the entire future system.

### 6. Choose the simplest adequate design

Prefer fewer unnecessary concepts, ownership surfaces, dependencies, and configuration mechanisms while preserving:

- repository ownership boundaries;
- clarity and idiomatic code;
- required validation;
- security and correctness invariants;
- data-loss protection;
- accessibility and explicit product requirements;
- maintainability of the actual expected change path.

Do not use file count, line count, or "one implementation" alone as proof that an abstraction is wrong.

### 7. Record a ceiling and upgrade trigger only when useful

When deliberately choosing a limited solution whose tradeoff is non-obvious, capture:

- the current ceiling/limitation;
- the concrete condition that should trigger reconsideration.

Example shape:

> Use one global lock for the current single-worker throughput. Reconsider per-account locking when concurrent account jobs become a measured bottleneck.

Do not create a special debt ledger or comment taxonomy solely for this skill. Put the rationale where future maintainers are most likely to need it: plan, issue, design note, or focused code comment.

## Output

Keep the result proportional to the decision. For a non-trivial case, report:

- **Conclusion:** justified as proposed | simplify | reuse existing mechanism | postpone | needs architectural deliberation | insufficient evidence
- **Necessity chain:** what concrete requirement/risk/constraint justifies the work
- **Alternatives checked:** cheaper correct options considered
- **Reversibility:** why now vs later is cheaper/safer
- **Ceiling / reconsideration trigger:** only if materially useful

## Boundaries

- Invoking this skill does **not** expand the current task, role, mutation authorization, or architectural authority. If the required judgment crosses an existing stop/escalation boundary, return `needs architectural deliberation` (or the repository's equivalent escalation outcome) and stop/escalate rather than making the higher-authority decision locally.
- Do not turn YAGNI into a veto against known future constraints.
- Do not prefer one line over clear code, or fewer files over correct ownership boundaries.
- Do not require an abstraction merely because "enterprise systems" commonly have one.
- Do not refactor unrelated code solely to make the current implementation look cleaner.
- Do not weaken tests, validation, security, data integrity, failure handling, or approved requirements in the name of simplicity.
- Do not invoke this skill for routine pattern-following work whose design is already established and unambiguous.
