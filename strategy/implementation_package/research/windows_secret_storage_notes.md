# Research Notes — Windows Secret Storage

**Research date:** 14 August 2026

## Verified Findings

Microsoft documents that DPAPI `CryptProtectData` encrypts a data blob such that, typically, only the Windows user with the same logon credential can decrypt it, and usually only on the same computer. DPAPI also adds a message authentication code to guard against data tampering. The `CRYPTPROTECT_LOCAL_MACHINE` option broadens access to any user on the same computer and is therefore inappropriate for a per-user desktop GitHub token. [1]

Microsoft documents that Credential Locker APIs are available to WinUI and other desktop apps through WinRT. It recommends using the store only for credentials rather than larger data blobs, saving a credential only after successful sign-in and explicit user consent, and never storing credentials in plaintext application data or roaming settings. Microsoft also notes an application limit of 20 credentials in Credential Locker. [2]

## Architecture Consequences

| Secret category | Recommended Windows mechanism | Why |
|---|---|---|
| GitHub App user token / OAuth refresh token | Credential Manager or Credential Locker, associated with the current Windows user | Small credential, OS-managed access controls, explicit user opt-in |
| Third-party AI-provider key | Credential Manager or Credential Locker; avoid storing unless the user elects to retain it | Same properties; desktop product should prefer enterprise gateway/OIDC instead of individual provider keys |
| Locally encrypted non-secret settings | DPAPI CurrentUser with product-specific optional entropy | Binds decryption to current user and device while allowing settings to remain in application data |
| License entitlement token | Plaintext cache only if signed and non-secret; otherwise DPAPI CurrentUser | Integrity comes from signature; DPAPI protects local privacy and tamper surface |
| Telemetry queue | Standard per-user app-data directory, encrypted with DPAPI only if it contains sensitive business metadata; never place credentials or source code in the queue | Telemetry data must be schema-minimised rather than “secured later” |

## Decisions

1. The desktop product should use a `SecretStore` abstraction rather than write secrets to files, JSON, SQLite or Qt settings.
2. The Windows implementation should use a user-scoped OS credential store for small credentials and **must not** use `CRYPTPROTECT_LOCAL_MACHINE` for user tokens.
3. CLI/CI flows should accept short-lived environment-injected tokens or an external secret-manager integration; `--token` should be deprecated because command-line arguments can be visible in process listings and shell history.
4. Uninstall must offer a deliberate choice to remove local credentials. “Sign out” must delete the corresponding credential immediately.
5. The application must continue to work in a limited offline/deterministic review mode if a credential cannot be retrieved.

## Sources

[1]: https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata "Microsoft Learn — CryptProtectData function (dpapi.h)"
[2]: https://learn.microsoft.com/en-us/windows/apps/develop/security/credential-locker "Microsoft Learn — Credential locker for Windows apps"

---
**Prepared by Manus AI**
