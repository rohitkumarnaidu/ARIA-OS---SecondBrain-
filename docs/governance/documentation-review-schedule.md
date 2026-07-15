# Documentation Review Schedule â€” Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-REV-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Internal â€” Operations |
| Owner | Principal Product Manager |
| Last Updated | 2026-07-10 |
| Next Review | 2026-10-10 |
| Review Cycle | Quarterly |
| Approving Authority | Product Lead |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Principal Product Manager | Initial quarterly review schedule with tiered frequencies |

---

## 1. Tiered Review Framework

Documents are classified into three tiers based on criticality:

| Tier | Label | Cadence | Example Docs | SLA for Review |
|---|---|---|---|---|
| **Tier 1** | Critical | Monthly | AGENTS.md, Runbooks, Security, Prompts | Complete within 7 days of reminder |
| **Tier 2** | Standard | Quarterly | Engineering, Product, AI, Design | Complete within 14 days of quarter end |
| **Tier 3** | Low-Priority | Bi-Annually | Legacy/archived docs, historical ADRs | Complete within 30 days of reminder |

---

## 2. Quarterly Calendar (2026-2027)

### 2.1 Q3 2026 (Jul-Sep)

| Month | Tier 1 (Monthly) | Tier 2 (Quarterly) | Tier 3 (Bi-Annual) |
|---|---|---|---|
| **July** | AGENTS.md, Runbooks, Security, Prompts (agents + system), Doc Index, Implementation Status, CI/CD docs, Incident Response | â€” | â€” |
| **August** | AGENTS.md, Runbooks, Security, Prompts, Sentry docs, Tracing docs, Alerting docs | â€” | â€” |
| **September** | AGENTS.md, Runbooks, Security, Prompts, Deployment docs, Release Management | **All Product docs** (30 files), **All Engineering docs** (78 files), **All AI docs** (27 files), **All Design docs** (42 files) | â€” |

### 2.2 Q4 2026 (Oct-Dec)

| Month | Tier 1 (Monthly) | Tier 2 (Quarterly) | Tier 3 (Bi-Annual) |
|---|---|---|---|
| **October** | AGENTS.md, Runbooks, Security, Prompts, Doc Index, Implementation Status | â€” | â€” |
| **November** | AGENTS.md, Runbooks, Security, Prompts, CI/CD, Incident Response | â€” | â€” |
| **December** | AGENTS.md, Runbooks, Security, Prompts, Deployment, Release Management | **All DevOps docs** (13 files), **All QA docs** (14 files), **All Operations docs** (47 files) | Legacy ADRs (pre-2026) |

### 2.3 Q1 2027 (Jan-Mar)

| Month | Tier 1 (Monthly) | Tier 2 (Quarterly) | Tier 3 (Bi-Annual) |
|---|---|---|---|
| **January** | AGENTS.md, Runbooks, Security, Prompts, Doc Index, Implementation Status | â€” | â€” |
| **February** | AGENTS.md, Runbooks, Security, Prompts, CI/CD, Incident Response | â€” | â€” |
| **March** | AGENTS.md, Runbooks, Security, Prompts, Deployment, Release Management | **All Security docs** (10 files), **All Frontend docs** (4 files) | Legacy wireframes, Workflow Architecture v1 docs |

### 2.4 Q2 2027 (Apr-Jun)

| Month | Tier 1 (Monthly) | Tier 2 (Quarterly) | Tier 3 (Bi-Annual) |
|---|---|---|---|
| **April** | AGENTS.md, Runbooks, Security, Prompts, Doc Index, Implementation Status | â€” | â€” |
| **May** | AGENTS.md, Runbooks, Security, Prompts, CI/CD, Incident Response | â€” | â€” |
| **June** | AGENTS.md, Runbooks, Security, Prompts, Deployment, Release Management | **All Product docs** (30 files), **All Engineering docs** (78 files), **All AI docs** (27 files), **All Design docs** (42 files) | Legacy operations docs (pre-Q3 2026) |

---

## 3. Review Template

### 3.1 Review Document Template

