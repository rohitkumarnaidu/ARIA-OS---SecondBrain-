# 22. Memory Architecture — Enterprise Reference

---

## Document Control

| Metadata | Value |
|----------|-------|
| **Document ID** | ARIA-ARCH-MEM-001 |
| **Version** | 2.0.0 |
| **Status** | APPROVED |
| **Classification** | INTERNAL — Engineering |
| **Last Updated** | 2026-06-11 |
| **Owner** | AI Architecture Team |
| **Review Cycle** | Quarterly |
| **Next Review** | 2026-09-11 |

---

## Executive Summary

### Why Memory Architecture Matters

The memory architecture is the foundational layer enabling ARIA's persistent learning, contextual awareness, and behavioral adaptation. Without a structured memory system, every AI interaction would be stateless — the system would have no recollection of past conversations, user preferences, learned patterns, or procedural knowledge. This architecture bridges the gap between stateless LLM inference and stateful personal AI companionship.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Tiered Memory Model** | 5-tier (Buffer → Working → Episodic → Semantic → Procedural) | Inspired by human cognitive architecture (Atkinson-Shiffrin + Tulving); enables graduated retention, relevance weighting, and resource optimization |
| **Storage Backend** | Supabase (PostgreSQL + JSONB) | Leverages existing project infrastructure; JSONB enables schema-less value storage with indexing; Row-Level Security provides tenant isolation |
| **Importance Scoring** | Composite score (recency × frequency × source × category) | Ensures high-value memories are preferentially surfaced while noise decays naturally |
| **Consolidation Strategy** | Scheduled (daily) + Event-driven (on significant interaction) | Balances computational cost with timeliness; daily batch handles bulk, events capture critical updates immediately |
| **Memory Retrieval** | Hybrid: SQL ordering + semantic scoring | Low-latency for production queries without requiring vector infrastructure on day one |
| **Token Budget** | 4000 tokens max for assembled context | Matches typical LLM context window constraints; prevents prompt overflow |

### Architecture Principles

1. **Tenant Isolation** — All memory is scoped by `user_id`; no cross-tenant leakage
2. **Graceful Degradation** — If a tier is unavailable, the system falls back to higher-priority tiers
3. **Eventual Consistency** — Episodic → Semantic consolidation is asynchronous; short-term views may lag by up to 24 hours
4. **Privacy by Design** — Every memory has a source, confidence, and importance; users can query, modify, or delete any memory
5. **Observability** — All memory operations are logged with latency, size, and access patterns

---

## Memory Model Reference Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        ARIA MEMORY ARCHITECTURE (5-TIER MODEL)                  │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  TIER 0       │    │  TIER 1      │    │  TIER 2      │    │  TIER 3      │   │
│  │  BUFFER       │───▶│  WORKING     │───▶│  EPISODIC    │───▶│  SEMANTIC    │   │
│  │  (Last N msgs)│    │  (Session)   │    │  (History)   │    │  (Knowledge) │   │
│  │  Volatile     │    │  Volatile    │    │  Persisted   │    │  Persisted   │   │
│  │  In-memory    │    │  In-memory   │    │  Supabase    │    │  Supabase    │   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │                   │           │
│         │    ┌──────────────┴───────────────────────────────────┐   │           │
│         │    │                  TIER 4                           │   │           │
│         │    │              PROCEDURAL MEMORY                   │   │           │
│         │    │  (Skills, Workflows, How-To Knowledge)           │   │           │
│         │    │  Persisted — Supabase + Versioned                │   │           │
│         │    └──────────────────────┬───────────────────────────┘   │           │
│         │                           │                               │           │
│         ▼                           ▼                               ▼           │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                     MEMORY SERIALIZATION LAYER                            │   │
│  │  Compression → Encoding → Storage → Retrieval → Decompression            │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│         │                           │                               │           │
│         ▼                           ▼                               ▼           │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                     CONSOLIDATION ENGINE                                   │   │
│  │  Short-Term → Long-Term Transfer | Summarization | Pattern Detection      │   │
│  │  Signal Extraction | Noise Filtering | Deduplication                      │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│         │                                                                       │
│         ▼                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                     RETRIEVAL ENGINE                                       │   │
│  │  Semantic Search | Recency Boost | Relevance Scoring | Hybrid Query       │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Tier 0: Buffer Memory

### Purpose

Buffer memory holds the last N messages of the current conversation for immediate contextual continuity. It is the most ephemeral tier — scoped to the current interaction window and never persisted to the database.

### Characteristics

| Property | Value |
|----------|-------|
| **Retention** | Last N messages (configurable, default: 10) |
| **Persistence** | None — in-memory only |
| **Scope** | Current conversation turn |
| **Latency** | < 1 ms (local variable) |
| **Size** | ~2000 tokens max |

### Implementation

```python
class BufferMemory:
    """Ring buffer of recent messages for immediate context."""

    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.messages: list[dict] = []

    def add(self, role: str, content: str, metadata: dict | None = None) -> None:
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        })
        if len(self.messages) > self.capacity:
            self.messages.pop(0)

    def get_context(self) -> list[dict]:
        return list(self.messages)

    def get_token_count(self) -> int:
        return sum(len(m["content"].split()) for m in self.messages)

    def trim_to_token_budget(self, budget: int = 2000) -> list[dict]:
        trimmed = []
        total = 0
        for m in reversed(self.messages):
            tokens = len(m["content"].split())
            if total + tokens > budget:
                break
            trimmed.insert(0, m)
            total += tokens
        return trimmed
```

### Lifecycle

- **Created**: On new user message
- **Updated**: Appended after each turn in the current interaction
- **Destroyed**: When conversation window closes (user navigates away, session timeout, or explicit clear)
- **Promoted**: When a message is part of a significant interaction (e.g., task created, goal set), it is elevated to Tier 2 (Episodic) immediately

---

## Tier 1: Working Memory

### Purpose

Working memory is the assembled context snapshot for the current session. It is rebuilt on every request by querying real-time state from Supabase and enriching it with temporal and session-level data. Unlike Buffer (raw message text), Working Memory is a structured, enriched view of the user's current state.

### Structure

```python
working_memory_schema = {
    "identity": {
        "user_name": str,                     # Display name
        "user_id": str,                       # UUID
        "last_interaction": datetime,         # Last user message timestamp
        "current_mood": str | None,           # Inferred or explicitly stated
        "persona_tone": str,                  # Contextual tone (professional, casual, urgent)
    },
    "temporal": {
        "current_time": datetime,             # Server time
        "day_of_week": str,                   # Monday, Tuesday, etc.
        "time_of_day": str,                   # morning|afternoon|evening|night
        "semester_week": int | None,          # Academic calendar position
        "is_exam_period": bool,               # Flag for exam proximity
    },
    "session": {
        "session_id": str,                    # UUID for this session
        "message_count_today": int,           # Total messages today across sessions
        "last_3_messages": [str, str, str],   # Raw text of last 3 exchanges
        "current_intent": str | None,         # Detected user intent
        "pending_actions": [str],             # Tasks user agreed to complete
        "active_dialog_state": str | None,    # Multi-turn dialog tracking
    },
    "state": {
        "tasks_today_count": int,             # Tasks created or due today
        "overdue_count": int,                 # Past-due tasks
        "sleep_score": int | None,            # Last sleep quality (0-100)
        "active_goals_count": int,            # Number of active goals
        "habit_streak": int | None,           # Current longest habit streak
        "upcoming_deadlines": [dict],         # Next 3 deadlines
        "current_course_load": int,           # Active enrolled courses
    },
}
```

### Refresh Cadence

| Trigger | Action | Latency Budget |
|---------|--------|----------------|
| Every user message | Full rebuild | < 200 ms |
| Every system event | Partial update (affected keys only) | < 50 ms |
| Background refresh | TTL-based (60s) cache for read-only state | < 100 ms |

### Enrichment Pipeline

