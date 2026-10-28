# Activate the optional visual specialist

Use this route only when adopting or reconciling `visual_specialist`, or verifying its activation.
Ordinary frontend work does not need an activation exercise or a mandatory visual review.

## Source and release

The canonical [role](../.codex/agents/visual_specialist.toml) selects `gpt-6.1-terra` with medium
reasoning effort. [Model defaults](../skills/codex-workflow/references/models.md) and
[dispatch guidance](../skills/codex-workflow/references/orchestration.md#visual-and-interactive-work)
own task routing. OpenAI documents the model's image input and medium effort support in the
[model reference](https://developers.openai.com/api/docs/models/gpt-6.1-terra); account and host
availability still need verification.

Validate and build through the canonical repository's README recipe. The archive includes the role
and this guide. Update the existing private plugin identity through Plugin Creator only when
authorized, using its observed release as the conflict guard, then read back changed files. Preserve
scope, audience, existing components and plugin identity. A package version or source merge alone
does not establish a saved account release or host installation.

## Project registration and capabilities

Current [Codex custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
discovers standalone TOML files in project `.codex/agents/` or personal `~/.codex/agents/`.
Use project registration for project adoption; do not edit personal settings incidentally. Copy only
the selected role into the target project's `.codex/agents/visual_specialist.toml` after checking for
an existing adaptation. Preserve and reconcile an existing file rather than overwriting it.
The repository's optional `install-into-repo.ps1 -IncludeRoles` stages all missing roles and the
operating fragment; it is broader than adopting this one role. Plugin installation alone does not
prove that the host discovered packaged roles.

Start a fresh supported session in the target project if the running session's role inventory is
stale. Inspect the actual available role/model/tool surface before dispatch. The role inherits parent
permissions, provider and MCP servers; TOML cannot provision screenshot/browser tools or override
the parent's sandbox. Its assessment default is a behavioral boundary, not filesystem enforcement.
Configure a read-only parent session when enforced read-only filesystem access is required; connector
and browser permissions remain separate. Do not silently substitute another model or generic child.

## Focused runtime smoke check

When authorized and available, spawn the registered `visual_specialist` by role, with a narrow
assessment assignment and a genuine image/capture accessible to it. Use a local/disposable screen
or a non-sensitive screenshot with a visually observable result. Ask it to open the image or capture
the screen, report specific visual findings and identify unavailable capabilities. A file path,
alt text, DOM dump or source listing by itself does not establish visual input.

Record the actual role, model/effort metadata when exposed, image/capture tool result, and observable
findings. If interactive exploration is needed, also verify browser/computer-use tool availability
in that child and exercise only the authorized local/disposable flow. A static-image pass does not
prove interactive browser operation. Never use an authenticated submit/publish/delete control just
to complete a smoke check. Do not distribute raw captures, logs or private account/session metadata.

Report separately: source commit and changed paths; config/link/package checks; PR/CI state; saved
plugin version/release; installed plugin/skill discovery; target-project role registration; static
visual execution; and interactive capability if required. Leave any missing item as a named
activation gate. Full operational availability requires the release, installation/registration and
the visual/tool evidence required by the selected workflow.
