# GDPR Article 30 Record of Processing Activities (ROPA)

## Document Control

| Field | Value |
|---|---|
| **Document ID** | COMP-GDPR-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | Restricted |
| **Last Updated** | 2026-07-10 |
| **Next Review** | 2026-10-10 |
| **Owner** | Data Protection Officer |
| **Approved By** | Developer |
| **Related Documents** | SEC-046 Data Privacy & GDPR Compliance, COMP-DPIA-001, SEC-POLICY-VULN-001 |

---

## 1. Data Controller Information

| Field | Value |
|---|---|
| **Controller Name** | Second Brain OS (ARIA OS) |
| **Controller Type** | Individual Developer (Sole Proprietor) |
| **Developer** | BTech CSE Student, India |
| **DPO Contact** | dpo@secondbrainos.app |
| **Grievance Officer** | grievances@secondbrainos.app |
| **Registered Address** | India (individual developer â€” no registered office) |
| **Representative in EU** | Not appointed (individual developer, no EU establishment) |
| **Data Protection Framework** | GDPR (Art. 2 â€” personal/household exemption may apply; compliance pursued voluntarily) |
| **Supervisory Authority** | Lead DPA based on user location; Data Protection Commission (Ireland) if EU establishment |

---

## 2. Processing Activities Table

### Activity 1: Account Management & Authentication

| Field | Details |
|---|---|
| **Name** | Account Management & Authentication |
| **Purpose** | Create and maintain user accounts, authenticate users, manage sessions |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) â€” necessary for service delivery |
| **Data Subjects** | Registered users |
| **Data Categories** | Identity (name, email, avatar), Authentication (tokens, OAuth IDs) |
| **Recipients** | Supabase (database), Google (OAuth provider) |
| **Retention** | Until account deletion; tokens until expiry |
| **Security Measures** | TLS 1.3, JWT (HS256), RLS, bcrypt password hashing, rate limiting |

### Activity 2: Task Management

| Field | Details |
|---|---|
| **Name** | Task Management |
| **Purpose** | Create, track, and complete personal tasks with priorities and deadlines |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) â€” core service functionality |
| **Data Subjects** | Registered users |
| **Data Categories** | Task title, description, due date, priority, status, tags, category, recurrence, dependencies |
| **Recipients** | Supabase (database), Vercel (frontend hosting), Railway (backend hosting) |
| **Retention** | Completed + 90 days active, archived 1 year, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, rate limiting, audit logging |

### Activity 3: Habit Tracking

| Field | Details |
|---|---|
| **Name** | Habit Tracking & Streak Management |
| **Purpose** | Define habits, track daily completion, maintain streak counts |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) |
| **Data Subjects** | Registered users |
| **Data Categories** | Habit name, frequency, streak count, reminders, start date, completion logs, dates |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | Habits: current + 1 year; Habit logs: 1 year |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest |

### Activity 4: Goal & Project Management

| Field | Details |
|---|---|
| **Name** | Goal & Project Management |
| **Purpose** | Set goals with milestones, manage projects with phases and blockers |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) |
| **Data Subjects** | Registered users |
| **Data Categories** | Goal title, description, target date, progress, milestones; Project name, description, status, timeline, links, blockers |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | Until completion + 1 year, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, audit logging |

### Activity 5: Course & Learning Progress Tracking

| Field | Details |
|---|---|
| **Name** | Course & Learning Progress Tracking |
| **Purpose** | Track enrolled courses, progress, notes, and learning metrics |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) |
| **Data Subjects** | Registered users |
| **Data Categories** | Course name, provider, progress percentage, notes, resources, learning metrics snapshots |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | Until completion + 1 year, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest |

### Activity 6: Financial Tracking

| Field | Details |
|---|---|
| **Name** | Financial Tracking (Income) |
| **Purpose** | Log income entries, track hourly rates, generate financial insights |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) + Legal Obligation (Art. 6(1)(c)) â€” Indian income tax law |
| **Data Subjects** | Registered users |
| **Data Categories** | Amount, date, source, description, hourly rate |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | 7 years (Indian income tax law â€” Sec. 44AA, Rule 6F) |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, column-level encryption for amounts (pgcrypto) |

### Activity 6: Sleep Tracking

| Field | Details |
|---|---|
| **Name** | Sleep Tracking & Analysis |
| **Purpose** | Log sleep patterns, calculate sleep debt, generate wind-down messages |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) |
| **Data Subjects** | Registered users |
| **Data Categories** | Sleep time, wake time, duration, quality rating, notes, sleep debt |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | Current + 1 year, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest |

