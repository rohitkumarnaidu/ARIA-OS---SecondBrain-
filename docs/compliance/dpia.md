# Data Protection Impact Assessment (DPIA)

## Document Control

| Field | Value |
|---|---|
| **Document ID** | COMP-DPIA-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | Restricted |
| **Last Updated** | 2026-07-10 |
| **Next Review** | 2026-10-10 |
| **Assessor** | Staff Security Engineer |
| **DPO** | Developer (acting) |
| **Approved By** | Developer |
| **Related Documents** | COMP-GDPR-ROPA-001, SEC-046 Data Privacy, SEC-POLICY-VULN-001, SEC-040 Incident Response |

---

## 1. System Description

### 1.1 System Overview

| Field | Value |
|---|---|
| **System Name** | ARIA OS (Second Brain OS) |
| **Type** | Personal AI Productivity System |
| **Version** | 1.x |
| **Data Controller** | Developer (BTech CSE Student, India) |
| **Data Processors** | Supabase, Vercel, Railway, Anthropic (Claude), Resend, Sentry, Google (OAuth) |
| **AI Components** | 11 agent modules (briefing, memory, learning, opportunity, task, weekly review, sleep, nudge, roadmap, opportunity matching, skill) |
| **AI Models** | Ollama (Mistral 7B — local), Claude API (Anthropic — cloud, opt-in) |
| **Users** | Individual users (BTech CSE students, personal productivity) |
| **Data Volume** | ~50–500 MB per user (tasks, habits, chat, etc.) |

### 1.2 AI Processing Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ARIA OS AI PROCESSING ARCHITECTURE               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  USER INPUT                                                             │
│    │                                                                    │
│    ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    FASTAPI BACKEND (Railway)                      │  │
│  │                                                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │
│  │  │ Chat Route  │  │ Automation  │  │ Prompt      │               │  │
│  │  │ /api/v1/chat│  │ Routes      │  │ Loader      │               │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │  │
│  │         │               │                │                        │  │
│  │         ▼               ▼                ▼                        │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │                 ARIA ORCHESTRATOR                          │    │  │
│  │  │  Classifies intent → Dispatches to sub-agent              │    │  │
│  │  └──────────┬───────────────────────────────────────────────┘    │  │
│  │             │                                                    │  │
│  │             ▼                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │             10 AI AGENT MODULES                            │    │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │  │
│  │  │  │ Briefing │ │ Memory   │ │ Learning │ │Opportunity│   │    │  │
│  │  │  │ Agent    │ │ Agent    │ │ Agent    │ │ Agent     │   │    │  │
│  │  │  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤   │    │  │
│  │  │  │ Task     │ │ Weekly   │ │ Sleep    │ │ Nudge    │   │    │  │
│  │  │  │ Agent    │ │ Review   │ │ Agent    │ │ Agent    │   │    │  │
│  │  │  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤   │    │  │
│  │  │  │ Roadmap  │ │ Opp.     │ │          │ │          │   │    │  │
│  │  │  │ Agent    │ │ Matching │ │          │ │          │   │    │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │             │                                                    │  │
│  │             ▼                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │              LLM CLIENT (ai/client.py)                    │    │  │
│  │  │  Circuit breaker │ Retry (3x) │ Provider failover         │    │  │
│  │  └──────┬───────────────────────────────────────────┬───────┘    │  │
│  │         │                                           │            │  │
│  │         ▼                                           ▼            │  │
│  │  ┌──────────────┐                          ┌──────────────┐     │  │
│  │  │ OLLAMA       │                          │ CLAUDE API   │     │  │
│  │  │ (Local)      │                          │ (Anthropic)  │     │  │
│  │  │ Mistral 7B   │                          │ Cloud, opt-in│     │  │
│  │  │ No data tx   │                          │ 30-day retain│     │  │
│  │  └──────────────┘                          └──────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    SUPABASE DATABASE                               │  │
│  │  All agent outputs stored in respective tables with RLS           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flows — AI Processing

### Flow 1: AI Chat

| Step | Data | Destination | Security |
|---|---|---|---|
| 1. User types message | Message text | Frontend → Backend API | TLS 1.3 |
| 2. Backend retrieves context | Last N messages (default 20) | Supabase `chat_messages` | RLS, user_id filter |
| 3. Backend constructs prompt | Messages + system prompt | In-memory | N/A |
| 4. Send to AI provider | Message text (no PII in system prompt) | Ollama (local) or Claude API | Local: none; Claude: TLS 1.3 |
| 5. Receive AI response | Generated text | Backend | TLS 1.3 |
| 6. Store conversation | User message + AI response | Supabase `chat_messages` | RLS, AES-256 at rest |
| 7. Display to user | AI response | Frontend | TLS 1.3 |