```markdown
# Documentation Review Report

**Document:** [Title]
**Document ID:** [ID]
**Reviewer:** [Name/Role]
**Review Date:** YYYY-MM-DD
**Review Type:** [Monthly / Quarterly / Bi-Annual]

## Checklist

- [ ] **Accuracy** â€” Content reflects current codebase/architecture state?
- [ ] **Completeness** â€” No missing sections or outdated references?
- [ ] **Document Control** â€” Version bumped, last updated date set?
- [ ] **Cross-References** â€” All links to other docs are valid?
- [ ] **Code Alignment** â€” Code examples match current implementation?
- [ ] **Naming Conventions** â€” Follows documentation standards?
- [ ] **Broken Links** â€” All internal and external links resolve?
- [ ] **Spelling & Grammar** â€” No typos?
- [ ] **Frontmatter** â€” (Prompts only) Passes `make validate-prompts`?
- [ ] **Deprecation** â€” Any content that should be marked legacy?
- [ ] **Related Docs** â€” Owners of cross-referenced docs notified?

## Findings

| # | Issue | Severity | Action Required | Owner | Target Date |
|---|---|---|---|---|---|
| 1 | ... | High/Med/Low | ... | ... | ... |

## Changes Made

- [ ] Version updated: [old] â†’ [new]
- [ ] Last updated date set
- [ ] PR submitted: #[number]
- [ ] Related doc owners notified

## Notes

[Additional observations, recommendations, or concerns]
```

### 3.2 Severity Definitions

| Severity | Definition | Response Time |
|---|---|---|
| **High** | Factual error, security concern, broken critical path | Fix within 24 hours |
| **Medium** | Outdated content, minor inaccuracy | Fix within current review cycle |
| **Low** | Typo, formatting, minor wording improvement | Fix before next review cycle |

---

## 4. Critical Documents â€” Monthly Review

These documents are reviewed **every month** without exception:

| Document | Primary Owner | Risk of Staleness | Sign-off Required |
|---|---|---|---|
| `AGENTS.md` | Principal Product Manager | AI agents change frequently; new modules added | Product Lead |
| `docs/operations/39_Runbooks.md` | Site Reliability Engineer | Deployments and infrastructure change | Staff DevOps Engineer |
| `docs/security/24_Security.md` | Staff Security Engineer | Vulnerability landscape evolves | Staff Security Engineer |
| `docs/security/25_Compliance.md` | Staff Security Engineer | Compliance requirements change | Principal Product Manager |
| `docs/security/soc2_control_matrix.md` | Staff Security Engineer | Controls need continuous validation | Principal Product Manager |
| `docs/security/ThreatModel.md` | Staff Security Engineer | New features introduce new threats | Principal Software Architect |
| `docs/security/VulnerabilityInventory.md` | Staff Security Engineer | New CVEs and vulnerabilities discovered | Staff DevOps Engineer |
| `prompts/system/aria_system.md` | AI Systems Architect | Orchestrator prompt updated frequently | QA Director |
| `prompts/system/guardrails.md` | AI Systems Architect | Safety guidelines need constant review | Staff Security Engineer |
| `prompts/agents/*.md` (10 files) | AI Systems Architect | Agent prompts change with feature updates | QA Director |
| `docs/operations/30_Analytics.md` | Site Reliability Engineer | Event tracking changes | Principal Product Manager |
| `docs/operations/32_Monitoring.md` | Site Reliability Engineer | Monitoring rules and dashboards change | Staff DevOps Engineer |
| `docs/devops/CI.md`, `docs/devops/CD.md` | Staff DevOps Engineer | Pipeline changes frequently | Site Reliability Engineer |
| `docs/devops/26_Deployment.md` | Staff DevOps Engineer | Deployment process evolves | Site Reliability Engineer |
| `docs/devops/38_ReleaseManagement.md` | Staff DevOps Engineer | Release process changes | Principal Product Manager |
| `docs/operations/40_IncidentResponse.md` | Site Reliability Engineer | Incident procedures need to stay current | Staff Security Engineer |

---

## 5. Standard Documents â€” Quarterly Review

Reviewed at the end of every quarter (March, June, September, December):