### Activity 7: Time Tracking

| Field | Details |
|---|---|
| **Name** | Time Tracking & Pomodoro |
| **Purpose** | Log time entries, track deep work sessions, Pomodoro timer |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) |
| **Data Subjects** | Registered users |
| **Data Categories** | Start time, end time, duration, task/project link, session type |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | 2 years, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest |

### Activity 8: Idea & Resource Management

| Field | Details |
|---|---|
| **Name** | Idea & Resource Management |
| **Purpose** | Capture ideas, bookmark resources, organize with tags |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) |
| **Data Subjects** | Registered users |
| **Data Categories** | Idea title, description, tags, stage; Resource URL, title, description, tags, category |
| **Recipients** | Supabase, Vercel, Railway |
| **Retention** | Ideas: until archived + 1 year; Resources: indefinite (user-controlled) |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest |

### Activity 9: Opportunity Radar

| Field | Details |
|---|---|
| **Name** | Opportunity Radar & Matching |
| **Purpose** | Detect and match opportunities (jobs, internships, projects) to user skills and interests |
| **Legal Basis (Art. 6)** | Consent (Art. 6(1)(a)) â€” explicit opt-in required |
| **Data Subjects** | Registered users (opt-in) |
| **Data Categories** | Skills, interests, enrolled courses, past projects, opportunity title, description, source, match score |
| **Recipients** | Supabase, Vercel, Railway, Claude API (if cloud AI enabled) |
| **Retention** | Until archived + 1 year, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, opt-in consent, data minimization |

### Activity 10: AI Chat & Conversation

| Field | Details |
|---|---|
| **Name** | AI Chat & Conversation |
| **Purpose** | Provide conversational AI assistant for productivity, learning, and general queries |
| **Legal Basis (Art. 6)** | Contract (Art. 6(1)(b)) for local AI; Consent (Art. 6(1)(a)) for cloud AI (Claude API) |
| **Data Subjects** | Registered users |
| **Data Categories** | User message text, AI response text, timestamps, session ID, conversation context |
| **Recipients** | Supabase (storage), Ollama (local â€” no data leaves machine), Claude API (Anthropic â€” if cloud AI enabled) |
| **Retention** | Last 500 messages active; full history archived 5 years |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, opt-in consent for cloud AI, data minimization (last N messages sent) |

### Activity 11: AI Briefing Generation

| Field | Details |
|---|---|
| **Name** | AI Briefing Generation (Daily & Weekly) |
| **Purpose** | Generate AI-powered daily and weekly summaries of tasks, habits, sleep, and goals |
| **Legal Basis (Art. 6)** | Consent (Art. 6(1)(a)) â€” explicit opt-in required |
| **Data Subjects** | Registered users (opt-in) |
| **Data Categories** | Task data, habit data, sleep logs, goals, generated briefing text |
| **Recipients** | Supabase (storage), Ollama (local â€” no data leaves machine), Claude API (Anthropic â€” if cloud AI enabled) |
| **Retention** | 90 days, then hard deleted |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, opt-in consent, data minimization (only recent data sent) |

### Activity 12: Memory Consolidation

| Field | Details |
|---|---|
| **Name** | AI Memory Consolidation |
| **Purpose** | Extract and store user preferences, patterns, and insights from chat and activity data |
| **Legal Basis (Art. 6)** | Consent (Art. 6(1)(a)) â€” AI feature opt-in |
| **Data Subjects** | Registered users (opt-in) |
| **Data Categories** | User preferences, behavioral patterns, learning insights, extracted knowledge |
| **Recipients** | Supabase (storage), Ollama (local), Claude API (if cloud AI enabled) |
| **Retention** | Until user deletes or account deletion |
| **Security Measures** | RLS, user_id filtering, TLS 1.3, AES-256 at rest, opt-in consent, data minimization |

### Activity 13: Usage Analytics & Monitoring

| Field | Details |
|---|---|
| **Name** | Usage Analytics & System Monitoring |
| **Purpose** | Product improvement, bug detection, security monitoring, capacity planning |
| **Legal Basis (Art. 6)** | Legitimate Interest (Art. 6(1)(f)) â€” product improvement, security operations |
| **Data Subjects** | Registered users |
| **Data Categories** | Page views, feature usage, click events, session duration, IP address, user agent, browser/OS info |
| **Recipients** | Supabase (storage), Sentry (error tracking), Vercel (edge analytics) |
| **Retention** | Raw: 30 days; Aggregated (anonymized): 12 months; Error logs: 30 days |
| **Security Measures** | Data anonymization after 30 days, IP truncation, opt-out available, RLS |

