# Wide Research Notes 01 — AI Review Market and GitHub Competitive Baseline

**Research date:** 14 August 2026

## Verified Findings

### AI-assisted delivery creates a review-verification problem

DORA characterises AI as an amplifier of existing engineering-system strengths and weaknesses. Its 2025 analysis reports that 30% of developers have little or no trust in AI-generated code and describes a **verification tax** in which time saved in code generation is reallocated to auditing, prompting and production integration. DORA also links higher AI adoption with increased throughput and increased delivery instability. The strategic implication is that AI-Code-Reviewer should sell verified, explainable and governable review workflows—not generic “AI productivity.” [1]

### GitHub’s enterprise-native offering establishes the minimum expected workflow

GitHub Copilot Code Review reviews pull requests, can suggest changes, supports automatic reviews and is available across GitHub.com, CLI, mobile and several IDEs. Its enterprise configuration includes administrator policy controls, usage-based AI-credit billing, effort-level choices, and GitHub Actions/self-hosted runners for full-repository context and agentic capabilities. GitHub states that its `Lite` review typically consumes an estimated US$0.05–US$1.00 in AI credits, while `Balanced` typically consumes US$0.25–US$5.00, excluding Actions minutes. These are GitHub estimates and may evolve. [2]

## Strategic Implications

| Decision | Implication for AI-Code-Reviewer |
|---|---|
| Buyer outcome | Lead with reduced verification burden, high-signal findings, review explainability, policy alignment and evidence—not autonomous replacement of reviewers. |
| Workflow parity | CI/PR-native review, configurable review depth, repository context, fix governance, budget controls and evidence trails are table stakes for larger accounts. |
| Differentiation | A local-first / customer-controlled deployment path, policy-driven review, privacy-minimised metadata and independent reviewer workflow can differentiate where GitHub-native tools are constrained by centralisation, spend controls or data-governance rules. |
| Pricing | Provide predictable organization-level plans and review-volume governance; do not force users to guess credit consumption on security-critical paths. |
| Product guardrail | Keep a human-in-the-loop decision model. AI suggestions require confidence/provenance and policy-based escalation; no blanket “auto-merge” positioning. |

## Sources

[1]: https://dora.dev/insights/balancing-ai-tensions/ "DORA — Balancing AI tensions: Moving from AI adoption to effective SDLC use"
[2]: https://docs.github.com/en/copilot/concepts/agents/code-review "GitHub Docs — About GitHub Copilot code review"

---
**Prepared by Manus AI**
