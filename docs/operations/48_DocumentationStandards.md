# 48_DocumentationStandards — Documentation Standards & Style Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | OPS-STD-001 |
| Version | 1.0.0 |
| Status | Draft |
| Date | 2026-06-11 |
| Classification | Internal |

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Documentation Architecture](#2-documentation-architecture)
- [3. Document Structure](#3-document-structure)
- [4. Markdown Standards](#4-markdown-standards)
- [5. Content Standards](#5-content-standards)
- [6. Diagram Standards](#6-diagram-standards)
- [7. Review & Quality Process](#7-review--quality-process)
- [8. Templates](#8-templates)
- [9. Maintenance](#9-maintenance)
- [10. Appendices](#10-appendices)
- [Revision History](#revision-history)

---

## 1. Executive Summary

### 1.1 Purpose

Establish a single, authoritative standard for every markdown document in the Second Brain OS project. Consistent structure, naming, and formatting ensure that humans and AI agents can navigate, understand, and maintain the documentation set with minimal friction.

### 1.2 Scope

Applies to all `.md` files under `docs/` and any future documentation added to this repository. External contributions, AI-generated documents, and auto-generated API docs must conform. The only exceptions are auto-generated `CHANGELOG.md`, `README.md`, and third-party vendored docs.

### 1.3 Audience

- **Developers** — writing and maintaining feature, engineering, and operations docs
- **AI Agents** — reading and generating docs during automated workflows
- **Future Contributors** — onboarding via consistent, discoverable documentation

### 1.4 Philosophy

- **Docs as Code** — documentation lives in the repository, versioned alongside code, reviewed in pull requests
- **DRY (Don't Repeat Yourself)** — one authoritative source per fact; cross-reference instead of duplicating
- **Consistency over Creativity** — predictable structure beats clever prose; readers should never guess where to find information
- **Text-First** — plain markdown, no images, no proprietary formats, no binary artifacts

---

## 2. Documentation Architecture

### 2.1 Document Hierarchy / Taxonomy

```
docs/
├── product/          # WHAT we build — vision, PRD, features, user stories, roadmap
│   ├── 00_ProjectVision.md
│   ├── 01_CurrentStateAudit.md
│   ├── 02_PRD.md
│   ├── 03_BRD.md, 03_Features.md
│   └── 04_SRS.md ...
├── engineering/      # HOW it works — architecture, database, API specs, data flow
├── design/           # HOW it looks — UI/UX guidelines, design system, component library
├── ai/               # HOW it thinks — agent definitions, prompt chains, memory schemas
├── security/         # HOW it's protected — threat models, auth flows, compliance
├── devops/           # HOW it's deployed — CI/CD, infrastructure, environment configs
├── qa/               # HOW it's tested — test plans, coverage targets, regression suites
└── operations/       # HOW it's run — monitoring, runbooks, DR, SLA, standards
```

Each directory maps to a functional domain. Cross-category references use relative paths from the `docs/` root.

### 2.2 Numbering Convention

- Two-digit numbering (`00`–`99`) within each category directory
- Numbers indicate **reading order**, not priority — lower numbers are foundational
- Gaps are left for future insertions (e.g., `05`, `06`, `07` are reserved between `04_SRS.md` and `20_Agent.md`)
- Inserting a new document: choose the next available number in the logical order, not the highest existing number

### 2.3 File Naming Convention

```
{NUMBER}_{TitleCaseWithUnderscores}.md
```

**Examples**:
```
02_PRD.md
20_Agent.md
41_DisasterRecovery.md
48_DocumentationStandards.md
```

**Rules**:
- Numbers are zero-padded to 2 digits (`01`, not `1`)
- Title case with underscores: `DisasterRecovery`, not `disaster-recovery` or `Disaster_Recovery`
- Descriptive but concise — under 40 characters including the number and extension
- No special characters except underscore — no spaces, hyphens, or dots before the extension
- No version numbers in filenames — versioning lives in Document Control

---

## 3. Document Structure

### 3.1 Required Sections per Document

Every document MUST include this skeleton:

```markdown
# Title — Subtitle

## Document Control

| Field | Value |
|---|---|
| ...

---

## [Content sections]

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| ...
```

A Table of Contents is required when the document has more than 5 top-level sections (H2 headings).

### 3.2 Document Control Table Format

```markdown
| Field | Value |
|---|---|
| Document ID | {CATEGORY}-{TYPE}-{NNN} |
| Version | {MAJOR.MINOR.PATCH} |
| Status | Draft / Review / Approved / Deprecated |
| Date | {YYYY-MM-DD} |
| Classification | Internal / Confidential / Public |
```

**Document ID pattern**: `{CATEGORY}-{TYPE}-{NNN}`

| Segment | Meaning | Examples |
|---|---|---|
| CATEGORY | 3-letter directory code | PRD (product), ENG (engineering), DSG (design), AI, SEC, OPS, QA, DVO |
| TYPE | 3-letter document type | STD (standard), ARC (architecture), API, PRD (product req doc), RUN (runbook), SRS (software req spec) |
| NNN | 3-digit sequential number | 001, 002, etc. |

### 3.3 Heading Hierarchy

```
# H1 — Page Title (only one per page)

## H2 — Top-level section

### H3 — Subsection

#### H4 — Sub-subsection

##### H5 — Rarely needed
```

**Rules**:
- Exactly one H1 per document — the title
- H2s are the primary structural sections
- Never skip a level (e.g., H2 to H4)
- Never bold text in place of a heading — use proper heading markup
- Headings should not end with a colon

### 3.4 Revision History Format

```markdown
| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial document |
| 1.1.0 | 2026-07-01 | Developer | Added section on X |
```

**Semantic versioning**:

| Increment | Trigger |
|---|---|
| MAJOR | Significant restructuring, rewrite, or breaking change |
| MINOR | New sections or substantial additions |
| PATCH | Corrections, minor updates, formatting fixes |

---

## 4. Markdown Standards

### 4.1 Syntax Rules

- Use **GitHub-Flavored Markdown (GFM)** — the CommonMark superset supported by GitHub
- Line breaks: single blank line between paragraphs (two newlines); no double-blank lines
- No trailing whitespace on any line
- Code blocks MUST specify a language identifier
- Tables must have an alignment separator row (`|---|---|---|`)
- Unordered lists: use `-` (not `*` or `+`)
- Ordered lists: always start with `1.` — let the renderer auto-number
- Bold: `**text**` (not `__text__`)
- Italic: `*text*` (not `_text_`)
- Horizontal rules: `---` with blank lines before and after
- Blockquotes: `>` for quotations, warnings, or callouts

### 4.2 Code Block Standards

````
```python
def example():
    pass
```

```typescript
const x: string = "hello";
```

```sql
SELECT * FROM tasks WHERE user_id = '...';
```

```bash
npm run build
```

```json
{
  "key": "value"
}
```

```yaml
name: CI
on: [push]
```

```mermaid
graph TD
    A --> B
```
````

**Rules**:
- Every code block must have a language tag — no bare triple backticks
- Inline code: use single backticks for filenames, commands, and short variable names
- No syntax errors in example code blocks
- Use `text` tag only when no language applies (e.g., example output)

### 4.3 Table Standards

```markdown
| Column A | Column B | Column C |
|---|---|---|
| Value 1 | Value 2 | 123 |
| Value 3 | Value 4 | 456 |
```

**Rules**:
- Always include the alignment separator row: `|---|---|---|`
- Left-align text, right-align numbers
- No blank cells — use an em-dash (`—`) for intentionally empty cells
- Maximum 7 columns. Wider data should be split or summarized
- Tables are for structured data only — do not use tables for layout
- Keep cell content concise; multi-sentence cells should be footnoted or moved to paragraphs

### 4.4 Linking Standards

```markdown
<!-- Internal cross-reference -->
[Architecture Overview](../engineering/00_Architecture.md)

<!-- With anchor -->
[Authentication Flow](../engineering/10_Auth.md#oauth-flow)

<!-- External -->
[Next.js Documentation](https://nextjs.org/docs)

<!-- Section anchor within same page -->
[See Section 2.1](#21-document-hierarchy--taxonomy)
```

**Rules**:
- Never use raw URLs as link text — `https://example.com` must become `[Example](https://example.com)`
- Internal links use relative paths from the referencing document to the target
- Anchors are auto-generated from heading text (lowercase, spaces to hyphens, remove special chars)
- Link text should describe the destination, not instructions like "click here"

---

## 5. Content Standards

### 5.1 Tone & Voice

| Quality | Guideline |
|---|---|
| Professional | Technical writing tone — precise, concise, objective |
| Active voice | "The API returns a task object" — not "A task object is returned by the API" |
| Present tense | "The system uses Supabase" — not "The system will use Supabase" |
| Second person | "Run the following command" — for instructions and procedures |
| Third person | "The scheduler executes daily" — for descriptions and reference |
| No undefined jargon | Define acronyms and domain terms on first use |
| No marketing | Describe what the system does, not how impressive it is |

### 5.2 Language Rules

| Do | Don't |
|---|---|
| "Configure the environment" | "Set up the stuff" |
| "The system returns" | "The system would return" |
| "Click Save" | "You need to click on the Save button" |
| "SQL injection protection" | "SQLi prot" |
| "For example," | "e.g." (avoid Latin abbreviations — use English) |
| "That is," | "i.e." |
| U.S. English spelling | British English — "color", not "colour"; "authorize", not "authorise" |
| "5GB" | "5 GB" (no space between number and unit) |

### 5.3 Do's and Don'ts

- DO use bullet points for lists of related items
- DO use numbered lists for sequential instructions (steps the reader must follow in order)
- DO use tables for comparisons, parameters, and structured data
- DO use code blocks for commands, configuration, and code snippets
- DO use blockquotes (`>`) for warnings, notes, and important callouts
- DON'T use screenshots — this project uses text-based documentation; use ASCII or Mermaid diagrams instead
- DON'T use emojis in enterprise documentation
- DON'T use inline HTML in markdown — use GFM constructs only
- DON'T use footnotes — use inline parentheticals or appendices for supplementary information
- DON'T use `TODO`, `TBD`, `FIXME`, or `HACK` in committed documents — these are only acceptable in Draft status

---

## 6. Diagram Standards

### 6.1 Diagram Types

Since the project uses plain markdown without images or attachments, two approaches are used:

| Type | Use Case | Max Complexity |
|---|---|---|
| Mermaid.js | Sequence diagrams, Gantt charts, class diagrams, state machines, complex flowcharts | 15 nodes |
| ASCII art | Simple flowcharts, architecture boxes, CLI output mockups | 80 chars wide |

### 6.2 Mermaid Guidelines

````mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[FastAPI App]
    C --> D[(Supabase)]
    B --> E[Redis Cache]
````

**Rules**:
- Always wrap in a ` ```mermaid ` fenced code block
- Maximum 15 nodes per diagram — split complex flows into multiple diagrams
- Use descriptive node labels: `A[User Authentication Service]`, not `A[Auth]`
- Preferred diagram types: `graph TD` (top-down flowcharts), `sequenceDiagram` (interactions), `classDiagram` (data models)
- Style diagrams with `style` directives sparingly — clarity over aesthetics
- Place diagrams immediately after the paragraph that introduces them

### 6.3 ASCII Art Guidelines

```
+----------------+        +----------------+
|   Frontend     |------->|    Backend     |
|   (Next.js)    |        |   (FastAPI)    |
+----------------+        +----------------+
         |                       |
         |  HTTP/HTTPS           |  SQL
         v                       v
+----------------+        +----------------+
|     Client     |        |   Supabase     |
|    Browser     |        |  (PostgreSQL)  |
+----------------+        +----------------+
```

**Rules**:
- Use `-` for horizontal lines, `|` for vertical lines, `+` for corners/intersections
- Align all elements with spaces — tabs render unpredictably
- Keep diagrams under 80 characters wide
- Always wrap ASCII diagrams in a fenced code block (no language tag, or `text`)
- Prefer Mermaid over ASCII art for anything more complex than 5 boxes

---

## 7. Review & Quality Process

### 7.1 Document Review Checklist

Every document MUST pass the following checks before being marked as Approved:

- [ ] Document Control table filled completely with valid Document ID
- [ ] No placeholder text — zero occurrences of `TODO`, `TBD`, `FIXME`, `HACK`
- [ ] All links verified — no broken internal or external references
- [ ] Tables render correctly with alignment separator rows
- [ ] Code blocks specify a language identifier
- [ ] Spelling and grammar checked against project dictionary
- [ ] Consistent terminology — matches existing docs (no synonyms for the same concept)
- [ ] Version number incremented correctly per semantic versioning rules
- [ ] Revision History updated with the new version entry
- [ ] Cross-references use correct relative paths (not absolute or repo-relative)

### 7.2 Document Lifecycle

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

### 7.3 Review Cadence

| Document Category | Review Frequency | Trigger for Unscheduled Review |
|---|---|---|
| Engineering (architecture, API, database) | Quarterly | Any schema or API change |
| Operations (runbooks, DR, SLA, standards) | Quarterly | Infrastructure or deployment change |
| Product (PRD, features, roadmap) | Semi-annually | Sprint planning or roadmap revision |
| AI (agents, prompts, memory schemas) | Per agent change | Every agent or prompt update |
| Security (threat models, compliance) | Annually | Incident or audit finding |
| Design (UI/UX, design system) | Per component addition | New component or design token added |

---

## 8. Templates

### 8.1 Standard Document Template

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

---

## 1. Section One

Content here.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | {date} | Developer | Initial document |
```

### 8.2 API Endpoint Template

```markdown
### `{METHOD} /api/{path}`

**Description**: What this endpoint does.

**Authentication**: Required / Optional / None

**Request Body**:

```json
{
  "field": "type — description"
}
```

**Response 200**:

```json
{
  "id": "uuid",
  "field": "value"
}
```

**Errors**: 400, 401, 404, 500
```

### 8.3 Procedure / Runbook Template

```markdown
## Procedure: {Procedure Name}

**Purpose**: Why this procedure exists.

**Prerequisites**:
- Access to {system}
- {Tool} installed

**Steps**:
1. Step one
2. Step two

**Verification**: How to confirm the procedure succeeded.

**Rollback**: How to undo if something goes wrong.
```

---

## 9. Maintenance

### 9.1 Documentation Debt

- Track missing, outdated, or incomplete docs as GitHub Issues
- Required label: `type: documentation`
- Target threshold: no more than 5 open documentation issues at any time
- Every feature pull request MUST include or update relevant documentation — PRs without doc changes require an explicit exemption
- Documentation debt is technical debt — prioritize alongside code debt

### 9.2 Automation (Future State)

| Tool | Purpose | Configuration |
|---|---|---|
| `markdownlint` | Markdown style and syntax enforcement | `.markdownlint.json` at repo root |
| `lychee` or `broken-link-checker` | Verify all internal and external links | CI job on PR |
| `cspell` | Spell check with project-specific dictionary | `cspell.json` at repo root |
| `doctoc` or `markdown-toc` | Auto-generate and maintain tables of contents | Pre-commit hook or CI |
| Custom CI check | Validate Document Control, Revision History, and required sections | GitHub Action on PR |

**Implementation priority**: spell check and link checking first (catch real errors), then markdownlint (enforce style), then auto-TOC (reduce friction).

---

## 10. Appendices

### Appendix A: Quick Reference Card

| Rule | Standard |
|---|---|
| File name | `{NN}_{TitleCase}.md` |
| Document ID | `{CAT}-{TYPE}-{NNN}` |
| Version | `{MAJOR.MINOR.PATCH}` |
| H1 per page | Exactly one |
| Language on code blocks | Always |
| Table alignment | `|---|---|---|` |
| No raw URLs | `[text](url)` always |
| No emojis | Never |
| No inline HTML | Never |
| No screenshots | ASCII or Mermaid instead |
| Active voice | Always |
| Present tense | Always |

### Appendix B: Document ID Registry

All active document IDs in the project.

| Document ID | File | Status |
|---|---|---|
| OPS-STD-001 | `docs/operations/48_DocumentationStandards.md` | Draft |

*This registry must be updated when new documents are created.*

### Appendix C: Spelling Dictionary

Project-specific terms that must be recognized by spell checkers.

```
SecondBrain, ARIA, FastAPI, Supabase, Nextjs, Zustand, Framer, Postgres, Pydantic, 
APScheduler, Runbook, Runbooks, Devops, Cyberpunk, GFM, CommonMark, Mermaid, 
markdownlint, lychee, cspell, doctoc, pre-commit, monorepo
```

### Appendix D: Common Markdown Mistakes

| Mistake | Correct |
|---|---|
| `## Title:` | `## Title` (no trailing colon) |
| `**Title**` as section heading | Use `## Title` |
| `_italic_` | `*italic*` |
| Bare URLs: `https://example.com` | `[Example](https://example.com)` |
| `<br/>` for line breaks | Blank line for new paragraph |
| Mixed list markers (`-` and `*`) | Consistent `-` only |
| Missing blank line before list | Always add blank line before `-` or `1.` |
| `[see here](url)` | `[Descriptive text](url)` |
| No language on ` ``` ` | Always specify: ` ```python ` |

### Appendix E: Revision History — This Document

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial document |
