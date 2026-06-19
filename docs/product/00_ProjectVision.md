# Project Vision Document — Second Brain OS (ARIA OS)

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-PVD-001 |
| Version | 4.0.0 |
| Status | Active |
| Classification | Public — Product Vision |
| Owner | Product Lead |
| Last Updated | 2026-06-11 |
| Next Review | 2026-09-11 |
| Review Cycle | Quarterly |
| Approving Authority | Product Lead (Self — Solo Project) |

---

## Revision History

| Version | Date | Author | Changes | Review Status |
|---|---|---|---|---|
| 1.0.0 | 2026-06-01 | Developer | Initial project vision | Draft |
| 2.0.0 | 2026-06-11 | Developer | Expanded to 15 sections, market analysis, risk register | Approved |
| 3.0.0 | 2026-06-11 | Developer | Enterprise upgrade: 5-year vision, user transformation arc, platform vision, community strategy, monetization philosophy | Approved |
| 4.0.0 | 2026-06-11 | Developer | Enterprise v4: Strategic context, competitive warfare analysis, GTM strategy, technology innovation roadmap, stakeholder value map, weighted decision framework, quantitative risk model, brand architecture, sustainability plan, data governance vision, measurement framework, implementation milestone map | Approved |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Strategic Context & Market Timing](#2-strategic-context--market-timing)
3. [Product Philosophy & Mission](#3-product-philosophy--mission)
4. [Origin Story & Problem Space](#4-origin-story--problem-space)
5. [Target Audience & User Transformation](#5-target-audience--user-transformation)
6. [Value Proposition & Competitive Positioning](#6-value-proposition--competitive-positioning)
7. [Product Vision — 5-Year Horizon](#7-product-vision--5-year-horizon)
8. [Technology Vision & Innovation Roadmap](#8-technology-vision--innovation-roadmap)
9. [Platform Strategy & Ecosystem](#9-platform-strategy--ecosystem)
10. [Go-to-Market Strategy](#10-go-to-market-strategy)
11. [Stakeholder Value Map](#11-stakeholder-value-map)
12. [Success Metrics & Measurement Framework](#12-success-metrics--measurement-framework)
13. [Brand Architecture & Positioning](#13-brand-architecture--positioning)
14. [Monetization Philosophy & Sustainability](#14-monetization-philosophy--sustainability)
15. [Community & Contributor Strategy](#15-community--contributor-strategy)
16. [Risk Management & Vision Safeguards](#16-risk-management--vision-safeguards)
17. [Implementation Roadmap & Milestones](#17-implementation-roadmap--milestones)
18. [Data Governance & Privacy Vision](#18-data-governance--privacy-vision)
19. [Glossary](#19-glossary)
20. [References & Related Documents](#20-references--related-documents)

---

### Vision → Execution Flow

```mermaid
%%
init: {
  'theme': 'base',
  'themeVariables': {
    'background': '#0A0B0F',
    'primaryColor': '#13151A',
    'primaryBorderColor': '#6366F1',
    'primaryTextColor': '#F1F5F9',
    'lineColor': '#818CF8',
    'secondaryColor': '#1A1D24',
    'tertiaryColor': '#00FFA3',
    'fontFamily': 'DM Sans',
    'fontSize': '14px'
  }
}
%%
graph LR
  subgraph V["🎯 Vision"]
    V1[Purpose-Built AI OS<br/>for BTech CSE Students]
    V2[Zero-Cost Architecture<br/>Rs. 0/month]
    V3[15 Unified Modules<br/>One Intelligent Surface]
  end

  subgraph S["📊 Strategy"]
    S1[Competitive Positioning<br/>Unique Category Creation]
    S2[GTM: Student Communities<br/>College Ambassador Program]
    S3[Monetization: Freemium →<br/>Pro → Enterprise]
  end

  subgraph R["🗺️ Roadmap"]
    R1[12-Month Build<br/>9 Phases, 455 Hours]
    R2[Alpha → Beta → GA<br/>Q3 2026 → Q2 2027]
    R3[Modular Delivery<br/>Ship Every Phase]
  end

  subgraph E["⚡ Execution"]
    E1[Ollama Local AI<br/>Claude Fallback]
    E2[FastAPI + Next.js 14<br/>Supabase PostgreSQL]
    E3[Solo Dev + Community<br/>Open Source Contributions]
  end

  V --> S --> R --> E
  E -.->|Feedback| V

  style V fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style S fill:#13151A,stroke:#818CF8,color:#F1F5F9
  style R fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style E fill:#13151A,stroke:#F59E0B,color:#F1F5F9
```

### 5-Year Strategic Roadmap

```mermaid
%%
init: {
  'theme': 'base',
  'themeVariables': {
    'background': '#0A0B0F',
    'primaryColor': '#13151A',
    'primaryBorderColor': '#6366F1',
    'primaryTextColor': '#F1F5F9',
    'lineColor': '#818CF8',
    'secondaryColor': '#1A1D24',
    'tertiaryColor': '#00FFA3',
    'fontFamily': 'DM Sans',
    'fontSize': '14px'
  }
}
%%
gantt
  title 5-Year Strategic Vision Timeline
  dateFormat  YYYY-MM
  axisFormat  %Y Q%q

  section 🏗️ Foundation
  Core Build (15 Modules + AI)    :2026-07, 2026-12
  Alpha → Beta → GA Launch        :2026-10, 2027-06

  section 🚀 Growth
  Mobile App (React Native)       :2027-04, 2027-10
  Browser Extension               :2027-07, 2027-12
  Collaboration Features           :2027-10, 2028-03

  section 📈 Scale
  Community Platform               :2028-01, 2028-06
  API Marketplace & Integrations   :2028-04, 2028-10
  Enterprise Licensing             :2028-07, 2029-01

  section 🌍 Ecosystem
  Institutional Partnerships        :2029-01, 2029-06
  ARIA Skills SDK                  :2029-04, 2029-10
  Global Student Network            :2029-07, 2030-03

  section 🔮 Horizon
  AI Tutor & Mentor Network        :2030-01, 2030-06
  Decentralized Knowledge Graph    :2030-04, 2030-12
```

---

## 1. Executive Summary

### 1.1 The Vision in One Sentence

**Second Brain OS (ARIA OS)** is the world's first purpose-built AI operating system for BTech CSE students — a unified platform that transforms fragmented student lives into compounded, measurable growth by connecting learning, building, earning, and well-being into a single intelligent system.

### 1.2 The Core Insight

BTech CSE students represent one of the most valuable but underserved segments in the productivity market. They manage 10+ disconnected tools, lose 80% of ideas within 24 hours, miss 60% of relevant opportunities, abandon 70% of courses, and have zero systematic time or income tracking. The result is a systematic failure of potential — students who could be building real things spend their college years in fragmentation.

**Second Brain OS solves this with three architectural innovations:**

| Innovation | What It Does | Why It Matters |
|---|---|---|
| **Active Push Intelligence** | ARIA agent proactively delivers briefings, radar scans, nudges, and reminders without user prompting | Students forget to check tools. The system must push information at the right moment — morning briefing (7 AM), opportunity scan (6 AM), wind-down (9:30 PM), progress nudge (6 PM) |
| **15-Module Unified Surface** | Courses, tasks, goals, ideas, opportunities, income, projects, habits, sleep, time, resources, YouTube, academics, chat, automation — all in one system | Every other tool covers 1-3 domains. Fragmentation itself is the problem. One surface means everything compounds |
| **Zero-Cost Architecture** | Runs entirely on free-tier infrastructure: Vercel, Supabase, Ollama, Brave Search, Resend | Rs. 0/month means financially inaccessible students get the same power as enterprise tool users |

### 1.3 Key Metrics at a Glance

| Metric | Current | Target (Year 1) | Target (Year 5) |
|---|---|---|---|
| Daily Active Users | 0 (pre-launch) | 100 | 25,000+ |
| Task completion rate | ~35% (baseline) | >78% | >85% |
| Course completion rate | ~25% (baseline) | >70% | >80% |
| User retention (30-day) | 0% | >60% | >70% |
| Opportunities found/month | 0.5 (baseline) | 8+ | 15+ |
| Infrastructure cost | Rs. 0 | <Rs. 100/month | <Rs. 5,000/month |
| Revenue | Rs. 0 | Rs. 0 (indirect) | Rs. 50 lakhs+/year |

### 1.4 The BHAG (Big Hairy Audacious Goal)

**By 2031, Second Brain OS will help 25,000+ students complete 500,000+ courses, ship 100,000+ projects, and collectively earn Rs. 10 crore+ through opportunities found via the system — while operating at zero cost to every user.**

---

## 2. Strategic Context & Market Timing

### 2.1 Why Now? — The Convergence of Five Tailwinds

Second Brain OS exists at the intersection of five powerful secular trends. 2026-2031 represents a unique window of opportunity where all five align simultaneously:

```
TIMELINE OF CONVERGENCE
══════════════════════════════════════════════════════════════════════

2023 ───── 2024 ───── 2025 ───── 2026 ───── 2027 ───── 2028 ───── 2029 ───── 2030 ───── 2031
                                  │
                                  │ ★ SECOND BRAIN OS LAUNCH
                                  │
  ◄── AI NATIVE ERA ───────────────────────────────────────────────────────────────►
  ChatGPT launched Dec 2022   AI in every app    Users expect AI    AI-first is table stakes
       (Year -3)                                  natively in all               by 2028
                                                  productivity tools

  ◄── BUILDER GENERATION ──────────────────────────────────────────────────────────►
  62% of Indian Gen Z want to start a business (Deloitte 2024 Millennial Survey)
       (Year -2)                                  Startup culture          Creator economy
                                                  peaks in Indian          becomes primary
                                                  college campuses          career path

  ◄── FREE INFRASTRUCTURE MATURITY ────────────────────────────────────────────────►
  Supabase launches  Supabase reaches  Vercel,Railway,    Free tiers abundant   Marginal cost
  (2020)             500K+ users       Supabase free       but tightening        of compute near
                      (2022)           tiers mature                             zero for apps
                                       (2024-25)                                under 1K users

  ◄── PRIVACY RENAISSANCE ─────────────────────────────────────────────────────────►
  Self-hosted tools  Local LLMs        Data sovereignty    Privacy as            Self-sovereign
  gaining traction   (Ollama, Llama)   becomes mainstream  competitive            AI expectations
                     (2023)            consumer concern    differentiator         become default
                                       (2024-25)          (2026-28)

  ◄── INDIA TECH BOOM ────────────────────────────────────────────────────────────►
  50K+ startups      1.5M engineers   Internship market   AI/ML job boom   India becomes
  (2023)             graduate/year    at all-time high    exceeds supply  3rd largest
                     (2024)           (2025-26)           (2027-28)       startup ecosystem
                                                                            by 2030
```

### 2.2 Market Timing Analysis

| Factor | 2026 State | Why It Matters |
|---|---|---|
| **AI Literacy** | 72% of Indian college students have tried ChatGPT | Users understand AI capabilities — no education barrier |
| **Ollama Maturity** | Mistral 7B runs on 8GB RAM laptops | Local AI is viable on student hardware |
| **Supabase Scale** | 2M+ registered users, proven free tier | Infrastructure is battle-tested at zero cost |
| **Student Income Pressure** | 47% of BTech students seek freelance income during college | Built-in need for income tracking + opportunity radar |
| **Remote Work Normalization** | 68% of tech internships are remote (2025 NASSCOM) | Opportunity radar can find national opportunities, not just local |
| **Tool Fatigue** | Avg student uses 7.3 productivity tools (survey data) | High pull for consolidation — fragmentation pain is acute |

### 2.3 The Window of Opportunity

The product has approximately **24-36 months** before incumbents (Notion, Todoist, Motion) or new entrants build student-specific AI features. However, three factors create a durable moat:

1. **Depth of student-specific modules** (courses, CGPA, semester structure, hackathon radar) — general tools need 5+ new modules to match
2. **Zero-cost architecture** — VC-backed competitors must monetize, limiting their ability to offer free
3. **Privacy-first local AI** — centralized AI providers cannot offer local-first without restructuring their entire business model

---

## 3. Product Philosophy & Mission

### 3.1 The Five Core Pillars

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           SECOND BRAIN OS CORE PILLARS                          │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ACTIVE INTELLIGENCE                  COMPOUND GROWTH                           │
│  ┌──────────────────────────────┐   ┌──────────────────────────────┐            │
│  │ Pushes information           │   │ Every action feeds every     │            │
│  │ proactively — never waits    │   │ other action. Course→skill→  │            │
│  │ to be asked. 8 agents        │   │ project→income. Nothing is  │            │
│  │ orchestrated by ARIA.        │   │ isolated. Everything         │            │
│  │ 6 automated cron jobs.       │   │ compounds.                   │            │
│  └──────────────────────────────┘   └──────────────────────────────┘            │
│                                                                                  │
│  PRIVACY FIRST                         ZERO BARRIERS                            │
│  ┌──────────────────────────────┐   ┌──────────────────────────────┐            │
│  │ Your data never leaves your  │   │ Rs. 0, offline-capable,      │            │
│  │ control. RLS on every table. │   │ runs on 8GB RAM. Cost,       │            │
│  │ Local AI via Ollama.         │   │ connectivity, or hardware    │            │
│  │ No data used for training.   │   │ never stops any student.     │            │
│  └──────────────────────────────┘   └──────────────────────────────┘            │
│                                                                                  │
│  BUILD FIRST                                                                    │
│  ┌────────────────────────────────────────────────────────────────────┐         │
│  │ Everything funnels toward building real things. Courses exist to  │         │
│  │ build projects. Ideas exist to ship products. Skills exist to     │         │
│  │ earn income. The system measures shipped output, not input.       │         │
│  └────────────────────────────────────────────────────────────────────┘         │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Mission Statement

> Second Brain OS exists to solve the fragmentation problem of student life: courses registered and forgotten, YouTube videos saved and never watched, startup ideas at 2 AM that disappear by morning, internship deadlines missed by one day, skills meant to be learned six months ago but never started, income earned at unknown rates, health neglected until burnout. We provide the single system that makes all of it compound instead of staying separate.

### 3.3 Vision Statement

> To empower every BTech CSE student to become a builder who makes real things, earns real money, and builds real experience while still in college — by giving them an AI system that remembers everything they forget, watches the internet for opportunities that match them, tells them what to do each morning, and connects their learning to their building to their income.

### 3.4 Operating Principles (The 10 Commandments)

| # | Principle | Definition | Implication |
|---|---|---|---|
| 1 | **Owned Entirely By You** | No subscription. Data never leaves your Supabase instance. | Self-hosted; open-source forever |
| 2 | **Zero Miss Policy** | Every task is done, rescheduled, or explicitly dropped. No silent failures. | Cron checks every 15 min for overdue tasks |
| 3 | **Active Intelligence** | System pushes information: briefings, nudges, radar scans, reminders. | 6 automated cron jobs, 8 sub-agents |
| 4 | **Build First** | Everything connects to building real things. | Project module is the culmination of all other modules |
| 5 | **Honest About Status** | No fake streaks. Real metrics. Compassionate honesty. | Raw completion rates; no gamification |
| 6 | **Offline First** | PWA with IndexedDB. Works without internet. | All CRUD operations work offline |
| 7 | **Privacy by Default** | Data never used to train AI models. RLS on every table. Local AI via Ollama. | No data leaves user's control |
| 8 | **Compound Not Fragment** | Every action feeds every other action. | Course completion updates skill profile → better radar matches → more income |
| 9 | **Progressive Complexity** | Works on Day 1 with zero config. Advanced features reveal themselves. | Dashboard is immediately useful; advanced AI features unlock over time |
| 10 | **Build With, Not For** | Developer is also user. Every feature built because it was needed. | Dogfood development; no speculative features |

### 3.5 Anti-Principles (What We Deliberately Avoid)

| Anti-Principle | Why We Avoid It | What We Do Instead |
|---|---|---|
| Gamification (streaks/badges/leaderboards) | Creates fake motivation loops; users optimize for badges not outcomes | Honest metrics dashboard showing real progress |
| Social features / sharing / feeds | Productivity comparison anxiety; privacy violation | Single-user architecture per ADR-002 |
| "AI-first" at cost of reliability | AI failures should not block core functionality | Every AI feature has deterministic algorithmic fallback |
| Feature creep / scope bloat | 15 modules is already ambitious; every new feature must pass "Builder Test" | Explicit out-of-scope list; quarterly scope review |
| Lock-in / proprietary formats | Users must own their data | JSON/CSV export from Day 1; standard Supabase schema |
| VC-funded growth / dark patterns | Growth hacking contradicts privacy-first ethos | Organic growth through demonstrated value |
| Monthly/yearly subscriptions | Students cannot pay for software | Rs. 0 forever for core product |
| Ads or data monetization | Users are not the product | Revenue from enterprise licensing + optional premium AI credits |

---

## 4. Origin Story & Problem Space

### 4.1 The Fragmentation Crisis — A Day in the Life

```
BEFORE SECOND BRAIN OS — A TYPICAL STUDENT DAY
══════════════════════════════════════════════════════════════════════

Time        Activity                              Tools Used                    Outcome
────        ────────                              ──────────                    ───────
7:00 AM     Wake up, check phone                  WhatsApp, Instagram           Immediate overwhelm, 50+ notifications
9:00 AM     College classes                        Notebook, Google Classroom    Scattered notes, no central capture
1:00 PM     Free period — "will study DSA"         Opens YouTube, Udemy,         Opens 10 tabs, closes all after 30 min
                                                   GitHub, Stack Overflow        
4:00 PM     "Time to code project"                 Opens 3 repos in VS Code      Reads code, anxious about architecture, closes
6:00 PM     Remembers 2 assignments due in 2 days  Google Keep, Google Calendar  Stress spike, starts one assignment
8:00 PM     Watches 3 YouTube tutorials            YouTube, browser tabs         Saves to "Watch Later" — never watched again
10:00 PM    Brilliant startup idea                  WhatsApp voice note, Notes    Saved in WhatsApp — never seen again
11:30 PM    Sleep guilt — knows sleep is poor       Alarm clock                   No data, no awareness
12:00 AM    Regret spiral — another unproductive    None                          Stress, poor sleep, repeat tomorrow
            day
```

**The cost of this fragmentation:**
- **Course fees wasted**: Rs. 3,000-15,000/year per student
- **Missed income**: Rs. 50,000+/year in unfound opportunities
- **Lost ideas**: 80% of creative potential evaporates within 24 hours
- **Skill decay**: Skills learned in courses forgotten within 6 months because never applied
- **Time blindness**: 10-15 hours/week unaccounted = 520-780 hours/year lost

### 4.2 The Question That Created a Product

> **"What if there was one system that watched everything — remembered courses I enrolled in, scanned the web for opportunities I'd never find, resurfaced ideas before I forgot them, tracked my income to know my hourly rate, monitored my sleep to protect my health, and told me every morning exactly what I should do today?"**

No existing tool answered this question:

| Tool | Why It Fails |
|---|---|
| **Notion** | Generic workspace — no student-specific modules, no AI agent, no proactive push, expensive templates |
| **Todoist** | Task manager only — no courses, no opportunities, no income, no AI. Passive — user must check it |
| **Motion** | AI scheduling — $19/month ($1,600/year). Priced out of student budgets. No student features |
| **ChatGPT/Claude** | No persistent memory, no proactive push, no integration with student workflows. Requires manual prompting |
| **Obsidian** | Powerful knowledge graph but no execution engine. Passive — user must manually connect notes |
| **Notion Calendar** | Calendar only — no task intelligence, no course tracking, no radar |
| **College ERP** | Poor UX, locked data silos, no AI, no cross-system integration |
| **Google Keep** | Simple notes — no structure, no AI, no deadlines, no relations |

### 4.3 The Compounding Problem

The fragmentation creates a **negative compounding cycle**:

```
                    ┌──────────────────────────┐
                    │  MISSED INTERNSHIP        │
                    │  DEADLINE                 │
                    └───────────┬──────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │  LOST INCOME             │
                    │  (~Rs. 50,000)           │
                    └───────────┬──────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │  REDUCED MOTIVATION       │
                    │  (imposter syndrome)      │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │  FEWER PROJECTS SHIPPED   │
                    │  (weaker portfolio)       │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │  WEAKER PORTFOLIO         │
                    │  → fewer interviews       │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │  MORE MISSED OPPORTUNITIES│
                    │  → cycle repeats          │
                    └──────────────────────────┘
```

**Second Brain OS breaks this cycle at every node simultaneously:**

| Node | Intervention | Mechanism |
|---|---|---|
| Missed deadlines | Task auto-reschedule (every 15 min check) | Missed tasks rescheduled based on priority, never silently expire |
| Lost income | Income tracking + effective hourly rate | Every income entry logged, hourly rate calculated automatically |
| Motivation decline | Daily briefing + weekly review | Positive reinforcement through data: "You completed 18 tasks this week" |
| Weak portfolio | Project phase tracking + GitHub integration | Ships tracked as phases completed; GitHub commit activity visible |
| Missed opportunities | Opportunity radar (6 categories, daily scan) | Matched to skills, deadline urgency indicators, push alerts |

### 4.4 The "After" Day — What Success Looks Like

```
AFTER SECOND BRAIN OS (3 MONTHS IN) — A TRANSFORMED DAY
══════════════════════════════════════════════════════════════════════

Time        Activity                              Module(s) Used                 Outcome
────        ────────                              ────────────                   ───────
6:00 AM     Radar scan completes                   Opportunity Radar              3 new matches found (internship, hackathon,
                                                                                  grant) — match scores 72, 85, 91
7:00 AM     Briefing delivered                     Daily Briefing                 Top 3 priorities for today, weather,
                                                                                  opportunity highlights, sleep reminder
9:00 AM     College classes                        Academics                      Logs attendance; auto-captures notes
1:00 PM     Free period — opens system             Dashboard                      Shows next action for main project
1:05 PM     Starts task "Implement auth middleware" Time Tracker (Pomodoro)        25 min focus timer starts
3:00 PM     Coding session                         Projects + Time                Deep work session logged (2h continuous)
4:00 PM     Checks radar opportunities             Opportunity Dashboard          Applies to 2 matches — saves to "Applied"
6:00 PM     Nudge: "DSA course hasn't progressed"   Course Progress Nudge          Studies DSA for 1 hour
8:00 PM     Saves YouTube tutorial                 YouTube Vault (via extension)  Auto-linked to current project
9:30 PM     Wind-down message                      Sleep Agent                    Sleep log reminder; "You did 18 pomodoros
                                                                                  today — rest well"
10:30 PM    Logs sleep                             Sleep Log                      Duration: 7.5h, Quality: 4/5
```

**Quantified transformation (after 3 months):**

| Dimension | Baseline | After 3 Months | Improvement |
|---|---|---|---|
| Tasks completed/week | 3-5 (urgent only) | 18-22 (balanced) | +340% |
| Course completion rate | <30% | >70% | +133% |
| Opportunities found/month | 0.5 | 8-12 | +1500% |
| Projects shipped/year | 0.5 | 3-5 | +700% |
| Income tracked | 0% | 95% | — |
| Ideas actioned | 10% | 65% | +550% |
| Sleep logged | 0 nights/week | 5-6 nights/week | — |
| Deep work hours/week | 0 (unmeasured) | 12-15 | — |
| Effective hourly rate | Unknown | Known and optimized | — |

---

## 5. Target Audience & User Transformation

### 5.1 Primary Personas (P0-P1)

#### Persona A: "The Overloaded Optimist" (Arjun, 19, 2nd Year)

| Attribute | Detail | System Implication |
|---|---|---|
| **Situation** | 4 online courses + college + hackathon team. 200+ browser tabs. | Needs course completion nudges, tab consolidation, task prioritization |
| **Pain** | Buys courses on sale. Never finishes. Guilt cycles. | Course module must show progress visually; resurface unfinished courses |
| **Tech** | Windows (8GB RAM), mid-range Android, spotty hostel Wi-Fi | Must run on low-end hardware; offline mode critical |
| **Income** | Rs. 2,000/month from parents | Cannot afford any paid tool — Rs. 0 is mandatory |
| **Trigger** | "I missed another internship deadline. I need a system that won't let me miss things." | Opportunity radar with deadline alerts is the hook |
| **Monthly Value** | Rs. 5,000-10,000 (saved fees + found opportunities) | >10x value even at Rs. 0 cost |
| **Engagement Pattern** | Check-in 2-3x/day, less during exams, heavy during holidays | Notification-driven re-engagement during low periods |

#### Persona B: "The Solo Builder" (Priya, 20, 3rd Year)

| Attribute | Detail | System Implication |
|---|---|---|
| **Situation** | Building SaaS product. Freelances Rs. 5,000-15,000/month. | Needs income tracking, time analytics, project roadmap |
| **Pain** | Can't track time across income streams. Underpricing because unknown hourly rate. | Effective hourly rate calculator is the hook |
| **Tech** | MacBook Air, good Android, stable internet | Can handle more resource-intensive features |
| **Income** | Rs. 5,000-15,000/month freelancing | Could pay Rs. 99/month for premium AI features if value is clear |
| **Trigger** | "I spent 40 hours on a project paying Rs. 3,000. That's Rs. 75/hour. I need to know this." | Income/time module integration delivers immediate ROI |
| **Monthly Value** | Rs. 5,000-10,000 (rate optimization) | Premium candidate if conversion needed |
| **Engagement Pattern** | Heavy daily use during project phases; Pomodoro power user | Needs deep time tracking, phase management |

#### Persona C: "The Idea Generator" (Rohan, 18, 1st Year)

| Attribute | Detail | System Implication |
|---|---|---|
| **Situation** | 50+ startup ideas in various notes. Zero shipped. | Needs idea pipeline (raw → validating → building → shipped) |
| **Pain** | Ideas urgent at 2 AM, irrelevant by morning. Cannot decide what to build. | Idea scoring system (effort × impact × confidence) provides decision framework |
| **Tech** | Old Windows laptop, budget Android | Lightweight frontend; minimal JS; PWA preferred over native |
| **Income** | Rs. 1,000/month from parents | Rs. 0 forever |
| **Trigger** | "I can't even remember the details of my idea from 3 weeks ago." | Idea capture with timestamp + automatic resurface |
| **Monthly Value** | Structured pipeline from idea → execution | Prevents idea overwhelm; provides decision clarity |

### 5.2 Secondary Personas (P2-P3)

#### Persona D: "The Self-Taught Switcher" (22, Non-CS Degree)

| Attribute | Detail |
|---|---|
| **Background** | B.Com/B.A graduate learning to code via bootcamps, YouTube, freeCodeCamp |
| **Pain** | No academic structure, no peer group, no opportunity network, no portfolio |
| **Needs** | Skill tracking, project roadmap, portfolio builder, opportunity radar |
| **System Adaptation** | Course module needs bootcamp/non-degree tracks; skill profile is primary |
| **Conversion Path** | YouTube → resource vault → project builder → portfolio → opportunities |

#### Persona E: "The Fresh Graduate" (22-24, Junior Developer)

| Attribute | Detail |
|---|---|
| **Background** | Employed 0-2 years as junior developer at startup/tech company |
| **Pain** | Transition from academic to professional structure; still building foundation |
| **Needs** | Shift from CGPA to career growth tracking; work-related modules; meeting notes |
| **System Adaptation** | Modify academic modules; add meeting tracking; OKR alignment for career goals |

### 5.3 User Needs Hierarchy

```
SELF-TRANSCENDENCE
  "I mentor others. My system helps other students build."
      │
      │  Community contribution features (Year 3+)
      │  Plugin development, template sharing, mentorship matching
      │
      ▼
SELF-ACTUALIZATION
  "I complete courses. Ship projects. Land career-defining opportunities."
      │
      │  Full 15-module system
      │  Weekly review shows measurable progress
      │  Skill-to-income pipeline validates growth
      │
      ▼
BELONGING & COMPETENCE
  "I know where my time goes. I see progress. I'm not alone."
      │
      │  Analytics dashboards (time, income, habits, sleep)
      │  Community (GitHub, Discord — optional opt-in)
      │  Streak recovery metrics (compassionate tracking)
      │
      ▼
CONTROL & STRUCTURE
  "I have a system. Nothing falls through the cracks."
      │
      │  Daily briefing, task management, auto-reschedule
      │  Course deadlines, opportunity radar alerts
      │  Habit consistency, sleep logs
      │
      ▼
CAPTURE & REMEMBER
  "I can save anything. The system remembers everything."
      │
      │  Tasks, ideas, YouTube videos, resources, bookmarks
      │  AI-powered memory (chat history, preferences, patterns)
      │  Resurface engine — context-aware recall
      │
```

### 5.4 Anti-Audience (Explicitly Out of Scope)

| Group | Exclusion Reason | When/If to Revisit |
|---|---|---|
| **Enterprise teams** | Single-user per ADR-002. No team features. | Year 3+ if collaborative features requested by community |
| **Non-technical users** | CLI tools, GitHub, self-hosting required. Below minimum threshold. | 1-click deploy template (Year 2) reduces barrier |
| **K-12 students** | Semester/CGPA system doesn't apply. Content too advanced. | Year 4+ with simplified curriculum tracking |
| **Professionals >5yr** | Needs are around management, leadership, networking — not covered | Year 4+ with career pivot module |
| **Social users seeking feed/leaderboards** | Privacy-first. No sharing, no friends, no likes. | Never — violates core principle |
| **VC-backed growth stage** | Rs. 0 model + privacy-first incompatible with growth-at-all-costs | Never — philosophical incompatibility |

### 5.5 User Segment Prioritization

| Priority | Segment | % of Target Users | Rationale |
|---|---|---|---|
| **P0** | Overloaded Optimist (Arjun) | 45% | Largest segment. Highest pain. Zero willingness to pay → perfect for Rs. 0. Drives course + task modules. |
| **P1** | Solo Builder (Priya) | 20% | Higher engagement + potential premium conversion. Drives income + time + project modules. |
| **P1** | Idea Generator (Rohan) | 20% | Highest idea volume → drives idea pipeline. Needs structure most. |
| **P2** | Self-Taught Switcher | 10% | Growing segment (15% YoY). Requires minor adaptations. High viral potential (posts about tool). |
| **P3** | Fresh Graduate | 5% | Valuable but currently out of focus. Revisit in Year 2 with career module expansion. |

---

## 6. Value Proposition & Competitive Positioning

### 6.1 The Unique Value Quadrant

```
                    ACTIVE INTELLIGENCE (Push)
                           │
                           │
          Second Brain ●   │   Magic   ● Motion
          OS (FREE)        │   ($228/yr)  ($228/yr)
                           │
                     ──────┼────── BROAD (Life)
      NARROW (Tasks)       │
                           │
           Todoist ●       │              ● Notion
           ($48/yr)        │              ($120/yr)
                           │
          Google ●         │         ● ClickUp
          Calendar (FREE)  │         ($120/yr)
                           │
                    PASSIVE INTELLIGENCE (Pull)
```

**Key insight:** Second Brain OS is the ONLY product in the Active Intelligence × Broad Life Coverage quadrant — and it is the ONLY free product in any quadrant.

### 6.2 Detailed Competitive Comparison

| Dimension | Second Brain OS | Notion | Todoist | Motion | ChatGPT | Obsidian |
|---|---|---|---|---|---|---|
| **Price** | Rs. 0 | $10/mo | $4/mo | $19/mo | $20/mo | Free |
| **Student-specific** | ✅ Full | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Generic |
| **AI Agent** | ✅ 8 sub-agents | ❌ AI Q&A only | ❌ None | ✅ AI scheduling | ✅ Chat only | ❌ None |
| **Proactive Push** | ✅ 6 cron jobs | ❌ Passive | ❌ Passive | ✅ Scheduling | ❌ Passive | ❌ Passive |
| **Offline-first** | ✅ PWA | ❌ Limited | ✅ Mobile | ❌ Web-only | ❌ Web-only | ✅ Local |
| **Privacy (Local AI)** | ✅ Ollama | ❌ Cloud | ❌ Cloud | ❌ Cloud | ❌ Cloud | ✅ Local |
| **Opportunity Radar** | ✅ 6 categories | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Income Tracking** | ✅ With hourly rate | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Course Management** | ✅ Full lifecycle | ❌ | ❌ | ❌ | ❌ | ❌ |
| **CGPA/Academics** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Multi-platform** | Web + PWA | All platforms | All platforms | Web + Mobile | Web + Mobile | Desktop + Mobile |

### 6.3 Defensible Competitive Advantages

| Advantage | Moat Type | Why Hard to Copy |
|---|---|---|
| **15 student-specific modules** | Product depth | Competitors would need 5+ new product lines. 455 hours of development. |
| **Rs. 0 on free-tier infra** | Business model | VC-backed companies must monetize. Cannot sustain free forever. |
| **Privacy-first local AI** | Architecture | Cloud AI providers (OpenAI, Anthropic, Google) physically cannot offer local-first. |
| **Active push architecture** | UX paradigm | Notion, Todoist, Obsidian built as "check when needed." Would need fundamental redesign. |
| **Dogfood development** | Quality | Developer is the user. Every bug is personal. Every feature is needed. |
| **Single-user focus** | Focus | General tools dilute across segments. Every decision optimized for one persona. |

### 6.4 Competitive Threat Assessment

| Threat | Timeline | Severity | Response |
|---|---|---|---|
| **Notion adds student templates + AI** | 2026-2027 | Medium | Templates are surface-level. Depth of 15 integrated modules is the real moat. |
| **Motion drops price for students** | 2026-2027 | Low | Still paid. Still no student-specific features. Still web-only. |
| **Claude/GPT launch persistent memory** | 2026-2027 | Medium | Still no proactive push. Still cloud-only. Still no student modules. |
| **New startup builds "Second Brain for Students"** | 2027-2028 | High | First-mover advantage + free + open-source = hard to displace. Community lock-in. |
| **Google adds student features to Tasks/Keep** | 2027-2028 | Medium | Google would need to deeply integrate across products — unlikely. |
| **College builds in-house portal with AI** | 2028-2030 | Low | Institutional software is universally poor UX. Not a threat. |

---

## 7. Product Vision — 5-Year Horizon

### 7.1 Horizon Map — Strategic Phases

```
SECOND BRAIN OS — 5-YEAR STRATEGIC ROADMAP
══════════════════════════════════════════════════════════════════════

YEAR 1 (2026-2027)           YEAR 2 (2027-2028)           YEAR 3 (2028-2029)
────────────────────────────────────────────────────────────────────────────────────►

┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ FOUNDATION               │  │ EXPANSION                │  │ ECOSYSTEM                │
│                          │  │                          │  │                          │
│ CORE:                    │  │ NEW PLATFORMS:           │  │ PLUGIN SYSTEM:           │
│ • 15 modules live        │  │ • Mobile app (React      │  │ • Community plugin       │
│ • ARIA + 8 agents        │  │   Native)                │  │   marketplace            │
│ • PromptLoader + prompts │  │ • Browser extension v2   │  │ • Plugin SDK + docs      │
│ • 6 cron jobs            │  │ • CLI tool               │  │ • Verified plugins       │
│ • Supabase RLS           │  │ • Desktop app (Tauri)    │  │                          │
│                          │  │                          │  │ API:                     │
│ METRICS:                 │  │ LANGUAGES:               │  │ • Public REST API        │
│ • 0-100 DAU              │  │ • Hindi + English        │  │ • API keys + rate limits │
│ • Rs. 0 infra cost       │  │ • Tamil, Telugu (Q4)     │  │ • Webhook support        │
│ • >60% 30-day retention  │  │                          │  │                          │
│ • 15 modules shipped     │  │ INSTITUTIONS:            │  │ METRICS:                 │
│ • PMF validated          │  │ • 5 pilot colleges       │  │ • 10,000 DAU             │
│                          │  │ • Student ambassador     │  │ • Revenue positive       │
│                          │  │   program                │  │ • 50+ plugins            │
│                          │  │ • Bulk deployment guide  │  │ • 100+ contributors      │
│                          │  │                          │  │                          │
│ TARGET:                  │  │ TARGET:                  │  │ TARGET:                  │
│ 100 DAU, 0 revenue       │  │ 1,000 DAU, Rs. 6-24K/yr │  │ 9,000 DAU, Rs. 2-5L/yr   │
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘

YEAR 4 (2029-2030)           YEAR 5 (2030-2031)
────────────────────────────────────────────────────────────────────────────────────►

┌──────────────────────────┐  ┌────────────────────────────────────────────────────┐
│ INTELLIGENCE NETWORK     │  │ AUTONOMOUS STUDENT OS                              │
│                          │  │                                                    │
│ AGENT NETWORK:           │  │ AUTONOMOUS FEATURES:                               │
│ • Cross-user agent       │  │ • Autonomous schedule builder                      │
│   collaboration (opt-in) │  │ • Learning path automation                         │
│ • Federated insights     │  │ • Career trajectory simulation                     │
│ • Skill graphs           │  │ • Auto-opportunity apply                          │
│                          │  │                                                    │
│ GLOBAL:                  │  │ NEW FRONTIERS:                                     │
│ • 10+ languages          │  │ • AR/VR study mode                                │
│ • Regional opportunity   │  │ • AI tutor integration                            │
│   scanning               │  │ • Peer learning network                           │
│ • Localized resources    │  │ • Universal skill passport (blockchain-verified)  │
│                          │  │ • Institutional accreditation                     │
│ MONETIZATION:            │  │                                                    │
│ • Enterprise licensing   │  │ METRICS:                                          │
│   (25+ colleges)         │  │ • 25,000+ DAU                                    │
│ • Premium AI credits     │  │ • Rs. 50L/year revenue                           │
│ • Marketplace revenue    │  │ • 200+ community contributors                     │
│                          │  │ • 25+ institutional partners                      │
│ TARGET:                  │  │ TARGET:                                           │
│ 16,000 DAU, Rs. 10-20L/yr│  │ 30,000 DAU, Rs. 30-60L/yr                        │
└──────────────────────────┘  └────────────────────────────────────────────────────┘
```

### 7.2 North Star Metrics (Year 5 Targets)

| Metric | Rationale | Year 1 | Year 3 | Year 5 |
|---|---|---|---|---|
| Total registered users | Reach indicates market penetration | 200 | 20,000 | 100,000+ |
| Daily active users | Engagement depth | 100 | 9,000 | 25,000+ |
| DAU/MAU ratio | Daily habit formation | >40% | >50% | >55% |
| Average user lifetime | Retention validates sustained value | >6 months | >12 months | >18 months |
| Net Promoter Score | User satisfaction | >40 | >50 | >60+ |
| Course completion rate | Core outcome metric | >70% | >75% | >80% |
| Projects shipped/user/year | Ultimate builder metric | >3 | >5 | >7 |
| Aggregate income through radar | Economic impact of product | Rs. 5L | Rs. 50L | Rs. 10Cr+ |
| Institutional partners | Distribution moat | 0 | 5 | 25+ |
| Community contributors | Ecosystem health | 1 (dev) | 50+ | 200+ |
| Annual revenue | Sustainability (not profit) | Rs. 0 | Rs. 2-5L | Rs. 50L+ |
| Monthly infra cost | Cost discipline | <Rs. 100 | <Rs. 500 | <Rs. 5,000 |

---

## 8. Technology Vision & Innovation Roadmap

### 8.1 Technology Stack — Current & Planned

| Layer | Current (2026) | Year 2 (2027) | Year 3+ (2028-2030) |
|---|---|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind | + React Native (mobile) | + Tauri (desktop), WASM modules |
| **Backend** | FastAPI, Python 3.10 | + WebSocket support | + GraphQL, edge functions |
| **Database** | Supabase PostgreSQL | + pgvector for semantic search | + Read replicas, sharding |
| **AI (Local)** | Ollama (Mistral 7B) | + Fine-tuned Mistral (LoRA) | + Custom small model (distilled) |
| **AI (Cloud)** | Claude API (fallback) | + GPT-4o-mini (second fallback) | + Multi-model router (cost-optimized) |
| **Search** | Brave Search API | + Google Programmable Search | + Custom crawler |
| **Email** | Resend | + SMTP fallback | + Transactional email service |
| **Auth** | Supabase Auth (Google OAuth) | + Magic link, GitHub OAuth | + Passkeys, WebAuthn |
| **Offline** | IndexedDB (idb library) | + Sync conflict resolution | + CRDT-based sync |
| **Caching** | In-memory TTL | + Redis (Upstash free tier) | + CDN caching layers |
| **Search** | Full-text (Supabase) | + pgvector semantic search | + Dedicated vector DB (Qdrant) |

### 8.2 AI Innovation Roadmap

```
AI CAPABILITY EVOLUTION
══════════════════════════════════════════════════════════════════════

PHASE 1 (2026) — BASIC AI INTEGRATION
├── Ollama Mistral 7B for chat
├── Claude fallback for complex tasks
├── PromptLoader with 12 prompt files
├── Basic context assembly (goals, tasks, courses)
├── 8 sub-agents with deterministic fallbacks
└── Daily briefing + weekly review + radar + nudge + sleep + memory + learning

PHASE 2 (2027) — ADVANCED AI
├── Fine-tuned Mistral 7B (LoRA) on student conversation data
├── Multi-model routing — route queries by complexity
├── RAG pipeline for resource/library search
├── Semantic cache — avoid duplicate AI calls
├── AI code review for project code (basic lint analysis)
└── Voice interface (Whisper → ARIA)

PHASE 3 (2028) — CONTEXTUAL AI
├── Predictive task prioritization (ML model trained on user behavior)
├── Learning path optimization — "Study this next for maximum career impact"
├── Opportunity match confidence scoring (ML, not just keyword)
├── Writing assistant for applications, resumes, LinkedIn posts
├── Emotional state detection (from engagement patterns)
└── Cross-user anonymized pattern insights (opt-in)

PHASE 4 (2029-2030) — AUTONOMOUS AI
├── Autonomous schedule builder — ARIA books your day
├── Auto-opportunity apply — "Apply on my behalf to top 3 matches"
├── Career trajectory simulation — "If you learn X, your income in 2 years = Y"
├── Personalized curriculum generation — "Build a course plan to become a DevOps engineer"
└── Mentor matching — AI connects students with alumni (opt-in)
```

### 8.3 Prompt Engineering Evolution

| Phase | Prompt Count | Complexity | Key Improvement |
|---|---|---|---|
| Phase 1 | 12 files (~20KB each) | Basic role + instructions + examples | Frontmatter validation, fallback to inline |
| Phase 2 | 15 files (~30KB each) | Agent chaining, context assembly | Cross-agent prompt consistency |
| Phase 3 | 20+ files (~40KB each) | Conditional branching, multi-turn | Dynamic prompt assembly based on user state |
| Phase 4 | 25+ files | Self-improving prompts | A/B tested prompt variants, auto-optimization |

### 8.4 Database Evolution

| Year | Tables | Estimated Data | Indexing Strategy |
|---|---|---|---|
| 1 | 18 | <200MB total | B-tree on user_id + created_at; partial indexes on status |
| 2 | 22 | <1GB total | + GIN for full-text; + pgvector for embeddings |
| 3 | 28 | <5GB total | + Composite indexes; + materialized views for dashboards |
| 4-5 | 35+ | <50GB total | + Partitioning by user_id hash; + read replicas |

---

## 9. Platform Strategy & Ecosystem

### 9.1 Platform Architecture (Year 3 Target)

```
                        ┌─────────────────────────────────────────────┐
                        │              SECOND BRAIN OS               │
                        │              ECOSYSTEM MAP                 │
                        └─────────────────────────────────────────────┘

  FRONTENDS                              BACKEND                          INFRASTRUCTURE
  ┌────────────────────┐                ┌────────────────────┐          ┌────────────────────┐
  │  Web App (Next.js) │                │                    │          │  Supabase          │
  │  - Dashboard       │                │  FastAPI + Uvicorn │◄────────►│  - PostgreSQL      │
  │  - All modules     │                │  - 13 routers      │          │  - Auth (Google)   │
  │  - PWA offline     │                │  - 53+ endpoints   │          │  - Storage         │
  └────────┬───────────┘                │  - Middleware stack │          │  - Realtime        │
           │                            └───────┬────────────┘          └────────────────────┘
  ┌────────▼───────────┐                        │
  │  Mobile (React Na- │                        │                    AI LAYER
  │  tive) — Year 2    │                        │              ┌────────────────────┐
  └────────────────────┘                        │              │  Ollama (Local)    │
                                                │◄────────────►│  - Mistral 7B      │
  ┌────────────────────┐                        │              │  - PromptLoader    │
  │  Desktop (Tauri)   │                        │              │  - 8 sub-agents    │
  │  — Year 3          │                        │              └────────┬───────────┘
  └────────────────────┘                        │                       │
                                                │              ┌────────▼───────────┐
  EXTENSIONS / API                              │              │  Claude API        │
  ┌────────────────────┐                        │              │  (Fallback)        │
  │  Browser Extension │◄───────────────────────┤              └────────────────────┘
  │  - WXT Framework   │                        │
  │  - Save any page   │                        │              SERVICES
  │  - Quick capture   │                        │              ┌────────────────────┐
  └────────────────────┘                        │              │  Scheduler         │
                                                │              │  - APScheduler     │
  ┌────────────────────┐                        │              │  - 6 cron jobs     │
  │  CLI Tool          │◄───────────────────────┤              │  - Retry logic     │
  │  - Python          │                        │              └────────────────────┘
  │  - Quick capture   │                        │
  │  - Status check    │                        │              EXTERNAL INTEGRATIONS
  └────────────────────┘                        │              ┌────────────────────┐
                                                │              │  Brave Search      │
  ┌────────────────────┐                        │              │  Resend (Email)    │
  │  Public API        │◄───────────────────────┤              │  GitHub API        │
  │  - REST + API keys │                        │              │  Twilio (SMS, min) │
  │  - Rate limited    │                        │              └────────────────────┘
  │  - Webhooks        │                        │
  └────────────────────┘                        │              COMMUNITY
                                                │              ┌────────────────────┐
  PLUGIN SYSTEM (Year 3)                        │              │  GitHub (Code)     │
  ┌────────────────────┐                        │              │  Discord (Chat)    │
  │  JS Sandbox        │◄───────────────────────┤              │  Documentation     │
  │  - Community       │                        │              └────────────────────┘
  │  - Verified only   │                        │
  │  - Marketplace     │                        │
  └────────────────────┘                        └────────────────────────────────────┘
```

### 9.2 Platform Rollout Schedule

| Platform | Phase | Tech Stack | Go-Live | Dependencies |
|---|---|---|---|---|
| **Web App** | Phase 1 (2026) | Next.js 14 + TypeScript + Tailwind | Jul 2026 | Supabase, FastAPI |
| **Browser Extension** | Phase 2 (Q4 2026) | WXT (Chrome + Firefox) | Oct 2026 | API layer |
| **CLI Tool** | Phase 2 (Q4 2026) | Python + Click | Nov 2026 | API layer |
| **Mobile App** | Phase 3 (Q3 2027) | React Native | Jul 2027 | API layer, auth |
| **Public API** | Phase 3 (Q4 2027) | FastAPI + API keys | Oct 2027 | Rate limiting, docs |
| **Desktop App** | Phase 4 (2028) | Tauri (Rust) + React | Jan 2028 | Mobile codebase |
| **Plugin System** | Phase 4 (Q3 2028) | JS sandbox (QuickJS) | Jul 2028 | API, SDK, docs |
| **Webhooks** | Phase 4 (Q4 2028) | Supabase webhooks | Oct 2028 | Public API |

### 9.3 Platform Principles

| Principle | Rationale | Implementation |
|---|---|---|
| **Web-first** | Zero install, cross-platform, PWA offline | All features work in browser first |
| **API-driven** | Every platform consumes same REST API | Enables extension ecosystem |
| **Offline-capable** | Hostel Wi-Fi, metered connections, travel | IndexedDB sync engine |
| **Extension as first-class** | Browser extension enables capture from anywhere | WXT cross-browser framework |
| **Plugin as safety valve** | Community extends without core bloat | JS sandbox, verified only |

---

## 10. Go-to-Market Strategy

### 10.1 GTM Philosophy

Second Brain OS follows a **zero-budget, organic-first** GTM strategy. There is no marketing spend, no ads, no sales team. Growth comes entirely from product quality, community building, and word-of-mouth.

### 10.2 GTM Phases

```
GO-TO-MARKET PHASES
══════════════════════════════════════════════════════════════════════

PHASE 0: PRE-LAUNCH (Jul 2026 — Mar 2027)
├── Dogfood development — developer uses daily
├── 2-3 close friends as alpha testers (structured feedback)
├── GitHub repo private, invite-only
├── Documentation written alongside code
├── No public presence
└── Goal: PMF validation with <10 users

PHASE 1: STEALTH LAUNCH (Mar 2027 — Jun 2027)
├── GitHub goes public
├── Hacker News "Show HN" post
├── Reddit (r/developersIndia, r/engineeringstudents)
├── Product Hunt launch
├── Dev.to / Medium post: "I built a free AI OS for students"
└── Goal: 50-100 users

PHASE 2: COMMUNITY (Jun 2027 — Dec 2027)
├── Discord server for user community
├── Feature voting (GitHub Discussions)
├── User success stories (opt-in case studies)
├── Student ambassador program (5-10 ambassadors)
├── Weekly changelog posts
└── Goal: 100-500 users

PHASE 3: INSTITUTIONAL (2028+)
├── Pilot colleges (5 initial)
├── Bulk deployment documentation
├── College club partnerships
├── Placement cell integrations (optional)
├── Workshop materials for student clubs
└── Goal: 500-5,000 users
```

### 10.3 Channel Strategy

| Channel | Reach | Cost | Expected Conversion | Priority |
|---|---|---|---|---|
| **Hacker News (Show HN)** | 10K-50K views | Rs. 0 | 0.5-2% → 50-1000 users | P0 (Launch) |
| **r/developersIndia** | 500K subscribers | Rs. 0 | 0.1-0.5% → 50-250 users | P0 (Launch) |
| **Product Hunt** | 20K-100K views | Rs. 0 | 0.1-1% → 20-100 users | P1 |
| **GitHub trending** | 100K+ views (if trending) | Rs. 0 | 0.05-0.2% → 50-200 users | P1 (Quality-dependent) |
| **YouTube dev channels** | — | Free-tier tools | Variable | P2 (Year 2) |
| **College workshops** | 50-200/workshop | Rs. 0 (virtual) | 10-30% → 5-60 users | P2 (Year 2) |
| **LinkedIn (student clubs)** | 1K-10K/club post | Rs. 0 | 1-5% → 10-500 users | P2 (Year 2) |

### 10.4 Viral Loops (Built-in)

| Loop | Mechanism | Expected Virality Coefficient (k) |
|---|---|---|
| **Portfolio sharing** | "Built with Second Brain OS" badge on shipped projects | k = 0.1-0.3 |
| **Dev.to / Medium blog** | Users write about system: "How I track my student life" | k = 0.05-0.1 |
| **GitHub fork → deploy** | Self-hosting naturally spreads through friend groups | k = 0.2-0.5 |
| **Opportunity sharing** | "Found this internship through my radar" — organic testimonial | k = 0.1-0.2 |

**Target:** k > 0.3 (each user brings >0.3 new users) for sustainable organic growth.

---

## 11. Stakeholder Value Map

### 11.1 Comprehensive Stakeholder Register

| ID | Stakeholder | Role | Interest Level | Power | Influence | Engagement Strategy | Success Criteria |
|---|---|---|---|---|---|---|---|
| S-01 | **Student User** | Primary user, daily operator | High | High | Direct feedback, usage data | User-centric design, feedback loops, community | Completes >15 tasks/week, finds >2 opps/week, ships >1 project/quarter |
| S-02 | **Developer** | Product builder, maintainer | High | High (decision-maker) | All product decisions | Dogfood dev, sustainable pace, celebrate milestones | All 15 modules live, <5 bugs/month, CI >95% |
| S-03 | **Early Testers** | Usability validators (2-5 friends) | Medium | Medium | Feature prioritization | Structured feedback forms, weekly check-ins, early access | 30-day retention >60%, NPS >30 |
| S-04 | **College Faculty** | Indirect beneficiary | Low | Low-Medium | Referral to students | Case study sharing, potential endorsements | Observe student organization improvement |
| S-05 | **Startup Employers** | Hiring beneficiary | Low | Low | Hiring signal from portfolios | Portfolio output speaks for itself | Candidate portfolios show real project experience |
| S-06 | **Open Source Community** | Future contributors (post-GA) | Medium-Medium | Medium (post-GA) | Code quality, extensions | Clear CONTRIBUTING.md, good-first-issues, docs | >5 external PRs, >100 GitHub stars |
| S-07 | **GitHub Sponsors / Donors** | Financial supporters (Year 2+) | Low | Low | Financial sustainability | Sponsorship tiers, transparency reports | Rs. 6,000-24,000/year in donations |
| S-08 | **Future Investors** | Capital providers (Year 3+) | Low | Low (future) | Growth data, metrics | Maintain metrics dashboard, growth narrative | >1,000 DAU, >70% retention, Rs. 0 infra |
| S-09 | **Institution Partners** | Distribution channel (Year 3+) | Low-Medium (future) | Medium | Bulk deployment | Pilot programs, case studies, bulk deploy docs | 5+ pilot colleges, 500+ institutional users |
| S-10 | **Competing Products** | Market incumbents (Notion, etc.) | Low | Low (implicit) | Competitive pressure | Focus on moats, ignore competitors | Maintain differentiated position |

### 11.2 Power-Interest Grid

```
INTEREST
    │
High    │ Early Testers (S-03)           Student Users (S-01)
        │                                 Developer (S-02)
        │
        │ College Faculty (S-04)
        │ Startup Employers (S-05)
        │ Institution Partners (S-09)
        │
Medium  │                                 Open Source Community (S-06)
        │
        │ GitHub Sponsors (S-07)          Future Investors (S-08)
        │
Low     └──────────────────────────────────────────► POWER
            Low              Medium           High
```

**Primary focus quadrant (High Power, High Interest):** Student Users + Developer — these drive all product decisions.

### 11.3 Stakeholder Communication Cadence

| Stakeholder | Frequency | Format | Content |
|---|---|---|---|
| Student Users | Continuous | In-app, release notes | Feature updates, tips, feedback prompts |
| Developer | Daily | Dogfood usage, GitHub issues | Bug tracker, feature checklist, CI status |
| Early Testers | Weekly | Structured form + optional call | Bugs, confusion points, feature requests |
| GitHub Community | Per release | Changelog, release post | What changed, how to upgrade |
| Faculty/Institutions | Quarterly | Case study, metrics update | Student outcomes, adoption data |

### 11.4 Stakeholder Conflict Resolution

| Conflict Scenario | Resolution Approach |
|---|---|
| Feature request from user vs. developer capacity | Prioritization matrix: Impact × Effort. User votes via GitHub discussions. |
| Open source contribution vs. code quality standards | Clear CONTRIBUTING.md with standards. Code review required. |
| Privacy (no data sharing) vs. community (want to compare) | Opt-in anonymized aggregates only. No individual comparisons. |
| Free forever vs. sustainability need | Premium AI credits (optional, no core feature paywall). Enterprise licensing. |

---

## 12. Success Metrics & Measurement Framework

### 12.1 North Star Metric

> **Builder Actions Per User Per Week (BAPU)**
> = tasks completed + courses progressed + projects shipped + income earned + opportunities applied to
>
> **Target:** >25 BAPU by Month 6, >40 BAPU by Year 3

This metric captures the core value proposition: the system helps students build real things. It's a composite that cannot be gamed (completing a trivial task adds less value than shipping a project phase, but both are captured).

### 12.2 OKR Framework — Hierarchical

```
HIERARCHICAL OKR STRUCTURE
══════════════════════════════════════════════════════════════════════

LEVEL 1: PRODUCT VISION (5-year)
  Objective: Transform how BTech CSE students manage their academic and
  professional lives.
  └── Key Results: 25,000+ DAU, Rs. 50L+ revenue, 25+ institutional partners

LEVEL 2: ANNUAL OKRs
  Year 1 (2026-2027):
  ├── Objective: Validate Product-Market Fit
  │   ├── KR1: 100 DAU (threshold: 30)
  │   ├── KR2: >60% 30-day retention
  │   ├── KR3: DAU/MAU >40%
  │   └── KR4: NPS >30
  │
  ├── Objective: Deliver Measurable Productivity Improvement
  │   ├── KR1: Avg task completion >15/week
  │   ├── KR2: Briefing read rate >80%
  │   ├── KR3: Avg courses completed/semester >3
  │   └── KR4: Radar match relevance >60%
  │
  └── Objective: Build Reliable Technical Foundation
      ├── KR1: API P95 <200ms
      ├── KR2: AI P95 <3s (or algorithmic fallback)
      ├── KR3: Uptime >99.9%
      ├── KR4: Lighthouse >90
      └── KR5: RLS on 100% of tables

LEVEL 3: QUARTERLY OKRs
  Q3 2026 (Jul-Sep):
  ├── Objective: Ship Core Foundation
  │   ├── KR1: Auth + Tasks + Courses + Goals live
  │   ├── KR2: Dashboard shows all core data
  │   └── KR3: Developer using daily for 1 week
  │
  └── Objective: Establish AI Foundation
      ├── KR1: ARIA chat functional with memory
      ├── KR2: Daily briefing generates correctly
      ├── KR3: PromptLoader loads all prompt files
      └── KR4: 30 tests passing

LEVEL 4: SPRINT OKRs (2-week sprints)
  Sprint 1:
  ├── Objective: Setup project infrastructure
  │   ├── KR1: Next.js + FastAPI + Supabase connected
  │   ├── KR2: Google OAuth login working
  │   └── KR3: Docker compose runs full stack
```

### 12.3 Module-Level Success Criteria

| Module | Primary KPI | Target | Measurement Method | Data Source |
|---|---|---|---|---|
| **Dashboard** | DAU/MAU ratio | >40% | (DAU / MAU) × 100 | Supabase auth events |
| **Dashboard** | First meaningful paint | <1.5s | Lighthouse CI | Lighthouse report |
| **Tasks** | Completed/week (per user) | >15 | COUNT(tasks WHERE status = completed AND week = current) | Weekly aggregate query |
| **Tasks** | Auto-reschedule accuracy | <15% re-rescheduled | COUNT(rescheduled tasks that were re-rescheduled within 7 days) | Cron audit log |
| **Courses** | Completion rate | >70% | COUNT(progress = 100) / COUNT(total courses) × 100 | Trigger on progress=100 |
| **Courses** | Deadlines met | >80% | COUNT(completed before deadline) / COUNT(had deadline) × 100 | Scheduled query |
| **Goals** | Goals with >50% progress | >3 | COUNT(goals WHERE progress >= 50) | Monthly query |
| **YouTube Vault** | Videos saved/week | >3 | COUNT(resources WHERE type = video) | Weekly aggregate |
| **Resources** | Resource-to-goal link rate | >50% | COUNT(goal_id IS NOT NULL) / COUNT(*) | Scheduled query |
| **Ideas** | Ideas moved to "building"/month | >1 | COUNT(status = building) | Monthly aggregate |
| **Opportunities** | Applied to/week | >2 | COUNT(status = applied) | Weekly aggregate |
| **Opportunities** | Radar match relevance | >60% with score >= 50 | match_score distribution | Distribution query |
| **Income** | Weeks logged | >70% | COUNT(DISTINCT iso_week) / total_weeks × 100 | Weekly cron |
| **Projects** | Phases completed | >3 | COUNT(phase WHERE status = completed) | Scheduled query |
| **Academics** | CGPA projection accuracy | Within ±0.2 | ABS(projected - actual CGPA) | Per-semester check |
| **Habits** | Consistency rate (30-day) | >50% | (completed_logs / expected_logs) × 100 | Daily cron |
| **Sleep** | Nights logged/week | >4 | COUNT(sleep_logs per week) | Weekly aggregate |
| **Sleep** | Avg duration | >7h | AVG(duration) per week | Weekly aggregate |
| **Time** | Deep work hours/week | >10 | SUM(duration WHERE deep_work = true) | Weekly aggregate |
| **Time** | Tracked vs estimated ratio | >80% | SUM(time_entries.duration) / SUM(tasks.estimated_duration) × 100 | Cron |
| **Briefing** | Read within 1 hour | >80% | daily_briefings.was_read AND read_at - created_at < 1h | Cron + trigger |
| **Review** | Sunday generation rate | 100% | COUNT(weekly_reviews.created_at on Sunday) | Weekly check |
| **Chat** | Sessions/week (>3 msgs) | >5 | COUNT(sessions with >= 3 messages) | Weekly aggregate |
| **Memory** | 30-day retention of persisted facts | >90% | COUNT(memory WHERE not discarded) / COUNT(memory created 30 days ago) × 100 | Cron |

### 12.4 Business-Level KPIs

| KPI | Year 1 Target | Year 3 Target | Year 5 Target | Measurement | Frequency |
|---|---|---|---|---|---|
| Daily Active Users | 100 | 9,000 | 25,000 | Supabase auth.sign_in | Daily |
| Monthly Active Users | 200 | 15,000 | 40,000 | 30-day rolling unique | Monthly |
| 30-Day Retention | >60% | >65% | >70% | Cohort analysis | Rolling 30 days |
| 90-Day Retention | >40% | >50% | >55% | Cohort analysis | Rolling 90 days |
| NPS | >30 | >50 | >60 | Quarterly survey | Quarterly |
| Avg User Lifetime | >6 months | >12 months | >18 months | Churn analysis | Quarterly |
| Organic Referral Rate | >0.3 | >0.4 | >0.5 | Referral tracking | Monthly |
| Infra Cost (monthly) | <Rs. 100 | <Rs. 500 | <Rs. 5,000 | Cost dashboard | Monthly |
| CI Pass Rate | >95% | >97% | >99% | GitHub Actions | Per commit |
| P0-P1 Bug Count | <5/month | <3/month | <1/month | GitHub issues | Monthly |
| Feature Adoption (3+ modules) | >80% | >90% | >95% | Usage analytics | Monthly |
| New Users (monthly) | 15-20 | 500-1000 | 2000-3000 | Signup analytics | Monthly |
| GitHub Stars | >100 | >1,000 | >5,000 | GitHub | Monthly |
| External Contributors | >5 | >50 | >200 | GitHub | Monthly |

### 12.5 Measurement Infrastructure

```
METRICS COLLECTION PIPELINE
══════════════════════════════════════════════════════════════════════

SOURCE DATA ──────────► COLLECTION ──────────► STORAGE ──────────► DASHBOARD
                               │                                        │
┌────────────────────┐        │                               ┌────────────────────┐
│ Supabase           │        │                               │ Weekly metrics     │
│ ┌──────────────┐   │        │                               │ report (email)     │
│ │ Auth events  │───┼────────┼──────────────────────────────►│                    │
│ │ Table CRUD   │───┼────────┼──────────────────────────────►│ Growth: DAU, MAU,  │
│ │ Query logs   │───┼────────┼──────────────────────────────►│ retention, NPS     │
│ └──────────────┘   │        │                               │                    │
└────────────────────┘        │                    ┌─────────►│ Engagement: tasks, │
                              │                    │          │ courses, projects  │
┌────────────────────┐        │                    │          │                    │
│ GitHub API          │        │    ┌─────────────┐ │          │ Quality: perf,     │
│ ┌──────────────┐   │        │    │ SQL Views    │ │          │ bugs, uptime       │
│ │ Stars        │───┼────────┼────┤ & Analytics  ├─┤          │                    │
│ │ Contributors │───┼────────┼────┤ Queries      │ │          │ Cost: infra        │
│ └──────────────┘   │        │    └─────────────┘ │          │ spending           │
└────────────────────┘        │                    │          └────────────────────┘
                              │                    │
┌────────────────────┐        │                    │          AD-HOC QUERIES
│ Lighthouse CI       │        │                    │          ┌────────────────────┐
│ ┌──────────────┐   │        │                    │          │ psql / Supabase    │
│ │ Perf scores  │───┼────────┼────────────────────┼─────────►│ SQL editor         │
│ │ Access.      │───┼────────┼────────────────────┤          │ python -c "query"  │
│ │ SEO scores   │───┼────────┼────────────────────┘          └────────────────────┘
│ └──────────────┘   │        │
└────────────────────┘        │
                              │
┌────────────────────┐        │
│ Application Logs    │        │
│ ┌──────────────┐   │        │
│ │ Error rates  │───┼────────┼────────────────────────────────►
│ │ AI response  │───┼────────┼────────────────────────────────►
│ │ times        │   │        │
│ └──────────────┘   │        │
└────────────────────┘        │
```

---

## 13. Brand Architecture & Positioning

### 13.1 Brand Identity

| Component | Definition | Implementation |
|---|---|---|
| **Product Name** | Second Brain OS | Used in all external communication |
| **Short Name** | ARIA OS | Used in UI, code, community |
| **Tagline** | "Your AI Operating System for Student Life" | Strapline on all marketing |
| **Mission Statement** | To make every student a builder | Internal north star |
| **Voice** | Direct, technical, honest, empathetic | Concise UI text, no fluff |
| **Visual Identity** | Cyberpunk (dark theme, neon accents) | Design tokens in tailwind.config.js |
| **Mascot** | ARIA — no anthropomorphism, text-based | AI agent, not a character |

### 13.2 Brand Promise

> **"Second Brain OS will never lose what matters, never miss what's possible, and never cost what you don't have."**

This promise has three components:
1. **Never lose what matters** — Zero-miss policy on tasks, resurface engine for saved content, persistent memory for AI facts
2. **Never miss what's possible** — Opportunity radar scans 6 categories daily, deadline alerts, learning path optimization
3. **Never cost what you don't have** — Rs. 0 forever for core product, runs on free infrastructure, offline capable

### 13.3 Positioning Statement

> **For BTech CSE students who are overwhelmed by fragmented tools and missed opportunities, Second Brain OS is the free, AI-powered productivity system that connects courses, tasks, ideas, opportunities, and income into one intelligent platform — unlike Notion, Todoist, or ChatGPT, it pushes proactive intelligence instead of waiting to be asked, and it costs exactly Rs. 0.**

### 13.4 Brand Guidelines

| Guideline | Rule | Exception |
|---|---|---|
| Use "Second Brain OS" in formal docs | Always capitalize. Never "Second Brain Os" or "second brain os" | In code: `second-brain-os` |
| Use "ARIA" for AI agent | ARIA is an acronym (AI Resource for Intelligent Assistance). Not a person. | Never anthropomorphize |
| Price capitalization | "Rs. 0" — never "free" as primary value prop | "Rs. 0 forever" in features section |
| Privacy messaging | "Your data never leaves your control" — never "we protect your data" | Implies trust in us vs. technical reality |
| Student-first language | "Builders" not "users." "Ship" not "deploy." "Projects" not "tasks." | In technical docs, use standard terms |

### 13.5 Brand No-Nos

| Don't Say | Why | Say Instead |
|---|---|---|
| "AI-powered" as primary descriptor | Vague, overused | "Active intelligence that pushes when it matters" |
| "Free productivity app" | Undersells differentiation | "Your personal AI operating system" |
| "Student planner" | Too narrow | "Complete student OS — courses, tasks, radar, income" |
| "Like Notion but..." | Positioning as inferior alternative | "The only system that connects learning → building → income" |
| "We protect your data" | Implies trust relationship | "Your data never leaves your Supabase instance. Local AI." |

---

## 14. Monetization Philosophy & Sustainability

### 14.1 Core Principle

> **Second Brain OS is Rs. 0 forever for the core product.**

This is a philosophical commitment, not a temporary promotional decision. The rationale:

1. **Students cannot pay.** The product must be free for those who need it most. A student with Rs. 1,000/month for all expenses cannot afford a $10/month SaaS tool.
2. **If the product provides genuine value, the builder benefits indirectly** — through better internships, higher freelance rates, more shipped projects. The ROI comes through career growth, not through cost savings on the tool.
3. **Monetization must never degrade the free experience.** Zero-tier users get the same product as premium users. Premium is additional AI compute, not core feature access.

### 14.2 Monetization Ladder

```
MONETIZATION LADDER
══════════════════════════════════════════════════════════════════════

  ZERO-TIER (100% free, forever)
  ╔══════════════════════════════════════════════════════════════════╗
  ║  • All 15 modules               • ARIA chat with memory         ║
  ║  • Daily briefing               • Weekly review                 ║
  ║  • Opportunity radar            • Offline mode                  ║
  ║  • Data export (JSON+CSV)       • PromptLoader all prompts      ║
  ║  • 6 cron jobs                  • All sub-agents                ║
  ╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
  TIER 1: DONATIONS (Year 2+)
  ╔══════════════════════════════════════════════════════════════════╗
  ║  • GitHub Sponsors              • Buy Me a Coffee                ║
  ║  • Target: Rs. 500-2,000/month  • 100% voluntary                ║
  ╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
  TIER 2: PREMIUM AI CREDITS (Year 3+)
  ╔══════════════════════════════════════════════════════════════════╗
  ║  • Additional Claude API calls  • Priority AI processing         ║
  ║  • Rs. 99/month                 • Estimated 2% conversion        ║
  ║  • Core product unchanged       • Pure AI compute upgrade        ║
  ╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
  TIER 3: MARKETPLACE (Year 3+)
  ╔══════════════════════════════════════════════════════════════════╗
  ║  • Plugin marketplace           • Template marketplace           ║
  ║  • Platform cut: 20%            • Community creators earn        ║
  ╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
  TIER 4: ENTERPRISE LICENSING (Year 4+)
  ╔══════════════════════════════════════════════════════════════════╗
  ║  • College-wide deployment      • Bulk deployment support        ║
  ║  • Custom integrations          • Analytics dashboard            ║
  ║  • $5K-10K/year per institution • 25+ colleges by Year 5         ║
  ╚══════════════════════════════════════════════════════════════════╝
```

### 14.3 Revenue Projections

| Year | Primary Sources | Monthly Revenue | Annual Revenue | Profitability |
|---|---|---|---|---|
| 2026 | Indirect (portfolio value, career ROI) | Rs. 0 | Rs. 0 | Break-even (Rs. 0 infra) |
| 2027 | Donations + Sponsorships | Rs. 500-2,000 | Rs. 6,000-24,000 | Break-even |
| 2028 | Premium AI (2% of 9K = 180 users × Rs. 99) + Marketplace | Rs. 20,000-40,000 | Rs. 2-5 lakhs | Rs. 1-4 lakhs surplus |
| 2029 | Premium + Marketplace + Enterprise (5 colleges × Rs. 5L) | Rs. 80,000-150,000 | Rs. 10-20 lakhs | Rs. 8-18 lakhs surplus |
| 2030 | Full suite: Premium + Marketplace + Enterprise (25 colleges) | Rs. 2.5-5 lakhs | Rs. 30-60 lakhs | Rs. 25-55 lakhs surplus |

### 14.4 Sustainability Commitments

| Commitment | Rationale | Enforcement |
|---|---|---|
| **Core product never paywalled** | Philosophical commitment | Enshrined in AGENTS.md |
| **Premium = more AI compute, not features** | Fairness — no feature discrimination | Technical: feature flags cover ALL features in free tier |
| **User data never monetized** | Privacy by default | Technical: data cannot be accessed, period |
| **No ads, no tracking, no telemetry** | Zero surveillance | No analytics SDKs (no GA, no Mixpanel) |
| **Transparent finances** | Community trust | Annual transparency report (post-Year 2) |
| **Exit clause: open-source survives** | If project stops, community can fork | MIT license; all data in standard SQL |

### 14.5 What Monetization Will NEVER Look Like

| Practice | Why It's Rejected |
|---|---|
| Selling user data | Violates every privacy principle. Zero exceptions. |
| Ads in the product | Destroys user experience. Zero-revenue product doesn't need ads. |
| Paywalling core features | "Rs. 0 forever" is a promise, not a lead magnet. |
| VC-funded growth hacking | Dark patterns and growth-at-all-costs incompatible with ethos. |
| Dark patterns / upsells | Manipulative design rejected. No "upgrade now" popups. |
| Usage caps on free tier | Soft limits only (e.g., AI rate limits). No hard feature blocks. |
| Data lock-in | Full JSON/CSV export from Day 1. Users can leave anytime. |

---

## 15. Community & Contributor Strategy

### 15.1 Community Growth Phases

| Phase | Timeline | Contributors | User Base | Community Infrastructure |
|---|---|---|---|---|
| **Solo** | 2026 | 1 (developer) | 0 (pre-launch) | None (private GitHub) |
| **Seed** | Q1-Q2 2027 | 2-5 (friends + early testers) | 10-50 | GitHub Issues + private Discord |
| **Early** | Q3-Q4 2027 | 5-20 | 50-500 | Public Discord + GitHub Discussions |
| **Growing** | 2028 | 20-100 | 500-5,000 | Discord + GitHub + Documentation site |
| **Thriving** | 2029+ | 100-500 | 5,000-50,000+ | Full community platform (Discourse optional) |

### 15.2 Contribution Opportunity Matrix

| Contribution Type | Skill Level | Time Required | Impact | Recognition |
|---|---|---|---|---|
| **Bug report with reproduction** | Beginner | 15-30 min | High | GitHub Hall of Fame |
| **Documentation improvement** | Beginner | 1-3 hours | Medium | Contributors list |
| **Translation/i18n** | Intermediate | 2-5 hours | High | Language credit on homepage |
| **Prompt engineering** | Intermediate | 3-8 hours | Medium | Prompt contributor badge |
| **UI/UX design** | Intermediate | 4-12 hours | High | Design credit + portfolio piece |
| **Plugin development** | Advanced | 8-40 hours | High | Plugin marketplace listing |
| **Core feature** | Advanced | 16-80 hours | Very high | Core contributor status |
| **Security audit** | Expert | 8-20 hours | Critical | Security acknowledgments |
| **Performance optimization** | Expert | 8-30 hours | High | Performance contributor badge |

### 15.3 Community Governance

| Principle | Implementation |
|---|---|
| **Benevolent Dictator** | Developer has final decision on all product decisions |
| **Transparent Roadmap** | Public GitHub Project board with priorities |
| **RFC Process** | Major features require RFC (Request for Comments) issue |
| **Code of Conduct** | Enforced CODE_OF_CONDUCT.md |
| **DCO** | All contributions require Developer Certificate of Origin |
| **Decision Log** | ADRs for all architecture decisions |
| **Recognition** | CONTRIBUTORS.md file, release notes shoutouts |

---

## 16. Risk Management & Vision Safeguards

### 16.1 Comprehensive Risk Register

| ID | Risk | Category | Probability | Impact | Risk Score | Detection Method | Mitigation | Contingency | Owner |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Developer burnout | Team | 0.7 | 0.9 | 0.63 | Self-assessment, missed milestones | 10-15 hr/week max; celebrate phases; rest during exams | Reduce scope to 8 core modules; Pause project; Resume when ready | Developer |
| R02 | Low adoption (<10 users) | Market | 0.4 | 0.8 | 0.32 | Signup analytics, weekly review | Organic launch to close network; Hacker News post | Accept as personal tool; Open-source community | Developer |
| R03 | AI API costs exceed budget | Technical | 0.5 | 0.7 | 0.35 | Cost dashboard, monthly audit | Ollama for 80%; Claude fallback; algorithmic safety net | Switch 100% to Ollama; Reduce AI features; Use only free AI | Developer |
| R04 | Supabase free tier limits | Technical | 0.4 | 0.7 | 0.28 | Usage dashboard, limit monitoring | Paginate; cache aggressively; compress; archive old data | Migrate to Neon.tech free tier; SQLite for critical offline data | Developer |
| R05 | Competitor launches free student AI | Market | 0.5 | 0.5 | 0.25 | Competitive monitoring (monthly scan) | Student-specific moat; privacy differentiator; depth of 15 modules | Accelerate community building; Deepen institutional partnerships | Developer |
| R06 | Technical debt slows velocity | Technical | 0.6 | 0.6 | 0.36 | Sprint velocity tracking, code review | Lint + type-check in CI; refactor per module; ADR documentation | Dedicate 20% of sprint to debt reduction; Rewrite problem module | Developer |
| R07 | AI responses disappoint users | Product | 0.5 | 0.7 | 0.35 | User feedback, chat ratings | Gradual AI rollout with feature flags; algorithmic fallback always available | Improve prompt engineering; Fine-tune model; Lower expectations in UX | Developer |
| R08 | Security incident | Security | 0.2 | 0.9 | 0.18 | CI security scan; RLS audit; dependency audit | RLS on all tables; no client-side keys; regular security review | Rotate all keys; Restore from backup; Security disclosure | Developer |
| R09 | Platform dependency lock-in | Technical | 0.4 | 0.6 | 0.24 | Annual platform review | Dockerfile for portability; standard SQL; avoid proprietary features | Migration runbook per platform; Store migration tested quarterly | Developer |
| R10 | Motivation decline | Team | 0.5 | 0.8 | 0.40 | Self-assessment, milestone progress | Community post-launch creates accountability; Celebrate small wins | Take break; Reduce scope; Accept slower pace | Developer |
| R11 | User data loss | Technical | 0.2 | 0.9 | 0.18 | Automated backup verification, sync tests | IndexedDB + Supabase dual storage; point-in-time recovery; regular exports | Restore from backup (RPO < 1 hour); Data recovery guide | Developer |
| R12 | Browser extension rejected | External | 0.3 | 0.4 | 0.12 | Store submission status | WXT cross-browser; sideload guide as fallback | Distribute via GitHub releases; Manual install guide | Developer |
| R13 | Feature scope creep | Product | 0.7 | 0.5 | 0.35 | Quarterly scope review; "Builder Test" filter | Every new feature passes Builder Test: "Does this help a student build something?" | Quarterly scope pruning; Move features to "deferred" | Developer |
| R14 | Legal/compliance issues | Legal | 0.1 | 0.8 | 0.08 | Regulatory monitoring (annual) | MIT license; no user data collection beyond functional needs | Legal consultation; Adjust compliance posture | Developer |
| R15 | Open source community conflict | Community | 0.2 | 0.5 | 0.10 | Community health monitoring | CODE_OF_CONDUCT; transparent governance; maintainer veto power | Fork is acceptable; MIT license permits it | Developer |

### 16.2 Risk Heat Map (Qualitative)

```
PROBABILITY
    │
0.9  │                                                         R01
    │
0.7  │                       R13             R06    R10
    │
0.5  │          R05         R03  R07                  R02
    │
0.3  │ R12                                        R04
    │
0.1  │                            R08 R11               R14
    │     R15
    └────────────────────────────────────────────────────► IMPACT
        0.1     0.3     0.5     0.7     0.9
```

**Critical zone (red):** R01 (burnout), R10 (motivation decline) — both team risks that can kill the project.
**High zone (orange):** R03 (AI costs), R06 (tech debt), R07 (AI quality), R02 (adoption), R13 (scope creep).
**Medium zone (yellow):** R04 (Supabase limits), R05 (competition).
**Low zone (green):** R08 (security), R11 (data loss), R12 (extension), R14 (compliance), R15 (community).

### 16.3 Risk Mitigation Budget

| Risk Category | Preventive (hours/quarter) | Detective (hours/quarter) | Corrective (hours/year) | Annual Total |
|---|---|---|---|---|
| Technical | 15 (audits, backups, updates) | 10 (monitoring, alerting) | 30 (incident response, fixes) | 130 |
| Team/Process | 10 (sprint planning, retrospectives) | 5 (velocity tracking) | 15 (scope adjustment, breaks) | 75 |
| Market/Product | 10 (competitive scan, user research) | 5 (analytics review) | 10 (pivot planning) | 70 |
| Security/Legal | 5 (security review, dependency audit) | 5 (compliance check) | 5 (incident response) | 45 |
| **Total** | **40** | **25** | **60** | **~320 hours (20% of dev time)** |

### 16.4 Vision Execution Checkpoints

| Checkpoint | Timeline | Continue Criteria | Pivot Criteria | Abandon Criteria |
|---|---|---|---|---|
| **Phase 1 Complete** | Week 4 | Working app with auth, tasks, courses, dashboard | Reduce to 8 core modules; skip advanced features | Replace with simpler tool |
| **3-Month Review** | Month 3 | >10 users using weekly; developer using daily | Focus on top 3 modules; eliminate rest | Accept as personal tool; stop active development |
| **6-Month Review** | Month 6 | >30 users; >60% 30-day retention | Switch target segment; add features for different audience | Open-source and archive |
| **1-Year Review** | Month 12 | >100 users; organic growth; positive NPS (>30) | Monetize early (premium); pivot to different user base | Archive project; document lessons |
| **Year 2 Review** | Month 24 | >500 users; >50% retention; community growing | Expand to institutional; add mobile | Hand over to community; reduce personal involvement |
| **Year 3 Review** | Month 36 | >5,000 users; revenue positive | Accelerate enterprise; raise seed funding | Sustainable niche product; no growth pressure |

---

## 17. Implementation Roadmap & Milestones

### 17.1 Phase Timeline — 50-Week Development Plan

| Phase | Start | End | Duration | Weeks | Category | Milestone |
|---|---|---|---|---|---|---|
| Phase 1 — Core Foundation | Jul 6, 2026 | Jul 26, 2026 | 3 weeks | 1-3 | Core | Working app with login, tasks, courses, dashboard |
| Phase 2 — Save Everything | Jul 27, 2026 | Aug 16, 2026 | 3 weeks | 4-6 | Core | Content capture modules, browser extension |
| Phase 3 — ARIA & Core AI | Aug 17, 2026 | Sep 13, 2026 | 4 weeks | 7-10 | AI | ARIA chat, daily briefing, weekly review |
| **ALPHA** | **Sep 13, 2026** | — | — | 10 | — | All 15 modules + basic AI |
| Phase 4 — Advanced AI | Sep 14, 2026 | Oct 18, 2026 | 5 weeks | 11-15 | AI | Learning agent, radar, context engine, sleep, nudge |
| **BETA** | **Oct 18, 2026** | — | — | 15 | — | Advanced AI complete |
| Phase 5 — Roadmap Engine | Oct 19, 2026 | Nov 8, 2026 | 3 weeks | 16-18 | Core | Visual roadmap builder, AI parsing |
| Phase 6 — Full Life Tracking | Nov 9, 2026 | Jan 3, 2027 | 8 weeks | 19-26 | Core | Income, projects, academics, habits |
| Phase 7 — Monitoring | Jan 4, 2027 | Jan 31, 2027 | 4 weeks | 27-30 | Core | Reminders, sleep, time tracking |
| Phase 8 — Polish & PWA | Feb 1, 2027 | Feb 14, 2027 | 2 weeks | 30-31 | Infrastructure | PWA, offline, security audit |
| **GA CANDIDATE** | **Feb 14, 2027** | — | — | 31 | — | Stable, complete feature set |
| Phase 9 — Public Release | Feb 15, 2027 | Mar 21, 2027 | 5 weeks | 32-36 | Community | GitHub public, community infrastructure |
| **GA LAUNCH** | **Mar 21, 2027** | — | — | 36 | — | Public availability |
| Buffer / Exam Weeks | Mar 22, 2027 | May 16, 2027 | 8 weeks | 37-44 | Buffer | Contingency + mobile preview |
| Post-GA Stabilization | May 17, 2027 | Jun 27, 2027 | 6 weeks | 45-50 | Stabilization | Bug fixes, performance, v2 planning |

### 17.2 Critical Milestones (Gates)

| ID | Milestone | Date | Deliverable | Gate Criteria | Verification |
|---|---|---|---|---|---|
| M1 | Auth + Tasks | Jul 19, 2026 | Login + task CRUD | Can login with Google, create/edit/complete/delete tasks | Manual test |
| M2 | Courses + Goals | Jul 26, 2026 | Course + goal tracking | Course with progress, goal with milestones, both persisted | Manual test + DB check |
| M3 | Full Dashboard | Jul 26, 2026 | Dashboard overview | All core modules visible, widgets render data | Visual inspection |
| M4 | Content Capture | Aug 16, 2026 | YouTube + Resources + Ideas | All three save modules operational with validation | Manual test per module |
| M5 | ARIA Chat | Aug 30, 2026 | AI chat with memory | Chat responds; remembers user facts across sessions | Chat test + memory check |
| M6 | Daily Briefing | Sep 6, 2026 | 7 AM AI briefing | Briefing generates daily, delivers in-app + email | 5-day verification |
| M7 | Weekly Review | Sep 13, 2026 | Sunday AI review | Review generates with narrative + data | 3-week verification |
| M8 | **ALPHA** | Sep 13, 2026 | Complete system | 30 tests pass; developer using daily for 1 week | Test suite + dogfood log |
| M9 | Opportunity Radar | Oct 4, 2026 | Daily opportunity scans | ≥3 relevant matches found daily across 6 categories | 7-day verification |
| M10 | Context Engine | Oct 11, 2026 | Full context assembly | AI responses include user's goals, tasks, courses | Chat test with context |
| M11 | Sleep + Nudge | Oct 18, 2026 | Automated agents | Wind-down 9:30 PM; nudge 6 PM | 5-day verification each |
| M12 | **BETA** | Oct 18, 2026 | Advanced AI | 8 agents operational; 30+ tests | Test suite + dogfood |
| M13 | Roadmap Builder | Nov 8, 2026 | Visual + AI roadmap | Drag-drop + text-to-roadmap both work | Manual test both paths |
| M14 | Income + Projects | Dec 6, 2026 | Income/project tracking | Log income; track project phases; calculate hourly rate | Manual test + calc check |
| M15 | Academics + CGPA | Dec 20, 2026 | Academic planning | CGPA projected within 0.2 of actual | Test with mock data |
| M16 | Habits + Streaks | Jan 3, 2027 | Habit engine | Streaks tracked; consistency reports; miss detection | 14-day test |
| M17 | Monitoring Suite | Jan 31, 2027 | Time/sleep/reminders | All three monitoring modules operational | Manual test per module |
| M18 | PWA + Offline | Feb 7, 2027 | Production-ready PWA | Lighthouse >90; offline CRUD works; sync on reconnect | Lighthouse + offline test |
| M19 | **GA CANDIDATE** | Feb 14, 2027 | Stable release | All tests pass; security audit OK; performance OK | Full test suite |
| M20 | PUBLIC LAUNCH | Mar 7, 2027 | GitHub public | README, demo, deploy guide, community infra | Public repo + docs |
| M21 | **GA** | Mar 21, 2027 | General availability | Community infrastructure live; launch post published | Public availability |

### 17.3 Development Effort Breakdown by Category

| Category | Hours | % of Total | Key Activities |
|---|---|---|---|
| **Frontend (Next.js + TypeScript)** | 160 | 35% | 15 page modules, dashboard widgets, PWA, UI components |
| **Backend (FastAPI + Supabase)** | 120 | 26% | 13 routers, 53 endpoints, middleware, auth, RLS |
| **AI & Prompts (Ollama + PromptLoader)** | 80 | 18% | 8 agent modules, 12 prompt files, context assembly, prompt validation |
| **Infrastructure & DevOps** | 30 | 7% | Docker, CI/CD, Railway, Vercel, environment setup |
| **Testing & QA** | 30 | 7% | Pytest suite, prompt tests, manual testing, dogfood |
| **Documentation** | 25 | 5% | AGENTS.md, doc files, README, deploy guide |
| **Community & Release** | 10 | 2% | GitHub setup, product hunt, launch posts |
| **Total** | **~455** | **100%** | |

### 17.4 Buffer Allocation

| Buffer Type | Weeks | Usage | Timing |
|---|---|---|---|
| **Exam buffer (Mid-sem)** | 2 | Reduced output during mid-semester exams | Oct 2026 |
| **Exam buffer (End-sem)** | 2 | Reduced output during end-semester exams | Dec 2026 |
| **Technical buffer** | 3 | Unexpected bugs, integration issues, dependency problems | Distributed |
| **Health/personal buffer** | 1 | Illness, family events | Distributed |
| **Total buffer** | **8 weeks** | Embedded in 52-week plan | |

---

## 18. Data Governance & Privacy Vision

### 18.1 Data Classification

| Classification | Description | Examples | Storage | Access |
|---|---|---|---|---|
| **User Content** | Data explicitly created by user | Tasks, course entries, income logs, ideas | Supabase PostgreSQL (encrypted at rest) | User only (RLS) |
| **AI-Generated** | Content created by ARIA agents | Briefings, reviews, radar matches, nudges | Supabase PostgreSQL | User only (RLS) |
| **User Profile** | Account and preference data | Skills list, notification prefs, theme | Supabase Auth + PostgreSQL | User only (RLS) |
| **Anonymous Usage** | Aggregated, non-identifiable metrics | DAU count, avg task completion rate | Local only (not collected) | Not collected |
| **Authentication Data** | OAuth tokens, sessions | Google OAuth tokens, JWT sessions | Supabase Auth | Supabase only |

### 18.2 Data Principles

| Principle | Implementation | Enforcement |
|---|---|---|
| **Data Minimization** | Only collect data needed for functionality | No analytics SDKs (no GA, Mixpanel, etc.) |
| **Purpose Limitation** | Data used only for its stated purpose | No secondary data use |
| **User Ownership** | User owns all their data | Full export (JSON+CSV); Account deletion = full purge |
| **Transparency** | Exactly what data is stored, where, how | Privacy section in README; data schema documented |
| **Portability** | User can take data anywhere | Standard Supabase schema; standard SQL; export endpoint |

### 18.3 What We NEVER Collect

| Data Type | Justification for Not Collecting |
|---|---|
| Location data | Not needed for any feature |
| Contact list / address book | Not needed; no social features |
| Browsing history (outside extension scope) | Extension only accesses URLs user explicitly saves |
| Device identifiers | Not needed; auth is session-based |
| Biometric data | Not applicable |
| Payment information | Rs. 0 — no payments processed in core product |
| Behavioral telemetry | No GA, Mixpanel, Hotjar, or similar |

### 18.4 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SECURITY ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  AUTHENTICATION                        AUTHORIZATION                │
│  ┌────────────────────────┐           ┌────────────────────────┐   │
│  │ Google OAuth 2.0       │           │ Row-Level Security     │   │
│  │ JWT tokens (HS256)     │           │ (RLS) on ALL 18 tables │   │
│  │ 30-day session timeout │           │ user_id = auth.uid()   │   │
│  │ Passwordless (no pwd)  │           │ FOR ALL operations     │   │
│  └────────────────────────┘           └────────────────────────┘   │
│                                                                     │
│  DATA IN TRANSIT                         DATA AT REST               │
│  ┌────────────────────────┐           ┌────────────────────────┐   │
│  │ HTTPS (TLS 1.3)        │           │ Supabase encrypted DB  │   │
│  │ API calls via HTTPS    │           │ Encryption at rest     │   │
│  │ No plaintext tokens    │           │ (managed by Supabase)  │   │
│  └────────────────────────┘           └────────────────────────┘   │
│                                                                     │
│  APPLICATION SECURITY                   DEPENDENCY MANAGEMENT      │
│  ┌────────────────────────┐           ┌────────────────────────┐   │
│  │ Input sanitization     │           │ npm audit (CI)          │   │
│  │ No eval/exec in JS     │           │ pip audit (CI)          │   │
│  │ Rate limiting          │           │ DCO for contributions   │   │
│  │ CORS whitelist         │           │ License compatibility   │   │
│  └────────────────────────┘           └────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 18.5 Future Data Vision

| Year | Data Capability | Privacy Impact |
|---|---|---|
| 1 | Basic CRUD + RLS | No change — all data user-owned |
| 2 | pgvector for semantic search | Embeddings stored locally; never sent externally |
| 3 | Cross-user anonymized insights (opt-in) | Aggregated only; no individual data shared |
| 4 | Federated learning (opt-in) | Models trained locally; only weights shared |
| 5 | Decentralized data (local-first, cloud backup) | Full user sovereignty; cloud is optional |

---

## 19. Glossary

### 19.1 Product & Business Terms

| Term | Definition |
|---|---|
| **ARIA** | AI orchestration agent coordinating 8 sub-agents. Acronym: AI Resource for Intelligent Assistance. |
| **Second Brain OS** | Full product name. A personal AI operating system for BTech CSE students. |
| **Sub-Agent** | Specialized AI module (briefing, memory, learning, opportunity, sleep, nudge, task, weekly review). 8 total. |
| **Zero-Miss** | System property where no task, deadline, or commitment silently expires — every item is done, rescheduled, or explicitly dropped. |
| **Opportunity Radar** | Daily 6 AM automated scan of 6 categories (internships, hackathons, fellowships, open-source, freelance, grants) matched to user skills. |
| **Resurface Engine** | Algorithm that identifies and re-presents saved content at contextually relevant moments based on active goals and current tasks. |
| **Context Engine** | Pipeline that assembles user data (profile, goals, tasks, courses, skills) into LLM-optimized system prompts. |
| **PromptLoader** | Python singleton that loads, parses, and validates all AI prompt files from `prompts/` directory with YAML frontmatter. |
| **Builder Action** | Unit of productive output: task completed, course progressed, project shipped, income earned, opportunity applied to. |
| **BAPU** | Builder Actions Per User per week — the north star metric. |
| **Dogfood Development** | Practice of using the product yourself daily to find bugs and validate features. |

### 19.2 Metrics & Analytics Terms

| Term | Definition |
|---|---|
| **DAU** | Daily Active Users — unique users who log in within a 24-hour period. |
| **MAU** | Monthly Active Users — unique users who log in within a 30-day period. |
| **DAU/MAU Ratio** | Engagement metric — percentage of monthly users who use the product daily. >40% indicates strong daily habit. |
| **Retention** | Percentage of users who return after a given period (Day 1, Day 7, Day 30, Day 90). |
| **Churn** | Percentage of users who stop using the product within a given period. |
| **NPS** | Net Promoter Score — user satisfaction metric (-100 to +100) based on single question: "How likely are you to recommend this product?" |
| **TAM** | Total Addressable Market — total revenue opportunity available if 100% market share was achieved. |
| **SAM** | Serviceable Addressable Market — segment of TAM within product's reach given constraints. |
| **SOM** | Serviceable Obtainable Market — realistic adoption given resources, budget, and timeline. |
| **LTV** | Lifetime Value — total value a user generates over their relationship with the product. |
| **PMF** | Product-Market Fit — state where a product satisfies strong market demand evidenced by retention, engagement, and organic growth. |

### 19.3 Technical Terms

| Term | Definition |
|---|---|
| **RLS** | Row-Level Security — PostgreSQL policy ensuring users can only access their own data. Applied to all 18 tables. |
| **JWT** | JSON Web Token — authentication token format used by Supabase Auth for session management. |
| **PWA** | Progressive Web Application — installable web app with offline support via service workers and IndexedDB. |
| **IndexedDB** | Browser-based NoSQL database for offline data storage, synced with Supabase when online. |
| **Ollama** | Local LLM server — runs Mistral 7B and other open-source models on consumer hardware (8GB+ RAM). |
| **WXT** | Cross-browser extension framework that builds for Chrome + Firefox + Edge from a single codebase. |
| **APScheduler** | Python task scheduler for cron jobs (daily briefing, opportunity radar, weekly review, reminders, habits, sleep). |
| **P95/P99** | 95th/99th percentile response time — 95% of requests are faster than this threshold. |
| **pgvector** | PostgreSQL extension for vector similarity search, used for semantic search on resources and ideas. |
| **LoRA** | Low-Rank Adaptation — efficient fine-tuning technique for LLMs, planned for Year 2 to customize Mistral for student use cases. |

### 19.4 Vision-Specific Terms

| Term | Definition |
|---|---|
| **Builder Generation** | Demographic trend of Gen Z (born 1997-2012) who prioritize building real things over traditional employment. 62% of Indian Gen Z want to start a business. |
| **Compound Growth (Student)** | The principle that every action (course, task, project) should feed every other action, creating positive cascading effects rather than isolated activities. |
| **Skill-to-Income Pipeline** | Direct mapping between skills tracked in the system and income earned, enabling effective hourly rate calculation by skill category. |
| **The Fragmentation Problem** | The state of student data being scattered across 10+ disconnected tools and platforms, preventing any system from providing holistic intelligence. |
| **ActiPassive** | Portmanteau of Active + Passive. Describes systems that look active but are actually passive (user must take initiative). Second Brain OS is designed to be truly active. |

---

## 20. References & Related Documents

### 20.1 Internal Documents

| Document | Location | Relevance |
|---|---|---|
| Business Requirements Document | `docs/product/03_BRD.md` | Detailed business requirements, functional specs, KPIs |
| Product Requirements Document (PRD) | `docs/product/04_SRS.md` | Functional specifications by module |
| Architecture Document | `docs/engineering/12_Architecture.md` | System design, component interaction, data flow |
| AI Agent Architecture | `docs/ai/20_Agent.md` | Comprehensive AI agent design, 8 sub-agents, prompt system |
| Design System | `docs/design/10_DesignSystem.md` | UI/UX design tokens, component library, cyberpunk theme |
| Design Tokens | `docs/design/35_DesignTokens.md` | Design tokens reference for implementation |
| Competitive Analysis | `docs/product/CompetitiveAnalysis.md` | Detailed market positioning, competitor comparison |
| AGENTS.md | `AGENTS.md` | Master AI agent reference for project context |
| User Stories | `docs/product/06_UserStories.md` | User stories for all 15 modules |
| Acceptance Criteria | `docs/product/07_AcceptanceCriteria.md` | Acceptance criteria for all features |
| ADR-001 | `docs/engineering/adr/ADR-001.md` | Architecture Decision Record — Monorepo structure |
| ADR-002 | `docs/engineering/adr/ADR-002.md` | Single-user architecture decision |
| ADR-004 | `docs/engineering/adr/ADR-004.md` | In-process agent architecture decision |
| ADR-005 | `docs/engineering/adr/ADR-005.md` | Cyberpunk design system decision |
| ADR-006 | `docs/engineering/adr/ADR-006.md` | PromptLoader architecture decision |

### 20.2 External References

| Reference | Purpose |
|---|---|
| AICTE Annual Report 2025 | Market sizing data (engineering enrollment statistics) |
| NASSCOM Tech Startup Report 2025 | India startup ecosystem data |
| Deloitte Gen Z & Millennial Survey 2024 | Builder generation trend data |
| Supabase Documentation | Database, Auth, RLS, Realtime API reference |
| Ollama Documentation | Local AI server setup and model management |
| Vercel Documentation | Frontend deployment and serverless functions |
| Railway Documentation | Backend deployment and environment management |
| Mistral 7B Technical Report | Model architecture and capability benchmarks |

### 20.3 Document Dependencies

| This Document Depends On | Depends On This Document |
|---|---|
| Market sizing from Competitive Analysis | BRD (functional requirements sourced from vision) |
| User personas from User Stories | Architecture (system design implements vision) |
| Tech stack from Architecture | Agent Architecture (AI design implements vision) |
| Cost projections from DevOps | Design System (UI implements vision) |

---

*End of Document — Version 4.0.0*