```
Raw request
    │
    ▼
┌─────────────────────┐
│ Load Identity       │ ← users table (name, preferences)
│ (50 ms)             │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Load Temporal       │ ← server clock + academic calendar
│ (5 ms)              │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Load Session State  │ ← current session cache + message count
│ (20 ms)             │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Load Real-Time      │ ← tasks, goals, sleep, habits queries
│ (100 ms)            │ ← Parallelized Supabase queries
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Assemble & Validate │ ← Schema validation, size check
│ (10 ms)             │
└──────────┬──────────┘
           ▼
    Working Memory Ready
```

### Token Budget Allocation

```python
WORKING_MEMORY_BUDGET = 1200  # tokens (out of 4000 total)

budget_allocation = {
    "identity": 100,           # User name, preferences
    "temporal": 100,           # Time context
    "session": 400,            # Recent messages, intent
    "state": 400,              # Task/goal state summaries
    "buffer_overhead": 200,    # Formatting, separators
}
```

### Truncation Rules (when budget exceeded)

1. **Priority 1 (Never remove)**: user_name, current_time, active_goals_count
2. **Priority 2 (Keep if possible)**: overdue_count, sleep_score, pending_actions
3. **Priority 3 (Truncate first)**: completed goals list, old opportunity descriptions, verbose task titles
4. **Fallback**: If still over budget after truncation, oldest session messages are dropped first

### Lifecycle

- **Created**: On every user message or system event requiring AI response
- **Used**: Passed to all sub-agents in the call chain as the `context` parameter
- **Destroyed**: After response is returned; synthesized contents promoted to Episodic Memory

---

## Tier 2: Episodic Memory

### Purpose

Episodic memory stores records of past interactions — what was said, decided, promised, or corrected. This tier enables ARIA to reference past conversations, maintain conversational continuity across sessions, and learn from user corrections. It is the persistence layer for all interaction history.

### Storage Schema

**Core Table: `chat_messages`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | PK, DEFAULT gen_random_uuid() | Unique message identifier |
| `user_id` | `uuid` | FK → users(id), NOT NULL, INDEX | Tenant ownership |
| `session_id` | `uuid` | INDEX | Groups messages into sessions |
| `role` | `text` | CHECK(role IN ('user', 'aria', 'system')) | Message origin |
| `message` | `text` | NOT NULL | Full message content |
| `message_summary` | `text` | NULL | LLM-generated summary (for retrieval) |
| `token_count` | `int` | DEFAULT 0 | Estimated token count |
| `metadata` | `jsonb` | DEFAULT '{}'::jsonb | Intent, entities, sentiment, topics |
| `interaction_type` | `text` | NULL | query, command, correction, decision, creation |
| `parent_message_id` | `uuid` | NULL, FK → chat_messages(id) | Thread tracking |
| `importance_score` | `float` | DEFAULT 0.5 | 0.0–1.0 episodic importance |
| `created_at` | `timestamptz` | DEFAULT now(), INDEX | Event timestamp |

**Indexes**:
```sql
CREATE INDEX idx_chat_messages_user_created 
    ON chat_messages (user_id, created_at DESC);
CREATE INDEX idx_chat_messages_session 
    ON chat_messages (user_id, session_id);
CREATE INDEX idx_chat_messages_type 
    ON chat_messages (user_id, interaction_type) 
    WHERE interaction_type IS NOT NULL;
CREATE INDEX idx_chat_messages_metadata_gin 
    ON chat_messages USING GIN (metadata jsonb_path_ops);
```

### Retrieval Strategies

```python
class EpisodicRetrievalStrategy(Enum):
    LAST_N = "last_n"                     # Most recent N messages
    TIME_WINDOWED = "time_windowed"       # All messages in time range
    TOPIC_FILTERED = "topic_filtered"     # Filtered by intent/topic metadata
    SESSION_GROUPED = "session_grouped"   # Last K complete sessions
    IMPORTANCE_RANKED = "importance"      # Highest importance score first
    HYBRID = "hybrid"                     # Combine multiple strategies
```

#### Strategy 1: Last-N (Default)

```python
async def get_episodic_last_n(
    user_id: str, 
    limit: int = 10,
    min_importance: float = 0.0
) -> list[dict]:
    """Retrieve last N messages with optional importance filter."""
    query = (
        supabase.from_("chat_messages")
        .select("role, message, message_summary, metadata, importance_score, created_at")
        .eq("user_id", user_id)
        .order("created_at", ascending=False)
        .limit(limit)
    )
    if min_importance > 0.0:
        query = query.gte("importance_score", min_importance)
    
    response = await query.execute()
    return response.data
```

#### Strategy 2: Topic-Filtered

```python
async def get_episodic_by_topic(
    user_id: str,
    topic: str,
    limit: int = 20,
    lookback_days: int = 30
) -> list[dict]:
    """Retrieve messages tagged with a specific topic."""
    cutoff = (datetime.now() - timedelta(days=lookback_days)).isoformat()
    response = await (
        supabase.from_("chat_messages")
        .select("role, message, message_summary, metadata, created_at")
        .eq("user_id", user_id)
        .gte("created_at", cutoff)
        .contains("metadata", {"intent": topic})
        .order("created_at", ascending=False)
        .limit(limit)
        .execute()
    )
    return response.data
```

#### Strategy 3: Time-Windowed

```python
async def get_episodic_time_window(
    user_id: str, 
    start_time: datetime, 
    end_time: datetime | None = None
) -> list[dict]:
    """Get all messages within a specific time window."""
    query = (
        supabase.from_("chat_messages")
        .select("role, message, metadata, created_at")
        .eq("user_id", user_id)
        .gte("created_at", start_time.isoformat())
        .order("created_at", ascending=True)
    )
    if end_time:
        query = query.lte("created_at", end_time.isoformat())
    
    response = await query.execute()
    return response.data
```

### Consolidation to Semantic Memory

#### Scheduled Consolidation (Daily)

```python
async def consolidate_episodic_to_semantic(user_id: str, lookback_hours: int = 24):
    """
    Daily consolidation pipeline.
    
    Steps:
    1. Fetch recent episodic entries
    2. Summarize multi-turn interactions into single entries
    3. Extract patterns, preferences, decisions
    4. Score extracted memories by importance
    5. Upsert into semantic memory (aria_memory)
    """
    cutoff = datetime.now() - timedelta(hours=lookback_hours)
    
    messages = await get_episodic_time_window(user_id, cutoff)
    if not messages:
        return
    
    # Prepare for LLM summarization
    message_batch = [
        {"role": m["role"], "content": m["message"]} 
        for m in messages
    ]
    
    # Extract patterns via LLM or heuristic rules
    patterns = await detect_behavioral_patterns(message_batch)
    preferences = await extract_preferences(message_batch)
    decisions = await extract_decisions(message_batch)
    facts = await extract_facts(message_batch)
    
    # Store extracted memories
    for key, value in patterns.items():
        await upsert_semantic_memory(
            user_id=user_id,
            key=f"pattern_{key}",
            value=value,
            importance=calculate_importance(value, category="pattern"),
            category="pattern",
            source="consolidated",
        )
    
    for key, value in preferences.items():
        await upsert_semantic_memory(
            user_id=user_id,
            key=f"preference_{key}",
            value=value,
            importance=calculate_importance(value, category="preference"),
            category="preference",
            source="consolidated",
        )
    
    # Update daily_logs with consolidation summary
    await supabase.from_("daily_logs").insert({
        "user_id": user_id,
        "date": datetime.now().date().isoformat(),
        "consolidation_summary": {
            "messages_processed": len(messages),
            "patterns_found": len(patterns),
            "preferences_found": len(preferences),
            "decisions_found": len(decisions),
            "facts_found": len(facts),
        },
        "created_at": datetime.now().isoformat(),
    }).execute()
```

#### Event-Driven Consolidation

Triggered immediately when a high-significance interaction occurs:

```python
HIGH_SIGNIFICANCE_EVENTS = {
    "task_created", "goal_created", "preference_stated", 
    "correction_provided", "decision_made", "milestone_reached"
}

async def event_driven_consolidation(user_id: str, message_id: str, event_type: str):
    """Immediately consolidate high-significance interactions."""
    if event_type not in HIGH_SIGNIFICANCE_EVENTS:
        return
    
    message = await get_message_by_id(message_id)
    extraction = await extract_semantic_from_message(message)
    
    if extraction and extraction["importance"] > 0.7:
        await upsert_semantic_memory(
            user_id=user_id,
            key=extraction["key"],
            value=extraction["value"],
            importance=extraction["importance"],
            category=extraction["category"],
            source="event_driven",
        )
```

---

## Tier 3: Semantic Memory

### Purpose

Semantic memory is the long-term knowledge store about the user. It captures preferences, behavioral patterns, stable traits, past decisions, factual information, and skill-related data. This is the tier that enables ARIA to "know" the user over time — to anticipate needs, personalize responses, and detect behavioral shifts.

### Storage Schema

**Core Table: `aria_memory`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | PK, DEFAULT gen_random_uuid() | Unique memory identifier |
| `user_id` | `uuid` | FK → users(id), NOT NULL, INDEX | Tenant ownership |
| `key` | `text` | NOT NULL, UNIQUE(user_id, key) | Memory identifier (e.g., "preferred_study_time") |
| `value` | `jsonb` | NOT NULL | Memory value (scalar, array, or object) |
| `importance` | `float` | DEFAULT 0.5, CHECK(0.0–1.0), INDEX | Importance weight for retrieval ranking |
| `category` | `text` | NOT NULL, CHECK(...) | preference, pattern, trait, decision, fact, skill |
| `subcategory` | `text` | NULL | Fine-grained classification within category |
| `source` | `text` | NOT NULL, CHECK(...) | How learned: extracted, explicit, inferred, consolidated, event_driven |
| `confidence` | `float` | DEFAULT 0.5, CHECK(0.0–1.0) | Certainty level |
| `ttl_days` | `int` | NULL | Time-to-live; NULL = indefinite |
| `version` | `int` | DEFAULT 1 | Incremented on update |
| `created_at` | `timestamptz` | DEFAULT now() | First stored timestamp |
| `updated_at` | `timestamptz` | DEFAULT now() | Last modification timestamp |
| `last_accessed` | `timestamptz` | DEFAULT now(), INDEX | Last retrieval for decay calculation |
| `access_count` | `int` | DEFAULT 0 | Number of retrievals |
| `parent_key` | `text` | NULL | Hierarchical relationship (e.g., preference_group) |
| `tags` | `jsonb` | DEFAULT '[]'::jsonb | Arbitrary tagging for faceted search |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_aria_memory_user_key 
    ON aria_memory (user_id, key);
CREATE INDEX idx_aria_memory_user_importance 
    ON aria_memory (user_id, importance DESC);
CREATE INDEX idx_aria_memory_category 
    ON aria_memory (user_id, category);
CREATE INDEX idx_aria_memory_last_accessed 
    ON aria_memory (user_id, last_accessed);
CREATE INDEX idx_aria_memory_tags_gin 
    ON aria_memory USING GIN (tags jsonb_path_ops);
```

### Memory Categories

| Category | Description | Example | Typical Importance | Retention |
|----------|-------------|---------|--------------------|-----------|
| `preference` | Stated or inferred user preferences | `preferred_study_time: "night"` | 0.7–0.9 | Indefinite |
| `pattern` | Behavioral pattern detected | `task_abandonment_rate: 0.3` | 0.6–0.9 | 90 days |
| `trait` | Stable user characteristic | `consistency: "high", initiation: "low"` | 0.5–0.8 | Indefinite |
| `decision` | Past decision made | `framework_choice: "React over Vue"` | 0.5–0.7 | Indefinite |
| `fact` | Factual information about user | `current_year: 3`, `major: "CSE"` | 0.4–0.6 | Until invalidated |
| `skill` | Skill-related information | `skill_level: {python: "intermediate"}` | 0.6–0.8 | Indefinite |
| `observation` | Contextual observation not yet confirmed as pattern | `mentioned_job_search: true` | 0.2–0.4 | 30 days |
| `correction` | Explicit user correction to ARIA behavior | `preferred_ formality: "casual"` | 0.8–0.95 | Indefinite |

### Importance Scoring Algorithm

```python
def calculate_importance(
    memory_value: Any,
    category: str,
    source: str = "extracted",
    days_old: int = 0,
    access_count: int = 0,
    is_correction: bool = False,
) -> float:
    """
    Composite importance scoring.
    
    Factors:
    - Base importance by category
    - Recency bonus (newer = more important)
    - Frequency bonus (often accessed = more important)
    - Source authority (explicit > event_driven > consolidated > extracted)
    - Correction multiplier (user corrections are high-value)
    """
    
    # Base importance by category
    CATEGORY_BASE = {
        "preference": 0.6,
        "pattern": 0.7,
        "trait": 0.5,
        "decision": 0.5,
        "fact": 0.4,
        "skill": 0.6,
        "observation": 0.2,
        "correction": 0.8,
    }
    
    score = CATEGORY_BASE.get(category, 0.4)
    
    # Recency bonus
    if days_old < 1:
        score += 0.2
    elif days_old < 7:
        score += 0.15
    elif days_old < 30:
        score += 0.05
    
    # Frequency bonus
    if access_count > 20:
        score += 0.15
    elif access_count > 10:
        score += 0.10
    elif access_count > 5:
        score += 0.05
    
    # Source authority
    SOURCE_BONUS = {
        "explicit": 0.20,
        "event_driven": 0.15,
        "consolidated": 0.10,
        "extracted": 0.05,
        "inferred": 0.0,
    }
    score += SOURCE_BONUS.get(source, 0.0)
    
    # Correction multiplier
    if is_correction or category == "correction":
        score *= 1.2
    
    return min(1.0, max(0.0, score))
```

### Retrieval

```python
async def get_semantic_context(
    user_id: str, 
    top_k: int = 20,
    min_importance: float = 0.3,
    preferred_categories: list[str] | None = None,
) -> list[dict]:
    """
    Retrieve highest-importance semantic memories for context building.
    
    Parameters:
        top_k: Maximum memories to return
        min_importance: Minimum importance threshold
        preferred_categories: Boost these categories' scores
    """
    query = (
        supabase.from_("aria_memory")
        .select("key, value, importance, category, confidence, tags")
        .eq("user_id", user_id)
        .gte("importance", min_importance)
        .order("importance", ascending=False)
        .limit(top_k)
    )
    
    response = await query.execute()
    memories = response.data
    
    # Update access tracking (fire-and-forget for performance)
    asyncio.create_task(_update_access_tracking(user_id, memories))
    
    # Category boost for preferred categories
    if preferred_categories:
        for memory in memories:
            if memory["category"] in preferred_categories:
                memory["importance"] = min(1.0, memory["importance"] * 1.2)
        memories.sort(key=lambda x: x["importance"], reverse=True)
    
    return memories


async def _update_access_tracking(user_id: str, memories: list[dict]):
    """Increment access count and update last_accessed timestamp."""
    for memory in memories:
        await (
            supabase.from_("aria_memory")
            .update({
                "access_count": supabase.raw("access_count + 1"),
                "last_accessed": datetime.now().isoformat(),
            })
            .eq("user_id", user_id)
            .eq("key", memory["key"])
            .execute()
        )