### Flow 2: Daily Briefing Generation

| Step | Data | Destination | Security |
|---|---|---|---|
| 1. Cron triggers briefing agent | User ID | Scheduler → Backend | Internal |
| 2. Query user data | Tasks, habits, sleep logs, goals | Supabase (filtered by user_id) | RLS |
| 3. Construct briefing prompt | Aggregated productivity data (no raw PII) | In-memory | N/A |
| 4. Send to AI | Aggregated data summary | Ollama (local) or Claude API | Local: none; Claude: TLS 1.3 |
| 5. Store briefing | Generated briefing text | Supabase `daily_briefings` | RLS, 90-day TTL |
| 6. Deliver to user | Briefing text | Frontend | TLS 1.3 |

### Flow 3: Memory Consolidation

| Step | Data | Destination | Security |
|---|---|---|---|
| 1. Trigger (post-chat or cron) | User ID | Backend | Internal |
| 2. Query recent activity | Recent tasks, chat summaries, habit streaks | Supabase (filtered by user_id) | RLS |
| 3. Extract patterns | Behavioral insights, preferences | Ollama (local) or Claude API | Local: none; Claude: TLS 1.3 |
| 4. Store memory | Extracted preferences, patterns | Supabase `memory` table | RLS, user_id filter |

### Flow 4: Opportunity Radar

| Step | Data | Destination | Security |
|---|---|---|---|
| 1. Cron triggers radar | User ID | Scheduler → Backend | Internal |
| 2. Query user profile | Skills, interests, courses, projects | Supabase (filtered by user_id) | RLS |
| 3. Match against opportunities | Skills vs opportunity requirements | Ollama (local) or Claude API | Local: none; Claude: TLS 1.3 |
| 4. Store matches | Opportunity + match score | Supabase `opportunities` | RLS |

### Flow 5: Sleep Wind-Down

| Step | Data | Destination | Security |
|---|---|---|---|
| 1. Cron triggers at 9:30 PM | User ID | Scheduler → Backend | Internal |
| 2. Query sleep data | Recent sleep logs, sleep debt | Supabase `sleep_logs` | RLS |
| 3. Query task data | Incomplete tasks for tomorrow | Supabase `tasks` | RLS |
| 4. Generate wind-down message | Sleep data + task summary | Ollama (local) or Claude API | Local: none; Claude: TLS 1.3 |
| 5. Deliver to user | Wind-down message | Frontend / Notification | TLS 1.3 |

### Flow 6: Course Progress Nudge

| Step | Data | Destination | Security |
|---|---|---|---|
| 1. Cron triggers at 6 PM | User ID | Scheduler → Backend | Internal |
| 2. Query course data | Course progress, deadlines | Supabase `courses`, `learning_progress` | RLS |
| 3. Generate nudge | Course status + recommendation | Ollama (local) or Claude API | Local: none; Claude: TLS 1.3 |
| 4. Deliver to user | Nudge message | Frontend / Notification | TLS 1.3 |

---

## 3. Processing Purposes

| Purpose | AI Agent | Data Used | Necessity |
|---|---|---|---|
| **Conversational AI assistant** | ARIA Orchestrator + Task Agent | Chat messages, task context | Optional — enhances productivity but core features work without it |
| **Daily productivity briefing** | Briefing Agent | Tasks, habits, sleep logs, goals | Optional — opt-in feature |
| **Weekly review generation** | Weekly Review Agent | Tasks, habits, goals, projects, time entries | Optional — opt-in feature |
| **Memory consolidation** | Memory Agent | Chat messages, task completions, habit streaks | Optional — improves AI personalization |
| **Pattern detection** | Learning Agent | Tasks, habits, courses, time entries | Optional — provides insights |
| **Opportunity matching** | Opportunity Agent + Matching Agent | Skills, courses, projects, interests | Optional — opt-in feature |
| **Sleep wind-down** | Sleep Agent | Sleep logs, tasks | Optional — opt-in feature |
| **Course nudges** | Nudge Agent | Course progress, deadlines | Optional — opt-in feature |
| **Skill roadmap optimization** | Roadmap Agent | Courses, skills, goals | Optional — opt-in feature |

---

## 4. Legitimate Interest Assessment