**Q1 (March):** Security (10), Frontend (4)
**Q2 (June):** Product (30), Engineering (78), AI (27), Design (42)
**Q3 (September):** DevOps (13), QA (14), Operations (47)
**Q4 (December):** Product (30), Engineering (78), AI (27), Design (42)

**Owners must:**
1. Receive automated reminder 14 days before quarter end
2. Complete review within 14 days
3. Submit PR with changes
4. Update the `Last Reviewed` date in the document's control table
5. Bump version per semver rules
6. Notify owners of any cross-referenced docs that need updates

---

## 6. Low-Priority Documents â€” Bi-Annual Review

Reviewed every 6 months (June and December):

| Document Group | Reason for Low Priority | Review Window |
|---|---|---|
| Legacy ADRs (pre-2026) | Historical decisions; unlikely to change | June + December |
| Legacy wireframes | Superseded by living design system | June + December |
| Workflow Architecture v1 | Superseded by implementation | June + December |
| Old sprint plans / backlog archives | Historical reference only | June + December |
| Pre-v4 engineering docs | Replaced by architecture updates | June + December |

---

## 7. Automation

### 7.1 GitHub Issues Automation

Create recurring GitHub Issues using `.github/ISSUE_TEMPLATE/doc-review.md`:

```yaml
---
name: Documentation Review
about: Scheduled documentation review reminder
title: '[DOC REVIEW] <Tier> â€” <Month> <Year>'
labels: ['documentation', 'review']
assignees: '<owner-gh-handle>'
---

## Review Required

**Tier:** [Critical / Standard / Low-Priority]
**Due Date:** YYYY-MM-DD

### Documents to Review

[List of document paths]

### Instructions

1. Read each document
2. Complete the review checklist (see `documentation-review-schedule.md`)
3. Submit a PR with changes
4. Update the ownership matrix with new review dates
```

### 7.2 Calendar Integration

Create recurring calendar events for each review tier:

| Tier | Frequency | Calendar Rule | Notification |
|---|---|---|---|
| **Critical** | 1st of every month | `FREQ=MONTHLY;BYMONTHDAY=1` | GitHub Issue + Slack reminder |
| **Standard** | 15th of last month in quarter | `FREQ=MONTHLY;BYMONTH=3,6,9,12;BYMONTHDAY=15` | GitHub Issue + Email |
| **Low-Priority** | 1st of June + December | `FREQ=YEARLY;BYMONTH=6,12;BYMONTHDAY=1` | GitHub Issue |

### 7.3 CI Validation

The following automated checks run on every PR that touches documentation:

```yaml
# .github/workflows/doc-quality.yml (planned)
# - Check all internal links resolve
# - Validate all document IDs are unique
# - Ensure all docs have valid document control tables
# - Run prompt frontmatter validation on prompts/
# - Flag broken cross-references
```

---

## 8. Review Output

Each review cycle produces these artifacts:

| Artifact | Description | Location |
|---|---|---|
| **PR with changes** | Actual document updates | GitHub PR |
| **Review report** | Filled review template | Attached to PR as comment |
| **Updated ownership matrix** | `Last Reviewed` dates refreshed | `documentation-ownership.md` |
| **Version bumps** | Semver update in document control | In each reviewed doc |
| **Notification to related owners** | Cross-reference updates | GitHub @mention or Slack |
| **Metrics update** | Review completion rate tracked | `docs/operations/KPIs.md` |

### 8.1 Review Completion Metrics

Track these KPIs for documentation health:

| Metric | Target | How to Measure |
|---|---|---|
| **On-time review rate** | >90% | GitHub Issues closed within due date |
| **Documents with stale review** | <5% at any time | Count of docs with `Last Reviewed` > 1 cycle past |
| **Average review turnaround** | <7 days for Tier 1, <14 days for Tier 2 | Time from issue creation to PR merge |
| **Broken link count** | 0 | Automated link checker in CI |

---

## 9. Quick Reference Card

```
MONTHLY (1st of month):
  AGENTS.md, Runbooks, Security, Prompts, CI/CD, Doc Index

QUARTERLY (End of Mar/Jun/Sep/Dec):
  Product, Engineering, AI, Design, DevOps, QA, Operations, Security

BI-ANNUALLY (Jun + Dec):
  Legacy docs
```
