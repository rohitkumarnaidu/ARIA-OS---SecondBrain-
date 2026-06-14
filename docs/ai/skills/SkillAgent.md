
# SkillAgent — Skill Domain Controller & Agent Orchestrator

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-SKILLAGENT-ARCH-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-13 |
| Classification | Internal — Architecture Reference |
| Source of Truth | `docs/ai/skills/skills.md` (§1–§33, App A) |
| Companion Docs | `docs/ai/skills/SkillAssessment.md` (Assessment Engine) |
| | `docs/ai/skills/SkillEvidence.md` (Evidence Engine) |
| | `docs/ai/skills/SkillIntelligence.md` (Analytics Engine) |
| | `docs/ai/skills/SkillMarketIntelligence.md` (Market Engine) |
| | `docs/ai/skills/SkillRoadmapEngine.md` (Roadmap Engine) |
| | `docs/ai/skills/SkillOpportunityMatching.md` (Opportunity Engine) |
| | `docs/ai/skills/SkillGraphArchitecture.md` (Graph Engine) |
| Agent Registry Ref | `docs/ai/20_Agent.md` (A00–A14 Agent Specifications) |
| Target Audience | AI Agents, Engineers, Architects, Product Managers |

---

## Table of Contents

- [0. SkillAgent Overview](#0-skillagent-overview)
  - [0.1 Purpose](#01-purpose)
  - [0.2 Architecture Diagram](#02-architecture-diagram)
  - [0.3 Sub-Agent Spectrum](#03-sub-agent-spectrum)
  - [0.4 Relationship to ARIA OS](#04-relationship-to-aria-os)
- [1. Mission](#1-mission)
- [2. Responsibilities](#2-responsibilities)
- [3. Inputs](#3-inputs)
- [4. Outputs](#4-outputs)
- [5. Tools](#5-tools)
- [6. Memory Usage](#6-memory-usage)
- [7. Reasoning Flow](#7-reasoning-flow)
- [8. Context Building](#8-context-building)
- [9. Recommendation Logic](#9-recommendation-logic)
- [10. Escalation Rules](#10-escalation-rules)
- [11. Guardrails](#11-guardrails)
- [12. Observability](#12-observability)
- [13. KPIs](#13-kpis)
- [14. Evaluation Framework](#14-evaluation-framework)
- [15. Sub-Agent Deep Dives](#15-sub-agent-deep-dives)
  - [15.1 Skill Assessment Agent](#151-skill-assessment-agent)
  - [15.2 Skill Recommendation Agent](#152-skill-recommendation-agent)
  - [15.3 Skill Intelligence Agent](#153-skill-intelligence-agent)
  - [15.4 Skill Roadmap Agent](#154-skill-roadmap-agent)
  - [15.5 Skill Evidence Agent](#155-skill-evidence-agent)
  - [15.6 Skill Career Agent](#156-skill-career-agent)
  - [15.7 Skill Opportunity Agent](#157-skill-opportunity-agent)
  - [15.8 Skill Market Agent](#158-skill-market-agent)
  - [15.9 Skill Graph Agent](#159-skill-graph-agent)
- [16. Integration Patterns](#16-integration-patterns)
- [Appendix A: Glossary](#appendix-a-glossary)
- [Appendix B: Prompt File Specifications](#appendix-b-prompt-file-specifications)
- [Appendix C: Implementation Roadmap](#appendix-c-implementation-roadmap)
- [Appendix D: Relationship Map](#appendix-d-relationship-map)

---

## 0. SkillAgent Overview

### 0.1 Purpose

SkillAgent is the **Skill Domain Controller** — the single AI agent responsible for managing, reasoning about, and acting upon the user's entire skill ecosystem within ARIA OS. It serves as the intelligent layer between ARIA's orchestrator (A00) and the seven companion engine documents, orchestrating nine specialized sub-agents that together cover skill assessment, evidence validation, intelligence analysis, market monitoring, roadmap generation, opportunity matching, career planning, knowledge graph navigation, and personalized recommendations.

**Why a Dedicated Skill Agent?**

| Document | Role | Analogy |
|---|---|---|
| `skills.md` | Data model, formulas, and taxonomy | Constitution |
| `SkillAssessment.md` | Skill evaluation & level scoring | Exam Proctor |
| `SkillEvidence.md` | Evidence collection & verification | Private Investigator |
| `SkillIntelligence.md` | Analytics, scoring, and metrics | Data Analyst |
| `SkillMarketIntelligence.md` | Market data ingestion & trend analysis | Economist |
| `SkillRoadmapEngine.md` | Learning path generation & execution | GPS Navigator |
| `SkillOpportunityMatching.md` | Opportunity scoring & ranking | Headhunter |
| `SkillGraphArchitecture.md` | Graph storage & traversal | Cartographer |
| **SkillAgent** | **AI orchestration across all skill domains** | **Chief Strategy Officer** |

### 0.2 Architecture Diagram

```
                                    ┌──────────────────────────────────────┐
                                    │          ARIA Orchestrator (A00)     │
                                    │   (Intent classification, dispatch)   │
                                    └────────────────┬─────────────────────┘
                                                     │  skill_* intents
                                                     ▼
                                    ┌──────────────────────────────────────┐
                                    │         SKILLAGENT (SK-CORE)          │
                                    │   Skill Domain Controller & Reasoner  │
                                    │    (Context Builder + Recommender)    │
                                    └──┬───┬───┬───┬───┬───┬───┬───┬───┬──┘
                                       │   │   │   │   │   │   │   │   │
            ┌──────────────────────────┼───┼───┼───┼───┼───┼───┼───┼───┼──────────────┐
            ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼                  │
       ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐ │
       │  SK-01 ││  SK-02 ││  SK-03 ││  SK-04 ││  SK-05 ││  SK-06 ││  SK-07 ││  SK-08 │ │
       │Assess- ││Recom-  ││Intelli-││Roadmap ││Evidence││ Career ││Opportu-││ Market │ │
       │ ment   ││mendation││ gence  ││        ││        ││        ││ nity   ││        │ │
       └───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘ │
           │         │         │         │         │         │         │         │       │
           └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴───┐   │
                                                                                      │   │
            ┌──────────┐                                                             │   │
            │  SK-09   │  Skill Graph Agent (cross-cutting — serves all sub-agents)  │   │
            │  Graph   │◀─────────────────────────────────────────────────────────────┘   │
            └──────────┘                                                                 │
                                                                                         │
            ┌────────────────────────────────────────────────────────────────────────────┘
            ▼
    ┌───────────────────────────────────────────────┐
    │          7 Companion Engine Documents          │
    │   (Algorithmic engines — no LLM dependency)    │
    └───────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────────┐
    │     Supabase DB (skills, evidence, market,    │
    │     assessments, roadmaps, opportunities)      │
    └───────────────────────────────────────────────┘
```

### 0.3 Sub-Agent Spectrum

SkillAgent orchestrates **9 sub-agents** organized into two tiers:

**5 Main Sub-Agents (Core Domain):**

| ID | Agent | Primary Role | LLM Dep | Engine Doc | Status |
|---|---|---|---|---|---|
| SK-01 | Skill Assessment Agent | Skill evaluation, level scoring, readiness | Yes | `SkillAssessment.md` | Design |
| SK-02 | Skill Recommendation Agent | What to learn/improve/drop/emerge | Yes | `skills.md` §20 | Design |
| SK-03 | Skill Intelligence Agent | Analytics, growth velocity, career readiness | Yes | `SkillIntelligence.md` | Design |
| SK-04 | Skill Roadmap Agent | Learning path generation, milestone tracking | Yes | `SkillRoadmapEngine.md` | Design |
| SK-05 | Skill Evidence Agent | Evidence collection, quality scoring, fraud detection | Yes | `SkillEvidence.md` | Design |

**4 Additional Sub-Agents (Supporting Domain):**

| ID | Agent | Primary Role | LLM Dep | Engine Doc | Status |
|---|---|---|---|---|---|
| SK-06 | Skill Career Agent | Career readiness, trajectory, job targeting | Yes | `skills.md` §19 | Design |
| SK-07 | Skill Opportunity Agent | Skill-opportunity matching, application ranking | Yes | `SkillOpportunityMatching.md` | Design |
| SK-08 | Skill Market Agent | Market data ingestion, trend analysis, salary bench | No | `SkillMarketIntelligence.md` | Design |
| SK-09 | Skill Graph Agent | Graph traversal, relationship discovery, pathfinding | No | `SkillGraphArchitecture.md` | Design |

### 0.4 Relationship to ARIA OS

SkillAgent registers with ARIA (A00) as a **skill-domain router**. When ARIA detects a `skill_*` intent in a user message, it dispatches to SkillAgent rather than handling it directly. SkillAgent then:

1. **Classifies** the specific sub-domain (assessment, recommendation, roadmap, etc.)
2. **Assembles context** from the relevant engine documents and user profile
3. **Dispatches** to the appropriate sub-agent (or handles directly for simple queries)
4. **Synthesizes** the sub-agent's output into a natural-language response
5. **Persists** key data back into the skill system (new skills, updated levels, evidence records)

**Trigger Matrix:**

| Trigger | Example Intent | SK Handler | LLM Needed |
|---|---|---|---|
| User Chat | "What skills should I learn next?" | SK-02 Recommendation | Yes |
| User Chat | "Assess my Python skill" | SK-01 Assessment | Yes |
| User Chat | "Am I ready for senior roles?" | SK-06 Career | Yes |
| User Chat | "Find internships matching my skills" | SK-07 Opportunity | Yes |
| Cron (Daily) | Refresh market intelligence | SK-08 Market | No |
| Cron (Weekly) | Generate skill growth report | SK-03 Intelligence | Yes |
| Cron (Weekly) | Review evidence for expiry | SK-05 Evidence | No |
| Cron (On-demand) | Sync skill graph dependencies | SK-09 Graph | No |
| API Call | Submit evidence for review | SK-05 Evidence | Yes |
| API Call | Generate learning roadmap | SK-04 Roadmap | Yes |


---

## 1. Mission

SkillAgent maximizes the user's career and skill-growth trajectory by intelligently orchestrating skill assessments, evidence validation, intelligence analysis, market monitoring, roadmap generation, opportunity matching, career planning, and personalized recommendations — bridging the gap between the user's current skill state and their aspirational future state through AI-powered reasoning over the full ARIA OS skills ecosystem.

---

## 2. Responsibilities

SkillAgent owns 12 primary responsibilities across the skills domain:

| # | Responsibility | Owner | LLM? | Frequency | Engine Doc |
|---|---|---|---|---|---|
| R01 | Classify incoming skill intents and dispatch to the correct sub-agent | SkillAgent Core | Yes | Per request | — |
| R02 | Maintain a unified user skill profile (current skills, levels, evidence, targets) | SkillAgent Core | No | Continuous | `skills.md` §7 |
| R03 | Execute skill assessments — evaluate user skill levels via AI-driven tests | SK-01 Assessment | Yes | On-demand | `SkillAssessment.md` |
| R04 | Validate evidence submissions — verify authenticity, score quality, assign levels | SK-05 Evidence | Yes | On-demand | `SkillEvidence.md` |
| R05 | Generate skill recommendations — what to learn, improve, drop, or watch | SK-02 Recommendation | Yes | Daily + On-demand | `skills.md` §20 |
| R06 | Build and optimize learning roadmaps — sequenced milestones with time estimates | SK-04 Roadmap | Yes | Weekly + On-demand | `SkillRoadmapEngine.md` |
| R07 | Compute intelligence scores — growth velocity, career readiness, opportunity match, income potential | SK-03 Intelligence | Yes | Weekly | `SkillIntelligence.md` |
| R08 | Match user skills to external opportunities — score, rank, recommend | SK-07 Opportunity | Yes | Daily | `SkillOpportunityMatching.md` |
| R09 | Assess career readiness — identify gaps, recommend next roles, plot trajectory | SK-06 Career | Yes | Weekly + On-demand | `skills.md` §19 |
| R10 | Track market intelligence — demand trends, salary benchmarks, emerging skills | SK-08 Market | No | Daily | `SkillMarketIntelligence.md` |
| R11 | Maintain the skill knowledge graph — relationships, prerequisites, dependencies | SK-09 Graph | No | Continuous | `SkillGraphArchitecture.md` |
| R12 | Persist all skill-related data to Supabase with user-scoped RLS | All sub-agents | No | Per action | `skills.md` §24 |

**Responsibility-to-Sub-Agent Matrix:**

```
                    SK-01  SK-02  SK-03  SK-04  SK-05  SK-06  SK-07  SK-08  SK-09
R01 Classify          │      │      │      │      │      │      │      │      │
R02 Profile Mgmt      │      │      │      │      │      │      │      │      │
R03 Assessment        ◆      │      │      │      │      │      │      │      │
R04 Evidence           │      │      │      │     ◆      │      │      │      │
R05 Recommend          │     ◆      │      │      │      │      │      │      │
R06 Roadmap            │      │      │     ◆      │      │      │      │      │
R07 Intelligence       │      │     ◆      │      │      │      │      │      │
R08 Opportunity        │      │      │      │      │      │     ◆      │      │
R09 Career             │      │      │      │      │     ◆      │      │      │
R10 Market             │      │      │      │      │      │      │     ◆      │
R11 Graph              │      │      │      │      │      │      │      │     ◆
R12 Persistence        │      │      │      │      │      │      │      │      │

◆ = Primary owner | │ = Cross-cutting dependency
```

---

## 3. Inputs

### 3.1 Input Channels

| Source | Format | Volatility | Description |
|---|---|---|---|
| **User Message** | Natural language (via A00) | Per-request | Direct queries: assess, recommend, compare, analyze |
| **Cron Scheduler** | JSON event payload | Scheduled (daily/weekly) | Recurring triggers: briefings, reviews, market refresh |
| **API Call** | JSON/Form data | On-demand | Evidence submissions, assessment triggers, data syncs |
| **Companion Engine Docs** | Markdown (prompt-embedded) | Versioned | 7 algorithmic engines providing structured data |
| **Supabase DB** | PostgreSQL rows | Real-time | User skills, assessments, evidence, market data, roadmaps |
| **PromptLoader** | YAML frontmatter + body | Versioned | System prompts, agent prompts, template prompts |
| **External APIs** | JSON (REST) | Varies | Market data sources, job boards, certification providers |

### 3.2 Input Data Model (Simplified)

```python
@dataclass
class SkillAgentInput:
    intent: SkillIntent  # assess | recommend | roadmap | evidence | intelligence | career | opportunity | market | graph
    user_id: str
    user_message: str | None = None
    sub_agent_target: str | None = None  # Specific agent to route to
    parameters: dict = field(default_factory=dict)  # Intent-specific params
    context: dict = field(default_factory=dict)  # Pre-assembled context
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### 3.3 Key Database Dependencies

| Table | Sub-Agent(s) | Purpose |
|---|---|---|
| `user_skills` | All | Current skill inventory with levels and confidence |
| `skill_targets` | SK-02, SK-04, SK-06 | Target skills with timelines |
| `skill_assessments` | SK-01 | Assessment history and scores |
| `skill_evidence` | SK-05 | Evidence records with quality scores |
| `skill_roadmaps` | SK-04 | Generated learning roadmaps |
| `skill_intelligence_scores` | SK-03 | Computed analytics scores |
| `skill_market_data` | SK-03, SK-08 | Market demand, salary, trends |
| `skill_opportunities` | SK-07 | External opportunity matches |
| `skill_graph_edges` | SK-09 | Skill relationship graph |
| `skill_events` | All | Audit log of skill actions |

---

## 4. Outputs

### 4.1 Output Channels

| Destination | Format | Description |
|---|---|---|
| **User (via ARIA)** | Natural language | Assessment results, recommendations, roadmaps, answers |
| **Supabase DB** | SQL INSERT/UPDATE | All skill data: assessments, evidence, scores, profiles |
| **PromptLoader** | YAML + Markdown | Generated/updated prompt files for sub-agents |
| **ARIA Memory (A02)** | Structured event | Skill acquisitions, level-ups, evidence records |
| **Notification System** | JSON | Skill milestones, deadline reminders, market alerts |
| **Analytics Pipeline** | Structured event | KPIs, usage metrics, recommendation feedback |

### 4.2 Output Data Types

```python
@dataclass
class SkillAgentOutput:
    response_type: SkillResponseType
    user_message: str
    data: dict  # Structured data for persistence
    sub_agent_results: list[dict] = field(default_factory=list)
    confidence: float = 1.0
    requires_human_review: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

# Response types
SkillResponseType = Enum(
    "SkillResponseType",
    "ASSESSMENT_RESULT RECOMMENDATION ROADMAP CAREER_ANALYSIS "
    "EVIDENCE_RESULT OPPORTUNITY_MATCH MARKET_INTEL GRAPH_QUERY ERROR"
)
```

---

## 5. Tools

### 5.1 Core Tools (SkillAgent Main)

| Tool | Parameters | Returns | Description |
|---|---|---|---|
| `classify_intent()` | message: str | `SkillIntent` | Classifies user message into skill sub-domain |
| `assemble_context()` | user_id, intent | `ContextBundle` | Assembles all necessary context from DB + engines |
| `dispatch_to_sub_agent()` | agent_id, context | `SubAgentResult` | Routes to correct sub-agent with context |
| `synthesize_response()` | results: list | str | Combines sub-agent outputs into natural response |
| `persist_to_db()` | data: dict | bool | Writes structured data to Supabase |
| `notify_aria_memory()` | event: dict | bool | Logs skill events to ARIA's memory system |

### 5.2 Sub-Agent Tools

Each sub-agent exposes tools that SkillAgent can invoke directly:

| Tool | Owner | Parameters | Description |
|---|---|---|---|
| `assess_skill()` | SK-01 | user_id, skill_id, method | Run a skill assessment for a specific skill |
| `score_evidence()` | SK-05 | evidence_id | Score submitted evidence for quality and level |
| `recommend_skills()` | SK-02 | user_id, strategy, top_k | Generate skill development recommendations |
| `build_roadmap()` | SK-04 | user_id, target_skills, timeline | Generate a sequenced learning roadmap |
| `compute_intelligence()` | SK-03 | user_id | Refresh all intelligence scores |
| `match_opportunities()` | SK-07 | user_id, opp_type, top_k | Find and rank external opportunities |
| `assess_career_readiness()` | SK-06 | user_id, target_role | Evaluate readiness for a career target |
| `refresh_market_data()` | SK-08 | skill_ids | Fetch latest market intelligence |
| `query_graph()` | SK-09 | query_type, params | Navigate the skill knowledge graph |
| `find_shortest_path()` | SK-09 | from_skill, to_skill | Discover shortest learning path |

### 5.3 Cross-Cutting Tools

| Tool | Owner | Description |
|---|---|---|
| `validate_frontmatter()` | PromptLoader | Validates prompt YAML frontmatter |
| `render_prompt()` | PromptLoader | Renders a prompt template with variables |
| `get_user_profile()` | ARIA Core | Fetches full user profile |
| `log_analytics_event()` | Analytics Pipeline | Logs KPI-relevant events |
| `send_notification()` | Notification System | Sends push/email notification |
| `cache_get/set()` | TTL Cache | 15-min TTL cache for frequent queries |

---

## 6. Memory Usage

### 6.1 Memory Architecture

SkillAgent uses a four-tier memory model:

```
Tier 1: Working Memory (session-scoped)
  └── Current conversation context, active skill being assessed, pending recommendations

Tier 2: Episodic Memory (interaction-scoped)
  └── Past skill recommendations (what was recommended, was it followed, outcome)
  └── Assessment history (last 10 assessments per skill)
  └── Evidence reviews (last 20 evidence submissions)

Tier 3: Semantic Memory (user-scoped, persistent)
  └── User skill inventory (current levels, confidence scores)
  └── Skill targets and learning goals
  └── Career trajectory and preferences
  └── Past recommendation outcomes (accepted/rejected/delayed)

Tier 4: Global Memory (system-scoped)
  └── Skill taxonomy (all canonical skills, tree structure)
  └── Market intelligence data (demand trends, salary benchmarks)
  └── Companion engine configurations and formulas
```

### 6.2 Memory Storage

| Memory Type | Storage | Retention | TTL | Scope |
|---|---|---|---|---|
| Working | In-memory (Python dict) | Session | < 30 min | Per request |
| Episodic | TTL Cache (TTLCache) | Rolling | 24 hours | Per user |
| Semantic | Supabase (skill tables) | Permanent | — | Per user |
| Global | Supabase + In-memory cache | Permanent | 1 hour (cache) | System-wide |

### 6.3 Memory Key Schema

```python
MEMORY_KEYS = {
    "working":     f"sk:w:{user_id}:{session_id}",
    "episodic":    f"sk:e:{user_id}:assessment_latest:{skill_id}",
    "episodic":    f"sk:e:{user_id}:recommendation_history",
    "episodic":    f"sk:e:{user_id}:evidence_reviews",
    "semantic":    f"sk:s:{user_id}:profile",
    "semantic":    f"sk:s:{user_id}:targets",
    "semantic":    f"sk:s:{user_id}:career_prefs",
    "global":      f"sk:g:taxonomy",
    "global":      f"sk:g:market_insights",
    "global":      f"sk:g:engine_configs"
}
```

### 6.4 Memory Update Triggers

| Trigger | Memory Updated | Sub-Agent |
|---|---|---|
| Assessment completed | Episodic: assessment history; Semantic: skill level | SK-01 |
| Evidence validated | Episodic: evidence review; Semantic: skill confidence | SK-05 |
| Recommendation generated | Episodic: recommendation history | SK-02 |
| Roadmap generated | Semantic: current roadmap, milestones | SK-04 |
| Intelligence scores computed | Semantic: growth velocity, readiness scores | SK-03 |
| Career analysis performed | Semantic: career trajectory, gap list | SK-06 |
| Opportunity matched | Episodic: opportunity history | SK-07 |
| Market data refreshed | Global: market intelligence cache | SK-08 |
| Graph updated | Global: graph edges and nodes | SK-09 |


---

## 7. Reasoning Flow

### 7.1 Top-Level Reasoning Chain

When SkillAgent receives a request, it follows this reasoning chain:

```
Step 1: Intent Classification
  ├── Parse user message + extract entities (skill names, levels, timeframes)
  ├── Map to SkillIntent (assess | recommend | roadmap | evidence | intelligence | career | opportunity | market | graph)
  ├── Identify target skills, target levels, and any constraints
  └── Confidence: [0.0-1.0] → If < 0.7, ask clarifying question

Step 2: Context Assembly
  ├── Fetch user profile (current skills, levels, evidence, targets)
  ├── Fetch relevant historical data (past assessments, recommendations, outcomes)
  ├── Fetch engine-specific configuration (scoring profiles, thresholds, weight matrices)
  └── Bundle into ContextPackage → pass to sub-agent

Step 3: Sub-Agent Dispatch
  ├── Route to the appropriate sub-agent (SK-01 through SK-09)
  ├── Sub-agent executes its specialized reasoning chain (see §15)
  ├── Sub-agent returns structured result + confidence + evidence
  └── Handle timeout (5s) → fallback to algorithmic approximation

Step 4: Synthesis
  ├── Merge sub-agent result with user context
  ├── Apply guardrails (see §11)
  ├── Format as natural language response
  └── Include: primary answer, confidence, data sources, next steps

Step 5: Persistence & Feedback
  ├── Write structured data to Supabase (assessments, scores, recommendations)
  ├── Notify ARIA Memory (A02) of significant skill events
  ├── Log analytics event for KPI tracking
  └── Cache result (if applicable) with TTL
```

### 7.2 Reasoning Chain Visualization

```
User: "What skills should I learn to become a senior ML engineer?"
  │
  ▼
┌─────────────────────────────────────────────┐
│ Step 1: Classify Intent                      │
│   Intent → Career Analysis (SK-06)           │
│   Entities: ["senior ML engineer"]           │
│   Sub-intent: skill_gap + recommendation     │
│   Confidence: 0.92                           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Step 2: Assemble Context                     │
│   User skills: [Python L4, PyTorch L3, ...] │
│   Target role: Senior ML Engineer            │
│   Market data: Demand high (+34% YoY)        │
│   Career engine config: readiness weights   │
│   Past recs: ["Learn Kubernetes"] (pending)  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Step 3: Sub-Agent Dispatch                   │
│   Primary: SK-06 (Career)                    │
│   Secondary: SK-02 (Recommendation)          │
│   Supporting: SK-03 (Intelligence - trends)  │
│   SK-09 (Graph - prerequisite chain)         │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
     ┌────────┐┌────────┐┌────────┐
     │ SK-06  ││ SK-02  ││ SK-03  │
     │ Career ││Rec     ││ Intel  │
     │ Gap    ││ ommend ││ Trends │
     │ Analysis││ Skills ││ +Data  │
     └───┬────┘└───┬────┘└───┬────┘
         │         │         │
         └─────────┼─────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 4: Synthesize                           │
│   Gaps: [MLOps L3, Kubernetes L3, AWS L4]   │
│   Recs: [Learn MLOps (8w), K8s (6w)]        │
│   Market: Demand rising, salary $180K+      │
│   Roadmap: 3-phase, 24-week plan             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Step 5: Persist & Log                        │
│   Save gap analysis to skill_targets        │
│   Save recommendation set to skill_events   │
│   Notify A02 of career milestone interest   │
│   Log analytics: career_analysis_completed  │
│   Cache: 15-min TTL                         │
└─────────────────────────────────────────────┘
```

### 7.3 Decision Tree: Intent Classification

```
User Message Received
  │
  ├── Contains "assess", "evaluate", "test my"?
  │     └──→ SK-01 Assessment Agent
  │
  ├── Contains "recommend", "what should I learn", "next skill"?
  │     └──→ SK-02 Recommendation Agent
  │
  ├── Contains "roadmap", "learning path", "how to become", "plan"?
  │     └──→ SK-04 Roadmap Agent
  │
  ├── Contains "evidence", "certificate", "prove", "portfolio"?
  │     └──→ SK-05 Evidence Agent
  │
  ├── Contains "growth", "progress", "velocity", "analytics"?
  │     └──→ SK-03 Intelligence Agent
  │
  ├── Contains "career", "promotion", "senior", "role", "job"?
  │     └──→ SK-06 Career Agent
  │
  ├── Contains "opportunity", "internship", "job match", "hackathon"?
  │     └──→ SK-07 Opportunity Agent
  │
  ├── Contains "market", "trend", "salary", "demand", "in demand"?
  │     └──→ SK-08 Market Agent
  │
  ├── Contains "graph", "relationship", "dependency", "prerequisite", "path"?
  │     └──→ SK-09 Graph Agent
  │
  └── Ambiguous or multi-intent?
        └──→ Route to SkillAgent Core → ask clarifying question
              "I see you're asking about skills. Would you like me to..."
              "...assess your current skills?"
              "...recommend what to learn next?"
              "...build a career roadmap?"
              "...or check market trends?"
```

### 7.4 Multi-Agent Coordination

When a request spans multiple sub-domains, SkillAgent runs a **coordinated dispatch**:

```python
async def coordinated_dispatch(user_id: str, intent: SkillIntent, context: ContextPackage):
    # Determine which sub-agents to invoke
    agents = coordination_matrix[intent]
    # Run independent agents in parallel
    results = await asyncio.gather(
        *[invoke_agent(a, user_id, context) for a in agents if a.parallel],
        return_exceptions=True
    )
    # Run dependent agents sequentially
    for agent in agents:
        if not agent.parallel and agent not in [a for a in agents if a.parallel]:
            results.append(await invoke_agent(agent, user_id, context))
    return results
```

**Coordination Matrix:**

| Primary Intent | Parallel Agents | Sequential Agents | Explanation |
|---|---|---|---|
| assess (SK-01) | SK-09 (graph deps) | — | Assessment may need prerequisite chain |
| recommend (SK-02) | SK-03 (trends), SK-08 (market), SK-09 (graph) | SK-06 (career goals) | Needs trends + market + career alignment |
| roadmap (SK-04) | SK-09 (shortest path) | SK-02 (skill sequence) | Builds on recommendation sequence |
| career (SK-06) | SK-03 (readiness), SK-08 (market), SK-07 (opps) | SK-02 (gap recs), SK-04 (roadmap) | Full pipeline: gaps → recs → roadmap |

---

## 8. Context Building

### 8.1 Context Package Structure

```python
@dataclass
class ContextPackage:
    # User Information
    user_id: str
    user_skills: dict[str, SkillLevel]        # Current skill inventory
    user_targets: list[SkillTarget]            # Target skills with deadlines
    user_career_prefs: CareerPreferences       # Career goals, preferred roles
    user_history: UserHistory                  # Past assessments, recs, outcomes

    # System Information
    skill_taxonomy: SkillTaxonomy              # Canonical skill tree
    market_data: MarketSnapshot                # Demand trends, salary data
    engine_configs: dict[str, EngineConfig]    # Per-engine configurations

    # Request Information
    intent: SkillIntent
    entities: list[ExtractedEntity]            # Parsed from user message
    constraints: dict                          # Time, difficulty, budget constraints

    # Metadata
    assembled_at: datetime
    cache_buster: str                          # For cache invalidation
    debug_mode: bool = False

    def is_stale(self, max_age_seconds: int = 300) -> bool:
        return (datetime.utcnow() - self.assembled_at).seconds > max_age_seconds
```

### 8.2 Context Assembly Pipeline

```
Step 1: Identity Resolution
  └── Resolve user_id → fetch base profile from user_skills table
  └── Load user preferences (career targets, learning pace, available hours)

Step 2: Skill State Extraction
  └── SELECT * FROM user_skills WHERE user_id = :uid
  └── SELECT * FROM skill_targets WHERE user_id = :uid AND status = 'active'
  └── SELECT * FROM skill_assessments WHERE user_id = :uid ORDER BY created_at DESC LIMIT 50
  └── SELECT * FROM skill_evidence WHERE user_id = :uid AND status = 'verified'

Step 3: Historical Context
  └── SELECT * FROM skill_events WHERE user_id = :uid AND created_at > now() - interval '90 days'
  └── Load past recommendations with acceptance/rejection outcomes
  └── Load past roadmaps with completion status

Step 4: System Context
  └── Load skill taxonomy from global cache (or DB)
  └── Load market intelligence snapshot (demand, salary, trends)
  └── Load engine-specific configuration (weight matrices, thresholds)

Step 5: Entity Enrichment
  └── Extract skill canonical_ids from user message entities
  └── Resolve aliases via taxonomy mapper (e.g., "JS" → "javascript")
  └── Look up prerequisite chain for mentioned skills via SK-09

Step 6: Package Assembly
  └── Bundle everything into ContextPackage
  └── Add cache_buster (hash of all components)
  └── Set assembled_at timestamp
  └── Return for dispatch
```

### 8.3 Context Size Budget

| Component | Max Tokens | Priority | Cacheable |
|---|---|---|---|
| User skill inventory | 800 | High | Yes (5 min) |
| User targets | 300 | High | Yes (5 min) |
| Career preferences | 200 | Medium | Yes (15 min) |
| Past assessments (last 5) | 400 | Medium | Yes (30 min) |
| Past recommendations (last 10) | 500 | Medium | Yes (30 min) |
| Skill taxonomy (relevant subset) | 1000 | High | Yes (1 hour) |
| Market snapshot | 600 | Low | Yes (1 hour) |
| Engine configs | 400 | Low | Yes (1 hour) |
| **Total** | **~4200** | | |

**If context exceeds token budget:**
1. Trim market data first (least critical per-request)
2. Truncate past assessments to last 3
3. Truncate past recommendations to last 5
4. In extreme cases: use only user skills + taxonomy + intent

---

## 9. Recommendation Logic

### 9.1 Recommendation Framework (from skills.md §20)

SkillAgent's recommendation engine follows the five-pillar framework defined in skills.md §20:

```
Recommendation Output = f(current_skills, target_skills, market_data, career_goals, timeline)

Five Pillars:
  1. Skills to Learn    → New skills not yet acquired, high market demand
  2. Skills to Improve  → Existing skills below target level, room for growth
  3. Skills to Drop     → Low-demand skills, no longer aligned with career
  4. Emerging Skills    → Rising in market, early adopter advantage
  5. Opportunity Ready  → Skills sufficient for specific opportunities
```

### 9.2 Recommendation Algorithm

```python
async def generate_recommendations(user_id: str, strategy: str = "balanced") -> RecommendationSet:
    context = await assemble_context(user_id, SkillIntent.RECOMMEND)
    recs = []

    # Pillar 1: Skills to Learn
    learn_scores = {}
    for skill in context.skill_taxonomy.all_skills():
        if skill.canonical_id in context.user_skills:
            continue
        demand = context.market_data.demand.get(skill.canonical_id, 0)
        salary_impact = context.market_data.salary_boost.get(skill.canonical_id, 0)
        career_alignment = _career_alignment(skill, context.user_career_prefs)
        growth_rate = context.market_data.growth_rate.get(skill.canonical_id, 0)
        learn_scores[skill.canonical_id] = {
            "score": (0.35 * demand + 0.25 * salary_impact +
                      0.25 * career_alignment + 0.15 * growth_rate),
            "demand": demand,
            "salary_impact": salary_impact,
            "career_alignment": career_alignment,
            "growth_rate": growth_rate
        }
    recs.append(RecommendationPillar(
        name="learn",
        items=sorted(learn_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:5],
        reason="High market demand and career alignment"
    ))

    # Pillar 2: Skills to Improve
    improve_scores = {}
    for skill_id, skill_level in context.user_skills.items():
        target = context.user_targets.get(skill_id)
        target_level = target.target_level if target else skill_level.level + 1
        if skill_level.level >= target_level:
            continue
        gap = target_level - skill_level.level
        demand = context.market_data.demand.get(skill_id, 0)
        confidence_penalty = 1 - skill_level.confidence
        improve_scores[skill_id] = {
            "score": (0.30 * (gap / 5) + 0.30 * demand +
                      0.20 * confidence_penalty + 0.20 * _career_alignment_by_id(skill_id, context)),
            "current_level": skill_level.level,
            "target_level": target_level,
            "gap": gap
        }
    recs.append(RecommendationPillar(
        name="improve",
        items=sorted(improve_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:5],
        reason="Gap between current and target levels"
    ))

    # Pillar 3: Skills to Drop
    drop_scores = {}
    for skill_id, skill_level in context.user_skills.items():
        demand = context.market_data.demand.get(skill_id, 0.5)
        if demand > 0.6:
            continue
        career_relevance = _career_alignment_by_id(skill_id, context)
        last_used = skill_level.last_used_at
        months_since_use = (datetime.utcnow() - last_used).days / 30 if last_used else 12
        drop_scores[skill_id] = {
            "score": (0.40 * (1 - demand) + 0.30 * (1 - career_relevance) +
                      0.30 * min(months_since_use / 12, 1.0)),
            "demand": demand,
            "career_relevance": career_relevance,
            "months_unused": months_since_use
        }
    recs.append(RecommendationPillar(
        name="drop",
        items=sorted(drop_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:3],
        reason="Low market demand and career relevance"
    ))

    # Pillar 4: Emerging Skills
    emerging = []
    for skill in context.skill_taxonomy.all_skills():
        growth = context.market_data.growth_rate.get(skill.canonical_id, 0)
        maturity = context.market_data.maturity.get(skill.canonical_id, 1.0)
        if growth > 0.3 and maturity < 0.6 and skill.canonical_id not in context.user_skills:
            emerging.append({"skill": skill.canonical_id, "growth": growth, "maturity": maturity})
    recs.append(RecommendationPillar(
        name="emerging",
        items=sorted(emerging, key=lambda x: x["growth"], reverse=True)[:3],
        reason="Rapidly growing in market, early adopter window"
    ))

    # Pillar 5: Opportunity Ready
    ready = []
    for skill_id, skill_level in context.user_skills.items():
        threshold = context.engine_configs.get("opportunity_threshold", 3)
        if skill_level.level >= threshold:
            matches = await find_opportunities_for_skill(skill_id, context)
            if matches:
                ready.append({"skill": skill_id, "level": skill_level.level, "opportunities": len(matches)})
    recs.append(RecommendationPillar(
        name="opportunity_ready",
        items=sorted(ready, key=lambda x: x["level"], reverse=True)[:5],
        reason="Skills at levels sufficient for external opportunities"
    ))

    return RecommendationSet(pillars=recs, generated_at=datetime.utcnow())
```

### 9.3 Strategy Profiles

| Strategy | Learn Weight | Improve Weight | Drop Weight | Emerging Weight | Best For |
|---|---|---|---|---|---|
| **Balanced** | 0.25 | 0.25 | 0.15 | 0.20 | General use |
| **Aggressive** | 0.40 | 0.30 | 0.05 | 0.25 | Career pivot / fast growth |
| **Conservative** | 0.15 | 0.40 | 0.10 | 0.10 | Deepening expertise |
| **Market-Driven** | 0.35 | 0.15 | 0.20 | 0.30 | Maximizing employability |
| **Career-Focused** | 0.30 | 0.30 | 0.10 | 0.10 | Targeting specific role |

### 9.4 LLM Enhancement

The algorithmic scores serve as the base ranking. When LLM is available, SkillAgent re-ranks using:

```python
async def llm_enhance_recommendations(
    recs: RecommendationSet,
    user_context: ContextPackage
) -> RecommendationSet:
    prompt = render_prompt("skill_recommendation_enhancer", {
        "user_skills": user_context.user_skills,
        "market_data": user_context.market_data,
        "algorithmic_recs": recs.to_dict(),
        "strategy": user_context.user_career_prefs.recommendation_strategy
    })
    response = await llm.generate_json(prompt, max_tokens=2048)
    return RecommendationSet.from_llm_response(response, base_recs=recs)
```

Logic: algorithmic score (70%) + LLM refinement (30%) with LLM providing nuanced reasoning about skill synergies, career narrative, and learning sequencing that pure math cannot capture.

---

## 10. Escalation Rules

### 10.1 Escalation Matrix

| Condition | Escalation To | Action | Example |
|---|---|---|---|
| **Low confidence** (< 0.6) | ARIA A00 | Return clarifying question | "I'm not sure if you want an assessment or roadmap. Could you clarify?" |
| **Conflict detected** | Human Review Queue | Flag for manual review | Evidence contradicts prior assessment score |
| **Cross-domain intent** | ARIA A00 + multi-agent orchestration | Dispatch to multiple domain agents | "What's my overall productivity?" → Skills + Tasks + Habits |
| **System error** (DB down, API timeout) | ARIA A00 | Return graceful degradation message | "I'm having trouble accessing your skill data. Please try again." |
| **Guardrail violation** | ARIA A00 + Audit Log | Reject request, log violation | User requests skill rating manipulation |
| **Data anomaly** (>3σ from baseline) | Admin Notification | Alert engineering team | Skill level jumps 4 levels in one day |
| **New skill discovery** | ARIA A00 + Taxonomy Admin | Flag for taxonomy expansion | User has a skill not in canonical taxonomy |
| **Repeated failure** (>3 in 10 min) | Circuit Breaker (SK-agent) | Disable sub-agent, auto-recover after 60s | Evidence agent timeout 3x in a row |

### 10.2 Escalation Flow

```
                    ┌───────────────────────┐
                    │ SkillAgent Processing  │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Check Exit Conditions │
                    │ ┌───────────────────┐ │
                    │ │ Confidence >= 0.6 │ │──→ Normal path
                    │ │ No conflicts     │ │
                    │ │ No errors        │ │
                    │ └───────────────────┘ │
                    └───────────┬───────────┘
                                │ (exit condition met)
                                ▼
                    ┌───────────────────────┐
                    │ Check For Escalation   │
                    │ ┌───────────────────┐ │
                    │ │ Confidence < 0.6? │ │──→ Escalate to A00 (clarification)
                    │ │ Conflict?         │ │──→ Escalate to Human Review
                    │ │ System error?     │ │──→ Escalate to A00 (degradation)
                    │ │ Guardrail breach? │ │──→ Escalate to Audit + Reject
                    │ └───────────────────┘ │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Execute Escalation    │
                    │ └────────────────────┘
                    │
                    ▼
            ┌───────────────────┐
            │  Return Response   │
            │  + Escalation Log  │
            └───────────────────┘
```

### 10.3 Human Review Criteria

| Criterion | Auto-Trigger | Review Turnaround | Reviewer |
|---|---|---|---|
| Evidence contradicts assessment | Score diff > 2 levels | < 4 hours | Skill Admin |
| User-reported accuracy issue | 3+ flags on same assessment | < 24 hours | Quality Team |
| Taxonomy missing skill | Not found in any canonical branch | < 1 week | Taxonomy Admin |
| Fraud suspicion | Evidence fraud score > 0.8 | < 2 hours | Security Team |
| Career escalation | User requests manager involvement | < 1 hour | HR / Manager |


---

## 11. Guardrails

### 11.1 Hard Guardrails (Enforced, Cannot Be Overridden)

| # | Guardrail | Rationale | Enforcement | Violation Action |
|---|---|---|---|---|
| G01 | Never assign a skill level higher than the highest quality evidence supports | Prevents skill inflation | Check: requested_level <= max(evidence_levels) | Clamp to max evidence level + log warning |
| G02 | Never recommend a skill above Level 5 (L5 = Expert) for a user below Level 3 | Prevents unrealistic roadmaps | Check: user's max level >= recommended_level - 2 | Filter out over-ambitious recommendations |
| G03 | Never fabricate evidence or assessment results | Integrity of skill system | Check: all evidence has source_id and verification_hash | Reject with error + audit log |
| G04 | Never expose one user's skill data to another user | Data privacy (RLS) | Check: all queries include user_id = auth.uid() | Block request + security alert |
| G05 | Never delete user skill history — only soft-delete (archive) | Audit trail | Check: DELETE queries rewritten to UPDATE status='archived' | Rewrite query + log |
| G06 | Never assess more than 10 skills per day per user without explicit opt-in | Rate limiting / fatigue | Check: count(assessments today) < 10 | Return "Daily limit reached" |
| G07 | Never recommend a skill the user has already mastered at that level | Avoid redundancy | Check: user's level >= recommendation level | Filter out + log |
| G08 | Never auto-enroll user in a paid course without explicit confirmation | Financial guard | Check: recommendation.cost > 0 → requires confirmation | Return "This course costs $X. Proceed?" |
| G09 | Never bypass human review for flagged evidence | Fraud prevention | Check: evidence.fraud_score > 0.7 → human_review = True | Hold in review queue |
| G10 | Never modify the canonical skill taxonomy automatically | Taxonomy integrity | Check: all taxonomy mutation requires admin token | Block with 403 |

### 11.2 Soft Guardrails (Advisory, Can Be Overridden with Reason)

| # | Guardrail | Rationale | Override Condition |
|---|---|---|---|
| S01 | Prefer skills with market demand > 0.5 over declining skills | Maximize ROI for user effort | User explicitly requests legacy skill |
| S02 | Keep learning roadmaps to ≤ 3 concurrent paths | Prevent overwhelm and context-switching | User explicitly requests more |
| S03 | Recommend evidence-backed skill levels for resumes | Credibility to external parties | User requests estimation (marked as "estimated") |
| S04 | Surface at most 5 recommendations per pillar | Information density | User requests "show me everything" |
| S05 | Prefer free resources over paid when quality is similar | Cost consideration | User explicitly requests premium content |

### 11.3 Guardrail Evaluation on Every Response

```python
GUARDRAIL_REGISTRY = {
    "assessment_level": {
        "check": lambda ctx, result: result.level <= max(e.level for e in ctx.user_evidence.get(result.skill_id, [])),
        "action": "clamp",
        "severity": "hard"
    },
    "no_fabrication": {
        "check": lambda ctx, result: result.has_verification_source,
        "action": "reject",
        "severity": "hard"
    },
    "rlz_check": {
        "check": lambda ctx, result: result.user_id == ctx.user_id,
        "action": "block",
        "severity": "hard"
    },
    "max_daily_assessments": {
        "check": lambda ctx, result: ctx.daily_assessment_count < 10,
        "action": "rate_limit",
        "severity": "hard"
    },
    "market_demand_minimum": {
        "check": lambda ctx, result: ctx.market_data.demand.get(result.skill_id, 0.5) > 0.3,
        "action": "warn",
        "severity": "soft"
    }
}

async def apply_guardrails(context: ContextPackage, result: SubAgentResult) -> GuardrailResult:
    violations = []
    for name, guardrail in GUARDRAIL_REGISTRY.items():
        if not guardrail["check"](context, result):
            violations.append(GuardrailViolation(
                guardrail=name,
                severity=guardrail["severity"],
                action=guardrail["action"],
                message=f"Guardrail {name} violated"
            ))
    if any(v.severity == "hard" and v.action == "reject" for v in violations):
        result.status = "rejected"
        result.guardrail_violations = violations
        logger.warning(f"[Guardrail] Hard violation: {violations}")
    elif any(v.severity == "hard" for v in violations):
        result = clamp_result(result, violations)
    if violations:
        result.guardrail_violations = violations
    return result
```

---

## 12. Observability

### 12.1 Logged Events

Every significant action across SkillAgent and its sub-agents produces a structured log event.

```python
# Event taxonomy
SKILL_EVENTS = {
    "intent_classified": {"fields": ["user_id", "intent", "confidence", "latency_ms"]},
    "context_assembled": {"fields": ["user_id", "component_count", "token_count", "latency_ms"]},
    "sub_agent_dispatched": {"fields": ["agent_id", "user_id", "intent", "latency_ms"]},
    "sub_agent_completed": {"fields": ["agent_id", "status", "confidence", "result_size"]},
    "sub_agent_failed": {"fields": ["agent_id", "error", "attempt", "fallback_used"]},
    "recommendation_generated": {"fields": ["user_id", "pillars", "total_items", "strategy"]},
    "assessment_completed": {"fields": ["user_id", "skill_id", "level", "confidence"]},
    "evidence_scored": {"fields": ["user_id", "evidence_id", "quality", "fraud_score"]},
    "roadmap_generated": {"fields": ["user_id", "milestones", "duration_days"]},
    "guardrail_violation": {"fields": ["guardrail", "severity", "action", "user_id"]},
    "escalation_triggered": {"fields": ["reason", "target", "user_id", "confidence"]},
    "cache_hit": {"fields": ["key_prefix", "ttl_remaining"]},
    "cache_miss": {"fields": ["key_prefix"]},
    "llm_call": {"fields": ["model", "tokens_in", "tokens_out", "latency_ms", "success"]},
    "db_query": {"fields": ["table", "operation", "rows_affected", "latency_ms"]}
}
```

### 12.2 Health Check Contract

```python
class SkillAgentHealth:
    @staticmethod
    async def health() -> dict:
        return {
            "status": "healthy" if all_green else "degraded",
            "version": "1.0.0",
            "sub_agents": {
                "SK-01": await check_sub_agent("SK-01"),
                "SK-02": await check_sub_agent("SK-02"),
                "SK-03": await check_sub_agent("SK-03"),
                "SK-04": await check_sub_agent("SK-04"),
                "SK-05": await check_sub_agent("SK-05"),
                "SK-06": await check_sub_agent("SK-06"),
                "SK-07": await check_sub_agent("SK-07"),
                "SK-08": await check_sub_agent("SK-08"),
                "SK-09": await check_sub_agent("SK-09"),
            },
            "db_connected": await check_db(),
            "llm_connected": await check_llm(),
            "cache_hit_ratio": cache.stats()["hit_ratio"],
            "uptime_seconds": (datetime.utcnow() - started_at).seconds
        }

    @staticmethod
    async def metrics() -> dict:
        return {
            "requests_total": counter["requests"],
            "requests_by_intent": counter["intents"],
            "avg_latency_ms": avg_latency(),
            "p95_latency_ms": p95_latency(),
            "sub_agent_latencies": sub_agent_latencies(),
            "guardrail_violations": counter["guardrail_violations"],
            "escalations": counter["escalations"],
            "cache_stats": cache.stats(),
            "llm_stats": llm.stats()
        }

    @staticmethod
    async def version() -> dict:
        return {
            "agent": "SkillAgent",
            "version": "1.0.0",
            "prompt_version": "1.0.0",
            "sub_agent_versions": {
                "SK-01": "1.0.0", "SK-02": "1.0.0", "SK-03": "1.0.0",
                "SK-04": "1.0.0", "SK-05": "1.0.0", "SK-06": "1.0.0",
                "SK-07": "1.0.0", "SK-08": "1.0.0", "SK-09": "1.0.0"
            },
            "dependencies": {
                "skills.md": "2.0.0",
                "SkillAssessment.md": "1.0.0",
                "SkillEvidence.md": "1.0.0",
                "SkillIntelligence.md": "1.0.0",
                "SkillMarketIntelligence.md": "1.0.0",
                "SkillRoadmapEngine.md": "1.0.0",
                "SkillOpportunityMatching.md": "1.0.0",
                "SkillGraphArchitecture.md": "1.0.0"
            }
        }
```

### 12.3 Tracing & Monitoring

| Signal | Method | Tool | Retention |
|---|---|---|---|
| Request tracing | OpenTelemetry spans | Jaeger / Zipkin | 7 days |
| Error tracking | Structured JSON logs | ELK / Grafana Loki | 30 days |
| Performance metrics | Prometheus gauges + histograms | Grafana | 90 days |
| Business KPIs | Custom counters → Prometheus | Grafana dashboard | 2 years (aggregated) |
| Audit trail | Supabase `skill_events` table | Direct DB query | 2 years |
| User feedback | Rating widget after recommendations | Supabase + Analytics | Permanent |
| LLM quality | Response sampling + human eval | Custom eval pipeline | 90 days |

### 12.4 Alert Rules

| Condition | Severity | Channel | Cooldown |
|---|---|---|---|
| P95 latency > 5s for 5 min | Critical | PagerDuty + Slack | 15 min |
| Error rate > 5% for 10 min | High | Slack | 30 min |
| Cache hit ratio < 0.5 | Medium | Slack | 60 min |
| Sub-agent down > 3 consecutive calls | High | Slack | 10 min |
| LLM success rate < 90% | Medium | Slack | 30 min |
| Guardrail violation rate > 1% of requests | Low | Weekly report | — |

---

## 13. KPIs

### 13.1 Core KPIs

| KPI | Target | Measurement | Frequency | Owner |
|---|---|---|---|---|
| **Recommendation Acceptance Rate** | > 60% | % of recommendations user follows (starts learning, adjusts target) | Weekly | SK-02 |
| **Assessment Accuracy** | > 85% | Correlation AI-assessed level vs human review | Monthly | SK-01 |
| **Evidence Quality Score** | > 0.75 | Average quality score of accepted evidence | Weekly | SK-05 |
| **Gap Closure Rate** | > 65% | % of identified skill gaps closed within estimated time | Monthly | SK-04 |
| **Career Readiness Accuracy** | > 80% | Predicted readiness vs actual placement success | Quarterly | SK-06 |
| **Intelligence Score Freshness** | > 95% | % of intelligence scores refreshed within SLA | Daily | SK-03 |
| **Opportunity Match Precision** | > 0.7 | Precision@10 for opportunity recommendations | Weekly | SK-07 |
| **Market Data Freshness** | > 98% | % of market data refreshed within 24h of source update | Daily | SK-08 |
| **Graph Query Latency P95** | < 100 ms | Response time for knowledge graph queries | Continuous | SK-09 |
| **User Satisfaction** | > 4.0 / 5.0 | Average rating of SkillAgent responses | Weekly | All |

### 13.2 Operational KPIs

| KPI | Target | Measurement | Frequency |
|---|---|---|---|
| **Request Latency P50** | < 1.5s | Median response time across all intents | Continuous |
| **Request Latency P95** | < 4.0s | 95th percentile response time | Continuous |
| **Request Latency P99** | < 8.0s | 99th percentile response time | Continuous |
| **LLM Success Rate** | > 95% | % of LLM calls that complete without error | Continuous |
| **Cache Hit Ratio** | > 0.70 | % of requests served from cache | Continuous |
| **Uptime** | > 99.5% | % of time all sub-agents are operational | Monthly |
| **Escalation Rate** | < 5% | % of requests that require human escalation | Weekly |
| **Guardrail Violation Rate** | < 0.5% | % of requests triggering hard guardrail | Weekly |

### 13.3 Business Impact KPIs

| KPI | Target | Measurement | Reporting |
|---|---|---|---|
| **Skill Growth Velocity** | +1.5 levels/user/quarter | Avg level increase across all skills | Quarterly report |
| **Time to Target** | < 12 weeks | Avg time from target creation to level achievement | Monthly |
| **Career Progression** | 1 role upgrade / 18 months | Avg time between career level advances | Annual |
| **Skill Portfolio Diversity** | > 5 categories | Avg number of skill categories with active targets | Monthly |
| **Learning ROI** | > 3x | Salary increase / hours invested in learning | Annual |

---

## 14. Evaluation Framework

### 14.1 Quality Dimensions

SkillAgent's output is evaluated across five dimensions:

| Dimension | Weight | Description | Measurement |
|---|---|---|---|
| **Accuracy** | 35% | Correctness of assessments, scores, recommendations | Compared against human expert review (sampled 10%) |
| **Relevance** | 25% | How well recommendations match user's goals and context | User rating (1-5) + follow-through rate |
| **Timeliness** | 15% | Responsiveness and freshness of data | Latency metrics + data staleness detection |
| **Explainability** | 15% | Clarity of reasoning behind recommendations | User survey "Did the explanation make sense?" |
| **Safety** | 10% | Absence of guardrail violations, privacy breaches | Automated guardrail pass rate |

### 14.2 Evaluation Cadence

| Evaluation Type | Frequency | Sample Size | Method | Owner |
|---|---|---|---|---|
| **Automated unit tests** | Per commit | 100% | pytest on all sub-agent logic | Engineering |
| **A/B testing** | Continuous | 10% traffic | Compare LLM vs algorithmic recommendations | ML Team |
| **Human expert review** | Weekly | 10% of assessments | Certified assessor double-checks AI scores | QA Team |
| **User satisfaction survey** | Per interaction | 5% sampled | 1-click rating after SkillAgent responses | Product |
| **Monthly quality audit** | Monthly | 5% of all outputs | Full audit across all 9 sub-agents | QA Team |
| **Quarterly calibration** | Quarterly | All sub-agents | Recalibrate scoring models vs new ground truth | ML Team |

### 14.3 A/B Testing Framework

```python
AB_TEST_CONFIG = {
    "recommendation_strategy": {
        "variants": ["algorithmic", "llm_boosted", "hybrid"],
        "traffic_split": [0.1, 0.1, 0.8],
        "metrics": ["acceptance_rate", "user_rating", "follow_through"],
        "min_duration_days": 14,
        "min_sample_size": 500
    },
    "assessment_method": {
        "variants": ["adaptive_quiz", "project_eval", "hybrid"],
        "traffic_split": [0.3, 0.3, 0.4],
        "metrics": ["accuracy", "user_completion", "time_to_complete"],
        "min_duration_days": 21,
        "min_sample_size": 200
    },
    "roadmap_format": {
        "variants": ["timeline", "dependency_graph", "hybrid"],
        "traffic_split": [0.25, 0.25, 0.5],
        "metrics": ["user_satisfaction", "roadmap_completion_rate"],
        "min_duration_days": 30,
        "min_sample_size": 100
    }
}

async def run_ab_test(variant: str, config: dict, user_id: str) -> str:
    assignment = hash(f"{user_id}:{config}") % 100
    cumulative = 0
    for v, split in zip(config["variants"], config["traffic_split"]):
        cumulative += split * 100
        if assignment < cumulative:
            return v
    return config["variants"][-1]
```

### 14.4 Bias Detection

```python
BIAS_CHECKS = {
    "demographic_parity": {
        "description": "Recommendation quality should not vary by user demographics",
        "method": "Compare avg rating across demographic groups",
        "threshold": "max_diff < 0.5",
        "action": "Recalibrate model if exceeded"
    },
    "skill_level_parity": {
        "description": "Novice users should get quality recommendations too",
        "method": "Compare recommendation acceptance rate by user level",
        "threshold": "max_diff < 0.2",
        "action": "Adjust recommendation algorithm for novice users"
    },
    "category_parity": {
        "description": "All skill categories should receive equal recommendation quality",
        "method": "Compare avg score by category (backend, frontend, AI/ML, etc.)",
        "threshold": "std_dev < 0.15",
        "action": "Audit skill tree for coverage gaps"
    },
    "temporal_bias": {
        "description": "No systematic preference for recently added skills",
        "method": "Correlate recommendation frequency with skill age",
        "threshold": "r < 0.3",
        "action": "Add decay factor to recommendation score"
    }
}
```

### 14.5 Feedback Loop

```
User Action ──→ Outcome Tracked ──→ Model Updated ──→ Next Interaction Improved
    │               │                    │                     │
    ▼               ▼                    ▼                     ▼
Recommendation  Followed? (Y/N)     Adjust weights in      Better recommendations
accepted        Skill improved?      recommendation         for similar future
                Assessment passed?   scoring algorithm      queries
                Evidence verified?


---

## 15. Sub-Agent Deep Dives

### 15.1 Skill Assessment Agent (SK-01)

#### Mission
Accurately evaluate a user's skill level through dynamic AI-powered assessment, returning a validated level with confidence score and evidence trail.

#### Capability Template (skills.md §21.2)

| Property | Value |
|---|---|
| Skill ID | `skill:assess` |
| Agent | SK-01 |
| Trigger | User Chat, API Call |
| Input | skill_id, assessment_method (quiz / project / hybrid) |
| Output | skill_level, confidence, evidence_ids, gaps |
| LLM Required | Yes |
| Prompt File | `prompts/agents/skill_assessment_agent.md` |
| Complexity | High |
| Status | Design |

#### Skill Steps
1. Parse assessment request → identify skill_id and method
2. Fetch current skill level + target level from user profile
3. Generate adaptive questions based on current level estimate
4. Score user responses using AI evaluation rubric (SkillAssessment.md §6)
5. Cross-reference with existing evidence (SkillEvidence.md)
6. Compute final level: algorithmic_score × 0.6 + llm_score × 0.4
7. Update user_skills table with new level + confidence
8. Log assessment event for analytics

#### Execution Diagram

```
Request: "Assess my Python"
  │
  ▼
┌─────────────────────────────┐
│ 1. Identify Skill           │ Python, canonical_id="python"
│    Current Level: L3        │ From user_skills
│    Target Level: L4         │ From skill_targets
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 2. Generate Questions        │
│    Method: hybrid            │
│    ┌─────────────────────┐  │
│    │ 5 MCQ (basic)       │  │
│    │ 3 Code (intermediate)│  │
│    │ 2 Design (advanced)  │  │
│    └─────────────────────┘  │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 3. Score Responses           │
│    MCQ: 4/5 correct          │
│    Code: 2/3 passing         │
│    Design: 1/2 strong        │
│    Algorithmic: 0.72         │
│    LLM Score: 0.78           │
│    Combined: 0.74 → L4       │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 4. Cross-reference Evidence  │
│    Found: 3 evidence items   │
│    Highest supports: L4      │
│    Confidence: 0.82          │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 5. Publish Result            │
│    Python: L3 → L4           │
│    Confidence: 0.82          │
│    Gaps: async/await,        │
│          decorators          │
└─────────────────────────────┘
```

#### Performance Metrics
| Metric | Target | Method |
|---|---|---|
| Assessment accuracy | > 85% | Human expert review (10% sample) |
| Time to complete | < 15 min | Average session duration |
| User satisfaction | > 4.0/5.0 | Post-assessment rating |
| Retake consistency | r > 0.9 | Correlation between retake scores |

---

### 15.2 Skill Recommendation Agent (SK-02)

#### Mission
Generate personalized, market-aligned skill development recommendations across five pillars — what to learn, improve, drop, watch as emerging, and leverage for opportunities.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:recommend` |
| Agent | SK-02 |
| Trigger | User Chat, Daily Cron |
| Input | user_id, strategy (balanced / aggressive / conservative / market-driven / career-focused) |
| Output | RecommendationSet with 5 pillars |
| LLM Required | Yes |
| Prompt File | `prompts/agents/skill_recommendation_agent.md` |
| Complexity | High |
| Status | Design |

#### Skill Steps
1. Load user profile (current skills, targets, career preferences)
2. Fetch market intelligence snapshot (demand, salary, growth rates)
3. Compute algorithmic scores for all 5 pillars (§9.2)
4. Apply strategy profile weights (§9.3)
5. LLM-enhance ranking with nuanced reasoning (§9.4)
6. Apply guardrails (no mastered skills, no over-ambitious targets)
7. Format as structured recommendation set with explanations
8. Log to skill_events + notify user (if cron trigger)

#### Improvement Signals (skills.md §21.5)
| Success Signal | Failure Signal | Adaptation |
|---|---|---|
| User starts learning recommended skill | User dismisses recommendation repeatedly | Lower weight for that skill category |
| Recommendation leads to level-up within timeline | User reports "already knew this" | Cross-check mastery level before recommending |
| High user rating (> 4) on recommendation | Low rating (< 2) | Flag for A/B test variant |

---

### 15.3 Skill Intelligence Agent (SK-03)

#### Mission
Compute and maintain real-time analytics scores across user's skill ecosystem — growth velocity, career readiness, opportunity match, and income potential.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:intelligence` |
| Agent | SK-03 |
| Trigger | Weekly Cron, User Chat (on-demand) |
| Input | user_id |
| Output | IntelligenceScores (4 scores + breakdowns) |
| LLM Required | Yes (for narrative interpretation) |
| Prompt File | `prompts/agents/skill_intelligence_agent.md` |
| Complexity | High |
| Status | Design |

#### Score Computation Pipeline

```
Compute Intelligence Scores for User
  │
  ├── 1. Growth Velocity
  │     v = Σ(level_change_i / months_i) / n
  │     Target: > 0.33 levels/month (1 level per quarter)
  │     → GrowthVelocity: 0.41 levels/month → "Above Average"
  │
  ├── 2. Career Readiness
  │     r = Σ(weight_i × readiness_i) / Σ(weight_i)
  │     readiness_i = 1.0 if level >= target, 0.5 if >= target-1, 0.0 otherwise
  │     → CareerReadiness: 0.72 → "Moderately Ready"
  │
  ├── 3. Opportunity Match
  │     m = max(match_score(opp_i, user_skills)) for all active opportunities
  │     → OpportunityMatch: 0.81 → "Strong Match"
  │
  └── 4. Income Potential
        i = Σ(potential_income(opp_type, level, demand)) / n
        → IncomePotential: $145K/yr → "Above Median"
```

#### Output Schema

```json
{
  "user_id": "user_001",
  "scores": {
    "growth_velocity": {"value": 0.41, "trend": "increasing", "percentile": 72},
    "career_readiness": {"value": 0.72, "target_role": "senior_backend", "gaps": 3},
    "opportunity_match": {"value": 0.81, "top_opportunities": ["..."]},
    "income_potential": {"value": 145000, "currency": "USD", "confidence": 0.65}
  },
  "narrative": "Your skill growth is above average at 0.41 levels/month. You're moderately ready for senior backend roles with 3 remaining gaps. Your skills match well with current market opportunities (0.81), and your income potential is estimated at $145K/yr.",
  "computed_at": "2026-06-13T00:00:00Z"
}
```

---

### 15.4 Skill Roadmap Agent (SK-04)

#### Mission
Generate optimized, personalized learning roadmaps that sequence skill acquisition in dependency order with realistic time estimates and milestone tracking.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:roadmap` |
| Agent | SK-04 |
| Trigger | User Chat, Weekly Cron |
| Input | user_id, target_skills, timeline_days, constraints |
| Output | Roadmap (phases, milestones, durations, resources) |
| LLM Required | Yes |
| Prompt File | `prompts/agents/skill_roadmap_agent.md` |
| Complexity | High |
| Status | Design |

#### Roadmap Generation Flow

```
User: "Build a roadmap to become a Senior AI Engineer"
  │
  ▼
┌───────────────────────────────────────────────┐
│ 1. Identify Target State                       │
│    Target: Senior AI Engineer                  │
│    Required Skills: [MLOps L4, K8s L3, AWS L4]│
│    Current Skills: [Python L4, PyTorch L3]    │
│    Gaps: [MLOps(L2), K8s(L0), AWS(L2)]        │
└──────────────────┬────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────┐
│ 2. Compute Dependency Order (via SK-09 Graph)  │
│    Python → ML Basics → PyTorch → MLOps → K8s │
│                           AWS ────────────────┘│
│    Critical Path: Python → MLOps (6 weeks)     │
└──────────────────┬────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────┐
│ 3. Generate Milestones                         │
│    Phase 1 (Weeks 1-4): MLOps Fundamentals     │
│      → Week 2: Complete MLOps course           │
│      → Week 4: Deploy first ML pipeline        │
│    Phase 2 (Weeks 5-10): Infrastructure        │
│      → Week 7: AWS SageMaker certification     │
│      → Week 10: Kubernetes deployment          │
│    Phase 3 (Weeks 11-14): Integration           │
│      → Week 12: End-to-end ML system           │
│      → Week 14: Production deployment          │
└──────────────────┬────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────┐
│ 4. Apply LLM Enhancement                      │
│    Add: Synergy notes, resource recommendations│
│    Adjust: Timeline based on user's available  │
│            hours (15h/week → 14 weeks → 24w)   │
└──────────────────┬────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────┐
│ 5. Save + Notify                               │
│    Save: skill_roadmaps table                  │
│    Notify: "Your AI Engineering roadmap is     │
│             ready! 3 phases, 24 weeks."        │
└───────────────────────────────────────────────┘
```

---

### 15.5 Skill Evidence Agent (SK-05)

#### Mission
Collect, verify, score, and manage skill evidence — ensuring every skill level claim has verifiable, quality-assessed supporting proof.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:evidence` |
| Agent | SK-05 |
| Trigger | User Chat, API Call (evidence submission) |
| Input | evidence_type, evidence_data (file/content), skill_id |
| Output | quality_score, fraud_score, verified_level, status |
| LLM Required | Yes (authenticity verification) |
| Prompt File | `prompts/agents/skill_evidence_agent.md` |
| Complexity | High |
| Status | Design |

#### Evidence Verification Pipeline

```
Evidence Submitted (certificate, project link, code sample, etc.)
  │
  ▼
┌──────────────────────────────────────────────┐
│ 1. Metadata Validation                       │
│    Check: file format, size, source URL      │
│    Check: issuer authenticity (if cert)      │
│    Result: PASS / FAIL / NEEDS_MANUAL        │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 2. LLM Authenticity Check                    │
│    Analyze: content for AI-generation signs  │
│    Check: consistency with claimed skill      │
│    Fraud Score: 0.0-1.0                      │
│    If > 0.7 → Flag for human review          │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 3. Quality Scoring (SkillEvidence.md §5)     │
│    Criteria: relevance, depth, recency,      │
│              originality, completeness       │
│    Quality Score: 0.0-1.0                    │
│    Level Supported: L3                       │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 4. Cross-Reference with Existing Evidence    │
│    Match: consistent with 2 prior items       │
│    Confidence Boost: 0.05                    │
│    Contradiction: 1 item suggests L2         │
│    → Set to L3 (majority) with note          │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 5. Finalize + Persist                        │
│    Status: verified                          │
│    Level: L3                                 │
│    Quality: 0.82                             │
│    Fraud: 0.12 (clean)                      │
│    → Update user_skills.confidence           │
│    → Log evidence event                      │
└──────────────────────────────────────────────┘
```

---

### 15.6 Skill Career Agent (SK-06)

#### Mission
Assess career readiness, identify skill gaps for target roles, and plot career trajectory with actionable milestones.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:career` |
| Agent | SK-06 |
| Trigger | User Chat, Weekly Cron |
| Input | user_id, target_role (optional) |
| Output | career_readiness_score, gap_analysis, trajectory |
| LLM Required | Yes |
| Prompt File | `prompts/agents/skill_career_agent.md` |
| Complexity | High |
| Status | Design |

#### Career Readiness Algorithm

```python
async def assess_career_readiness(user_id: str, target_role: str = None) -> CareerAssessment:
    context = await assemble_context(user_id, SkillIntent.CAREER)
    role = target_role or context.user_career_prefs.target_role
    if not role:
        return CareerAssessment(status="needs_target", message="What role are you targeting?")

    # Get role skill requirements (from skills.md §19 or external data)
    role_requirements = await get_role_requirements(role)

    # Compute readiness
    gaps = []
    total_weight = 0
    weighted_score = 0
    for req in role_requirements.required_skills:
        total_weight += req.weight
        user_skill = context.user_skills.get(req.canonical_id)
        if user_skill is None:
            weighted_score += 0
            gaps.append({"skill": req.canonical_id, "gap_type": "missing", "severity": "critical" if req.weight > 0.8 else "high"})
        elif user_skill.level < req.min_level:
            weighted_score += user_skill.level / req.min_level * req.weight
            gaps.append({"skill": req.canonical_id, "gap_type": "deficit", "from": user_skill.level, "to": req.min_level})
        else:
            weighted_score += req.weight

    readiness = weighted_score / total_weight if total_weight > 0 else 0

    return CareerAssessment(
        target_role=role,
        readiness_score=readiness,
        gaps=gaps,
        estimated_prep_time=_estimate_prep_time(gaps),
        next_milestones=_generate_milestones(role, readiness, gaps),
        trajectory=_plot_trajectory(context.user_skills, role_requirements)
    )
```

---

### 15.7 Skill Opportunity Agent (SK-07)

#### Mission
Match user's skill profile to external opportunities — jobs, internships, hackathons, fellowships, competitions, freelance, open source, startup programs, contracts, grants — using the SkillOpportunityMatching engine.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:opportunity` |
| Agent | SK-07 |
| Trigger | Daily Cron, User Chat |
| Input | user_id, opp_type (optional), top_k |
| Output | ranked_opportunities list with match scores |
| LLM Required | Yes |
| Prompt File | `prompts/agents/opportunity_matching_agent.md` |
| Complexity | High |
| Status | Design (engine complete) |

#### Integration Note
SK-07 is the AI layer over `SkillOpportunityMatching.md`. It:
1. Calls `ScoringEngine` for algorithmic primary scores
2. Calls `SuccessProbabilityModel` for secondary scores
3. Uses `AIRanker` (Level 1) for LLM-based ranking
4. Falls back to Level 5 (algorithmic) if LLM unavailable
5. Adds natural-language explanations for each opportunity

---

### 15.8 Skill Market Agent (SK-08)

#### Mission
Ingest, process, and maintain real-time market intelligence data — skill demand trends, salary benchmarks, emerging skill detection, and industry certification value.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:market` |
| Agent | SK-08 |
| Trigger | Daily Cron, On-demand API |
| Input | skill_ids (optional batch) |
| Output | MarketSnapshot (demand, salary, growth, maturity) |
| LLM Required | No (algorithmic pipeline) |
| Prompt File | N/A |
| Complexity | Medium |
| Status | Design |

#### Data Pipeline

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Job Boards    │  │ Freelance    │  │ Certification │
│ (LinkedIn,    │  │ Platforms    │  │ Providers     │
│  Indeed, etc) │  │ (Upwork, etc)│   │ (Coursera etc)│
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│ Ingestion Pipeline                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Scraper  │  │ API      │  │ RSS/Webhook      │  │
│  │ Engine   │  │ Consumer │  │ Listener          │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Normalization & Dedup                                │
│ → Extract skill mentions → Canonical ID mapping     │
│ → Aggregate demand frequency → Salary normalization │
│ → Trend computation (7, 30, 90 day windows)          │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ MarketSnapshot                                       │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│ │ Demand   │ │ Salary   │ │ Growth   │ │ Maturity│ │
│ │ Scores   │ │ Bench-   │ │ Rates    │ │ Scores  │ │
│ │          │ │ marks    │ │ (% YoY)  │ │ (0-1)   │ │
│ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└──────────────────────┬──────────────────────────────┘
                       ▼
                  ┌──────────┐
                  │ Supabase │
                  │ skill_   │
                  │ market_  │
                  │ data     │
                  └──────────┘
```

---

### 15.9 Skill Graph Agent (SK-09)

#### Mission
Maintain, query, and traverse the skill knowledge graph — discovering prerequisite chains, dependency relationships, learning paths, and skill clusters.

#### Capability Template

| Property | Value |
|---|---|
| Skill ID | `skill:graph` |
| Agent | SK-09 |
| Trigger | User Chat, Internal (sub-agent queries) |
| Input | query_type, params (from_skill, to_skill, max_depth, etc.) |
| Output | graph_path, relationships, metadata |
| LLM Required | No (algorithmic graph traversal) |
| Prompt File | N/A |
| Complexity | Medium |
| Status | Design |

#### Graph Operations

```python
class SkillGraphAgent:
    async def find_shortest_path(self, from_skill: str, to_skill: str, max_depth: int = 5) -> GraphPath:
        # BFS over skill_dependencies graph
        visited = set(); queue = deque([(from_skill, [from_skill])])
        while queue:
            node, path = queue.popleft()
            if node == to_skill: return GraphPath(path=path, length=len(path)-1)
            if len(path) > max_depth: continue
            for neighbor in await self.get_dependencies(node, direction="outgoing"):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return GraphPath(path=[], length=-1, error="No path found within depth limit")

    async def find_related_skills(self, skill_id: str, relationship: str = "all", max_results: int = 10) -> list[SkillRelation]:
        # Query graph for skills related via specified relationship type
        query = """MATCH (s:Skill {id: $sid})-[r]->(related)
                   WHERE r.type = $rel OR $rel = 'all'
                   RETURN related.id, r.type, r.weight
                   ORDER BY r.weight DESC LIMIT $limit"""
        return await self.graph_db.query(query, {"sid": skill_id, "rel": relationship, "limit": max_results})

    async def compute_skill_clusters(self, skill_ids: list[str]) -> list[SkillCluster]:
        # Community detection over subgraph
        query = """CALL algo.louvain.stream($ids, {
                      nodeProjection: 'Skill',
                      relationshipProjection: 'DEPENDS_ON'
                   }) YIELD nodeId, community
                   RETURN community, collect(algo.getNodeById(nodeId).id) as skills"""
        return await self.graph_db.query(query, {"ids": skill_ids})
```

#### Graph Schema

```
Skill Node:
  - id (canonical_id)
  - name, category, level, description
  - market_demand, growth_rate, maturity

Relationships:
  - DEPENDS_ON → weight (0.0-1.0), type (hard/soft)
  - PREREQUISITE_FOR → weight
  - RELATED_TO → weight, type (synergistic/substitutes)
  - BELONGS_TO → category (tree membership)
  - LEADS_TO → target_role (career progression)

Query Patterns:
  - Shortest prerequisite chain: BFS from A to B
  - Missing prerequisites: Find unacquired prerequisites for target skill
  - Skill clusters: Louvain community detection
  - Career path: Sequence of skills leading to target role
  - Gap analysis: Prerequisites not in user_skills


---

## 16. Integration Patterns

### 16.1 ARIA Orchestrator (A00) Integration

SkillAgent registers with ARIA as a domain-specific route handler. ARIA dispatches to SkillAgent when:

```
User: "How are my skills doing?"
  → ARIA classifies intent: skill_agent_query
  → Dispatches to SkillAgent with full user message
  → SkillAgent returns structured response
  → ARIA formats and delivers to user
```

**Dispatch Contract:**

```python
# ARIA → SkillAgent API
class SkillAgentDispatch:
    async def handle(self, message: str, user_id: str, context: dict) -> AgentResponse:
        intent = await self.classify_intent(message)
        sk_context = await SkillAgent.assemble_context(user_id, intent, context)
        result = await SkillAgent.dispatch(user_id, intent, sk_context)
        return AgentResponse(
            message=result.user_message,
            data=result.data,
            confidence=result.confidence,
            requires_human=result.requires_human_review
        )
```

### 16.2 Companion Engine Integration

Each sub-agent maps to one primary companion engine document:

| Sub-Agent | Engine Document | Integration Pattern |
|---|---|---|
| SK-01 Assessment | `SkillAssessment.md` | Calls assessment execution API + AI evaluation protocol |
| SK-05 Evidence | `SkillEvidence.md` | Calls evidence scoring + fraud detection algorithms |
| SK-03 Intelligence | `SkillIntelligence.md` | Calls score computation + analytics aggregation |
| SK-08 Market | `SkillMarketIntelligence.md` | Calls market data ingestion + trend analysis |
| SK-04 Roadmap | `SkillRoadmapEngine.md` | Calls roadmap generation + milestone optimization |
| SK-07 Opportunity | `SkillOpportunityMatching.md` | Calls scoring + matching + ranking engines |
| SK-09 Graph | `SkillGraphArchitecture.md` | Calls graph traversal + shortest path algorithms |
| SK-02 Recommendation | `skills.md` §20 | Directly implements recommendation algorithm |
| SK-06 Career | `skills.md` §19 | Directly implements career readiness algorithm |

### 16.3 Prompt System Integration

All LLM-dependent sub-agents use the PromptLoader system:

```python
from ai.prompt_loader import prompts

class SubAgentPromptManager:
    def __init__(self):
        self.prompt_registry = {
            "SK-01": "skill_assessment_agent",
            "SK-02": "skill_recommendation_agent",
            "SK-03": "skill_intelligence_agent",
            "SK-04": "skill_roadmap_agent",
            "SK-05": "skill_evidence_agent",
            "SK-06": "skill_career_agent",
            "SK-07": "opportunity_matching_agent"
        }

    async def get_prompt(self, agent_id: str, **kwargs) -> str:
        prompt_name = self.prompt_registry.get(agent_id)
        if not prompt_name:
            raise ValueError(f"No prompt registered for {agent_id}")
        entry = prompts.get_agent(prompt_name)
        if entry:
            return entry.render(**kwargs)
        # Graceful fallback: return hardcoded prompt
        return self._fallback_prompt(agent_id, **kwargs)

    def _fallback_prompt(self, agent_id: str, **kwargs) -> str:
        fallbacks = {
            "SK-01": "You are a skill assessment AI. Evaluate the user's skill level...",
            "SK-02": "You are a skill recommendation AI. Recommend skills to learn...",
            "SK-03": "You are a skill intelligence AI. Analyze skill scores...",
            "SK-04": "You are a roadmap building AI. Create a learning path...",
            "SK-05": "You are an evidence verification AI. Validate skill evidence...",
            "SK-06": "You are a career analysis AI. Assess career readiness...",
            "SK-07": "You are an opportunity matching AI. Rank opportunities..."
        }
        return fallbacks.get(agent_id, "You are a helpful AI assistant.")
```

### 16.4 Cross-Agent Communication

Sub-agents never call each other directly. All communication flows through SkillAgent Core or Supabase:

```
SkillAgent Core
  │
  ├── SK-01 → writes assessment result to user_skills
  ├── SK-02 → SK-02 reads from user_skills (updated by SK-01)
  │           SK-02 reads from market_data (updated by SK-08)
  │           SK-02 reads from skill_graph (updated by SK-09)
  ├── SK-03 → SK-03 reads from user_skills (updated by SK-01, SK-05)
  │           SK-03 reads from market_data (updated by SK-08)
  ├── SK-04 → SK-04 reads from user_skills + skill_graph
  │           SK-04 reads from skill_targets (updated by SK-02)
  ├── SK-05 → writes evidence results to skill_evidence
  ├── SK-06 → SK-06 reads from user_skills + market_data
  │           SK-06 reads from skill_targets + skill_assessments
  ├── SK-07 → SK-07 reads from user_skills (all sub-agents)
  │           SK-07 reads from opportunity data
  ├── SK-08 → writes market data to skill_market_data
  └── SK-09 → writes graph edges to skill_graph_edges
               SK-09 reads from all skill tables to build graph
```

### 16.5 Data Flow: End-to-End Scenario

```
User: "What should I learn to get a job at Google?"
  │
  ▼ SKILLAGENT CORE
  ├── Classify: recommend + career (multi-intent)
  ├── Assemble: full context package
  │
  ├──→ SK-06 (Career)
  │   ├── Target: "Software Engineer at Google"
  │   ├── Gaps: [System Design L2, DSA L3, Go L0]
  │   └── Readiness: 0.45
  │
  ├──→ SK-02 (Recommendation) — parallel
  │   ├── Input: gaps from SK-06 + full context
  │   ├── Skills to Learn: Go (demand:0.85, career:0.95)
  │   ├── Skills to Improve: DSA (gap:1, demand:0.90)
  │   └── Skills to Drop: jQuery (demand:0.15)
  │
  ├──→ SK-03 (Intelligence) — parallel
  │   ├── Compute: growth velocity, readiness
  │   └── Narrative: "You're 45% ready. 3 gaps remain."
  │
  ├──→ SK-04 (Roadmap) — after SK-02
  │   ├── Gaps: [Go, System Design, DSA]
  │   ├── Order: DSA (wks 1-4) → Go (5-10) → SysDesign (11-16)
  │   └── Total: 16 weeks at 15h/week
  │
  └── Synthesize:
      "To prepare for Google SWE roles, here's your plan:
       • Skill Readiness: 45% (3 gaps)
       • Priority: Learn Go, improve DSA & System Design
       • 16-week roadmap generated ✓
       • Market Insight: Go demand up 34% YoY"


---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| **SkillAgent** | The Skill Domain Controller — AI agent managing the entire skills ecosystem |
| **Sub-Agent (SK-01…SK-09)** | Specialized skill-domain agent under SkillAgent orchestration |
| **Skill Intent** | Classified user goal: assess, recommend, roadmap, evidence, intelligence, career, opportunity, market, graph |
| **Context Package** | Assembled bundle of user profile + system state + market data for a request |
| **Skill Pillar** | One of five recommendation categories: learn, improve, drop, emerging, opportunity_ready |
| **Strategy Profile** | Weight configuration for recommendation pillars (balanced, aggressive, etc.) |
| **Skill Level** | Proficiency level from L0 (Unknown) to L5 (Expert) per skills.md §5 |
| **Skill Gap** | Delta between user's current skill level and target/required level |
| **Career Readiness** | 0.0-1.0 score measuring preparedness for a target role |
| **Growth Velocity** | Average skill level increase per unit time (levels/month) |
| **Evidence Quality** | 0.0-1.0 score measuring evidence reliability |
| **Fraud Score** | 0.0-1.0 probability that evidence is fraudulent or AI-generated |
| **Guardrail** | Hard or soft rule enforced on every SkillAgent response |
| **Human Review** | Escalation path when AI confidence is too low or conflict detected |
| **PromptLoader** | Central prompt management system at `packages/ai/prompt_loader.py` |
| **Canonical Skill ID** | Normalized skill identifier (e.g., `python`, `react`, `ml_supervised`) |
| **TTL Cache** | Time-to-live cache for frequent queries (default 15 min) |
| **LLM Fallback** | Graceful degradation when LLM is unavailable (5-level chain) |

## Appendix B: Prompt File Specifications

### B.1 Required Prompt Files

| Prompt File | Agent | Lines (est) | Status |
|---|---|---|---|
| `prompts/agents/skill_assessment_agent.md` | SK-01 | ~200 | ✅ Generated |
| `prompts/agents/skill_recommendation_agent.md` | SK-02 | ~250 | Design |
| `prompts/agents/skill_intelligence_agent.md` | SK-03 | ~200 | Design |
| `prompts/agents/skill_roadmap_agent.md` | SK-04 | ~250 | Design |
| `prompts/agents/skill_evidence_agent.md` | SK-05 | ~200 | Design |
| `prompts/agents/skill_career_agent.md` | SK-06 | ~200 | Design |
| `prompts/agents/opportunity_matching_agent.md` | SK-07 | ~210 | ✅ Generated |
| `prompts/system/skill_agent_system.md` | Core | ~150 | Design |

### B.2 Frontmatter Template

Every prompt file must follow the standard frontmatter schema:

```yaml
---
version: 1.0.0
status: active
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.3
description: >
  SK-{NN} {Name} — {one-line purpose}
last_updated: 2026-06-13
approved_by: developer
review_cycle: weekly
tags: [skills, agent, sk-{nn}, {domain}]
---
```

### B.3 Prompt Structure Template (from AGENTS.md §11.3)

```
---
<YAML frontmatter>
---

# <Title>

## Role Definition
(Who the agent is, its purpose, tone, constraints)

## Input Schema
(YAML or JSON schema of all input fields with types, defaults, examples)

## Output JSON Schema
(Full JSON schema with required/optional fields, validation rules, examples)

## Detailed Instructions
(Step-by-step reasoning chain, priority rules, decision trees)

## Few-Shot Examples
(3-5 complete input → output examples with explanations)

## Edge Cases
(Empty data, missing fields, contradictory data, errors, boundary conditions)

## Anti-Patterns
(What NOT to do, with examples of bad outputs and why they're bad)

## Quality Criteria
(Checklist for self-verification before output)

## Error Recovery
(What to do when generation fails, token budget exceeded, etc.)
```

## Appendix C: Implementation Roadmap

### C.1 Phase 1: Foundation (Current — v1.0.0)

| Item | Status | Dependencies |
|---|---|---|
| SkillAgent Core (Intent classification + dispatch) | Design | — |
| SK-07 Opportunity Agent prompt | ✅ Complete | SkillOpportunityMatching.md |
| Context assembly pipeline | Design | — |
| Guardrail system | Design | — |
| Observability framework | Design | — |
| KPI definitions | Design | — |

### C.2 Phase 2: Core Sub-Agents (v1.1.0)

| Item | Status | ETA |
|---|---|---|
| SK-01 Assessment Agent + prompt | Design | 2 weeks |
| SK-05 Evidence Agent + prompt | Design | 2 weeks |
| SK-09 Graph Agent (algorithmic) | Design | 1 week |
| Evaluation framework | Design | 1 week |
| A/B testing infrastructure | Design | 2 weeks |

### C.3 Phase 3: Intelligence & Market (v1.2.0)

| Item | Status | ETA |
|---|---|---|
| SK-03 Intelligence Agent + prompt | Design | 3 weeks |
| SK-08 Market Agent (algorithmic pipeline) | Design | 2 weeks |
| Career readiness algorithm | Design | 2 weeks |
| Market data ingestion pipeline | Design | 3 weeks |

### C.4 Phase 4: Recommendation & Roadmap (v1.3.0)

| Item | Status | ETA |
|---|---|---|
| SK-02 Recommendation Agent + prompt | Design | 3 weeks |
| SK-04 Roadmap Agent + prompt | Design | 3 weeks |
| SK-06 Career Agent + prompt | Design | 2 weeks |
| Full multi-agent coordination | Design | 4 weeks |

### C.5 Phase 5: Enterprise Hardening (v2.0.0)

| Item | Status | ETA |
|---|---|---|
| Bias detection system (§14.4) | Design | 4 weeks |
| Advanced fraud detection | Design | 4 weeks |
| Multi-tenant isolation | Design | 6 weeks |
| Performance benchmarking | Design | 2 weeks |
| Production readiness review | Design | 8 weeks |

## Appendix D: Relationship Map

### D.1 Complete Skills Document Ecosystem

```
                      ┌─────────────────────────────────────┐
                      │          skills.md (§1-§33)          │
                      │        Constitution & Taxonomy       │
                      └──────┬──────┬──────┬──────┬─────────┘
                             │      │      │      │
         ┌───────────────────┼──────┼──────┼──────┼───────────────────┐
         ▼                   ▼      ▼      ▼      ▼                   ▼
┌─────────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐
│ SkillAgent.md   │ │ Assessment  │ │Evidence  │ │Intelligence  │ │Market    │
│ (THIS DOCUMENT) │ │ Engine      │ │ Engine   │ │ Engine       │ │Engine    │
│ Orchestrator    │ │ (7,489 ln)  │ │(5,454 ln)│ │(5,155 ln)    │ │(4,306 ln)│
└─────────────────┘ └────────────┘ └──────────┘ └──────────────┘ └──────────┘

 ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐
 │ Roadmap      │ │ Opportunity  │ │ Graph Architecture │
 │ Engine       │ │ Engine       │ │ (3,285 ln)         │
 │ (5,059 ln)   │ │ (3,529 ln)   │ └───────────────────┘
 └──────────────┘ └──────────────┘
```

### D.2 Agent-to-Doc Cross-Reference

| Agent ID | Agent Name | Primary Doc | Supporting Docs |
|---|---|---|---|
| A00 | ARIA Orchestrator | `20_Agent.md` | All |
| A03 | Learning Agent | `20_Agent.md` | SkillRoadmapEngine.md |
| A06 | Opportunity Agent | `20_Agent.md` | SkillOpportunityMatching.md |
| SK-CORE | SkillAgent | **SkillAgent.md** | All 7 engine docs |
| SK-01 | Assessment Agent | SkillAssessment.md | skills.md §5, §12 |
| SK-02 | Recommendation Agent | skills.md §20 | SkillMarketIntelligence.md, SkillGraphArchitecture.md |
| SK-03 | Intelligence Agent | SkillIntelligence.md | skills.md §19 |
| SK-04 | Roadmap Agent | SkillRoadmapEngine.md | skills.md §15 |
| SK-05 | Evidence Agent | SkillEvidence.md | skills.md §11 |
| SK-06 | Career Agent | skills.md §19 | SkillIntelligence.md, MarketIntel.md |
| SK-07 | Opportunity Agent | SkillOpportunityMatching.md | skills.md §16 |
| SK-08 | Market Agent | SkillMarketIntelligence.md | skills.md §17 |
| SK-09 | Graph Agent | SkillGraphArchitecture.md | skills.md §9, §10 |

### D.3 Data Dependency Graph

```
skill_market_data (SK-08)
  │
  ▼
skill_intelligence_scores (SK-03)
  │
  ▼
user_skills (SK-01, SK-05) ──→ skill_targets (SK-02)
  │                                  │
  │                                  ▼
  │                          skill_roadmaps (SK-04)
  │
  └────────────────────────→ skill_opportunities (SK-07)
  │
  └────────────────────────→ career_analysis (SK-06)
  │
  └────────────────────────→ skill_graph_edges (SK-09)
                                   │
                                   ▼
                            All sub-agents (graph queries)


---

## Appendix E: Database Schemas

### E.1 Core Skill Tables

```sql
-- User skills inventory
CREATE TABLE user_skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    canonical_id    VARCHAR(100) NOT NULL,
    skill_name      VARCHAR(255) NOT NULL,
    level           SMALLINT NOT NULL CHECK (level BETWEEN 0 AND 5),
    confidence      DECIMAL(4,3) DEFAULT 0.5 CHECK (confidence BETWEEN 0 AND 1),
    category        VARCHAR(50),
    last_assessed_at TIMESTAMPTZ,
    last_used_at    TIMESTAMPTZ,
    evidence_count  INTEGER DEFAULT 0,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, canonical_id)
);

-- Skill targets/goals
CREATE TABLE skill_targets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    canonical_id    VARCHAR(100) NOT NULL,
    target_level    SMALLINT NOT NULL CHECK (target_level BETWEEN 0 AND 5),
    current_level   SMALLINT DEFAULT 0,
    priority        VARCHAR(20) DEFAULT 'medium',
    target_date     DATE,
    source          VARCHAR(50), -- 'career', 'roadmap', 'self', 'recommendation'
    source_id       UUID,       -- FK to originating recommendation/roadmap
    status          VARCHAR(20) DEFAULT 'active', -- active | achieved | paused | dropped
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, canonical_id, source)
);

-- Skill assessments
CREATE TABLE skill_assessments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    canonical_id    VARCHAR(100) NOT NULL,
    method          VARCHAR(30) NOT NULL, -- 'adaptive_quiz', 'project_eval', 'hybrid'
    level_before    SMALLINT,
    level_after     SMALLINT NOT NULL,
    algorithm_score DECIMAL(4,3),
    llm_score       DECIMAL(4,3),
    combined_score  DECIMAL(4,3),
    confidence      DECIMAL(4,3) NOT NULL,
    questions       JSONB DEFAULT '[]',
    responses       JSONB DEFAULT '[]',
    time_spent_sec  INTEGER,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, canonical_id, created_at)
);

-- Skill evidence
CREATE TABLE skill_evidence (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    canonical_id    VARCHAR(100) NOT NULL,
    evidence_type   VARCHAR(30) NOT NULL, -- 'certificate', 'project', 'code_sample', 'endorsement', 'article', 'testimony'
    title           VARCHAR(255),
    url             TEXT,
    content_hash    VARCHAR(64),
    quality_score   DECIMAL(4,3) DEFAULT 0.0,
    fraud_score     DECIMAL(4,3) DEFAULT 0.0,
    level_supported SMALLINT,
    status          VARCHAR(20) DEFAULT 'pending', -- pending | verified | rejected | flagged
    reviewer_notes  TEXT,
    verified_by     VARCHAR(50), -- 'ai', 'human', 'system'
    verified_at     TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, canonical_id, content_hash)
);
```

### E.2 Intelligence & Market Tables

```sql
-- Intelligence scores (computed weekly)
CREATE TABLE skill_intelligence_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    score_type      VARCHAR(30) NOT NULL, -- 'growth_velocity', 'career_readiness', 'opportunity_match', 'income_potential'
    score_value     DECIMAL(6,4) NOT NULL,
    score_label     VARCHAR(20), -- 'low', 'below_average', 'average', 'above_average', 'excellent'
    percentile      SMALLINT CHECK (percentile BETWEEN 0 AND 100),
    breakdown       JSONB DEFAULT '{}',
    narrative       TEXT,
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, score_type, computed_at)
);

-- Market data for skills
CREATE TABLE skill_market_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_id    VARCHAR(100) PRIMARY KEY,
    skill_name      VARCHAR(255) NOT NULL,
    demand_score    DECIMAL(4,3) DEFAULT 0.5,
    demand_trend    VARCHAR(20), -- 'rising', 'stable', 'declining'
    demand_7d       INTEGER,
    demand_30d      INTEGER,
    demand_90d      INTEGER,
    salary_min      INTEGER,
    salary_median   INTEGER,
    salary_max      INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    growth_rate_pct DECIMAL(5,2),
    maturity_score  DECIMAL(4,3),
    job_postings_30d INTEGER,
    top_employers   JSONB DEFAULT '[]',
    top_industries  JSONB DEFAULT '[]',
    source          VARCHAR(50),
    refreshed_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### E.3 Roadmap & Career Tables

```sql
-- Generated roadmaps
CREATE TABLE skill_roadmaps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    target_role     VARCHAR(255),
    target_skills   JSONB DEFAULT '[]',
    phases          JSONB DEFAULT '[]',
    total_duration_days INTEGER,
    estimated_hours_per_week DECIMAL(4,1),
    status          VARCHAR(20) DEFAULT 'active',
    progress_pct    DECIMAL(5,2) DEFAULT 0.0,
    llm_enhanced    BOOLEAN DEFAULT false,
    algorithm_version VARCHAR(20),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Roadmap milestones
CREATE TABLE skill_roadmap_milestones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id      UUID NOT NULL REFERENCES skill_roadmaps(id),
    phase_number    SMALLINT NOT NULL,
    milestone_number SMALLINT NOT NULL,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    canonical_id    VARCHAR(100),
    target_level    SMALLINT,
    duration_days   INTEGER,
    resources       JSONB DEFAULT '[]',
    status          VARCHAR(20) DEFAULT 'pending', -- pending | in_progress | completed | skipped
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Career analysis history
CREATE TABLE career_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    target_role     VARCHAR(255) NOT NULL,
    readiness_score DECIMAL(4,3) NOT NULL,
    gaps            JSONB DEFAULT '[]',
    estimated_prep_days INTEGER,
    milestones      JSONB DEFAULT '[]',
    trajectory      JSONB DEFAULT '[]',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### E.4 Index Strategy

```sql
-- High-frequency query indexes
CREATE INDEX idx_us_user_cat    ON user_skills(user_id, category);
CREATE INDEX idx_us_level_range ON user_skills(user_id, level);
CREATE INDEX idx_st_active      ON skill_targets(user_id, status) WHERE status = 'active';
CREATE INDEX idx_sa_recent      ON skill_assessments(user_id, canonical_id, created_at DESC);
CREATE INDEX idx_se_status      ON skill_evidence(user_id, status) WHERE status = 'pending';
CREATE INDEX idx_se_fraud       ON skill_evidence(fraud_score DESC) WHERE fraud_score > 0.7;
CREATE INDEX idx_sis_recent     ON skill_intelligence_scores(user_id, score_type, computed_at DESC);
CREATE INDEX idx_smd_demand     ON skill_market_data(demand_score DESC);
CREATE INDEX idx_smd_growth     ON skill_market_data(growth_rate_pct DESC);
CREATE INDEX idx_sr_active      ON skill_roadmaps(user_id, status) WHERE status = 'active';
CREATE INDEX idx_srm_roadmap    ON skill_roadmap_milestones(roadmap_id, phase_number);
CREATE INDEX idx_ca_recent      ON career_analyses(user_id, created_at DESC);
```

## Appendix F: SLA & Cost Tables

### F.1 Sub-Agent SLAs

| Sub-Agent | P50 | P95 | P99 | Success Rate | Availability | Error Budget (monthly) |
|---|---|---|---|---|---|---|
| SK-CORE (Classification) | 200 ms | 500 ms | 1.5 s | 99.5% | 99.9% | 216 min downtime |
| SK-01 (Assessment) | 3 s | 8 s | 15 s | 98% | 99.5% | 216 min |
| SK-02 (Recommendation) | 2 s | 5 s | 10 s | 99% | 99.5% | 216 min |
| SK-03 (Intelligence) | 4 s | 10 s | 20 s | 97% | 99% | 432 min |
| SK-04 (Roadmap) | 5 s | 12 s | 25 s | 97% | 99% | 432 min |
| SK-05 (Evidence) | 3 s | 8 s | 15 s | 98% | 99.5% | 216 min |
| SK-06 (Career) | 3 s | 8 s | 15 s | 98% | 99.5% | 216 min |
| SK-07 (Opportunity) | 2 s | 6 s | 12 s | 99% | 99.5% | 216 min |
| SK-08 (Market) | 30 s (batch) | 60 s | 120 s | 99.5% | 99.9% | 43 min |
| SK-09 (Graph) | 100 ms | 500 ms | 1 s | 99.9% | 99.99% | 4.3 min |

### F.2 Estimated Cost Per Request

| Sub-Agent | Model | Tokens In | Tokens Out | Est Cost/Call | Calls/Day | Monthly Cost |
|---|---|---|---|---|---|---|
| SK-CORE (classification) | Mistral 7B | 200 | 50 | $0.0001 | 500 | $1.50 |
| SK-01 (LLM path) | Mistral 7B | 1500 | 400 | $0.002 | 50 | $3.00 |
| SK-02 (LLM path) | Mistral 7B | 2000 | 800 | $0.003 | 30 | $2.70 |
| SK-03 (LLM path) | Mistral 7B | 2500 | 600 | $0.003 | 7 (weekly) | $0.63 |
| SK-04 (LLM path) | Mistral 7B | 3000 | 1500 | $0.005 | 10 | $1.50 |
| SK-05 (LLM path) | Mistral 7B | 1500 | 300 | $0.002 | 20 | $1.20 |
| SK-06 (LLM path) | Mistral 7B | 2000 | 500 | $0.003 | 10 | $0.90 |
| SK-07 (LLM path) | Mistral 7B | 2500 | 800 | $0.003 | 15 | $1.35 |
| SK-08 (algorithmic) | — | 0 | 0 | $0.000 | 5 (daily) | $0.00 |
| SK-09 (algorithmic) | — | 0 | 0 | $0.000 | 100 | $0.00 |
| **Total** | | | | | **~747/day** | **~$12.78/month** |

### F.3 Ollama Fallback Costs

| Fallback Level | Model | Cost Multiplier | Est Total/Month |
|---|---|---|---|
| Level 1 (Primary) | Ollama Mistral 7B | 1.0x (free) | $0.00 (local HW) |
| Level 2 (Fallback) | Claude Sonnet 4 | ~100x | ~$12.78 (cloud) |

## Appendix G: Edge Cases & Failure Recovery

### G.1 Edge Case Matrix

| Edge Case | Scenario | Handling |
|---|---|---|
| **Empty skill profile** | New user with no assessed skills | Return default recommendations based on career goals or popular skills |
| **All skills mastered** | User at L5 in all relevant skills | Switch to emerging/bleeding-edge recommendations |
| **No market data** | SK-08 offline or data source down | Use cached data (max 7 days stale) or default demand=0.5 |
| **Contradictory evidence** | Evidence supports L2, assessment says L4 | Flag for human review, set level to max(evidence, assessment) - 1 |
| **LLM timeout** | No response in 10s | Fallback to algorithmic scoring only |
| **Rate limit hit** | > 10 assessments/day | Return informative message with next available time |
| **User rage-quits** | User gives up mid-assessment | Save partial progress, offer resume later |
| **Skill not in taxonomy** | User mentions "quantum blockchain dev" | Flag for taxonomy expansion, recommend using closest canonical skill |
| **Cross-session context** | User returns after weeks | Reload from database, summarize changes since last visit |
| **Multi-user conflict** | Team account with overlapping skill claims | Use per-user RLS, no conflict possible |

### G.2 Failure Recovery

| Failure Mode | Detection | Recovery | User Impact |
|---|---|---|---|
| SK-08 market data stale | > 24h since refresh | Use last good data, trigger async refresh | Slightly outdated market intel |
| SK-09 graph DB unreachable | Connection timeout | Fallback to flat taxonomy (JSON tree) | No graph recommendations |
| Prompt file missing | PromptLoader returns None | Use hardcoded fallback prompt | None (transparent) |
| Assessment in progress lost | Server restart | Reload from skill_assessments (saved state) | None (auto-resume) |
| LLM returns malformed JSON | JSON parse error | Retry 1x, then use algorithmic scoring | Less nuanced output |
| DB write fails | Supabase error | Retry 3x, then cache write for next attempt | Delayed persistence |
