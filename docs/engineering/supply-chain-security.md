# Supply Chain Security

## Document Control

| Field | Value |
|---|---|
| Document ID | SEC-SCS-001 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-12 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Dependency Scanning

### 1.1 npm Audit (Frontend)

- Runs automatically in CI via `.github/workflows/ci.yml`
- Scans `apps/web/package-lock.json` for known vulnerabilities
- Fails CI on high-severity findings
- Weekly Dependabot PRs for automated updates (see `.github/dependabot.yml`)

### 1.2 pip Audit (Backend)

- Runs `pip-audit` on `apps/api/requirements.txt` and `services/scheduler/requirements.txt`
- Integrated into CI pipeline (security job)
- Fails CI on critical/high findings

### 1.3 Trivy Vulnerability Scan

- Container-level scanning across all 3 Docker images
- Runs in CI security job after Docker build
- Fails on critical/high CVEs in base images and installed packages

## 2. Dependabot Configuration

- **npm**: Weekly checks, grouped PRs for React/Next.js/Supabase
- **pip**: Weekly checks for `apps/api/` and `services/scheduler/`
- **Docker**: Monthly checks for base image updates
- **GitHub Actions**: Monthly checks for action version bumps

## 3. SBOM Generation

- Software Bill of Materials generated on release
- Captures all direct and transitive dependencies
- Stored alongside release artifacts

## 4. License Compliance

| License | Allowed |
|---|---|
| MIT | Yes |
| Apache 2.0 | Yes |
| BSD | Yes |
| ISC | Yes |
| GPL v2/v3 | No |
| AGPL | No |
| Proprietary | Requires review |

All new dependencies must pass license check before inclusion.

## 5. Software Bill of Materials (SBOM)

### 5.1 What is an SBOM?

A Software Bill of Materials (SBOM) is a formal, machine-readable inventory of all components — including direct and transitive dependencies — used in a software project. SBOMs enable rapid vulnerability triage by correlating known CVEs against the exact dependency graph of each build. They also support compliance with Executive Order 14028 and NIST SP 800-218 (SSDF) requirements.

### 5.2 SBOM Format

This project uses the **CycloneDX** format (ISO/IEC 5962:2021), selected for its broad tool support and depth of metadata. CycloneDX is generated at release time for both frontend and backend components. The JSON representation includes component names, versions, purl (Package URLs), license identifiers, and dependency relationships.

### 5.3 Generation Commands

```bash
# Backend (Python) — generate CycloneDX SBOM via pip-audit
pip-audit --requirement apps/api/requirements.txt --requirement services/scheduler/requirements.txt --format cyclonedx-json > sbom/api-cyclonedx.json

# Backend — alternative using cyclonedx-bom tool
pip install cyclonedx-bom
cyclonedx-py --evaluate-pip-requires apps/api/requirements.txt -o sbom/api-cyclonedx.json

# Frontend (npm) — generate CycloneDX SBOM
cd apps/web
npx @cyclonedx/cyclonedx-npm --output-format json --output-file ../../sbom/web-cyclonedx.json

# Combined SBOM aggregator (run on release)
python scripts/generate-sbom.py
```

### 5.4 SBOM Storage

| Artifact | Location | Format | Generated |
|---|---|---|---|
| API SBOM | `sbom/api-cyclonedx.json` | CycloneDX JSON | Per release |
| Web SBOM | `sbom/web-cyclonedx.json` | CycloneDX JSON | Per release |
| Scheduler SBOM | `sbom/scheduler-cyclonedx.json` | CycloneDX JSON | Per release |
| Aggregated SBOM | `sbom/aggregated.json` | CycloneDX JSON | Per release |
| SPDX (optional) | `sbom/aggregated.spdx` | SPDX 2.3 | Per release |

SBOM files are committed to the repository under `sbom/` and published alongside GitHub release artifacts. Each release tag includes an SBOM attachment for auditability.

### 5.5 SBOM Validation

Every generated SBOM is validated against the CycloneDX JSON schema before acceptance:

```bash
# Validate SBOM against CycloneDX schema
npx @cyclonedx/cyclonedx-cli validate --input-file sbom/api-cyclonedx.json --fail-on-errors
```

