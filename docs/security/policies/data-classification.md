# Data Classification and Handling Policy

## Document Control

| Field | Value |
|---|---|
| **Document ID** | SEC-DC-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | Internal |
| **Last Updated** | 2026-07-11 |
| **Next Review** | 2026-10-11 |
| **Owner** | Developer (Staff Security Engineer) |
| **Approved By** | Developer |
| **Related Documents** | SEC-001 Security Architecture, SEC-046 Data Privacy, SEC-ENC-001 Encryption, SEC-POLICY-VULN-001, SEC-POLICY-IR-001, COMP-SOC2-001 |

---

## 1. Purpose and Scope

### 1.1 Purpose

This policy defines the data classification framework for Second Brain OS (ARIA OS). It establishes four tiers of data sensitivity, handling requirements for each tier, and the data inventory mapping every system component to its classification tier. All data stored, processed, or transmitted by the system MUST be classified and handled according to this policy.

### 1.2 Scope

This policy applies to:

| In Scope | Out of Scope |
|---|---|
| All data stored in Supabase (production, staging, dev) | Vendor-managed infrastructure telemetry (Vercel, Railway, Supabase internal) |
| Application configuration and secrets (env vars) | Third-party SaaS usage data (e.g., Anthropic API logs) |
| AI prompts, agent outputs, and generated content | Physical documents or offline records |
| Logs, metrics, and audit trails | End-user device data not transmitted to the system |
| Source code and CI/CD configurations | |
| Documentation and design artifacts | |

---

## 2. Classification Tiers

### 2.1 Tier Definitions

| Tier | Label | Definition | Examples | Risk if Disclosed |
|---|---|---|---|---|
| **T4** | **Public** | Information intended for public consumption. No confidentiality requirement. | README, AGENTS.md (public portions), marketing materials, public API docs | No impact |
| **T3** | **Internal** | Business information not intended for public disclosure but low sensitivity if leaked. | Internal documentation, design docs, threat models, test data, sprint plans | Minor reputational risk |
| **T2** | **Confidential** | User-identifiable or business-sensitive information. Restricted to authorized parties. | User tasks, goals, habits, courses, projects, resources, income entries, time entries, opportunities, ideas, sleep logs, memory entries, chat messages, daily briefings, weekly reviews | Moderate (privacy violation, competitive insight) |
| **T1** | **Restricted** | Highly sensitive information. Strict access control required. Breach would cause significant harm. | Authentication tokens, JWT secrets, API keys, database credentials, user email addresses, AI provider keys, session tokens, encryption keys | Severe (account takeover, data breach, regulatory penalty) |

### 2.2 Classification Criteria

| Criterion | T4 (Public) | T3 (Internal) | T2 (Confidential) | T1 (Restricted) |
|---|---|---|---|---|
| Contains PII | Never | Never | May contain | Contains |
| Contains authentication secrets | Never | Never | Never | Always |
| Contains financial data | Never | Never | Yes (income) | Never |
| Contains health/sleep data | Never | Never | Yes | Never |
| Contains AI-generated insights | Never | Never | Yes | Never |
| Required for application function | No | No | Yes | Yes |
| Could enable account takeover | Never | Never | Never | Yes |

---

## 3. Data Inventory

### 3.1 Database Tables by Classification

#### T2 â€” Confidential

