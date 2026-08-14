# Research Notes — Windows Release Signing and License Signatures

**Research date:** 14 August 2026

## Verified Findings

Microsoft documents that a Win32 MSI/EXE installer submitted to the Microsoft Store must be Authenticode-signed with a certificate chaining to a CA in the Microsoft Trusted Root Program; self-signed certificates are not accepted. The Microsoft documentation identifies Azure Artifact Signing (formerly Trusted Signing) as the recommended option for non-Store distribution and distinguishes Store/MSIX signing, traditional organisation-validated certificate signing and test-only self-signed certificates. [1]

NIST FIPS 186-5 specifies RSA, ECDSA and EdDSA as digital-signature techniques for generating and verifying signatures used to protect data. NIST describes Edwards curves as providing increased performance, side-channel resistance and simpler implementation compared with traditional curves. [2]

## Architecture Consequences

| Security control | Design decision |
|---|---|
| EXE / installer publisher authenticity | Sign every Windows release artifact and installer in CI using a managed signing service or an HSM-protected organisation certificate. Do not place an exportable code-signing private key in the repository, runner filesystem or a local developer device. |
| Release integrity | Publish SHA-256 hashes and SBOM alongside the signed release asset; verify signature and hash in the release-quality gate. |
| Offline license authenticity | Sign each entitlement payload in a controlled licensing service with an asymmetric private key. Ship only the corresponding public verification key(s) in the desktop application. |
| Algorithm choice | Use a reviewed cryptography library and either Ed25519/EdDSA or ECDSA P-256 according to the organisation’s policy and customer requirements. Do not implement signature algorithms directly. |
| Key rotation | Include `key_id` in the signed entitlement and support a public-key ring in the client. Keep at least one previously valid public key during rotation. |
| Revocation | Offline entitlement validation cannot instantly enforce revocation. Provide signed revocation lists when online, a time-limited license with renewal, and a configurable grace period. |

## Explicit Security Boundary

A digitally signed license confirms integrity and origin. It does **not** prevent a user with administrator control of their own device from altering process memory, intercepting runtime calls or using a valid license beyond contractual authorisation. Commercial enforcement therefore requires defence-in-depth: server-side entitlement checks for cloud services, audit trails, contractual controls, and regular signed renewal for high-value Enterprise entitlements.

## Sources

[1]: https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options "Microsoft Learn — Code signing options for Windows app developers"
[2]: https://csrc.nist.gov/news/2023/nist-releases-fips-186-5-and-sp-800-186 "NIST — FIPS 186-5 Digital Signature Standard and SP 800-186"

---
**Prepared by Manus AI**
