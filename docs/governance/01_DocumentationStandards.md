# 01_DocumentationStandards — Documentation Standards & Style Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-STD-001 |
| Version | 2.1.0 |
| Status | Approved |
| Date | 2026-07-11 |
| Classification | Internal |
| Owner | Developer |
| Location | `docs/governance/01_DocumentationStandards.md` |
| Supersedes | `docs/operations/48_DocumentationStandards.md` |

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Purpose](#2-purpose)
- [3. Scope](#3-scope)
- [4. Business Context](#4-business-context)
- [5. Documentation Architecture](#5-documentation-architecture)
- [6. Enterprise Document Structure](#6-enterprise-document-structure)
- [7. Markdown Standards](#7-markdown-standards)
- [8. Content Standards](#8-content-standards)
- [9. Diagram Standards](#9-diagram-standards)
- [10. Templates](#10-templates)
- [11. Cross-Reference Standards](#11-cross-reference-standards)
- [12. Review & Quality Process](#12-review--quality-process)
- [13. Maintenance & Governance](#13-maintenance--governance)
- [14. Non-Functional Requirements](#14-non-functional-requirements)
- [15. Performance Targets](#15-performance-targets)
- [16. Security & Compliance](#16-security--compliance)
- [17. Edge Cases](#17-edge-cases)
- [18. Failure Scenarios](#18-failure-scenarios)
- [19. Risks & Mitigations](#19-risks--mitigations)
- [20. Acceptance Criteria](#20-acceptance-criteria)
- [21. Traceability](#21-traceability)
- [22. Implementation Notes](#22-implementation-notes)
- [23. Testing Strategy](#23-testing-strategy)
- [24. References](#24-references)
- [25. Appendices](#25-appendices)
- [Revision History](#revision-history)

---

## 1. Executive Summary

This document establishes the single authoritative standard for every markdown document in the Second Brain OS project. It defines the mandatory enterprise document structure with 20 required sections, cross-reference standards, quality processes, and automation rules. Consistent structure ensures that humans and AI agents can navigate, understand, and maintain the documentation set with minimal friction across the entire 200+ file corpus.

## 2. Purpose

- Provide a single source of truth for documentation structure, style, and governance
- Ensure every document meets enterprise quality standards
- Enable AI agents to read, generate, and update docs consistently
- Maintain cross-references so updates in one document propagate to related documents
- Support audit readiness and SOC 2 compliance

## 3. Scope

Applies to all `.md` files under `docs/` and any future documentation added to this repository. External contributions, AI-generated documents, and auto-generated API docs must conform. Exceptions: auto-generated `CHANGELOG.md`, `README.md`, and third-party vendored docs.

## 4. Business Context

### 4.1 Audience

- **Developers** — writing and maintaining feature, engineering, and operations docs
- **AI Agents** — reading and generating docs during automated workflows
- **Future Contributors** — onboarding via consistent, discoverable documentation
- **Enterprise Reviewers** — auditors, security reviewers, architecture board

### 4.2 Philosophy

- **Docs as Code** — documentation lives in the repository, versioned alongside code, reviewed in pull requests
- **DRY (Don't Repeat Yourself)** — one authoritative source per fact; cross-reference instead of duplicating
- **Consistency over Creativity** — predictable structure beats clever prose
- **Text-First** — plain markdown, no images, no proprietary formats, no binary artifacts
- **Traceability** — every document connects to requirements, decisions, and related documents
- **Audit-Ready** — every document includes version history, owner, status, and cross-references

### 4.3 Document Lifecycle

```
Draft --> Review --> Approved --> Published --> Deprecated --> Archived
  ^                                                            |
  |____________________________________________________________|
```

| Status | Meaning | Expected Actions |
|---|---|---|
| Draft | In development, not ready for use | Author writes, no review required |
| Review | Ready for feedback | At least one peer review, checklist applied |
| Approved | Ready for use | Reviewer sign-off, checklist passed |
| Published | Released alongside a software version | Tagged in release notes, linked from changelog |
| Deprecated | Superseded but still available | Add deprecation notice at top, link to replacement |
| Archived | Removed from active docs | Move to `docs/archive/`, remove from index |

---

## 5. Documentation Architecture

### 5.1 Document Hierarchy / Taxonomy

```
docs/
├── product/          # WHAT we build — vision, governance, PRD, features, roadmap
├── engineering/      # HOW it works — architecture, database, API, backend, frontend
├── design/           # HOW it looks — UI/UX, design system, tokens, wireframes, motion
├── governance/       # HOW docs are governed — standards, ownership, review schedule, change management
├── ai/               # HOW it thinks — agent architecture, memory, prompts, skills
├── security/         # HOW it's protected — threat models, auth, encryption, compliance
├── devops/           # HOW it's deployed — CI/CD, Docker, k8s, environments, backup
├── qa/               # HOW it's tested — testing strategy, E2E, performance, security testing
├── frontend/         # Frontend-specific implementation docs
└── operations/       # HOW it's run — monitoring, runbooks, DR, analytics, standards
```

Each directory maps to a functional domain. Cross-category references use relative paths from the `docs/` root.

### 5.2 Numbering Convention

- Two-digit numbering (`00`–`99`) within each category directory
- Numbers indicate reading order, not priority
- Gaps are left for future insertions
- Inserting a new document: choose the next available number in the logical order

### 5.3 File Naming Convention

```
{NN}_{TitleCaseWithUnderscores}.md
```

**Rules:**
- Numbers are zero-padded to 2 digits (`01`, not `1`)
- Title case with underscores: `DisasterRecovery`, not `disaster-recovery`
- Descriptive but concise — under 40 characters including the number and extension
- No special characters except underscore
- No version numbers in filenames

---

## 6. Enterprise Document Structure

### 6.1 Mandatory Sections

Every document MUST include ALL of the following sections, in this order:

```markdown
# Title — Subtitle

## Document Control

| Field | Value |
|---|---|
| Document ID | {CAT}-{TYPE}-{NNN} |
| Version | 1.0.0 |
| Status | Draft / Review / Approved |
| Date | {YYYY-MM-DD} |
| Classification | Internal / Confidential / Public |
| Owner | Developer |

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- ...

---

## 1. Executive Summary

## 2. Purpose

## 3. Scope

## 4. Business Context

## 5. Functional Specification

## 6. Non-Functional Requirements

## 7. Architecture

## 8. Diagrams

## 9. Data Models

## 10. APIs

## 11. Security

## 12. Performance Targets

## 13. Edge Cases

## 14. Failure Scenarios

## 15. Risks & Mitigations

## 16. Acceptance Criteria

## 17. Traceability

## 18. Implementation Notes

## 19. Testing Strategy

## 20. References

---

## Revision History
```

A Table of Contents is required when the document has more than 5 top-level sections.

### 6.2 Document Control Table Format

```markdown
| Field | Value |
|---|---|
| Document ID | {CATEGORY}-{TYPE}-{NNN} |
| Version | {MAJOR.MINOR.PATCH} |
| Status | Draft / Review / Approved / Deprecated |
| Date | {YYYY-MM-DD} |
| Classification | Internal / Confidential / Public |
| Owner | Developer |
```

**Document ID pattern:** `{CATEGORY}-{TYPE}-{NNN}`

| Segment | Meaning | Examples |
|---|---|---|
| CATEGORY | 3-letter directory code | PRD (product), ENG (engineering), GOV (governance), DSG (design), AI, SEC, OPS, QA, DVO |
| TYPE | 3-letter document type | STD (standard), ARC (architecture), API, PRD, RUN (runbook), SRS |
| NNN | 3-digit sequential number | 001, 002, etc. |

### 6.3 Heading Hierarchy

```
# H1 — Page Title (only one per page)
## H2 — Top-level section
### H3 — Subsection
#### H4 — Sub-subsection
##### H5 — Rarely needed
```

### 6.4 Revision History Format

```markdown
| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | {date} | Developer | Initial document |
```

**Semantic versioning:** MAJOR (restructure), MINOR (new sections), PATCH (corrections)

---

## 7. Markdown Standards

### 7.1 Syntax Rules

- Use **GitHub-Flavored Markdown (GFM)**
- Single blank line between paragraphs
- No trailing whitespace
- Code blocks MUST specify a language identifier
- Tables must have alignment separator row
- Unordered lists: use `-`
- Ordered lists: start with `1.`
- Bold: `**text**`, Italic: `*text*`
- No inline HTML
- No emojis

### 7.2 Linking Standards

```markdown
[Name](../category/File.md)
[Name](#section-anchor)
[Name](https://example.com)
```

**Rules:**
- Never use raw URLs as link text
- Internal links use relative paths
- Link text must describe the destination

---

## 8. Content Standards

### 8.1 Tone & Voice

| Quality | Guideline |
|---|---|
| Professional | Technical writing tone — precise, concise, objective |
| Active voice | "The API returns a task object" |
| Present tense | "The system uses Supabase" |
| Second person | Instructions and procedures |
| Third person | Descriptions and reference |
| No undefined jargon | Define acronyms on first use |

### 8.2 Language Rules

| Do | Don't |
|---|---|
| "Configure the environment" | "Set up the stuff" |
| U.S. English spelling | British English |
| "For example," | "e.g." |
| "That is," | "i.e." |

### 8.3 Prohibited Content

- No emojis
- No inline HTML
- No TODO, TBD, FIXME, HACK in committed documents
- No screenshots (use Mermaid or ASCII)
- No marketing language

---

## 9. Diagram Standards

### 9.1 Diagram Types

| Type | Use Case | Max Complexity |
|---|---|---|
| Mermaid.js | Sequence, class, state, flowcharts | 15 nodes |
| ASCII art | Simple flowcharts, CLI mockups | 80 chars wide |

### 9.2 Mermaid Rules

- Always wrap in ` ```mermaid ` fenced code block
- Max 15 nodes per diagram
- Use descriptive labels
- Preferred: `graph TD`, `sequenceDiagram`, `classDiagram`
- Place diagram immediately after the paragraph that introduces it

### 9.3 ASCII Art Rules

- Use `-` for horizontal, `|` for vertical, `+` for corners
- Keep under 80 characters wide
- Always wrap in fenced code block

---

## 10. Templates

### 10.1 Enterprise Document Template

```markdown
# Title — Subtitle

## Document Control

| Field | Value |
|---|---|
| Document ID | {CAT}-{TYPE}-{NNN} |
| Version | 1.0.0 |
| Status | Draft |
| Date | {YYYY-MM-DD} |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

...

---

## 1. Executive Summary
## 2. Purpose
## 3. Scope
## 4. Business Context
## 5. Functional Specification
## 6. Non-Functional Requirements
## 7. Architecture
## 8. Diagrams
## 9. Data Models
## 10. APIs
## 11. Security
## 12. Performance Targets
## 13. Edge Cases
## 14. Failure Scenarios
## 15. Risks & Mitigations
## 16. Acceptance Criteria
## 17. Traceability
## 18. Implementation Notes
## 19. Testing Strategy
## 20. References

---

## Revision History
```

### 10.2 API Endpoint Template

```markdown
### `{METHOD} /api/{path}`

**Description**: ...
**Authentication**: Required / Optional / None

**Request Body**:

```json
{ "field": "type — description" }
```

**Response 200**:

```json
{ "id": "uuid", "field": "value" }
```

**Errors**: 400, 401, 404, 500
```

### 10.3 Procedure / Runbook Template

```markdown
## Procedure: {Procedure Name}

**Purpose**: ...
**Prerequisites**: ...
**Steps**: 1. ... 2. ...
**Verification**: ...
**Rollback**: ...
```

### 10.4 Data Model Template

```markdown
### Table: `{table_name}`

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | uuid | PK, NOT NULL | Primary key |
| user_id | uuid | FK, NOT NULL | References users.id |

**Relationships:**
- `user_id` → `users.id` (many-to-one)

**Indexes:**
- `idx_{table}_user_id` on `user_id`
```

---

## 11. Cross-Reference Standards

### 11.1 Cross-Reference Types

| Type | Format | Example |
|---|---|---|
| Internal doc | `[Name](../category/File.md)` | `[Database Schema](../engineering/15_Database.md)` |
| Same-category doc | `[Name](File.md)` | `[API Reference](17_API.md)` |
| Section anchor | `[Name](../file.md#section)` | `[Auth flow](../security/AuthArchitecture.md#oauth)` |
| External | `[Name](https://...)` | `[Supabase Docs](https://supabase.io/docs)` |
| ADR | `[ADR-004](../engineering/adr/ADR-004-*.md)` | `[ADR-004](../engineering/adr/ADR-004-in-process-agents-over-microservices.md)` |

### 11.2 Cross-Reference Index

The `docs/DOCUMENTATION_INDEX.md` file serves as the master registry. It lists every document by category with file path, document ID, status, and related documents.

---

## 12. Review & Quality Process

### 12.1 Document Review Checklist

- [ ] Document Control table filled completely
- [ ] All 20 enterprise sections present (or explicitly N/A)
- [ ] No placeholder text (TODO, TBD, FIXME, HACK)
- [ ] All links verified
- [ ] Tables render correctly with alignment separator rows
- [ ] Code blocks specify a language identifier
- [ ] Spelling and grammar checked
- [ ] Consistent terminology
- [ ] Version number incremented correctly
- [ ] Revision History updated
- [ ] Cross-references use correct relative paths
- [ ] Mermaid diagrams render correctly
- [ ] Traceability section links to related documents

### 12.2 Review Cadence

| Category | Frequency | Trigger for Unscheduled Review |
|---|---|---|
| Engineering | Quarterly | Schema or API change |
| Operations | Quarterly | Infrastructure change |
| Product | Semi-annually | Sprint planning |
| AI | Per agent change | Agent or prompt update |
| Security | Annually | Incident or audit |
| Design | Per component addition | New component or token |
| Governance | Quarterly | Process or ownership change |

---

## 13. Maintenance & Governance

### 13.1 Documentation Debt

- Track as GitHub Issues with `type: documentation` label
- Max 5 open documentation issues at any time
- Every feature PR must include or update relevant docs
- Documentation debt = technical debt

### 13.2 Automation (Future State)

| Tool | Purpose |
|---|---|
| `markdownlint` | Markdown style enforcement |
| `lychee` | Link validation in CI |
| `cspell` | Spell check with project dictionary |
| Custom CI check | Validate Document Control and required sections |

---

## 14. Non-Functional Requirements

| Requirement | Target | Measurement |
|---|---|---|
| Document load time | < 100ms | Page render |
| Cross-reference accuracy | 100% | All links resolve |
| Maximum document size | < 5000 lines | Line count |
| Minimum document size | > 50 lines of content | Substantive sections |
| Language | U.S. English | Consistent |
| Formatting consistency | 100% | Passes markdownlint |
| Version tracking | All docs | Revision history |

---

## 15. Performance Targets

| Metric | Target |
|---|---|
| Time to find any document | < 30 seconds via index |
| Time to understand a component | < 10 minutes |
| Cross-reference link validity | 100% verified monthly |
| Spelling accuracy | Zero errors in approved docs |
| Section structure compliance | 100% of docs pass validation |

---

## 16. Security & Compliance

| Requirement | Standard |
|---|---|
| Classification labels | Every doc has Internal/Confidential/Public |
| Audit trail | Revision history in every doc |
| Access control | Repo-level (private repository) |
| No secrets in docs | Passwords, keys, tokens never documented |

---

## 17. Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Document references non-existent file | CI rejects PR |
| Document ID conflict | Index catches duplicate |
| Two docs with same name | Numbering convention prevents |
| Document is deprecated | Deprecation notice at top |
| Feature is retired | Mark doc as deprecated, archive later |

---

## 18. Failure Scenarios

| Scenario | Impact | Recovery |
|---|---|---|
| Stale documentation | Misleading guidance | Quarterly review cycle |
| Missing document | Developer confusion | Cross-reference validation |
| Conflicting docs | Developer confusion | Index ensures single source of truth |
| Broken links | Frustrated readers | CI catches before merge |

---

## 19. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Docs drift from code | High | Medium | Quarterly review, doc changes in PR |
| Inconsistent quality | Medium | High | Standards doc, checklist, AI generation |
| Missing cross-references | Medium | Medium | CI validation |
| Too many docs to maintain | Medium | High | Automated generation, quarterly cleanup |

---

## 20. Acceptance Criteria

- [ ] Every document in `docs/` follows the enterprise structure (20 sections)
- [ ] Cross-reference index exists and is accurate
- [ ] All docs validated against this standards document
- [ ] AI agents can generate compliant docs using this standard
- [ ] Review checklist followed for every new/updated doc

---

## 21. Traceability

| Artifact | Location |
|---|---|
| This standard | `docs/governance/01_DocumentationStandards.md` |
| Cross-reference index | `docs/DOCUMENTATION_INDEX.md` |
| Review checklist | Section 12 of this document |
| Ownership matrix | `docs/governance/documentation-ownership.md` |
| Review schedule | `docs/governance/documentation-review-schedule.md` |
| Change management | `docs/governance/02_ChangeManagement.md` |

---

## 22. Implementation Notes

- All new documents MUST use the enterprise template (Section 10.1)
- Existing documents being upgraded should add missing sections gradually
- Use AI agents to generate initial drafts, apply human review before approving
- Update Document ID Registry every time a document is added or deprecated

---

## 23. Testing Strategy

| Test Type | What | How |
|---|---|---|
| Link validation | All cross-references | `lychee` or custom CI script |
| Structure validation | Required sections present | Custom CI script |
| Spelling | Technical terms | `cspell` with custom dictionary |
| Markdown linting | Syntax and style | `markdownlint` |
| ID uniqueness | No duplicate Document IDs | Cross-reference CI check |

---

## 24. References

- GitHub Flavored Markdown Spec: https://github.github.com/gfm/
- Mermaid Documentation: https://mermaid.js.org/
- Docs-as-code guide: https://www.writethedocs.org/guide/docs-as-code/

---

## 25. Appendices

### Appendix A: Quick Reference Card

| Rule | Standard |
|---|---|
| File name | `{NN}_{TitleCase}.md` |
| Document ID | `{CAT}-{TYPE}-{NNN}` |
| Version | `{MAJOR.MINOR.PATCH}` |
| H1 per page | Exactly one |
| Required sections | 20 |
| Language on code blocks | Always |
| Table alignment | `|---|---|---|` |
| No raw URLs | `[text](url)` always |
| No emojis | Never |
| Active voice | Always |
| Present tense | Always |

### Appendix B: Spelling Dictionary

```
SecondBrain, ARIA, FastAPI, Supabase, Nextjs, Zustand, Framer, Postgres, Pydantic, APScheduler, Runbook, Runbooks, Devops, Cyberpunk, GFM, CommonMark, Mermaid, markdownlint, lychee, cspell, doctoc, pre-commit, monorepo, shadcn, Radix, Playwright, Vitest, Vite, Ollama, Anthropic, Claude, Serwist, Tailwind, FramerMotion, Lucide, SupabaseRealtime, WebSocket, Webhook, PWA, ServiceWorker
```

### Appendix C: Common Markdown Mistakes

| Mistake | Correct |
|---|---|
| `## Title:` | `## Title` |
| `**Title**` as H2 | Use `## Title` |
| `_italic_` | `*italic*` |
| Bare URLs | `[text](url)` |
| Mixed list markers | Consistent `-` only |
| No language on code block | Always specify |

### Appendix D: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial document |
| 2.0.0 | 2026-07-10 | Developer | Enterprise upgrade: 20-section template, cross-reference standards, NFRs, performance targets, edge cases, failure scenarios, risks, acceptance criteria, traceability, testing strategy, security compliance |
| 2.1.0 | 2026-07-11 | Developer | Moved from `docs/operations/` to `docs/governance/`. Updated Document ID to GOV-STD-001. Added governance directory to documentation architecture. Updated traceability section. |