### Activity 12: Email Notifications

| Field | Details |
|---|---|
| **Name** | Email Notification Delivery |
| **Purpose** | Send task reminders, briefing digests, account notifications |
| **Legal Basis (Art. 6)** | Consent (Art. 6(1)(a)) for non-essential; Contract (Art. 6(1)(b)) for transactional emails |
| **Data Subjects** | Registered users (opt-in for non-essential) |
| **Data Categories** | Email address, email content, delivery status, timestamps |
| **Recipients** | Resend (email delivery), Supabase (email logs) |
| **Retention** | 90 days (email logs) |
| **Security Measures** | TLS 1.3, Resend SOC 2 compliance, data minimization (only necessary fields) |

### Activity 13: Security Monitoring & Logging

| Field | Details |
|---|---|
| **Name** | Security Monitoring & Audit Logging |
| **Purpose** | Detect security incidents, maintain audit trail, debug issues |
| **Legal Basis (Art. 6)** | Legitimate Interest (Art. 6(1)(f)) â€” security operations |
| **Data Subjects** | Registered users |
| **Data Categories** | IP address, user agent, request path, timestamps, error messages, audit events |
| **Recipients** | Supabase (storage), Sentry (error tracking), Vercel (edge logs) |
| **Retention** | Error logs: 30 days; Audit logs: 1 year; Sentry: 90 days |
| **Security Measures** | Data minimization (no PII in logs where avoidable), IP truncation, access controls, audit trail |

---

## 3. Data Categories by Table

| Table | Data Categories | Classification | Retention | RLS Enabled |
|---|---|---|---|---|
| `users` | Identity (name, email, avatar), preferences, consent records | Confidential | Until account deletion | âœ… |
| `tasks` | Productivity (title, description, due date, priority, status, tags, category, recurrence, dependencies) | Confidential | Completed + 90d active, 1y archived | âœ… |
| `courses` | Course name, provider, progress, notes, resources, deadlines | Confidential | Until completion + 1y | âœ… |
| `goals` | Title, description, target date, progress, milestones | Confidential | Until completion + 1y | âœ… |
| `habits` | Name, frequency, streak count, reminders, start date | Confidential | Current + 1y | âœ… |
| `habit_logs` | Date, completion status, notes | Confidential | 1 year | âœ… |
| `sleep_logs` | Sleep time, wake time, duration, quality rating, notes, sleep debt | Restricted | Current + 1y | âœ… |
| `income_entries` | Amount, date, source, description, hourly rate | Restricted | 7 years (tax) | âœ… |
| `projects` | Name, description, status, timeline, links, blockers | Confidential | Until completion + 1y | âœ… |
| `ideas` | Title, description, tags, stage | Confidential | Until archived + 1y | âœ… |
| `resources` | URL, title, description, tags, category | Confidential | Indefinite (user-controlled) | âœ… |
| `opportunities` | Title, description, source, status, deadline, match score | Confidential | Until archived + 1y | âœ… |
| `time_entries` | Start time, end time, duration, task/project link, session type | Confidential | 2 years | âœ… |
| `chat_messages` | User message, AI response, timestamp, session ID | Restricted | Last 500 active; 5y archived | âœ… |
| `daily_briefings` | Generated briefing text, date, metrics | Restricted | 90 days | âœ… |
| `weekly_reviews` | Generated review text, week range, metrics | Restricted | 90 days | âœ… |
| `memory` | User preferences, behavioral patterns, extracted knowledge | Restricted | Until user deletion | âœ… |
| `learning_progress` | Learning metrics snapshots, course progress, skill levels | Confidential | Until completion + 1y | âœ… |

---

## 4. Third-Party Processors