| Table | Description | Contains PII | Retention | Encryption Required |
|---|---|---|---|---|
| `tasks` | User tasks with priority, status, dependencies | Task descriptions may contain personal information | Per DPA or indefinite | At rest (Supabase AES-256) |
| `courses` | Course tracking with progress, deadlines | Course names, grades | Per DPA | At rest |
| `goals` | Goals with roadmap, milestones | Goal descriptions | Per DPA | At rest |
| `habits` | Habit definitions | Habit names, frequencies | Per DPA | At rest |
| `habit_logs` | Daily habit completion logs | Completion patterns | Per DPA | At rest |
| `sleep_logs` | Sleep tracking with score, debt | Sleep patterns, health insights | Per DPA | At rest |
| `income_entries` | Income logs with hourly rate | Financial data | Per DPA | At rest |
| `projects` | Project phases, blockers | Project details | Per DPA | At rest |
| `ideas` | Idea pipeline entries | Idea content | Per DPA | At rest |
| `resources` | Resource library | Resource content, URLs | Per DPA | At rest |
| `opportunities` | Opportunity radar entries | Match scores, descriptions | Per DPA | At rest |
| `time_entries` | Time tracking data | Work patterns | Per DPA | At rest |
| `chat_messages` | ARIA chat history | Full conversation content | Per DPA | At rest |
| `daily_briefings` | Generated briefings | Summarized personal data | Per DPA | At rest |
| `weekly_reviews` | Weekly reviews | Summarized personal data | Per DPA | At rest |
| `memory` | AI persistent memory | Learned preferences, patterns | Per DPA | At rest |
| `learning_progress` | Learning metrics | Skill assessments | Per DPA | At rest |
| `feedback` | User feedback entries | Feedback content | Per DPA | At rest |

#### T1 â€” Restricted

| Table / Resource | Description | Contains Secrets | Retention | Encryption Required |
|---|---|---|---|---|
| `users` | User profiles (email, preferences, settings) | Email addresses (PII), preferences | Per DPA + legal hold | At rest + TLS |
| `auth_tokens` | JWT tokens, session data | Authentication tokens | 1 hour (JWT expiry) | At rest + TLS |
| Environment variables | API keys, database URLs, JWT secrets | Full credentials | Rotated per policy | At rest + TLS |

#### T3 â€” Internal

| Resource | Description |
|---|---|
| Source code (packages/, apps/, services/) | Application source code |
| CI/CD configurations (.github/) | Pipeline definitions |
| Internal documentation (docs/ except public) | Architecture, designs, runbooks |
| Test data | Anonymized test fixtures |
| Threat models, pen test reports | Security assessments |
| SOC 2 evidence | Compliance documentation |

#### T4 â€” Public

| Resource | Description |
|---|---|
| README.md | Project overview |
| AGENTS.md (selected sections) | Public portions |
| Public-facing API documentation | API reference |
| LICENSE | MIT License |

### 3.2 Data Flow Diagram

```
User Input (Browser/CLI)
    â”‚
    â–¼
[TLS 1.3] â”€â”€â–º Vercel Edge (T4/T3)
    â”‚                 â”‚
    â–¼                 â–¼
FastAPI â”€â”€â–º Supabase (T2/T1 at rest, AES-256)
    â”‚
    â”œâ”€â”€â–º Ollama/Claude API (T2 prompts)
    â”œâ”€â”€â–º Redis Cache (T2, ephemeral)
    â””â”€â”€â–º Structured Logs (T3)
```

---

## 4. Handling Requirements

### 4.1 Access Control

| Tier | Authentication Required | Authorization Check | Multi-Factor | Principle of Least Privilege |
|---|---|---|---|---|
| T4 (Public) | No | No | No | N/A |
| T3 (Internal) | Yes (GitHub) | GitHub team membership | Recommended | Yes |
| T2 (Confidential) | Yes (JWT) | RLS + user_id filter | No (single-user app) | Yes â€” user-scoped |
| T1 (Restricted) | Yes (JWT + API key) | Explicit role check | Recommended | Yes â€” minimal surface |

### 4.2 Encryption

| Tier | At Rest | In Transit | Application-Level |
|---|---|---|---|
| T4 (Public) | Not required | Not required | Not required |
| T3 (Internal) | Not required | Recommended | Not required |
| T2 (Confidential) | Required (AES-256 â€” Supabase managed) | Required (TLS 1.3) | Not currently (future: field-level for high-sensitivity fields) |
| T1 (Restricted) | Required (AES-256 â€” Supabase managed) | Required (TLS 1.3) | Required (bcrypt for passwords, HS256 for tokens) |

