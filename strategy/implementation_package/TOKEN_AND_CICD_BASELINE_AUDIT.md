# Baseline Audit — Exposed Token and CI/CD

**Audit date:** 14 August 2026  
**Scope:** Repository configuration, `.github/workflows/build.yml`, `requirements.txt`, and the previously exposed classic GitHub PAT. This is a configuration review, not proof that the token was or was not abused.

## Immediate Risk Assessment

The GitHub personal access token was pasted in the conversation and was later used for publishing repository changes. It must be treated as compromised, even if no suspicious activity is visible. Revocation and rotation are the correct immediate response because a leaked long-lived credential cannot be made safe by simply removing it from a repository or chat history.

The current release workflow has repository-wide `contents: write`, is triggered by any `v*` tag push, uses mutable action tags (`actions/checkout@v4`, `actions/setup-python@v5`, `softprops/action-gh-release@v2`), installs dependency ranges (`>=`) without hashes or a lockfile, builds an unsigned EXE, and publishes it in the same job. These properties create avoidable supply-chain and release-integrity risk.

| Area | Verified current state | Risk | Required P0 change |
|---|---|---:|---|
| User credential | A classic PAT was exposed outside the intended secret boundary | Critical | Revoke now; replace with GitHub App or fine-grained, short-lived least-privilege credential |
| Release permissions | Workflow declares `contents: write` globally | High | Use job-level least privilege; release job only receives `contents: write` after protected approval |
| Action integrity | Workflow uses floating major tags | High | Pin third-party actions to immutable full commit SHA and monitor updates |
| Dependency integrity | `requirements.txt` uses only lower-bound ranges | High | Compile hashes/lockfile and install with `--require-hashes`; review dependency updates |
| Release integrity | EXE built with PyInstaller but no Authenticode signing, SBOM, provenance or hash asset | High | Sign, verify, publish SHA-256/SBOM and require release approval |
| Trigger governance | Any matching tag may publish a release | Medium–High | Use protected release environment, signed/restricted tags and separate build from publish |
| Secret handling | A release token is injected as `GITHUB_TOKEN`; no explicit secret scan/redaction gate is visible | Medium | Add secret scan, log controls, branch protection and fork/PR restrictions |

## Non-Negotiable First Actions

1. Revoke the exposed PAT in GitHub and invalidate it in every local/CI credential store; do not wait for a repository sweep.
2. Generate a credential inventory: local `gh` authentication, Windows Credential Manager, repository/organisation secrets, environment variables, CI logs and service accounts.
3. Replace human PAT publishing with either GitHub's scoped workflow token under a protected environment or a GitHub App installation token minted at runtime.
4. Disable automated public release publishing until the hardened workflow has passed review and produces a signed, verifiable test artifact.
5. Search source history, release assets and logs for the token fingerprint without reproducing the secret value in reports or issues.

---
**Prepared by Manus AI**