| Processor | Service | Data Accessed | Location | Certifications | DPA Status | Sub-Processors |
|---|---|---|---|---|---|---|
| **Supabase** | PostgreSQL database, Authentication, Storage | All user data (tasks, habits, income, chat, etc.) | US (us-east-1) / EU (eu-west-1) / India (ap-south-1) | SOC 2 Type II, ISO 27001 | âœ… Executed | AWS |
| **Vercel** | Frontend hosting, CDN, Edge Network | IP address, user agent, request metadata | Global edge (100+ locations) | SOC 2 Type II, ISO 27001 | âœ… Executed | AWS, Cloudflare |
| **Railway** | Backend hosting (FastAPI) | Transient API request data, env vars | US (us-west-1) | SOC 2 Type II (planned 2026) | ðŸŸ¡ Requested | AWS |
| **Ollama (Local)** | Local AI inference | Chat messages, conversation context | User's local machine | N/A â€” no data transmitted | N/A | None |
| **Claude API (Anthropic)** | Cloud AI inference | Chat messages, conversation context | US | SOC 2 Type II, ISO 27001 | âœ… Executed | AWS, GCP |
| **Resend** | Email delivery | Email address, content, metadata | US (us-east-1) | SOC 2 Type II | âœ… Executed | AWS |
| **GitHub** | Source code hosting, CI/CD, issue tracking | Code, CI logs, issue metadata | Global (GitHub-managed) | SOC 2 Type II, ISO 27001 | âœ… Executed | Microsoft Azure |
| **Sentry** | Error tracking, performance monitoring | Error stack traces, request metadata, user ID (configurable) | US (us-east-1) | SOC 2 Type II, ISO 27001, HIPAA | âœ… Executed | AWS, GCP |

---

## 4. International Transfers Assessment

| Transfer | From | To | Mechanism | Adequacy | Risk |
|---|---|---|---|---|---|
| User data â†’ Supabase | India / EU | US (us-east-1) | SCCs (Supabase DPA) | Adequacy decision (US Data Privacy Framework) | Low |
| User data â†’ Vercel | India / EU | Global edge (100+ PoPs) | SCCs (Vercel DPA) | Adequacy decision + SCCs | Low |
| User data â†’ Railway | India / EU | US (us-west-1) | SCCs (Railway DPA) | Adequacy decision | Low |
| Chat messages â†’ Anthropic | India / EU | US | SCCs (Anthropic DPA) | Adequacy decision + SCCs | Low |
| Email data â†’ Resend | India / EU | US (us-east-1) | SCCs (Resend DPA) | Adequacy decision | Low |
| Identity â†’ Google OAuth | India / EU | Global | Google's DPA (Workspace) | Adequacy decision | Low |
| Error data â†’ Sentry | India / EU | US (us-east-1) | SCCs (Sentry DPA) | Adequacy decision | Low |

**Assessment:** All international transfers are covered by either:
- **Adequacy decision**: EU-US Data Privacy Framework (for US-based processors)
- **Standard Contractual Clauses (SCCs)**: Included in all processor DPAs
- **Binding Corporate Rules**: Not applicable (single developer)

**Risk rating:** Low â€” all processors have SOC 2 Type II certification and executed DPAs with SCCs.

---

## 5. Security Measures â€” Technical & Organizational

### Technical Measures

| Measure | Implementation | Standard |
|---|---|---|
| Encryption at rest | Supabase PostgreSQL AES-256 | ISO 27001 |
| Encryption in transit | TLS 1.3 (Vercel + Railway edge) | PCI DSS |
| Access control | Row-Level Security (RLS) on all tables | SOC 2 CC6 |
| Authentication | JWT (HS256) + Google OAuth 2.0 | OAuth 2.0 |
| Authorization | `user_id` filter on all queries | SOC 2 CC5 |
| Rate limiting | 100 req/min per IP (configurable) | NIST SP 800-63 |
| Input validation | Pydantic schemas on all endpoints | OWASP ASVS |
| Audit logging | Structured JSON logs with request IDs | SOC 2 PI1.4 |
| SQL injection protection | Supabase SDK parameterized queries | OWASP ASVS |
| CORS | Whitelist of allowed origins | OWASP ASVS |
| Session management | HTTP-only cookies, short-lived JWTs (1h access, 30d refresh) | OWASP ASVS |
| DDoS protection | Vercel + Railway edge protection | Platform-level |
| Secret management | Environment variables, never in code | OWASP ASVS |
| Input validation | Pydantic schemas on all endpoints | OWASP ASVS |

### Organizational Measures

| Measure | Description | Status |
|---|---|---|
| Data protection training | Self-study: GDPR, DPDP Act, OWASP Top 10 | Quarterly |
| Data inventory review | Quarterly review of data inventory and retention schedules | Quarterly |
| Incident response plan | Documented in SEC-040 | âœ… Complete |
| Vendor due diligence | All vendors reviewed for SOC 2 / ISO 27001 | Annual |
| Risk assessment | Annual security risk assessment | Annual |
| Code review | All changes reviewed before deployment | Ongoing |
| Dependency scanning | `npm audit`, `pip-audit`, `safety` in CI | Every deployment |
| Penetration testing | SAST (OWASP ZAP) + DAST scripts | Quarterly |

