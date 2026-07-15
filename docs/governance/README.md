## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-IDX-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Governance Directory â€” Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Directory | `docs/governance/` |
| Purpose | Documentation governance â€” standards, ownership, review processes, and change management |
| Status | Active |
| Last Updated | 2026-07-11 |
| Classification | Internal |
| Owner | Developer |

---

## Purpose

The governance directory centralizes all documentation-related process and policy documents. Separating these from operational runbooks (which live in `docs/operations/`) ensures that process definitions are versioned, reviewable, and independently maintainable from day-to-day operations content.

These documents define:
- **What standards** every document must follow (file naming, structure, markdown conventions)
- **Who owns** each document and how ownership transfers work
- **When and how** documents are reviewed, updated, and deprecated
- **How changes** to the system are managed, classified, and released

---

## File Index

| File | Document ID | Description | Owner |
|---|---|---|---|
| `01_DocumentationStandards.md` | GOV-STD-001 | Single authoritative standard for all markdown documents: naming, structure, templates, cross-references, quality process | Developer |
| `02_ChangeManagement.md` | GOV-CM-001 | Change classification, risk assessment, PR workflow, release management, rollback procedures, dependency management | Developer |
| `documentation-maturity-model.md` | GOV-MM-001 | 5-level documentation maturity framework: assessment dimensions, scoring rubric, target levels by category, review frequencies, promotion paths | Developer |
| `documentation-ownership.md` | (inherited) | Primary + backup ownership model for all ~270 docs across 8 categories. Escalation paths and emergency update procedures | Principal Product Manager |
| `documentation-review-schedule.md` | (inherited) | Tiered review framework (monthly/quarterly/bi-annual), calendar by quarter through Q2 2027, review templates, automation setup | Principal Product Manager |
| `README.md` | â€” | This file â€” governance directory index | Developer |

### Templates

Reusable doc templates are available in the [templates/](templates/) directory:

| Template | File | Best For |
|---|---|---|
| Architecture Template | [template-architecture.md](templates/template-architecture.md) | ADRs, system architecture, component design docs |
| API Endpoint Template | [template-api-endpoint.md](templates/template-api-endpoint.md) | REST API references, endpoint documentation |
| Guide Template | [template-guide.md](templates/template-guide.md) | How-to guides, procedures, configuration walkthroughs |

---

## Related Documents

| Category | Location | Purpose |
|---|---|---|
| Operations | `docs/operations/` | Runbooks, monitoring, incident response, DR, analytics, SLA |
| DevOps | `docs/devops/` | CI/CD, deployment, infrastructure, backup verification |
| Engineering | `docs/engineering/` | Architecture, API, database schemas, ADRs |
| Root | `AGENTS.md` | Master AI agent reference (v6) â€” includes Golden Rules, coding conventions, and cross-references to governance docs |

---

## For Authors

Use the following templates as starting points when creating new documentation:

- **Architecture/ADR**: [template-architecture.md](templates/template-architecture.md) â€” includes design goals, component descriptions, data flow, security considerations, alternatives considered
- **API Reference**: [template-api-endpoint.md](templates/template-api-endpoint.md) â€” covers all CRUD endpoints, error codes, rate limiting, request/response examples
- **Guides/Procedures**: [template-guide.md](templates/template-guide.md) â€” step-by-step instructions with prerequisites, common issues, verification steps

**Before writing a new doc:**
1. Check the [Documentation Maturity Model](documentation-maturity-model.md) to understand the target level for your category
2. Choose the appropriate template from [templates/](templates/)
3. Follow the enterprise 20-section structure defined in [GOV-STD-001](01_DocumentationStandards.md)
4. Include a Document Control table with a unique Document ID
5. Add cross-references to related documents

---

## Governance Review Process

1. **Standard review**: Governance docs are reviewed quarterly by the Developer
2. **Triggered review**: Any change to documentation standards, naming conventions, or process workflows triggers an unscheduled review
3. **Change proposal**: Submit a PR with proposed changes to the relevant governance document
4. **Review criteria**:
   - Does the change improve consistency or reduce friction?
   - Does it conflict with any existing governance document?
   - Are cross-references in related docs updated?
   - Has the version field been bumped per semver?
5. **Approval**: Self-approved by Developer after PR review checklist completed
6. **Publication**: Merge to `main` â€” deployment is automatic (doc-only change)

---

## How to Propose Changes to Governance

1. **Minor fix** (typo, formatting): Direct commit to `main` with descriptive message
2. **Process change** (new review cadence, changed ownership model):
   - Create a GitHub Issue with `type: governance` label
   - Discuss approach (self-review)
   - Branch from `main`: `governance/{issue-number}-{description}`
   - Submit PR with before/after of process impact
   - Self-approve and merge
3. **Major restructure** (new governance category, cross-cutting change):
   - Create GitHub Issue with `type: governance` + `risk: high`
   - Document the change in a brief design note
   - Branch, implement, submit PR
   - Run `make test` to validate no broken cross-references
   - Merge and notify relevant doc owners

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial governance directory index created as part of documentation restructure |