### 4.3 Data Retention

| Tier | Default Retention | Minimum | Maximum | Deletion Method |
|---|---|---|---|---|
| T4 (Public) | Indefinite | N/A | N/A | N/A |
| T3 (Internal) | Life of project | 1 year post-project end | Indefinite | Repo deletion |
| T2 (Confidential) | Active user + 90 days | 90 days post-account deletion | Indefinite (active) | Soft delete â†’ hard delete after 90 days |
| T1 (Restricted) | Active session + 30 days | Immediately on revocation | 90 days in secure backup | Cryptographic destruction (overwrite + delete) |

### 4.4 Logging and Audit

| Tier | Audit Required | Retention | Details to Log |
|---|---|---|---|
| T4 (Public) | No | N/A | N/A |
| T3 (Internal) | Recommended | 90 days | Access events, modification |
| T2 (Confidential) | Yes | 1 year | Create, read, update, delete â€” with user_id and timestamp |
| T1 (Restricted) | Yes | 2 years | All access events, with request ID, IP, timestamp, resource ID |

### 4.5 Incident Notification

| Tier | Internal Notification | User Notification | Regulatory Notification |
|---|---|---|---|
| T4 (Public) | Not required | Not required | Not required |
| T3 (Internal) | Within 72 hours | Not required | Not required |
| T2 (Confidential) | Within 4 hours | Within 24 hours | As required by law (GDPR: 72 hours) |
| T1 (Restricted) | Within 1 hour | Within 4 hours | As required by law (GDPR: 72 hours) |

### 4.6 Data Loss Prevention

| Tier | DLP Control | Implementation |
|---|---|---|
| T4 (Public) | None | â€” |
| T3 (Internal) | Git repository access control | GitHub team permissions |
| T2 (Confidential) | RLS policies, user_id filtering | `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;` â€” enforced per table |
| T1 (Restricted) | RLS + environment variable isolation + secret rotation | `.env` excluded from git, `JWT_SECRET` rotated per policy |

---

## 5. Labeling and Metadata Standards

### 5.1 Document Labels

All documents in `docs/` MUST include a classification label in their document control table:

```markdown
| Classification | <Tier Label> |
```

Valid values: `Public`, `Internal`, `Engineering Team`, `Security Team`, `Restricted â€” Internal Only`

### 5.2 Code Labels

| Artifact | Label Location | Example |
|---|---|---|
| Python modules | Module docstring | `""" Task routes â€” Confidential """` |
| API endpoints | Tag metadata | `tags=["tasks"]` + auth dependency |
| Database tables | Table comment | `COMMENT ON TABLE tasks IS 'T2 â€” Confidential';` |
| Environment variables | Naming convention | `SUPABASE_SERVICE_KEY` (T1), `NEXT_PUBLIC_*` (T4) |

### 5.3 Commit and PR Labels

| Label | When to Use |
|---|---|
| `data-classification:T2` | PR modifies Confidential data handling |
| `data-classification:T1` | PR modifies Restricted data handling (secrets, auth) |
| `data-classification:T3` | PR modifies Internal documentation or code |

### 5.4 Metadata Requirements

All artifacts containing T2 or T1 data MUST include:
- **Creation timestamp** (ISO 8601, UTC)
- **Owner** (user_id for user data)
- **Classification marker** (in metadata or adjacent comment)

---

## 6. Data Handling Procedures

### 6.1 Data at Rest

| Procedure | T2 | T1 |
|---|---|---|
| Storage location | Supabase managed db | Supabase db + env vars |
| Encryption | AES-256 (provider-managed) | AES-256 + bcrypt for passwords |
| Backup encryption | AES-256 encrypted backups | AES-256 encrypted, restricted access |
| Indexing | Allowed on non-sensitive columns | Allowed only on non-secret columns |

### 6.2 Data in Transit

