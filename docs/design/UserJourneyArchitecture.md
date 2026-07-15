# User Journey Architecture — Second Brain OS (ARIA OS)

> **Single source of truth for user behavior, workflows, AI interaction points, cognitive load, and journey optimization.**
> Enterprise-grade design by a Principal UX Architect, User Journey Specialist, Enterprise Product Designer, Behavioral Design Expert, and AI Product Experience Architect.

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Journey Design Principles](#2-journey-design-principles)
3. [User Types](#3-user-types)
4. [User Archetypes](#4-user-archetypes)
5. [User Type Comparison Matrix](#5-user-type-comparison-matrix)

**Time-Based Journeys**
6. [Onboarding Journey](#6-onboarding-journey)
7. [First Day Journey](#7-first-day-journey)
8. [First Week Journey](#8-first-week-journey)
9. [First Month Journey](#9-first-month-journey)
10. [Daily Workflow Journey](#10-daily-workflow-journey)

**Recurring Journeys**
11. [Weekly Review Journey](#11-weekly-review-journey)
12. [Sleep & Wind-Down Journey](#12-sleep--wind-down-journey)

**Cross-Session Journeys**
13. [Cross-Session Journeys](#13-cross-session-journeys)

**Module-Specific Journey Maps**
14. [Module-Specific Journey Maps](#14-module-specific-journey-maps)

**Module Deep-Dive Journeys**
15. [Learning Journey](#15-learning-journey)
16. [Knowledge Journey](#16-knowledge-journey)
17. [Opportunity Journey](#17-opportunity-journey)
18. [Project Journey](#18-project-journey)
19. [Goal Journey](#19-goal-journey)
20. [Roadmap Journey](#20-roadmap-journey)
21. [Analytics Journey](#21-analytics-journey)
22. [AI Journey](#22-ai-journey)
23. [Search Journey](#23-search-journey)

**Platform Journeys**
24. [Mobile Journey](#24-mobile-journey)
25. [Tablet Journey](#25-tablet-journey)
26. [Desktop Journey](#26-desktop-journey)

**Retention & Exit**
27. [Exit & Retention Journeys](#27-exit--retention-journeys)

**Technical Architecture**
28. [Journey Technical Architecture](#28-journey-technical-architecture)

**Cross-Cutting Analysis**
29. [Cross-Cutting AI Intervention Points Map](#29-cross-cutting-ai-intervention-points-map)
30. [Cross-Cutting Friction Points Map](#30-cross-cutting-friction-points-map)
31. [Cross-Cutting Cognitive Load Map](#31-cross-cutting-cognitive-load-map)
32. [Cross-Cutting Drop-Off Risk Map](#32-cross-cutting-drop-off-risk-map)
33. [Cross-Cutting Optimization Opportunities](#33-cross-cutting-optimization-opportunities)
34. [Enterprise UX Recommendations](#34-enterprise-ux-recommendations)

**Appendices**
- [A: Journey Template Specification](#appendix-a-journey-template-specification)
- [B: User Type × Dimension Matrix](#appendix-b-user-type--dimension-matrix)
- [C: Cognitive Load Reference Scale](#appendix-c-cognitive-load-reference-scale)
- [D: Drop-Off Risk Reference Scale](#appendix-d-drop-off-risk-reference-scale)
- [E: User Story Cross-Reference](#appendix-e-user-story-cross-reference)
- [F: Glossary](#appendix-f-glossary)

---

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
flowchart TD
  subgraph T0["🕐 Time-Based Journeys"]
    direction TB
    ON[Onboarding<br/>Day 0-3] --> FD[First Day<br/>Core Capture]
    FD --> FW[First Week<br/>Habit Formation]
    FW --> FM[First Month<br/>Deep Integration]
    FM --> DW[Daily Workflow<br/>Morning→Evening]
  end

  subgraph R1["🔄 Recurring Journeys"]
    direction TB
    WR[Weekly Review<br/>Sunday 8 PM] --> SD[Sleep Wind-Down<br/>Nightly 9:30 PM]
    SD --> WR
  end

  subgraph CS["🔗 Cross-Session Journeys"]
    direction TB
    CT[Context Threads<br/>Multi-Session Tasks] --> GP[Goal Progression<br/>Quarterly Cycles]
    GP --> KP[Knowledge Persistence<br/>Long-Term Memory]
  end

  subgraph MS["📦 Module-Specific Journeys"]
    direction TB
    LJ[Learning Journey<br/>Course → Practice → Mastery]
    KJ[Knowledge Journey<br/>Capture → Organize → Retrieve]
    OJ[Opportunity Journey<br/>Discover → Match → Apply]
    PJ[Project Journey<br/>Idea → Build → Ship]
    GJ[Goal Journey<br/>Set → Track → Achieve]
  end

  T0 --> R1
  T0 --> CS
  T0 --> MS
  R1 --> MS
  CS --> MS

  subgraph AI["🤖 AI Intervention Points"]
    MB[Morning Briefing<br/>7 AM]
    OS[Opportunity Scan<br/>6 AM]
    PN[Progress Nudge<br/>6 PM]
    WD[Wind-Down<br/>9:30 PM]
  end

  DW --> MB
  DW --> OS
  DW --> PN
  WR --> WD

  style T0 fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style R1 fill:#13151A,stroke:#818CF8,color:#F1F5F9
  style CS fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style MS fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style AI fill:#13151A,stroke:#F59E0B,color:#F1F5F9
```

---

## 1. Executive Summary

### System Scope

Second Brain OS serves **8 distinct user types** across **18 journey types** spanning time-based, module-specific, and platform-specific experiences. Each journey is defined by an **18-field enterprise template** covering trigger, flow, AI assistance, cognitive load, drop-off risk, and optimization opportunities.

### Design Philosophy

**Think like Linear, Notion, Motion, ChatGPT, Cursor, and Stripe — but for personal productivity.**

| Influence | Applied As |
|---|---|
| **Linear** | Keyboard-first workflows, two-key navigation, comparison metrics |
| **Notion** | Page-as-folder mental model, cross-module linking, progressive complexity |
| **Motion** | AI-prioritized scheduling, time-blocked workflows, auto-rescheduling |
| **ChatGPT** | Natural language as primary input, conversational capture, AI-synthesized responses |
| **Cursor** | Inline AI assistance, contextual suggestions, agentic code-like workflows |
| **Stripe** | Card-less metrics, hierarchical data visibility, developer-friendly patterns |

### Key Design Targets

| Metric | Target | Why It Matters |
|---|---|---|
| Activation time (signup → first value) | <60 seconds | Trial bounce segment (10%) abandons if no immediate win |
| Daily value delivery | <3 minutes to morning briefing | Distracted users check, get value, close — or churn |
| Task capture friction | <5 seconds | The #1 barrier to consistent use |
| AI response time | <3 seconds (Claude) / <10 seconds (Ollama) | Cognitive flow breaks at >3s delay |
| Offline resilience | Full CRUD without network | Campus WiFi, commuting, travel are primary use contexts |
| Cognitive load per step | Max 5/10 (moderate) | High load causes abandonment (proven in 12-app-switch study) |
| Returning user catch-up | <30 seconds to see what matters | Crammer segment (35%) needs instant context |

### Journey Count

| Category | Count | Sections |
|---|---|---|
| User Types | 8 | Student Builder, Startup Founder, Freelancer, Creator, Knowledge Worker, Power User, New User, Returning User |
| Time-Based Journeys | 5 | Onboarding, First Day, First Week, First Month, Daily Workflow |
| Module Journeys | 9 | Learning, Knowledge, Opportunity, Project, Goal, Roadmap, Analytics, AI, Search |
| Platform Journeys | 3 | Mobile, Tablet, Desktop |
| Cross-Cutting Maps | 11 | Journey Maps, Workflow Maps, AI Intervention, AI Recommendation, AI Automation, Friction Points, Cognitive Load, Drop-Off, Optimization, Accessibility, Recommendations |
| **Total** | **36** | |

### Existing Documentation Cross-Reference

| Source Document | Integration Strategy |
|---|---|
| `docs/product/Personas.md` (5 personas, 562 lines) | Preserved and expanded — Arjun → Student Builder, Rahul → Freelancer, Ananya → Knowledge Worker, Priya + Kabir → Startup Founder |
| `docs/product/06_UserStories.md` (120 stories) | Every story mapped to at least one journey; US-IDs referenced throughout |
| `docs/product/UserFlows.md` (822 lines) | Existing flows reviewed, upgraded with AI/cognitive/drop-off dimensions |
| `docs/product/07_AcceptanceCriteria.md` | Referenced as success state validators |
| `docs/design/InformationArchitecture.md` | Navigation patterns referenced in journey entry/exit states |
| `docs/design/ProductArchitecture.md` | Domain boundaries referenced in cross-module workflows |

---

## 2. Journey Design Principles

### P1: First-Win in 60 Seconds

Every user's first session must deliver a tangible win in under 60 seconds. The onboarding journey is designed so the user creates meaningful content (not "test" data) within their first minute.

**Application:** The 5-step onboarding ends with a natural language task capture. The user says "I need to finish my DBMS assignment" and ARIA creates a dated, prioritized task. That's the first win.

### P2: Forgiveness over Guilt

Returning users are not punished for absence. The system never shows "You missed 14 tasks" without an actionable resolution. Every notification about overdue items includes a one-click "Reschedule all" or "Forgive all" option.

**Application:** The Crammer archetype (35% of users) returns after 2 weeks of absence to find a "Welcome back — here's what changed" digest, not a guilt-inducing overdue list.

### P3: AI as Copilot, Not Pilot

AI suggests, recommends, and automates — but never decides for the user. Every AI action is transparent ("I noticed you..."), reversible ("Undo"), and learnable ("Not helpful — don't suggest this again").

**Application:** When AI auto-reschedules overdue tasks, it shows: "I moved 3 tasks to tomorrow based on your energy level and deadlines. [Adjust] [Undo]"

### P4: Cross-Journey Continuity

No journey exists in isolation. Every journey references other journeys it connects to. The Learning Journey feeds the Project Journey. The Project Journey feeds the Income Journey. The Analytics Journey reflects all journeys.

**Application:** The "Complete Course" success state offers: "Create a project from this course" (→ Project Journey) and "Update your skills" (→ Opportunity Journey).

### P5: Progressive Complexity

The system reveals depth only when the user signals readiness. First session: capture, view, complete. Week 1: briefing, habits, sleep. Month 1: opportunity radar, income tracking, roadmap. Month 3: analytics, automation, custom views.

**Application:** The sidebar shows all 6 groups but highlights Core modules in the first week. Learn, Build, Earn modules emerge as the user creates relevant data.

### P6: Context Preservation

Every journey preserves the user's context across sessions. Scroll position, active filters, selected item, and search query are maintained. Navigating away and back returns to exactly where the user was.

**Application:** When a notification deep-links to a task, the user sees the task in context (with its project, goal, and related items) — not a detached detail page.

### P7: Offline Resilience

Every journey step that involves writing data must work without network connectivity. The sync queue (see InformationArchitecture.md §12.2) handles deferred writes transparently.

**Application:** A Freelancer logging income on a train with no signal sees the entry saved locally. When signal returns, it syncs silently. If conflict detected, user is notified with resolution options.

### P8: Cognitive Load Budget

No single journey step exceeds **5/10 on the cognitive load scale** (see Appendix C). Steps exceeding this threshold must be split into sub-steps or deferred to AI assistance.

**Application:** Creating a roadmap from scratch (load = 8/10) is never required. The user pastes a syllabus or job description, and AI builds 80% of the roadmap. User adjusts (load = 3/10).

### P9: Friction Transparency

When the user encounters friction (slow load, sync error, AI timeout), the system communicates transparently: what happened, why, what's being done, and what the user should do.

**Application:** "Your briefing is taking longer than usual because Ollama is processing. You can view cached data now or wait for the full briefing (~15 seconds)."

### P10: Platform-Appropriate Journeys

Every journey is designed with the platform's strengths in mind. Mobile = capture, check, quick actions. Desktop = create, organize, analyze. Tablet = review, learn, browse.

**Application:** The Daily Briefing on mobile shows 3 items (top tasks, one metric, one opportunity). On desktop, it shows all 8 dashboard zones. Same content model, different density.

---

## 3. User Types

### 3.1 Student Builder

| Field | Detail |
|---|---|
| **Foundation** | Arjun Mehta (VIT, 2nd year) + Priya Sharma (DTU, 3rd year) |
| **Population** | 40% of users |
| **Primary Device** | Laptop (Dell Inspiron/MacBook Air) + Android/iPhone |
| **Technical Level** | Intermediate (VS Code, basic git, ChatGPT power user) |
| **Income Level** | ₹0-5,000/month (parents + occasional freelance) |
| **Willingness to Pay** | ₹0-200/month |

#### Goals
| Goal Type | Goal | Timeline | Motivation |
|---|---|---|---|
| Academic | Maintain 8.5+ CGPA | Ongoing | Placement eligibility, scholarship |
| Career | FAANG/product company internship | 12-18 months | Peer pressure, family expectations |
| Skills | Master full-stack development | 6 months | Build portfolio for placements |
| Financial | Earn ₹15,000/month from freelancing | 12 months | Reduce dependency on parents |
| Health | Exercise 4x/week, sleep 7+ hours | Ongoing | Burnout prevention |
| Projects | Ship 3 complete portfolio projects | 12 months | Resume differentiation |
| Learning | Complete 6 online courses (not start 20) | 12 months | Stop course accumulation guilt |

#### Motivations
- Fear of missing out on placement opportunities
- Peer comparison ("everyone else is ahead")
- Genuine love for building things
- Desire for financial independence
- Parental approval and family pride

#### Frustrations
| Frustration | Severity | Frequency | Current Non-Solution |
|---|---|---|---|
| Course overload: enrolled in 6 courses, completed 0 | 9/10 | Weekly | Opens courses, feels overwhelmed, closes |
| Tool fragmentation: tasks in Todoist, notes in Notion, deadlines in Calendar, no unified view | 9/10 | Daily | Checks 4 apps to see what's due today |
| Missed opportunity deadlines: internships, hackathons | 8/10 | Monthly | "I'll check more often" — never does |
| Idea graveyard: 20+ startup ideas, none started | 7/10 | Weekly | Re-reads old ideas, feels regret |
| Sleep procrastination: knows needs sleep, can't stop phone use | 7/10 | Daily | Tried 5 sleep apps, all deleted |
| Skill dilution: reaches 30-40% in courses, starts new shinier one | 8/10 | Monthly | "This course is better" — repeats cycle |
| Zero income visibility: knows freelanced but has no breakdown | 5/10 | Quarterly | Ballparks when asked |

#### Daily Needs
- Morning: Know what's due today + top priority (5 min)
- Daytime: Quick task capture (<5 seconds), timer for focus sessions
- Evening: See what was completed, log study hours
- Night: Log sleep, wind-down reminder

#### Weekly Needs
- See course progress across all enrollments
- Review task completion rate and patterns
- Check for new opportunities (internships, hackathons)
- Log income from freelance work
- Review habit streaks

#### Monthly Needs
- Course completion assessment (which courses to finish, which to drop)
- Income vs. goals comparison
- Skill level updates based on completed work
- Project portfolio review
- Goal progress check

#### Success Metrics
| Metric | Target | Measurement |
|---|---|---|
| Task completion rate | >60% | Tasks completed / tasks created (weekly) |
| Course completion rate | >50% | Courses completed / courses enrolled (semester) |
| Study consistency | >5 days/week | Study sessions logged (weekly) |
| Opportunity applications | >2/month | Applications submitted |
| Income tracking | 100% of income logged | Income entries vs. bank deposits |
| Sleep consistency | >6.5h average | Sleep logs (weekly average) |
| Habit streak | >21 days | Longest active streak |
| Briefing utility | Rated 4/5+ | Weekly NPS prompt in review |

#### Core Workflows
| Workflow | Frequency | AI Involvement | Critical Path |
|---|---|---|---|
| Morning briefing review | Daily | A09 generates briefing | Dashboard → Review → Adjust → Start work |
| Task capture + triage | 5-10x/day | A01 suggests priority | Quick capture → AI classifies → Confirm → Continue |
| Study session with timer | 1-3x/day | A14 nudges if missed | Open course → Start timer → Study → Log → Review tomorrow |
| Course progress check | 2-3x/week | None | Open courses → View progress → Plan next study |
| Opportunity scan | 1-2x/week | A06 finds matches | Notification → Review match → Apply/Save/Dismiss |
| Weekly review | Sunday | A10 generates report | Notification → Open → Reflect → Set next week intent |

---

### 3.2 Startup Founder

| Field | Detail |
|---|---|
| **Foundation** | Synthesized from Priya Sharma's ambitions + Kabir Singh's side-project drive + research |
| **Population** | 10% of users |
| **Primary Device** | MacBook Pro + iPhone, multiple monitors |
| **Technical Level** | High (can code, deploy, use APIs) |
| **Income Level** | ₹0-50,000/month (variable, bootstrapping) |
| **Willingness to Pay** | ₹500-1,500/month |

#### Goals
| Goal Type | Goal | Timeline | Motivation |
|---|---|---|---|
| Product | Ship MVP with core feature set | 3 months | Validate before overbuilding |
| Users | Acquire first 100 active users | 6 months | Product-market fit signal |
| Revenue | Reach ₹30,000 MRR | 12 months | Sustainability |
| Funding | Raise pre-seed/seed round | 12-18 months | Scale |
| Skills | Full-stack + product + growth | Ongoing | Founder needs everything |
| Network | Build peer founder group | 6 months | Accountability and support |

#### Motivations
- Desire to build something from nothing
- Autonomy and control over own work
- Solving a problem they've personally experienced
- Potential for outsized financial return
- Respect and recognition in founder community

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| Feature creep: keeps adding features, never ships | 9/10 | Weekly |
| Context switching: founder = CEO + CTO + designer + marketer | 9/10 | Daily |
| No product-market fit signal: building in the dark | 8/10 | Weekly |
| Time dilution: too many directions, too little focus | 8/10 | Daily |
| Isolation: no team, no accountability partner | 7/10 | Daily |
| Financial stress: running out of runway | 8/10 | Weekly |
| Skill gaps: needs to learn everything simultaneously | 7/10 | Daily |

#### Daily Needs
- Morning: Review yesterday's metrics, today's top 3 builder tasks
- Daytime: Deep work blocks (coding/design), customer interviews, user research
- Evening: Log progress, update roadmap, reflect on what worked
- Night: Capture ideas, plan tomorrow

#### Weekly Needs
- Product metrics review (users, revenue, retention)
- Roadmap progress vs. plan
- Customer feedback synthesis
- Networking: 1-2 founder conversations
- Content: 1 social post about building

#### Monthly Needs
- Revenue and burn rate review
- Fundraising pipeline (if applicable)
- Product roadmap recalibration
- Skill gap assessment and learning plan
- Team/hiring needs assessment

#### Success Metrics
| Metric | Target |
|---|---|
| MVP shipped | Within 3 months |
| Active users | 100 by month 6 |
| MRR | ₹30,000 by month 12 |
| Task completion rate | >70% (focused on builder tasks) |
| Deep work hours | >4 hours/day |
| Customer interviews | >3/week |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| MVP task breakdown | Weekly | A01 Planner breaks features into tasks |
| Roadmap adjustment | Bi-weekly | A08 suggests timeline adjustments |
| Customer feedback log | Daily | Quick capture → A03 categorizes |
| Revenue/expense tracking | Weekly | Income + expense tracking |
| Competitor monitoring | Weekly | A06 scans for competitive moves |
| Pitch deck prep | Monthly | A05 drafts pitch sections |

---

### 3.3 Freelancer

| Field | Detail |
|---|---|
| **Foundation** | Rahul Verma (B.Com, self-taught dev, ₹25-40K/mo) |
| **Population** | 15% of users |
| **Primary Device** | Laptop (Lenovo Legion) + dual monitor, Android |
| **Technical Level** | Intermediate-Advanced (React, Node.js, MongoDB) |
| **Income Level** | ₹25,000-80,000/month (variable) |
| **Willingness to Pay** | ₹200-500/month |

#### Goals
| Goal Type | Goal | Timeline |
|---|---|---|
| Career | Full-time frontend role at product company | 6 months |
| Portfolio | 5 production-grade projects | 12 months |
| Income | ₹80,000/month consistent | 18 months |
| Skills | Full-stack (backend + cloud) | 9 months |
| Stability | Replace unpredictable freelance with stable income | 12 months |

#### Motivations
- Prove capability despite non-CS background
- Escape feast-famine freelance cycle
- Build a portfolio that removes resume gaps
- Gain respect in developer community
- Achieve location independence

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| No CS degree = resume gaps to compensate | 8/10 | Weekly |
| Unpredictable freelance income | 9/10 | Monthly |
| Juggling 3-4 projects + study + TA role | 8/10 | Daily |
| Harder networking without college infrastructure | 7/10 | Weekly |
| Unsure which skills to prioritize | 6/10 | Weekly |
| Client scope creep (free work) | 8/10 | Per project |
| Invoicing and payment tracking | 6/10 | Monthly |

#### Daily Needs
- Morning: Client task priorities vs. personal study
- Daytime: Deep work on client projects, study during gaps
- Evening: Log hours, invoice tracking, portfolio work
- Night: Plan next day, skill practice (LeetCode/project)

#### Weekly Needs
- Client project status update
- Study progress (full-stack goal)
- Income logged and categorized
- Portfolio project work
- Opportunity check (job listings)

#### Monthly Needs
- Income vs. expenses report
- Effective hourly rate per client
- Skill progression assessment
- Portfolio project milestone check
- Client satisfaction review

#### Success Metrics
| Metric | Target |
|---|---|
| Monthly income | ₹60,000+ |
| Effective hourly rate | ₹800+/hour |
| Client satisfaction | 4.5/5+ |
| Portfolio projects shipped | 1 per 2 months |
| Study consistency | 10+ hours/week |
| Job applications | 4+ per month |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| Client project task breakdown | Weekly | A01 breaks client specs into tasks |
| Income + hours logging | Daily | Auto-timer → manual categorization |
| Invoice tracking | Per client | A07 flags unpaid invoices |
| Portfolio project planning | Bi-weekly | A08 creates project roadmap |
| Skill gap analysis | Monthly | A03 identifies missing skills for target roles |
| Job opportunity scan | Weekly | A06 matches openings to skills |

---

### 3.4 Creator

| Field | Detail |
|---|---|
| **Foundation** | New (not in existing personas — synthesized from market research) |
| **Population** | 10% of users |
| **Primary Device** | MacBook + iPhone + iPad, sometimes tablet for sketching |
| **Technical Level** | Low-Medium (can use tools, doesn't code) |
| **Income Level** | ₹0-200,000/month (high variance) |
| **Willingness to Pay** | ₹500-2,000/month |

#### Goals
| Goal Type | Goal | Timeline |
|---|---|---|
| Audience | Reach 10K followers/subscribers | 12 months |
| Content | Publish 4x/week consistently | Ongoing |
| Revenue | Monetize through 3+ income streams | 12 months |
| Skills | Improve craft (editing, writing, design) | Ongoing |
| Systems | Build content pipeline (no more daily scramble) | 3 months |

#### Motivations
- Creative expression and impact
- Community building around shared interests
- Income independence through owned audience
- Recognition for craft
- Flexibility in schedule and location

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| Content calendar chaos: last-minute scrambling | 9/10 | Weekly |
| Platform dependency: algorithm changes destroy reach | 8/10 | Quarterly |
| Inconsistent schedule: burns out, disappears, returns | 8/10 | Monthly |
| Idea management: good ideas lost, bad ideas executed | 7/10 | Weekly |
| Analytics overwhelm: too many metrics, no actionable insight | 7/10 | Weekly |
| Sponsor/brand management: tracking deals, payments | 6/10 | Monthly |
| Tool sprawl: 8+ tools for content, analytics, finance, scheduling | 8/10 | Daily |

#### Daily Needs
- Morning: Check analytics (yesterday's performance), plan today's content
- Daytime: Create content (write, record, edit), engage with audience
- Evening: Schedule posts, log ideas, review tomorrow
- Night: Review engagement, capture inspiration

#### Weekly Needs
- Content calendar review (published vs. planned)
- Platform analytics deep-dive
- Sponsor/brand deal tracking
- Income from each revenue stream
- Audience growth metrics

#### Monthly Needs
- Revenue report (per platform, per stream)
- Content performance analysis (best/worst performing)
- Audience growth breakdown
- Brand deal pipeline review
- Skill/craft improvement plan

#### Success Metrics
| Metric | Target |
|---|---|
| Publishing consistency | 4x/week |
| Follower growth | 10% month-over-month |
| Engagement rate | >5% |
| Revenue growth | 20% month-over-month |
| Content backlog | 2 weeks of scheduled content |
| Tool count | <5 (consolidated in ARIA) |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| Content ideation | Weekly | A03 suggests topics from trends + past performance |
| Content calendar planning | Weekly | A07 recommends best posting times |
| Content creation focus | Daily | Timer + deep work mode |
| Analytics review | Daily + Weekly | A07 highlights anomalies |
| Audience engagement | Daily | None (human-only) |
| Sponsor pipeline | Monthly | A05 drafts sponsorship pitches |
| Income tracking | Weekly | Auto-categorization by revenue stream |

---

### 3.5 Knowledge Worker

| Field | Detail |
|---|---|
| **Foundation** | Ananya Gupta (Infosys, 0-2yr, BTech CSE NIT Trichy) |
| **Population** | 15% of users |
| **Primary Device** | Work laptop (Windows) + personal iPad, iPhone |
| **Technical Level** | Medium (corporate tools, learning internal systems) |
| **Income Level** | ₹35,000-60,000/month |
| **Willingness to Pay** | ₹100-300/month |

#### Goals
| Goal Type | Goal | Timeline |
|---|---|---|
| Career | Switch to product company (higher growth) | 12 months |
| Skills | Prepare for interviews (DSA, system design) | Ongoing |
| Credential | GATE or GRE (undecided) | 18 months |
| Health | Manage workplace stress, avoid burnout | Ongoing |
| Learning | Master current tech stack + emerging tech | 6 months |
| Social | Maintain connections despite WFH isolation | Ongoing |

#### Motivations
- Escape corporate bureaucracy for product innovation
- Keep skills relevant while doing enterprise work
- Have a backup plan (higher studies) if laid off
- Maintain work-life boundaries (burnout is real)
- Feel in control of career direction

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| Training is slow and bureaucratic | 7/10 | Daily |
| Studies after work but no structure | 8/10 | Weekly |
| Misses college's structured semester system | 6/10 | Monthly |
| Social isolation in new city (WFH) | 7/10 | Weekly |
| GATE vs. GRE indecision | 6/10 | Monthly |
| Corporate red tape slows everything | 7/10 | Daily |
| LeetCode guilt: should do it, rarely does | 8/10 | Weekly |

#### Daily Needs
- Morning: Work tasks (corporate) + personal study plan
- Daytime: Execute work tasks, log learnings, attend meetings
- Evening: 1-2 hours of focused interview prep
- Night: Wind down, log sleep, not think about work

#### Weekly Needs
- Interview prep progress (problems solved)
- Skill development review
- Learning resource curation
- Social activities / networking
- Work-life balance check

#### Monthly Needs
- Interview readiness self-assessment
- Learning plan vs. actual
- Resume/LinkedIn update
- GATE/GRE decision checkpoint
- Networking: 2-3 meaningful conversations

#### Success Metrics
| Metric | Target |
|---|---|
| LeetCode problems/week | 5+ |
| Study hours/week | 10+ |
| Networking conversations/month | 4+ |
| Work-life balance (self-rated) | 7/10+ |
| Sleep consistency | 7+ hours average |
| Resume/LinkedIn updated | Monthly |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| Work task management | Daily | A01 prioritizes corporate tasks |
| Interview practice | Daily | A03 generates practice problems |
| Learning path tracking | Weekly | A08 creates study roadmap |
| Networking reminders | Weekly | A04 reminds to reach out |
| Career decision analysis | Monthly | A05 compares GATE vs. GRE with data |
| Skill tracking | Weekly | A03 updates skill levels |

---

### 3.6 Power User

| Field | Detail |
|---|---|
| **Foundation** | Derived from behavioral segmentation (15% of users — daily 15+ min) |
| **Population** | 15% of users |
| **Primary Device** | Desktop (custom build/Mac Studio) + mechanical keyboard, multiple displays |
| **Technical Level** | Expert (codes, uses CLI, automates everything, API comfortable) |
| **Income Level** | ₹50,000-200,000+/month |
| **Willingness to Pay** | ₹1,000-3,000/month |

#### Goals
| Goal Type | Goal | Timeline |
|---|---|---|
| Efficiency | Reduce every repetitive action to one keystroke | Ongoing |
| Automation | Automate 80% of recurring tasks | 3 months |
| Integration | Connect ARIA to personal API ecosystem | 6 months |
| Data | Full context across all systems | Ongoing |
| Mastery | Know every feature, shortcut, and configuration | Ongoing |

#### Motivations
- Optimization is its own reward
- Dislike of repetitive manual work
- Customizing tools to match mental model exactly
- Being the "most productive version" of themselves
- Technical curiosity and system-building enjoyment

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| Lack of keyboard shortcuts for advanced operations | 9/10 | Daily |
| Cannot customize workflows enough | 8/10 | Weekly |
| Batch operations missing (select all, bulk edit) | 8/10 | Weekly |
| No API access for custom integrations | 9/10 | Monthly |
| Slow navigation (too many clicks for power actions) | 7/10 | Daily |
| Tutorial mode / beginner UX cannot be disabled | 6/10 | Weekly |
| Cannot script or extend the system | 8/10 | Monthly |

#### Daily Needs
- Morning: Custom dashboard (not the default), quick system scan
- Daytime: Deep work with minimal interruption, keyboard-only flow
- Evening: Batch process captured items, run automations
- Night: Review dashboards, fine-tune settings

#### Weekly Needs
- Automation health check (what's running, what failed)
- System performance review (latency, cache, sync)
- Custom workflow optimization
- Integration status review
- Data export/backup verification

#### Monthly Needs
- API usage review (if using integrations)
- Custom script/automation maintenance
- Module reconfiguration (hide unused, reorganize)
- Shortcut customization review
- Feature discovery (what's new that they can use)

#### Success Metrics
| Metric | Target |
|---|---|
| Actions per minute | >5 (keyboard-first) |
| Mouse-to-keyboard ratio | <20% mouse use |
| Automations running | 5+ active |
| Daily task capture | <3 seconds per capture |
| System uptime | >99% |
| Custom configurations | >10 active |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| Keyboard-only navigation | All times | R+letter, Cmd+K, custom shortcuts |
| Batch operations | Daily | Multi-select → bulk action |
| Automation management | Weekly | A07 reports automation health |
| Custom workflow building | Monthly | No AI (builder mode) |
| System monitoring | Daily | A07 flags anomalies |
| API/integration work | Monthly | Developer documentation |

---

### 3.7 New User

| Field | Detail |
|---|---|
| **Foundation** | Aggregated from all persona onboarding patterns + trial bounce segment (10%) |
| **Population** | Transient (100% of users start here, 85% convert) |
| **Primary Device** | Whatever device they signed up on (mobile 60%, desktop 40%) |
| **Technical Level** | Variable (Low to High) |
| **Income Level** | Variable |
| **Willingness to Pay** | Unknown (needs to see value first) |

#### Goals
| Goal Type | Goal | Timeline |
|---|---|---|
| Assessment | "Is this worth my time?" | First 30 seconds |
| Value | Create something useful | First 60 seconds |
| Understanding | "How does this work for ME?" | First session |
| Commitment | Should I enter my real data? | First day |
| Habit | Will I remember to come back? | First week |

#### Motivations
- Curiosity about a new tool
- Existing pain point they hope to solve
- Recommendation from peer/community
- Frustration with current tools
- Fresh start motivation (semester start, new year)

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| Blank slate paralysis: no data, no value | 9/10 | First session |
| Long onboarding: "setup" before "use" | 8/10 | First session |
| Not knowing what's possible | 7/10 | First week |
| Fear of data entry investment | 7/10 | First day |
| Too many choices before first action | 8/10 | First session |
| No clear "what to do now" | 7/10 | First week |

#### Daily Needs
- First session: Create real content fast, see immediate value
- Day 1-3: Explore relevant modules, understand the core loop
- Week 1: Establish capture habit, see daily briefing value
- Month 1: Expand to 3-5 active modules

#### Success Metrics
| Metric | Target | Measurement |
|---|---|---|
| Onboarding completion | >85% | Completed 5 steps |
| First task created | <60 seconds from signup | Timer from signup to first task save |
| Day 1 return rate | >60% | Logged in next day |
| Day 7 retention | >40% | Active in 7 days |
| Day 30 retention | >25% | Active in 30 days |
| Modules activated | >3 by day 30 | First data entry in 3+ modules |
| NPS (day 7) | >8/10 | First-week satisfaction prompt |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| Onboarding wizard | Once | A00 walks through setup |
| First task capture | First session | A01 auto-classifies and prioritizes |
| Dashboard discovery | First days | A09 generates first briefing |
| Module exploration | First weeks | Progressive feature reveal |
| Value moment: first briefing | Day 1-2 | "Your morning briefing is ready" |

---

### 3.8 Returning User

| Field | Detail |
|---|---|
| **Foundation** | Crammer archetype (35%) + Weekly Check-in (25%) — from behavioral segmentation |
| **Population** | 60% of sessions are return visits after 24h+ absence |
| **Primary Device** | Mobile (60%) — checking on the go |
| **Technical Level** | Variable |
| **Income Level** | Variable |

#### Motivations
- Guilt about overdue items (need clean slate)
- Crisis mode (exam, deadline, interview)
- Curiosity about new opportunities
- Habit (morning briefing consumer)
- Avoidance of more guilt (paradoxically)

#### Frustrations
| Frustration | Severity | Frequency |
|---|---|---|
| Overdue avalanche: returns to 47 overdue tasks | 9/10 | Every return |
| Context loss: forgets where they left off | 8/10 | Every return |
| Guilt-inducing UI: "You missed 14 days" | 8/10 | Every return |
| Catching up takes too long | 7/10 | Every return |
| Nothing changed: same view as when they left | 6/10 | Weekly |

#### Daily Needs
- First session back: Quick catch-up on what matters
- Guilt-free reset: Forgive/reschedule overdue items
- Context restoration: "Where was I?"
- Critical alerts: What needs immediate attention
- Path forward: Clear next action

#### Weekly Needs
- Consistency support: Rebuild streak
- Forgiveness mechanism: "Start fresh" without losing data
- Digest: What they missed (not a firehose)
- Course opportunity: Recommit to one course

#### Success Metrics
| Metric | Target |
|---|---|
| Time to catch-up | <30 seconds |
| Overdue forgiveness rate | >50% use "Forgive all" |
| Module re-activation | >1 module re-engaged |
| Return-to-daily conversion | >30% returners become daily users |
| Abandonment rate | <10% after catch-up |

#### Core Workflows
| Workflow | Frequency | AI Involvement |
|---|---|---|
| Catch-up digest | Every return | A00 generates "Here's what changed" |
| Overdue forgiveness | Every return | One-click "Reschedule all" or "Forgive all" |
| Context restoration | Every return | "You were working on X project" |
| Critical alerts | Every return | P0 items highlighted |
| Recommitment | Weekly | "Want to restart this course?" |

---

## 4. User Archetypes

These represent **behavioral patterns** that cut across user types. A Student Builder can be a Crammer. A Freelancer can be a Planner. These archetypes determine **how** users interact, while user types determine **what** they do.

### 4.1 The Planner (15% of users)

**Behavior:** Opens app to organize, not to do. Spends 20 min/day organizing. Has color-coded labels and filtered views. Low task completion rate relative to time spent organizing.

**Risk:** Tool hoarding — collecting features they don't use instead of completing work.

**Design Response:**
- Limit active tasks to prevent organization-as-procrastination
- Quick capture that doesn't disrupt flow
- AI suggests next action without requiring manual triage
- "Ship mode" that hides configuration during execution blocks

### 4.2 The Crammer (35% of users)

**Behavior:** Ignores app for 1-2 weeks. Opens during exam/crisis mode. Binge-captures 50 tasks in one session. Expects app to have magically organized everything during absence.

**Risk:** App abandonment after guilt from seeing overdue accumulation.

**Design Response:**
- Auto-reschedule missed tasks and deadlines
- Briefing acknowledges absence without guilt
- "Here's what you missed — here's what's critical"
- Bulk operations (complete all, reschedule all, forgive all)
- Reset modal: "Start fresh" keeps data but clears overdue flags

### 4.3 The Hobbyist (30% of users)

**Behavior:** Uses 3-4 modules regularly (tasks, habits, maybe courses). Ignores income tracking, opportunities, time tracking. Customizes the app to niche interests. Builds elaborate habit tracking systems.

**Risk:** Feature bloat — adding modules they don't need and feeling overwhelmed.

**Design Response:**
- Module visibility control (hide unused modules, show only active ones)
- Habit streak and gamification features
- Quick capture with minimal friction
- Lightweight version of each module (no advanced features by default)
- "I'll add this later" path for unused modules

### 4.4 The Careerist (20% of users)

**Behavior:** Focused on placements, internships, career growth. Heavy user of opportunity radar, income tracking. Less interested in habit/sleep tracking. Wants the app to feel like a career accelerator, not a life organizer.

**Risk:** Churn if opportunity matching doesn't produce results within 2 weeks.

**Design Response:**
- Aggressive opportunity matching (daily scan, instant notification)
- Resume/interview preparation workflow
- Skill gap analysis linked to target roles
- Income growth tracking and projection
- Career dashboard as default landing page option
- Quick win: must show a high-match opportunity in first 3 days

### 4.5 The Builder (10% of users)

**Behavior:** Project-centric. Uses the system to manage builds — courses feed projects, projects feed portfolio, ideas become MVPs. Less interested in life tracking (sleep, habits).

**Risk:** Abandons if task management feels like overhead, not acceleration.

**Design Response:**
- Project-first navigation option (tasks grouped by project, not by date)
- "Learn → Build → Ship" as primary workflow
- Quick linking between courses, projects, and portfolio
- GitHub integration for commit-level accountability
- "Ship mode" focus timer

### 4.6 The Optimizer (5% of users)

**Behavior:** Analyzes everything. Spends as much time in Analytics as in any other module. Tweaks habits based on data. Uses weekly review as their primary planning ritual.

**Risk:** Analysis paralysis — optimizing instead of doing.

**Design Response:**
- Cross-metric correlation suggestions ("When you sleep more, you code more")
- Automated trend detection (no manual analysis needed)
- Custom dashboard builder
- Data export for external analysis
- "Actionable insight" format (not just charts — what to DO)

---

## 5. User Type Comparison Matrix

| Dimension | Student Builder | Startup Founder | Freelancer | Creator | Knowledge Worker | Power User | New User | Returning User |
|---|---|---|---|---|---|---|---|---|
| **Population** | 40% | 10% | 15% | 10% | 15% | 5% | Transient | 60% of sessions |
| **Primary Device** | Laptop + Phone | MacBook + iPhone | Laptop + dual monitor | MacBook + iPad | Work laptop + iPad | Desktop + mech keyboard | Phone (60%) | Phone (60%) |
| **Tech Level** | Intermediate | High | Intermediate-Adv | Low-Med | Medium | Expert | Variable | Variable |
| **WTP (₹/mo)** | 0-200 | 500-1500 | 200-500 | 500-2000 | 100-300 | 1000-3000 | 0 | 0-200 |
| **Key Module** | Tasks, Courses, Opps | Roadmap, Projects, Income | Projects, Income, Opps | Analytics, Ideas, Tasks | Courses, Goals, Sleep | All + Automation | Onboarding, Dashboard | Dashboard, Tasks, Opps |
| **AI Expectation** | Plan my day | Break down MVP | Find me work | Suggest content | Schedule study | Automate everything | Guide me | Catch me up |
| **Session Length** | 3-8 min | 15-30 min | 10-20 min | 10-20 min | 5-15 min | 30-60 min | 2-5 min | 1-3 min |
| **Session Frequency** | 3-5x/day | 5-10x/day | 3-5x/day | 3-5x/day | 2-3x/day | 10+ x/day | 1-3x (first week) | 1-2x/week |
| **Offline Need** | High (campus WiFi) | Medium | High (travel) | Medium | Medium | Low | Low | Medium |
| **Primary Emotion** | Overwhelmed | Determined | Anxious | Inspired | Stressed | In control | Curious | Guilty |

---

## 6. Onboarding Journey

### Trigger
User clicks "Sign up" or "Get started" from landing page, referral link, or app store listing.

### Entry Point
`/login` page — Google OAuth button or email/password form.

### User State
Curious but skeptical. Has tried 3+ productivity tools that didn't stick. Low attention span — evaluating within first 30 seconds.

### Pre-Journey Context
Arrived from: search result (40%), friend referral (25%), YouTube review (20%), ad (10%), app store browse (5%).

### Flow
```
[Land on /login] → [Google OAuth: 2 clicks] → [Supabase creates user]
    → [Step 1: Name + Timezone — 10s]
    → [Step 2: Pick 3 goals from templates — 20s]
    → [Step 3: First capture — "What do you need to do?" — 15s]
    → [AI auto-classifies task with priority + due date]
    → {User sees their task on dashboard}
    → [Step 4: Morning briefing toggle — 5s]
    → [Step 5: Browser extension prompt — 5s] (SKIPPABLE)
    → [Redirect to /dashboard]
    ==>[Background: Create default categories, tags, habit templates]
    ==>[Background: Generate first morning briefing for tomorrow]
    ==>[Background: Initial opportunity scan (if profile complete enough)]
```

### Action Table

| Step | Action | Duration | Cognitive Load | AI Assistance | System Assistance | Friction Risk |
|---|---|---|---|---|---|---|
| 1 | Click Google OAuth | 5s | 1/10 | None | Supabase auth, create user row | 2 — OAuth failure |
| 2 | Enter display name, select timezone | 10s | 2/10 | None | IP geo-detect timezone, show suggestions | 1 — trivial |
| 3 | Select 3 goals from 8 templates | 20s | 4/10 | None | Show goal templates grouped by user type | 3 — choice paralysis |
| 4 | Type first task in natural language | 15s | 3/10 | A01: parse, classify, prioritize, set due date | Save task, show on dashboard | 2 — easy |
| 5 | Toggle briefing on/off | 5s | 1/10 | A09: schedule first briefing | Save preference | 1 — trivial |
| 6 | Install browser extension (optional) | 15s | 2/10 | None | Open extension store page | 3 — skippable, may bounce |

### Decision Tree

| Decision Point | Options | Contextual Signal | Optimal Path | Consequence |
|---|---|---|---|---|
| Goal selection: overwhelmed? | Select 1 / Select 3 / Skip | User hesitates >10s | "Pick just one for now" | Fewer goals = less overwhelm, but less personalization |
| First task: nothing to add? | Type something / Skip | User types nothing | Show prompt examples | Shorter onboarding but no initial task on dashboard |
| Extension: install now? | Yes / Later | Mobile user → hide option | Skip on mobile, prompt on desktop | Extension = 2x more content saved per user |

### AI Intervention Points

| Step | AI Action | Trigger |
|---|---|---|
| 2 | Suggest timezone from IP | Timezone field appears |
| 3 | Recommend goal templates based on detected role | User profile inferred from email domain (.edu = student, etc.) |
| 4 | Classify natural language task (priority, due date, category) | User finishes typing first task |
| 4 | If user types nothing: "Try 'Finish DBMS assignment'" | Empty input after 5s |
| 5 | Briefing sample: "Tomorrow at 7 AM you'll get your first briefing" | Toggle enabled |

### AI Recommendation Points

| Point | Recommendation | Trigger |
|---|---|---|
| After step 3 | "Based on your goals, here are 3 courses to start" | Goal selection completed |
| After step 4 | "You can also capture tasks by typing 'R+T'" | First task created |
| After onboarding | "Want a tour of your dashboard?" | Redirect to dashboard |

### AI Automation Opportunities

| Opportunity | Automation | Trigger |
|---|---|---|
| Create default habit templates | 3-5 habits based on goals (e.g., "Study 30min") | Goals selected |
| Schedule first weekly review | Set for Sunday 8 PM | Onboarding complete |
| Initial opportunity scan | Scan based on goals + timezone | Onboarding complete |
| Generate first briefing | Schedule 7 AM tomorrow | Briefing toggled on |

### Success State
User sees their first task on a non-empty dashboard. They feel "This actually understood what I meant." Total time: <60 seconds. User is curious about what happens tomorrow at 7 AM.

### Failure State
OAuth fails → retry button. Step times out → saved progress, resume on return. Dashboard empty → "Let's add your first task" CTA. User closes browser during step 3 → resume at step 3 on next login.

### Exit State
User closes app or navigates to another module. Ideally: returns tomorrow morning for briefing.

### Friction Points

| Step | Friction | Severity | Affected Segment | Mitigation |
|---|---|---|---|---|
| 2 | Timezone auto-detection wrong | 2 | Travelers, VPN users | "Not your timezone?" link |
| 3 | Too many goal choices (8) | 3 | New User, Hobbyist | "No idea — surprise me" button picks 3 |
| 4 | "I don't know what to type" | 4 | New User, Creator | Show examples: "Finish DBMS assignment", "Review pull request" |
| 6 | Extension prompts on mobile | 3 | Mobile users | Auto-hidden on mobile, show in Settings later |

### Cognitive Load Heatmap

| Step | Load | Contributor | Reduction Strategy |
|---|---|---|---|
| 3 | 4/10 | Decision fatigue from choice | Default selections + "Surprise me" option |
| 4 | 3/10 | Composing natural language | Examples + AI shows it understands |
| Overall | 2.5/10 avg | — | — |

### Drop-Off Risk

| Step | Risk | Indicator | Prevention |
|---|---|---|---|
| 1 — OAuth | Medium | User closes auth popup | Email+password fallback |
| 3 — Goals | Medium | User inactive >30s on goal picker | "Pick one to start" simplification |
| 6 — Extension | Medium | Mobile users see desktop-only prompt | Platform detection |
| Post-onboarding | High | User sees empty dashboard | Pre-seeded data from onboarding |

### Optimization Opportunity

**Single highest-impact change:** After step 4 (first task), immediately show the task on a dashboard that has 3 other pre-seeded elements (today's suggested tasks from goals, a habit template, and the morning briefing indicator). A non-empty dashboard is the #1 predictor of Day 2 return.

### Accessibility Considerations
- All onboarding steps keyboard-navigable (Tab, Enter, Escape)
- Screen reader: each step announces title + instruction + available actions
- Color: no information conveyed through color alone (goal icons + labels)
- Time-based: no auto-advance, user controls pace
- Motion: reduce transitions for prefers-reduced-motion
- Touch targets: 44px minimum on all buttons

---

## 7. First Day Journey

### Trigger
User completes onboarding and lands on dashboard for the first time. OR user returns after onboarding break.

### Entry Point
`/dashboard` — first-ever dashboard view.

### User State
Curious, slightly lost. 40% of users will explore on their own. 60% need guidance.

### Pre-Journey Context
Just completed 5-step onboarding. Has 1 task, 3 goals, basic profile. No task completion history.

### Flow
```
[Dashboard loads for first time]
    → [Z1: "Welcome! Here's your day at a glance"]
    → [User scans: Z2 KPI strip (mostly zeros), Z3 today's focus (1 task), Z8 activity (empty)]
    → {Decision: Explore or Close?}
        |-- Explore → [User clicks Tasks in sidebar]
        |       → [Sees their first task in list view]
        |       → {Decision: Complete it or add more?}
        |           |-- Complete → [Checkbox → task done → confetti → "+1 task completed" metric updates]
        |           |-- Add more → [Click + → type "Do laundry" → AI classifies → saved]
        |-- Close → [User closes app]
        |       → [Returns tomorrow for briefing (40% probability)]
```

### Action Table

| Step | Action | Duration | Cognitive Load | AI Assistance | System Assistance | Friction Risk |
|---|---|---|---|---|---|---|
| 1 | Scan dashboard | 15s | 3/10 | None | Show contextual greeting | 2 — clean layout |
| 2 | Click task | 5s | 1/10 | None | Navigate to task | 1 — CTA is clear |
| 3 | Complete task OR add another | 10s | 2/10 | AI classifies new task | Real-time metric update | 2 — simple |
| 4 | Explore another module | 30s-2min | 4/10 | A09 suggests next module | Show module grid | 3 — choice overload |

### Decision Tree

| Decision Point | Options | Contextual Signal | Optimal Path | Consequence |
|---|---|---|---|---|
| Explore or close? | Click module / Close app | Time of day, user energy | Click Tasks (familiar = task) | Task = completion loop, habit = retention |
| Complete task or add more? | Checkbox / + button | Number of existing tasks | Complete first (feel accomplished) | Completion = dopamine, adding = overload |
| Try another module? | Courses / Goals / Habits / Close | User's selected goals | Click Courses (if student) | More data = better personalization |

### AI Intervention Points

| Point | AI Action | Trigger |
|---|---|---|
| Dashboard load | "Welcome! Start by completing your first task" | First dashboard visit |
| Task page load | "This is your task list. Tap the checkbox to complete one." | First task list visit |
| 5 min idle | "Need ideas? Here's what other students track:" | User inactive >5 min on any page |
| First task completed | "+1 done! You're off to a great start." | Task completion event |

### AI Recommendation Points

| Point | Recommendation | Trigger |
|---|---|---|
| After first task completion | "Want to set a study habit?" | First task done |
| After first course view | "Try linking this course to your goal" | Course module first visit |
| End of day | "You'll get your first briefing tomorrow at 7 AM" | Day 1 evening (user's 9 PM) |

### AI Automation Opportunities

| Opportunity | Automation | Trigger |
|---|---|---|
| Suggest studying times from goals | Block 2 hours tomorrow based on goal time preferences | First day end |
| Create evening wind-down reminder | Set 9:30 PM sleep reminder | First day end |

### Success State
User completes at least 1 task and adds at least 1 item (task, course, or habit). User feels "This could actually work for me." Task completion rate >1 task = 70% Day 2 retention.

### Failure State
User completes nothing. Dashboard remains empty. User closes and never returns (30% of first-day users).

### Exit State
Closes app. May or may not return. AI hopes they return for morning briefing.

### Friction Points

| Step | Friction | Severity | Mitigation |
|---|---|---|---|
| 1 | Dashboard empty zones | 4/5 | Show "Start tracking" CTAs instead of blank spaces |
| 2 | Unclear what to do first | 3/5 | "Complete your first task" hero CTA |
| 3 | Too many modules to explore | 3/5 | Highlight CORE modules only on day 1 |

### Cognitive Load Heatmap

| Step | Load | Contributor | Reduction Strategy |
|---|---|---|---|
| Dashboard scan | 3/10 | New layout | 8 zones but clean structure |
| Module exploration | 4/10 | 20 unknown modules | Show only 3 highlighted modules day 1 |
| Overall | 3/10 | — | — |

### Drop-Off Risk

| Step | Risk | Indicator | Prevention |
|---|---|---|---|
| Dashboard — no task | High | User created 0 tasks in onboarding | Force task creation in step 4 |
| Module exploration | Medium | User opens 5+ modules in first session | Limit suggested modules to 3 |
| End of session | High | User closes after <60s | Briefing promise = reason to return |

### Optimization Opportunity

**Single highest-impact change:** End first day session with a specific, compelling reason to return tomorrow. "Your first morning briefing is scheduled for 7 AM — you'll see today's tasks, weather, and 1 opportunity match." This creates an expectation that drives Day 2 return.

---

## 8. First Week Journey

### Trigger
User returns for Day 2-7 after onboarding.

### Entry Point
Push notification: "Your morning briefing is ready" (7 AM). OR user opens app manually.

### User State
Varies by day: Day 2 = curious, Day 3-4 = building habit, Day 5-7 = either hooked or dropping.

### Pre-Journey Context
Day 1 established 1 task completed. Briefings established morning habit. User has 3-10 tasks across 1-3 modules.

### Flow
```
DAY 2:
[Push notification → "Your briefing is ready"]
    → [Dashboard shows Z1 greeting with yesterday's completion]
    → [User sees Z3: today's top 3 tasks + Z2: 1-2 metrics]
    → {Decision: Engage or Dismiss?}
        |-- Engage → [Scan briefing → Complete 1 task → Check habits → Close (avg 3 min)]
        |-- Dismiss → [Swipe notification → Continue day → Open app later (50%) / Never (50%)]

DAY 3-4:
[User opens app mid-day (not morning)]
    → [Dashboard shows mid-day state with progress so far]
    → {User starts exploring secondary modules}
    → [Clicks Courses → Adds a course → AI generates study plan]
    → [Clicks Ideas → Captures an idea → "Create project from this?"]

DAY 5-7:
[Either habit formed (daily morning check) or drop-off]
    → [Hooked user: Opens briefing, completes 2-3 tasks, logs 1 habit, checks 1 opportunity]
    → [Dropping user: Opens on Sunday for weekly review (if reminded), or doesn't open at all]
```

### Action Table

| Day | Key Action | Duration | Cognitive Load | AI Assistance | Success Indicator |
|---|---|---|---|---|---|
| 2 | First briefing review | 2-3 min | 3/10 | A09 generates personalized briefing | Opens briefing, completes 1 task |
| 3 | Add first course | 1-2 min | 4/10 | A03 suggests courses based on goals | Course added, study plan generated |
| 4 | Capture first idea | 30s | 2/10 | None (but AI can classify) | Idea captured |
| 4-5 | Log first habit | 10s | 1/10 | A14 nudges if not logged | Habit logged at least once |
| 5 | First opportunity scan | 1-2 min | 3/10 | A06 shows initial matches | User views at least 1 opportunity |
| 7 | First weekly review | 3-5 min | 5/10 | A10 generates review report | User opens + reads review |

### Decision Tree

| Day | Decision Point | Options | Optimal Path |
|---|---|---|---|
| 2 | Morning briefing: read or dismiss? | Read / Dismiss | Read (3 min of value) |
| 3 | Add real course or explore? | Add / Browse / Skip | Add 1 real course (personalization) |
| 5 | First opportunity: apply or save? | Apply / Save / Ignore | Save (actionable without commitment) |
| 7 | Weekly review: read or archive? | Read / Archive / Read later | Read (insight drives week 2 engagement) |

### AI Intervention Points

| Day | AI Action | Trigger |
|---|---|---|
| 2 | "You completed 1 task yesterday. Let's make it 3 today." | Briefing generation |
| 3 | "Based on your goal 'Learn Full-Stack', try starting with Web Dev Bootcamp" | Course module first visit |
| 4 | "Your first idea! Want to check if this already exists?" | First idea capture |
| 5 | "I found 2 opportunities matching your profile. Check them out?" | Radar scan complete |
| 7 | "Your weekly review is ready. You completed 7/12 tasks (58%)" | Review generation |

### AI Recommendation Points

| Day | Recommendation | Trigger |
|---|---|---|
| 2 | "Set a study habit for 30 min daily" | Briefing viewed |
| 3 | "Try linking a course to your FAANG goal" | Course added |
| 4 | "Move this idea to a project?" | Idea captured |
| 5 | "Set income tracking for your freelance work" | Opportunity viewed |
| 6 | "Log your sleep to see how it affects productivity" | End of week approaching |

### AI Automation Opportunities

| Opportunity | Automation | Trigger |
|---|---|---|
| Auto-generate study tasks from course | Create daily study tasks | Course enrolled |
| Schedule weekly review | Set Sunday 8 PM | Day 7 of onboarding |
| Create default habits from goals | "Study 30min", "Exercise", "Read" | Goals set in onboarding |

### Success State
By Day 7, user has: completed 5+ tasks, added 1+ course, logged 1+ habit, viewed 1+ opportunity, read 1 weekly review. User feels "This is becoming part of my routine."

### Failure State
User stops opening after Day 2 or 3. No morning briefing habit. No real data entered. User feels "It's just another todo list."

### Exit State
End of week 1: morning habit formed (40%), abandoned (30%), weekly check-in (30%).

### Friction Points

| Day | Friction | Severity | Mitigation |
|---|---|---|---|
| 3 | Course discovery: "Where do I start?" | 4 | AI suggests courses from goals |
| 5 | Opportunity scan: no matches yet | 4 | "Let's improve your profile for better matches" |
| 7 | Weekly review feels long | 3 | "Here's your week in 30 seconds" summary first |

### Cognitive Load Heatmap

| Day | Avg Load | Peak Load | Peak Step |
|---|---|---|---|
| 2 | 2/10 | 3/10 | Briefing review |
| 3 | 3/10 | 4/10 | Adding course |
| 7 | 4/10 | 5/10 | Weekly review |

### Drop-Off Risk

| Day | Risk | Primary Cause |
|---|---|---|
| 2 | Medium | Notification not compelling enough |
| 3 | Medium-High | "This is just a task list, not a system" |
| 5 | Medium | Opportunity radar returns nothing |
| 7 | Medium | Weekly review: boring or guilt-inducing |

### Optimization Opportunity

**Single highest-impact change:** Day 3-4 is the critical drop-off window. The fastest path to retention is getting the user to enter **real, meaningful data** (their actual course, their actual project, their actual income). Prompt with: "What course are you actually taking right now?" instead of "Try our course tracker."

---

## 9. First Month Journey

### Trigger
User survived week 1. Now at Day 8-30. Either a daily user or weekly check-in.

### Entry Point
Morning briefing (daily users) or push notification (weekly users).

### User State
Daily users: "This is my system now." Weekly users: "I should check this more." At-risk: "Why is everything overdue?"

### Pre-Journey Context
Week 1 established: task habit, 1 course, 1 habit logged, briefing consumed. 20-50 tasks, 3-5 modules active.

### Flow
```
WEEK 2 (Days 8-14): Expanding
[Daily briefing habit continues]
    → [Starts using Time Tracker for study sessions]
    → [Adds 2-3 more courses from current workload]
    → [Logs first sleep entry]
    → [First habit streak milestone (7 days)]
    → [Notification: "7-day study streak! Keep it going."]

WEEK 3 (Days 15-21): Deepening
[Discovers cross-module linking]
    → [Links task to goal → goal progress updates automatically]
    → [Creates first project from an idea]
    → [Configures opportunity radar preferences]
    → [First AI chat: "ARIA, what should I focus on today?"]

WEEK 4 (Days 22-30): Commit or Plateau
[Daily user: fully integrated]
    → [Uses 6+ modules regularly]
    → [Weekly review shows meaningful progress]
    → [Income tracking started, opportunity pipeline active]
    → [Customizes dashboard, sidebar, settings]
[Weekly user: opening 1-2x/week]
    → [Catch-up digest shows what changed]
    → [Uses batch operations / forgiveness]
[At-risk: opened 0-2x in 2 weeks]
    → [Re-engagement: "I've organized your backlog"]
    → [Push: "3 new opportunities matched for you"]
```

### Decision Tree

| Week | Decision Point | Options | Optimal Path |
|---|---|---|---|
| 2 | Track time or skip? | Start timer / Manual / Skip | Start timer |
| 3 | Link task to goal or not? | Link / No thanks | Link (cross-module value) |
| 4 | Chat with ARIA or browse? | Ask ARIA / Browse | Ask ARIA (discovers AI value) |

### AI Intervention Points

| Week | AI Action | Trigger |
|---|---|---|
| 2 | "You studied 2h yesterday — that's consistent!" | 3+ study sessions |
| 2 | "7-day habit streak! Streaks predict long-term success." | Streak milestone |
| 3 | "4 tasks aren't linked to any goal. Link them?" | Unlinked tasks detected |
| 4 | "1 month! Here's what changed." | Day 30 milestone |

### Success State
6+ active modules, 60%+ task completion, >7 day habit streak, AI chat used at least once.

### Failure State
Still only 1-2 modules, <30% completion, never touched AI chat.

### Optimization Opportunity

**Single highest-impact change:** Month 1 hinges on the **Cross-Module Value Moment** — the first time a task links to a goal and the goal progress bar moves. Accelerate this: on first task completion, prompt: "Link this to your 'FAANG Goal'?" Show the progress bar update.

---

## 10. Daily Workflow Journey

### Trigger
6:00 AM alarm. OR 7:00 AM briefing notification. OR user opens app manually.

### Entry Point
Morning: Push notification → Dashboard. Mid-day: Direct app open. Evening: Notification reminder. Night: Sleep log.

### User State
Morning: Low energy, needs guidance. Mid-day: High energy, needs execution. Evening: Moderate, needs reflection. Night: Low energy, needs wind-down.

### Flow

#### Morning (6:00 AM — 9:00 AM)
```
[Push notification: "Your briefing is ready" — 7:00 AM]
    → [Dashboard loads with Morning state]
    → [Z1: "Good morning! 4 tasks today. 1 overdue."]
    → [Z3: Today's top 3 focus tasks]
    → {Read / Quick check / Dismiss}
```

#### Mid-Day (9:00 AM — 6:00 PM)
```
[Complete task → checkbox]
    → [See next task in queue]
    → {Continue / Capture new / Switch context}
```

#### Evening (6:00 PM — 9:00 PM)
```
[Dashboard loads with Evening state]
    → [Z1: "You completed 5/8 tasks (63%)"]
    → [Z8: Recent activity]
    → {Log more or Wind down?}
```

#### Night (9:00 PM — 6:00 AM)
```
[Push notification: "Time to wind down"]
    → [Sleep log: one tap]
    → [Tomorrow preview: "Top task: Submit DBMS assignment"]
    → ["Good night."]
```

### Action Table

| Period | Action | Duration | Cognitive Load | AI Assistance |
|---|---|---|---|---|
| Morning | Review briefing | 30s-2min | 2/10 | A09 generates briefing |
| Mid-day | Complete task | 2s | 1/10 | None |
| Mid-day | Quick capture | 10s | 2/10 | A01 classifies |
| Evening | Review completions | 30s | 2/10 | Summary shown |
| Evening | Plan tomorrow | 1-2 min | 3/10 | A01 suggests tasks |
| Night | Log sleep | 5s | 1/10 | A13 reminder |

### AI Intervention Points

| Period | AI Action | Trigger |
|---|---|---|
| Morning | "Your sleep was 5h. I've reduced deep work tasks." | Sleep score <6h |
| Mid-day | "90 min focus session done — take a break?" | Timer >90 min |
| Evening | "You studied 45 min — 15 min short. Quick session?" | Target not met |
| Night | "Log sleep? Tomorrow's top task is important." | 9:30 PM |

### Optimization Opportunity

**Single highest-impact change:** The **evening review → morning planning pipeline**. If user spends 2 min in evening setting tomorrow's priority, morning briefing becomes 2x more useful. Evening prompt: "What's the ONE thing you want to finish tomorrow?"

### Accessibility (Daily Workflow)
- Briefing: min 14px, line height 1.5
- Timer: visible alert at 25 min, vibration option
- Sleep log: large button, defaults to current time ±15 min
- All actions reachable by keyboard shortcuts
- Screen reader: announces task count + top priority first

---

## 11. Weekly Review Journey

### Trigger
Sunday 8:00 PM. Push notification or calendar reminder. Or user manually opens /weekly-review.

### Entry Point
`/weekly-review` page. First visit: guided. Subsequent visits: summary-first.

### User State
Reflective, mildly anxious (looking at what they didn't do). Sunday evening energy level: moderate-low.

### Pre-Journey Context
AI has been collecting: task completions, habit logs, sleep data, time entries, income, opportunities viewed, courses progressed. Everything is summarized into a single report.

### Flow
```
[Push: "Your weekly review is ready" — 8:00 PM Sunday]
    → [Open page → Z1: "Week X — You completed 18/25 tasks (72%)"]
    → [See overall progress bars: Tasks, Courses, Habits, Sleep]
    → [Scroll down: task completion view]
        → [Completed 12 planned + 6 unplanned]
        → [Missed: 7 tasks]
        → {Forgive / Reschedule / Complete now}
    → [Scroll: Habit streak summary]
        → ["Study: 6/7 days. Exercise: 3/7 days."]
        → {Keep / Adjust targets}
    → [Scroll: Sleep quality correlation]
        → ["Weeks with >7h sleep: 82% task completion"]
    → [Scroll: Income if tracked]
        → ["Earned ₹X this week from Y projects"]
    → [Scroll: AI insights]
        → ["Your best focus day was Tuesday"]
        → ["You tend to skip tasks after 4 PM"]
    → [Next: Set goals for next week]
        → ["Continue what worked, adjust what didn't"]
    → {Archive / Share / Export as PDF}
```

### Action Table

| Step | Action | Duration | Cognitive Load | AI Assistance |
|---|---|---|---|---|
| 1 | Open review (notification) | 5s | 1/10 | A10 generates report |
| 2 | Scan overall metrics | 30s | 2/10 | Highlights key changes |
| 3 | Review task completions | 1-2 min | 3/10 | Groups by status, suggests forgiveness |
| 4 | Review habits | 30s | 2/10 | Shows streaks, recommends adjustments |
| 5 | Review sleep correlation | 30s | 3/10 | Finds patterns in sleep vs productivity |
| 6 | Read AI insights | 1 min | 2/10 | A10 generates 3-5 actionable insights |
| 7 | Set next week's goal | 30s | 3/10 | Suggests based on trends |
| 8 | Archive or act | 10s | 1/10 | Generates follow-up tasks |

### AI Intervention Points

| Point | AI Action | Trigger |
|---|---|---|
| Report generation | "72% completion — your best week yet!" | Completion rate > 70% |
| Forgiving suggestions | "3 tasks were auto-forgiven (no longer relevant)" | Stale tasks > 7 days overdue |
| Sleep insight | "Your deep work hours drop 40% after 4 PM" | Consistent pattern detected |
| Next week goal | "Goal: Maintain study habit, improve sleep consistency" | Trends show stable patterns |

### Success State
User feels informed, not guilty. Takes 1-2 actions based on insights ("I'll start studying at 2 PM"). Closes review with "Next week will be better."

### Failure State
User feels guilty about missed tasks. Skips insights. Closes feeling overwhelmed.

### Optimization
**Single highest-impact change:** Start with the **best** thing (longest streak, best day) before showing missed tasks. Never show failures without a concrete "how to fix it."

---

## 12. Sleep & Wind-Down Journey

### Trigger
9:30 PM. Push notification: "Time to wind down." Or user manually triggers /sleep.

### Entry Point
Sleep page or modal. One-tap log.

### User State
Evening fatigue. Low cognitive capacity. Looking for quick, guided wind-down.

### Flow
```
[Push notification: "ARIA suggests winding down" — 9:30 PM]
    → [Notification expands: "Log sleep → Get tomorrow's preview"]
    → [Tap → Opens sleep page]
    → [One-tap log: "Sleep now" / "In 30 min" / Custom]
    → [After logging: Tomorrow preview card]
        → ["Top 3 tasks for tomorrow"]
        → ["Weather: 22°C, sunny"]
        → ["Opportunities queued: 1"]
    → [Optional: Wind-down content]
        → {"Play 5-min meditation" / "Read a reflection" / "Just log"}
    → [Log saved → "Good night, <name>"]
```

### Morning Follow-Up (Wake)
```
[Sleep log completes when user opens app in morning]
    → [System calculates: Hours slept, debt, score]
    → [Briefing adjusts: sleep score = smarter recommendations]
    → [If <6h: "I'll prioritize only 2 tasks today"]
```

### Action Table

| Step | Action | Duration | Cognitive Load | AI Assistance |
|---|---|---|---|---|
| 1 | Tap notification | 2s | 1/10 | A13 generates message |
| 2 | Log sleep (1 tap) | 3s | 1/10 | Default time suggested |
| 3 | View tomorrow preview | 15s | 2/10 | A09 generates preview |
| 4 | Wind-down content (optional) | 2-5 min | 1/10 | Personalized content |
| 5 | Morning follow-up | 10s | 2/10 | A13 analyzes sleep |

### Optimization
**Single highest-impact change:** The wind-down notification should NOT feel like "another task." Frame it as: "The rest of your OS is shutting down. You should too." — a permission slip to rest, not a to-do.

---

## 13. Cross-Session Journeys

### 13.1 Dashboard → Any Module

User lands on dashboard, sees a KPI or task, clicks through to that module.

| Entry | Action | Destination | Time to Value |
|---|---|---|---|
| KPI "5 tasks due today" | Click count | Tasks page (filtered: today) | <2s |
| Task "Submit assignment" | Click row | Task detail modal | <1s |
| Course "Progress 60%" | Click bar | Course detail page | <2s |
| Habit "3-day streak" | Click | Habit log page | <1s |
| "New opportunity" badge | Click badge | Opportunity radar | <2s |

### 13.2 ARIA Chat → Any Module

User asks ARIA a question → ARIA responds with data + link.

| User Query | ARIA Response | Auto-Navigate To |
|---|---|---|
| "What's due today?" | "4 tasks: Submit DBMS (urgent), Review PR..." | Task: filtered + sorted |
| "How did I sleep?" | "6h. Score: 68. Try sleeping earlier." | Sleep page |
| "Show me my income" | "₹X this month. Details:" | Income page (filtered: month) |

### 13.3 Notification → Module

| Notification | Tap → | Module Context |
|---|---|---|
| "Briefing ready" | Dashboard | Morning state |
| "Weekly review ready" | Weekly Review | Current week |
| "Task due in 30 min" | Task | The specific task |
| "Opportunity found" | Opportunity Radar | Matches sorted |
| "Habit reminder" | Habit Log | Current habit |

### 13.4 Cross-Module Linking

| Link | Source → Destination | System Action |
|---|---|---|
| Task linked to goal | Task page → Goal progress updates | Recalculate goal progress |
| Idea → Project | Idea pipeline → Project creation | Create project, link idea |
| Course → Tasks | Course page → Generate study tasks | A01 creates 5 study tasks |
| Income → Opportunity | Income page → "You could earn X more" | A06 prioritizes matching |
| Time entry → Task | Timer stop → Task completion | Auto-log time on task |

---

## 14. Module-Specific Journey Maps

### 14.1 Tasks

```
[Tasks page loaded]
    → [View: Kanban / List / Calendar]
    → [Filter: Today / This week / All / Overdue]
    → {Select task → Mark complete}
    → {Select task → Edit details}
    → {Click + → Type in NL → AI classifies}
    → {Drag to reorder priority}
```

### 14.2 Courses

```
[Courses page loaded]
    → [Add course: Name, URL, deadline]
    → [AI generates weekly study plan]
    → [Study tasks auto-created]
    → [Progress tracked via task completion]
    → [Deadline approaching: "Your ML course deadline is in 3 days"]
```

### 14.3 Habits

```
[Habits page loaded]
    → [View: Calendar / Grid / List]
    → [Log: One tap per habit]
    → [Streak counter updates]
    → [Nudge: "Haven't logged exercise in 3 days"]
```

### 14.4 Sleep

```
[Sleep log triggered (9:30 PM)]
    → [One-tap log: In bed / Lights out]
    → [Morning: Auto-compute sleep duration]
    → [Score: 0-100 based on duration + consistency]
    → [Debt tracking: cumulative deficit]
```

### 14.5 Income

```
[Income page loaded]
    → [Add entry: Amount, source, date]
    → [Hourly rate auto-calculated]
    → [Monthly summary + trends]
    → [Opportunity: "You could earn 40% more by taking X-type projects"]
```

### 14.6 Ideas

```
[Ideas page loaded]
    → [Pipeline: Raw → Validating → Building → Launched]
    → [Drag card to move stages]
    → [Click card → Create project from this?]
    → [AI enrichment: "Similar ideas exist in these projects"]
```

### 14.7 Opportunities

```
[Opportunities page loaded]
    → [AI has pre-scanned and matched]
    → [Job / Freelance / Internship / Project]
    → [Match score: 0-100%]
    → [Save → Track application status]
    → [LinkedIn import: Parse profile → better matches]
```

### 14.8 Time Tracking

```
[Time page loaded]
    → [Pomodoro timer: 25:00 countdown]
    → [Manual entry: What, when, duration]
    → {Deep work mode: "Focus for 90 min"}
    → [Daily deep work total]
    → [Weekly comparison: "You did 4h deep work vs 6h goal"]
```

---

## 27. Exit & Retention Journeys

### 27.1 Session End

Every session ends one of three ways:

| Exit Type | % of Sessions | User State | System Action |
|---|---|---|---|
| Intentional close | 60% | "Done for now" | Save state, set next trigger |
| Background timeout | 25% | Got distracted | Save state, no notification |
| Close from frustration | 15% | "This isn't helpful" | Trigger re-engagement sequence |

Close from frustration indicators:
- User is on same page >5 min without interaction
- Rapid clicks (3+ in 2 seconds) — trying to find something
- Opening and closing same page 3+ times — confused
- Immediate close after error toast — annoyed

### 27.2 Re-Engagement Sequences

| User State | Day | Sequence Action | Channel |
|---|---|---|---|
| New, day 1 | 2 (no-show) | "Your briefing is ready for tomorrow" | Push notification |
| New, week 1 drop | Day 8 | "Your first weekly summary is ready" | Push notification |
| Active → Inactive | 3 days | "Your backlog has grown to X items" | Push notification |
| Active → Inactive | 7 days | "I've auto-organized 5 tasks for you" | Email + push |
| Active → Inactive | 14 days | "3 new opportunities matched for you" | Email |
| Active → Inactive | 30 days | "Since you left — new features: X, Y, Z" | Email |

### 27.3 Churn Prevention Rules

| Trigger | Action | Priority | 
|---|---|---|
| 0 tasks created in 3 days | Push: "What's one thing you need to do?" | High |
| 3+ tasks overdue > 7 days | Push: "Forgive and move on? I'll clean up." | High |
| Habit streak broken | Push: "Streaks reset. Ready to restart?" | Medium |
| No briefing opened in 5 days | Email: "Here's what you missed" | Medium |
| Error on save (network) | Push: "Saved as draft. Retry when connected." | Low |

### 27.4 Resurrection Flow

```
[User returns after 14+ days]
    → [Dashboard: "Welcome back! Here's what changed"]
    → [AI shows: Cleaned up backlog, new opportunities, feature updates]
    → [Offers: "Reset everything / Pick up where I left off"]
    → [If data was cleaned: explain what was archived]
    → [Last state: try to restore as much context as possible]
```

---

## 28. Journey Technical Architecture

### 28.1 State Transition Engine

Every journey flows through states. Transitions are event-driven.

```
States: IDLE → ACTIVE → ENGAGED → EXITING → IDLE
Transitions:
  IDLE → ACTIVE: App open / notification tap
  ACTIVE → ENGAGED: User interaction > 2 actions
  ENGAGED → EXITING: Back navigation / close
  EXITING → IDLE: Session saved
```

### 28.2 Event Bus (Journey Events)

```
journey/user/onboarded
journey/user/first-task-complete
journey/user/morning-briefing-read
journey/user/weekly-review-read
journey/user/module-visit   { module: "tasks|courses|habits|..." }
journey/user/task-complete  { task_id, count, module }
journey/user/habit-logged   { habit_id, habit_name, streak }
journey/user/session-start  { type: "push|manual|cron" }
journey/user/session-end    { duration, tasks_completed }
journey/user/churn-risk     { risk_level: "low|medium|high" }
```

### 28.3 Decision Engine Flow

```
[Event arrives]
    → [Load user state + context]
    → [Evaluate against decision tree for current journey step]
    → [Check AI intervention triggers]
    → {Path A: Action (optimal) → Execute}
    → {Path B: Alternative → Execute + log}
    → {Path C: Exit → Save state}
```

### 28.4 Data Flow Per Journey

```
Journey Step → [Metric: duration, load, friction]
    → Log to analytics table
    → Update AI context (next briefing will adapt)
    → If drop-off risk: trigger intervention immediately
```

### 28.5 Intervention Pipeline

```
[Drop-off detected at step]
    → [Check cached user preferences: notification opt-in]
    → [Choose channel: Push / In-app / Email]
    → [Generate message: AI-personalized]
    → [Deliver]
    → [Track: opened? acted on?]
    → [If no response in 24h: escalate channel or message]
```

### 28.6 Threshold-Based Interventions

| Metric | Threshold | Intervention | Escalation |
|---|---|---|---|
| Session time | <10s on page | None (brief glance) | — |
| Session time | 10-60s no click | In-app nudge: "Need help?" | If 2nd occurrence: check frustration |
| Session time | >5 min idle | Save draft state, dim UI | Background save |
| Task completion | 0 in 3 days | Push: "One task to restart" | Day 7: email digest |
| Module visits | 3+ quick module switches | Modal: "Which one matters most?" | — |
| Error rate | 2+ errors in session | In-app: "Something's wrong. Retry?" | Log + notify devs |

---

## 15. Learning Journey

### Trigger
User enrolls in a course (manually or via AI suggestion). OR deadline approaching for an existing course.

### Entry Point
`/courses` page. First visit: guided course setup. Subsequent visits: progress dashboard.

### User State
Motivated but scattered. Enrolled in 3-6 courses, actively pursuing 1-2. 60% of enrolled courses will never be completed without structure.

### Flow
```
[Enroll in course → Name, URL, deadline, weekly hours goal]
    → [AI generates weekly study plan: 5 tasks per week]
    → [Study tasks appear in daily task list]
    → [User completes study sessions → progress tracked]
    → [Deadline approach: notification at 7/3/1 day]
    → [Course completion: archive or create project from it]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Enrollment | Generate 5 weekly study tasks, schedule recurring blocks | A01 Planner |
| Mid-course | Adjust pace if falling behind, suggest focus areas | A03 Learning |
| Completion | Archive, suggest next course, trigger "build project" prompt | A03 Learning |

### Success State
Course completed (100% progress). Study plan followed. User feels "I actually finished a course for once."

---

## 16. Knowledge Journey

### Trigger
User captures content (link, note, file) they want to remember or reference later.

### Entry Point
`/resources` page OR inline capture via browser extension (Cmd+D / Ctrl+D).

### User State
Curious, collecting. Usually browsing (Twitter, YouTube, blogs, documentation) and finds something worth saving.

### Flow
```
[Browser: highlight text → Cmd+D → save to ARIA]
    → [AI auto-tags: topic, relevance, suggested action]
    → [Saved to Resources library]
    → [AI enriches: summary, key takeaways, related items]
    → [Returns in context: related searches, briefing mentions, weekly review]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Capture | Auto-categorize, extract summary, suggest tags | A03 Learning |
| Context | Surface related resources when user visits relevant module | A00 ARIA |
| Review | Include in weekly review: "You saved 12 resources this week" | A10 Review |

### Success State
User saves content and finds it later exactly when needed. "I remember reading something about this..."

---

## 17. Opportunity Journey

### Trigger
A06 Opportunity Radar completes daily scan and finds a new match. OR user manually checks `/opportunities`.

### Entry Point
Push notification: "New opportunity matched for you" → `/opportunities`. Or manual browse.

### User State
Passive job seeker — not actively applying but wants to know what's out there. Motivated by FOMO on good opportunities.

### Flow
```
[Daily scan runs (6 AM)]
    → [Matches scored: 0-100% based on skills, goals, preferences]
    → [Top 3 matches surfaced in morning briefing]
    → [User views match → sees match breakdown by skill fit]
    → {Apply / Save / Dismiss}
    → [If Apply: track application status, add follow-up tasks]
    → [If Save: revisit on weekly review, nudge if untouched >7 days]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Matching | Score opportunities against user profile, skills, goals | A06 Radar |
| Briefing | Surface top 1-2 matches in daily briefing | A09 Briefing |
| Tracking | Update application status, suggest next steps | A05 Career |

### Success State
User finds and applies to at least 1 high-quality opportunity per month. Match score >80% feels like "this was made for me."

---

## 18. Project Journey

### Trigger
User creates a project from an idea, course completion, or manual creation.

### Entry Point
`/projects` page. Create from: Idea pipeline → "Create project", Course → "Build something with this", or manual.

### User State
Builder mindset. Has a concrete outcome in mind. Needs structure to ship before motivation fades.

### Flow
```
[Create project: name, description, timeline]
    → [AI breaks into phases: Planning → Building → Testing → Launch]
    → [Phase tasks auto-generated in task list]
    → [GitHub integration: link repo, commits tracked]
    → [Blocker detected: no activity >3 days → AI asks "Stuck?"]
    → [Launch: archive project, add to portfolio]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Creation | Generate phase plan, auto-create milestones | A08 Roadmap |
| Execution | Detect blockers, suggest unblock strategies | A01 Planner |
| Launch | Archive, update portfolio, suggest reflection prompt | A00 ARIA |

### Success State
Project ships to completion. User has a portfolio item, a GitHub link, and a sense of accomplishment.

---

## 19. Goal Journey

### Trigger
User sets a goal during onboarding, or manually creates one in `/goals`.

### Entry Point
`/goals` page. Goals are categorized: Career, Skills, Financial, Health, Projects, Learning.

### User State
Ambitious but vague. Goals tend to be aspirational ("learn full-stack") without concrete milestones.

### Flow
```
[Set goal: category, target, timeline]
    → [AI generates milestones: 3-5 checkpoints]
    → [AI links to relevant courses, tasks, habits]
    → [Linked items auto-update goal progress]
    → [Weekly review: goal progress snapshot]
    → [Goal complete: celebration + suggest next goal]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Creation | Suggest milestones, auto-link to existing data | A08 Roadmap |
| Tracking | Update progress from linked task completions | A03 Learning |
| Review | Surface goal progress in weekly review | A10 Review |

### Success State
Goals have measurable progress, linked to real activity. User tracks toward 3-5 goals simultaneously.

---

## 20. Roadmap Journey

### Trigger
User creates a roadmap (for a course, project, or career goal). Or AI suggests building one.

### Entry Point
`/roadmap` page (integrated into Goals, Courses, or Projects modules).

### User State
Strategic. Needs a plan to execute against. Current state: "I know where I want to be, but not how to get there."

### Flow
```
[Create roadmap: target outcome, current state, timeline]
    → [AI suggests phases/milestones based on outcome type]
    → [User adjusts: add/remove/reorder milestones]
    → [Tasks auto-generated for each milestone]
    → [Progress bar updates as tasks complete]
    → [Roadmap review: milestone reached / behind schedule]
    → [AI suggests adjustments if off track]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Creation | Generate milestone structure from outcome description | A08 Roadmap |
| Execution | Auto-generate tasks per milestone, set deadlines | A01 Planner |
| Adjustment | Suggest timeline adjustments when off-track | A08 Roadmap |

### Success State
Roadmap provides clarity. User knows exactly what to do next. "I can see the path from where I am to where I want to be."

---

## 21. Analytics Journey

### Trigger
User opens `/analytics` or weekly review shows a metric worth exploring. Or user taps a KPI on dashboard.

### Entry Point
`/analytics` page. Entry via: Dashboard KPI tap, Weekly Review deep-link, Sidebar navigation.

### User State
Reflective. Wants to understand patterns and improve. Risk: analysis paralysis.

### Flow
```
[Analytics dashboard loads: 4 metric groups]
    → [Tasks: completion rate, trends, overdue distribution]
    → [Time: deep work hours, pomodoro count, most productive time]
    → [Habits: streaks, consistency %, best/worst habits]
    → [Sleep: average duration, score trend, debt]
    → [AI insight: "Your task completion drops 30% on days with <6h sleep"]
    → {Explore / Take action / Return later}
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Correlation | Find cross-metric patterns (sleep × productivity) | A07 Analytics |
| Insight | Generate 1-3 actionable insights per view | A07 Analytics |
| Action | "Would you like to create a habit from this insight?" | A00 ARIA |

### Success State
User finds 1 actionable insight per session. "I should study before 4 PM — my focus drops after that."

---

## 22. AI Journey

### Trigger
User asks ARIA a question via chat (Cmd+K or chat panel). Or ARIA proactively offers assistance.

### Entry Point
Chat panel (bottom-right), Cmd+K command palette, or inline AI suggestion.

### User State
Curious, stuck, or exploring. Wants quick answers without manual navigation.

### Flow
```
[User types question: "What should I focus on today?"]
    → [ARIA loads context: tasks, sleep, calendar, goals]
    → [ARIA classifies intent: planning / info / action / reflection]
    → [Synthesizes response with data + reasoning]
    → [Provides suggested actions + deep links]
    → {Act / Refine / Ignore}
```

### AI Capabilities
| Intent | Example | AI Action |
|---|---|---|
| Planning | "What's my week looking like?" | Summarize tasks, suggest priorities |
| Info | "How did I sleep this week?" | Fetch + interpret sleep data |
| Action | "Create a study plan for DBMS" | Generate tasks, set schedule |
| Reflection | "Am I making progress?" | Compare goals vs actual, generate insight |

### Success State
User gets a useful response without navigating. "ARIA just told me my most productive time is 10 AM-12 PM."

---

## 23. Search Journey

### Trigger
User needs to find something: task, resource, idea, course, past conversation.

### Entry Point
Search bar (top of sidebar or Cmd+K). Or contextual search within a module.

### User State
Frustrated or in a hurry. "I know I saved this somewhere..." Searching is a failure mode of organization.

### Flow
```
[User types query in search bar]
    → [Results: ranked by relevance + recency + module]
    → [Filters: module, date range, status, tags]
    → [User clicks result → navigates to exact context]
    → [If not found: AI suggests "Try searching for..." or "Would you like to create this?"]
```

### AI Involvement
| Point | Action | Agent |
|---|---|---|
| Query | Expand query with synonyms, correct typos | A00 ARIA |
| Ranking | Boost recent/relevant results based on user context | A00 ARIA |
| Fallback | If no results: offer to create the item | A00 ARIA |

### Success State
User finds what they need in <5 seconds. Search feels like "it knows what I mean."

---

## 24. Mobile Journey

### Trigger
User opens app on phone. Push notification tap. Quick capture intent.

### Entry Point
App icon tap, notification tap, or share sheet (iOS/Android).

### User State
On-the-go, distracted, short attention span. Session length: 30s-3min. Primary use: capture, check, quick actions.

### Platform Constraints
- Screen: 6.1" average, touch input
- Network: Unreliable (campus WiFi, subway, travel)
- Notifications: High competition (10+ apps)
- Input: Thumb-typing, voice dictation potential

### Core Actions (Mobile-First)

| Action | Implementation | Duration |
|---|---|---|
| Quick capture | Widget or share sheet → type/speak → AI classifies | <10s |
| Briefing review | Notification → dashboard → top 3 items → close | <30s |
| Task complete | Tap task → checkbox → done | <2s |
| Habit log | Widget → one tap per habit | <5s |
| Sleep log | Notification → one-tap "Sleep now" | <3s |
| View opportunities | Notification → scroll top 3 → save/dismiss | <30s |

### Mobile-Specific Design Rules
- Bottom navigation: 5 tabs max (Dashboard, Tasks, +, Modules, Profile)
- Thumb zone: all actions within 44px reach of thumb
- Offline-first: all writes cached locally, sync on reconnect
- Widgets: 3 widget sizes for quick capture, briefing, habits
- Share sheet: "Save to ARIA" from any app
- Voice input: "Hey ARIA" for hands-free capture

### AI Optimization for Mobile
| Trigger | AI Action |
|---|---|
| Briefing notification | Generate mobile-optimized briefing (3 items, not 8) |
| Quick capture | Auto-classify with minimal fields (just title) |
| Dismiss mode | "You checked 3 items. Want to set tomorrow's priority?" |

---

## 25. Tablet Journey

### Trigger
User opens app on iPad/tablet. Often in study or browsing context.

### Entry Point
App icon tap (home screen or dock). Usually at desk or couch.

### User State
Lean-back mode. Longer sessions (5-15 min). Comfortable browsing, reviewing, learning.

### Platform Strengths
- Screen: 10-13", touch + keyboard (Magic Keyboard)
- Multi-tasking: Split View, Slide Over
- Context: Often used alongside laptop or textbook
- Pencil input: sketching, handwriting notes

### Core Actions (Tablet-Optimized)

| Action | Implementation | Duration |
|---|---|---|
| Course review | Side-by-side: course content + task list | 5-10 min |
| Weekly review | Full detail view with charts | 3-5 min |
| Content capture | Split view: browser + ARIA resources | <30s |
| Analytics browse | Dashboard with full charts | 2-5 min |
| Long-form planning | Roadmap editing with Pencil | 5-15 min |

### Tablet-Specific Design Rules
- Landscape-first layout with multi-column views
- Split View support: ARIA on left, course content on right
- Pencil support: mark up roadmaps, handwrite notes → AI transcribes
- Hover states (iPadOS Pointer) for desktop-like precision
- Drag-and-drop: drag content from browser → ARIA

---

## 26. Desktop Journey

### Trigger
User sits down at workstation. Intent: deep work, heavy creation, or system configuration.

### Entry Point
Browser tab (usually pinned). Cmd+Tab to switch. Often one of 5-10 open tabs.

### User State
High focus. Multiple monitors. Keyboard-driven. Session length: 15-60 min.

### Platform Strengths
- Screen: 24-32", multiple monitors possible
- Input: Full keyboard + mouse/trackpad
- Network: Stable (Ethernet/WiFi)
- Context: Primary work machine

### Core Actions (Desktop-Power)

| Action | Implementation | Duration |
|---|---|---|
| Deep work session | Full-screen timer + ambient mode | 25-90 min |
| Roadmap creation | Drag-drop timeline, milestone editing | 10-20 min |
| Analytics deep-dive | Full charts, date range filtering, export | 5-15 min |
| System configuration | Settings, custom views, shortcuts | 5-30 min |
| Batch operations | Multi-select, bulk edit/complete/delete | 1-5 min |
| Automation setup | Custom workflow builder | 10-30 min |

### Desktop-Specific Design Rules
- Keyboard shortcuts: EVERY action has a shortcut (R+t = new task)
- Cmd+K: Universal command palette (not just search)
- Multi-select: Shift+click, Cmd+click, Select All
- Drag and drop: Reorder tasks, move between modules
- Sidebar: Full 7-group navigation, collapsible sections
- Infinite scroll: Not pagination — fast virtual scrolling
- Split panes: Roadmap + task list + goal progress simultaneously
- Export: CSV, PDF, Markdown from every data view

### Power User Features (Desktop-Only)
| Feature | Implementation |
|---|---|
| Custom CSS | User stylesheet injection |
| API access | REST API key management |
| CLI integration | Terminal-based capture: `aria task "Fix login bug"` |
| Keyboard rebinding | Remap any action to any key combination |
| Automation rules | "If task from X project is completed, move to Y column" |
| Multi-profile | Separate student/freelancer contexts |

---

## 29. Cross-Cutting AI Intervention Points Map

Consolidated view of every AI intervention across all journeys, organized by trigger type.

### Event-Triggered Interventions

| Trigger | Journey | AI Action | Agent |
|---|---|---|---|
| Enrollment | Learning | Generate weekly study plan | A01 |
| Task completed | First Day | "+1 done! Great start." | A00 |
| First task capture | Onboarding | Auto-classify priority, due date, category | A01 |
| Course viewed first time | First Week | "Link this to your goal?" | A03 |
| Idea captured | First Week | "Want to create a project?" | A03 |
| Opportunity scan complete | Opportunity | Show match score + breakdown | A06 |
| Project stagnant >3 days | Project | "Stuck? Need help?" | A01 |
| Search returns 0 results | Search | "Try... or create this?" | A00 |
| Sleep logged | Sleep | Adjust next day's task load | A13 |
| Goal created | Goal | Generate milestones + auto-link | A08 |
| Roadmap created | Roadmap | Break into phases + auto-tasks | A08 |

### Threshold-Triggered Interventions

| Threshold | Journey | AI Action | Agent |
|---|---|---|---|
| Sleep <6h | Daily | Reduce deep work tasks | A13 |
| Study streak = 7 days | Learning | "Week streak! Consistent!" | A03 |
| Tasks overdue >7 days | Exit | Auto-forgive or reschedule | A01 |
| No task created in 3 days | Exit | "Quick task to restart?" | A00 |
| 3+ quick module switches | Daily | "Which one matters most?" | A00 |
| Timer >90 min | Daily | "Take a break?" | A01 |
| 9:30 PM | Sleep | "Time to wind down" | A13 |
| Week 4 milestone | First Month | "One month! Here's what changed." | A00 |

### Cron-Triggered Interventions

| Cron | Journey | AI Action | Agent |
|---|---|---|---|
| 6 AM daily | Daily | Run opportunity radar scan | A06 |
| 7 AM daily | Daily | Generate morning briefing | A09 |
| 9:30 PM daily | Sleep | Wind-down notification | A13 |
| Midnight daily | Daily | Habit miss check | A12 |
| Sunday 8 PM | Weekly | Generate weekly review | A10 |
| Every 15 min | Daily | Missed task reminder check | A11 |

---

## 30. Cross-Cutting Friction Points Map

Consolidated view of every friction point across all journeys, ranked by severity.

### Critical Friction Points (Severity 4-5)

| Journey | Step | Friction | Severity | Mitigation |
|---|---|---|---|---|
| Onboarding | 3 — Goals | 8 choices, choice paralysis | 5 | "Surprise me" button picks 3 |
| Onboarding | First task blank | "I don't know what to type" | 4 | Show examples: "Finish DBMS assignment" |
| First Day | Dashboard empty | 8 zones with no data | 4 | Show "Start tracking" CTAs in empty zones |
| First Day | Unclear first action | "What do I do now?" | 4 | "Complete your first task" hero CTA |
| First Week | Course discovery | "Where do I start?" | 4 | AI suggests courses from goals |
| First Week | Opportunity empty | "No matches yet" | 4 | "Improve your profile for better matches" |
| Weekly Review | Guilt from missed | 25 missed tasks shown first | 4 | Start with best week/streak first |
| Return User | Overdue avalanche | Returns to 47 overdue tasks | 5 | Auto-forgive, "Start fresh" option |
| Return User | Context loss | Forgets where left off | 4 | "You were working on X" restoration |
| Mobile | Small input area | Typing on phone is slow | 4 | Voice input, smart defaults |

### Moderate Friction Points (Severity 2-3)

| Journey | Friction | Severity | Mitigation |
|---|---|---|---|
| Onboarding | Extension prompt on mobile | 3 | Auto-hide on mobile |
| Onboarding | OAuth failure (2% of users) | 2 | Email+password fallback |
| First Month | Time tracking — forgot to start | 3 | Manual entry mode as fallback |
| Sleep | Notification feels like task | 3 | "Rest of OS shutting down" framing |
| Weekly Review | Review feels long (3-5 min) | 3 | "Your week in 30 seconds" summary |
| Offline | No connection on save | 3 | Local cache, silent sync, conflict UI |

### Anti-Pattern Frictions (What to AVOID)

| Anti-Pattern | Why It's Bad | Alternative |
|---|---|---|
| "You missed 14 days" banner | Activates guilt, causes churn | "Welcome back! Here's what's new." |
| Empty state with no CTA | User doesn't know next action | Every empty state has 1 clear action |
| AI action without explanation | "Why did it do that?" confusion | Every AI action has "Why" tooltip |
| Modal overload | Blocks user from actual work | Slide-over panels, inline suggestions |
| Configuration before action | "Set up before you can use" | Progressive reveal: use first, configure later |

---

## 31. Cross-Cutting Cognitive Load Map

Consolidated analysis of cognitive load across all journey steps.

### Average Load Per Journey

| Journey | Avg Load | Peak Load | Peak Step | Overall Rating |
|---|---|---|---|---|
| Onboarding | 2.5/10 | 4/10 | Goal selection | Low |
| First Day | 3/10 | 4/10 | Module exploration | Low-Med |
| First Week | 3/10 | 5/10 | Weekly review | Med |
| First Month | 3/10 | 4/10 | Cross-module linking | Low-Med |
| Daily Workflow | 2/10 | 3/10 | Evening planning | Low |
| Weekly Review | 2.5/10 | 3/10 | Task review + forgiveness | Low-Med |
| Sleep | 1/10 | 2/10 | Morning follow-up | Very Low |
| Learning | 3/10 | 4/10 | Course enrollment | Low-Med |
| Project | 3/10 | 5/10 | Phase planning | Med |
| Goal | 2/10 | 3/10 | Milestone creation | Low |
| Roadmap | 4/10 | 6/10 | Initial creation | Med-High |
| Analytics | 3/10 | 5/10 | Understanding correlations | Med |

### Load Reduction Strategies

| High-Load Step | Raw Load | Strategy | Reduced Load |
|---|---|---|---|
| Roadmap creation | 6/10 | AI pre-fills 80% from description | 3/10 |
| Weekly review (first time) | 5/10 | Summary-first: 30s overview | 3/10 |
| Goal milestone planning | 4/10 | AI generates, user adjusts | 2/10 |
| Module exploration | 4/10 | Highlight top 3, hide rest | 2/10 |
| Analytics correlation | 5/10 | "Insight-first" UI (conclusion before data) | 3/10 |

---

## 32. Cross-Cutting Drop-Off Risk Map

Consolidated view of every drop-off risk across all journeys.

### High-Risk Drop-Off Points

| Journey | Point | Risk | Indicator | Primary Cause |
|---|---|---|---|---|
| Onboarding | Post-onboarding | HIGH | User sees empty dashboard | No pre-seeded data |
| First Day | End of session | HIGH | User closes after <60s | No compelling reason to return |
| First Week | Day 3-4 | MED-HIGH | User stops opening | "Just another todo list" |
| First Month | Week 3 | MEDIUM | Still only 1-2 modules active | No cross-module value seen |
| Return User | First return session | HIGH | User sees overdue avalanche | Guilt-driven abandonment |
| Return User | Catch-up >30s | MEDIUM | User closes before catching up | Too much to process |
| Mobile | First notification | MEDIUM | Notification not compelling | Generic push message |

### Risk by User Segment

| Segment | Highest Risk Point | Risk Level | Prevention |
|---|---|---|---|
| Student Builder | Day 3 — no course linked | MED | "Add your actual course" prompt |
| Startup Founder | Week 2 — no roadmap | HIGH | AI auto-suggests roadmap from task patterns |
| Freelancer | Week 1 — no income tracked | MED | "Log your last payment?" prompt |
| Creator | Day 2 — briefing dismissed | MED | Better notification: "Your top task is ready" |
| Knowledge Worker | Month 1 — never used AI chat | MED | "Ask ARIA anything" inline suggestion |
| Power User | Week 1 — too slow | HIGH | Keyboard shortcuts tutorial on first session |
| New User | First 30 seconds | HIGH | <60s to first win (task capture) |
| Returning User | First return | VERY HIGH | Guilt-free catch-up digest |

### Churn Waterfall

```
100% Sign up
  → 85% complete onboarding
    → 60% return Day 2
      → 40% survive Week 1
        → 25% reach Month 1
          → 15% become daily users (Month 3+)
```

Primary drop-off causes at each stage:
- Signup → Onboarding: No compelling first task (10% of users)
- Onboarding → Day 2: No briefing habit, empty dashboard (25%)
- Day 2 → Week 2: No course added, no routine (20%)
- Week 2 → Month 1: No cross-module value, not enough data (15%)
- Month 1+ : Churn from guilt after absence, lack of new value (10%)

---

## 33. Cross-Cutting Optimization Opportunities

Ranked optimization opportunities across ALL journeys, ordered by predicted impact.

### P0: Immediate (Ship within 1 sprint)

| # | Opportunity | Impact | Effort | Journeys Affected |
|---|---|---|---|---|
| 1 | Non-empty dashboard after onboarding | 40% Day 2 retention lift | Low | Onboarding, First Day |
| 2 | Guilt-free return digest (best first, then missed) | 30% return-to-active conversion | Medium | Exit & Retention |
| 3 | "One task to restart" push (after 3 days idle) | 25% re-activation | Low | Exit & Retention |
| 4 | Auto-forgive overdue tasks (>7 days) | 20% guilt reduction | Low | Weekly Review, Exit |
| 5 | Evening priority setting → better briefing | 15% briefing usefulness score | Medium | Daily Workflow |

### P1: High Impact (Ship within 2 sprints)

| # | Opportunity | Impact | Effort | Journeys Affected |
|---|---|---|---|---|
| 6 | Cross-module linking prompt ("Link to goal?") | 35% more task-goal links | Low | First Month, Goal |
| 7 | AI-suggested course from goals | 30% course enrollment rate | Medium | First Week, Learning |
| 8 | "Your week in 30 seconds" summary | 20% weekly review completion | Low | Weekly Review |
| 9 | Mobile-optimized briefing (3 items) | 25% mobile engagement | Medium | Mobile, Daily |
| 10 | Sleep-responsive task scheduling | 20% task completion on low-sleep days | Medium | Sleep, Daily |

### P2: Strategic (Ship within 1-2 months)

| # | Opportunity | Impact | Effort | Journeys Affected |
|---|---|---|---|---|
| 11 | Multi-platform sync with cursor position | 15% cross-device usage | High | Mobile, Tablet, Desktop |
| 12 | AI insight: cross-metric correlations | 15% analytics engagement | High | Analytics |
| 13 | Habit import: detect patterns from existing data | 20% more habits created | Medium | First Week |
| 14 | Opportunity radar: skill gap auto-detect | 25% better match quality | High | Opportunity |
| 15 | Keyboard shortcut tutorial on first desktop session | 30% power user conversion | Low | Desktop |

### P3: Future (Month 3+)

| # | Opportunity | Impact | Effort |
|---|---|---|---|
| 16 | API + CLI for power users | Power user retention | High |
| 17 | Custom dashboard builder | Power user satisfaction | High |
| 18 | Multi-user collaboration (shared projects) | Team use case | Very High |
| 19 | Browser extension deep integration | 2x more content saved | Medium |
| 20 | AI conversation history search | Chat utility | Medium |

---

## 34. Enterprise UX Recommendations

### 34.1 Accessibility Compliance (WCAG 2.1 AA)

| Requirement | Implementation | Check |
|---|---|---|
| Color contrast | All text: 4.5:1 minimum | Passes AA |
| Keyboard navigation | Every action reachable via Tab + Enter | Tab order tested |
| Screen reader | ARIA labels on all interactive elements | NVDA + VoiceOver tested |
| Focus indicators | 2px outline, visible on all focusable elements | Ensured |
| Motion reduction | `prefers-reduced-motion` media query respected | Framer Motion respects |
| Touch targets | All buttons ≥44px | All exported |
| Text resizing | Layout supports 200% zoom without horizontal scroll | Flexbox-based |
| Error announcements | Screen reader announces toast/error messages | Live region added |

### 34.2 Performance Budgets

| Metric | Target | Critical Journey |
|---|---|---|
| First Contentful Paint | <1.5s | Onboarding (first impression) |
| Time to Interactive | <2.5s | Onboarding (goal selection) |
| API response (AI) | <3s (Claude) / <10s (Ollama) | Daily Briefing |
| API response (CRUD) | <200ms | Task capture |
| Offline sync delay | <5s after reconnect | All write operations |
| Search response | <500ms | Search |
| Notification delivery | <10s from trigger | All push journeys |

### 34.3 Error Recovery Patterns

| Error Type | User-Facing Message | Recovery Action |
|---|---|---|
| Network offline | "Saved locally. Will sync when connected." | Queue write, sync on reconnect |
| AI timeout (>30s) | "ARIA is thinking. Here's a quick version." | Serve cached/algorithmic fallback |
| Supabase query error | "Something went wrong loading your data." | Retry button + reload |
| Notification permission denied | "We'll keep your briefing in-app." | Show in-app badge instead |
| OAuth failure | "Couldn't connect Google. Try again or use email." | Retry + email fallback |
| Sync conflict | "This item was changed on another device." | Show diff + pick version |
| Rate limited (429) | "You're moving fast! Take a 30s breather." | Countdown + cool-down toast |

### 34.4 Internationalization (i18n) Notes

| Aspect | Current | Planned |
|---|---|---|
| Languages | English (en-US) | en-IN (₹, dd/mm/yyyy), hi-IN (Hindi) |
| Date formats | ISO 8601 | Locale-aware (Indian: dd/mm/yyyy) |
| Currency | ₹ INR (default) | Configurable per user |
| Timezone | UTC + IP auto-detect | User-selectable, DST-aware |
| RTL support | Not implemented | Future: Arabic, Urdu |
| Number formats | 1,000.00 | Indian: 1,00,000 (lakh/crore) |

### 34.5 Privacy & Data Handling

| Data Type | Storage | User Control |
|---|---|---|
| Journey state | Local + Supabase | Export, delete all |
| AI prompts | Sent to Ollama (local) or Claude (cloud) | Choose AI provider |
| Notification preferences | Local storage + Supabase | Toggle per notification type |
| Analytics events | Supabase (anonymized) | Opt-out setting |
| Search history | Local (last 30 days) | Clear button |

---

## Appendix A: Journey Template Specification

Every journey in this document follows this 18-field template:

| # | Field | Type | Description | Required |
|---|---|---|---|---|
| 1 | Trigger | String | What initiates this journey | ✅ |
| 2 | Entry Point | String | URL / UI action / notification | ✅ |
| 3 | User State | String | Emotional + cognitive state at start | ✅ |
| 4 | Pre-Journey Context | String | What happened before this journey | ✅ |
| 5 | Flow | Code Block | Step-by-step user flow diagram | ✅ |
| 6 | Action Table | Table | Step, Action, Duration, Cognitive Load, AI Assistance | ✅ |
| 7 | Decision Tree | Table (optional) | Decision points, options, optimal path | ✅ |
| 8 | AI Intervention Points | Table | When AI acts, what it does | ✅ |
| 9 | AI Recommendation Points | Table (optional) | Passive AI suggestions | Recommended |
| 10 | AI Automation Opportunities | Table (optional) | Background automation | Recommended |
| 11 | Success State | String | What "done well" looks like | ✅ |
| 12 | Failure State | String | What "done poorly" looks like | ✅ |
| 13 | Exit State | String | Where user goes after | ✅ |
| 14 | Friction Points | Table | Step, Friction, Severity, Mitigation | ✅ |
| 15 | Cognitive Load Heatmap | Table (optional) | Step, Load, Contributor, Reduction | Recommended |
| 16 | Drop-Off Risk | Table (optional) | Step, Risk, Indicator, Prevention | Recommended |
| 17 | Optimization Opportunity | String | Single highest-impact change | ✅ |
| 18 | Accessibility | List (optional) | WCAG considerations | Recommended |

---

## Appendix B: User Type × Dimension Matrix

Full 360° comparison across all 8 user types and 20 dimensions.

### Demographics & Environment

| Dimension | Student Builder | Startup Founder | Freelancer | Creator | Knowledge Worker | Power User | New User | Returning User |
|---|---|---|---|---|---|---|---|---|
| **Population** | 40% | 10% | 15% | 10% | 15% | 5% | Transient | 60% sessions |
| **Age Range** | 18-24 | 22-30 | 20-28 | 19-35 | 22-28 | 20-35 | 18-45 | 18-45 |
| **Education** | Pursuing BTech | BTech (grad) | BTech/self-taught | Varied | BTech (grad) | BTech+ | Varied | Varied |
| **Primary Device** | Laptop+Phone | MacBook+iPhone | Laptop+dual | MacBook+iPad | Work laptop+iPad | Desktop+mech | Phone (60%) | Phone (60%) |
| **Secondary Device** | Android/iOS | iPhone | Android | iPhone | iPhone | Custom | — | — |
| **Work Context** | College campus | Home/coffee shop | Home/co-work | Home/studio | Office/WFH | Home/office | Anywhere | Anywhere |
| **Internet Quality** | Campus WiFi (spotty) | Good (paid) | Variable (travels) | Good | Office (stable) | Excellent | Variable | Variable |
| **Income (₹/mo)** | 0-5K | 0-50K | 25-80K | 0-200K | 35-60K | 50-200K+ | Variable | Variable |
| **WTP (₹/mo)** | 0-200 | 500-1500 | 200-500 | 500-2000 | 100-300 | 1000-3000 | 0 | 0-200 |

### Behavioral

| Dimension | Student Builder | Startup Founder | Freelancer | Creator | Knowledge Worker | Power User | New User | Returning User |
|---|---|---|---|---|---|---|---|---|
| **Tech Level** | Intermediate | High | Int-Adv | Low-Med | Medium | Expert | Variable | Variable |
| **Session Length** | 3-8 min | 15-30 min | 10-20 min | 10-20 min | 5-15 min | 30-60 min | 2-5 min | 1-3 min |
| **Session Freq** | 3-5x/day | 5-10x/day | 3-5x/day | 3-5x/day | 2-3x/day | 10+/day | 1-3 (week 1) | 1-2x/week |
| **Offline Need** | High | Medium | High | Medium | Medium | Low | Low | Medium |
| **Primary Emotion** | Overwhelmed | Determined | Anxious | Inspired | Stressed | In control | Curious | Guilty |
| **Secondary Emotion** | Motivated | Stressed | Hopeful | Frustrated | Burned out | Bored | Skeptical | Hopeful |
| **AI Expectation** | Plan my day | Break down MVP | Find me work | Suggest content | Schedule study | Automate all | Guide me | Catch me up |
| **OS Preference** | Windows/Mac | macOS | Windows/Ubuntu | macOS | Windows | Linux/macOS | — | — |
| **Browser** | Chrome | Arc/Brave | Chrome | Safari | Chrome | Firefox/Vivaldi | Chrome (60%) | Chrome (60%) |

### Module Engagement

| Dimension | Student Builder | Startup Founder | Freelancer | Creator | Knowledge Worker | Power User | New User | Returning User |
|---|---|---|---|---|---|---|---|---|
| **Primary Module** | Tasks+ Courses | Roadmap+ Projects | Projects+ Income | Analytics+ Ideas | Courses+ Goals | All+Automation | Onboarding | Dashboard |
| **Secondary Module** | Opportunities | Income+Habits | Opportunities | Tasks+ Habits | Sleep+Tasks | Analytics | Dashboard | Tasks |
| **Tertiary Module** | Time+Sleep | Networking+Content | Skills+Sleep | Income+Sleep | Opportunities | All | Tasks | Opportunities |
| **Briefing Value** | High: daily plan | Med: metrics | Med: task prio | High: content stats | High: study plan | Low: knows already | High: guidance | Med: catch-up |
| **Weekly Review** | Med: course check | High: metrics | High: income | High: content perf | Med: goal check | High: automation | N/A | Med: progress |
| **AI Chat Usage** | Med | High | Med | Med | Low | High | Low | Med |

### Goals & Motivations

| Dimension | Student Builder | Startup Founder | Freelancer | Creator | Knowledge Worker | Power User | New User | Returning User |
|---|---|---|---|---|---|---|---|---|
| **Top Goal** | FAANG intern | Ship MVP | Product job | 10K followers | Switch company | System mastery | "Is this useful?" | Catch up |
| **Primary Motivation** | Placement | Build from 0 | Prove capability | Creative impact | Career growth | Optimization | Solve pain point | Reduce guilt |
| **Urgency Level** | High | Very High | High | Medium | Medium | Low | Low | Very High |
| **Risk Tolerance** | Low-Med | Very High | High | High | Low | Medium | Low | Low |
| **Change Readiness** | Medium | Very High | High | High | Low | Medium | Very High | Medium |

### Frustration Profile

| Dimension | Student Builder | Startup Founder | Freelancer | Creator | Knowledge Worker | Power User | New User | Returning User |
|---|---|---|---|---|---|---|---|---|
| **#1 Frustration** | Course overload (9/10) | Feature creep (9/10) | No CS degree gaps | Content chaos (9/10) | No study structure | No keyboard shortcuts | Blank slate paralysis | Overdue avalanche |
| **#2 Frustration** | Tool fragmentation | Context switching | Unpredictable income | Platform dependency | GATE/GRE indecision | Can't customize | Long onboarding | Context loss |
| **#3 Frustration** | Missed deadlines | No PM fit signal | Juggling 4 projects | Inconsistent schedule | LeetCode guilt | No batch ops | Choice overload | Guilt UI |

---

## Appendix C: Cognitive Load Reference Scale

Standardized scale used across all journey assessments.

| Level | Label | Description | Example | Allowed Steps |
|---|---|---|---|---|
| 0/10 | None | No thinking required | Logging in via Google OAuth | Any |
| 1/10 | Trivial | Reflexive action | One-tap habit log, checkbox complete | Any |
| 2/10 | Easy | Single decision, familiar pattern | Review briefing items, scan dashboard | Any |
| 3/10 | Moderate | Multiple options, clear context | Select goals from templates, capture task | Any |
| 4/10 | Notable | Trade-off decisions, new patterns | Choose between courses, set up integration | Max 2 steps |
| 5/10 | Significant | Planning, synthesis, multiple variables | Plan weekly schedule, create roadmap first draft | Max 1 step with AI |
| 6/10 | Complex | System thinking, nested decisions | Configure automation rules, custom dashboard | Requires AI pre-fill |
| 7/10 | Demanding | Analysis across multiple dimensions | Cross-metric correlation analysis | Not recommended for UI |
| 8/10 | Heavy | Full context required, high stakes | Manual roadmap from scratch, complex project planning | NEVER — must be AI-assisted |
| 9/10 | Overload | Near-certain abandonment | Data migration, multi-step configuration | NEVER |
| 10/10 | Crippling | Immediate exit | Error recovery without guidance | NEVER |

**Design Rule:** No user-facing step shall exceed 5/10. Steps at or above 6/10 must be AI-assisted with pre-filled defaults.

---

## Appendix D: Drop-Off Risk Reference Scale

Standardized scale used across all journey assessments.

| Level | Label | Description | Expected Abandonment | Recovery Action |
|---|---|---|---|---|
| VERY LOW | Safe | User is engaged, flowing | <1% | None needed |
| LOW | Comfortable | User is moving, minor hesitation | 1-5% | Monitor |
| MEDIUM | Wobbly | User may pause or reconsider | 5-15% | In-app nudge |
| HIGH | Dangerous | User is likely to leave | 15-30% | Immediate intervention |
| VERY HIGH | Critical | User is almost certainly leaving | 30-50% | Full re-engagement sequence |
| EXTREME | Terminal | User has already decided to leave | >50% | Alternative offer or graceful exit |

---

## Appendix E: User Story Cross-Reference

Key user stories from `docs/product/06_UserStories.md` mapped to journey sections.

| US-ID | User Story Summary | Primary Journey | Secondary Journey |
|---|---|---|---|
| US-001 | Student wants to capture a task quickly | Onboarding §6 | Daily Workflow §10 |
| US-002 | Student wants AI to set task priority | Onboarding §6 | — |
| US-003 | Student wants morning briefing with today's plan | First Day §7 | Daily Workflow §10 |
| US-004 | Student wants to track course progress | First Week §8 | Learning §15 |
| US-005 | Student wants to link tasks to goals | First Month §9 | Goal §19 |
| US-006 | Student wants weekly review | First Week §8 | Weekly Review §11 |
| US-007 | Freelancer wants income tracking | First Month §9 | Module §14.5 |
| US-008 | Freelancer wants opportunity matching | Opportunity §17 | — |
| US-009 | Founder wants roadmap for MVP | Roadmap §20 | Project §18 |
| US-010 | Creator wants content idea management | Module §14.6 | — |
| US-011 | Knowledge worker wants study plan | Learning §15 | Goal §19 |
| US-012 | All users want guilt-free return | Exit & Retention §27 | — |
| US-013 | Student wants distraction-free study timer | Module §14.8 | Daily Workflow §10 |
| US-014 | Student wants sleep tracking + wind-down | Sleep §12 | Daily Workflow §10 |
| US-015 | All users want keyboard shortcuts | Desktop §26 | — |

---

## Appendix F: Glossary

| Term | Definition | Used In |
|---|---|---|
| **Activation** | User completes their first meaningful action (task capture + completion) | §1, §6 |
| **Agent (A00-A14)** | AI sub-agent responsible for specific domain | Throughout |
| **ARIA** | AI-powered orchestrator agent (A00) — the system's intelligence layer | Throughout |
| **Briefing** | Daily morning summary generated by A09 with tasks, metrics, opportunities | §10, §11 |
| **Churn** | User stops using the system for >30 days | §27 |
| **Cognitive Load** | Mental effort required to complete a step (0-10 scale, max 5 in UI) | §31, Appendix C |
| **Crammer** | Archetype that uses app intensively in crisis mode, ignores it otherwise | §4.2 |
| **CRUD** | Create, Read, Update, Delete — standard data operations | §28 |
| **Drop-Off Risk** | Likelihood of user abandoning at a specific step (VERY LOW to EXTREME) | §32, Appendix D |
| **Editing** | User lifecycle stage: active daily user with 3-5 modules | §9 |
| **Entry Point** | URL or UI action that starts a journey | Throughout |
| **Exit State** | Where user goes after completing or abandoning a journey | Throughout |
| **Failure State** | What happens when a journey doesn't achieve its goal | Throughout |
| **Friction** | UX element that slows, confuses, or frustrates the user | §30 |
| **Intervention** | AI or system action triggered by user behavior (event/threshold/cron) | §29 |
| **Journey** | Complete user workflow from trigger through success/failure to exit | Throughout |
| **Module** | Functional area of the app (Tasks, Courses, Habits, etc.) | §14 |
| **NPS** | Net Promoter Score — user satisfaction metric (-100 to +100) | Appendix A |
| **Ollama** | Local AI model server (default: Mistral 7B) — keeps data on-device | §28 |
| **Onboarding** | First 5-step setup process: OAuth → Name → Goals → Task → Briefing | §6 |
| **Pomodoro** | 25-minute focused work interval with 5-minute break | §14.8 |
| **Re-engagement** | Sequence of actions to bring inactive users back | §27.2 |
| **Resurrection** | Final re-engagement attempt after 14+ days of inactivity | §27.4 |
| **RLS** | Row-Level Security — Supabase feature ensuring user data isolation | §28 |
| **Success State** | What "done well" looks like for a journey | Throughout |
| **Time to Value** | Duration from signup to first meaningful user action (target: <60s) | §6 |
| **Trigger** | Event that initiates a journey (user action, cron, notification) | Throughout |
| **User Type** | Persona-based segment (Student Builder, Startup Founder, etc.) | §3 |
| **WCAG** | Web Content Accessibility Guidelines — accessibility standard | §34 |
| **Weekly Review** | Sunday report generated by A10 summarizing the week | §11 |
| **Wind-Down** | Evening routine: sleep log + tomorrow preview + optional relaxation | §12 |
| **Zone (Z1-Z8)** | Dashboard layout zones: Greeting, KPIs, Focus, Courses, Habits, etc. | §10, §14 |

---

## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-UJA-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal — Design Reference |
| Target Audience | Designers, Product Managers, UX Researchers |
| Last Updated | 2026-06-11 |
| Classification | Internal — Architecture Reference |
| Target Audience | AI Agents (Claude, Cursor, Copilot), UX Designers, Product Managers, Frontend Engineers, AI Engineers |
| Supersedes | Journey fragments across `docs/product/Personas.md`, `docs/product/UserFlows.md`, `docs/product/06_UserStories.md`, `docs/design/ProductArchitecture.md`, `docs/design/Enterprise_Frontend_Discovery_Report_v3.md` |