## 6. Dependency Update Cadence

### 6.1 Update Frequencies per Ecosystem

| Ecosystem | Check Frequency | Update Window | Critical Fix SLA |
|---|---|---|---|
| npm (Frontend) | Weekly (Monday) | Within 7 days | 24 hours |
| pip (Backend) | Weekly (Monday) | Within 14 days | 48 hours |
| pip (Scheduler) | Weekly (Monday) | Within 14 days | 48 hours |
| Docker base images | Monthly | Within 30 days | 7 days |
| GitHub Actions | Monthly | Within 30 days | 7 days |

### 6.2 Update Workflow

1. **Detection**: Dependabot opens a PR with the version bump and changelog link
2. **Review**: Developer reviews changelog for breaking changes
3. **CI Validation**: All CI jobs must pass (lint > test > build > security scan)
4. **Merge**: Approved PR is merged; auto-deploy to production
5. **Verification**: Production health check confirms the dependency works in context

### 6.3 Breaking Change Handling

| Scenario | Action |
|---|---|
| Major version bump with breaking API | Create migration branch, update code, test thoroughly, merge alongside dependency |
| Major version bump with no breaking changes | Standard review and merge |
| Security fix for active CVE | Fast-track: expedited review, emergency merge |
| Deprecated dependency (end-of-life) | Create migration issue in backlog, schedule replacement within 30 days |

## 7. Vulnerability Response Playbook

### 7.1 Vulnerability Triage

When a CVE or security advisory is reported (via Dependabot, npm audit, pip-audit, Trivy, or manual disclosure):

| Step | Action | Owner | Time Target |
|---|---|---|---|
| 1 | **Triage**: Is the CVE exploitable in our context? Check attack surface, deployment topology, and data exposure | Developer | 1 hour (critical), 4 hours (high) |
| 2 | **Assess**: Which environments are affected? (dev, staging, production) | Developer | 30 minutes |
| 3 | **Scope**: Which dependencies are impacted? Trace transitive dependency tree | Developer | 1 hour |
| 4 | **Patch**: Update the dependency to the minimum fixed version | Developer | 2 hours |
| 5 | **Test**: Run full CI suite (lint, unit tests, integration tests, security scans) | CI | 30 minutes |
| 6 | **Verify**: Confirm the fix remediates the CVE via re-scan | CI | 10 minutes |
| 7 | **Deploy**: Emergency deploy to affected environments (production first if critical) | DevOps | 30 minutes |
| 8 | **Monitor**: Observe error rates, latency, and dependency health for 24 hours post-deploy | Developer | 24 hours |
| 9 | **Document**: Record incident in postmortem log, update security advisory register | Developer | After resolution |

### 7.2 Severity-Based Response Timeline

| Severity | Response SLA | Fix SLA | Deploy SLA |
|---|---|---|---|
| Critical (CVSS 9.0-10.0) | 1 hour | 4 hours | 6 hours |
| High (CVSS 7.0-8.9) | 4 hours | 24 hours | 48 hours |
| Medium (CVSS 4.0-6.9) | 24 hours | 7 days | Next sprint |
| Low (CVSS 0.1-3.9) | 7 days | 30 days | Next release |

### 7.3 False Positive Handling

If a vulnerability is flagged but is not exploitable in our deployment context:
1. Document the rationale explaining why it is not exploitable
2. Add the CVE identifier to `.trivyignore` or equivalent suppression file
3. Tag the advisory record as `false-positive` in the security register
4. Review quarterly and remove suppression if context changes

## 8. Tool Chain

### 8.1 Dependency Scanning Tools