### 4.1 Three-Part Test

| Test | Assessment | Outcome |
|---|---|---|
| **1. Purpose test** — Is there a legitimate interest? | AI processing improves user productivity, provides personalized insights, and enhances the core value proposition of the system. Users explicitly opt in to AI features. | ✅ Legitimate interest established |
| **2. Necessity test** — Is processing necessary? | AI features are not necessary for core service functionality (tasks, habits, goals work without AI). However, once opted in, AI processing is necessary to deliver the promised feature (e.g., briefing generation requires processing task data). | ✅ Necessary for opted-in features |
| **3. Balancing test** — Do interests override data subject rights? | Data subjects have full control: opt-in required, granular toggles, data deletion, no automated decisions with legal effects. AI processes productivity data, not special categories. Risk to data subjects is low. | ✅ Interests do not override rights |

### 4.2 Conclusion

Legitimate interest is established for:
- **Local AI (Ollama)**: Data never leaves user's machine — minimal privacy impact
- **Cloud AI (Claude API)**: Requires explicit, revocable consent — falls under consent, not legitimate interest

---

## 5. Risk Assessment

### 5.1 Risk to Data Subjects from AI Processing

| Risk ID | Risk Description | Likelihood | Impact | Risk Level | Affected Data |
|---|---|---|---|---|---|
| R1 | **Unauthorized access to AI-generated content** — Briefings, memories, or recommendations accessed by unauthorized party | Low | High | **Medium** | Briefings, memories, chat history |
| R2 | **AI data exposure to third party** — Chat messages sent to Claude API intercepted or accessed by Anthropic beyond stated purpose | Low | High | **Medium** | Chat messages |
| R3 | **Inaccurate AI profiling** — AI generates incorrect patterns or recommendations that user relies on | Medium | Low | **Low** | Behavioral patterns, recommendations |
| R4 | **AI bias in recommendations** — Opportunity Radar or Roadmap Agent produces biased recommendations | Low | Low | **Low** | Opportunity matches, skill roadmaps |
| R5 | **Data retention beyond purpose** — AI-generated content retained longer than necessary | Low | Medium | **Low** | Briefings, memories |
| R6 | **Consent withdrawal complexity** — User cannot easily withdraw from AI processing | Low | Medium | **Low** | All AI-processed data |
| R7 | **Re-identification from anonymized data** — Aggregated analytics re-identified to specific user | Very Low | High | **Low** | Analytics events |
| R8 | **Prompt injection / AI manipulation** — Malicious input causes AI to reveal other users' data or system prompts | Low | Medium | **Low** | Chat messages, system prompts |
| R9 | **Data breach via AI provider** — Anthropic suffers data breach exposing user chat messages | Very Low | High | **Low** | Chat messages (Claude API users only) |
| R10 | **Local AI model compromise** — Ollama model on user machine tampered with | Very Low | Medium | **Low** | All local AI data |

### 5.2 Risk Matrix

```
Likelihood
  High  │     │     │     │     │
        │     │     │     │     │
 Medium │     │     │  R1 │     │
        │     │     │     │     │
   Low  │ R3  │ R5  │ R2  │     │
        │ R4  │ R6  │ R7  │     │
        │ R8  │ R10 │ R9  │     │
 Very   │     │     │     │     │
 Low    └──────────────────────────
        Very   Low   Med   High  Impact
        Low
```

**No risks fall in the "High" or "Critical" zone.** All risks are either Low or Medium.

---

## 6. Mitigation Measures

### 6.1 Technical Mitigations