```

### Lifecycle

| Stage | Trigger | Action |
|-------|---------|--------|
| **Create** | Consolidation pipeline, explicit user statement, event-driven trigger | Insert into `aria_memory` with computed importance |
| **Read** | Context assembly, direct memory query | Fetch with importance ordering; update access tracking |
| **Update** | New information supersedes old, user correction, reinforcement from feedback | Update value, increment version, recalculate importance |
| **Decay** | Weekly cron, last_accessed > 90 days | Multiply importance by 0.8 |
| **Archive** | Importance drops below 0.1 | Move to `aria_memory_archive` table; exclude from context assembly |
| **Delete** | User request, privacy purge | Cascade delete all user memories |
| **Export** | User data portability request | Serialize all user memories to JSON |

---

## Tier 4: Procedural Memory

### Purpose

Procedural memory stores knowledge about *how to do things* — workflows, skills, processes, and action sequences. Unlike Semantic Memory (which stores *what* the system knows about the user), Procedural Memory stores *how* the system should operate, interact, and execute tasks. This tier enables ARIA to learn and refine its operational behavior over time.

### What Procedural Memory Contains

| Category | Description | Example |
|----------|-------------|---------|
| **Workflow Templates** | Multi-step processes for common tasks | "How to help user set up a study plan" |
| **Skill Execution** | How to use a specific tool or API | "How to query the knowledge graph for skill gaps" |
| **Interaction Patterns** | Preferred response formats for scenarios | "When giving course recommendations, always include difficulty level" |
| **Error Recovery** | How to handle specific failure modes | "When a Supabase query fails, retry once then return cached fallback" |
| **Behavioral Rules** | Hard rules learned from corrections | "If user asks about deadlines, always check overdue_count first" |
| **Contextual Actions** | Actions to take automatically in contexts | "When user mentions exam, retrieve upcoming exam dates from calendar" |

### Storage Schema

**Table: `procedural_memory`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | PK | Unique identifier |
| `user_id` | `uuid` | FK → users(id), NOT NULL, INDEX | Tenant ownership |
| `trigger` | `text` | NOT NULL, INDEX | Condition that activates this procedure |
| `trigger_type` | `text` | CHECK(...) | keyword, intent, pattern, schedule, event |
| `procedure` | `jsonb` | NOT NULL | Steps, parameters, preconditions, postconditions |
| `version` | `int` | DEFAULT 1 | Incremented on updates |
| `effectiveness` | `float` | DEFAULT 0.5, CHECK(0.0–1.0) | How well this procedure achieves its goal |
| `execution_count` | `int` | DEFAULT 0 | How many times this was invoked |
| `success_count` | `int` | DEFAULT 0 | How many times it succeeded |
| `tags` | `jsonb` | DEFAULT '[]'::jsonb | Categorization tags |
| `created_at` | `timestamptz` | DEFAULT now() | Creation timestamp |
| `updated_at` | `timestamptz` | DEFAULT now() | Last modification |

### Procedure Schema (JSONB)

```python
procedure_schema = {
    "trigger": {
        "type": "string",                    # Activation condition
        "match_mode": "exact|fuzzy|regex",   # Matching strategy
        "priority": 0.0–1.0,                 # Priority vs other matching procedures
    },
    "steps": [
        {
            "order": 1,
            "action": "query|transform|generate|store|notify",
            "params": {},                     # Action-specific parameters
            "timeout_ms": 5000,               # Per-step timeout
            "retry_count": 2,                 # Retries on failure
            "fallback": "skip|abort|default",
        }
    ],
    "preconditions": [
        {"condition": "has_entity(user_id)", "on_fail": "skip"},
    ],
    "postconditions": [
        {"assertion": "memory_stored", "action": "log_success"},
    ],
    "metadata": {
        "author": "system|user|learned",
        "learning_source": "extracted|manual|customized",
        "last_reviewed": "datetime",
        "effectiveness_history": [float],
    }
}
```

### Learning Procedures from Experience

```python
async def learn_procedure_from_interaction(
    user_id: str,
    trigger_intent: str,
    actions_taken: list[dict],
    outcome: str,  # "success" | "failure" | "partial"
):
    """
    Extract and store a procedure from a successful multi-step interaction.
    
    This enables ARIA to remember how it handled similar situations
    and replicate effective patterns.
    """
    # Check if similar procedure exists
    existing = await (
        supabase.from_("procedural_memory")
        .select("*")
        .eq("user_id", user_id)
        .contains("trigger", {"type": trigger_intent})
        .execute()
    )
    
    if existing.data:
        # Update existing procedure with new execution data
        proc = existing.data[0]
        new_proc = merge_procedures(proc["procedure"], actions_taken)
        await (
            supabase.from_("procedural_memory")
            .update({
                "procedure": new_proc,
                "version": proc["version"] + 1,
                "execution_count": proc["execution_count"] + 1,
                "success_count": proc["success_count"] + (1 if outcome == "success" else 0),
                "effectiveness": calculate_procedure_effectiveness(proc),
                "updated_at": datetime.now().isoformat(),
            })
            .eq("id", proc["id"])
            .execute()
        )
    else:
        # Create new procedure
        await supabase.from_("procedural_memory").insert({
            "user_id": user_id,
            "trigger": trigger_intent,
            "trigger_type": "intent",
            "procedure": {"steps": actions_taken},
            "execution_count": 1,
            "success_count": 1 if outcome == "success" else 0,
            "effectiveness": 0.5,
        }).execute()
```

### Procedure Retrieval & Activation

```python
async def get_applicable_procedures(
    user_id: str, 
    current_intent: str,
    context: dict,
    top_k: int = 3,
) -> list[dict]:
    """Find procedures matching the current interaction context."""
    response = await (
        supabase.from_("procedural_memory")
        .select("*")
        .eq("user_id", user_id)
        .gte("effectiveness", 0.3)
        .order("effectiveness", ascending=False)
        .limit(top_k * 3)  # Over-fetch for fuzzy matching
        .execute()
    )
    
    candidates = []
    for proc in response.data:
        match_score = match_trigger(proc["trigger"], current_intent, context)
        if match_score > 0.0:
            candidates.append({
                "procedure": proc,
                "match_score": match_score,
            })
    
    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates[:top_k]
```

---

## Memory Serialization

### Purpose

Memory serialization defines how memory content is transformed between its storage format (database rows) and the format consumed by the AI (compressed, structured context strings). Proper serialization minimizes token usage while preserving semantic fidelity.

### Compression Strategy

| Technique | Compression Ratio | Quality Impact | When Applied |
|-----------|------------------|----------------|--------------|
| **Truncation** | Variable | Low (loses tail) | Messages exceeding max_length |
| **Summarization** | 5:1–20:1 | Medium (semantic preservation) | Episodic consolidation |
| **Deduplication** | 1.1:1–5:1 | None (identical content) | Pre-storage for semantic memory |
| **Structured Encoding** | 2:1–5:1 | Low (structure preserved) | Memory values with repeated schema |
| **Pruning (Low-Importance)** | 1.5:1–10:1 | Low (low-value content removed) | Context assembly when over budget |

### Serialization Format

```python
def serialize_memory_to_context(
    working_memory: dict,
    episodic_messages: list[dict],
    semantic_memories: list[dict],
    token_budget: int = 4000,
) -> str:
    """
    Assemble and serialize all memory tiers into a single context string.
    
    Output format is structured text optimized for LLM consumption:
    - Tier 0: Raw recent messages (verbatim)
    - Tier 1: Structured key-value pairs (compressed)
    - Tier 2: Summarized recent history (summarized)
    - Tier 3: Prioritized long-term knowledge (ranked by importance)
    """
    sections = []
    remaining_budget = token_budget
    
    # Tier 0: Buffer (raw, high priority)
    buffer_text = serialize_buffer(working_memory.get("last_3_messages", []))
    buffer_tokens = estimate_tokens(buffer_text)
    sections.append(("BUFFER", buffer_text))
    remaining_budget -= buffer_tokens
    
    # Tier 1: Working Memory (structured, compact)
    working_text = serialize_working_memory_compact(working_memory)
    working_tokens = estimate_tokens(working_text)
    if working_tokens <= remaining_budget:
        sections.append(("CURRENT STATE", working_text))
        remaining_budget -= working_tokens
    
    # Tier 2: Episodic (summarized if needed)
    episodic_text = serialize_episodic_compact(episodic_messages, remaining_budget)
    episodic_tokens = estimate_tokens(episodic_text)
    sections.append(("RECENT HISTORY", episodic_text))
    remaining_budget -= episodic_tokens
    
    # Tier 3: Semantic (prioritized by importance)
    semantic_text = serialize_semantic_priority_ordered(
        semantic_memories, remaining_budget
    )
    sections.append(("ABOUT YOU", semantic_text))
    
    # Assemble
    context_parts = []
    for section_name, section_content in sections:
        if section_content.strip():
            context_parts.append(f"[{section_name}]\n{section_content}")
    
    return "\n\n".join(context_parts)


