# Wide Research Notes 03 — Regulatory and Secure-Development Baseline

**Research date:** 14 August 2026

## Verified Findings

### European Union AI Act

The European Commission states that the EU AI Act entered into force on 1 August 2024 and became broadly applicable on 2 August 2026, subject to exceptions. The Commission identifies 2 February 2025 for prohibited-practice and AI-literacy obligations, 2 August 2025 for governance rules and obligations concerning general-purpose AI models, 2 December 2027 for high-risk use cases in specified sensitive areas, and 2 August 2028 for high-risk systems embedded in certain regulated products. [1]

AI-Code-Reviewer is not automatically a high-risk system merely because it reviews software. Classification depends on the specific intended purpose, deployment and applicable law. However, selling into Europe warrants a documented AI-governance baseline: clear capability limits, human-review expectations, model/vendor inventory, data processing disclosures, customer-controlled configuration, incident/support procedures, and staff AI-literacy material.

### NIST secure-development guidance for generative AI

NIST SP 800-218A is a Secure Software Development Framework (SSDF) community profile that augments SSDF 1.1 with AI-model-development-specific practices, tasks and recommendations. NIST states that the profile is intended for producers of models, producers of AI systems using those models, and acquirers of such systems. [2]

For AI-Code-Reviewer, the practical product implication is to manage AI review as a secure software system: secure model/provider configuration, provenance of generated findings, change management for prompts/rules/models, logged approval boundaries, vulnerability disclosure, and evidence that the product’s own development lifecycle is governed.

## Strategic Implications

| Area | Minimum position before enterprise claims | Product / operating action |
|---|---|---|
| AI governance | Do not imply legal compliance by default; document intended purpose, limitations and human oversight. | Publish an AI System Card and customer-facing Responsible AI / Human Review policy. |
| Data governance | Define what code, metadata, telemetry and credentials are collected, processed, retained, transmitted and deleted. | Implement data-classification controls, consented telemetry, configurable retention and deployment-specific data-flow diagrams. |
| Model governance | Acknowledge model/provider versions and behaviour can change. | Build a model registry, prompt/rule versioning, evaluation suites and rollback/change-control process. |
| Secure SDLC | Enterprise buyers will expect secure development evidence beyond scanner features. | Align engineering controls with SSDF; maintain SBOM, dependency/update policy, threat model and vulnerability disclosure process. |
| Europe expansion | The local-first position helps, but legal, privacy and AI governance must be operational rather than marketing statements. | Create a regional-readiness gate with DPA, subprocessors list, hosting/data-residency choices, security questionnaire and compliance mapping. |

## Sources

[1]: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai "European Commission — AI Act"
[2]: https://www.nist.gov/publications/secure-software-development-practices-generative-ai-and-dual-use-foundation-models-ssdf "NIST SP 800-218A — Secure Software Development Practices for Generative AI and Dual-Use Foundation Models"

---
**Prepared by Manus AI**