---

## 5. International Transfers Summary

| Destination | Processors | Mechanism | Risk |
|---|---|---|---|
| **United States** | Supabase, Vercel, Railway, Anthropic, Resend, Sentry | SCCs + EU-US Data Privacy Framework | Low |
| **Global Edge** | Vercel CDN (100+ locations) | SCCs + Vercel DPA | Low |
| **India** | Supabase (configurable region) | Local processing â€” no transfer | None |
| **User Local Machine** | Ollama | No transfer â€” fully local | None |

**Conclusion:** All international transfers are adequately safeguarded via Standard Contractual Clauses (SCCs) and/or adequacy decisions. No supplementary measures required.

---

## 5. Security Measures â€” Technical & Organizational

### Technical Measures

| Control | Implementation | Standard |
|---|---|---|
| Encryption at rest | Supabase PostgreSQL AES-256 | ISO 27001 |
| Encryption in transit | TLS 1.3 (Vercel + Railway edge) | PCI DSS |
| Authentication | JWT (HS256) + Google OAuth 2.0 | OAuth 2.0 |
| Authorization | `Depends(get_current_user)` on all endpoints | SOC 2 CC5 |
| Row-Level Security | RLS policies on all user-data tables | SOC 2 CC6 |
| Input validation | Pydantic schemas on all request bodies | OWASP ASVS |
| Rate limiting | 100 req/min per IP (configurable) | NIST SP 800-63 |
| Audit logging | Structured JSON logs with request IDs | SOC 2 PI1.4 |
| SQL injection protection | Supabase SDK parameterized queries | OWASP ASVS |
| Secret management | Environment variables, never in code | OWASP ASVS |
| Session management | HTTP-only cookies, 1h access / 30d refresh tokens | OWASP ASVS |
| CORS | Whitelist of allowed origins | OWASP ASVS |
| DDoS protection | Vercel + Railway edge protection | Platform-level |
| Input sanitization | XSS sanitizer (`packages/shared/utils/xss.py`) | OWASP ASVS |
| CSRF protection | CSRF middleware (`packages/shared/utils/csrf.py`) | OWASP ASVS |

### Organizational Measures

| Measure | Description | Frequency |
|---|---|---|
| Data protection training | GDPR, DPDP Act, OWASP Top 10 self-study | Quarterly |
| Data inventory review | Review data categories, retention, access | Quarterly |
| Incident response drills | Tabletop exercises for breach scenarios | Semi-annual |
| Vendor risk assessment | Review vendor SOC 2 reports, DPAs | Annual |
| Code review | All changes reviewed before deployment | Per PR |
| Penetration testing | SAST + DAST + custom attack scenarios | Quarterly |
| Access review | Supabase dashboard review of active users | Quarterly |
| Policy review | All security policies reviewed and updated | Bi-weekly (per AGENTS.md) |

---

## 6. DPIA Assessment â€” Whether Required for AI Processing

| Criterion | Assessment | DPIA Required? |
|---|---|---|
| **Systematic & extensive profiling** (Art. 35(3)(a)) | AI agents generate briefings and recommendations based on user data â€” this constitutes profiling of productivity patterns | âš ï¸ Borderline â€” briefings are non-binding recommendations, not automated decisions with legal effects |
| **Large-scale processing of special categories** (Art. 35(3)(b)) | No special category data (health, biometrics, etc.) processed. Sleep logs could be considered health-adjacent but are user-provided, not inferred. | âŒ Not triggered |
| **Systematic monitoring of publicly accessible areas** (Art. 35(3)(c)) | No CCTV, no public space monitoring | âŒ Not triggered |
| **AI processing of personal data** | AI agents process productivity data to generate briefings, recommendations, and memory consolidation | âš ï¸ Borderline â€” DPIA recommended as best practice |

**DPIA Conclusion:** A DPIA is **recommended as best practice** due to AI processing of personal data, though not strictly required under Art. 35. See `docs/compliance/dpia.md` for the completed DPIA.

---

## 6. Revision History

| Version | Date | Author | Changes | Approved By |
|---|---|---|---|---|
| 1.0.0 | 2026-07-10 | Staff Security Engineer | Initial ROPA â€” GDPR Art. 30 compliant | Developer |
