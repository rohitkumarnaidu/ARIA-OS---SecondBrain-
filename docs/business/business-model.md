# Business Model — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | BIZ-MDL-001 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-12 |
| Classification | Internal |
| Owner | Developer |
| Review Cycle | Quarterly |

---

## 1. Overview

ARIA OS (Second Brain OS) is a personal AI productivity system designed specifically for BTech CSE students. It is maintained by a single developer as an open-source (MIT) project and is entirely free to use.

**Current state:** Personal tooling project with zero revenue, zero users beyond the developer. The project prioritizes quality, privacy, and completeness over monetization.

---

## 2. Value Proposition

| Stakeholder | Value |
|---|---|
| BTech CSE students | AI-powered second brain: courses, tasks, goals, habits, sleep, income, opportunities, projects, ideas, time tracking — all in one free system |
| Developer | Dogfood development: every bug is personal, every feature is needed |
| Open-source community | MIT-licensed, forkable, self-hostable, auditable code |

**Key differentiators:**
- Zero-cost forever (runs entirely on free-tier infrastructure)
- Privacy-first: local AI (Ollama) by default, no data leaves the machine
- Active push intelligence: 10 AI agents proactively deliver insights without prompting
- Graceful degradation: every feature works without AI via algorithmic fallback

---

## 3. Cost Structure

| Item | Current Cost (1 user) | At Scale (100 users) |
|---|---|---|
| Ollama AI (local) | $0/month | $0/month |
| Claude API fallback | ~$1.50/month | ~$15/month |
| Supabase Database | $0 (Free tier, 500 MB) | $25/month (Pro, 8 GB) |
| Vercel hosting (frontend) | $0 (Free tier) | $20/month (Pro) |
| Railway hosting (backend + scheduler) | $0 (Free tier) | $5/month (Starter) |
| Resend email | $0 (100 emails/day free) | $0 (100 emails/day free) |
| GitHub (source + CI) | $0 (Free tier) | $0 (Free tier) |
| **Total** | **~$1.50/month** | **~$65/month** |

### 3.1 Architecture Cost Flow

```mermaid
graph LR
    subgraph USER["User"]
        U1["Free User"]
    end

    subgraph FRONTEND["Frontend Hosting"]
        F1["Vercel Free<br/>$0/mo"]
    end

    subgraph BACKEND["Backend Hosting"]
        B1["Railway Free<br/>$0/mo"]
    end

    subgraph DATABASE["Storage"]
        D1["Supabase Free<br/>500MB DB<br/>$0/mo"]
    end

    subgraph AI["AI Layer"]
        A1["Ollama Local<br/>Mistral 7B<br/>$0/mo"]
        A2["Claude Fallback<br/>Sonnet 4<br/>~$1.50/mo"]
    end

    subgraph NOTIF["Notifications"]
        E1["Resend Free<br/>100 emails/day<br/>$0/mo"]
    end

    USER -->|"HTTPS"| FRONTEND
    FRONTEND -->|"API calls"| BACKEND
    FRONTEND -->|"Direct reads"| DATABASE
    BACKEND -->|"supabase-py"| DATABASE
    BACKEND -->|"AI Requests"| AI
    BACKEND -->|"Transactional"| NOTIF

    A1 -.->|"Circuit Breaker →"| A2

    style USER fill:#0A0B0F,stroke:#6366F1,color:#F1F5F9
    style FRONTEND fill:#13151A,stroke:#818CF8,color:#F1F5F9
    style BACKEND fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style DATABASE fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style AI fill:#13151A,stroke:#34D399,color:#F1F5F9
    style NOTIF fill:#13151A,stroke:#6366F1,color:#F1F5F9
    style A2 fill:#13151A,stroke:#EF4444,color:#F1F5F9
```

**Cost advantage:** Free-tier infrastructure keeps marginal cost near zero. The only variable cost is Claude API fallback usage (~$0.015/request), which is only used when Ollama is unavailable.

---

## 4. Future Monetization (Not Planned)

As a personal project, there are no current plans for monetization. If the project grows to support a broader community, possible future scenarios include:

| Model | Description | When |
|---|---|---|
| GitHub Sponsors | Community-funded development | At any time |
| Pro tier cloud AI | For users who want Claude API without running Ollama locally | Post-public launch |
| Institutional licensing | Colleges deploying ARIA OS for their CS departments | Year 2+ |

Any monetization would remain optional — the core product stays free and open-source (MIT) forever.

---

## 5. Related Documents

| Document | Location |
|---|---|
| Executive Summary | `docs/business/executive-summary.md` |
| Enterprise Roadmap | `docs/enterprise/enterprise-roadmap.md` |
| Technical Debt Register | `docs/enterprise/technical-debt-register.md` |
| Capacity Planning | `docs/performance/capacity-planning.md` |
| AGENTS.md §18 (Cost & Performance) | `AGENTS.md` |
| AGENTS.md §29 (Q3 Intelligence Phase) | `AGENTS.md` |