| Risk ID | Mitigation | Implementation | Effectiveness |
|---|---|---|---|
| R1 | Row-Level Security on all tables | Supabase RLS policies on `chat_messages`, `daily_briefings`, `memory` | High |
| R1 | user_id filtering on all queries | Every API query includes `user_id = auth.uid()` | High |
| R1 | Encryption at rest (AES-256) | Supabase PostgreSQL encryption | High |
| R1 | Encryption in transit (TLS 1.3) | Vercel + Railway edge | High |
| R2 | Opt-in consent for cloud AI | Claude API disabled by default; explicit toggle required | High |
| R2 | Data minimization | Only last N messages sent to Claude (default 20) | Medium |
| R2 | No PII in system prompts | System prompt contains no user-identifiable information | High |
| R2 | Anthropic DPA with SCCs | Contractual safeguards for data processing | High |
| R3 | Non-binding recommendations | All AI outputs are suggestions, not directives | Medium |
| R3 | User override | All AI-generated content can be edited or dismissed | High |
| R4 | Algorithmic fallback | Opportunity matching works without AI via keyword matching | Medium |
| R5 | Automated retention enforcement | 90-day TTL on briefings; memory pruning | High |
| R5 | User-controlled deletion | Users can delete individual items or full history | High |
| R6 | Granular consent toggles | Per-feature opt-in/opt-out in Settings | High |
| R6 | One-click withdrawal | Disable AI features at any time | High |
| R7 | Data anonymization | user_id removed from analytics after 30 days | Medium |
| R8 | Input sanitization | XSS sanitizer (`packages/shared/utils/xss.py`) | Medium |
| R8 | Rate limiting | 30 req/min on chat endpoint | Medium |
| R9 | Vendor due diligence | Anthropic SOC 2 Type II, DPA executed | Medium |
| R9 | Breach notification procedure | 72-hour notification to authorities and users | High |
| R10 | N/A — user-managed local environment | Documentation provided for secure Ollama setup | Low |

### 6.2 Organizational Mitigations

| Measure | Description | Status |
|---|---|---|
| Privacy notice | Published privacy policy with AI processing disclosures | ✅ Complete |
| Consent management | Granular opt-in toggles for each AI feature | ✅ Complete |
| Data protection training | GDPR, DPDP Act, OWASP Top 10 self-study | Quarterly |
| Incident response plan | Documented breach response procedure | ✅ Complete |
| Vendor due diligence | All AI vendors assessed for SOC 2 / ISO 27001 | ✅ Complete |
| Data retention policy | Automated deletion schedules for AI-generated content | ✅ Complete |
| Audit logging | All AI API calls logged with request IDs | ✅ Complete |
| Regular DPIA review | Quarterly review of AI processing risks | Scheduled |

### 6.3 Guardrails

| Guardrail | Description | Enforced By |
|---|---|---|
| **No automated decisions** | AI generates recommendations only; no decisions with legal or significant effects | Code architecture |
| **Human-in-the-loop** | All AI outputs reviewed by user before action | UI design |
| **Opt-in by default off** | All AI features default to OFF | Application settings |
| **Local-first** | Default AI is local Ollama; cloud AI requires explicit opt-in | Application logic |
| **Data minimization** | Only necessary data sent to AI; no PII in system prompts | Prompt engineering |
| **Transparency** | Clear disclosure when cloud AI is active | UI banners |
| **Right to object** | Users can disable any AI feature at any time | Settings UI |
| **Right to erasure** | Users can delete AI-generated content or full account | Account deletion flow |

---

## 7. DPIA Conclusion

### 7.1 Assessment Summary

| Criterion | Finding |
|---|---|
| **Is processing necessary?** | Yes — for opted-in AI features |
| **Are there less intrusive alternatives?** | Yes — local AI (Ollama) provides equivalent functionality without data leaving user's machine |
| **Are risks to data subjects acceptable?** | Yes — all risks are Low or Medium with existing mitigations |
| **Are additional safeguards needed?** | No — current controls (RLS, encryption, consent, data minimization, retention limits) are adequate |
| **Is DPA consultation required?** | No — processing is low-medium risk, not large-scale special category data |

### 7.1 Overall Assessment

| Aspect | Rating |
|---|---|
| **Risk to data subjects** | Low |
| **Effectiveness of mitigations** | High |
| **Compliance with GDPR principles** | High |
| **Proportionality of processing** | High |
| **DPIA outcome** | **Processing is acceptable with current mitigations** |

### 7.2 Conditions for Continued Processing

1. **All AI features must remain opt-in** — default OFF, explicit consent required
2. **Local AI must remain the default** — cloud AI requires separate opt-in
3. **Data minimization must be maintained** — only necessary data sent to AI
4. **Retention limits must be enforced** — 90-day TTL on briefings, memory pruning active
5. **Consent withdrawal must be immediate** — disabling AI features stops processing immediately
6. **DPIA must be reviewed quarterly** — next review: 2026-10-10

### 7.3 Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| **Assessor** | Staff Security Engineer | 2026-07-10 | On file |
| **DPO (acting)** | Developer | 2026-07-10 | On file |
| **Data Controller** | Developer | 2026-07-10 | On file |

---

## 8. Revision History

| Version | Date | Author | Changes | Approved By |
|---|---|---|---|---|
| 1.0.0 | 2026-07-10 | Staff Security Engineer | Initial DPIA — AI processing assessment | Developer |
