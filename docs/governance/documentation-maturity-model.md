# Documentation Maturity Model — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-MM-001 |
| Version | 1.0.0 |
| Status | Approved |
| Last Updated | 2026-07-11 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. The 5-Level Maturity Model](#2-the-5-level-maturity-model)
- [3. Assessment Dimensions](#3-assessment-dimensions)
- [4. Assessment Procedure](#4-assessment-procedure)
- [5. Scoring Rubric](#5-scoring-rubric)
- [6. Target Levels by Document Category](#6-target-levels-by-document-category)
- [7. Review Frequency by Level](#7-review-frequency-by-level)
- [8. Maturity Promotion Path](#8-maturity-promotion-path)
- [9. Tools and Automation](#9-tools-and-automation)
- [10. Edge Cases](#10-edge-cases)
- [11. Failure Scenarios](#11-failure-scenarios)
- [12. Risks and Mitigations](#12-risks-and-mitigations)
- [13. Acceptance Criteria](#13-acceptance-criteria)
- [14. References](#14-references)
- [Revision History](#revision-history)

---

## 1. Introduction

### 1.1 Why Maturity Matters

Documentation in a monorepo of this scale (~330 files, ~16 MB, 13 categories) drifts without systematic quality management. The documentation maturity model provides an objective, repeatable framework to assess every document's quality, track improvement over time, and define clear targets per category.

### 1.2 What It Measures

The model evaluates documentation along 10 orthogonal dimensions (completeness, accuracy, structure, navigability, etc.) and maps the average score to one of 6 levels (L0–L5). Each level has explicit criteria and required behaviors, making promotion unambiguous.

### 1.3 Scope

Applies to all `.md` files under `docs/` and any future documentation added to the repository. Auto-generated docs (CHANGELOG, API clients) and third-party vendored docs are exempt but encouraged to conform.

---

## 2. The 5-Level Maturity Model

| Level | Name | Description | Core Criteria | Target Documents |
|---|---|---|---|---|
| L0 | None | No documentation exists. Topic is entirely absent from the repository. | — | Never acceptable |
| L1 | Initial | A document exists on disk with a title and basic outline. Minimal structure, no Document Control. | Exists on disk, has a title, covers at least one heading beyond the title | All docs at minimum |
| L2 | Managed | Has Document Control table, covers the main topic with substance, follows naming convention. | DC table present, 500+ words, covers the main topic, numbered filename per convention | All active docs |
| L3 | Defined | Complete with cross-references, error handling, worked examples, and edge case coverage. All 20 mandatory sections present or explicitly N/A. | DC current and valid, cross-refs resolve, examples present, edge cases documented, 20-section structure | Engineering, AI, Security |
| L4 | Measured | Quality metrics tracked over time. Automated validation in CI. Reviewed on a fixed schedule with records kept. | Automated frontmatter and link validation, scheduled review recorded, metrics dashboard shows trend | Core docs (IR, DR, Security, API) |
| L5 | Optimized | Continuously improved through monthly reviews, automated updates tied to code changes, and acts as template for new docs. | Monthly reviews, automated content sync, linked to test suites, referenced as exemplar | Aspirational — no docs assigned yet |

### 2.1 Level Characteristics

| Attribute | L0 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|
| Exists on disk | No | Yes | Yes | Yes | Yes | Yes |
| Has title | — | Yes | Yes | Yes | Yes | Yes |
| DC table | — | No | Yes | Yes | Yes | Yes |
| 500+ words | — | No | Yes | Yes | Yes | Yes |
| Cross-references | — | No | Optional | Yes | Yes | Yes |
| Examples | — | No | No | Yes | Yes | Yes |
| Edge cases | — | No | No | Yes | Yes | Yes |
| Automated validation | — | No | No | No | Yes | Yes |
| Review schedule | — | Monthly | Quarterly | Semi-annual | Annual | On change only |
| Metrics tracked | — | No | No | No | Yes | Yes |

---

## 3. Assessment Dimensions

Each dimension is scored on a **1–10 scale** (1 = absent, 10 = exemplary). The average of all 10 scores determines the maturity level.

| # | Dimension | What It Measures | 1–3 (Poor) | 4–6 (Adequate) | 7–9 (Good) | 10 (Exemplary) |
|---|---|---|---|---|---|---|
| 1 | **Completeness** | Coverage of all expected topics for that document type | Most major sections missing | Core sections present, some gaps | All expected sections present | Every subsection thorough, no omissions |
| 2 | **Accuracy** | Content is current, correct, and matches the codebase | Outdated or incorrect statements | Mostly correct, minor outdated items | Current and correct | Verified against codebase, version-locked |
| 3 | **Structure** | Proper heading hierarchy, logical flow, table of contents | No headings or random order | Headings exist, flow is reasonable | Clear hierarchy, TOC, consistent depth | Exemplary information architecture |
| 4 | **Navigability** | Cross-references exist and resolve, links are valid | No cross-references or broken links | Some cross-refs, most work | All cross-refs resolve, internal + external links valid | Smart cross-refs, backlinks, annotated |
| 5 | **Document Control** | Has DC table, version tracked, status current | No DC table | DC present but incomplete | DC complete, version follows semver | DC accurate, linked to ownership matrix |
| 6 | **Readability** | Language is clear, appropriate for audience, well-written | Confusing, jargon-heavy, typos | Clear with minor roughness | Well-written, professional tone | Exemplary technical writing |
| 7 | **Examples** | Includes concrete examples where applicable | No examples | One or two minimal examples | Multiple examples, varied scenarios | Examples runnable, cover edge cases |
| 8 | **Coverage** | Covers edge cases, error states, failure modes | No edge cases mentioned | Some obvious edge cases | Systematic edge case coverage | Exhaustive edge case + error state matrix |
| 9 | **Maintenance** | Review date set, planned updates, ownership assigned | No owner, no review date | Owner assigned, review cadence noted | Review history recorded, next review scheduled | Trending metrics, automated freshness checks |
| 10 | **Consistency** | Matches project templates, naming conventions, and patterns | Ad-hoc format, ignores standards | Partially follows conventions | Fully conforms to standards | Sets the standard for others |

---

## 4. Assessment Procedure

### 4.1 Standard Assessment Flow

```
Run validation checks  →  Score 10 dimensions  →  Calculate average
       ↓                        ↓                        ↓
Record in tracking       Assign maturity          File issues for
spreadsheet              level from average        gaps found
```

### 4.2 Step-by-Step

**Step 1: Automated validation checks**

```bash
# Link validation
lychee docs/path/to/document.md

# Frontmatter check (if applicable)
python scripts/validate_prompts.py  # for prompt-style docs

# Structure validation (CI script)
python scripts/validate-doc-structure.py --file docs/path/to/document.md
```

**Step 2: Score each dimension 1–10**

Use the rubric in Section 3. For each of the 10 dimensions, assign an integer score. Document brief rationale.

**Step 3: Calculate average and assign level**

| Average Score | Maturity Level |
|---|---|
| 0.0 – 0.9 | L0 — None |
| 1.0 – 2.9 | L1 — Initial |
| 3.0 – 5.9 | L2 — Managed |
| 6.0 – 7.9 | L3 — Defined |
| 8.0 – 9.4 | L4 — Measured |
| 9.5 – 10.0 | L5 — Optimized |

**Step 4: Record in tracking spreadsheet**

Log the following in the documentation maturity tracker (`docs/governance/maturity-tracker.csv`):

- Document ID, Title, File Path
- Assessment date, Assessor
- Scores per dimension (1–10)
- Average score, Maturity level
- Target level
- Issues found (links to GitHub issues)
- Next review date

**Step 5: Schedule next review**

See Section 7 for review frequency by level. Add calendar entry.

### 4.3 First-Time Assessment

For initial population of the tracker:

1. Run bulk link validation across all `docs/` files
2. For each file, fill Document Control if missing (infer from filename and location)
3. Score from available evidence — do not spend more than 5 minutes per doc on initial assessment
4. Flag exceptions (auto-generated, vendored, exempted files)
5. Prioritize security, engineering, and operations categories first

---

## 5. Scoring Rubric

### 5.1 Dimension Weighting

All dimensions are equally weighted (10% each). Use equal weighting for all standard assessments. Re-weighting may be applied for specialized audits (e.g., security audit weights Accuracy and Security higher).

### 5.2 Quick-Score Card

Use this card for rapid assessment:

| Dim | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **Unacceptable** | **Minimal** | **Incomplete** | **Developing** | **Adequate** | **Competent** | **Good** | **Very Good** | **Excellent** | **Exemplary** |

### 5.3 Fractional Scoring

Dimensions may be scored at .5 increments (e.g., 6.5) when the document falls between two descriptors. Round the final average to one decimal place.

---

## 6. Target Levels by Document Category

| Category | Minimum Level | Tier 1 Docs (Target L4) | Tier 2 Docs (Target L3) | Tier 3 Docs (Target L2) |
|---|---|---|---|---|
| **Security** | L3 | Incident Response, Disaster Recovery, Data Classification, Threat Model | Auth Architecture, Encryption, Compliance, Vulnerability Management | Security policies, audit evidence |
| **Engineering** | L3 | API Reference, System Architecture, Database Schema | ADRs, Module guides, Integration docs | Component READMEs, migration guides |
| **AI** | L3 | Agent Architecture, Memory Architecture | Prompt guides, Agent specs, Context assembly | Model cards, evaluation reports |
| **Operations** | L2 | Disaster Recovery, Monitoring/Runbooks | Incident response runbooks, Backup verification | SLA docs, analytics |
| **DevOps** | L2 | Deployment Guide, CI/CD Pipeline | Docker setup, Environment config | Infrastructure docs |
| **Design** | L2 | Design System, Design Tokens | UI/UX guidelines, Component library | Wireframes, motion specs |
| **Product** | L2 | PRD, SRS, Features | User stories, Personas, Roadmap | Vision docs, acceptance criteria |
| **Governance** | L3 | Documentation Standards, Maturity Model | Change management, Ownership matrix | Review schedules |
| **QA** | L2 | Testing Strategy, E2E Guide | Performance testing, Security testing | Test plans, load test scripts |

### 6.1 Target Escalation Policy

- Any doc below its category minimum triggers a **P3 documentation debt** issue
- L0 docs for any required topic trigger a **P2 documentation gap** issue
- L4–L5 docs are **frozen for content** — changes require ADR-level approval

---

## 7. Review Frequency by Level

| Current Level | Review Frequency | Maximum Age Without Review | Escalation if Missed |
|---|---|---|---|
| L0 | Immediate action required | 0 days | P2 issue — create document |
| L1 | Monthly | 45 days | P3 issue — promote to L2 or archive |
| L2 | Quarterly | 120 days | P4 issue — schedule review |
| L3 | Semi-annually | 210 days | P4 issue — schedule review |
| L4 | Annually | 400 days | P4 issue — schedule review |
| L5 | On change only | Unlimited | Documented exception |

### 7.1 Review Triggers

In addition to scheduled reviews, these events trigger an unscheduled review:

| Event | Trigger | Action |
|---|---|---|
| Code change in related module | PR merges with doc impact | Update doc, bump version |
| Incident or security finding | Postmortem identifies doc gap | Review and update relevant docs |
| Dependency update | Major version bump of documented dependency | Verify accuracy |
| Ownership change | Owner transfers | Transfer in ownership matrix |
| AI model update | LLM model change affects prompt docs | Verify prompt docs match new model |

---

## 8. Maturity Promotion Path

### 8.1 L1 → L2 (Initial → Managed)

Checklist:
- [ ] Add Document Control table with all required fields
- [ ] Expand content to 500+ words covering the main topic
- [ ] Ensure filename follows `{NN}_{TitleCase}.md` convention
- [ ] Add at least 3 headings beyond the title

### 8.2 L2 → L3 (Managed → Defined)

Checklist:
- [ ] Add cross-references to all related documents (verify they resolve)
- [ ] Include at least 2 worked examples or code snippets
- [ ] Document edge cases (minimum 3)
- [ ] Add error/failure scenarios section
- [ ] Ensure all 20 mandatory sections from GOV-STD-001 are present or explicitly N/A

### 8.3 L3 → L4 (Defined → Measured)

Checklist:
- [ ] Set up automated validation (frontmatter check, link check in CI)
- [ ] Record baseline metrics and establish trend
- [ ] Schedule recurring review in calendar
- [ ] Link document to relevant test suites or verification procedures
- [ ] Add quality metrics display (badge or dashboard entry)

### 8.4 L4 → L5 (Measured → Optimized)

Checklist:
- [ ] Implement automated content refresh tied to code changes
- [ ] Achieve 6+ consecutive months of metric stability
- [ ] Document is cited as exemplar in onboarding guide
- [ ] Monthly reviews are automated or near-zero effort
- [ ] Document drives improvements in other docs (used as template)

---

## 9. Tools and Automation

### 9.1 Current Tools

| Tool | Purpose | Applies To |
|---|---|---|
| `scripts/validate_prompts.py` | YAML frontmatter validation | Prompt files in `prompts/` |
| `lychee` (planned) | Link validation across all docs | All `.md` files |
| `markdownlint` (planned) | Markdown style and syntax | All `.md` files |
| `cspell` (planned) | Spelling with project dictionary | All `.md` files |

### 9.2 Maturity Automation Roadmap

| Phase | Tool | Function | Timeline |
|---|---|---|---|
| 1 | Custom CI script | Validate DC table presence and required fields | Q3 2026 |
| 2 | `lychee` integration | Weekly link validation in CI | Q3 2026 |
| 3 | Maturity tracker | Semi-automated scoring spreadsheet | Q4 2026 |
| 4 | Dashboard | RED metrics for documentation quality | Q1 2027 |
| 5 | Automated review reminders | Calendar + Slack reminders based on schedule | Q1 2027 |

### 9.3 Metric Dashboard (Future)

A documentation quality dashboard would track:

- Documents per maturity level (stacked bar chart)
- Average maturity by category (grouped bar chart)
- Docs below minimum target (red/yellow/green heatmap)
- Review compliance % (docs reviewed on time vs overdue)
- Trend over time (line chart, monthly snapshots)

---

## 10. Edge Cases

| Edge Case | Handling |
|---|---|
| Auto-generated documentation (CHANGELOG, OpenAPI spec) | Exempt from maturity scoring; may be assessed voluntarily |
| Deprecated documents | Score frozen at last assessment. Re-assess only if revived |
| Documents in `docs/archive/` | Not scored. Record only file path and archive date |
| Empty or stub documents | Score L1 automatically. Flag for promotion or deletion |
| Vendor documentation bundled in repo | Exempt. Identify in tracker with `vendor: true` |
| Document with no clear category | Assign to most relevant category. Note ambiguity in tracker |
| Document ID conflict | Index catches duplicate. Fix before assessment |
| Document with multiple owners | Assign primary owner. Note secondary in ownership matrix |

---

## 11. Failure Scenarios

| Scenario | Impact | Detection | Recovery |
|---|---|---|---|
| Maturity scores plateau at L2 | No improvement in quality | Quarterly trend review | Targeted promotion campaign for L2→L3 |
| Reviews consistently missed | Docs drift out of date | Automated calendar alerts | Reduce review frequency or reassign ownership |
| Automated validation too strict | Valid docs flagged as failing | Developer feedback | Tune thresholds, allow overrides with rationale |
| Tracker spreadsheet becomes stale | Metrics lose credibility | Audit of tracker vs filesystem | Automate bulk import of new files |
| Ownership unclear for assessment | No one accountable | Ownership matrix review | Reassign during quarterly review |

---

## 12. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Maturity process adds overhead without value | Medium | High | Keep initial assessments to 5 min/doc. Automate scoring as much as possible |
| Categories resist standardization | Low | Medium | Allow deviations with documented rationale in tracker |
| Automated tools not adopted | Medium | Low | Manual scoring is sufficient for L1–L3; automation is only required for L4+ |
| Document count grows faster than review capacity | High | Medium | Prioritize by target level. Use AI-assisted assessment for bulk scoring |
| L5 aspirational target discourages incremental improvement | Low | Medium | Celebrate L1→L2 promotions. Make L5 explicitly aspirational |

---

## 13. Acceptance Criteria

- [ ] Every document in `docs/` has an assigned maturity level in the tracker
- [ ] Maturity model is referenced from the governance README
- [ ] At least one document has been promoted through the scoring workflow end-to-end
- [ ] Automated validation catches missing Document Control fields for L2+ documents
- [ ] Review schedule in Section 7 is implemented in the documentation-review-schedule.md
- [ ] Target levels in Section 6 are incorporated into the review workflow

---

## 14. References

| Reference | Location |
|---|---|
| Documentation Standards | [GOV-STD-001](01_DocumentationStandards.md) |
| Documentation Ownership | [documentation-ownership.md](documentation-ownership.md) |
| Documentation Review Schedule | [documentation-review-schedule.md](documentation-review-schedule.md) |
| Doc Templates | [templates/](templates/) |
| Change Management | [GOV-CM-001](02_ChangeManagement.md) |
| Governance README | [README.md](README.md) |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial maturity model — 5-level framework, 10 assessment dimensions, scoring rubric, target levels by category, review frequencies, promotion paths |
