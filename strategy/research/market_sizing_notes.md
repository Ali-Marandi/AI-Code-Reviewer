# Wide Research Notes 04 — Developer Ecosystem Scale and Demand Signals

**Research date:** 14 August 2026

## Verified Primary-Source Market Context

GitHub reports that developers created more than 230 repositories per minute, merged 43.2 million pull requests per month on average (up 23% year over year), and pushed nearly 1 billion commits during 2025 (up 25.1% year over year). It also reports more than 1.1 million public repositories using an LLM SDK, with 693,867 created in the preceding 12 months, a 178% year-over-year increase. GitHub’s data supports the direction of travel—more AI-assisted code and high pull-request volume—but it is not a measure of paid enterprise-market size. [1]

The Stack Overflow 2025 Developer Survey’s official AI section was reviewed as a secondary demand input. It exposes sections on AI-tool sentiment and usage, accuracy, complex-task capability, workflow satisfaction, frustrations and agent use; however, the site did not provide the underlying values in the accessible static page extract. The report should be revisited from its downloadable dataset before inserting survey percentages into external materials.

## Implications for AI-Code-Reviewer

| Market signal | Product implication |
|---|---|
| PR activity is extremely high and growing | Prioritise a scalable prioritisation/triage workflow—not an indiscriminate review-on-every-push default. |
| AI SDK adoption and code-generation usage are increasing | Focus on review of AI-assisted change: context-aware logic checks, hallucination-risk prompts, test sufficiency and governance. |
| Category trust remains unsettled | Use transparent severity, deterministic/AI origin labels, confidence signals and review rationale to turn scepticism into adoption. |
| Public developer population ≠ target buyer count | Size initial market bottom-up through organisations, teams, repositories and ACV; treat developer totals only as a directional top-of-funnel indicator. |

## Source

[1]: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ "GitHub Blog — Octoverse 2025: A new developer joins GitHub every second as AI leads TypeScript to #1"

---
**Prepared by Manus AI**
