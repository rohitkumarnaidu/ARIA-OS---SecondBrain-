# Constraints — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-CON-006 |
| Version | 1.0.0 |
| Status | Approved |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Business Constraints

| ID | Constraint | Description | Impact |
|---|---|---|---|
| BC-01 | Zero budget | No funding for infrastructure, tools, or services | All infra must be free tier (Supabase, Railway, Vercel) |
| BC-02 | Solo developer | Single person building, maintaining, and supporting | Feature velocity limited to ~10-15 hrs/week |
| BC-03 | Open source MIT | All code publicly available, forkable, reusable | No proprietary code, community contributions expected |
| BC-04 | Rs. 0 forever | Core product never charges users | Monetization only through optional premium add-ons |
| BC-05 | India-first | Primary target is Indian BTech CSE students | Academic calendar, CGPA, NPTEL, GATE-specific features |

---

## 2. Technical Constraints

| ID | Constraint | Description | Impact |
|---|---|---|---|
| TC-01 | Free tier Supabase | 500MB DB, 2GB bandwidth, 50K rows | Efficient schema design, archive old data |
| TC-02 | Free Railway | $5 credit/month, limited uptime | Service may sleep after inactivity, warm-up on first request |
| TC-03 | Free Vercel | 100GB bandwidth, 6000 build min/month | Optimize builds, use ISR over SSR where possible |
| TC-04 | Ollama local | Requires 8GB RAM, Mistral 7B limits | Algorithmic fallback for all AI features, Claude optional |
| TC-05 | PWA limitations | No native APIs (Bluetooth, NFC, sensors), iOS push limitations | React Native deferred to Y2, PWA as primary delivery |
| TC-06 | Single-user architecture | No collaboration, sharing, or social features | Simpler data model, no need for teams/spaces |

---

## 3. Schedule Constraints

| ID | Constraint | Description | Impact |
|---|---|---|---|
| SC-01 | Q3 2026 production | Production deploy by Jul 14, 2026 | Feature-complete by Jul 7, hardening through Sep |
| SC-02 | No dedicated QA | Developer is also QA | Heavy reliance on automated testing (2795+ tests) |
| SC-03 | Academic calendar | Features timed for Indian academic semesters (Jul-Nov, Jan-May) | Course features prioritized for semester starts |

---

## 4. Architectural Constraints

| ID | Constraint | Description | Impact |
|---|---|---|---|
| AC-01 | Monorepo structure | Single repo with apps/, packages/, services/ | All CI triggered on any change, large clone size |
| AC-02 | In-process agents | No microservices, agents as async Python functions | No horizontal scaling, all agents affected by process crash |
| AC-03 | API versioning | All endpoints under /api/v1/ | Backward compatibility enforced, migration required for breaking changes |
| AC-04 | No event bus | Direct function calls + Supabase Realtime | Tight coupling, no event persistence, revisit Y2 |
| AC-05 | In-memory cache | No Redis, TTL cache in process | Cache lost on restart, not shared across processes |

---

## 5. Compliance Constraints

| ID | Constraint | Description | Impact |
|---|---|---|---|
| CC-01 | MIT License | No GPL/AGPL dependencies allowed | License compatibility check for all deps |
| CC-02 | Data privacy | User data stored in India, local AI processing | Supabase Mumbai region, Ollama on local machine |
| CC-03 | SOC 2 readiness | Target SOC 2 Type I by Q2 2027 | Audit trail on all mutations, RLS, access controls |
| CC-04 | No secrets in code | API keys, tokens in env vars only | .env.example for documentation, .env in gitignore |

---

## 6. Constraint Interactions

| Interacting Constraints | Conflict | Resolution |
|---|---|---|
| BC-01 (Zero budget) + TC-01 (Free Supabase) | 500MB DB limit for growing user base | Data retention policies, archive old logs |
| BC-02 (Solo dev) + SC-01 (Q3 deadline) | Limited capacity for all features | Strict scope control, defer non-critical features |
| TC-04 (Ollama) + AI features | Local AI quality may be lower | Claude fallback for quality-sensitive operations |
| CC-01 (MIT) + dependency licenses | GPL/AGPL deps can't be used | Vetting all deps for license compatibility |

---

## 7. References

| Document | Location |
|---|---|
| Project Scope | ProjectScope.md |
| Risks | Risks.md |
| Assumptions | Assumptions.md |
| Architecture | `docs/engineering/12_Architecture.md` |
| ADRs | `docs/engineering/adr/` |

> **Duplicate note:** A separate technical constraints document exists at [`docs/engineering/Constraints.md`](../engineering/Constraints.md) covering database, API, and architectural constraints. This product-level document focuses on business and project-level constraints. See the engineering version for implementation-specific constraints.