| Tool | Scope | Trigger | Action on Finding |
|---|---|---|---|
| **Dependabot** | npm, pip, Docker, GitHub Actions | Weekly schedule + security advisories | Opens automated PR with version bump |
| **npm audit** | Frontend (`apps/web`) | Pre-merge CI (frontend job) | Fails CI on high-severity findings |
| **pip-audit** | Backend (`apps/api`, `services/scheduler`) | Pre-merge CI (security job) | Fails CI on critical/high findings |
| **Trivy** | All 3 Docker images | CI (security job, post-Docker build) | Fails CI on critical/high CVEs in base images and packages |
| **trufflehog** | Entire repository (git history + files) | Pre-commit hook + CI (security job) | Blocks commit / fails CI on secret exposure |
| **OSSF Scorecard** | GitHub repository | CI (security job, main branch only) | Reports supply chain health score (target: >= 8.0) |

### 8.2 Tool Configuration Locations

| Tool | Configuration File | Purpose |
|---|---|---|
| Dependabot | `.github/dependabot.yml` | Update schedule, grouped PRs, ecosystem config |
| npm audit | `apps/web/.npmrc` (if needed) | Audit level and registry settings |
| Trivy | `.trivyignore` | Vulnerability suppression with rationale |
| trufflehog | `.pre-commit-config.yaml` | Pre-commit hook integration |
| OSSF Scorecard | `.github/workflows/scorecard.yml` | Scorecard workflow definition |

### 8.3 Tool Version Pinning

All scanning tools are version-pinned in CI workflows to ensure reproducible results. For example, Trivy is pinned to a specific release version in the CI workflow to prevent unexpected breaking changes from new scanner releases.

## 9. License Compliance

### 9.1 License Policy

All third-party dependencies must carry an OSI-approved license compatible with this project's MIT license:

| License | SPDX Identifier | Allowed | Notes |
|---|---|---|---|
| MIT | MIT | Yes | Preferred license |
| Apache 2.0 | Apache-2.0 | Yes | Compatible with MIT |
| BSD 2-Clause | BSD-2-Clause | Yes | Compatible |
| BSD 3-Clause | BSD-3-Clause | Yes | Compatible |
| ISC | ISC | Yes | Compatible |
| Unlicense | Unlicense | Yes | Public domain equivalent |
| CC0 1.0 | CC0-1.0 | Yes | Public domain dedication |
| MPL 2.0 | MPL-2.0 | Yes | Weak copyleft; review required for derivative use |
| GPL v2 | GPL-2.0-only | No | Incompatible with MIT |
| GPL v3 | GPL-3.0-only | No | Incompatible with MIT |
| AGPL v3 | AGPL-3.0-only | No | Incompatible with MIT |
| LGPL | LGPL-3.0-only | Review required | Weak copyleft; case-by-case |
| Proprietary | N/A | Review required | Requires legal approval |

### 9.2 Compliance Enforcement

- **CI gate**: `license-checker` or `pip-licenses` runs in the security CI job to flag prohibited licenses
- **Pre-merge review**: Every Dependabot PR is checked for license changes
- **Quarterly audit**: Full license inventory reviewed against policy
- **Waiver process**: Prohibited licenses require documented waiver from developer

### 9.3 License Check Commands

```bash
# Node.js — check licenses for all frontend dependencies
cd apps/web
npx license-checker --failOn "GPL*;AGPL*" --production --json > license-report-web.json

# Python — check licenses for all backend dependencies
pip-licenses --format json --from apps/api/requirements.txt services/scheduler/requirements.txt --fail-on "GPL License;AGPL License" > license-report-api.json
```

---

## Related Documents

| Document | Purpose |
|---|---|
| [Secrets Management](secrets-management.md) | Environment variable and API key management |
| [SDL](../security/sdl.md) | Secure Development Lifecycle â€” Phase 4 (Implementation) covers dependency security |
| [Security Architecture](../security/24_Security.md) | Enterprise security architecture â€” Section 10 (Supply Chain) |
| [FastAPI Hardening](../security/hardening/fastapi.md) | Backend dependency auditing and scanning |
| [Next.js Hardening](../security/hardening/nextjs.md) | Frontend npm audit and bundle analysis |
| [CI/CD Pipeline](../../.github/workflows/ci.yml) | Security job with Trivy, npm audit, pip-audit |
| [Dependabot Config](../../.github/dependabot.yml) | Automated dependency update configuration |
| [AGENTS.md](../../AGENTS.md) | Master project reference â€” Section 27 (Dependency Management) |

