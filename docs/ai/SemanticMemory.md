# Semantic Memory — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | AI-SEM-005 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [23_KnowledgeGraph.md](23_KnowledgeGraph.md), [LongTermMemory.md](LongTermMemory.md), [Embeddings.md](Embeddings.md) |

---

## 1. Executive Summary

Semantic memory is Tier 3 of the 5-tier memory model, responsible for storing and retrieving factual knowledge about the user, their preferences, behavioral patterns, and conceptual relationships. It integrates with the knowledge graph for entity relationship queries and uses embedding-based similarity for flexible retrieval.

---

## 2. Semantic Memory vs Other Memory Types

| Aspect | Episodic | Semantic | Procedural |
|---|---|---|---|
| **What** | Specific events | General knowledge | How to do things |
| **Example** | "User asked about DSA yesterday" | "User is in 3rd year CSE" | "User uses Pomodoro technique" |
| **Persistence** | 90 days full, 1yr compressed | Permanent (until decay) | Permanent |
| **Granularity** | Per-message | Extracted facts | Behavioral patterns |
| **Source** | chat_messages | Consolidation from episodic | Pattern detection from episodic |

---

## 3. Knowledge Graph Integration

Semantic memory entities are nodes in the knowledge graph:

```
Relation Types:
- IS_TYPE:      Task → "has status" → "pending"
- RELATED_TO:   Goal → "includes" → Task
- PREFERS:      User → "prefers" → "morning study"
- PATTERN:      User → "has pattern" → "90min focus blocks"
```

See [23_KnowledgeGraph.md](23_KnowledgeGraph.md) for full graph architecture.

---

## 4. Entity Extraction Pipeline

```mermaid
graph LR
    CHAT["Chat Messages"] --> NLP["NLP Processing<br/>NER + Intent Classification"]
    NLP --> EXTRACT["Entity Extraction<br/>People, Places, Concepts<br/>Relationships, Preferences"]
    EXTRACT --> SCORE["Importance Scoring<br/>Recency × Frequency × Source"]
    SCORE --> STORE["Store in aria_memory<br/>+ Knowledge Graph<br/>+ Embeddings Index"]

    style CHAT fill:#13151A,stroke:#6366F1,color:#F1F5F9
    style STORE fill:#13151A,stroke:#00FFA3,color:#F1F5F9
```

---

## 5. Semantic Query Examples

```sql
-- Find all user preferences
SELECT * FROM aria_memory
WHERE user_id = 'uuid'
  AND memory_type = 'preference'
ORDER BY confidence DESC;

-- Find memories about a specific topic
SELECT * FROM aria_memory
WHERE user_id = 'uuid'
  AND content ILIKE '%stud%'
ORDER BY last_referenced_at DESC;
```

---

## 6. Concept Hierarchy

```
User Knowledge
├── Academic
│   ├── Courses (udemy, coursera, college)
│   ├── Subjects (DSA, OS, CN)
│   └── Skills (Python, React, SQL)
├── Professional
│   ├── Income sources
│   ├── Projects
│   └── Opportunities
├── Personal
│   ├── Habits
│   ├── Health (sleep)
│   └── Preferences
└── Goals
    ├── Career goals
    ├── Learning goals
    └── Project goals
```

---

## 7. Cross-Module Semantic Linking

Semantic memory connects data across modules:

```python
# Example: Link a task to a course to a goal
linked_context = {
    "task": {"title": "Complete React Hooks tutorial", "status": "pending"},
    "course": {"title": "Complete React Course", "progress": 60},
    "goal": {"title": "Become full-stack developer", "target_date": "2026-12-31"},
    "semantic_memory": [
        {"type": "preference", "content": "User prefers hands-on learning"}
    ]
}
```

---

## 8. Related Documents

| Document | Description |
|---|---|
| [23_KnowledgeGraph.md](23_KnowledgeGraph.md) | Knowledge graph architecture |
| [LongTermMemory.md](LongTermMemory.md) | Long-term memory details |
| [Embeddings.md](Embeddings.md) | Embedding-based similarity search |
| [MemoryRetrieval.md](MemoryRetrieval.md) | Retrieval strategies |
