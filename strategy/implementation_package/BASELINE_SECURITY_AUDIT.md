# AI-Code-Reviewer — Baseline Security, Licensing and Telemetry Audit

**Audit date:** 14 August 2026  
**Scope:** Static review of `app.py`, `core/ai_engine.py`, `core/github_client.py`, `core/license_manager.py`, `core/telemetry.py` and `ui/main_window.py`. This is a code-level architectural assessment; it is not a penetration test, security certification or legal-compliance opinion.

## Executive Assessment

The current desktop application has a **promising local-first review foundation**, but its handling of secrets, license entitlements and telemetry is prototype-grade. It must not be marketed as a secure enterprise desktop product until the P0 remediation items below are implemented and independently tested.

| Domain | Current implementation | Risk level | Required remediation |
|---|---|---:|---|
| GitHub token | Entered through password-masked UI and held in process memory; accepted through CLI `--token`; no persistent secure store | **High** | Use OS-backed credential storage for GUI; support environment/secure CI secret only for CLI; prohibit CLI arguments for long-lived tokens in production documentation |
| AI-provider key | Read from environment variable at process startup | **Medium** | Keep environment injection for CI, add OS-backed profile storage for desktop only, document provider data egress and secret rotation |
| Secret logging | No explicit logging of token found in reviewed flows, but no central redaction boundary exists | **High** | Centralise structured logging and enforce token/secret redaction; test logs and crash reports |
| License validation | Any string beginning `AI-ENT-` activates Enterprise features | **Critical** | Replace with asymmetric signed entitlement verification, expiry, device/tenant policy and revocation-ready validation |
| Telemetry | Enabled by default, writes arbitrary caller data to a hard-coded `/home/ubuntu/...` JSON file, has bare exception handling | **Critical** | Consent-driven, schema-validated, encrypted-at-rest local queue using a platform-specific data directory; no source/code/secret collection |
| Findings cache/history | SQLite stores hashes and metadata, avoids source-code persistence | **Low–Medium** | Preserve this principle; encrypt sensitive local fields where justified, set retention controls and use the appropriate Windows application-data path |
| GitHub API client | Uses a classic `Authorization: token` header | **Medium** | Prefer a least-privilege GitHub App or fine-grained PAT; limit scopes, use explicit timeouts, redact auth failures |
| Windows support | Paths contain Linux-specific `/home/ubuntu` reference and no Windows credential APIs | **High** | Use `platformdirs`, Windows Credential Manager / DPAPI-backed storage, OS access controls and Windows installer signing |

## Verified Implementation Facts

The current `LicenseManager` activates Enterprise status solely by testing whether the supplied value begins with `AI-ENT-`; it neither verifies a signature nor evaluates expiry, organisation, feature entitlement or revocation. The current telemetry component defaults to enabled and writes arbitrary `data` payloads to a local JSON file at a Linux-specific hard-coded path. The UI masks the GitHub Personal Access Token field, but its save flow builds a new in-memory GitHub client; there is no Keychain/Credential Manager integration. The command-line interface accepts a PAT through `--token`, which risks exposure through shell history, process listings and CI logs.

The analysis engine already makes a sound privacy-oriented decision: its findings-history store persists metadata and hashes, not source code or snippets. This property must be retained as the architecture moves to Windows and Enterprise deployments.

## P0 Remediation Sequence

| Order | Action | Owner | Acceptance evidence |
|---:|---|---|---|
| 1 | Immediately rotate the previously exposed GitHub PAT and replace it with a least-privilege fine-grained credential or GitHub App installation. | Repository owner | Old credential revoked; new credential scope review recorded |
| 2 | Remove hard-coded Linux telemetry path and default telemetry to disabled until informed consent is captured. | Desktop engineer | Automated test proves first run sends no event and creates no data file without consent |
| 3 | Implement a `SecretStore` interface with a Windows implementation backed by Credential Manager / DPAPI. | Desktop engineer | Integration test stores, reads, deletes and fails closed for an OS credential |
| 4 | Replace prefix-based licensing with signed entitlement verification. | Platform engineer | Tests reject altered, expired, wrong-product and wrong-tenant licenses |
| 5 | Introduce a fixed telemetry event schema and data-loss-prevention validation. | Privacy/security engineer | Tests reject source code, snippets, token-like values, repository URLs and arbitrary payload keys |
| 6 | Build central redacted logging and a secret-scanning release gate. | DevSecOps | CI scans source and release artefacts; redaction tests pass |

## Explicit Non-Claims

This audit does not establish that the application meets SOC 2, ISO 27001, GDPR, the EU AI Act or any customer-specific regulatory requirement. It identifies the security work necessary before beginning a controlled Enterprise design-partner pilot.

---
**Prepared by Manus AI**
