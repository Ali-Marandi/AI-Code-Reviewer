# Research Notes — Enterprise Pricing and Usage Governance

**Research date:** 14 August 2026

## Verified Competitor Reference Points

GitHub's official Copilot plans page lists Copilot Business at US$19 per granted seat per month and Copilot Enterprise at US$39 per granted seat per month. The product table includes Copilot code review and states that organisation/enterprise use may involve usage-based billing. [1]

CodeRabbit's official plan documentation lists Pro at US$24 per developer per month billed annually (US$30 monthly), Pro+ at US$48 annually (US$60 monthly), and a contact-sales Enterprise offering. Its Enterprise feature set includes self-hosting, multi-organisation support, SSO, SLA/customer-success support, marketplace billing, API access, custom RBAC and audit logs. It also implements per-developer rolling review limits and a usage-based add-on for eligible overage. [2]

## Pricing Design Consequences

| Observed market practice | Consequence for AI-Code-Reviewer |
|---|---|
| Enterprise purchasers accept per-seat pricing in the US$39–60/month range when it includes governance and organisational controls. | Price Team/Enterprise around seats for predictable procurement, but quote annual contracts and include a sensible review allowance. |
| AI review creates material variable costs and vendors meter/rate-limit usage. | Make included review capacity, risk-tier multipliers and overage price explicit; add hard budgets and approval controls before any extra usage. |
| Self-hosting, SSO, RBAC, audit logs, SLAs and multi-org management are gated as Enterprise. | Use these as Enterprise entitlement gates—not as unverified marketing claims. |
| Usage limits can be viewed negatively when hidden or triggered unexpectedly. | Offer visible organisation-level consumption dashboard, pre-run estimates and a “do not exceed budget” default. |

## Sources

[1]: https://docs.github.com/en/copilot/get-started/plans "GitHub Docs — Plans for GitHub Copilot"
[2]: https://docs.coderabbit.ai/management/plans "CodeRabbit Documentation — Plans and pricing"

---
**Prepared by Manus AI**
