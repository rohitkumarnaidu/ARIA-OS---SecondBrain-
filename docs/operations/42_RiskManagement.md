# Risk Management Plan

## Document Control

| Field | Value |
|---|---|
| Document ID | OPS-RM-001 |
| Version | 1.0.0 |
| Date | 2026-06-11 |
| Status | Draft |
| Classification | Internal â€” Confidential |
| Owner | Solo Developer |
| Framework Reference | ISO 31005:2018, NIST SP 800-30 Rev. 1 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Risk Management Framework](#2-risk-management-framework)
3. [Risk Taxonomy](#3-risk-taxonomy)
4. [Risk Register](#4-risk-register)
5. [Risk Response Strategies](#5-risk-response-strategies)
6. [Risk Treatment Plan](#6-risk-treatment-plan)
7. [Monitoring & Review](#7-monitoring--review)
8. [Risk Reporting](#8-risk-reporting)
9. [AI-Specific Risk Management](#9-ai-specific-risk-management)
10. [Appendices](#10-appendices)
    - [Appendix A: Risk Register Full Table](#appendix-a-risk-register-full-table)
    - [Appendix B: Risk Scoring Matrix](#appendix-b-risk-scoring-matrix)
    - [Appendix C: Risk Treatment Schedule](#appendix-c-risk-treatment-schedule)
    - [Appendix D: Glossary of Terms](#appendix-d-glossary-of-terms)
    - [Appendix E: Revision History](#appendix-e-revision-history)

---

## 1. Executive Summary

### 1.1 Purpose

This Risk Management Plan establishes a systematic framework for identifying, assessing, responding to, and monitoring risks across the Second Brain OS project. The plan ensures that the solo developer can make informed decisions about which risks to accept, mitigate, transfer, or avoid â€” recognizing that a single-developer student project has limited capacity for risk treatment but zero tolerance for catastrophic data loss or security breaches.

### 1.2 Scope

| In Scope | Out of Scope |
|---|---|
| Application code risks (Next.js, FastAPI) | Physical infrastructure risks (data center flood/fire) |
| Database risks (Supabase PostgreSQL, RLS policies) | Force majeure events |
| AI model risks (Ollama local, Claude API) | Geopolitical risks affecting cloud providers |
| Authentication risks (Supabase Auth, JWT) | Legal liability beyond data privacy |
| Deployment risks (Vercel, Railway) | Market competition risks |
| Third-party dependency risks (npm, PyPI) | |
| Data privacy & backup risks | |
| Operational continuity (bus factor, on-call) | |
| Cloud cost overrun risks | |
| AI-specific: hallucination, prompt injection, bias | |

### 1.3 Methodology

This plan follows the **ISO 31005:2018** risk management process (risk identification, analysis, evaluation, treatment, monitoring) mapped to the **NIST SP 800-30 Rev. 1** framework for risk assessment. Risk scoring uses a 5Ã—5 likelihood-impact matrix with discrete numerical values (1â€“5 per axis) to produce a composite score (1â€“25). Qualitative labels (Low, Medium, High, Critical) derive from score ranges.

---

## 2. Risk Management Framework

### 2.1 Governance Structure

Because this is a single-developer project, governance is streamlined:

| Role | Responsibility | Person |
|---|---|---|
| Risk Owner | All risk identification, assessment, treatment, and monitoring | Solo Developer |
| Decision Authority | Risk acceptance decisions, resource allocation for mitigation | Solo Developer |
| Auditor | Periodic self-review of risk controls | Solo Developer (quarterly self-audit) |
| Escalation Point | Not applicable â€” no management chain | N/A |

Governance is enforced through:
- **Automated controls**: CI/CD pipelines (lint, type-check, test), Supabase RLS validation scripts, automated backups
- **Process controls**: Monthly risk review checklist, quarterly full reassessment
- **Documentation**: This plan and risk register maintained in version control alongside code

### 2.2 Risk Appetite

| Domain | Risk Appetite | Rationale |
|---|---|---|
| **Data Loss** | Zero tolerance â€” Avoid | User-generated data (tasks, goals, journals) is irreplaceable. Any permanent data loss is unacceptable |
| **Security Breach** | Zero tolerance â€” Avoid | Credential leaks, auth bypass, or unauthorized data access destroys user trust in a personal AI system |
| **AI Hallucination** | Low tolerance â€” Mitigate | Hallucinated task suggestions or course advice is annoying but not life-critical. Must have clear disclaimers and human-in-the-loop |
| **Service Uptime** | Moderate tolerance â€” Accept | A personal productivity app can have brief downtime (RTO: 2 hours SEV-1). Solo developer cannot guarantee 99.9% uptime |
| **Feature Completeness** | High tolerance â€” Accept | Scope creep is expected. Features ship when ready. Delayed features are acceptable |
| **Cloud Costs** | Low tolerance â€” Monitor | Hard budget cap of â‚¹500/month (~$6 USD). Any cost overrun triggers immediate review |
| **Dependency Vulnerabilities** | Low tolerance â€” Mitigate | `npm audit` and `pip-audit` must pass before merge. Critical CVEs patched within 48 hours |

### 2.3 Risk Scoring Criteria

#### Likelihood (1-5)

| Score | Label | Description | Frequency Guide |
|---|---|---|---|
| 1 | Rare | May occur only in exceptional circumstances | > 2 years |
| 2 | Unlikely | Could occur at some time, but not expected | 6â€“24 months |
| 3 | Possible | Might occur at some point | 1â€“6 months |
| 4 | Likely | Will probably occur in most circumstances | Weeklyâ€“monthly |
| 5 | Almost Certain | Expected to occur repeatedly | Dailyâ€“weekly |

#### Impact (1-5)

| Score | Label | Description | Examples |
|---|---|---|---|
| 1 | Insignificant | Minimal disruption, no data loss, trivial fix | Minor UI bug, cosmetic issue |
| 2 | Minor | Small feature degraded, workaround exists, no data impact | Delayed sync, slow page load |
| 3 | Moderate | Feature unavailable, partial data impact, manual recovery needed | AI agent down, scheduler broken |
| 4 | Major | Core functionality down, data loss limited to one session, reputational damage | Database corruption, auth outage, backup failure |
| 5 | Catastrophic | Complete data loss, security breach, permanent service termination | Credential leak, GDPR violation, total DB loss |

#### Risk Score = Likelihood Ã— Impact

| Score Range | Priority | Color |
|---|---|---|
| 1â€“9 | Low | Green |
| 10â€“14 | Medium | Amber |
| 15â€“19 | High | Orange |
| 20â€“25 | Critical | Red |

---

## 3. Risk Taxonomy

### 3.1 Technical Risks

| Risk ID | Risk Category | Description |
|---|---|---|
| TEC-01 | Infrastructure Failure | Supabase database service degradation or outage. Railway/Vercel build pipeline failures. DNS misconfiguration |
| TEC-02 | Data Loss | Accidental DELETE/UPDATE without WHERE clause. Schema migration data loss. Supabase project suspension due to billing |
| TEC-03 | AI Model Decay | Ollama local model producing degraded responses over time. Claude API model version deprecation breaking prompt formats |
| TEC-04 | API Deprecation | Supabase API version sunset. Claude API endpoint changes breaking agent workflows. Resend API email delivery changes |
| TEC-05 | Dependency Vulnerability | npm package with critical CVE (e.g., next-auth, zod). PyPI package vulnerability (httpx, pydantic). Transitive dependency exploit |
| TEC-06 | TypeScript/React Upgrade Pain | Next.js major version upgrade breaks page router API. React 19 breaking changes. Framer Motion v11 compatibility |
| TEC-07 | Supabase Row-Level Security (RLS) Misconfiguration | Missing or incorrectly scoped RLS policy exposing cross-user data. Policy bypass via service_role key |

### 3.2 Operational Risks

| Risk ID | Risk Category | Description |
|---|---|---|
| OPS-01 | Single-Developer Bus Factor | Developer incapacitated (illness, exam pressure, burnout). No one else can deploy fixes, rotate keys, or restore backups |
| OPS-02 | No On-Call Coverage | Critical incident occurs at 3 AM during exam week. No pager duty, no escalation. Downtime extends to hours or days |
| OPS-03 | No Staging Environment | Production-only deployment means every merge is a risk. Breaking changes affect real users immediately |
| OPS-04 | CI/CD Pipeline Failure | GitHub Actions runner outage, failed deployment blocks hotfixes. Bad merge breaks production build |
| OPS-05 | Documentation Decay | Runbooks, architecture docs, and env setup instructions become stale. Recovery procedures untested |

### 3.3 Security Risks

| Risk ID | Risk Category | Description |
|---|---|---|
| SEC-01 | Credential Leak | `.env` file accidentally committed to public repo. Supabase service_role key or Claude API key exposed in client-side bundle |
| SEC-02 | Authentication Bypass | JWT secret weak or leaked. Supabase Auth misconfiguration allowing email enumeration or session hijacking |
| SEC-03 | Cross-Site Scripting (XSS) | User-generated content rendered without sanitization in task descriptions, note content, or idea vault |
| SEC-04 | CORS Misconfiguration | Overly permissive CORS headers exposing FastAPI backend to untrusted origins |
| SEC-05 | GitHub Token Exposure | CI/CD PAT with write access stored in plaintext. Compromised GitHub Actions workflow exfiltrates secrets |

### 3.4 Business Risks

| Risk ID | Risk Category | Description |
|---|---|---|
| BIZ-01 | Scope Creep | Endless feature additions without completion. 15 modules remain perpetually in "partial" state. No product ships |
| BIZ-02 | Feature Bloat | Too many features added simultaneously. User onboarding becomes confusing. Core value proposition diluted |
| BIZ-03 | User Adoption Failure | No real users beyond the developer. Product is over-engineered for a single user |
| BIZ-04 | Cloud Cost Overrun | Supabase database outgrows free tier. Claude API usage spikes from runaway agents. Ollama GPU compute costs |
| BIZ-05 | Abandonment | Motivation fades after initial excitement. Project joins graveyard of unfinished personal projects on GitHub |

### 3.5 Data Risks

| Risk ID | Risk Category | Description |
|---|---|---|
| DAT-01 | Privacy Breach | Personal data (tasks, journals, habits, sleep logs) accidentally exposed through bug or misconfiguration |
| DAT-02 | GDPR/Regulatory Non-Compliance | User data stored without consent. No data export/deletion mechanism. Failure to comply with India's DPDP Act 2023 |
| DAT-03 | Backup Failure | Automated pg_dump cron fails silently. Backup verification not run. Corrupt backup restored during disaster |
| DAT-04 | Migration Data Loss | Supabase schema migration with destructive column drop. No rollback plan for failed migration |

### 3.6 AI-Specific Risks

| Risk ID | Risk Category | Description |
|---|---|---|
| AI-01 | Model Hallucination | ARIA agent fabricates task suggestions, course recommendations, or productivity advice that is incorrect or harmful |
| AI-02 | Prompt Injection | User injects malicious prompt via task description or note content that manipulates ARIA into executing unintended actions |
| AI-03 | Model Bias | Ollama or Claude generates biased responses in course recommendations or opportunity radar based on skewed training data |
| AI-04 | AI Cost Spikes | Runaway agent loop â€” ARIA enters infinite reflection cycle consuming Claude API tokens. Monthly bill spikes from $0 to $50+ |
| AI-05 | Local AI Unavailability | Ollama service crashes, GPU out of memory, model not loaded. Fallback to Claude API increases cost and latency |

---

## 4. Risk Register

| ID | Category | Risk Description | L | I | Score | Priority | Owner | Mitigation Strategy | Contingency Plan |
|---|---|---|---|---|---|---|---|---|---|
| RISK-001 | Technical | Supabase database corruption or deletion causing permanent data loss | 2 | 5 | 10 | Medium | Developer | Daily automated pg_dump to local + cloud storage. RLS prevents accidental bulk delete | Restore from latest backup. Verify integrity checksums before restoring |
| RISK-002 | Technical | npm/PyPI critical CVE in production dependency exploited | 3 | 4 | 12 | Medium | Developer | Weekly `npm audit` and `pip-audit` in CI. Dependabot alerts enabled. Pin exact versions | Patch within 48 hours. Rollback to previous working version if patch unavailable |
| RISK-003 | Technical | RLS policy gap exposes user data to other users | 2 | 5 | 10 | Medium | Developer | RLS policy review checklist in PR template. Automated test queries for cross-user data access | Revoke service_role key usage. Audit logs to identify exposure scope. Notify affected users |
| RISK-004 | Technical | Next.js major version upgrade breaks existing pages and API routes | 2 | 3 | 6 | Low | Developer | Pin Next.js to stable minor. Run full build + type-check before upgrade. Read changelog for breaking changes | Rollback via Git revert. Maintain working branch on old version |
| RISK-005 | Technical | Supabase API deprecation removes endpoint used by app | 3 | 3 | 9 | Low | Developer | Monitor Supabase changelog and deprecation notices. Abstract Supabase calls behind repository layer | Migrate to new API endpoint. Fallback to direct PostgreSQL queries via pg library |
| RISK-006 | Operational | Developer incapacitated (illness, burnout) â€” no one can maintain the system | 3 | 4 | 12 | Medium | Developer | Document all runbooks, env setup, and recovery procedures. Keep `AGENTS.md` current for AI-assisted recovery | Grant trusted collaborator (GitHub read-only) access. Document emergency key rotation steps |
| RISK-007 | Operational | Production-only deployment â€” untested change breaks core feature | 4 | 3 | 12 | Medium | Developer | Run full test suite + lint + type-check in CI before deploy. Use feature flags for risky changes. Staged rollout via Vercel preview deploys | Revert the deployment. Use Vercel instant rollback to previous stable deploy |
| RISK-008 | Operational | CI/CD pipeline (GitHub Actions) fails blocking all deployments | 3 | 2 | 6 | Low | Developer | Use redundant runner (GitHub hosted). Cache dependencies to reduce flakiness | Re-run failed jobs. If runner outage, deploy manually from local machine |
| RISK-009 | Operational | Automated backup cron fails silently for weeks | 4 | 4 | 16 | High | Developer | Backup job sends success/failure notification to developer email. Weekly manual backup verification | Restore from previous verified backup. Fix cron configuration. Re-run backup |
| RISK-010 | Security | Supabase service_role key or Claude API key committed to public repo | 3 | 5 | 15 | High | Developer | `.env` in `.gitignore`. Pre-commit hook with `git-secrets` or `trufflehog`. No secrets in client-side bundle | Rotate ALL keys immediately. Audit git history with BFG Repo-Cleaner. Revoke exposed keys in Supabase dashboard + Anthropic console |
| RISK-011 | Security | JWT secret weak or exposed â€” unauthorized user gains access to any account | 2 | 5 | 10 | Medium | Developer | Use cryptographically random 256-bit JWT secret stored in Supabase secrets manager. Never log or expose the secret | Rotate JWT secret. Force all sessions to re-authenticate. Audit access logs for unauthorized activity |
| RISK-012 | Security | XSS vulnerability in user-generated content (task descriptions, notes) | 3 | 3 | 9 | Low | Developer | Sanitize all user input with DOMPurify on frontend. Never use `dangerouslySetInnerHTML`. Content Security Policy headers | Patch the vulnerable component. Scan for stored XSS payloads in database |
| RISK-013 | Security | CORS misconfiguration exposes FastAPI backend to untrusted origins | 2 | 3 | 6 | Low | Developer | Explicit allowlist of origins (`http://localhost:3000`, production domain). No wildcard CORS in production | Update CORS configuration. Audit logs for unauthorized cross-origin requests |
| RISK-014 | Business | Scope creep â€” 15 modules remain perpetually in "partial" state, no feature reaches completion | 4 | 3 | 12 | Medium | Developer | Strict MVP prioritization. Complete one module at a time before starting next. Use `IMPLEMENTATION_STATUS.md` to track completion | Quarterly scope review. De-scope underperforming modules. Ship 80% features to production |
| RISK-015 | Business | Cloud cost overrun â€” Claude API or Supabase exceeds free tier budget | 4 | 3 | 12 | Medium | Developer | Set hard monthly budget caps. Monitor costs weekly. Use local Ollama as default AI, Claude only for fallback | Implement token limits per session. Switch fully to Ollama. Rate-limit AI calls |
| RISK-016 | Business | Project abandonment â€” motivation fades, project joins unfinished personal project graveyard | 3 | 4 | 12 | Medium | Developer | Ship working product early (MVP). Real usage creates momentum. Document wins in changelog. Public roadmap for accountability | Accept that the project served its learning purpose. Archive the repo with README |
| RISK-017 | Business | Feature bloat â€” too many features confuse the single user (the developer) | 3 | 2 | 6 | Low | Developer | Keep UI focused: dashboard shows top 5 modules. De-prioritize low-value features. "Done is better than perfect" | Review and remove unused UI sections. Consolidate modules |
| RISK-018 | Data | Privacy breach â€” personal journals, tasks, or habits data exposed through application bug | 2 | 5 | 10 | Medium | Developer | RLS policies on all tables. All queries filtered by `user_id`. No logging of sensitive fields. Audit access regularly | Immediately revoke any exposed access. Identify scope via logs. Notify user of breach. Rotate all credentials |
| RISK-019 | Data | GDPR / DPDP Act non-compliance â€” no data export or deletion mechanism | 3 | 3 | 9 | Low | Developer | Implement "Export My Data" (JSON download) and "Delete My Account" (cascade delete all user rows) endpoints | Provide data deletion within 30 days of request. Manual DB cleanup if automated script fails |
| RISK-020 | Data | Schema migration drops column or table, causing unrecoverable data loss | 2 | 5 | 10 | Medium | Developer | Always backup database before migration. Never DROP column without 2-step: SET DEFAULT NULL first, then DROP in next migration | Restore from pre-migration backup. Re-run migration with corrected schema |
| RISK-021 | AI | ARIA agent hallucinates incorrect academic/career advice | 4 | 3 | 12 | Medium | Developer | Clear disclaimers on all AI-generated content. Human-in-the-loop before any automated action. Confidence scoring on responses | User can dismiss/flag hallucinated content. Log all hallucinations for model improvement |
| RISK-022 | AI | Prompt injection via user-generated content manipulates ARIA into unintended actions | 3 | 4 | 12 | Medium | Developer | Input sanitization before sending to LLM. System prompt with strict role boundaries. Separate user content from instructions | Review agent actions logs. Rate-limit agent-initiated changes. Manual override kill switch |
| RISK-023 | AI | AI cost spike â€” runaway reflection loop consumes $50+ in Claude API tokens in hours | 3 | 4 | 12 | Medium | Developer | Hard token budget per session (e.g., 100K tokens). Max iterations limit (3). Circuit breaker if cost exceeds threshold in 1 hour | Kill all active agent processes. Rotate API key temporarily. Switch to Ollama-only mode |
| RISK-024 | AI | Ollama local model crashes or GPU out-of-memory â€” AI features unavailable | 3 | 2 | 6 | Low | Developer | Graceful fallback to Claude API with user notification. Auto-restart Ollama service. Monitor GPU memory | Restart Ollama process. Reduce model size if OOM persists. Accept degraded AI experience |
| RISK-025 | AI | Model bias in opportunity radar â€” recommendations skewed toward certain fields or demographics | 2 | 3 | 6 | Low | Developer | Diversify prompt examples across fields. Manual review of opportunity radar output. User override on recommendations | Accept that personal AI has inherent bias from single-user training. Document limitations |

---

## 5. Risk Response Strategies

### 5.1 Critical (Score 20â€“25)

*No risks currently score in this range. If any risk reaches Critical, the response is immediate intervention.*

**Strategies:**
1. **Immediate service suspension** â€” Take the affected service offline to prevent further damage
2. **Root cause analysis** â€” Isolate the issue. For data loss: stop all writes. For security breach: rotate all credentials
3. **Emergency restore** â€” Execute disaster recovery plan (SB-DR-001) step by step
4. **Post-mortem within 24 hours** â€” Document what happened, why, and how to prevent recurrence
5. **Re-evaluation of all controls** â€” Full audit of the affected risk category before resuming service

### 5.2 High (Score 15â€“19)

**Strategy: Mitigate / Reduce**

| Strategy ID | Strategy | Applicable Risks | Implementation |
|---|---|---|---|
| H-01 | Automated alerts on backup failure with mandatory verification | RISK-009 | Backup script sends email on failure. Weekly manual checksum verification |
| H-02 | Pre-commit secrets scanning and credential rotation automation | RISK-010 | Install `pre-commit` with `gitleaks` hook. `scripts/rotate_keys.py` for 1-command key rotation |
| H-03 | Runbook documentation with recovery scripts | RISK-006, RISK-009 | Store runbooks in `docs/operations`. Recovery scripts in `scripts/` with `--dry-run` mode |
| H-04 | Feature flags for high-risk deployments | RISK-007 | Use environment variables as feature flags. New features behind `FEATURE_FLAG_*` disabled in production |
| H-05 | Token budget enforcement with circuit breaker | RISK-023 | Implement `MAX_TOKENS_PER_SESSION` and `MAX_AGENT_ITERATIONS` in FastAPI backend. Circuit breaker trips at 80% of monthly budget |

### 5.3 Medium (Score 10â€“14)

**Strategy: Transfer / Share**

| Strategy ID | Strategy | Applicable Risks | Implementation |
|---|---|---|---|
| M-01 | Dependabot + automated patch management | RISK-002 | Enable GitHub Dependabot for npm + pip. Auto-merge only patch versions. Review minor/major |
| M-02 | Supabase point-in-time recovery (PITR) | RISK-001, RISK-020 | Enable Supabase PITR (paid tier) if budget allows. Otherwise, daily encrypted backups to S3-compatible storage |
| M-03 | AI guardrails with input/output validation | RISK-021, RISK-022 | Pydantic models validate all LLM inputs and outputs. System prompt includes: "You are a productivity assistant. Never execute destructive actions" |
| M-04 | Shared repository documentation for bus factor | RISK-006 | Keep `AGENTS.md`, runbooks, and architecture docs in repo. Trusted friend has read-only GitHub access with instructions |
| M-05 | Budget alerts on all cloud services | RISK-015 | Set Supabase spend alerts at $5. Set Anthropic usage limits at $10/month. Weekly cost review in calendar |
| M-06 | RLS policy test suite | RISK-003, RISK-018 | Write integration tests that verify a user cannot access another user's data. Run in CI before deploy |

### 5.4 Low (Score 1â€“9)

**Strategy: Accept / Monitor**

| Strategy ID | Strategy | Applicable Risks | Implementation |
|---|---|---|---|
| L-01 | Pin dependency versions, upgrade on schedule | RISK-004 | Keep Next.js, React, Framer Motion on stable releases. Upgrade during semester breaks |
| L-02 | Monitor Supabase deprecation notices | RISK-005 | Subscribe to Supabase status page + changelog. Quarterly review of deprecated endpoints |
| L-03 | Content Security Policy headers | RISK-012 | Apply `Content-Security-Policy` via Next.js middleware. Allow only same-origin scripts |
| L-04 | Strict CORS allowlist, no wildcards | RISK-013 | FastAPI `CORSMiddleware` with explicit `allow_origins`. Validated in CI |
| L-05 | Track unused features for removal | RISK-017 | Quarterly review of feature usage. Archive low-engagement modules to "stretch goals" in roadmap |
| L-06 | Data export + delete endpoints | RISK-019 | Implement `/api/user/export` and `/api/user/delete` with cascade. Document in privacy policy |

---

## 6. Risk Treatment Plan

### Top 10 Highest-Risk Items Action Plan

| Rank | ID | Score | Treatment Approach | Specific Actions | Timeline | Success Criteria |
|---|---|---|---|---|---|---|
| 1 | RISK-009 | 16 | Mitigate | 1. Add email/webhook notification on backup job failure<br>2. Schedule weekly manual backup verification (calendar reminder every Sunday)<br>3. Add checksum verification to restore script | Week 1: notifications<br>Week 2: verification script<br>Week 3: runbook update | Zero silent backup failures. All backup jobs have delivery confirmation |
| 2 | RISK-010 | 15 | Mitigate | 1. Install `pre-commit` with `gitleaks` hook<br>2. Create `scripts/rotate_keys.py` with Supabase + Anthropic API rotation<br>3. Audit git history with BFG for any exposed secrets<br>4. Add secret scanning to CI pipeline | Week 1: pre-commit + CI scan<br>Week 2: rotation script<br>Week 3: git history audit | No secrets in repo. One-command key rotation in < 5 minutes |
| 3 | RISK-023 | 12 | Mitigate | 1. Implement `MAX_TOKENS_PER_SESSION = 100000` in AI agent config<br>2. Set `MAX_AGENT_ITERATIONS = 3` circuit breaker<br>3. Add Anthropic usage dashboard (cost tracking)<br>4. Auto-disable AI features if daily cost > $2 | Week 1: token limits<br>Week 2: circuit breaker<br>Week 3: monitoring dashboard | AI costs never exceed $10/month. Runaway loops auto-terminate |
| 4 | RISK-006 | 12 | Mitigate | 1. Create `ONBOARDING.md` with full environment setup (5 min)<br>2. Store recovery passwords in encrypted KeePass DB<br>3. Give one trusted friend read-only GitHub access<br>4. Document emergency key rotation in `docs/operations/` | Week 1: onboarding docs<br>Week 2: password manager<br>Week 3: emergency procedures | Another person could restore service within 1 hour using docs |
| 5 | RISK-007 | 12 | Mitigate | 1. Ensure CI runs full test suite before merge<br>2. Enable Vercel preview deployments for all PRs<br>3. Use feature flags for new modules<br>4. Document rollback procedure in runbook | Week 1: CI checks<br>Week 2: preview deploys<br>Week 3: feature flags | Zero production-only bugs. Rollback completes in < 5 minutes |
| 6 | RISK-014 | 12 | Accept/Manage | 1. One module at a time completion policy<br>2. Mark modules "Complete" only when all sub-features ship<br>3. Monthly review of `IMPLEMENTATION_STATUS.md` | Ongoing | At least 2 modules move from âš ï¸ to âœ… per month |
| 7 | RISK-015 | 12 | Mitigate | 1. Set Supabase spend alert at $5<br>2. Default AI to local Ollama, Claude as fallback only<br>3. Weekly cost check in calendar (5 min every Monday) | Week 1: alerts setup<br>Week 2: AI routing config<br>Ongoing: weekly review | Monthly cloud costs stay under â‚¹500 ($6). No surprise bills |
| 8 | RISK-021 | 12 | Mitigate | 1. Add "AI-generated" disclaimer badge on all ARIA suggestions<br>2. Require user confirmation before AI takes actions<br>3. Log all AI responses for quality review<br>4. Confidence threshold: hide suggestions below 60% confidence | Week 1: disclaimers<br>Week 2: confirmation flow<br>Week 3: logging | < 1% of AI suggestions flagged as incorrect by user |
| 9 | RISK-022 | 12 | Mitigate | 1. Input sanitization before LLM prompt construction<br>2. System prompt with strict boundaries: "You cannot delete data, only suggest"<br>3. Rate limit agent-initiated actions (max 5/min)<br>4. Kill-switch endpoint to disable all agent features | Week 1: sanitization<br>Week 2: prompt hardening<br>Week 3: kill switch | Zero successful prompt injection attempts |
| 10 | RISK-001 | 10 | Mitigate | 1. Verify daily backup cron is running<br>2. Test restore on development environment monthly<br>3. Enable Supabase PITR if within budget<br>4. Document restore procedure step-by-step with commands | Week 1: backup verification<br>Weekly: restore test plan<br>Monthly: full DR drill | Restore from backup completed in < 30 minutes. RPO < 24 hours |

---

## 7. Monitoring & Review

### 7.1 Risk Review Cadence

| Risk Priority | Review Frequency | Method | Duration |
|---|---|---|---|
| Critical (20â€“25) | Immediate â€” within 6 hours of identification | Emergency review + post-mortem | As needed |
| High (15â€“19) | Monthly | Risk register review + control effectiveness check | 30 minutes |
| Medium (10â€“14) | Quarterly | Full risk register review + new risk identification | 1 hour |
| Low (1â€“9) | Biannual | Spot-check + update if project context changed | 15 minutes |
| All Risks | Quarterly | Comprehensive risk reassessment + treatment plan update | 2 hours |

### 7.2 Trigger Events for Automatic Risk Review

The following events trigger an immediate ad-hoc risk review regardless of cadence:

1. **Security incident** (any SEV-1 or SEV-2 security event) â€” Full security risk review
2. **Cloud cost anomaly** (monthly bill exceeds â‚¹500 / $6) â€” Cost risk review + budget re-optimization
3. **Third-party API deprecation notice** (Supabase, Anthropic, Vercel, Railway) â€” Technical risk review
4. **Major dependency CVE** (CVSS â‰¥ 7.0 in production dependency) â€” Immediate patch + risk reassessment
5. **Data loss event** (any data loss, even a single row) â€” Full data risk review + backup verification audit
6. **New feature launch** (module moving from âš ï¸ to âœ…) â€” Feature-specific risk assessment
7. **Architecture change** (database schema change, new AI provider, new cloud service) â€” Technical risk review
8. **Development hiatus** (> 14 days no commits) â€” Operational risk review before resuming development

### 7.3 Key Risk Indicators (KRIs)

| KRI | Metric | Threshold | Alert Level | Monitoring Method |
|---|---|---|---|---|
| Backup Failure Rate | Number of failed backup jobs per month | > 0 | High | Backup notification email |
| Database Error Rate | 5xx errors from Supabase / API | > 1% of requests | High | Vercel Analytics / Railway logs |
| AI Token Consumption | Daily Claude API tokens used | > 50,000/day | Medium | Anthropic usage dashboard |
| API Response Time | p95 latency of FastAPI endpoints | > 2000ms | Medium | Vercel Analytics |
| Auth Failure Rate | Failed login attempts per hour | > 10/hour | High | Supabase Auth logs |
| Monthly Cloud Cost | Total spend across all services | > â‚¹500 ($6) | Critical | Provider billing dashboards |
| Dependency Vulnerabilities | Open `npm audit` / `pip-audit` findings | > 0 at High/Critical | High | Dependabot alerts |
| Deployment Failure Rate | Failed Vercel/Railway deploys per month | > 2/month | Low | GitHub Actions + deployment logs |

### 7.4 Escalation Thresholds

| Risk Score | Escalation Action | Response Time | Notification |
|---|---|---|---|
| 1â€“9 | Logged in risk register. No action required | â€” | None |
| 10â€“14 | Add to risk register with treatment plan. Review next quarter | 7 days | Calendar entry for quarterly review |
| 15â€“19 | Create treatment plan with specific actions. Begin mitigation within 48 hours | 48 hours | Email alert to developer |
| 20â€“25 | Immediate service suspension if applicable. Full emergency response. Post-mortem within 24 hours | Immediate | SMS + Email to developer |

---

## 8. Risk Reporting

### 8.1 Standard Risk Report Template

```markdown
# Risk Report â€” [YYYY-MM-DD]

## Summary
- Total risks identified: XX
- Critical: X | High: X | Medium: X | Low: X
- New risks since last report: X
- Risk score trend: â†‘ / â†’ / â†“
- Month-over-month change: +X / -X / 0

## Top 5 Risks by Score
| ID | Risk | Score | Priority | Status | Treatment Progress |
|---|---|---|---|---|---|
| RISK-XXX | ... | XX | High | Open / Mitigated / Closed | % complete |

## Risks Closed This Period
| ID | Risk | Reason for Closure |
|---|---|---|

## New Risks Identified
| ID | Risk | Score | Priority | Planned Treatment |
|---|---|---|---|---|

## Treatment Plan Status
| ID | Treatment Action | Due Date | Status | Notes |
|---|---|---|---|---|

## KRI Dashboard
| KRI | Current Value | Threshold | Status |
|---|---|---|---|
| Backup Failures | 0 | > 0 | âœ… Healthy |
| Monthly Cost | â‚¹XX | â‚¹500 | âœ… / âš ï¸ / ðŸ”´ |

## Action Items
- [ ] Action 1
- [ ] Action 2
```

### 8.2 Distribution & Frequency

| Report Type | Audience | Frequency | Format |
|---|---|---|---|
| Full Risk Register | Self (Developer) | Quarterly | Markdown in repo (`docs/operations/`) |
| Top Risks Summary | Self (Developer) | Monthly | Calendar reminder + checklist |
| KRI Dashboard | Self (Developer) | Weekly (5 min review) | Notion / Todoist checklist |
| Incident-Driven Report | Self (Developer) | Per incident | Post-mortem in `docs/postmortems/` |
| Annual Risk Review | Self (Developer) | Yearly | Full reassessment + strategy update |

### 8.3 Report Storage

All risk reports are stored in the project repository:
- **Risk Register**: `docs/operations/42_RiskManagement.md` (this document)
- **Post-Mortems**: `docs/postmortems/YYYY-MM-DD-incident-title.md`
- **Quarterly Reviews**: `docs/operations/reviews/Q1-2026-risk-review.md`
- **KRI Data**: Tracked via project monitoring dashboards (Supabase logs, Vercel Analytics, Anthropic Console)

---

## 9. AI-Specific Risk Management

### 9.1 Hallucination Guardrails

| Guardrail | Implementation | Location |
|---|---|---|
| Confidence scoring | ARIA assigns 0â€“100 confidence to each suggestion. Below 60: hidden from user | `packages/ai/agents/aria.py` |
| Human-in-the-loop | All AI-initiated actions (task creation, schedule changes) require user confirmation | `apps/web/app/api/aria/confirm/route.ts` |
| Source attribution | AI suggestions cite their source (calendar data, task history, course schedule) | `packages/ai/agents/base.py` |
| Disclaimers | "AI-generated suggestion â€” verify before acting" badge on all AI output | `packages/ui/components/ai-badge.tsx` |
| Hallucination logging | Every AI response logged with user feedback (thumbs up/down) for quality improvement | `packages/ai/audit/logger.py` |
| Response validation | Pydantic models validate AI output structure before it reaches the user | `packages/database/schemas/ai.py` |

### 9.2 Prompt Injection Prevention

| Layer | Control | Implementation |
|---|---|---|
| Input sanitization | Strip control characters, escape special tokens before prompt construction | `packages/ai/security/sanitizer.py` |
| Prompt separation | System prompt, user context, and user query are clearly delimited with XML tags | `packages/ai/prompts/templates/` |
| Output boundary | Strict system instruction: "You are a productivity assistant. You cannot execute database operations. You can only suggest actions to the user." | `packages/ai/agents/system-prompt.txt` |
| Rate limiting | Max 5 agent-initiated actions per minute. Max 100 agent calls per hour | `packages/shared/utils/rate_limiter.py` |
| Action audit log | All agent-initiated state changes logged with before/after diff | `packages/ai/audit/action_log.py` |
| Kill switch | `POST /api/aria/disable` immediately halts all agent processing | `apps/api/app/api/aria/control.py` |

### 9.3 Model Bias Mitigation

| Approach | Implementation |
|---|---|
| Diverse prompt examples | Opportunity radar prompts include examples from tech, healthcare, education, finance, creative fields | `packages/ai/agents/opportunity_radar.py` |
| User override | Opportunity radar includes "Show more like this" and "Not relevant" feedback loop | `apps/web/app/opportunities/page.tsx` |
| Bias audit logging | All AI recommendations logged with category distribution. Monthly review for skewed distributions | `packages/ai/audit/bias_monitor.py` |
| Local model diversity | When using Ollama, rotate between available models (llama3, mistral, phi3) to reduce single-model bias | `services/scheduler/config/ai.py` |

### 9.4 Cost Containment

| Control | Configuration | Enforcement |
|---|---|---|
| Token budget per session | `MAX_TOKENS_PER_SESSION = 100000` | Backend refuses new requests if exceeded |
| Hard monthly spend cap | Anthropic API: $10/month | Billing alerts at 50%, 80%, 100% |
| Max iterations per agent | `MAX_AGENT_ITERATIONS = 3` | Circuit breaker terminates runaway loops |
| Default AI mode | Local Ollama first, Claude API as fallback | Application config: `USE_LOCAL_AI=True` |
| Token tracking middleware | Every API call to Claude logs token count | `packages/ai/middleware/token_tracker.py` |
| Usage dashboard | `/api/admin/costs` returns current month spend | `apps/api/app/api/admin/costs.py` |

```python
# apps/api/app/api/ai/config.py
AI_CONFIG = {
    "provider": "ollama",          # default: local
    "fallback_provider": "claude", # if ollama unavailable
    "max_tokens_per_session": 100_000,
    "max_agent_iterations": 3,
    "monthly_budget_usd": 10.0,
    "daily_alert_threshold_usd": 2.0,
    "circuit_breaker_token_spike": 50_000,  # tokens in 5 minutes
    "allowed_models": ["claude-sonnet-4", "claude-haiku-4"],
}
```

### 9.5 Data Privacy in AI Context

| Risk | Control |
|---|---|
| User data sent to third-party AI (Claude API) | All PII (names, emails) stripped before sending to Claude. Use anonymous IDs |
| Local model (Ollama) stores data on disk | Ollama runs with `--no-keepalive` to clear context after each session |
| AI training on user data | Verify Anthropic API calls do not opt into training. Set `anthropic-version` header. Anthropic does NOT train on API inputs by default |
| Sensitive data in prompts | System prompt instructs model: "Do not repeat user's personal information in responses" |
| Data retention | Chat history stored locally in Supabase with `user_id` scope. User can delete chat history |

---

## 10. Appendices

### Appendix A: Risk Register Full Table

| ID | Category | Risk Description | L | I | Score | Priority | Owner | Mitigation | Contingency |
|---|---|---|---|---|---|---|---|---|---|
| RISK-001 | Technical | Supabase database corruption or deletion â€” permanent data loss | 2 | 5 | 10 | Medium | Developer | Daily pg_dump to cloud storage. RLS prevents bulk delete | Restore from latest backup with integrity check |
| RISK-002 | Technical | npm/PyPI critical CVE exploited in production | 3 | 4 | 12 | Medium | Developer | Weekly audit in CI. Dependabot alerts. Pin versions | Patch within 48h. Rollback if unavailable |
| RISK-003 | Technical | RLS policy gap exposes cross-user data | 2 | 5 | 10 | Medium | Developer | RLS review in PR template. Cross-user test queries | Revoke service_role key. Audit scope. Notify |
| RISK-004 | Technical | Next.js major upgrade breaks routes | 2 | 3 | 6 | Low | Developer | Pin to stable minor. Full build before upgrade | Git revert. Maintain old version branch |
| RISK-005 | Technical | Supabase API deprecation removes endpoint | 3 | 3 | 9 | Low | Developer | Monitor changelog. Repository layer abstraction | Migrate to new endpoint. Fallback to direct pg |
| RISK-006 | Operational | Developer incapacitated â€” no maintenance possible | 3 | 4 | 12 | Medium | Developer | Document runbooks. AGENTS.md for AI recovery | Trusted collaborator read-only access |
| RISK-007 | Operational | Production-only deployment breaks core feature | 4 | 3 | 12 | Medium | Developer | Full CI checks. Preview deploys. Feature flags | Vercel instant rollback |
| RISK-008 | Operational | CI/CD pipeline fails blocking deploys | 3 | 2 | 6 | Low | Developer | Redundant runners. Dependency caching | Manual deploy from local |
| RISK-009 | Operational | Backup cron fails silently for weeks | 4 | 4 | 16 | High | Developer | Email notification on failure. Weekly verification | Restore from previous verified backup |
| RISK-010 | Security | Service_role key or API key committed to repo | 3 | 5 | 15 | High | Developer | pre-commit gitleaks. CI secret scan. env in gitignore | Rotate ALL keys. BFG git history clean |
| RISK-011 | Security | Weak JWT secret â€” unauthorized account access | 2 | 5 | 10 | Medium | Developer | 256-bit random secret in Supabase secrets. No logging | Rotate secret. Force re-auth. Audit logs |
| RISK-012 | Security | XSS in user-generated content | 3 | 3 | 9 | Low | Developer | DOMPurify sanitization. CSP headers. No dangerouslySetInnerHTML | Patch component. Scan for stored payloads |
| RISK-013 | Security | CORS misconfiguration exposes backend | 2 | 3 | 6 | Low | Developer | Explicit origin allowlist. No wildcard CORS | Update config. Audit cross-origin requests |
| RISK-014 | Business | Scope creep â€” modules perpetually partial | 4 | 3 | 12 | Medium | Developer | One module at a time. Status tracking. Quarterly scope review | De-scope underperformers. Ship 80% features |
| RISK-015 | Business | Cloud cost exceeds â‚¹500/month budget | 4 | 3 | 12 | Medium | Developer | Budget alerts. Local AI default. Weekly cost review | Full Ollama switch. Rate-limit AI calls |
| RISK-016 | Business | Project abandonment â€” motivation fades | 3 | 4 | 12 | Medium | Developer | Ship MVP early. Public roadmap. Document wins | Archive repo with README |
| RISK-017 | Business | Feature bloat confuses single user | 3 | 2 | 6 | Low | Developer | Focused dashboard. De-prioritize low-value features | Remove unused sections |
| RISK-018 | Data | Privacy breach â€” personal data exposed via bug | 2 | 5 | 10 | Medium | Developer | RLS on all tables. user_id filtering. No sensitive field logging | Revoke access. Log audit. Notify. Rotate creds |
| RISK-019 | Data | GDPR/DPDP Act non-compliance | 3 | 3 | 9 | Low | Developer | Export data endpoint. Delete account endpoint | Manual cleanup within 30 days |
| RISK-020 | Data | Schema migration drops column causing data loss | 2 | 5 | 10 | Medium | Developer | Backup before migration. Two-step column removal | Restore from pre-migration backup |
| RISK-021 | AI | ARIA hallucinates incorrect advice | 4 | 3 | 12 | Medium | Developer | Disclaimers. Human-in-the-loop. Confidence scoring | User dismiss/flag. Log for improvement |
| RISK-022 | AI | Prompt injection via user content | 3 | 4 | 12 | Medium | Developer | Input sanitization. Strict system prompt. Rate limits | Review action logs. Kill switch |
| RISK-023 | AI | AI cost spike â€” runaway loop consumes $50+ | 3 | 4 | 12 | Medium | Developer | Token budget per session. Max 3 iterations. Circuit breaker | Kill agent processes. Rotate key. Ollama-only |
| RISK-024 | AI | Ollama crash / OOM â€” AI features unavailable | 3 | 2 | 6 | Low | Developer | Graceful fallback to Claude. Auto-restart. GPU monitor | Restart Ollama. Reduce model size |
| RISK-025 | AI | Model bias in opportunity radar recommendations | 2 | 3 | 6 | Low | Developer | Diverse prompt examples. User feedback loop. Bias audit logging | Accept limitations. Document bias sources |

### Appendix B: Risk Scoring Matrix (5Ã—5 Heat Map)

| Likelihood \ Impact | 1 â€” Insignificant | 2 â€” Minor | 3 â€” Moderate | 4 â€” Major | 5 â€” Catastrophic |
|---|---|---|---|---|---|
| **5 â€” Almost Certain** | 5 Low | 10 Medium | 15 High | 20 Critical | 25 Critical |
| **4 â€” Likely** | 4 Low | 8 Low | 12 Medium | 16 High | 20 Critical |
| **3 â€” Possible** | 3 Low | 6 Low | 9 Low | 12 Medium | 15 High |
| **2 â€” Unlikely** | 2 Low | 4 Low | 6 Low | 8 Low | 10 Medium |
| **1 â€” Rare** | 1 Low | 2 Low | 3 Low | 4 Low | 5 Low |

**Color Legend:**

| Score | Priority | Action |
|---|---|---|
| 20â€“25 | ðŸ”´ Critical | Immediate action. Service suspension if needed. Emergency response |
| 15â€“19 | ðŸŸ  High | Mitigation within 48 hours. Treatment plan required |
| 10â€“14 | ðŸŸ¡ Medium | Treatment plan within 7 days. Monitor quarterly |
| 1â€“9 | ðŸŸ¢ Low | Accept. Monitor on regular cadence |

**Current Risk Distribution on Matrix:**

```
                 Impact â†’
                 1     2     3     4     5
               +-----+-----+-----+-----+-----+
Likelihood   5 |     |     |     |     |     |
     â†“         +-----+-----+-----+-----+-----+
             4 |     |     |014  |009  |     |
               |     |     |015  |     |     |
               |     |     |007  |     |     |
               +-----+-----+-----+-----+-----+
             3 |     |008  |005  |006  |010  |
               |     |013  |002  |016  |     |
               |     |017  |021  |022  |     |
               |     |024  |012  |023  |     |
               |     |025  |019  |     |     |
               +-----+-----+-----+-----+-----+
             2 |     |004  |     |020  |001  |
               |     |     |     |018  |003  |
               |     |     |     |011  |     |
               +-----+-----+-----+-----+-----+
             1 |     |     |     |     |     |
               +-----+-----+-----+-----+-----+
```

### Appendix C: Risk Treatment Schedule

```mermaid
gantt
    title Risk Treatment Plan Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Week 1 (Jun 12â€“18)
    RISK-009: Add backup failure notifications       :active, r9a, 2026-06-12, 3d
    RISK-010: Install pre-commit + gitleaks           :active, r10a, 2026-06-12, 2d
    RISK-023: Implement MAX_TOKENS_PER_SESSION        :active, r23a, 2026-06-14, 3d
    RISK-006: Create ONBOARDING.md                    :active, r6a, 2026-06-14, 2d
    RISK-015: Set Supabase spend alert at $5          :active, r15a, 2026-06-12, 1d
    RISK-007: Ensure CI runs full test suite          :active, r7a, 2026-06-12, 3d
    RISK-021: Add AI disclaimer badges                :active, r21a, 2026-06-13, 3d
    RISK-022: Input sanitization for LLM prompts      :active, r22a, 2026-06-14, 3d
    RISK-001: Verify daily backup cron is running      :active, r1a, 2026-06-12, 1d

    section Week 2 (Jun 19â€“25)
    RISK-009: Weekly verification script              :active, r9b, 2026-06-19, 4d
    RISK-010: Create rotate_keys.py                   :active, r10b, 2026-06-19, 3d
    RISK-023: Circuit breaker implementation          :active, r23b, 2026-06-19, 3d
    RISK-006: Store passwords in encrypted DB          :active, r6b, 2026-06-19, 2d
    RISK-007: Enable Vercel preview deploys           :active, r7b, 2026-06-19, 3d
    RISK-015: Configure Ollama as default AI           :active, r15b, 2026-06-19, 2d
    RISK-021: User confirmation flow for AI actions    :active, r21b, 2026-06-19, 3d
    RISK-022: Strict system prompt hardening           :active, r22b, 2026-06-19, 3d
    RISK-001: Test restore on dev environment          :active, r1b, 2026-06-22, 4d

    section Week 3 (Jun 26â€“Jul 2)
    RISK-009: Checksum verification + runbook          :active, r9c, 2026-06-26, 4d
    RISK-010: Git history audit with BFG              :active, r10c, 2026-06-26, 3d
    RISK-023: Cost monitoring dashboard                :active, r23c, 2026-06-26, 4d
    RISK-006: Emergency procedures documented          :active, r6c, 2026-06-26, 3d
    RISK-007: Feature flags for new modules            :active, r7c, 2026-06-26, 4d
    RISK-021: AI response logging implementation       :active, r21c, 2026-06-26, 3d
    RISK-022: Rate limit + kill switch                 :active, r22c, 2026-06-26, 4d

    section Ongoing
    Weekly cost review (5 min every Monday)            :active, ongoing1, 2026-06-12, 90d
    Monthly risk review (High risks)                   :active, ongoing2, 2026-06-26, 90d
    Quarterly full risk reassessment                   :milestone, Q3, 2026-09-12, 0d
```

**Timeline Notes:**
- Week 1 focuses on immediate detections (backup, secret scanning, token limits)
- Week 2 implements the core controls (verification scripts, circuit breakers, AI guardrails)
- Week 3 hardens and documents everything (runbooks, monitoring, kill switches)
- Ongoing activities run perpetually with weekly/monthly/quarterly cadences

### Appendix D: Glossary of Terms

| Term | Definition |
|---|---|
| **ARIA** | AI-powered agent within Second Brain OS. Provides task suggestions, daily briefings, opportunity radar, and other AI features |
| **Bus Factor** | The minimum number of team members that need to be hit by a bus (or become unavailable) before the project stalls |
| **CORS** | Cross-Origin Resource Sharing. HTTP header mechanism that allows a server to indicate which origins are permitted to load resources |
| **CVE** | Common Vulnerability and Exposures. Publicly disclosed cybersecurity vulnerabilities |
| **CVSS** | Common Vulnerability Scoring System. Open standard for communicating severity of vulnerabilities (0â€“10 scale) |
| **DPDP Act** | India's Digital Personal Data Protection Act, 2023. Regulates processing of digital personal data |
| **GDPR** | General Data Protection Regulation. EU regulation on data protection and privacy |
| **JWT** | JSON Web Token. Compact URL-safe token format used for authentication |
| **KRI** | Key Risk Indicator. Metric used to signal increasing risk exposure |
| **LLM** | Large Language Model. AI model used for natural language understanding and generation |
| **Ollama** | Local LLM runtime. Enables running AI models on local hardware without cloud dependency |
| **PITR** | Point-in-Time Recovery. Database recovery capability that restores to any point within a retention window |
| **Pydantic** | Python library for data validation using type annotations. Used for API request/response schemas |
| **RLS** | Row-Level Security. PostgreSQL/Supabase feature that restricts which rows a user can access |
| **RPO** | Recovery Point Objective. Maximum acceptable data loss measured in time (e.g., 24 hours) |
| **RTO** | Recovery Time Objective. Maximum acceptable time to restore service after an incident |
| **Service Key** | Supabase service_role key. Has elevated privileges bypassing RLS. Must be kept secret |
| **XSS** | Cross-Site Scripting. Security vulnerability where attackers inject malicious scripts into web pages |

### Appendix E: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial risk management plan â€” 25 risks identified across 6 categories. Full treatment plan for top 10 risks |
