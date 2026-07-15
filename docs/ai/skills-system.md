# Skills System — Architecture & Reference

## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-SKS-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Internal — Engineering |
| Last Updated | 2026-07-11 |
| Review Cycle | Monthly |
| Approver | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Skill Sub-Agents](#3-skill-sub-agents)
4. [Data Model](#4-data-model)
5. [API Endpoints](#5-api-endpoints)
6. [Cron Jobs](#6-cron-jobs)
7. [Prompt Architecture](#7-prompt-architecture)
8. [Integration with Other Agents](#8-integration-with-other-agents)
9. [Frontend Integration](#9-frontend-integration)
10. [Future Roadmap](#10-future-roadmap)
11. [Cross-References](#11-cross-references)

---

## 1. Executive Summary

The **Skills System** is ARIA OS's competency tracking and intelligence framework. It enables users to inventory their skills, assess proficiency, receive personalized learning recommendations, track market demand, verify evidence, and match skills to career opportunities. The system consists of **8 AI-powered sub-agents** (driven by prompt files), **5 cron jobs**, a **comprehensive REST API**, and a **full CRUD data model** spanning 40+ database tables.

**Why it exists:** Students and professionals need to manage their skill portfolios with the same rigor they apply to financial assets. The Skills System provides market intelligence, gap analysis, personalized roadmaps, and evidence verification — turning raw skill data into actionable career intelligence.

**Key design tenants:**
- **Graceful degradation:** Every agent works without AI via algorithmic fallback if LLM is unavailable
- **PromptLoader-driven:** All sub-agent prompts are externalized in `prompts/agents/` with validated YAML frontmatter
- **Evidence-based scoring:** Skill levels are backed by verifiable evidence (projects, certifications, GitHub repos)
- **Market-aware:** Skill health scores incorporate demand, salary, growth, and competition data

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Skills Page │  │ Skill Detail │  │ Opportunity Radar     │   │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬───────────┘   │
└─────────┼─────────────────┼─────────────────────┼───────────────┘
          │        HTTP      │                     │
          ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                         │
│                    /api/v1/skills/...                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  SK-01 ~ SK-09   │ │    CRON JOBS     │ │   Supabase DB    │
│  AI Sub-Agents   │ │  (5 scheduled)   │ │  (40+ tables)    │
│  (PromptLoader)  │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │
          ▼
┌──────────────────┐
│   LLM Client     │
│ Ollama / Claude  │
│ (circuit breaker)│
└──────────────────┘
```

### 2.1 Component Responsibilities

| Layer | Technology | Responsibility |
|---|---|---|
| **Frontend** | Next.js 14, React, Tailwind CSS | Skills dashboard, detail pages, evidence upload UI |
| **API** | FastAPI — `/api/v1/skills/` | CRUD + AI-triggered endpoints, auth, pagination |
| **AI Agents** | Python async modules in `packages/ai/agents/` | Skill assessment, recommendation, intelligence, roadmap, evidence, career, market, opportunity matching |
| **Prompts** | Markdown files in `prompts/agents/skill_*.md` | System prompts for each sub-agent with YAML frontmatter |
| **Scheduler** | APScheduler in `services/scheduler/` | 5 cron jobs for intelligence refresh, evidence expiry, analytics snapshots, MV refresh, retention cleanup |
| **Database** | Supabase PostgreSQL | 40+ tables for skills, user skills, evidence, market data, roadmaps, career goals, relationships |

### 2.2 Data Flow

1. **User input** (manual skill entry, evidence upload, self-assessment) → API → Supabase
2. **Scheduled triggers** (cron jobs) → Sub-agent modules → LLM (if available) → DB update
3. **On-demand triggers** (user clicks "Assess" or "Recommend") → API → Sub-agent → LLM → Response
4. **Frontend** reads aggregated data via API + renders agent output (fallback content if AI unavailable)

---

## 3. Skill Sub-Agents

### 3.1 Agent Registry

| ID | Agent | Prompt File | Module Function | Trigger | LLM Required? | Fallback? |
|---|---|---|---|---|---|---|
| SK-01 | Skill Assessment | `skill_assessment_agent.md` | `assess_user_skill()` | On-demand | Yes | Statistical fallback |
| SK-02 | Skill Recommendation | `skill_recommendation_agent.md` | `recommend_skills()` | On-demand | Yes | Rule-based fallback |
| SK-03 | Skill Intelligence | `skill_intelligence_agent.md` | `analyze_skill_intelligence()` | Cron + on-demand | Yes | Score-based fallback |
| SK-04 | Skill Roadmap | `skill_roadmap_agent.md` | `generate_roadmap()` | On-demand | Yes | Template fallback |
| SK-05 | Skill Evidence | `skill_evidence_agent.md` | `verify_evidence()` | Cron | Yes | Auto-verify fallback |
| SK-06 | Career Readiness | `skill_career_agent.md` | `analyze_career_readiness()` | On-demand | Yes | Match-score fallback |
| SK-07 | Market Intelligence | `skill_market_agent.md` | `analyze_market_intelligence()` | Cron | Yes | Aggregate fallback |
| SK-08 | Skill Graph | _(module only)_ | Graph traversal functions | Internal | No | Always works |
| SK-09 | Skill Opportunity | `skill_opportunity_agent.md` | `match_opportunities()` | On-demand | Yes | Score-based fallback |

### 3.2 Agent Details

#### SK-01 — Skill Assessment Agent

- **File:** `prompts/agents/skill_assessment_agent.md` (46 lines, v1.0.0)
- **Model:** ollama/mistral:7b, temperature 0.3
- **Function:** Evaluates user proficiency (0–5 scale) based on current level, state, and evidence items. Produces objective level recommendations, confidence adjustments, and actionable gap analysis.
- **Input:** `skill_name`, `current_level`, `state`, `confidence_score`, `evidence_items[]`
- **Output:** `recommended_level`, `confidence_adjustment`, `gaps[]`, `next_milestones[]`
- **Code:** `packages/ai/agents/skill_agent.py:21-60+` — `assess_user_skill()`
- **Fallback:** Returns statistical estimate based on evidence count and quality scores

#### SK-02 — Skill Recommendation Agent

- **File:** `prompts/agents/skill_recommendation_agent.md` (726 lines, v2.0.0)
- **Model:** ollama/mistral:7b, temperature 0.4
- **Function:** Analyzes existing skills, career goals, and interests to recommend the 5–10 most valuable next skills. Balances user interests, career gaps, market demand, and skill adjacency.
- **Input:** `user_skills[]`, `career_goals[]`, `interests[]`, `market_data`
- **Output:** Ranked recommendations with reasoning, estimated commitment, priority
- **Code:** `packages/ai/agents/skill_agent.py` — `recommend_skills()`
- **Notes:** Includes diversity and bias mitigators — avoids popularity bias, considers unique user context

#### SK-03 — Skill Intelligence Agent

- **File:** `prompts/agents/skill_intelligence_agent.md` (718 lines, v2.0.0)
- **Model:** ollama/mistral:7b, temperature 0.3
- **Function:** Analyzes market intelligence data (demand, growth, salary, competition, future relevance). Computes composite health score (0–100) and generates strategic recommendations.
- **Input:** `skill_name`, `demand`, `growth_rate`, `salary_data`, `competition_level`, `future_relevance`
- **Output:** `health_score`, `trend_indicators[]`, `recommendations[]`, `anomaly_flags[]`
- **Notes:** Operates as a financial analyst for human capital — each skill is an asset with performance metrics

#### SK-04 — Skill Roadmap Agent

- **File:** `prompts/agents/skill_roadmap_agent.md` (861 lines, v2.0.0)
- **Model:** ollama/mistral:7b, temperature 0.4
- **Function:** Generates structured, phased learning roadmaps from current level to target. Detects prerequisite gaps and inserts foundation phases automatically.
- **Input:** `skill_name`, `current_level`, `target_level`, `interests`, `learning_style`, `hours_per_week`
- **Output:** Phased roadmap with milestones, resources, estimated hours per phase
- **Notes:** Dependency validator — detects missing prerequisites and inserts bridge phases

#### SK-05 — Skill Evidence Agent

- **File:** `prompts/agents/skill_evidence_agent.md` (44 lines, v1.0.0)
- **Model:** ollama/mistral:7b, temperature 0.2
- **Function:** Verifies and scores evidence items (projects, GitHub repos, certifications) submitted to support skill claims. Evaluates authenticity, quality, and relevance.
- **Input:** `title`, `source_type`, `url`, `description`, `current_state`, `signed_hash`
- **Output:** `verification_decision`, `quality_score`, `confidence`, `notes[]`
- **Code:** `packages/ai/agents/skill_agent.py` — `verify_evidence()`
- **Cron trigger:** Runs daily at 3 AM to check evidence expiry

#### SK-06 — Career Readiness Agent

- **File:** `prompts/agents/skill_career_agent.md` (43 lines, v1.0.0)
- **Model:** ollama/mistral:7b, temperature 0.3
- **Function:** Evaluates skill portfolio against career goals. Provides readiness score, path recommendations, and actionable improvement items.
- **Input:** `career_goal`, `skills[]`, `interests[]`, `skill_count`, `average_level`
- **Output:** `readiness_score`, `path_recommendations[]`, `skill_gaps[]`, `action_items[]`

#### SK-07 — Market Intelligence Agent

- **File:** `prompts/agents/skill_market_agent.md` (756 lines, v2.0.0)
- **Model:** ollama/mistral:7b, temperature 0.3
- **Function:** Analyzes market demand, salary trends, and growth opportunities. Acts as strategic investment advisor for the user's learning time.
- **Input:** `market_data[]`, `skill_name`, `industry`, `region`
- **Output:** `demand_trend`, `salary_range`, `growth_rate`, `market_saturation`, `strategic_verdict`
- **Notes:** Includes market bias mitigation — adjusts for data quality and sample size

#### SK-08 — Skill Graph Agent

- **File:** _(no prompt file — algorithmic only)_
- **Function:** Provides skill graph traversal and pathfinding (prerequisite chains, related skills, alternative paths). Purely algorithmic — no LLM needed.
- **Code:** `packages/ai/agents/skill_agent.py` — graph traversal functions

#### SK-09 — Skill Opportunity Agent

- **File:** `prompts/agents/skill_opportunity_agent.md` (837 lines, v2.0.0)
- **Model:** ollama/mistral:7b, temperature 0.2
- **Function:** Matches user skill profiles to opportunities (jobs, projects, gigs, internships, hackathons). Calculates fit scores with gap analysis and readiness assessment.
- **Input:** `user_skills[]`, `opportunities[]`, `career_goals[]`
- **Output:** Ranked matches with `fit_score`, `gap_analysis{}`, `readiness`, `critical_gaps[]`, `nice_to_haves[]`
- **Notes:** Distinguishes between hard blockers (required skills) and nice-to-haves (preferred skills)

---

## 4. Data Model

### 4.1 Core Tables

| Table | Description | Key Columns | RLs |
|---|---|---|---|
| `skills` | Master skill registry | `skill_id`, `name`, `description`, `category_id`, `level_min`, `level_max` | Public read |
| `skill_categories` | Skill taxonomy categories | `category_id`, `name`, `sort_order` | Public read |
| `skill_relationships` | Prerequisite/related/supersedes links | `relationship_id`, `source_skill_id`, `target_skill_id`, `relationship_type` | Public read |
| `user_skills` | User-skill bridge with level & state | `user_skill_id`, `user_id`, `skill_id`, `level`, `state`, `confidence_score` | User-scoped |
| `user_skill_evidence` | Evidence supporting skill claims | `evidence_id`, `user_skill_id`, `user_id`, `source_type`, `title`, `url`, `quality_score`, `state`, `signed_hash` | User-scoped |
| `user_skill_targets` | Target levels with priority | `target_id`, `user_skill_id`, `user_id`, `target_level`, `deadline`, `priority`, `status` | User-scoped |
| `user_skill_assessments` | Assessment history | `assessment_id`, `user_skill_id`, `user_id`, `assessment_type`, `previous_level`, `recommended_level`, `confidence_adjustment` | User-scoped |
| `skill_market_data` | Market intelligence snapshots | `market_data_id`, `skill_id`, `demand_score`, `growth_rate`, `salary_min`, `salary_max`, `competition_level`, `future_relevance` | Public read |
| `skill_income_data` | Income correlation data | `income_data_id`, `skill_id`, `avg_hourly_rate`, `avg_annual_salary`, `currency` | Public read |
| `skill_certifications` | Certification definitions | `certification_id`, `skill_id`, `name`, `provider`, `url`, `difficulty_level` | Public read |
| `skill_project_links` | Project templates for skills | `project_link_id`, `skill_id`, `title`, `description`, `difficulty_level` | Public read |
| `skill_roadmap_definitions` | Generated roadmaps | `roadmap_id`, `user_skill_target_id`, `phases[]`, `total_estimated_hours`, `status` | User-scoped |
| `skill_opportunity_links` | Opportunity matches | `opportunity_link_id`, `skill_id`, `opportunity_id`, `match_score`, `gap_analysis` | User-scoped |

### 4.2 Enum Types

| Enum | Values |
|---|---|
| `RelationshipType` | prerequisite, related_to, supersedes, variant_of, similar_to, recommended_before, complementary, alternative |
| `UserSkillState` | planned, learning, practicing, active, reviewing, archived, deprecated |
| `EvidenceSourceType` | project, github, certification, hackathon, freelance, opensource, assessment, work_experience, course, publication, patent, award |
| `EvidenceState` | raw, pending_verification, verified, verified_auto, verified_ai, verified_human, rejected, flagged, active, expired |
| `TargetPriority` | low, medium, high, urgent |
| `TargetStatus` | active, in_progress, achieved, paused, abandoned, expired |
| `AssessmentType` | self, ai_evaluated, auto_mcq, peer_review, human_review, project_evaluation, certification_equivalency |

### 4.3 Key Indexes

- `user_skills`: `(user_id, skill_id)` unique, `(user_id, state)` filter
- `user_skill_evidence`: `(user_skill_id, state)` for verification queries
- `skill_market_data`: `(skill_id, created_at)` for trend analysis

---

## 5. API Endpoints

All endpoints are under `/api/v1/skills/`. Authentication is required for all endpoints unless noted.

### 5.1 Category Management

| Method | Path | Description |
|---|---|---|
| `GET` | `/categories` | List all skill categories (paginated) |
| `POST` | `/categories` | Create a new category |
| `GET` | `/categories/{id}` | Get category by ID |
| `PUT` | `/categories/{id}` | Update a category |
| `DELETE` | `/categories/{id}` | Delete a category |

### 5.2 Skill Management

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | List all skills (paginated, filterable by category) |
| `POST` | `/` | Create a new skill |
| `GET` | `/{id}` | Get skill by ID |
| `PUT` | `/{id}` | Update a skill |
| `DELETE` | `/{id}` | Delete a skill |

### 5.3 User Skills

| Method | Path | Description |
|---|---|---|
| `GET` | `/user-skills` | List current user's skills |
| `POST` | `/user-skills` | Add a skill to user's inventory |
| `PUT` | `/user-skills/{id}` | Update user skill (level, state) |
| `DELETE` | `/user-skills/{id}` | Remove skill from inventory |
| `POST` | `/user-skills/{id}/assess` | Trigger SK-01 assessment |
| `POST` | `/user-skills/{id}/evidence` | Add evidence item |

### 5.4 Evidence

| Method | Path | Description |
|---|---|---|
| `GET` | `/evidence` | List evidence items |
| `POST` | `/evidence` | Submit new evidence |
| `PUT` | `/evidence/{id}` | Update evidence |
| `DELETE` | `/evidence/{id}` | Delete evidence |

### 5.5 AI-Powered Endpoints

| Method | Path | Agent | Description |
|---|---|---|---|
| `POST` | `/recommendations` | SK-02 | Get skill recommendations |
| `POST` | `/intelligence` | SK-03 | Get skill intelligence analysis |
| `POST` | `/roadmaps` | SK-04 | Generate learning roadmap |
| `POST` | `/career-readiness` | SK-06 | Get career readiness analysis |
| `POST` | `/market-intelligence` | SK-07 | Get market intelligence |
| `POST` | `/opportunity-matching` | SK-09 | Match skills to opportunities |

### 5.6 Relationships & Taxonomy

| Method | Path | Description |
|---|---|---|
| `GET` | `/relationships` | List skill relationships |
| `POST` | `/relationships` | Create relationship link |
| `GET` | `/tags` | List all tags |
| `POST` | `/tags` | Create a tag |
| `GET` | `/taxonomy/history` | Get taxonomy change history |

### 5.7 Market Data

| Method | Path | Description |
|---|---|---|
| `GET` | `/market-data` | List market data entries |
| `POST` | `/market-data` | Add market data |
| `GET` | `/market-history` | Get market trend history |

### 5.8 Activity & Events

| Method | Path | Description |
|---|---|---|
| `GET` | `/activity-log` | Get user's skill activity log |
| `POST` | `/events` | Create a skill event |
| `GET` | `/events` | List skill events |
| `GET` | `/forecasts` | Get skill forecasts |
| `GET` | `/audit-log` | Get audit trail (admin) |
| `GET` | `/analytics-snapshots` | Get analytics snapshots |
| `GET` | `/user-skill-history` | Get user skill level history |

---

## 6. Cron Jobs

5 scheduled jobs run via APScheduler in `services/scheduler/`:

| Job | Schedule | Function | Description |
|---|---|---|---|
| **Skill Intelligence Refresh** | Daily at 5:00 AM | `skill_intelligence_refresh.run()` | Refreshes `skill_market_data` — pulls latest demand, salary, and growth metrics from configured data sources |
| **Skill Evidence Expiry** | Daily at 3:00 AM | `skill_evidence_expiry.run()` | Checks `user_skill_evidence` for expired items (based on `expired` state + retention policy). Marks stale evidence and decrements confidence scores for affected user skills |
| **Skill Analytics Snapshot** | Daily at 11:30 PM | `skill_analytics_snapshot.run()` | Captures daily snapshot of aggregated skill metrics (total skills tracked, average levels, evidence counts) into `skill_analytics_snapshots` table for trend analysis |
| **Skill MV Refresh** | Daily at 4:00 AM | `skill_mv_refresh.run()` | Refreshes materialized views: skill health scores, skill relationship graphs, user skill aggregates |
| **Skill Retention Cleanup** | Daily at 2:30 AM | `skill_retention_cleanup.run()` | Enforces data retention policies — purges expired evidence, old assessment records, and stale activity logs beyond retention window |

---

## 7. Prompt Architecture

### 7.1 File Layout

```
prompts/agents/
├── skill_assessment_agent.md          (46 lines,  v1.0.0)  — SK-01
├── skill_recommendation_agent.md      (726 lines, v2.0.0)  — SK-02
├── skill_intelligence_agent.md        (718 lines, v2.0.0)  — SK-03
├── skill_roadmap_agent.md             (861 lines, v2.0.0)  — SK-04
├── skill_evidence_agent.md            (44 lines,  v1.0.0)  — SK-05
├── skill_career_agent.md              (43 lines,  v1.0.0)  — SK-06
├── skill_market_agent.md              (756 lines, v2.0.0)  — SK-07
└── skill_opportunity_agent.md         (837 lines, v2.0.0)  — SK-09
```

### 7.2 Frontmatter Schema (All Prompts)

All skill prompt files follow the standardized frontmatter:

```yaml
---
version: X.Y.Z          # Semver — bumped per revision
status: active           # active | draft | deprecated
model: ollama/mistral:7b # Target LLM model
max_tokens: 4096         # Token budget
temperature: 0.2-0.4     # Determinism vs creativity
description: >           # One-line summary of purpose
  Description here
tags: [skills, ...]      # Required categorization
last_updated: 2026-06-24 # ISO date
approved_by: developer    # Who approved
review_cycle: weekly      # Review frequency
---
```

### 7.3 Prompt Structure (All Skill Prompts)

Each prompt follows this internal structure:

1. **Role Definition** — Who the agent is, its purpose, values, and constraints
2. **Input Schema** — All input fields with types, descriptions, and whether they are required
3. **Output JSON Schema** — Complete schema with required/optional fields, types, validation rules
4. **Detailed Instructions** — Step-by-step reasoning chain, decision trees, priority rules
5. **Few-Shot Examples** — 3–5 complete input → output examples (larger prompts: 4–5 examples)
6. **Edge Cases** — Empty data, missing fields, contradictory inputs, boundary conditions
7. **Anti-Patterns** — What NOT to do with examples of bad outputs
8. **Quality Criteria** — Self-verification checklist before output generation
9. **Error Recovery** — What to do when generation fails or token budget is exceeded

### 7.4 Prompt Loading

All sub-agents use `PromptLoader` (from `packages/ai/prompt_loader.py`) to load prompts:

```python
from ai.prompt_loader import prompts

assessment_prompt = prompts.get_agent("skill_assessment_agent")
if assessment_prompt:
    system = assessment_prompt.system_prompt
    # ... construct user prompt, call LLM
else:
    # Fallback logic — no AI dependency
```

Graceful degradation is built in: if a prompt file is missing, malformed, or the LLM is unavailable, every agent returns a valid algorithmic result.

---

## 8. Integration with Other Agents

### 8.1 Learning Agent (A03)

The Learning Agent detects patterns in user behavior and feeds trend data into:
- **SK-02** (Recommendation): Learning velocity and topic affinity influence recommendations
- **SK-04** (Roadmap): Past learning pace calibrates roadmap phase durations

### 8.2 Opportunity Radar Agent (A06)

The Opportunity Radar (A06) provides the opportunity feed consumed by:
- **SK-09** (Opportunity Matching): Matches user skill profiles against radar opportunities
- **SK-06** (Career Readiness): Career path recommendations reference radar-identified opportunities

### 8.3 Memory Agent (A02)

The Memory Agent stores user preferences and patterns that inform:
- **SK-02** (Recommendation): Preferred learning styles, domain interests
- **SK-04** (Roadmap): Learning pace, time availability patterns

### 8.4 Nudge Agent (A14)

Nudge Agent uses skill assessment data from SK-01 to:
- Generate course/habit nudges when skill confidence drops below threshold
- Recommend skill practice sessions during low-productivity periods

### 8.5 Weekly Review Agent (A10)

The Weekly Review incorporates skills data:
- Skill progress highlights (levels gained, evidence added)
- Market intelligence changes for tracked skills
- Roadmap milestone completions or delays

---

## 9. Frontend Integration

### 9.1 Route Structure

```
(dashboard)/skills/page.tsx           — Skills dashboard (list, search, filter)
(dashboard)/skills/[skill_id]/        — Skill detail page (assessment, evidence, roadmap)
```

### 9.2 Dashboard Features

- **Skill inventory:** List of tracked skills with levels, states, confidence scores
- **Recommended for you:** SK-02 output — ranked skill recommendations with reasoning
- **Skill health cards:** SK-03 health scores displayed on radar charts
- **Active roadmaps:** SK-04 generated roadmaps with phase completion tracking
- **Evidence upload:** Evidence submission UI with AI-powered verification status
- **Market trends:** SK-07 market intelligence visualized as trend charts
- **Opportunity matches:** SK-09 match scores with gap analysis

### 9.3 UX States

| State | Behavior |
|---|---|
| **Loading** | Skeleton cards with pulse animation |
| **Empty** | "Get started" CTA to add your first skill or import from GitHub |
| **AI Unavailable** | Show algorithmic fallback data (statistical scores, template roadmaps) with subtle "AI unavailable" indicator |
| **Error** | Inline error toast + retry button |
| **Success** | Animated data cards with staggered reveal |

### 9.4 Data Display Components

- **SkillLevelBadge** — Color-coded level indicator (0–5 scale)
- **EvidenceCard** — Evidence item with verification status badge
- **RoadmapTimeline** — Phased roadmap with progress bars
- **HealthRadar** — Radar chart for skill health dimensions
- **OpportunityMatchCard** — Match score with gap pills

---

## 10. Future Roadmap

| Quarter | Feature | Description |
|---|---|---|
| Q3 2026 | **Skill Graph Visualization** | Interactive D3.js graph showing skill relationships, prerequisite chains, and user skill cluster |
| Q3 2026 | **GitHub Import** | Auto-detect skills from public GitHub repos (languages, frameworks, tools) |
| Q4 2026 | **Skill Forecasting** | ML-based forecasting of skill demand and salary trends over 1–5 year horizons |
| Q4 2026 | **Peer Benchmarking** | Anonymized skill level comparison against peer cohort (with opt-in) |
| Q1 2027 | **AI-Assisted Skill Discovery** | Autonomous skill suggestion based on browsing/bookmark analysis |
| Q1 2027 | **Certification Integration** | Direct badge/certification import from Credly, Coursera, LinkedIn |
| Q2 2027 | **Team Skills Dashboard** | (Multi-user) Team skill matrix for collaborative projects |
| Q2 2027 | **Skill-Based Project Matching** | Auto-suggest projects that exercise identified skill gaps |

---

## 11. Cross-References

| Document | Relevant Sections |
|---|---|
| `docs/engineering/12_Architecture.md` | System architecture, in-process agent model (ADR-004) |
| `docs/ai/20_Agent.md` | Full agent specification — ARIA orchestrator, agent registry (Section 9) |
| `docs/ai/prompt-engineering-guide.md` | Prompt structure guidelines, YAML frontmatter schema |
| `AGENTS.md` | Section 9 (AI Agent Architecture), Section 10 (Prompt System), Section 11 (Prompt Development Guide), Section 16 (Testing Standards) |
| `packages/ai/prompt_loader.py` | PromptLoader API — `get_agent()`, `render()`, `validate_frontmatter()` |
| `packages/ai/agents/skill_agent.py` | SkillAgent domain controller with all 9 sub-agent functions |
| `packages/database/schemas/skill.py` | Pydantic models for all 40+ skill tables and enums |
| `apps/api/app/api/skills.py` | FastAPI router — full CRUD + AI-triggered endpoints |
| `services/scheduler/main.py` | APScheduler configuration for 5 skill cron jobs |
| `prompts/agents/` | All 8 skill agent prompt files (7 AI-driven + 1 shared) |

---

*Document Version 1.0.0 — Last updated July 11, 2026. For questions, contact developer@secondbrain-os.com.*