| Channel | Protocol | Certificate Validation | Additional Controls |
|---|---|---|---|
| Browser â†” Vercel | TLS 1.3 | Yes (Let's Encrypt) | HSTS preload |
| Vercel â†” Railway | TLS 1.3 | Yes (internal) | Vercel edge network |
| Railway â†” Supabase | TLS 1.3 | Yes (Supabase managed) | IP allowlist |
| Railway â†” Ollama (local) | HTTP (localhost only) | N/A | Loopback only |
| Railway â†” Anthropic API | TLS 1.3 | Yes (Anthropic managed) | API key authentication |

### 6.3 Data in Use

| Control | Implementation |
|---|---|
| Memory isolation | OS-level process isolation (Docker containers) |
| Cache encryption | Redis in-memory cache â€” T2 data has TTL â‰¤ 5 min |
| Log scrubbing | Audit logger redacts T1 fields (passwords, tokens) |
| AI prompt sanitization | User input sanitized before LLM submission (`utils/sanitizer.py`) |

### 6.4 Data Deletion

| Method | When Used | Verification |
|---|---|---|
| Soft delete | User-initiated deletion of T2 data | `deleted_at` timestamp set, data hidden from queries |
| Hard delete | 90 days after soft delete (cron job) | Row physically removed from Supabase |
| Cryptographic destruction | T1 secrets on rotation | Overwritten in env var storage, old JWT signing keys discarded |
| Account deletion | User requests full deletion | All user-scoped T2 + T1 data removed within 30 days |

---

## 7. Roles and Responsibilities

| Role | Responsibilities |
|---|---|
| **Developer (Staff Security Engineer)** | Maintain data inventory; approve classification changes; enforce handling requirements; conduct quarterly classification audit |
| **Data Steward (implicit: Developer)** | Ensure data is classified correctly at creation; apply appropriate handling; report mishandling incidents |
| **CI/CD Pipeline** | Enforce classification labels in PRs; block T1 data from leaking into public artifacts |
| **Code Reviewer** | Verify data classification is appropriate in PR descriptions; flag unclassified data stores |

---

## 8. Compliance Mapping

### 8.1 SOC 2 Mapping

| Trust Service Criterion | Related Classification Tier | Control |
|---|---|---|
| CC6.1 â€” Logical and physical access | T1, T2 | RLS, JWT auth, environment variable isolation |
| CC6.2 â€” Encryption at rest | T1, T2 | Supabase AES-256 |
| CC6.3 â€” Encryption in transit | T1, T2, T3 | TLS 1.3 |
| CC6.5 â€” Vulnerability management | T1, T2 | SAST, DAST, dependency scanning |
| CC7.1 â€” Incident detection | T1, T2 | Sentry, audit logging |

### 8.2 GDPR Mapping

| GDPR Requirement | Affected Tier | Implementation |
|---|---|---|
| Right to access | T2, T1 | `GET /api/v1/data/export` endpoint |
| Right to erasure | T2, T1 | Account deletion + 90-day hard delete cron |
| Data portability | T2 | JSON export of all user data |
| Breach notification | T1, T2 | Incident response plan (SEC-POLICY-IR-001) |
| Data minimization | T2 | Only essential fields collected; no excessive PII |

---

## 9. Training and Awareness

| Audience | Training Topic | Frequency |
|---|---|---|
| Developer | Data classification overview | Onboarding + annually |
| Developer | Handling T1/T2 data securely | Onboarding + annually |
| Developer | Incident reporting for data breaches | Onboarding + annually |

---

## 10. Exceptions and Deviations

| Step | Description | Owner |
|---|---|---|
| 1 | Identify data that cannot be classified according to this policy | Developer |
| 2 | Document rationale for deviation | Developer |
| 3 | Assess risk acceptance with compensating controls | Developer |
| 4 | Approve deviation with expiry date | Developer |
| 5 | Review deviation at next quarterly security review | Developer |

---

## 11. Revision History

| Version | Date | Author | Changes | Approved By |
|---|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial data classification and handling policy | Developer |
