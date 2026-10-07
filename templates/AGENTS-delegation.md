## Portable Codex workflow

Use the lightest control loop that fits the current uncertainty and risk.

When installed, `.codex/WORKFLOW_MODES.md` owns workflow/model-selection guidance,
`.codex/ORCHESTRATION.md` owns Goal-execution delegation and review mechanics, and
`.codex/PROJECT.md` adapts those mechanics to this repository.

Do not duplicate those documents here.

### Workflow routing

- Keep bounded work atomic when one coherent result is enough.
- Keep evidence-dependent umbrellas exploratory while the next useful action still depends on what
  current investigation finds.
- Use coordinated Goal execution only after the desired outcome and acceptance boundary are stable
  enough to support dependent implementation.
- Goal-backed orchestration is explicit opt-in; task size, difficulty, duration, or delegation alone
  do not imply it.

Follow `.codex/WORKFLOW_MODES.md` for the current detailed mode and model routing.

### Primary ownership and delegation

The primary agent owns integration, validation decisions, and the final result. It remains
accountable for repository state and authorized mutations performed by workers.

Delegation is optional. Use it when a registered role materially improves execution, context
isolation, discovery, or independent review.

Delegate by coherent ownership boundary rather than mechanically by numbered plan item. Let a capable
child own its local inspect/edit/test loop. Do not shadow or repeat that work without a concrete
unresolved reason.

Reuse an existing context when it owns expensive relevant evidence and the next step is a direct
continuation. Use fresh context when a new ownership boundary, different capability, or meaningful
independence justifies the rediscovery cost.

Follow `.codex/ORCHESTRATION.md` for detailed role, context, review, and integration mechanics.

### Role integrity

When a specific registered project role is selected, use that actual role. Do not silently substitute
a generic/default child, another registered role, or a different model and then report it as the
requested route.

Role/model/sandbox configuration does not expand task scope, architectural authority, mutation
authorization, or repository policy.

Explicit current task instructions take precedence over optional skill guidance unless a controlling
repository contract requires otherwise. If a skill or workflow rule would pause or leave requested
work unfinished, identify the controlling requirement and explain why it applies.

### Complexity discipline

When structural-complexity judgment is genuinely non-trivial, use the installed
`$complexity-discipline` skill.

Typical triggers include new abstractions, dependencies, configuration surfaces, compatibility
mechanisms, generalized extension points, duplicated platform/repository capability, substantial
newly discovered work, or difficult-to-reverse future-constraint decisions.

Do not invoke it for straightforward pattern-following work whose design is already established.
The skill may conclude that the proposed complexity is justified; it is a decision procedure, not an
automatic simplifier.

### Evidence and review

Use evidence proportionate to the change and the repository's own validation policy. Delegation does
not by itself justify broader validation or additional review.

Review follows residual semantic risk rather than diff existence, file count, or ceremony. Obtain
independent review when remaining correctness or consequence warrants it; do not manufacture
independence merely because reviewer roles exist.

Repository-specific test commands, CI ownership, merge requirements, production checks, and
validation procedure belong in repository instructions or `.codex/PROJECT.md`, not this portable
fragment.

### Authorization

An authorized implementation outcome includes ordinary local repository operations reasonably needed
to complete it, within the assigned scope and any repository or task restrictions. Consequential
external or destructive mutations still require the authorization specified by repository and task
policy. Delegation and broad tool access do not expand that authority.
