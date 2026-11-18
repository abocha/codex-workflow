# Choosing a model and reasoning effort

Continue with the user's selected model and effort through investigation, implementation and verification. Keep the work with the agent that traced the problem while its evidence still applies. An authorized handoff can pay off when another agent can make independent progress, bring a needed capability or meet an expressed cost or latency preference.

When the user asks for a model recommendation, GPT-6.2 Sol fits everyday coding and GPT-6.2 Astra fits demanding work such as diagnosing a failure across services. A deeper investigation can justify raising reasoning effort, and a quick scan can justify lowering it. Check the options exposed by the host. [Codex model guide](https://learn.chatgpt.com/docs/models)

The portable [role definitions](../../../.codex/agents/) omit model and effort overrides so children inherit both from the parent. Choose a role for its responsibility. A project can explicitly configure its own overrides. [Codex subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents)

For visual work, verify that the assigned agent can inspect the image or interact with the requested surface. See [visual dispatch](orchestration.md#visual-and-interactive-work) and the [activation guide](../../../templates/visual-specialist-activation.md).

Plan where the evidence is accessible. Use ChatGPT for discussion or approval when that helps the user, and local tools for repository checks. Use host-specific usage information for quota questions. Base workflow changes on naturally occurring work.
