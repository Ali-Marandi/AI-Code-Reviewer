# Phase 0 Action Checklist — Stabilise the Foundation (0–30 days)

**Owner:** Engineering Lead  
**Target completion:** 14 September 2026  
**Gate:** All P0 items must be complete before design-partner pilots begin.

---

## P0 — Security and Credential Hygiene

- [ ] Audit all source files for hardcoded tokens, passwords and API keys; rotate any that were committed.
- [ ] Replace all credential storage with OS keychain (`keyring` library on Windows/macOS/Linux).
- [ ] Add a pre-commit hook and CI step that runs `detect-secrets` or equivalent on every push.
- [ ] Verify that no token, secret or source-code snippet appears in log output, telemetry events or the SQLite cache.

## P0 — Licensing Implementation

- [ ] Replace the placeholder `LicenseManager` with a signed, offline-verifiable license token (e.g., JWT with RSA-256 signed by a private key held offline).
- [ ] Implement feature entitlement flags in the license token (Community / Team / Enterprise / Enterprise+).
- [ ] Add a license-expiry check with a 30-day grace period and a clear in-product renewal prompt.
- [ ] Document the license issuance and revocation process.

## P0 — Telemetry Consent and Governance

- [ ] Add a first-run consent dialog that clearly describes what is collected, where it goes and how to disable it.
- [ ] Default all non-essential telemetry to opt-out.
- [ ] Implement a local event buffer with configurable flush interval and a disable/export/delete control in Settings.
- [ ] Define and document the telemetry schema: no code, snippets, repository names, secrets or personal data unless explicitly authorised by the customer.

## P0 — Automated Quality Gates

- [ ] Add a `pytest` test suite covering the AI engine, rule-pack loader, SARIF builder and findings-history store.
- [ ] Add `ruff` or `flake8` and `mypy` to the CI pipeline.
- [ ] Generate an SBOM (`cyclonedx-py` or `syft`) on every release build.
- [ ] Configure `dependabot` or `renovate` for automated dependency updates.
- [ ] Produce a reproducible Windows EXE build via GitHub Actions with a signed artifact.

## P0 — AI System Card and Privacy Documentation

- [ ] Draft and publish an AI System Card in `docs/AI_SYSTEM_CARD.md` covering: intended purpose, capability limits, known failure modes, human-review expectations, model inventory and update policy.
- [ ] Publish a data-flow diagram in `docs/DATA_FLOW.md` covering all paths that process source code, findings, credentials and telemetry.
- [ ] Add a `SECURITY.md` with a vulnerability disclosure policy and contact address.

## P1 — Review Schema Improvement

- [ ] Add `origin` field to each finding: `deterministic_sast`, `custom_rule_pack` or `ai_review`.
- [ ] Add `confidence` field: `high`, `medium`, `low` or `informational`.
- [ ] Add `evidence_ref` field: line range, matched pattern or model context summary.
- [ ] Add `reviewer_status` field: `open`, `accepted`, `dismissed`, `suppressed`.
- [ ] Update SARIF export and PR comment format to reflect the new schema.

---

## Exit Criteria for Gate G1

All P0 items above are closed. A security review of the credential-handling and telemetry implementation has been completed by a second engineer. The Windows EXE build is reproducible and the artifact is signed. The AI System Card and data-flow documentation are published in the repository.

---
**Prepared by Manus AI**