def serialize_working_memory_compact(wm: dict) -> str:
    """Serialize working memory as compact key-value pairs."""
    lines = []
    
    # Identity
    lines.append(f"User: {wm.get('identity', {}).get('user_name', 'Unknown')}")
    
    # Temporal
    temporal = wm.get("temporal", {})
    if temporal.get("time_of_day"):
        lines.append(f"Time: {temporal.get('time_of_day')} on {temporal.get('day_of_week')}")
    
    # State (compact)
    state = wm.get("state", {})
    state_items = []
    if state.get("tasks_today_count") is not None:
        state_items.append(f"tasks: {state['tasks_today_count']}")
    if state.get("overdue_count") is not None and state["overdue_count"] > 0:
        state_items.append(f"overdue: {state['overdue_count']}")
    if state.get("active_goals_count") is not None:
        state_items.append(f"goals: {state['active_goals_count']}")
    if state_items:
        lines.append(" | ".join(state_items))
    
    return "\n".join(lines)


def serialize_episodic_compact(messages: list[dict], budget: int) -> str:
    """Serialize episodic messages, summarizing older ones."""
    lines = []
    budget_per_message = max(50, budget // max(len(messages), 1))
    
    for msg in messages:
        role_tag = "U" if msg["role"] == "user" else "A"
        content = msg.get("message_summary") or msg.get("message", "")
        
        # Truncate if needed
        content_tokens = estimate_tokens(content)
        if content_tokens > budget_per_message:
            content = truncate_to_tokens(content, budget_per_message)
        
        lines.append(f"[{role_tag}] {content}")
    
    return "\n".join(lines)
```

### Token Estimation

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars ≈ 1 token for English text)."""
    return len(text) // 4 + 1

def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximately max_tokens."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 20] + "... [truncated]"
```

---

## Memory Consolidation

### Purpose

Memory consolidation is the process of transferring information from short-term, high-fidelity storage (Episodic) to long-term, compressed, generalized storage (Semantic and Procedural). It is the mechanism by which raw interaction data becomes durable user knowledge.

### Consolidation Pipeline

```
┌──────────────────┐
│  Raw Episodic     │  Chat messages, event logs
│  Entries          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  1. Filter       │  Remove: system messages, noise, duplicates
│     & Clean      │  Keep: user messages, ARIA responses, corrections
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. Group        │  Group by: session, topic, temporal proximity
│     & Segment    │  Output: coherent interaction clusters
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. Summarize    │  LLM summarization per cluster
│                  │  Input: 5-20 messages → Output: 3-5 sentence summary
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. Extract      │  Pattern detection, preference extraction
│     Signals      │  Decision logging, fact extraction
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  5. Score        │  Calculate importance, confidence
│     & Rank       │  Assign category, source metadata
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  6. Store        │  Upsert into aria_memory (Semantic)
│                  │  Insert/update procedural_memory
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  7. Cleanup      │  Update consolidation log
│     & Log        │  Mark processed episodes
└──────────────────┘
```

### Consolidation Strategies

#### Strategy A: Batch Consolidation (Daily Cron)

- **Schedule**: Every 24 hours at midnight
- **Scope**: All unprocessed episodic entries from the last 24–48 hours
- **Method**: LLM-based extraction with structured output format
- **Token Cost**: ~2000–4000 tokens per consolidation cycle
- **Latency Tolerance**: 30–60 seconds (background job)

#### Strategy B: Incremental Consolidation (Event-Driven)

- **Trigger**: High-significance events (corrections, decisions, explicit preferences)
- **Scope**: Single interaction or message
- **Method**: Rule-based extraction with optional LLM verification
- **Token Cost**: ~200–500 tokens per event
- **Latency Tolerance**: 1–3 seconds (inline with response)

#### Strategy C: Periodic Deep Consolidation (Weekly)

- **Schedule**: Every Sunday
- **Scope**: All episodic entries from the last 7 days
- **Method**: Full LLM analysis with cross-session pattern detection
- **Token Cost**: ~8000–16000 tokens
- **Latency Tolerance**: 2–5 minutes (background job)

### Prompt Templates for Consolidation

#### Pattern Detection Prompt

```
<system>
You are analyzing a conversation history for behavioral patterns.
Extract any recurring patterns in the user's behavior, preferences, 
or decision-making. Focus on patterns that would help personalize
future interactions.

Output format (JSON):
{
  "patterns": [
    {
      "key": "short_descriptive_key",
      "value": "description of the pattern",
      "confidence": 0.0-1.0,
      "evidence": ["specific example from conversation"]
    }
  ],
  "preferences": [
    {
      "key": "preference_key",
      "value": "preference value",
      "confidence": 0.0-1.0
    }
  ],
  "decisions": [
    {
      "topic": "what was decided",
      "choice": "the option chosen",
      "alternatives": ["rejected options"]
    }
  ]
}
</system>

<conversation>
{episodic_batch}
</conversation>
```

#### Preference Extraction Prompt

```
<system>
Extract explicit and implicit user preferences from the following 
conversation. Include preferences about:
- Study habits (time, place, duration, subjects)
- Communication style (formality, detail level, tone)
- Task management (organization, priority, deadlines)
- Learning style (video, text, hands-on, group)
- Tool/programming language preferences
</system>

<conversation>
{conversation_text}
</conversation>
```

---

## Memory Retrieval

### Retrieval Architecture

```
User Query / Context Request
    │
    ▼
┌──────────────────────────────┐
│ Query Analyzer               │
│ - Parse user intent          │
│ - Determine retrieval scope  │
│ - Select retrieval strategy  │
└──────────┬───────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌──────────┐ ┌──────────┐
│Episodic  │ │Semantic  │
│Retrieval │ │Retrieval │
│Engine    │ │Engine    │
└────┬─────┘ └────┬─────┘
    │             │
    └──────┬──────┘
           ▼
┌──────────────────────────────┐
│ Scoring & Ranking            │
│ - Recency boost              │
│ - Relevance scoring          │
│ - Importance weighting       │
│ - Category preference boost  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Context Assembly             │
│ - Merge with working memory  │
│ - Token budget enforcement   │
│ - Serialize to LLM format    │
└──────────┬───────────────────┘
           │
           ▼
    Assembled Context
```

### Scoring Functions

```python
@dataclass
class RetrievalScore:
    base_score: float        # Raw importance from memory store
    recency_boost: float     # Temporal proximity multiplier
    frequency_boost: float   # Access frequency multiplier
    relevance_score: float   # Query-specific relevance
    final_score: float       # Composite for ranking


def score_memory_for_retrieval(
    memory: dict,
    query_intent: str | None = None,
    current_time: datetime | None = None,
) -> RetrievalScore:
    """Compute composite retrieval score for a memory entry."""
    now = current_time or datetime.now()
    created = datetime.fromisoformat(memory.get("created_at", now.isoformat()))
    last_accessed = datetime.fromisoformat(memory.get("last_accessed", now.isoformat()))
    
    # Base: stored importance
    base = memory.get("importance", 0.5)
    
    # Recency boost: quadratic decay over 90 days
    days_since_access = (now - last_accessed).days
    recency = max(0.0, 1.0 - (days_since_access / 90) ** 2) * 0.3
    
    # Frequency boost: logarithmic scaling
    access_count = memory.get("access_count", 0)
    frequency = min(0.2, math.log10(access_count + 1) * 0.05)
    
    # Relevance (if query intent provided)
    relevance = 0.0
    if query_intent and memory.get("tags"):
        relevance = compute_semantic_relevance(query_intent, memory["tags"]) * 0.2
    
    final = min(1.0, base + recency + frequency + relevance)
    
    return RetrievalScore(
        base_score=base,
        recency_boost=recency,
        frequency_boost=frequency,
        relevance_score=relevance,
        final_score=final,
    )
```

### Recency Boost Formula

```python
def recency_boost(last_accessed: datetime, now: datetime | None = None) -> float:
    """
    Quadratic decay curve.
    
    - 0 days ago: +0.30 boost
    - 30 days ago: +0.20 boost  
    - 60 days ago: +0.07 boost
    - 90+ days ago: +0.00 boost
    """
    now = now or datetime.now()
    days = (now - last_accessed).days
    if days >= 90:
        return 0.0
    return 0.3 * (1.0 - (days / 90) ** 2)
```

### Hybrid Retrieval (Episodic + Semantic)

```python
async def hybrid_retrieval(
    user_id: str,
    query_intent: str | None = None,
    top_k_episodic: int = 5,
    top_k_semantic: int = 15,
    token_budget: int = 2000,
) -> dict:
    """
    Retrieve and merge episodic + semantic memories within token budget.
    
    Strategy:
    - Always include top-3 episodic (recency best)
    - Always include top-5 semantic (importance best)
    - Fill remaining budget with scored remainder
    """
    # Parallel retrieval
    episodic_task = get_episodic_last_n(user_id, limit=top_k_episodic)
    semantic_task = get_semantic_context(user_id, top_k=top_k_semantic)
    
    episodic, semantic = await asyncio.gather(episodic_task, semantic_task)
    
    # Score all candidates
    all_candidates = []
    
    for m in episodic:
        score = score_memory_for_retrieval(m, query_intent)
        all_candidates.append({"data": m, "score": score, "tier": "episodic"})
    
    for m in semantic:
        score = score_memory_for_retrieval(m, query_intent)
        all_candidates.append({"data": m, "score": score, "tier": "semantic"})
    
    # Sort by final score
    all_candidates.sort(key=lambda x: x["score"].final_score, reverse=True)
    
    # Fill within budget (guarantee min from each tier)
    selected = []
    token_count = 0
    
    # Guarantee: top 3 episodic
    episodic_added = 0
    for c in all_candidates:
        if c["tier"] == "episodic" and episodic_added < 3:
            tokens = estimate_tokens(str(c["data"]))
            selected.append(c)
            token_count += tokens
            episodic_added += 1
    
    # Guarantee: top 5 semantic
    semantic_added = 0
    for c in all_candidates:
        if c["tier"] == "semantic" and semantic_added < 5 and c not in selected:
            tokens = estimate_tokens(str(c["data"]))
            selected.append(c)
            token_count += tokens
            semantic_added += 1
    
    # Fill remainder by score
    for c in all_candidates:
        if c in selected:
            continue
        tokens = estimate_tokens(str(c["data"]))
        if token_count + tokens <= token_budget:
            selected.append(c)
            token_count += tokens
    
    return {
        "memories": selected,
        "total_tokens": token_count,
        "budget_used_pct": round(token_count / token_budget * 100, 1),
    }
```

---

## Memory Lifecycle

### State Machine

```
           ┌──────────────┐
           │   CREATE     │
           │ (New memory) │
           └──────┬───────┘
                  │
                  ▼
           ┌──────────────┐
           │   ACTIVE     │◄────────────────────┐
           │ (In context) │                     │
           └──────┬───────┘                     │
                  │                             │
         ┌────────┴────────┐                    │
         │                 │                    │
         ▼                 ▼                    │
   ┌──────────┐    ┌──────────────┐            │
   │ CONSOLID.│    │  REINFORCE   │────────────┘
   │ (to long │    │ (accessed)   │  (access updates)
   │  term)   │    └──────┬───────┘
   └────┬─────┘           │
        │                 │
        ▼                 ▼
   ┌──────────────────────────┐
   │          DECAY           │
   │  (importance * 0.8 if    │
   │   last_accessed > 90d)   │
   └────────────┬─────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   ┌──────────┐   ┌──────────┐
   │ ARCHIVE  │   │  FORGET  │
   │ (import  │   │ (import  │
   │  < 0.1)  │   │  < 0.05) │
   └──────────┘   └──────────┘
```

### Lifecycle Rules

| Stage | Condition | Action | Frequency |
|-------|-----------|--------|-----------|
| **CREATE** | New data from interaction, consolidation, or explicit input | Insert into `aria_memory` with computed importance | On every significant interaction |
| **ACTIVE** | Importance >= 0.1 | Included in context assembly queries | Every AI request |
| **CONSOLIDATE** | Scheduled cron or event trigger | Summarize episodic → semantic | Daily + event-driven |
| **REINFORCE** | Memory accessed and led to accepted suggestion | importance += 0.05, access_count += 1 | On user acceptance |
| **WEAKEN** | Suggestion based on this memory was rejected | importance -= 0.1 | On user rejection |
| **DECAY** | last_accessed > 90 days (weekly cron) | importance *= 0.8 | Weekly |
| **ARCHIVE** | importance < 0.1 after decay | Move from `aria_memory` to `aria_memory_archive` | Weekly |
| **FORGET** | importance < 0.05 after decay OR user explicitly deletes | DELETE from archive | Monthly + on request |
| **PURGE** | User account deletion or privacy request | CASCADE DELETE all user memories | On account deletion |

### Decay Implementation

```python
async def run_memory_decay():
    """
    Weekly maintenance job.
    
    Reduces importance of unused memories and archives forgotten ones.
    """
    now = datetime.now()
    decay_cutoff = (now - timedelta(days=90)).isoformat()
    
    # Step 1: Decay importance of old unaccessed memories
    decay_result = await (
        supabase.from_("aria_memory")
        .update({"importance": supabase.raw("GREATEST(0.05, importance * 0.8)")})
        .lt("last_accessed", decay_cutoff)
        .gte("importance", 0.1)
        .execute()
    )
    
    logger.info(f"Memory decay applied to {len(decay_result.data)} memories")
    
    # Step 2: Archive memories below threshold
    archive_result = await (
        supabase.from_("aria_memory")
        .select("*")
        .lt("importance", 0.1)
        .execute()
    )
    
    for memory in archive_result.data:
        # Move to archive table
        await supabase.from_("aria_memory_archive").insert(memory).execute()
        await supabase.from_("aria_memory").delete().eq("id", memory["id"]).execute()
    
    logger.info(f"Archived {len(archive_result.data)} forgotten memories")


async def reinforce_memory(memory_id: str):
    """Called when a suggestion based on this memory is accepted."""
    await (
        supabase.from_("aria_memory")
        .update({
            "importance": supabase.raw("LEAST(1.0, importance + 0.05)"),
            "access_count": supabase.raw("access_count + 5"),
            "last_accessed": datetime.now().isoformat(),
        })
        .eq("id", memory_id)
        .execute()
    )


async def weaken_memory(memory_id: str):
    """Called when a suggestion based on this memory is rejected."""
    await (
        supabase.from_("aria_memory")
        .update({
            "importance": supabase.raw("GREATEST(0.0, importance - 0.1)"),
            "last_accessed": datetime.now().isoformat(),
        })
        .eq("id", memory_id)
        .execute()
    )
```

---

## Memory Performance

### Storage Size Estimates

| Tier | Table | Per-User Row Count | Avg Row Size | Total Size (1 user) | Total Size (1000 users) |
|------|-------|-------------------|-------------|---------------------|-------------------------|
| Tier 1 | (in-memory) | — | ~2 KB | ~2 KB (volatile) | ~2 MB (volatile) |
| Tier 2 | `chat_messages` | 10,000–50,000 | ~2 KB | ~20–100 MB | ~20–100 GB |
| Tier 3 | `aria_memory` | 200–2,000 | ~1 KB | ~0.2–2 MB | ~0.2–2 GB |
| Tier 3 | `aria_memory_archive` | 500–5,000 | ~1 KB | ~0.5–5 MB | ~0.5–5 GB |
| Tier 4 | `procedural_memory` | 20–200 | ~3 KB | ~60–600 KB | ~60–600 MB |

### Retrieval Latency Budget

| Operation | Target | Warning | Critical | Notes |
|-----------|--------|---------|----------|-------|
| Tier 0: Buffer read | < 1 ms | > 5 ms | > 10 ms | In-memory, local variable |
| Tier 1: Working memory build | < 200 ms | > 500 ms | > 1000 ms | Parallelized Supabase queries |
| Tier 2: Episodic (last-N) | < 50 ms | > 100 ms | > 200 ms | Indexed query, limit N=10 |
| Tier 3: Semantic (top-K) | < 50 ms | > 100 ms | > 200 ms | Indexed query, limit K=20 |
| Tier 3: Semantic (importance update) | < 30 ms | > 50 ms | > 100 ms | Fire-and-forget after retrieval |
| Tier 4: Procedural match | < 100 ms | > 200 ms | > 500 ms | Pattern matching overhead |
| Full context assembly | < 400 ms | < 800 ms | > 1500 ms | Sum of all tiers + serialization |
| Consolidation (daily) | < 30 s | < 60 s | > 120 s | Background job, not user-facing |

### Token Budget Summary

```
Total Context Budget: 4000 tokens
    ├── Tier 0 Buffer:         200 tokens  (5%)
    ├── Tier 1 Working:       1200 tokens  (30%)
    ├── Tier 2 Episodic:       600 tokens  (15%)
    ├── Tier 3 Semantic:       800 tokens  (20%)
    ├── System Instructions:   800 tokens  (20%)
    └── User Message:          400 tokens  (10%)
```

### Caching Strategy

| Cache | Scope | TTL | Hit Rate Target | Benefit |
|-------|-------|-----|-----------------|---------|
| Working memory (partial) | Per-user, read-only fields | 60 s | 70% | Reduces Supabase queries by 70% for repeated requests within same minute |
| Semantic memory (top-20) | Per-user | 5 min | 80% | Avoids re-ranking on every request |
| Graph nodes | Per-user | 15 min | 85% | Graph queries are expensive |
| Procedural memories | Global (read-only templates) | 1 hour | 90% | System procedures rarely change |

---

## Memory Privacy

### Privacy Principles

1. **User Ownership** — All memory data belongs to the user. ARIA is a custodian, not an owner.
2. **Transparency** — Users can view what memories are stored about them at any time.
3. **Control** — Users can modify, archive, or delete individual memories or purge all data.
4. **Minimality** — Only store memories that demonstrably improve the user experience.
5. **Segmentation** — Memories are never shared between users. No cross-tenant access.
6. **Compliance** — Architecture supports GDPR/CCPA data portability and right-to-deletion requests.

### What Is Stored

| Stored | Not Stored |
|--------|------------|
| User preferences and settings | Raw passwords or authentication tokens |
| Behavioral patterns and habits | Financial account details or transaction IDs |
| Learning goals and progress | Private messages not sent to ARIA |
| Past decisions and choices | Health data (beyond sleep/exercise logs) |
| Skill levels and interests | Location tracking (unless explicitly enabled) |
| Communication style preferences | Biometric data |

### User Control

```python
class MemoryPrivacyService:
    """Handles user-facing privacy operations."""

    @staticmethod
    async def get_all_memories(user_id: str) -> list[dict]:
        """Return all memories for user review."""
        response = await (
            supabase.from_("aria_memory")
            .select("key, value, importance, category, source, confidence, created_at, last_accessed, access_count")
            .eq("user_id", user_id)
            .order("category", ascending=True)
            .execute()
        )
        return response.data

    @staticmethod
    async def delete_memory(user_id: str, key: str) -> bool:
        """Delete a single memory by key."""
        response = await (
            supabase.from_("aria_memory")
            .delete()
            .eq("user_id", user_id)
            .eq("key", key)
            .execute()
        )
        return len(response.data) > 0

    @staticmethod
    async def delete_category(user_id: str, category: str) -> int:
        """Delete all memories of a given category."""
        response = await (
            supabase.from_("aria_memory")
            .delete()
            .eq("user_id", user_id)
            .eq("category", category)
            .execute()
        )
        return len(response.data)

    @staticmethod
    async def purge_user(user_id: str) -> dict:
        """Cascade delete all user memory data across all tiers."""
        results = {}
        
        # Tier 2: Episodic
        ep = await supabase.from_("chat_messages").delete().eq("user_id", user_id).execute()
        results["chat_messages"] = len(ep.data)
        
        # Tier 3: Semantic (active)
        sm = await supabase.from_("aria_memory").delete().eq("user_id", user_id).execute()
        results["aria_memory"] = len(sm.data)
        
        # Tier 3: Semantic (archived)
        ar = await supabase.from_("aria_memory_archive").delete().eq("user_id", user_id).execute()
        results["aria_memory_archive"] = len(ar.data)
        
        # Tier 4: Procedural
        pr = await supabase.from_("procedural_memory").delete().eq("user_id", user_id).execute()
        results["procedural_memory"] = len(pr.data)
        
        # Daily logs
        dl = await supabase.from_("daily_logs").delete().eq("user_id", user_id).execute()
        results["daily_logs"] = len(dl.data)
        
        return {
            "status": "purged",
            "deleted_counts": results,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    async def export_user_data(user_id: str) -> dict:
        """Export all user memory data for portability."""
        tasks = [
            supabase.from_("chat_messages").select("*").eq("user_id", user_id).execute(),
            supabase.from_("aria_memory").select("*").eq("user_id", user_id).execute(),
            supabase.from_("procedural_memory").select("*").eq("user_id", user_id).execute(),
            supabase.from_("daily_logs").select("*").eq("user_id", user_id).execute(),
        ]
        results = await asyncio.gather(*tasks)
        
        return {
            "exported_at": datetime.now().isoformat(),
            "chat_messages": results[0].data,
            "semantic_memories": results[1].data,
            "procedural_memories": results[2].data,
            "daily_logs": results[3].data,
            "total_entries": sum(len(r.data) for r in results),
        }
```

---

## Future Roadmap

### Phase 2: Vector Memory Store

```python
# Planned integration with pgvector
#
# -- Enable pgvector extension
# CREATE EXTENSION vector;
#
# -- Add embedding column to aria_memory
# ALTER TABLE aria_memory ADD COLUMN embedding vector(384);
#
# -- Semantic search over memories
# SELECT key, value, importance,
#        1 - (embedding <=> query_embedding) AS similarity
# FROM aria_memory
# WHERE user_id = target_user_id
# ORDER BY similarity DESC
# LIMIT 20;
```

| Feature | Status | Target |
|---------|--------|--------|
| pgvector embeddings on `aria_memory` | Planned | Q3 2026 |
| Embedding-based similarity search | Planned | Q3 2026 |
| Automatic re-embedding on memory update | Planned | Q3 2026 |
| Hybrid keyword + vector retrieval | Planned | Q4 2026 |

### Phase 3: Knowledge Graph Integration

- Semantic memory entities will link to knowledge graph nodes for cross-domain queries
- Graph traversal can discover related memories not surfaced by importance ranking
- See: [23_KnowledgeGraph.md](./23_KnowledgeGraph.md)

### Phase 4: Cross-User Anonymized Learning (Enterprise)

- Aggregate anonymized memory patterns across users (opt-in)
- Train default procedural memory templates from aggregate data
- Privacy-preserving differential privacy layer

---

## Appendix A: Memory Schema Reference

### `chat_messages` Table — Full DDL

```sql
CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id      UUID,
    role            TEXT NOT NULL CHECK (role IN ('user', 'aria', 'system')),
    message         TEXT NOT NULL,
    message_summary TEXT,
    token_count     INTEGER DEFAULT 0,
    metadata        JSONB DEFAULT '{}'::jsonb,
    interaction_type TEXT CHECK (
        interaction_type IN (
            'query', 'command', 'correction', 'decision',
            'creation', 'preference', 'greeting', 'farewell',
            'feedback', 'system'
        )
    ),
    parent_message_id UUID REFERENCES chat_messages(id),
    importance_score   FLOAT DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
    created_at         TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chat_messages_user_created ON chat_messages (user_id, created_at DESC);
CREATE INDEX idx_chat_messages_session ON chat_messages (user_id, session_id);
CREATE INDEX idx_chat_messages_type ON chat_messages (user_id, interaction_type) WHERE interaction_type IS NOT NULL;
CREATE INDEX idx_chat_messages_metadata_gin ON chat_messages USING GIN (metadata jsonb_path_ops);
```

### `aria_memory` Table — Full DDL

```sql
CREATE TABLE aria_memory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key             TEXT NOT NULL,
    value           JSONB NOT NULL,
    importance      FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
    category        TEXT NOT NULL CHECK (
        category IN (
            'preference', 'pattern', 'trait', 'decision',
            'fact', 'skill', 'observation', 'correction'
        )
    ),
    subcategory     TEXT,
    source          TEXT NOT NULL CHECK (
        source IN ('explicit', 'extracted', 'inferred',
                   'consolidated', 'event_driven', 'system')
    ),
    confidence      FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    ttl_days        INTEGER,
    version         INTEGER DEFAULT 1,
    parent_key      TEXT,
    tags            JSONB DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    last_accessed   TIMESTAMPTZ DEFAULT now(),
    access_count    INTEGER DEFAULT 0,
    UNIQUE (user_id, key)
);

CREATE INDEX idx_aria_memory_user_importance ON aria_memory (user_id, importance DESC);
CREATE INDEX idx_aria_memory_category ON aria_memory (user_id, category);
CREATE INDEX idx_aria_memory_last_accessed ON aria_memory (user_id, last_accessed);
CREATE INDEX idx_aria_memory_tags_gin ON aria_memory USING GIN (tags jsonb_path_ops);
```

### `procedural_memory` Table — Full DDL

```sql
CREATE TABLE procedural_memory (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trigger           TEXT NOT NULL,
    trigger_type      TEXT NOT NULL CHECK (
        trigger_type IN ('keyword', 'intent', 'pattern', 'schedule', 'event')
    ),
    procedure         JSONB NOT NULL,
    version           INTEGER DEFAULT 1,
    effectiveness     FLOAT DEFAULT 0.5 CHECK (effectiveness >= 0 AND effectiveness <= 1),
    execution_count   INTEGER DEFAULT 0,
    success_count     INTEGER DEFAULT 0,
    tags              JSONB DEFAULT '[]'::jsonb,
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_procedural_memory_trigger ON procedural_memory (user_id, trigger);
CREATE INDEX idx_procedural_memory_effectiveness ON procedural_memory (user_id, effectiveness DESC);
```

### `aria_memory_archive` Table — Full DDL

```sql
CREATE TABLE aria_memory_archive (
    LIKE aria_memory INCLUDING ALL,
    archived_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Appendix B: Consolidation Prompt Templates

### Pattern Detection Template

```text
You are analyzing a batch of conversation history to extract behavioral patterns.

Analyze the following messages between a user (U) and AI assistant (A).

For each pattern you identify, provide:
1. A unique key name (snake_case, max 50 chars)
2. A human-readable description
3. Confidence score (0.0–1.0)
4. Evidence — specific excerpts that support this pattern

Focus on:
- Productivity patterns (peak hours, procrastination triggers)
- Learning patterns (preferred formats, difficulty thresholds)
- Communication patterns (verbosity, formality, emotional tone)
- Decision-making patterns (decisiveness, deferral, reconsideration)
- Habit patterns (consistency, slippage, recovery)

Respond in JSON format only:
{
    "patterns": [...],
    "preferences": [...],
    "decisions": [...],
    "summary": "2-3 sentence overall assessment"
}
```

### Memory Consolidation Template

```text
Summarize the following conversation into long-term memory entries.

Extract the following if present:
1. User preferences (study habits, communication style, tool choices)
2. Behavioral patterns (recurring behaviors, trends)
3. Stable traits (personality characteristics)
4. Decisions made (with reasoning if available)
5. Factual information (academic status, goals, timeline)
6. Corrections (user corrections to AI behavior)

For each extracted memory, assign:
- Category: preference | pattern | trait | decision | fact | correction
- Importance: 0.0–1.0 (how useful for future personalization)
- Confidence: 0.0–1.0 (how certain we are)

Conversation:
{conversation_text}
```

---

## Appendix C: Error Handling Matrix

| Error Scenario | Detection | Fallback | User Impact |
|----------------|-----------|----------|-------------|
| Supabase query timeout (> 2s) | Timeout wrapper | Return cached state; log error | Slightly stale context |
| Working memory exceeds token budget | Token count check | Aggressive truncation per priority rules | Reduced context detail |
| Episodic retrieval fails | Exception handler | Return empty list | No conversation history this turn |
| Semantic memory retrieval fails | Exception handler | Return cached snapshot from request start | Previous context still available |
| Consolidation job fails | Job error handler | Retry 2x; skip to next day; alert | Memory learning delayed 24h |
| Memory update fails (non-critical) | Continue on error | Log error; skip this memory | Single memory not updated |
| Memory decay job fails | Job error handler | Retry at next scheduled time | Memories may retain old importance |
| Procedural memory match fails | Default fallback | Use system default procedures | Generic (non-personalized) response |

---

## Appendix D: Configuration Reference

```python
# config/memory.py
MEMORY_CONFIG = {
    # Tier 0: Buffer
    "buffer_capacity": 10,           # Max raw messages retained
    "buffer_token_budget": 200,      # Max tokens for buffer section
    
    # Tier 1: Working
    "working_token_budget": 1200,    # Max tokens for working memory
    "working_cache_ttl_sec": 60,     # Partial cache TTL for read-only fields
    
    # Tier 2: Episodic
    "episodic_last_n_default": 10,   # Default last-N retrieval count
    "episodic_lookback_days": 30,    # Default topic-filtered lookback
    "episodic_token_budget": 600,    # Max tokens for episodic section
    
    # Tier 3: Semantic
    "semantic_top_k_default": 20,    # Default retrieval count
    "semantic_min_importance": 0.3,  # Minimum importance for retrieval
    "semantic_token_budget": 800,    # Max tokens for semantic section
    "semantic_cache_ttl_sec": 300,   # Top-20 cache TTL
    
    # Consolidation
    "consolidation_schedule": "daily",   # daily | event | both
    "consolidation_lookback_hours": 24,  # Hours of episodic to process
    "deep_consolidation_cron": "0 3 * * 0",  # Weekly Sunday 3 AM
    
    # Decay
    "decay_cron": "0 2 * * 0",       # Weekly Sunday 2 AM
    "decay_threshold_days": 90,      # Days before decay applies
    "decay_factor": 0.8,             # Importance multiplier on decay
    "archive_threshold": 0.1,        # Below this → archive
    "forget_threshold": 0.05,        # Below this → delete
    
    # Performance
    "context_total_budget": 4000,    # Total token budget for assembly
    "retrieval_timeout_ms": 2000,    # Max time for all retrievals
}
```

---

## Appendix E: Related Documents

| Document | Description |
|----------|-------------|
| [21_AI_Architecture.md](./21_AI_Architecture.md) | Overall AI system architecture |
| [23_KnowledgeGraph.md](./23_KnowledgeGraph.md) | Knowledge graph integration |
| [24_AgentOrchestration.md](./24_AgentOrchestration.md) | Agent routing and task dispatch |
| [25_PromptEngineering.md](./25_PromptEngineering.md) | Prompt templates and system instructions |
| [Database_Schema.md](../engineering/database_schema.md) | Full database schema reference |
| [Memory_Consolidation_Service.md](../engineering/memory_consolidation_service.md) | Consolidation service implementation |
| [PRD.md](../product/PRD.md) | Product requirements document |
