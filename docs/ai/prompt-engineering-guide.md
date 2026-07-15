# ARIA OS Prompt Engineering Guide

> **Internal reference for writing, testing, and maintaining AI prompts for the Second Brain OS agent system**

## Document Control

| Field | Value |
|---|---|
| **Document ID** | AI-PEG-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Review Cycle** | Bi-weekly |
| **Related Docs** | [Prompts README](/prompts/README.md), [PromptLoader](/packages/ai/prompt_loader.py), [Agent Architecture](/docs/ai/20_Agent.md), [AGENTS.md Â§9â€“11](/AGENTS.md), [Prompt Versioning](/docs/ai/PromptVersioning.md) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Prompt Architecture](#2-prompt-architecture)
3. [Prompt Structure Template](#3-prompt-structure-template)
4. [Token Budget Management](#4-token-budget-management)
5. [Temperature Guidelines](#5-temperature-guidelines)
6. [Testing Prompts](#6-testing-prompts)
7. [Versioning](#7-versioning)
8. [Common Pitfalls](#8-common-pitfalls)
9. [Prompt Review Process](#9-prompt-review-process)
10. [Quick Reference](#10-quick-reference)

---

## 1. Introduction

Prompt engineering is the single highest-leverage activity in the ARIA OS agent system. Every one of the **17 agents** (11 live, 6 in design) generates output that directly shapes the user's daily experience â€” briefings set their morning focus, nudges adjust their study habits, memory consolidation determines what the system remembers.

This guide covers the complete prompt lifecycle: **authoring â†’ frontmatter â†’ structure â†’ budgeting â†’ testing â†’ versioning â†’ review â†’ deployment**. Follow it for every prompt you create or modify.

### Why It Matters

| If prompts are... | User experiences... |
|---|---|
| Well-structured, consistent | Coherent, reliable AI behavior across all agents |
| Poorly versioned | Regressions, broken output parsing, silent failures |
| Under-budgeted | Truncated output, hallucinated completions |
| Over-specified | Rigid, robotic responses that ignore context |
| Missing edge cases | Surprising failures on empty data, errors, holidays |

---

## 2. Prompt Architecture

### 2.1 PromptLoader System

All prompts are externalized in `prompts/` and loaded at runtime by the `PromptLoader` singleton in `packages/ai/prompt_loader.py`. Every agent module imports it as:

```python
from ai.prompt_loader import prompts

# Recommended shorthand methods
entry = prompts.get_agent("briefing_agent")     # Returns PromptEntry | None
entry = prompts.get_system("aria_system")        # For system prompts
entry = prompts.get_template("context_assembly") # For templates

# Generic access
entry = prompts.get("agent_name", category="agents")
entry = prompts.get_required("agent_name")       # Raises PromptLoaderError if missing

# Rendering with variables
output = entry.render(tasks=tasks_data, user_name="Alex")

# Listing
all_prompts = prompts.list_prompts()
agent_names = prompts.list_prompts(category="agents")
categories = prompts.list_categories()
counts = prompts.count_prompts()
```

**Graceful degradation:** Every agent has inline fallback prompts. If the prompt file is missing, malformed, or the loader fails, the agent still works with a hardcoded default.

### 2.2 YAML Frontmatter Schema

Every prompt file MUST start with valid YAML frontmatter delimited by `---`. The `PromptLoader` parses and validates this on load.

#### Required Fields (ALL prompt types)

```yaml
---
version: 1.0.0              # semver â€” bumped on every change
status: active               # One of: active, draft, deprecated
model: ollama/mistral:7b     # Target AI model
max_tokens: 4096             # Token budget (MUST be a number, not string)
temperature: 0.5             # 0.0â€“1.0 (MUST be a number, not string)
---
```

| Field | Type | Constraints | Description |
|---|---|---|---|
| `version` | string | semver `MAJOR.MINOR.PATCH` | Updated per change type (see Â§7) |
| `status` | string | `active`, `draft`, or `deprecated` | Lifecycle stage |
| `model` | string | Any valid model ID | `ollama/mistral:7b`, `claude/sonnet-4`, etc. |
| `max_tokens` | number | Integer > 0 | Maximum output tokens the LLM is allowed |
| `temperature` | number | Float 0.0â€“1.0 | Creativity/randomness level |

#### Required Per Category

| Field | System | Agent | Template |
|---|---|---|---|
| `version` | âœ… Required | âœ… Required | âœ… Required |
| `status` | âœ… Required | âœ… Required | âœ… Required |
| `model` | âœ… Required | âœ… Required | âœ… Required |
| `max_tokens` | âœ… Required | âœ… Required | âœ… Required |
| `temperature` | âœ… Required | âœ… Required | âœ… Required |
| `description` | âœ… Required | Recommended | Recommended |
| `tags` | âœ… Required | âœ… Required | Recommended |

#### Optional (Recommended) Fields

```yaml
last_updated: 2026-06-11      # ISO date
approved_by: developer         # Who approved the current version
review_cycle: weekly           # How often to review
tags: [briefing, daily]       # Categorization for search
description: >                 # One-line summary
  Generates personalized morning briefings
```

#### Complete Frontmatter Example

```yaml
---
version: 2.1.0
status: active
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.6
description: >
  Generates personalized daily morning briefing
  synthesizing sleep, tasks, courses, habits, goals.
last_updated: 2026-06-11
approved_by: developer
review_cycle: weekly
tags: [briefing, morning, daily, sleep, task, goal]
---
```

### 2.3 File Organization

```
prompts/
â”œâ”€â”€ system/                     # 2 files â€” loaded at startup, cached
â”‚   â”œâ”€â”€ aria_system.md          # ARIA persona, capabilities, tone (v3.0.0, 369 lines)
â”‚   â””â”€â”€ guardrails.md           # Refusal categories, PII redaction (v2.0.0, 346 lines)
â”‚
â”œâ”€â”€ agents/                     # 18 files â€” one per agent module
â”‚   â”œâ”€â”€ briefing_agent.md       # Daily briefing generator (957 lines)
â”‚   â”œâ”€â”€ weekly_review_agent.md  # Weekly review generator (1264 lines)
â”‚   â”œâ”€â”€ memory_agent.md         # Memory consolidation (821 lines)
â”‚   â”œâ”€â”€ learning_agent.md       # Pattern detection (850 lines)
â”‚   â”œâ”€â”€ task_agent.md           # Task breakdown & analysis (839 lines)
â”‚   â”œâ”€â”€ sleep_agent.md          # Sleep analysis & wind-down (905 lines)
â”‚   â”œâ”€â”€ nudge_agent.md          # Course/habit nudges (665 lines)
â”‚   â”œâ”€â”€ opportunity_radar_agent.md  # Opportunity matching (822 lines)
â”‚   â”œâ”€â”€ opportunity_matching_agent.md  # Scoring engine (210 lines)
â”‚   â”œâ”€â”€ roadmap_agent.md        # Skill roadmap optimizer (257 lines)
â”‚   â”œâ”€â”€ skill_assessment_agent.md     # Skill assessment
â”‚   â”œâ”€â”€ skill_career_agent.md         # Career path analysis
â”‚   â”œâ”€â”€ skill_evidence_agent.md       # Evidence gathering
â”‚   â”œâ”€â”€ skill_intelligence_agent.md   # Market intelligence
â”‚   â”œâ”€â”€ skill_market_agent.md         # Market data
â”‚   â”œâ”€â”€ skill_opportunity_agent.md    # Opportunity detection
â”‚   â”œâ”€â”€ skill_recommendation_agent.md # Recommendation engine
â”‚   â””â”€â”€ skill_roadmap_agent.md        # Extended roadmap logic
â”‚
â””â”€â”€ templates/                  # 2 files â€” context builders, never sent to LLM directly
    â”œâ”€â”€ context_assembly.md     # Context packet structure, budgets, freshness
    â””â”€â”€ email_templates.md      # 9 email templates for notifications
```

### 2.4 Naming Convention

Prompt filenames use **snake_case** matching the agent module name:

```
prompts/agents/briefing_agent.md  â†â†’  packages/ai/agents/briefing_agent.py
prompts/agents/memory_agent.md    â†â†’  packages/ai/agents/memory_agent.py
```

The `README.md` in `prompts/` is governance documentation â€” it is automatically skipped by the `PromptLoader`.

---

## 3. Prompt Structure Template

Every prompt should follow this section order. This structure has been validated across all 18 agent prompts and consistently produces reliable output.

```markdown
---
<YAML frontmatter>
---

# <Agent Name>

## Role Definition

Define who the agent is, its purpose, tone, and constraints. Set expectations for how it should behave, what it should prioritize, and what boundaries it must respect.

**Keep to 3â€“5 paragraphs.** Cover: identity, purpose, key operating principles, and tone/voice guidelines.

## Input Schema

Document every input field the agent will receive. Use a table format:

| Field | Type | Description | Source |
|---|---|---|---|
| `tasks` | array | Pending tasks for today | tasks table, filtered by user_id |
| `sleep_score` | number | Last night's sleep score (0â€“100) | sleep_logs table |
| `streaks` | object | Active habit streaks | habit_logs aggregation |

Include defaults and edge cases (e.g., "empty array if no tasks").

## Output JSON Schema

Define the exact JSON structure the agent must return. Mark required vs optional fields.

```json
{
  "focus_area": "<string required â€” single most important task>",
  "motivation": "<string required â€” 1-2 sentence motivational message>",
  "top_tasks": "<array required â€” max 3 items>",
  "sleep_insight": "<string optional â€” only if sleep_score < 60>"
}
```

## Detailed Instructions

Step-by-step reasoning chain. Include:
- Priority rules (what takes precedence)
- Decision trees (if X then Y)
- Data weighting (which inputs matter most)
- Output formatting rules

**Use numbered steps** â€” agents follow them more reliably than paragraphs.

1. Evaluate sleep score: if < 60, deprioritize non-urgent tasks
2. Scan pending tasks sorted by priority â†’ due_date
3. Select top 3 tasks max â€” never recommend more
4. Check streak continuity and reinforce at-risk streaks

## Few-Shot Examples

**REQUIRED: 3â€“5 examples** showing realistic input/output pairs. Each should demonstrate a distinct scenario.

### Example 1: Normal Day

**Input:**
```
sleep_score: 78
tasks: [
  {"title": "Finish React project", "priority": "high", "due_date": "today"},
  {"title": "Read chapter 5", "priority": "medium", "due_date": "tomorrow"}
]
```

**Output:**
```json
{
  "focus_area": "Finish React project",
  "motivation": "You're 80% done â€” push through the last stretch today.",
  "top_tasks": [
    {"title": "Finish React project", "reason": "Due today, high priority"}
  ]
}
```

**Explanation:** Normal energy day, clear #1 priority identified.

### Example 2: Low Sleep

**Input:**
```
sleep_score: 42
tasks: [
  {"title": "Submit assignment", "priority": "high", "due_date": "today"},
  {"title": "Organize notes", "priority": "low", "due_date": "tomorrow"}
]
```

**Output:**
```json
{
  "focus_area": "Submit assignment",
  "motivation": "Rest today. Focus on what truly matters.",
  "top_tasks": [
    {"title": "Submit assignment", "reason": "Hard deadline, non-negotiable"}
  ],
  "sleep_insight": "Your sleep was poor. Consider a nap or early night."
}
```

**Explanation:** Low energy â€” only hard deadlines recommended, self-care emphasized.

(Add 1â€“3 more examples covering: deadline-day, weekend-mode, overdue-heavy, etc.)

## Edge Cases

Document how the agent should handle non-standard situations:

| Scenario | Expected Behavior |
|---|---|
| Empty task list | Return motivational message, suggest reviewing goals |
| Missing sleep data | Assume neutral energy, skip sleep insight field |
| All tasks completed | Congratulate user, suggest planning tomorrow |
| Holiday/weekend | Tone should be relaxed, avoid strict deadlines |
| Consecutive low scores (3+ days) | Escalate concern, suggest health resources |
| Multiple high-priority tasks | Choose one focus area, explain trade-off |

## Anti-Patterns

**DO NOT:**
- List more than 3 top tasks (overwhelms user)
- Use the same greeting two days in a row
- Recommend urgent action for non-urgent items
- Output generic platitudes ("You can do it!")
- Ignore sleep quality when recommending workload
- Contradict yourself between sections

## Quality Criteria

Self-check before output. Every generation MUST pass:

- [ ] Focus area is always a single item (never multiple)
- [ ] Top tasks never exceed 3 items
- [ ] Sleep insight only present when score < 60
- [ ] Tone matches: serious for deadlines, gentle for low sleep
- [ ] Greeting is unique (differs from recent briefings)
- [ ] No markdown in JSON output
- [ ] All required JSON fields present

## Error Recovery

When generation fails or produces invalid output:

1. **Validation error** (invalid JSON): re-request with stricter instructions
2. **Token budget exceeded**: truncate examples, keep instructions
3. **Model unavailable**: fall back to algorithmic briefing (no AI)
4. **Empty input context**: use defaults, skip agent-specific sections
5. **Circuit breaker open**: queue request, return cached briefing
```

---

## 4. Token Budget Management

### 4.1 Default Budgets

| Prompt Category | Default `max_tokens` | Typical Output |
|---|---|---|
| System prompts | 2048 | ~500 tokens (full context) |
| Agent prompts | 4096 | ~200â€“1200 tokens (varies by agent) |
| Templates | N/A | Not sent to LLM |

### 4.2 Token Estimation

A rough heuristic: **tokens â‰ˆ characters Ã· 4**

| Content | Characters | Estimated Tokens |
|---|---|---|
| Briefing output (~300 words) | ~1,800 | ~450 |
| Weekly review (~800 words) | ~4,800 | ~1,200 |
| Memory entry (~100 words) | ~600 | ~150 |
| Agent prompt body (full) | ~20,000â€“35,000 | ~5,000â€“8,750 |

### 4.3 Agent Token Budget Breakdown

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  System prompt    (1,600 tokens)    â”‚  â† aria_system.md + guardrails.md
â”‚  Context assembly (1,300â€“7,800)     â”‚  â† context_assembly.md rendered
â”‚  Agent prompt     (1,536â€“2,048)     â”‚  â† agent-specific instructions
â”‚  User input       (varies)          â”‚  â† current data packet
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
â”‚  Total context    (4,000â€“12,000)    â”‚
â”‚  Output budget    (2,048 max)       â”‚  â† max_tokens from frontmatter
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

| Agent | S+Guard | Context | Agent | Total | Output |
|---|---|---|---|---|---|
| briefing_agent | 1,600 | 7,800 | 2,048 | ~11,448 | ~800 |
| weekly_review_agent | 1,600 | 7,800 | 2,048 | ~11,448 | ~1,200 |
| nudge_agent | 1,600 | 7,800 | 2,048 | ~11,448 | ~400 |
| memory_agent | 1,600 | 2,500 | 2,048 | ~6,148 | ~300 |
| task_agent | 1,600 | 1,600 | 2,048 | ~5,248 | ~500 |
| sleep_agent | 1,600 | 600 | 1,536 | ~3,736 | ~400 |

### 4.4 Cost

| Provider | Cost | When Used |
|---|---|---|
| Ollama (Mistral 7B) | Free (local) | Default â€” all development and production |
| Claude Sonnet 4 | ~$0.003/req | Fallback if `USE_LOCAL_AI=False` |
| Claude (fallback chain) | ~$0.015/req | Fallback if Ollama circuit breaker opens |

**Monthly estimate (Ollama only):** ~50,000 tokens/day = **$0/month**
**Monthly estimate (Claude fallback):** ~500 requests Ã— $0.003 = **~$1.50/month**

### 4.5 Budget Rules

- Keep output under **1000 tokens** for all agents (except weekly review: 1500 max)
- If output consistently exceeds budget, increase `max_tokens` (never truncate silently)
- If agent prompt body exceeds 3000 tokens, split or prune examples
- Monitor budget utilization: target 70â€“85%, alert at >90% or <50%
- Use `render()` variables instead of hardcoding dynamic content in prompt bodies

---

## 5. Temperature Guidelines

Temperature controls the randomness/creativity of the model's output. Choose based on the task.

| Range | Use Case | Example Agents | Notes |
|---|---|---|---|
| **0.1â€“0.3** | Deterministic â€” extraction, classification, strict JSON | memory_agent, task_agent | Prefer lowest reliable temperature. JSON output must be parseable. |
| **0.3â€“0.5** | Balanced â€” structured generation with moderate variety | briefing_agent, weekly_review_agent | Good default for most agents. Consistent structure, varied language. |
| **0.5â€“0.7** | Creative â€” suggestions, ideas, motivational content | nudge_agent, sleep_agent | Allows for natural variation in tone and phrasing. |
| **0.7â€“1.0** | Exploratory â€” brainstorming, open-ended generation | (future design agents) | Risk of hallucination. Use sparingly. |

**Never use temperature 0.0.** Models can enter repetition loops at exactly zero, producing infinite repeating text.

**Current agent temperatures:**
- briefing_agent: 0.6 â€” balanced with creative morning greetings
- weekly_review_agent: 0.4 â€” structured but varied weekly summaries
- memory_agent: 0.2 â€” deterministic extraction and classification
- learning_agent: 0.4 â€” pattern recognition with some inference flexibility
- task_agent: 0.3 â€” reliable breakdowns with minor prioritization variance
- sleep_agent: 0.5 â€” structured recommendations with adaptive tone
- nudge_agent: 0.5 â€” escalation-aware with natural language variation
- opportunity_radar_agent: 0.4 â€” scoring with deterministic ranking
- opportunity_matching_agent: 0.3 â€” algorithmic scoring, low variance

---

## 6. Testing Prompts

### 6.1 Validation Pipeline

Every prompt must pass these checks before deployment:

```bash
# 1. Frontmatter validation â€” checks all 5 required fields, types, semver, status
python scripts/validate_prompts.py

# 2. Content tests â€” per-agent checks for keywords, minimum size, tags, imports
pytest tests/test_agent_prompts.py -v

# 3. Loader tests â€” loading, rendering, edge cases, error states
pytest tests/test_prompt_loader.py -v

# 4. Validation script unit tests
pytest tests/test_validate_script.py -v

# 5. All prompt-related tests
pytest tests/ -m "prompt or agent" -v
```

### 6.2 What the Tests Check

| Test File | Tests | What It Validates |
|---|---|---|
| `test_prompt_loader.py` (31 tests) | Loading, frontmatter, rendering, error cases | Every field present, correct types, fallback behavior |
| `test_agent_prompts.py` (42 tests) | Per-agent content, size, tags, imports | Body > 50 chars (all), > 1000 chars (agents), required tags, valid imports |
| `test_validate_script.py` (23 tests) | Validation script correctness | Script catches bad YAML, missing fields, invalid semver |

**Every prompt must pass:**
- 5 required frontmatter fields present and typed correctly
- `status` is one of: `active`, `draft`, `deprecated`
- `version` is valid semver (`MAJOR.MINOR.PATCH`)
- `max_tokens` and `temperature` are numbers (not strings)
- Body length > 50 characters
- Agent prompts: body > 1000 characters, `tags` field present

### 6.3 Manual Testing

```bash
# List all loaded prompts
python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"

# Inspect a specific prompt's frontmatter
python -c "from ai.prompt_loader import prompts; entry = prompts.get_agent('briefing_agent'); print(entry.frontmatter)"

# Print full prompt body
python -c "from ai.prompt_loader import prompts; print(prompts.get_agent('memory_agent').body)"

# Validate a single prompt
python -c "from ai.prompt_loader import prompts; print(prompts.validate_frontmatter('briefing_agent'))"

# Count prompts per category
python -c "from ai.prompt_loader import prompts; print(prompts.count_prompts())"
```

### 6.4 CI Enforcement

Validation happens automatically on every push:

1. **GitHub Actions CI**: runs `scripts/validate_prompts.py` + `pytest -m "prompt or agent"`
2. **Pre-commit hooks**: `validate-prompts` and `pytest-prompts` in `.pre-commit-config.yaml`
3. **Makefile**: `make validate-prompts` runs frontmatter checks on all files
4. **PR gate**: any prompt validation failure blocks merge

---

## 7. Versioning

### 7.1 Semver Rules

Every prompt file has an independent `version` field in its frontmatter.

| Bump | Criteria | Example | Frequency |
|---|---|---|---|
| **MAJOR** | Breaking output schema change | `1.0.0` â†’ `2.0.0` | Rare (quarterly) |
| **MINOR** | New fields, new sections, non-breaking expansion | `1.0.0` â†’ `1.1.0` | Monthly |
| **PATCH** | Wording fixes, clarifications, token optimization, examples | `1.0.0` â†’ `1.0.1` | Weekly |

**Examples of MAJOR changes:**
- Output JSON field renamed or removed
- Agent behavior fundamentally changes
- Model swap (e.g., Mistral 7B â†’ Claude)
- Input schema restructured

**Examples of MINOR changes:**
- New optional output field added
- New example scenario added
- New input data source integrated
- Additional instruction section added

**Examples of PATCH changes:**
- Typo fix or grammar improvement
- Token optimization (shortened examples)
- Clarification of existing instruction
- Updated date or metadata

### 7.2 Changelog Entry

When bumping a prompt version, update its frontmatter and document the change:

```yaml
# Old
version: 2.0.0
last_updated: 2026-06-01

# New
version: 2.1.0
last_updated: 2026-07-11
description: >
  Added weekend-mode profile. Clarified sleep_insight threshold (was 50, now 60).
```

### 7.3 Version Synchronization

Prompt version in `frontmatter.yaml` is the single source of truth. Related documents that reference prompt versions must be kept in sync:

- `prompts/README.md` â€” governance version table
- `docs/ai/PromptVersioning.md` â€” global version registry
- Agent module docstrings

Use the sync script for bulk updates:
```bash
python scripts/sync_versions.py  # Syncs all version references
python scripts/check_versions.py # CI check â€” asserts versions match
```

---

## 8. Common Pitfalls

### 8.1 Over-Specification

**Problem:** Too many rules, conditions, and constraints make the prompt rigid. The agent spends more tokens parsing instructions than generating output.

**Symptoms:**
- Agent consistently omits fields to stay within token budget
- Output feels robotic and repetitive
- Agent ignores lower-priority rules

**Fix:**
- Keep instructions to 7Â±2 numbered steps
- Use examples instead of exhaustive rules
- Prioritize: put the 3 most important rules first
- Split complex prompts into sub-agents

### 8.2 Under-Specification

**Problem:** Not enough guidance leads to inconsistent output structure, wrong JSON fields, or hallucinated data.

**Symptoms:**
- Output JSON varies between calls (different field names, nesting)
- Agent invents data not present in the input
- Output reads like generic boilerplate

**Fix:**
- Provide a complete output JSON schema with required/optional markers
- Include 3â€“5 diverse examples
- Add a quality self-check section
- Define anti-patterns explicitly

### 8.3 Contradictory Instructions

**Problem:** Two instructions conflict. The agent must choose which to follow, and the choice is unpredictable.

**Example:**
```
"Always recommend exactly 3 tasks"
"Only recommend tasks that are urgent"
"If no urgent tasks exist, recommend 0 tasks"
```

**Fix:**
- Use priority numbers or decision trees: "If X, do Y. Otherwise, do Z."
- Add explicit conflict resolution: "Rule 2 overrides Rule 1 when sleep_score < 50"
- Test with edge cases to surface contradictions

### 8.4 Missing Edge Cases

**Problem:** The prompt assumes data is always present, complete, and well-formed.

**Common missing edge cases:**
- Empty arrays (no tasks, no habits, no courses)
- Null/missing fields (no sleep data, no due date)
- Past dates (overdue tasks)
- Future dates (scheduled items)
- Boundary values (sleep_score = 0 or 100)
- Holiday/weekend detection
- First-time user (no history)

**Fix:** Add an Edge Cases section to every prompt covering the 5 most likely edge scenarios.

### 8.5 Model-Specific Behavior

Different models behave differently with the same prompt:

| Behavior | Mistral 7B (Ollama) | Claude Sonnet 4 |
|---|---|---|
| JSON compliance | Needs explicit formatting instructions | Generally compliant |
| Instruction following | Best with numbered steps | Handles paragraphs well |
| Token efficiency | Better with shorter prompts | Handles longer context |
| Creativity at low temp | Can still vary output | More deterministic |
| Refusal behavior | Rarely refuses | May refuse unsafe requests |

**Guidelines:**
- Always include "Your response must be valid JSON only" if parsing JSON
- Test prompts on both Ollama and Claude before deployment
- Use numbered steps (Mistral follows them more reliably)
- Keep critical instructions in the first 20% of the prompt body
- If switching models, re-validate all prompts

---

## 9. Prompt Review Process

### 9.1 Self-Review Checklist (10 items)

Before submitting a prompt change, verify:

- [ ] **Frontmatter complete**: all 5 required fields present, typed correctly
- [ ] **`version` bumped**: semver appropriate for the change
- [ ] **`status` correct**: `draft` for WIP, `active` for live, `deprecated` for retired
- [ ] **`validate-prompts` passes**: no YAML errors, no missing fields
- [ ] **Content tests pass**: `pytest tests/test_agent_prompts.py -v`
- [ ] **3â€“5 examples present**: covering normal, edge, and error scenarios
- [ ] **Edge Cases section populated**: at least 5 scenarios
- [ ] **Anti-Patterns section present**: at least 3 "DO NOT" items
- [ ] **Output schema documented**: JSON structure with required/optional fields
- [ ] **Quality criteria defined**: self-check list for the agent

### 9.2 Pre-Deployment Steps

```bash
# 1. Validate frontmatter
python scripts/validate_prompts.py

# 2. Run all prompt tests
pytest tests/test_prompt_loader.py tests/test_agent_prompts.py -v

# 3. Check version sync
python scripts/check_versions.py

# 4. Full test suite (ensures no regressions)
python -m pytest tests/ --cov=packages --cov=apps/api --cov-fail-under=85

# 5. Manual spot check
python -c "from ai.prompt_loader import prompts; e = prompts.get_agent('YOUR_AGENT'); print(e.body[:500])"
```

### 9.3 Peer Review

| Change Severity | Required Reviewers | Process |
|---|---|---|
| CRITICAL (breaking schema, guardrails, model swap) | Developer + Architecture Team | Architecture meeting review |
| HIGH (new prompt, new sections, behavior change) | Developer | PR review with diff |
| MEDIUM (examples, wording, edge cases) | Any team member | Quick PR review |
| LOW (typo, whitespace, formatting) | Self-review | Merge with passing CI |

### 9.4 Production Rollback

If a prompt change causes issues in production:

1. **Immediate**: Revert the prompt file to the previous commit: `git checkout HEAD~1 -- prompts/agents/your_agent.md`
2. **Validation**: Run `make validate-prompts` to confirm the reverted file is valid
3. **Deploy**: Push the revert
4. **Postmortem**: Document what went wrong (within 48 hours)
5. **Prevention**: Add a new test for the failure scenario

**The previous version is always available in git history** â€” never delete old versions, just set `status: deprecated`.

---

## 10. Quick Reference

### Command Cheat Sheet

```bash
# Validation
python scripts/validate_prompts.py         # Validate all prompt frontmatter
make validate-prompts                       # Same, via Makefile

# Testing
pytest tests/test_prompt_loader.py -v       # Loader tests (31)
pytest tests/test_agent_prompts.py -v       # Content tests (42)
pytest tests/test_validate_script.py -v     # Script tests (23)
pytest tests/ -m "prompt or agent" -v       # All prompt-related
pytest tests/                               # Full suite (2795+ tests)

# Inspection
python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"
python -c "from ai.prompt_loader import prompts; print(prompts.count_prompts())"
python -c "from ai.prompt_loader import prompts; e = prompts.get_agent('briefing_agent'); print(e.frontmatter)"
python -c "from ai.prompt_loader import prompts; e = prompts.get_agent('memory_agent'); print(e.body[:200])"

# Version sync
python scripts/sync_versions.py              # Sync version refs across docs
python scripts/check_versions.py             # CI check â€” must pass before merge

# Full pre-commit
make pre-commit                              # lint â†’ validate â†’ test â†’ type-check
```

### Frontmatter Template (Copy-Paste)

```yaml
---
version: 1.0.0
status: draft
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.4
description: >
  One-line summary of what this prompt does.
last_updated: 2026-07-11
approved_by: developer
review_cycle: weekly
tags: [tag1, tag2]
---
```

### Agent Prompt Checklist

- [ ] YAML frontmatter with 5 required fields
- [ ] Role Definition (3â€“5 paragraphs)
- [ ] Input Schema (table with types, sources)
- [ ] Output JSON Schema (required + optional)
- [ ] Detailed Instructions (numbered steps)
- [ ] Few-Shot Examples (3â€“5)
- [ ] Edge Cases (5+ scenarios)
- [ ] Anti-Patterns (3+ items)
- [ ] Quality Criteria (7+ checklist items)
- [ ] Error Recovery (5+ scenarios)
- [ ] Minimum body length: > 1000 chars
- [ ] `validate-prompts` passes
- [ ] Content tests pass

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial prompt engineering guide â€” architecture, structure template, token budgets, temperature guidelines, testing, versioning, pitfalls, review process |
