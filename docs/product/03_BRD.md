# Business Requirements Document (BRD) â€” Second Brain OS (ARIA OS)

---

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-BRD-001 |
| Version | 3.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal â€” Business Requirements |
| Owner | Product Lead |
| Next Review | 2026-09-11 |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-01 | Developer | Initial BRD with executive summary, market analysis, stakeholder map |
| 2.0.0 | 2026-06-11 | Developer | Added ROI analysis, GTM strategy, success metrics |
| 3.0.0 | 2026-06-11 | Developer | Enterprise upgrade: SMART goals, TAM/SAM/SOM, module-level functional requirements (P0/P1/P2), NFRs with SLAs, KPIs per module, risk assessment matrix, budget estimates, regulatory compliance, glossary |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Objectives (SMART Goals)](#2-business-objectives-smart-goals)
3. [Problem Statement](#3-problem-statement)
4. [Target Market (TAM / SAM / SOM)](#4-target-market-tam--sam--som)
5. [User Segmentation](#5-user-segmentation)
6. [Stakeholder Map](#6-stakeholder-map)
7. [Functional Requirements (by Module)](#7-functional-requirements-by-module)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Assumptions and Constraints](#9-assumptions-and-constraints)
10. [Dependencies](#10-dependencies)
11. [Success Criteria (KPIs per Module)](#11-success-criteria-kpis-per-module)
12. [Risk Assessment](#12-risk-assessment)
13. [Regulatory and Compliance Requirements](#13-regulatory-and-compliance-requirements)
14. [Budget and Resource Estimates](#14-budget-and-resource-estimates)
15. [Timeline](#15-timeline)
16. [Glossary](#16-glossary)
17. [Appendices](#17-appendices)

---

### Business Requirements Domain Model

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
graph TD
  subgraph Users["ðŸ‘¥ Users"]
    U1[BTech CSE Students]
    U2[Self-Taught Programmers]
    U3[Working Professionals]
  end

  subgraph Value["ðŸ’Ž Value Proposition"]
    V1[Unified Surface<br/>15 Modules, 1 App]
    V2[Active Push AI<br/>Zero-Config Intelligence]
    V3[Zero Cost<br/>Rs. 0/month Forever]
    V4[Privacy First<br/>Local AI, No Tracking]
  end

  subgraph Modules["ðŸ“¦ 15 Functional Modules"]
    M1[Tasks - Courses - Goals]
    M2[Habits - Sleep - Time]
    M3[Income - Projects - Ideas]
    M4[Resources - Opportunities]
    M5[Chat - Automation]
    M6[YouTube - Academics]
  end

  subgraph AI["ðŸ¤– AI Layer"]
    A1[ARIA Orchestrator]
    A2[11 Agents]
    A3[Ollama Local â†’ Claude Cloud]
    A4[Algorithmic Fallbacks]
  end

  subgraph Business["ðŸ“Š Business Outcomes"]
    B1[DAU > 100<br/>6 Months]
    B2[Retention > 60%<br/>30-Day]
    B3[Task Completion > 78%<br/>Post-AI]
    B4[Infra Cost < Rs. 100/mo<br/>Always]
  end

  Users --> Value
  Value --> Modules
  Modules --> AI
  AI --> Business
  Business -.->|Validate| Users

  style Users fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Value fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style Modules fill:#13151A,stroke:#818CF8,color:#F1F5F9
  style AI fill:#13151A,stroke:#F59E0B,color:#F1F5F9
  style Business fill:#13151A,stroke:#6366F1,color:#F1F5F9
```

### Value Chain

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
flowchart LR
  subgraph Input["ðŸ“¥ Input"]
    I1[Student Pain Points<br/>Fragmention, Overwhelm]
    I2[Market Gap<br/>No Student-First AI Tool]
  end

  subgraph Process["âš™ï¸ Process"]
    P1[Build 15 Modules<br/>Monorepo Architecture]
    P2[Train AI Agents<br/>8 Specialized Sub-Agents]
    P3[Zero-Cost Infra<br/>Vercel + Supabase + Ollama]
    P4[Community GTM<br/>College Ambassadors]
  end

  subgraph Output["ðŸ“¤ Output"]
    O1[ARIA OS Platform<br/>Working Product]
    O2[Documentation<br/>120+ Docs, 16 MB]
    O3[Open Source<br/>MIT Licensed]
  end

  subgraph Outcome["ðŸ’¥ Outcome"]
    OC1[DAU 100+<br/>Retention > 60%]
    OC2[PMF Validated<br/>Community Grown]
    OC3[Rs. 0 Infrastructure<br/>Sustainable Forever]
  end

  subgraph Impact["ðŸŒ Impact"]
    IM1[25K+ Students<br/>Year 5]
    IM2[Productivity x3<br/>Measured]
    IM3[New Category<br/>Personal AI OS]
  end

  Input --> Process --> Output --> Outcome --> Impact

  style Input fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Process fill:#13151A,stroke:#818CF8,color:#F1F5F9
  style Output fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Outcome fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style Impact fill:#13151A,stroke:#F59E0B,color:#F1F5F9
```

---

## 1. Executive Summary

**Second Brain OS (ARIA OS)** is a personal AI productivity system purpose-built for BTech CSE students in India. It addresses the critical gap between student potential and student execution by providing an integrated, AI-powered system that manages courses, tasks, ideas, opportunities, projects, income, habits, sleep, and time across 15 unified modules.

The product operates at **Rs. 0/month** using free-tier infrastructure (Vercel, Supabase, Ollama, Brave Search), making it accessible to every student regardless of financial background. The ARIA AI agent â€” a collection of 11 agents â€” provides proactive intelligence through daily briefings, opportunity scanning, learning pattern detection, and behavioral nudges. Every feature has a deterministic, algorithm-driven fallback to ensure the system works even without AI.

**Key business metrics:**
- **Target market**: ~600,000 serviceable users (BTech CSE students + self-taught programmers)
- **Entry strategy**: Single-user, privacy-first, Rs. 0 forever â€” no subscription, no ads, no data selling
- **Monetization**: Indirect (portfolio value) â†’ Donations (Year 1) â†’ Premium AI credits (Year 2) â†’ Enterprise licensing (Year 3+)
- **Development investment**: ~455 hours over 12 months, solo developer (part-time), Rs. 0 infrastructure cost
- **Success threshold**: 100 daily active users with >60% 30-day retention proves product-market fit

---

## 2. Business Objectives (SMART Goals)

### 2.1 Primary Business Objectives

| ID | Objective | Metric | Baseline | Target | Timeline | Owner |
|---|---|---|---|---|---|---|
| O-01 | **Establish PMF with BTech CSE students** | Daily Active Users (DAU) | 0 | 100 | 6 months post-alpha | Product Lead |
| O-02 | **Demonstrate measurable productivity improvement** | Avg task completion rate per user | <5/week (typical student baseline) | >15/week | 3 months after PMF | Product Lead |
| O-03 | **Prove Rs. 0 business model is viable** | Monthly infrastructure cost | Rs. 0 | <Rs. 100/month | Ongoing | Product Lead |
| O-04 | **Achieve high user retention** | 30-day retention rate | 0% | >60% | 6 months post-alpha | Product Lead |
| O-05 | **Build complete 15-module system** | Modules live in production | 0 | 15 | 12 months | Product Lead |
| O-06 | **Maintain high system reliability** | Uptime (excl. planned maintenance) | N/A | >99.9% | Ongoing | Product Lead |

### 2.2 Secondary Business Objectives

| ID | Objective | Metric | Target | Timeline |
|---|---|---|---|---|
| O-07 | **Create reusable blueprint for student AI productivity** | GitHub stars / forks | >100 stars | 6 months post-GA |
| O-08 | **Generate case studies** | Published user success stories | >3 case studies | 12 months post-GA |
| O-09 | **Establish ARIA as trusted AI brand** | NPS score | >40 | 12 months post-alpha |
| O-10 | **Achieve organic growth** | Referral rate | >0.3 (30% of users refer) | 12 months post-alpha |
| O-11 | **Build community contributors** | Active GitHub contributors | >5 non-owner contributors | 12 months post-GA |

### 2.3 SMART Verification

| Objective | Specific | Measurable | Achievable | Relevant | Time-bound |
|---|---|---|---|---|---|
| O-01 | BTech CSE students using the system | DAU = count of unique logins | 100 users = 0.02% of SAM | Core target audience | 6 months |
| O-03 | Infrastructure cost on free tier | Monthly Railway/Vercel/Supabase bill | Rs. <100/month on free tiers | Rs. 0 business model | Ongoing |
| O-04 | Users returning after 30 days | supabase auth analytics | >60% retention (industry avg for tools) | Indicates daily value | 6 months |
| O-05 | All 15 modules built and deployed | Module checklist in Roadmap.md | 455 hours over 12 months | Product definition | 12 months |

---

## 3. Problem Statement

### 3.1 The Core Business Problem

BTech CSE students in India face a **systematic failure of information and opportunity management** that prevents them from translating potential into execution. This problem manifests across eight interconnected domains:

| Domain | Problem | Quantitative Impact |
|---|---|---|
| **Course Management** | Students enroll in 4-7 online courses per semester but complete <30% | Rs. 3,000-15,000/year in wasted course fees |
| **Task Management** | No unified priority system â€” tasks accumulate in inboxes, forgotten | 65% of tasks remain incomplete |
| **Idea Capture** | Creative insights (startup ideas, project concepts) captured but lost within 24 hours | ~80% of ideas never executed |
| **Opportunity Discovery** | Internships, hackathons, fellowships discovered after deadlines or not at all | 5-15 missed opportunities/year |
| **Skill Application** | Skills studied in courses never applied to real projects, forgotten within 6 months | Years of learning time wasted |
| **Time Awareness** | No consistent time tracking â€” students cannot optimize what they do not measure | 10-15 hrs/week unaccounted |
| **Income Optimization** | Freelance/part-time income untracked â€” students do not know effective hourly rate | Systematic underpricing |
| **Health & Habits** | Sleep and health deprioritized during academic pressure | Burnout cycles, health deterioration |

### 3.2 Why Existing Solutions Fail

| Solution | Gap | Why It Doesn't Work for Students |
|---|---|---|
| **Notion** | Generic â€” no student-specific features | Requires custom setup, expensive templates, no AI agent |
| **Todoist** | Passive â€” no push intelligence | No course tracking, no opportunity radar, no AI |
| **Motion** | Expensive â€” $19/month ($1,600/year) | Priced out of student budgets |
| **ChatGPT/Claude** | No persistent memory, no proactive push | Requires manual prompting every time |
| **Obsidian** | High learning curve, no actions | Graph is passive, no execution engine |
| **College ERP** | Poor UX, no cross-system integration | Data locked in institutional silos |

### 3.3 Cost of Inaction

If the problem is not solved, each student loses:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                 ANNUAL COST OF INACTION                         â”‚
â”‚                    (Per Student)                                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚  Waste Category                      Financial    Opportunity   â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€    â”‚
â”‚  Wasted course fees                  Rs. 5,000    â€”             â”‚
â”‚  Missed internship income                         Rs. 50,000+  â”‚
â”‚  Missed freelance income                          Rs. 30,000+  â”‚
â”‚  Lost project opportunities                       Rs. 20,000+  â”‚
â”‚  Skill decay (re-learning cost)      Rs. 2,000    â€”             â”‚
â”‚  Time lost to disorganization                    Rs. 15,000+   â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€    â”‚
â”‚  TOTAL                               Rs. 7,000    Rs. 115,000+ â”‚
â”‚                                                                 â”‚
â”‚  Combined estimated loss per student: ~Rs. 1.2 lakhs/year      â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

For the 500,000 BTech CSE students enrolled annually, the aggregate loss exceeds **Rs. 600 crore/year**.

---

## 4. Target Market (TAM / SAM / SOM)

### 4.1 Total Addressable Market (TAM)

The total addressable market includes all students and early-career professionals in India who could benefit from an AI-powered productivity system.

| Segment | Population | Source | Growth Rate |
|---|---|---|---|
| BTech CSE students (currently enrolled) | 500,000 | AICTE annual report | 5% YoY |
| Total engineering students (all branches) | 1,500,000 | AICTE annual report | 3% YoY |
| Self-taught programmers (active learners) | 200,000 | Estimated from edX/Coursera India data | 15% YoY |
| Recent CS graduates (0-2 years experience) | 500,000 | Estimated from graduation data | 8% YoY |
| Indian Gen Z interested in tech careers | 5,000,000 | Estimated from NSSO survey | 10% YoY |
| **Total Addressable Market** | **~7,200,000** | | |

### 4.2 Serviceable Addressable Market (SAM)

The SAM filters TAM by criteria that directly affect adoption probability:

| Filter | Rationale | Reduction Factor | Remaining |
|---|---|---|---|
| TAM | â€” | â€” | 7,200,000 |
| Currently enrolled or recently graduated (0-2 yrs) | Product is optimized for college-to-early-career transition | 70% | 5,040,000 |
| Actively seeking productivity improvement | Self-selection â€” students who already use tools or feel the pain | 40% | 2,016,000 |
| Comfortable with self-hosted / open-source tools | Technical requirement â€” deployment via CLI, GitHub | 50% | 1,008,000 |
| Willing to try a new non-brand tool | Early adopter mindset â€” not locked into existing tools | 60% | 604,800 |
| **Serviceable Addressable Market** | | | **~600,000** |

### 4.3 Serviceable Obtainable Market (SOM)

The SOM represents realistic adoption targets given the solo-developer, no-marketing, organic-growth strategy:

| Year | Penetration Rate | Annual New Users | Cumulative Users | Cumulative % of SAM |
|---|---|---|---|---|
| Year 1 (2026-2027) | 0.02% | 100 | 100 | 0.02% |
| Year 2 (2027-2028) | 0.17% | 900 | 1,000 | 0.17% |
| Year 3 (2028-2029) | 1.50% | 8,000 | 9,000 | 1.50% |
| Year 4 (2029-2030) | 2.67% | 7,000 | 16,000 | 2.67% |
| Year 5 (2030-2031) | 5.00% | 14,000 | 30,000 | 5.00% |

**SOM expansion drivers:**
- **Year 1**: Dogfooding + 2-3 close friends (organic, zero marketing)
- **Year 2**: GitHub release â†’ Hacker News / Reddit viral potential
- **Year 3**: Community growth + Word of mouth + Product Hunt
- **Year 4**: Institutional partnerships + International expansion
- **Year 5**: Plugin ecosystem + Mobile app + Brand recognition

### 4.4 Market Sizing â€” Revenue-Adjusted

| Year | Users | Revenue Model | Est. Annual Revenue |
|---|---|---|---|
| 1 | 100 | Rs. 0 (indirect only) | Rs. 0 |
| 2 | 1,000 | Donations + Sponsorships | Rs. 6,000-24,000 |
| 3 | 9,000 | Donations + Premium AI (2% conversion at Rs. 99/mo) | Rs. 2-5 lakhs |
| 4 | 16,000 | Premium + Marketplace (5% conversion) | Rs. 10-20 lakhs |
| 5 | 30,000 | Full suite + Enterprise (3 colleges at Rs. 5 lakhs/year) | Rs. 30-60 lakhs |

---

## 5. User Segmentation

### 5.1 Primary Personas

#### Persona A: "The Overloaded Optimist" (Arjun)

| Attribute | Description |
|---|---|
| **Demographics** | Male, 19, 2nd Year CSE, Tier-2 city |
| **Behavior** | Enrolls in 4-7 courses simultaneously. 200+ browser tabs. Buys courses on sale. |
| **Tech Setup** | Windows laptop (8GB RAM), mid-range Android, unreliable hostel Wi-Fi |
| **Monthly Spend** | Rs. 2,000 from parents â€” zero budget for software |
| **Pain Points** | Course abandonment, idea loss, task overwhelm, missed deadlines |
| **Emotional State** | Guilt cycles â€” excited about new courses, guilty about unfinished ones |
| **Adoption Trigger** | Misses an internship deadline â†’ "I need a system that won't let me miss things" |
| **Monthly Value** | Would pay Rs. 0 (cannot pay). Value delivered: Rs. 5,000-10,000/month in saved fees + found opportunities |

#### Persona B: "The Solo Builder" (Priya)

| Attribute | Description |
|---|---|
| **Demographics** | Female, 20, 3rd Year CSE, Tier-1 city |
| **Behavior** | Building a SaaS product. Freelances on Upwork (Rs. 5,000-15,000/month). Ships 1-2 projects/year. |
| **Tech Setup** | MacBook Air, good Android phone, stable internet |
| **Monthly Spend** | Rs. 5,000-15,000 from freelancing â€” willing to spend on tools that increase earning |
| **Pain Points** | Time fragmentation across income streams, underpricing, no project structure |
| **Emotional State** | Driven but tired â€” knows she could earn more if optimized |
| **Adoption Trigger** | Discovers effective hourly rate is Rs. 75 â†’ "I need to know this before every project" |
| **Monthly Value** | Would pay Rs. 99/month if premium features needed. Value delivered: Rs. 5,000-10,000/month in rate optimization |

#### Persona C: "The Idea Generator" (Rohan)

| Attribute | Description |
|---|---|
| **Demographics** | Male, 18, 1st Year CSE, Tier-2 city |
| **Behavior** | 50+ startup ideas in various notes. Zero shipped. Buys domain names on impulse. |
| **Tech Setup** | Old Windows laptop, budget Android phone |
| **Monthly Spend** | Rs. 1,000 from parents â€” prioritizes food and data over software |
| **Pain Points** | Idea overwhelm, no validation process, cannot decide what to build |
| **Emotional State** | Excitement â†’ overwhelm â†’ abandonment â†’ repeat |
| **Adoption Trigger** | Forgets a brilliant idea â†’ "I need to capture and evaluate systematically" |
| **Monthly Value** | Would pay Rs. 0. Value delivered: Structured pipeline from idea to execution |

### 5.2 Secondary Personas

#### Persona D: "The Self-Taught Switcher"

| Attribute | Description |
|---|---|
| **Profile** | 22, non-CS degree, learning to code via bootcamps/YouTube |
| **Pain Points** | No academic structure, no peer group, no opportunity network |
| **Needs** | Skill tracking, project roadmap, portfolio builder, opportunity radar |
| **Adaptation** | Course module needs bootcamp/non-degree tracks |

#### Persona E: "The Fresh Graduate"

| Attribute | Description |
|---|---|
| **Profile** | 22-24, employed 0-2 years as junior developer |
| **Pain Points** | Transition from academic to professional structure, still building foundation |
| **Needs** | Shift from CGPA to career growth tracking, work-related modules |
| **Adaptation** | Modify academic modules, add meeting tracking, OKR alignment |

### 5.3 Anti-Personas (Explicitly Out of Scope)

| Persona | Reason for Exclusion |
|---|---|
| **Enterprise team lead** | Product is single-user. No team features. No org-wide deployment. |
| **Non-technical user** | Requires CLI, GitHub, self-hosting. Below minimum technical literacy threshold. |
| **K-12 student** | Academic system (semesters, CGPA) does not apply. Content too advanced. |
| **Senior professional (>5 years exp)** | Needs are around management, leadership, networking â€” not covered. |
| **Social user** | No friends, no leaderboards, no sharing. Product is intentionally private. |

### 5.4 User Segment Prioritization

| Priority | Segment | Rationale |
|---|---|---|
| **P0** | Persona A â€” Overloaded Optimist | Largest segment. Highest pain. Zero willingness to pay â†’ perfect for Rs. 0 model. |
| **P1** | Persona B â€” Solo Builder | Higher engagement potential. May convert to premium. Drives income modules. |
| **P1** | Persona C â€” Idea Generator | Needs structure most. Drives idea pipeline and roadmap modules. |
| **P2** | Persona D â€” Self-Taught Switcher | Growing segment. Requires minor adaptations. |
| **P3** | Persona E â€” Fresh Graduate | Valuable but currently out of focus. Revisit in Year 2. |

---

## 6. Stakeholder Map

### 6.1 Stakeholder Register

| ID | Stakeholder | Role | Interest | Influence | Engagement Strategy |
|---|---|---|---|---|---|
| S-01 | **Student User** | Primary user, daily operator | Complete more tasks, find opportunities, track progress, earn income | High | User-centric design, feedback loops, community |
| S-02 | **Developer** | Product builder, maintainer | Working system, clean codebase, deployment success, personal career growth | High (decision-maker) | Dogfood development, sustainable pace |
| S-03 | **Early Testers** | Usability validators (2-5 friends) | Working tool, bug-free experience | Medium | Structured feedback forms, weekly check-ins |
| S-04 | **College Faculty** | Indirect beneficiary | More organized students, better academic outcomes | Low | Case study sharing, potential endorsements |
| S-05 | **Startup Employers** | Indirect beneficiary | Candidates with real project experience, portfolios | Low | Care... see operational processes from the portfolio output |
| S-06 | **Open Source Community** | Future contributors | Code quality, documentation, extensibility | Medium (post-GA) | Clear CONTRIBUTING.md, good-first-issues |
| S-07 | **GitHub Sponsors / Donors** | Financial supporters | Product viability, transparency | Low | Sponsorship tiers, transparency reports |
| S-08 | **Future Investors** | Capital providers (Year 3+) | User growth, engagement, scalable model | Low (future) | Maintain metrics dashboard, growth data |

### 6.2 Power-Interest Grid

```
INTEREST
    â”‚
High    â”‚ Early Testers (S-03)           Student Users (S-01)
        â”‚                                 Developer (S-02)
        â”‚
        â”‚ College Faculty (S-04)          
        â”‚ Startup Employers (S-05)        
        â”‚
Medium  â”‚                                 Open Source Community (S-06)
        â”‚
        â”‚ GitHub Sponsors (S-07)          Future Investors (S-08)
        â”‚
Low     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º POWER
            Low              Medium          High
```

**Primary focus quadrant (High Power, High Interest):** Student Users + Developer â€” these drive all product decisions.

### 6.3 Stakeholder Success Criteria

| Stakeholder | Success Criteria | Measurement |
|---|---|---|
| **Student User** | Completes >15 tasks/week. Finds >2 opportunities/week. Ships >1 project/quarter. | System analytics + quarterly survey |
| **Developer** | All 15 modules live. <5 bugs/month. CI passing >95%. | GitHub issues + CI dashboard |
| **Early Testers** | 30-day retention >60%. NPS >30. | Auth analytics + feedback form |
| **Open Source Community** | >5 external PRs merged. >100 GitHub stars. | GitHub insights |
| **Future Investors** | >1,000 DAU. >70% retention. Rs. 0 infrastructure. | Growth metrics deck |

---

## 7. Functional Requirements (by Module)

### 7.1 Requirements Classification

Each requirement is classified by priority:

| Priority | Definition | Timeline |
|---|---|---|
| **P0** | Critical path â€” system does not function without it | Alpha (Month 3) |
| **P1** | Important â€” core value proposition depends on it | Beta (Month 6) |
| **P2** | Valuable â€” enhances experience, deferred if necessary | GA (Month 12) |
| **P3** | Future â€” desirable but not committed | Post-GA |

### 7.2 Module: Dashboard

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-DB-01 | Display today's top 3 priorities from briefing | P0 | Priorities shown on first load; refreshed daily |
| FR-DB-02 | Show pending tasks count with overdue indicator | P0 | Count updates in real-time; overdue tasks highlighted in red |
| FR-DB-03 | Display upcoming course deadlines (next 7 days) | P0 | Courses with deadlines within 7 days shown |
| FR-DB-04 | Show weekly task completion trend (7-day sparkline) | P1 | Chart renders with last 7 days of completion data |
| FR-DB-05 | Display unread opportunity radar count | P1 | Badge shows count of opportunities not yet reviewed |
| FR-DB-06 | Show weekly income summary | P1 | Total income for current week displayed |
| FR-DB-07 | Display habit consistency rate for current week | P1 | Percentage shown with progress bar |
| FR-DB-08 | Show sleep score for last night (if logged) | P1 | Score displayed with color coding (green/yellow/red) |
| FR-DB-09 | Quick-add task from dashboard | P0 | Text input + submit creates task immediately |
| FR-DB-10 | Show next ARIA insight or nudge | P2 | AI-generated insight card rotates daily |
| FR-DB-11 | Mobile-responsive layout with all widgets | P0 | All dashboard widgets render correctly on 360px width |
| FR-DB-12 | Dashboard loads in <1 second (first meaningful paint) | P0 | Measured by Lighthouse; server-side render critical data |

### 7.3 Module: Tasks

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-TK-01 | Create task with title, description, priority (low/medium/high/urgent) | P0 | All fields saved; validation on empty title |
| FR-TK-02 | Set due date with optional time | P0 | Date picker; overdue tasks highlighted after date passes |
| FR-TK-03 | Assign category/tag (max 3 per task) | P0 | Categories from predefined list + custom |
| FR-TK-04 | Mark task complete with optional completion note | P0 | Task moves to completed; timestamp recorded |
| FR-TK-05 | Edit task (all fields) with update history | P0 | Edit modal; version history tracked |
| FR-TK-06 | Delete task with confirmation | P0 | Soft delete (archived for 30 days) |
| FR-TK-07 | View tasks by status (pending/completed/archived) | P0 | Filter tabs; counts for each status |
| FR-TK-08 | View tasks by priority (sorted highâ†’low) | P0 | Priority sort; urgent tasks visually distinct |
| FR-TK-09 | View tasks by due date (nearest first) | P0 | Default view; past-due tasks at top |
| FR-TK-10 | Auto-reschedule overdue tasks based on priority | P1 | Algorithm moves tasks to today/tomorrow; reschedule logged |
| FR-TK-11 | Link task to goal (goal_id foreign key) | P1 | Task shows in goal roadmap; goal progress updates |
| FR-TK-12 | Link task to course (course_id foreign key) | P1 | Task appears in course timeline |
| FR-TK-13 | Task search by title and description | P1 | Full-text search; results in <500ms |
| FR-TK-14 | Bulk actions (complete, delete, reschedule) | P2 | Checkbox selection + action bar |
| FR-TK-15 | Recurring tasks (daily, weekly, custom) | P2 | Recurrence rule; auto-creation on completion |
| FR-TK-16 | Task dependencies (task B cannot start until task A is complete) | P2 | Dependency graph; visual indicator |
| FR-TK-17 | Estimated time vs actual time tracking | P2 | Pomodoro timer integration; variance report |
| FR-TK-18 | Task completion streak (consecutive days with â‰¥1 task done) | P2 | Streak counter; reset on miss day |

### 7.4 Module: Courses

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-CR-01 | Add course with title, platform, URL | P0 | Required fields validated |
| FR-CR-02 | Set target completion date with progress % | P0 | Progress slider 0-100%; date picker |
| FR-CR-03 | Add weekly schedule (e.g., Mon/Wed/Fri 2 hours) | P0 | Schedule stored; task auto-created from schedule |
| FR-CR-04 | Mark course as complete with date | P0 | Completion timestamp; skill profile updated |
| FR-CR-05 | Edit course details with update history | P0 | All fields editable |
| FR-CR-06 | Delete course with confirmation | P0 | Soft delete |
| FR-CR-07 | View course list with progress bars | P0 | Visual progress; color coding (red <30%, yellow 30-70%, green >70%) |
| FR-CR-08 | Filter by status (active/completed/on-hold) | P0 | Tab-based filtering |
| FR-CR-09 | Course deadline alerts (>14 days, >7 days, >3 days, overdue) | P1 | Notification levels with escalation |
| FR-CR-10 | Link course to skills (skill_id foreign key) | P1 | Each course tagged with 1-5 skills |
| FR-CR-11 | Course notes section per course | P1 | Rich text; auto-save |
| FR-CR-12 | Course completion certificate upload | P2 | File upload; stored in Supabase storage |
| FR-CR-13 | Course comparison (time spent vs completion speed) | P2 | Analytics: hours per module, completion rate by platform |
| FR-CR-14 | AI course recommendation based on skill gaps | P2 | Learning agent detects gaps; suggests courses |

### 7.5 Module: Goals

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-GL-01 | Create goal with title, description, target date | P0 | Required fields; date validation |
| FR-GL-02 | Add milestones with target dates (up to 10 per goal) | P0 | Milestone checklist; each has due date |
| FR-GL-03 | Mark milestone complete | P0 | Progress % recalculated automatically |
| FR-GL-04 | Visual roadmap view (React Flow) | P1 | Drag-and-drop; milestones as nodes |
| FR-GL-05 | Link tasks to goal (task references goal_id) | P0 | Tasks shown in goal detail |
| FR-GL-06 | Link courses to goal | P1 | Courses shown in goal detail |
| FR-GL-07 | Goal progress % (auto-calculated from milestones + tasks) | P0 | Real-time update; visual progress bar |
| FR-GL-08 | AI goal breakdown (text â†’ milestone plan) | P1 | "I want to build X" â†’ structured roadmap |
| FR-GL-09 | Goal categories (career, skills, health, finance, project) | P1 | Category filter; predefined |
| FR-GL-10 | Quarterly goal review with AI insights | P2 | AI analyzes progress vs plan; suggests adjustments |
| FR-GL-11 | Goal archive for completed/deprioritized goals | P1 | Archived goals viewable but not active |
| FR-GL-12 | Goal comparison (planned vs actual timeline) | P2 | Timeline variance analysis |

### 7.6 Module: YouTube Vault

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-YT-01 | Save YouTube video with URL, title, channel | P0 | URL validation; auto-fetch metadata |
| FR-YT-02 | AI summary of video transcript (Claude API) | P1 | Summary generated and stored; fallback: no summary |
| FR-YT-03 | Watch scheduling with deadline | P0 | Schedule date; reminder before expiry |
| FR-YT-04 | 60-day expiry with notification and auto-archive | P1 | After 60 days, video archived; notification sent |
| FR-YT-05 | Search vault by title, channel, summary text | P1 | Full-text search across metadata |
| FR-YT-06 | Filter by watch status (to-watch/watching/watched/expired) | P0 | Filter tabs with counts |
| FR-YT-07 | Link video to goal or course | P1 | Reference goal_id or course_id |
| FR-YT-08 | Mark video as watched with rating (1-5) | P0 | Rating star input |
| FR-YT-09 | Save via browser extension (one-click) | P0 | Extension button â†’ auto-save with metadata |
| FR-YT-10 | AI topic tagging (auto-categorization) | P2 | Tags generated from transcript |
| FR-YT-11 | Watch queue optimization (AI suggests what to watch when) | P2 | Based on goals, course progress, time available |

### 7.7 Module: Resources

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-RS-01 | Save resource with URL, title, type (article/book/repo/tool) | P0 | Type validation; URL metadata fetch |
| FR-RS-02 | Add custom tags (up to 10 per resource) | P0 | Tag input with autocomplete |
| FR-RS-03 | Auto-tagging via AI (Ollama) | P1 | Tags generated; user can override |
| FR-RS-04 | Natural language search across resources | P1 | Semantic search (pgvector); falls back to full-text |
| FR-RS-05 | Link resource to goal or course | P1 | Reference goal_id or course_id |
| FR-RS-06 | Save from browser extension | P0 | One-click; auto-detect type |
| FR-RS-07 | Resurface engine â€” show relevant resources contextually | P2 | When working on linked goal, surface resources |
| FR-RS-08 | Resource archive with read/unread status | P0 | Status toggle |
| FR-RS-09 | Reading list with priority ordering | P1 | Drag-to-reorder; manual prioritization |
| FR-RS-10 | Resource notes (personal annotations) | P1 | Markdown editor per resource |
| FR-RS-11 | Bookmark import (Chrome bookmarks, Pocket) | P2 | CSV/JSON import |
| FR-RS-12 | Collaborative resource list (shared with specific users) | P3 | Future â€” deferred to collaboration phase |

### 7.8 Module: Ideas

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-ID-01 | Capture idea with title, description (min 10 chars) | P0 | Quick capture â†’ title + description form |
| FR-ID-02 | Status pipeline: raw â†’ validating â†’ building â†’ shipped â†’ archived | P0 | Status dropdown; pipeline visualization |
| FR-ID-03 | AI market check â€” "Has this been built? Market size?" | P1 | Ollama-based analysis; falls back to manual |
| FR-ID-04 | Link idea to goal or skill | P1 | Reference goal_id or skill_id |
| FR-ID-05 | Idea scoring (effort: 1-5, impact: 1-5, confidence: 1-5) | P1 | Score = effort * impact * confidence / 125 (normalized) |
| FR-ID-06 | Sort by score (highest first) | P1 | Default sort; manual override |
| FR-ID-07 | AI action suggestion â€” "What's the next step for this idea?" | P2 | Based on status; suggests concrete actions |
| FR-ID-08 | Quick capture from mobile/browser/voice | P0 | Multiple entry points; unified storage |
| FR-ID-09 | Idea age indicator (days since capture) | P1 | Visual badge; ideas >30 days in "raw" get nudge |
| FR-ID-10 | Google Keep / Apple Notes import | P3 | Future â€” deferred |

### 7.9 Module: Opportunities

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-OP-01 | Daily 6 AM scan of 6 categories (internships, hackathons, fellowships, open-source, freelance, grants) | P0 | Cron job executes; results stored |
| FR-OP-02 | Skill match score (0-100) for each opportunity | P0 | Algorithm: match user skills with required skills |
| FR-OP-03 | Deadline urgency indicator | P0 | Color-coded: green (>14 days), yellow (7-14), red (<7), critical (<48h) |
| FR-OP-04 | History personalization â€” hide already-seen opportunities | P0 | Deduplication; seen_at tracking |
| FR-OP-05 | Opportunities dashboard with filters | P0 | Filter by category, match score, deadline, status |
| FR-OP-06 | Apply tracking â€” mark as applied/interviewed/rejected/accepted | P0 | Status pipeline |
| FR-OP-07 | Critical deadline alerts (push + email for <48 hours) | P1 | Multi-channel notification |
| FR-OP-08 | Opportunity profile editor â€” fine-tune radar sources | P1 | Add/remove categories, keywords, minimum match score |
| FR-OP-09 | Application documents tracker (resume, portfolio, SOP links) | P1 | Save links per opportunity |
| FR-OP-10 | AI opportunity match analysis â€” "Why this matches you" | P2 | Generated by learning agent |
| FR-OP-11 | Application success rate analytics | P2 | Applied â†’ accepted rate; identify best-performing resume |
| FR-OP-12 | Warm lead pipeline â€” companies that previously accepted | P3 | Future |

### 7.10 Module: Income

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-IC-01 | Log income entry with amount, source, date | P0 | Required: amount > 0; source required |
| FR-IC-02 | Categorize by type (freelance, internship, part-time, gift, other) | P0 | Category dropdown |
| FR-IC-03 | Link income to skill (what skill earned this money?) | P1 | Skill_id reference |
| FR-IC-04 | Calculate effective hourly rate (amount / hours worked) | P1 | Auto-calculated when hours entered |
| FR-IC-05 | Monthly income summary with trend chart | P0 | Bar chart; month-over-month comparison |
| FR-IC-06 | Year-to-date total | P1 | Running total |
| FR-IC-07 | Income by skill â€” which skills earn most? | P1 | Pie chart or ranked list |
| FR-IC-08 | Weekly income review email | P2 | Automated weekly summary |
| FR-IC-09 | Income goal setting (monthly target) | P2 | Goal vs actual tracking |
| FR-IC-10 | Tax estimation (basic â€” applicable for freelance income) | P3 | Future |

### 7.11 Module: Projects

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-PR-01 | Create project with name, description, goals | P0 | Required: name; optional: description, goals |
| FR-PR-02 | Phase tracking (planning â†’ building â†’ testing â†’ launched â†’ maintaining) | P0 | Kanban-style phase view |
| FR-PR-03 | Next action rule â€” auto-suggest next step | P1 | Algorithm: based on current phase, last action, elapsed time |
| FR-PR-04 | Blocker logging â€” describe what's blocking | P1 | Blocker form; escalation if >3 days unresolved |
| FR-PR-05 | GitHub repo link integration | P1 | URL validation; commit count display |
| FR-PR-06 | Weekly commit check (alert if no commits in 7 days) | P1 | Automated check; notification on stagnation |
| FR-PR-07 | Skill profile auto-update (GitHub languages â†’ skills) | P2 | Parse languages from repos; suggest skill additions |
| FR-PR-08 | Project URL (deployed link, demo) | P0 | URL field |
| FR-PR-09 | LinkedIn post generator on milestone | P2 | AI draft based on milestone description |
| FR-PR-10 | Project portfolio view (public-facing, optional) | P3 | Future |
| FR-PR-11 | AI project health assessment | P2 | Analyzes: commits, blockers, phase progress â†’ health score |

### 7.12 Module: Academics

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-AC-01 | Add semester with subjects + credits | P0 | Semesters ordered; subjects have name, code, credits |
| FR-AC-02 | Input marks/grades per subject | P0 | Grade input (S/A/B/C/D/F or numeric) |
| FR-AC-03 | CGPA calculation with projections | P0 | Formula: sum(grade_points * credits) / sum(credits) |
| FR-AC-04 | CGPA projection â€” "If I get X grade in remaining subjects, CGPA = Y" | P1 | What-if analysis |
| FR-AC-05 | At-risk subject alerts (current performance < minimum required) | P1 | Threshold-based alerts |
| FR-AC-06 | Semester timeline view (exam dates, submission deadlines) | P1 | Calendar view |
| FR-AC-07 | Grade distribution across semesters (trend chart) | P2 | Bar chart: CGPA per semester |
| FR-AC-08 | Backlog tracking (subjects failed and needs retake) | P1 | Separate backlog list; retake planning |
| FR-AC-09 | Attendance tracking (percentage per subject) | P2 | Threshold alert if <75% |
| FR-AC-10 | Subject â†’ skill mapping (what skills does each subject teach?) | P2 | Manual mapping; links to skill profile |

### 7.13 Module: Habits

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-HB-01 | Create habit with name, frequency (daily/weekly/custom) | P0 | Frequency configuration; max 10 active habits |
| FR-HB-02 | Log habit completion for current day | P0 | One-tap completion; timestamp |
| FR-HB-03 | Streak tracking (consecutive days/weeks) | P0 | Auto-calculated; reset on miss |
| FR-HB-04 | Consistency rate (completed / expected over 30 days) | P1 | Percentage; displayed as progress bar |
| FR-HB-05 | Miss detection â€” alert if habit not logged by cutoff time | P1 | Notification if not completed by configurable time |
| FR-HB-06 | Link habit to goal (habit supports goal progress) | P1 | Goal_id reference |
| FR-HB-07 | Weekly habit summary (which habits maintained, which slipped) | P1 | Automated weekly report |
| FR-HB-08 | Recovery rate tracking (streak recovery after miss) | P2 | Alternative metric: "how many days to restart after break" |
| FR-HB-09 | Habit categories (health, coding, reading, reflection) | P1 | Category filter |
| FR-HB-10 | AI habit optimization suggestion based on patterns | P2 | "You're more consistent with morning habits" type insights |

### 7.14 Module: Sleep

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-SL-01 | Log bedtime and wake time with date | P0 | Time picker; date auto-set |
| FR-SL-02 | Sleep quality rating (1-5 stars) | P0 | Star input |
| FR-SL-03 | Calculate sleep duration, score (duration * quality) | P0 | Auto-calculated |
| FR-SL-04 | Sleep debt tracking (recommended 8h vs actual) | P1 | Running debt balance |
| FR-SL-05 | Weekly sleep average chart | P1 | Line chart: average duration per night |
| FR-SL-06 | Wind-down message at 9:30 PM (AI-generated) | P1 | Based on tomorrow's schedule, today's exertion |
| FR-SL-07 | Task adjustment based on sleep â€” if sleep <5h, lower today's expectations | P1 | Algorithm: reduce task count; remove non-essential |
| FR-SL-08 | Google Fit / Apple Health integration (optional) | P2 | Import sleep data from watch/phone |
| FR-SL-09 | Sleep insights â€” correlations with productivity | P2 | "When you sleep >7h, you complete 40% more tasks" |
| FR-SL-10 | Bedtime reminder (customizable schedule) | P0 | Push notification at configurable time |

### 7.15 Module: Time Tracking

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-TM-01 | Start timer for current task | P0 | Timer running indicator; task selector |
| FR-TM-02 | Stop timer with elapsed time display | P0 | Duration saved; logged to time_entries |
| FR-TM-03 | Manual time entry (if timer not used) | P0 | Duration input; task selector |
| FR-TM-04 | Pomodoro mode (25 min focus, 5 min break) | P1 | Timer with notification; session count tracking |
| FR-TM-05 | Deep work detection (>60 min continuous on same task) | P1 | Flag in time_entries; deep work analytics |
| FR-TM-06 | Focus hour analysis (which hours are most productive) | P1 | Heatmap: productivity by hour of day |
| FR-TM-07 | Time analytics dashboard (daily, weekly, monthly views) | P0 | Bar/line charts; category breakdown |
| FR-TM-08 | Category breakdown (how much time per project/domain) | P1 | Pie chart; time per category |
| FR-TM-09 | Time-based alerts (if overspending on one category) | P2 | Configurable threshold alerts |
| FR-TM-10 | Weekly time summary email | P2 | Automated weekly report |

### 7.16 Module: AI / ARIA Chat

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-AI-01 | Chat panel UI with message history | P0 | Scrollable messages; user + AI bubbles |
| FR-AI-02 | Ollama integration (Mistral 7B) as primary LLM | P0 | API call to local Ollama; timeout 30s |
| FR-AI-03 | Claude API fallback when Ollama unavailable | P1 | Automatic fallback; token budget management |
| FR-AI-04 | Persistent memory (aria_memory table) â€” remembers user facts | P0 | Key-value storage; retrieval on context assembly |
| FR-AI-05 | Chat-triggered actions â€” "Add task: ..." creates task | P1 | Natural language intent parsing; action execution |
| FR-AI-06 | Chat-triggered goal updates, resource saves | P1 | Similar to FR-AI-05; multi-intent support |
| FR-AI-07 | Context builder â€” assemble user state into prompt | P0 | Serialize profile, goals, tasks, courses |
| FR-AI-08 | Streaming responses (typing indicator) | P1 | Server-sent events; progressive rendering |
| FR-AI-09 | Message history persistence (chat_messages table) | P0 | All messages saved; viewable in chat |
| FR-AI-10 | Context-aware responses (references user's active goals) | P1 | Context builder includes active goals in system prompt |

### 7.17 Module: Automation / Cron Jobs

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-AU-01 | Daily briefing generation (7 AM) | P0 | Cron: triggers briefing_agent; stores in daily_briefings |
| FR-AU-02 | Opportunity radar scan (6 AM) | P0 | Cron: triggers opportunity_agent; stores results |
| FR-AU-03 | Weekly review generation (Sunday 8 PM) | P0 | Cron: triggers weekly_review_agent; stores in weekly_reviews |
| FR-AU-04 | Task auto-reschedule (every 15 min) | P0 | Cron: algorithm checks overdue tasks; reschedules |
| FR-AU-05 | Habit miss detection (configurable time, default 9 PM) | P1 | Cron: checks habit_logs; sends reminder |
| FR-AU-06 | Sleep wind-down (9:30 PM) | P1 | Cron: triggers sleep_agent; sends notification |
| FR-AU-07 | Course progress nudge (6 PM) | P1 | Cron: checks course progress; sends nudge if stagnant |
| FR-AU-08 | Learning progress snapshot (daily midnight) | P1 | Cron: captures current state to learning_progress |
| FR-AU-09 | Email digest â€” weekly summary (Sunday 6 PM) | P2 | Cron: compiles weekly metrics; sends via Resend |
| FR-AU-10 | Missed task escalation (push â†’ email â†’ SMS) | P2 | Cron: escalation ladder; SMS via Twilio |

### 7.18 Module: Settings & Profile

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-ST-01 | User profile with name, email, skills list | P0 | Edit all fields; skills autocomplete |
| FR-ST-02 | Notification preferences (push/email/SMS per event type) | P1 | Granular toggle per notification type |
| FR-ST-03 | Theme toggle (dark/light â€” dark is default) | P0 | Persisted in user_preferences |
| FR-ST-04 | Data export (JSON + CSV) | P1 | Export all tables; download link |
| FR-ST-05 | Account deletion with data purge | P0 | Confirmation flow; soft delete with 30-day recovery |
| FR-ST-06 | API key management (for future API access) | P3 | Future |
| FR-ST-07 | Feature flag overrides (user-level opt-in/opt-out) | P1 | Toggle in settings; syncs to user_preferences |

---

## 8. Non-Functional Requirements

### 8.1 Performance Requirements

| ID | Requirement | Target | Measurement | Violation Consequence |
|---|---|---|---|---|
| NFR-P-01 | API P95 response time | <200ms | Prometheus + Grafana (or Supabase analytics) | P1 bug â€” immediate investigation |
| NFR-P-02 | API P99 response time | <500ms | Same as above | P1 bug â€” investigate within 24h |
| NFR-P-03 | AI response time (P95) | <3s | Client-side timing | Fallback to algorithmic response |
| NFR-P-04 | AI response timeout | 30s max | Abort controller | Graceful error + fallback |
| NFR-P-05 | Page load time (first meaningful paint) | <1.5s on LTE | Lighthouse | P2 bug â€” optimize within sprint |
| NFR-P-06 | Lighthouse performance score | >90 | Lighthouse CI | Blocking (pre-GA) |
| NFR-P-07 | Lighthouse accessibility score | >85 | Lighthouse CI | P2 bug |
| NFR-P-08 | Lighthouse SEO score | >90 | Lighthouse CI | P2 bug |
| NFR-P-09 | Lighthouse best practices | >90 | Lighthouse CI | P1 bug |
| NFR-P-10 | Time to interactive | <2.5s on mid-range Android | Web Vitals | P1 bug |
| NFR-P-11 | Database query P95 | <100ms | Supabase query analytics | Add index / optimize query |
| NFR-P-12 | Static asset size (JS bundle) | <200KB gzipped | Next.js bundle analyzer | Code split / lazy load |
| NFR-P-13 | CRON job execution time | <60s per job | APScheduler logs | P1 bug â€” optimize or split |
| NFR-P-14 | Supabase storage read time | <500ms for typical query | Client timing | P2 bug |

### 8.2 Availability Requirements

| ID | Requirement | Target | Measurement | Notes |
|---|---|---|---|---|
| NFR-A-01 | System uptime (excl. planned maintenance) | >99.9% | Uptime monitoring (<8.76h downtime/year) | Based on Vercel + Railway + Supabase uptime |
| NFR-A-02 | Planned maintenance window | Sunday 2-4 AM IST | 2 hours/month maximum | Communicate 1 week in advance |
| NFR-A-03 | CRON job reliability | >99% of scheduled jobs execute | Job log audit | Retry mechanism: 3 attempts |
| NFR-A-04 | AI service availability | >95% (Ollama local) | Health check every 5 min | Fallback to Claude when down |
| NFR-A-05 | Degraded mode availability | 100% (core CRUD without AI) | Feature flag state | All non-AI features work without AI |

### 8.3 Security Requirements

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-S-01 | Row-Level Security on ALL database tables | 100% of 27 tables | Automated RLS audit script |
| NFR-S-02 | No API keys in client-side code | Zero exposure | CI scan for API key patterns |
| NFR-S-03 | Authentication via Supabase Auth (Google OAuth) | All users authenticated | Bypassing auth returns 401 |
| NFR-S-04 | JWT validation on every API request | 100% of protected endpoints | Integration test per endpoint |
| NFR-S-05 | Rate limiting on all endpoints | 100 requests/min/IP | Rate limiter unit tests |
| NFR-S-06 | Input sanitization on all user inputs | XSS, SQL injection protection | OWASP ZAP scan |
| NFR-S-07 | HTTPS enforced on all connections | 100% of traffic | Vercel + Railway default |
| NFR-S-08 | Passwordless auth only (Google OAuth) | No password storage | No password table exists |
| NFR-S-09 | Session timeout after 30 days of inactivity | Re-login required | Token refresh logic |
| NFR-S-10 | Audit log for sensitive operations (account deletion) | Logged to separate table | Audit trail check |

### 8.4 Scalability Requirements

| ID | Requirement | Target | Notes |
|---|---|---|---|
| NFR-SC-01 | Support 100 concurrent users on free tier | Verified with load test | Railway + Supabase free tier limits |
| NFR-SC-02 | Database query optimization for 10,000 users | P95 <200ms | Indexed columns, pagination |
| NFR-SC-03 | Database storage growth <1MB/user/month | Monitor and optimize | Archive old data if needed |
| NFR-SC-04 | CRON job queue handles 10,000 user jobs | Execution within time window | Batch processing for large user base |
| NFR-SC-05 | Static assets CDN-cached (Vercel Edge) | <50ms TTFB globally | Automatic via Vercel |
| NFR-SC-06 | AI request queue (serialize per user) | No concurrent AI requests per user | Prevent Ollama overload |

### 8.5 Reliability Requirements

| ID | Requirement | Target | Implementation |
|---|---|---|---|
| NFR-R-01 | Graceful degradation â€” all features work without AI | 100% feature coverage | Algorithmic fallback for every AI feature |
| NFR-R-02 | Offline CRUD â€” all write operations work offline | Tasks, courses, habits, income, ideas | IndexedDB + background sync |
| NFR-R-03 | Crash recovery â€” no data loss on browser crash | IndexedDB persistence | Pre-save to localStorage as backup |
| NFR-R-04 | API idempotency on POST (retry-safe) | No duplicate records on retry | Idempotency key on sensitive endpoints |
| NFR-R-05 | Database connection pooling | Handle 20 concurrent connections | Supabase pooler |
| NFR-R-06 | Error logging with context | All errors logged with user, action, timestamp | Structured JSON logging |

### 8.6 Usability Requirements

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-U-01 | New user onboarding to first task | <2 minutes | Timer measurement in onboarding |
| NFR-U-02 | Mobile-responsive on 360px width minimum | All pages render correctly | Responsive design audit |
| NFR-U-03 | PWA installable with offline support | Full offline CRUD | Lighthouse PWA audit |
| NFR-U-04 | Keyboard accessible (tab navigation) | WCAG 2.1 AA minimum | Accessibility audit |
| NFR-U-05 | Color contrast ratio | 4.5:1 minimum for text | Design token verification |
| NFR-U-06 | Error messages in plain English | User-actionable error messages | UI review |
| NFR-U-07 | Loading states on all async operations | Spinner/skeleton on every fetch | UX audit |
| NFR-U-08 | Undo action on destructive operations | 5-second undo window | Soft delete + undo toast |

### 8.7 Maintainability Requirements

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-M-01 | TypeScript strict mode | No `any` types | tsc --noEmit check |
| NFR-M-02 | Python type hints on all functions | 100% coverage | mypy check |
| NFR-M-03 | ESLint + Ruff pass on CI | Zero warnings | CI job |
| NFR-M-04 | Test coverage > 70% for critical paths | Prompt loader, API endpoints | pytest coverage report |
| NFR-M-05 | ADR documented for all architecture decisions | Every decision has rationale | ADR directory review |
| NFR-M-06 | CHANGELOG.md maintained | Every release noted | Manual review |
| NFR-M-07 | Prompt frontmatter validated in CI | 100% of prompts valid | validate_prompts.py |
| NFR-M-08 | Dependencies updated quarterly | No critical vulnerabilities | npm audit + pip audit |

### 8.8 Data Requirements

| ID | Requirement | Target | Implementation |
|---|---|---|---|
| NFR-D-01 | Database backup daily | Point-in-time recovery | Supabase backup (automatic) |
| NFR-D-02 | Data retention â€” user data kept until account deletion | Deletion = permanent erase | Cascade delete on user deletion |
| NFR-D-03 | Data portability â€” export in JSON + CSV | All tables exportable | Export endpoint |
| NFR-D-04 | Archival policy â€” logs kept for 90 days | Older logs purged | Cron job for archive |
| NFR-D-05 | PII minimization â€” only essential data collected | No location, no contacts, no device data | Data audit |

---

## 9. Assumptions and Constraints

### 9.1 Assumptions

| ID | Assumption | Impact if Wrong | Mitigation |
|---|---|---|---|
| A-01 | Target users have basic CLI proficiency (can run npm/pip commands) | Product unusable for intended audience | Provide 1-click deploy template (Railway + Vercel) |
| A-02 | Free-tier services remain free for foreseeable future | Infrastructure costs increase | Monitor pricing pages; migrate if needed |
| A-03 | Ollama runs reliably on consumer laptops (8GB RAM+) | AI features fail for low-RAM users | Claude API fallback for all AI features |
| A-04 | Students have reliable internet for most daily usage | Offline features underused | Still build PWA offline; sync when online |
| A-05 | Users are willing to self-host/self-configure | Low adoption due to setup friction | Deploy guide video; Railway template |
| A-06 | Google OAuth is the preferred auth method | Users without Google accounts cannot log in | Add email magic link as alternative |
| A-07 | Brave Search API free tier (2000 queries/month) is sufficient | Radar must be less frequent | Reduce scan frequency; cache results |
| A-08 | Morning briefing provides daily value | Users ignore briefings | A/B test timing, format; add opt-out |

### 9.2 Constraints

| ID | Constraint | Source | Impact |
|---|---|---|---|
| C-01 | Solo developer, part-time (10-15 hrs/week) | Resource | 12-month timeline; reduced feature scope |
| C-02 | Rs. 0 infrastructure budget | Business model | No paid tiers; must fit free-tier limits |
| C-03 | No dedicated designer | Resource | Cyberpunk design system must be self-contained |
| C-04 | No QA or support team | Resource | Self-testing only; self-serve documentation |
| C-05 | No legal entity or liability coverage | Business | Best-effort availability; no SLA |
| C-06 | India geographic focus (opportunity sources, academic) | Business | International expansion deferred to Year 2+ |
| C-07 | Single-user architecture per ADR-002 | Architecture | No collaboration features until Year 3 |
| C-08 | Supabase free tier limits: 500MB DB, 50MB transfer/day | Infrastructure | Pagination (20 items max); aggressive caching |
| C-09 | Brave Search: 2000 queries/month | Infrastructure | Radar limited to ~66 searches/day |
| C-10 | Resend free tier: 3000 emails/month | Infrastructure | ~100 days of daily briefings at 1 email/user |
| C-11 | Claude API: $5 free credits | Infrastructure | Heavy AI must use Ollama after credits exhausted |
| C-12 | Twilio: $15 one-time free credits | Infrastructure | SMS for critical P0 tasks only |

---

## 10. Dependencies

### 10.1 Internal Dependencies

| Dependency | From | To | Nature |
|---|---|---|---|
| User authentication | Supabase Auth | All modules | Every module requires authenticated user |
| Database | Supabase PostgreSQL | All modules | All data operations depend on schema |
| API layer | FastAPI server | Frontend components | All CRUD flows through API |
| PromptLoader | packages/ai/prompt_loader.py | All agent modules | Agent prompts loaded from `prompts/` directory |
| Context builder | Phase 4 | All advanced AI agents | Agents need assembled context |
| Task module | Phase 1 | Briefing, review, reschedule | Briefing needs task data |
| Course module | Phase 1 | Learning agent, nudge agent | Agents need course progress |
| Skill profile | Phase 1 | Opportunity radar, income | Radar matches skills; income links to skills |

### 10.2 External Dependencies

| Dependency | Provider | Criticality | Alternative |
|---|---|---|---|
| **Authentication** | Supabase Auth | Critical | Auth0, Clerk (free tiers) |
| **Database** | Supabase PostgreSQL | Critical | Neon.tech (PostgreSQL), PlanetScale |
| **Frontend hosting** | Vercel | Critical | Netlify, Cloudflare Pages |
| **Backend hosting** | Railway | Critical | Render, Fly.io |
| **LLM (primary)** | Ollama (local Mistral 7B) | High | Llama 3.1, Phi-3 |
| **LLM (fallback)** | Claude API (Anthropic) | Medium | OpenAI GPT-4o-mini, Gemini API |
| **Web search** | Brave Search API | Medium | SerpAPI, Google Custom Search |
| **Email delivery** | Resend | Medium (non-critical) | SendGrid (100 emails/day), SMTP |
| **SMS** | Twilio | Low (critical tasks only) | Vonage, AWS SNS |
| **GitHub API** | GitHub | Medium | Manual commit logging |
| **Google Calendar** | Google OAuth | Low (enhancement) | Manual calendar view |

### 10.3 Dependency Risk Assessment

| Dependency | Risk | Mitigation |
|---|---|---|
| **Ollama (local AI)** | High â€” may not run on low-RAM devices | Claude fallback + algorithmic fallback |
| **Supabase free tier** | Medium â€” limits may be reached | Cache aggressively; paginate; compress |
| **Vercel free tier** | Low â€” generous limits | Optimize bandwidth (100GB/month) |
| **Railway free tier** | Medium â€” may deprecate free plan | Maintain Dockerfile for alternative hosts |
| **Claude API credits** | Medium â€” $5 exhausts quickly | Ollama for 80% of calls; token budget limits |
| **Brave Search free tier** | Medium â€” 2000 queries/month limit | Cache results for 24h; reduce scan diversity |
| **Browser extension stores** | Low â€” may reject extension | WXT cross-browser; sideload guide |

---

## 11. Success Criteria (KPIs per Module)

### 11.1 Module-Level KPIs

| Module | KPI | Target | Measurement | Collection Method |
|---|---|---|---|---|
| **Dashboard** | DAU/MAU ratio | >40% | (DAU / MAU) * 100 | Supabase auth.sign_in events |
| **Dashboard** | Time to first meaningful paint | <1.5s | Lighthouse | Lighthouse CI |
| **Tasks** | Tasks completed per week (per user) | >15 | COUNT(tasks) WHERE status = 'completed' AND week = current | Scheduled query |
| **Tasks** | Auto-reschedule accuracy | <15% re-rescheduled | COUNT(rescheduled = true AND rescheduled_from IS NOT NULL) | Cron audit |
| **Courses** | Course completion rate | >70% | COUNT(progress = 100) / COUNT(total courses) * 100 | Trigger on progress update |
| **Courses** | Courses started per semester | >4 | COUNT(courses.created_at in semester) | Semester date filter |
| **Goals** | Goals with >50% progress | >3 | COUNT(progress >= 50) | Scheduled query |
| **YouTube Vault** | Weekly videos saved | >3 | COUNT(resources WHERE type = 'video') | Weekly aggregate |
| **Resources** | Resource â†’ goal link rate | >50% | COUNT(goal_id IS NOT NULL) / COUNT(*) | Scheduled query |
| **Ideas** | Ideas moved to "building" per month | >1 | COUNT(status = 'building') per month | Monthly aggregate |
| **Opportunities** | Opportunities applied to per week | >2 | COUNT(status = 'applied') | Weekly aggregate |
| **Opportunities** | Radar match relevance | >60% with match_score >= 50 | opportunities.match_score distribution | Distribution query |
| **Income** | Weeks with â‰¥1 income entry | >70% | COUNT(DISTINCT iso_week) / total_weeks | Weekly cron |
| **Projects** | Projects with >2 phases completed | >2 | COUNT(phases WHERE status = 'completed') >= 2 | Scheduled |
| **Academics** | CGPA projection accuracy | Within 0.2 of actual | ABS(projected - actual) | After each semester |
| **Habits** | Average habit consistency | >50% | (completed_logs / expected_logs) * 100 for last 30 days | Daily cron |
| **Sleep** | Nights logged per week | >4 | COUNT(sleep_logs per week) | Weekly aggregate |
| **Sleep** | Avg sleep duration | >7h | AVG(duration) per week | Weekly aggregate |
| **Time** | Deep work hours per week | >10 | SUM(duration WHERE deep_work = true) | Weekly aggregate |
| **Time** | Time tracked as % of estimated | >80% | SUM(time_entries.duration) / SUM(tasks.estimated_duration) | Cron |
| **Briefing** | Briefing read within 1 hour | >80% | daily_briefings.was_read AND read_at - created_at < 1h | Cron + trigger |
| **Review** | Weekly review generation | 100% of Sundays | COUNT(weekly_reviews.created_at on Sunday) | Weekly check |
| **Chat** | ARIA chat sessions per week | >5 | COUNT(sessions with >= 3 messages) | Weekly aggregate |
| **Memory** | Memory retention rate | >90% after 30 days | COUNT(memory where not discarded by agent) | Cron |

### 11.2 Business-Level KPIs

| KPI | Target | Measurement Frequency | Reporting |
|---|---|---|---|
| Daily Active Users (DAU) | 100 (Year 1) | Daily | Metrics dashboard |
| Monthly Active Users (MAU) | 200 (Year 1) | Monthly | Growth report |
| 30-Day Retention | >60% | Rolling 30 days | Cohort analysis |
| NPS Score | >40 | Quarterly | Survey |
| User Lifetime | >6 months (avg) | Quarterly | Churn analysis |
| Organic Referral Rate | >0.3 | Monthly | Referral tracking |
| Infrastructure Cost | <Rs. 100/month | Monthly | Cost dashboard |
| CI Pass Rate | >95% | Per commit | GitHub Actions |
| Bug Count | <5/month (P0-P1) | Monthly | GitHub issues |
| Feature Adoption (core modules) | >80% of users use >3 modules | Monthly | Module usage analytics |

### 11.3 KPI Dashboard

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                KPI DASHBOARD â€” EXECUTIVE VIEW                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚  GROWTH                ENGAGEMENT             QUALITY           â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ DAU: 42/100    â”‚   â”‚ Task Comp/Wk   â”‚   â”‚ API P95: 145ms â”‚   â”‚
â”‚  â”‚ MAU: 89/200    â”‚   â”‚   18.3/15 âœ“    â”‚   â”‚     âœ“ <200ms   â”‚   â”‚
â”‚  â”‚ Retention:     â”‚   â”‚ Briefing Read  â”‚   â”‚ Lighthouse:    â”‚   â”‚
â”‚  â”‚   72%/60% âœ“    â”‚   â”‚   84%/80% âœ“    â”‚   â”‚   92/90 âœ“      â”‚   â”‚
â”‚  â”‚ Referral:      â”‚   â”‚ Radar App/Wk   â”‚   â”‚ CI Pass:       â”‚   â”‚
â”‚  â”‚   0.35/0.3 âœ“   â”‚   â”‚   2.4/2 âœ“      â”‚   â”‚   97%/95% âœ“    â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                                 â”‚
â”‚  COST                    MODULE HEALTH                          â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ Infrastructure â”‚   â”‚ Tasks: â— Courses: â— Goals: â—       â”‚   â”‚
â”‚  â”‚ Rs. 47/month âœ“ â”‚   â”‚ Radar: â—‹ Briefing: â— Review: â—    â”‚   â”‚
â”‚  â”‚ Budget: Rs. 100â”‚   â”‚ Sleep: â— Habits: â— Income: â—‹      â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 12. Risk Assessment

### 12.1 Complete Risk Register

| ID | Risk | Category | Probability | Impact | Risk Score | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-01 | **User churns before seeing value** | Product | High | High | 16 | 7 AM briefing drives daily habit from Day 1; onboarding reduces to <2 min to first value | Product Lead |
| R-02 | **AI API credits exhausted** | Technical | Medium | High | 12 | Ollama primary (80% calls); Claude secondary; algorithmic fallback as safety net | Product Lead |
| R-03 | **Scraping restrictions from opportunity sources** | External | Medium | Medium | 9 | User bookmarklet + manual add; daily rotation of sources | Product Lead |
| R-04 | **Supabase free tier shut down or degraded** | External | Low | High | 8 | Database export script; migration to SQLite for offline-critical data | Product Lead |
| R-05 | **Competitor launches free student AI tool** | Market | Medium | Medium | 9 | Rs. 0 moat + student-specific features + privacy differentiation | Product Lead |
| R-06 | **Developer burnout** | Team | High | High | 16 | 10-15 hr/week max; sustainability over velocity; celebrate phase completions | Developer |
| R-07 | **Browser extension rejected by store** | External | Medium | Medium | 9 | WXT cross-browser (Chrome + Firefox); sideload guide as fallback | Product Lead |
| R-08 | **Data security incident** | Security | Low | Critical | 8 | RLS on all tables; no client-side keys; audit log; immediate rotation plan | Product Lead |
| R-09 | **Low quality AI responses disappoint users** | Product | Medium | High | 12 | Gradual rollout with feature flags; algorithmic fallback always available; user feedback collection | Product Lead |
| R-10 | **Exam period kills development velocity** | Team | High | Medium | 12 | Buffer weeks; reduced scope during exam months (Phase 6 scheduled in Q1) | Developer |
| R-11 | **Low adoption after public release** | Market | Medium | High | 12 | Target 100 users (0.02% of SAM); low bar makes success achievable | Product Lead |
| R-12 | **Platform dependency lock-in** | Technical | Medium | High | 12 | Dockerfile for portability; standard SQL; avoid proprietary features | Developer |
| R-13 | **Feature scope creep** | Product | High | Medium | 12 | "Builder test" for every new feature; explicit out-of-scope list | Product Lead |
| R-14 | **User data loss** | Technical | Low | Critical | 8 | IndexedDB backup; Supabase point-in-time recovery; regular exports | Product Lead |
| R-15 | **Open-source community conflict** | Community | Low | Medium | 6 | CODE_OF_CONDUCT; transparent governance; maintainer holds final decision | Developer |

### 12.2 Risk Mitigation Budget

| Mitigation Type | Budget (Hours) | Description |
|---|---|---|
| **Preventive** | 40 hours (quarterly) | Code audits, dependency updates, security reviews |
| **Detective** | 20 hours (quarterly) | Monitoring setup, alert configuration, log analysis |
| **Corrective** | 60 hours (annual) | Incident response, bug fixes, security patches |
| **Total risk budget** | **120 hours/year** | ~20% of total development capacity |

### 12.3 Risk Monitoring Cadence

| Risk | Monitor | Frequency | Escalation |
|---|---|---|---|
| R-01 (Churn) | User retention cohort analysis | Weekly | If 30-day retention <40%, investigate onboarding |
| R-02 (API costs) | API usage dashboard | Monthly | If costs exceed Rs. 100/month, restrict Claude usage |
| R-04 (Supabase) | Supabase status page | Daily | If limits reach 80%, archive old data |
| R-08 (Security) | CI security scan | Per commit | Any finding â†’ immediate fix within 24h |
| R-11 (Adoption) | User signup analytics | Weekly | If <5 new users/week post-launch, revise GTM |

---

## 13. Regulatory and Compliance Requirements

### 13.1 Data Protection

| Requirement | Compliance Approach | Status |
|---|---|---|
| **Indian IT Act 2000 (Section 43A)** â€” Reasonable security practices for sensitive data | RLS on all tables; encryption in transit (HTTPS); no client-side secrets | âœ… Designed-in |
| **Digital Personal Data Protection Act 2023 (India)** â€” User consent, data minimization, right to erasure | Explicit consent on signup; data minimization (no unnecessary PII); account deletion = full erasure | âœ… Designed-in |
| **GDPR (future international expansion)** â€” Data portability, right to be forgotten | JSON/CSV export; account deletion cascades to all tables | âœ… Export ready; GDPR notice needed post-EU expansion |

### 13.2 Accessibility

| Requirement | Compliance Approach | Target |
|---|---|---|
| **WCAG 2.1 Level AA** | Semantic HTML; ARIA labels; keyboard navigation; color contrast 4.5:1 | Lighthouse a11y score >85 |

### 13.3 Open Source Compliance

| Requirement | Compliance Approach |
|---|---|
| **MIT License** | LICENSE file included; all dependencies MIT/Apache 2.0 compatible |
| **Dependency license audit** | Check all npm/pip dependencies for license compatibility pre-release |
| **Contribution licensing** | CONTRIBUTING.md specifies DCO (Developer Certificate of Origin) |

### 13.4 What Does NOT Apply

| Regulation | Reason for Non-Applicability |
|---|---|
| **PCI DSS** | No payment processing |
| **HIPAA** | No healthcare data |
| **COPPA** | Users are 18+ (college students) |
| **SOC 2** | Not an enterprise SaaS product |
| **ISO 27001** | Not applicable at current scale |

---

## 14. Budget and Resource Estimates

### 14.1 Development Investment

| Phase | Weeks | Hours | Category | Cost (Opportunity) |
|---|---|---|---|---|
| Phase 1 â€” Core Foundation | 3 | 45 | Infrastructure, auth, CRUD | Rs. 0 (student time) |
| Phase 2 â€” Save Everything | 3 | 40 | Content modules, extension | Rs. 0 |
| Phase 3 â€” ARIA & Core AI | 4 | 50 | AI integration, prompts | Rs. 0 |
| Phase 4 â€” Advanced AI | 5 | 55 | Agents, radar, context | Rs. 0 |
| Phase 5 â€” Roadmap Engine | 3 | 40 | Visual builder, AI parsing | Rs. 0 |
| Phase 6 â€” Full Life Tracking | 8 | 60 | Income, projects, academics, habits | Rs. 0 |
| Phase 7 â€” Monitoring | 4 | 45 | Reminders, sleep, time | Rs. 0 |
| Phase 8 â€” Polish & PWA | 2 | 30 | Offline, performance, security | Rs. 0 |
| Phase 9 â€” Public Release | 5 | 50 | GitHub, community, docs | Rs. 0 |
| Buffer / Exam Weeks | 8 | 40 | Contingency | Rs. 0 |
| **Total** | **48 weeks** | **~455 hours** | | **Rs. 0** |

### 14.2 Monthly Infrastructure Budget

| Service | Free Tier Limit | Expected Usage | Cost |
|---|---|---|---|
| **Vercel (Frontend)** | 100GB bandwidth, 100GB hours | <5GB bandwidth, <50GB hours | Rs. 0 |
| **Railway (Backend)** | $5 credit/month (or free tier) | ~$0-3/month equivalent | Rs. 0-250 |
| **Supabase (Database)** | 500MB database, 50MB transfer/day | <200MB database, <10MB transfer/day | Rs. 0 |
| **Ollama (AI)** | Local machine â€” free | Running on developer's laptop | Rs. 0 |
| **Claude API** | $5 free credits | ~$2-3/month (fallback only) | Rs. 0 (until credits exhaust) |
| **Brave Search** | 2000 queries/month | ~500-1000 queries/month | Rs. 0 |
| **Resend (Email)** | 3000 emails/month | ~300-1000 emails/month | Rs. 0 |
| **Twilio (SMS)** | $15 one-time credits | ~$0.50/month (critical only) | Rs. 0-40 |
| **GitHub (Code)** | Unlimited public repos | 1 public repo | Rs. 0 |
| **Total** | | | **Rs. 0-290/month** |

### 14.3 Resource Allocation (Human)

| Resource | Availability | Role |
|---|---|---|
| **Developer** | 10-15 hrs/week, part-time | Full-stack development, AI, DevOps, product decisions |
| **Early Testers** | ~2 hrs/week each (2-5 people) | Usability testing, bug reporting, feature feedback |
| **Community Contributors** | Variable (post-GA) | Bug fixes, documentation, plugin development |

### 14.4 Resource Constraints Summary

| Resource | Constraint | Impact |
|---|---|---|
| **Time** | 10-15 hrs/week | Extended timeline; must prioritize ruthlessly |
| **Money** | Rs. 0/month | Must use free tiers; no paid tools |
| **Design** | No dedicated designer | Self-contained design system; must be consistent |
| **Testing** | Self-testing only | Bugs may reach users; quick iteration required |
| **Support** | No support team | Self-serve documentation; community support post-GA |

---

## 15. Timeline

### 15.1 Phase Timeline

| Phase | Start | End | Duration | Weeks | Milestone |
|---|---|---|---|---|---|
| Phase 1 â€” Core Foundation | Jul 6, 2026 | Jul 26, 2026 | 3 weeks | 1-3 | Working app with login, tasks, courses, dashboard |
| Phase 2 â€” Save Everything | Jul 27, 2026 | Aug 16, 2026 | 3 weeks | 4-6 | Content capture modules, browser extension |
| Phase 3 â€” ARIA & Core AI | Aug 17, 2026 | Sep 13, 2026 | 4 weeks | 7-10 | ARIA chat, daily briefing, weekly review |
| **ALPHA** | **Sep 13, 2026** | â€” | â€” | 10 | All 15 modules + basic AI |
| Phase 4 â€” Advanced AI | Sep 14, 2026 | Oct 18, 2026 | 5 weeks | 11-15 | Learning agent, radar, context engine, sleep, nudge |
| **BETA** | **Oct 18, 2026** | â€” | â€” | 15 | Advanced AI complete |
| Phase 5 â€” Roadmap Engine | Oct 19, 2026 | Nov 8, 2026 | 3 weeks | 16-18 | Visual roadmap builder, AI parsing |
| Phase 6 â€” Full Life Tracking | Nov 9, 2026 | Jan 3, 2027 | 8 weeks | 19-26 | Income, projects, academics, habits |
| Phase 7 â€” Monitoring & Automation | Jan 4, 2027 | Jan 31, 2027 | 4 weeks | 27-30 | Reminders, sleep, time tracking |
| Phase 8 â€” Polish & Production | Feb 1, 2027 | Feb 14, 2027 | 2 weeks | 30-31 | PWA, offline, security audit |
| **GA CANDIDATE** | **Feb 14, 2027** | â€” | â€” | 31 | Stable, complete feature set |
| Phase 9 â€” Public Release | Feb 15, 2027 | Mar 21, 2027 | 5 weeks | 32-36 | GitHub public, community infrastructure |
| **GA LAUNCH** | **Mar 21, 2027** | â€” | â€” | 36 | Public availability |
| Buffer / Mobile Preview | Mar 22, 2027 | May 16, 2027 | 8 weeks | 37-44 | Contingency + mobile app preview |
| Post-GA Stabilization | May 17, 2027 | Jun 27, 2027 | 6 weeks | 45-50 | Bug fixes, performance optimization, v2 planning |

### 15.2 Critical Milestones

| Milestone | Date | Deliverable | Gate Criteria |
|---|---|---|---|
| **M1: Auth + Tasks** | Jul 19, 2026 | Login + task CRUD | Can login with Google, create/edit/complete/delete tasks |
| **M2: Courses + Goals** | Jul 26, 2026 | Course + goal tracking | Course with progress, goal with milestones |
| **M3: Full Dashboard** | Jul 26, 2026 | Dashboard overview | All core modules visible on dashboard |
| **M4: Content Capture** | Aug 16, 2026 | YouTube + Resources + Ideas | All three save modules operational |
| **M5: ARIA Chat** | Aug 30, 2026 | AI chat with memory | Chat responds, remembers user facts |
| **M6: Daily Briefing** | Sep 6, 2026 | 7 AM AI briefing | Briefing generates daily, delivers in-app + email |
| **M7: Weekly Review** | Sep 13, 2026 | Sunday AI review | Review generates with narrative + data |
| **M8: ALPHA** | Sep 13, 2026 | Complete system | 30 tests pass; developer using daily for 1 week |
| **M9: Opportunity Radar** | Oct 4, 2026 | Daily opportunity scans | â‰¥3 relevant matches found daily |
| **M10: Context Engine** | Oct 11, 2026 | Full context assembly | AI responses include user goals, tasks, courses |
| **M11: Sleep + Nudge** | Oct 18, 2026 | Automated agents | Wind-down 9:30 PM; nudge 6 PM |
| **M12: BETA** | Oct 18, 2026 | Advanced AI | 11 agents operational; 30+ tests |
| **M13: Roadmap Builder** | Nov 8, 2026 | Visual + AI roadmap | Drag-drop + textâ†’roadmap both work |
| **M14: Income + Projects** | Dec 6, 2026 | Income/project tracking | Log income, track project phases |
| **M15: Academics + CGPA** | Dec 20, 2026 | Academic planning | CGPA projected within 0.2 of actual |
| **M16: Habits + Streaks** | Jan 3, 2027 | Habit engine | Streaks tracked; consistency reports |
| **M17: Monitoring Suite** | Jan 31, 2027 | Time/sleep/reminders | All three monitoring modules operational |
| **M18: PWA + Offline** | Feb 7, 2027 | Production-ready PWA | Lighthouse >90; offline CRUD works |
| **M19: GA CANDIDATE** | Feb 14, 2027 | Stable release | All tests pass; security audit OK |
| **M20: PUBLIC LAUNCH** | Mar 7, 2027 | GitHub public | README, demo, deploy guide, community infra |
| **M21: GA** | Mar 21, 2027 | General availability | Community infrastructure live, public launch |

### 15.3 Timeline Buffer

| Buffer Type | Weeks | Usage |
|---|---|---|
| **Exam buffer** | 4 | Reduced output during Oct (mid-sem), Dec (end-sem), Apr (final) exams |
| **Technical buffer** | 4 | Unexpected bugs, integration issues, dependency problems |
| **Health/personal buffer** | 2 | Illness, family events, mental health breaks |
| **Total buffer** | **10 weeks** | Embedded in 52-week plan |

---

## 16. Glossary

### 16.1 Product Terms

| Term | Definition |
|---|---|
| **ARIA** | AI-powered orchestration agent that coordinates sub-agents and user interaction across all 15 modules |
| **Sub-Agent** | Specialized AI module (briefing, memory, learning, opportunity, sleep, nudge, etc.) â€” 8 total |
| **Second Brain OS** | Full product name â€” the personal AI productivity system |
| **Zero-Miss** | System property where no task, deadline, or commitment silently expires â€” every item is either done, rescheduled, or explicitly dropped |
| **Opportunity Radar** | Daily 6 AM automated scan of 6 categories (internships, hackathons, fellowships, open-source, freelance, grants) matched to user skills |
| **Resurface Engine** | Algorithm that identifies and re-presents saved content (resources, ideas) at contextually relevant moments based on active goals |
| **Context Engine** | Pipeline that assembles user data (profile, goals, tasks, courses, skills) into LLM-optimized system prompts for ARIA |
| **PromptLoader** | Python singleton that loads, parses, and validates all AI prompt files from `prompts/` directory with YAML frontmatter |
| **Skill-to-Income** | Direct mapping between skills tracked in the system and income earned, enabling effective hourly rate calculation |

### 16.2 Business Terms

| Term | Definition |
|---|---|
| **PMF** | Product-Market Fit â€” state where a product satisfies strong market demand |
| **DAU** | Daily Active Users â€” unique users who log in within a 24-hour period |
| **MAU** | Monthly Active Users â€” unique users who log in within a 30-day period |
| **DAU/MAU** | Engagement ratio â€” percentage of monthly users who use the product daily |
| **NPS** | Net Promoter Score â€” user satisfaction metric (-100 to +100) based on "how likely to recommend" |
| **TAM** | Total Addressable Market â€” total revenue opportunity available if 100% market share |
| **SAM** | Serviceable Addressable Market â€” segment of TAM within product's reach |
| **SOM** | Serviceable Obtainable Market â€” realistic adoption given constraints |
| **Retention** | Percentage of users who return after a given period (Day 1, Day 7, Day 30) |
| **Churn** | Percentage of users who stop using the product within a given period |
| **LTV** | Lifetime Value â€” total value a user generates over their relationship with the product |
| **CAC** | Customer Acquisition Cost â€” cost to acquire one user (Rs. 0 for organic) |
| **GTM** | Go-To-Market strategy â€” plan for reaching target users and achieving adoption |
| **SLA** | Service Level Agreement â€” commitment to uptime, response time, etc. |
| **OKR** | Objectives and Key Results â€” goal-setting framework |

### 16.3 Technical Terms

| Term | Definition |
|---|---|
| **RLS** | Row-Level Security â€” PostgreSQL policy ensuring users can only access their own data |
| **JWT** | JSON Web Token â€” authentication token format used by Supabase Auth |
| **PWA** | Progressive Web Application â€” installable web app with offline support |
| **IndexedDB** | Browser-based NoSQL database for offline data storage |
| **Service Worker** | Browser script that enables offline functionality and push notifications |
| **Ollama** | Local LLM server â€” runs Mistral 7B and other models on consumer hardware |
| **WXT** | Cross-browser extension framework (Chrome + Firefox from single codebase) |
| **APScheduler** | Python task scheduler for cron jobs (daily briefing, radar, etc.) |
| **P95/P99** | 95th/99th percentile response time â€” 95% of requests are faster than this value |
| **pgvector** | PostgreSQL extension for vector similarity search (used for semantic search) |

### 16.4 Metric Terms

| Term | Definition |
|---|---|
| **Task completion rate** | (Tasks completed / tasks created) * 100, measured per week |
| **Course completion rate** | (Courses with progress = 100% / total courses) * 100 |
| **Effective hourly rate** | Total income / total hours worked for that income |
| **Briefing read rate** | Briefings read within 1 hour / total briefings delivered |
| **Radar match relevance** | Opportunities with match_score >= 50 / total opportunities found |
| **Habit consistency** | (Habit completions / expected completions) * 100 over rolling 30 days |
| **Streak recovery rate** | Number of days to resume habit after a miss (lower is better) |
| **Deep work hours** | Hours with continuous >60 minute focus on single task |

---

## 17. Appendices

### Appendix A: Requirements Traceability Matrix

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚            REQUIREMENTS TRACEABILITY MATRIX (SAMPLE)           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚  BRD ID  â”‚ Module   â”‚ Priority â”‚ SRS ID  â”‚ Test ID â”‚ Status   â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚  FR-TK-01â”‚ Tasks    â”‚ P0       â”‚ SRS-4.1 â”‚ T-TK-01 â”‚ Planned  â”‚
â”‚  FR-TK-02â”‚ Tasks    â”‚ P0       â”‚ SRS-4.2 â”‚ T-TK-02 â”‚ Planned  â”‚
â”‚  FR-CR-01â”‚ Courses  â”‚ P0       â”‚ SRS-5.1 â”‚ T-CR-01 â”‚ Planned  â”‚
â”‚  FR-AI-01â”‚ Chat     â”‚ P0       â”‚ SRS-12.1â”‚ T-AI-01 â”‚ Planned  â”‚
â”‚  NFR-P-01â”‚ All      â”‚ P0       â”‚ SRS-2.1 â”‚ T-PF-01 â”‚ Planned  â”‚
â”‚  NFR-S-01â”‚ All      â”‚ P0       â”‚ SRS-3.1 â”‚ T-SC-01 â”‚ Planned  â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Appendix B: Document References

| Document | Location | Relevance |
|---|---|---|
| Product Vision | `docs/product/00_ProjectVision.md` | Long-term vision alignment |
| Build Roadmap | `docs/product/Roadmap.md` | Detailed implementation timeline |
| PRD / SRS | `docs/product/04_SRS.md` | Functional specifications by module |
| Architecture | `docs/engineering/12_Architecture.md` | System design, component interaction |
| Agent Architecture | `docs/ai/20_Agent.md` | AI agent design, prompt files |
| Design System | `docs/design/10_DesignSystem.md` | UI/UX design tokens, components |
| Competitive Analysis | `docs/product/CompetitiveAnalysis.md` | Market positioning, competitor comparison |
| AGENTS.md | `AGENTS.md` | Master reference â€” all AI agent instructions |
| ADR-002 | `docs/engineering/adr/ADR-002.md` | Single-user architecture decision |
| ADR-004 | `docs/engineering/adr/ADR-004.md` | In-process agent architecture decision |

### Appendix C: Business Model Canvas Summary

| Key Partners | Key Activities | Value Propositions | Customer Relationships | Customer Segments |
|---|---|---|---|---|
| Supabase, Vercel, Ollama, Brave Search, Resend, Anthropic (Claude) | AI agent development, 15 module CRUD, prompt engineering, community management | Rs. 0 AI productivity; all-in-one student OS; proactive intelligence; privacy-first | Self-serve (docs); community (Discord/GitHub); no support team | BTech CSE students (primary); self-taught programmers; recent graduates |

| Key Resources | | Channels | |
|---|---|---|---|
| Solo developer (10-15 hrs/week); free-tier infrastructure; open-source codebase | | GitHub; word of mouth; Hacker News; Reddit; Product Hunt; student communities | |

| Cost Structure | Revenue Streams |
|---|---|
| Rs. 0-290/month infrastructure; 455 hours development (opportunity cost: Rs. 0) | Rs. 0 (Year 1); donations (Year 2); premium AI + marketplace (Year 3); enterprise (Year 4+) |

### Appendix D: Glossary â€” Quick Reference Card

| Term | Quick Definition |
|---|---|
| ARIA | AI orchestrator â€” 11 agents |
| Zero-Miss | No task silently expires |
| Radar | Daily opportunity scanner |
| Resurface | Context-aware content recall |
| PromptLoader | Prompt file manager with validation |
| RLS | Database user isolation |
| PWA | Offline-capable web app |
| Ollama | Local AI server (Mistral 7B) |
| DAU/MAU | Daily/Monthly Active Users |
| NPS | User satisfaction score |
| TAM/SAM/SOM | Market size tiers |
| PMF | Product-Market Fit |
