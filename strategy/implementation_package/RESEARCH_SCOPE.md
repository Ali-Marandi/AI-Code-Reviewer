# Research Scope — Windows Security and Enterprise Licensing

**Confirmed research tracks:**

| Track | Precise question | Target source type |
|---|---|---|
| Windows credential storage | Which Windows-native APIs protect application secrets at rest and bind decryption to a user or machine? | Microsoft Learn / Windows API documentation |
| DPAPI and Credential Manager | What is the correct separation between DPAPI-protected blobs, Credential Manager entries and application metadata? | Microsoft Learn / Windows API documentation |
| Desktop secret-storage implementation | How should a cross-platform Python desktop application call the Windows store and safely fall back on macOS/Linux? | Official library/documentation plus platform guidance |
| Code-signing and installer trust | What controls establish Windows executable provenance and reduce SmartScreen / tampering risk? | Microsoft Learn and Authenticode documentation |
| License-entitlement security | How should offline-verifiable, signed licenses enforce product, term and feature rights without embedding a private signing key in the desktop client? | Cryptographic standards / vendor-neutral security guidance |
| Enterprise packaging and pricing | Which unit, included usage, overage and deployment gates create predictable pricing while preserving gross-margin control? | Current official competitor plan documentation and pricing pages |
| Pilot operating model | Which pilot roles, baselines, success metrics and decision gates are needed to validate paid Enterprise demand in 30 days? | Product-management synthesis, grounded in the verified product baseline |

**Execution rule:** Findings from each track will be independently sourced, time-stamped, consolidated into the implementation package and clearly labelled as either verified fact or product recommendation.

---
**Prepared by Manus AI**
