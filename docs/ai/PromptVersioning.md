# Prompt Versioning Strategy

## Document Control

| Property | Value |
|---|---|
| **Document ID** | DOC-AI-005 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Author** | AI Engineering Team |
| **Last Updated** | 2026-06-11 |
| **Approved By** | — |
| **Supersedes** | — |

---

## 1. Executive Summary

Prompt versioning is the practice of managing changes to AI prompts with the same rigor as application code. In Second Brain OS, every interaction with ARIA's agents — from daily briefings to opportunity scanning to memory consolidation — is driven by a system prompt. An unversioned change to a prompt can silently alter agent behavior, degrade output quality, or break downstream consumers that depend on a specific response format.

**Why it matters:**

- **Reliability**: A versioned prompt produces deterministic output structure. Downstream parsers, database inserters, and notification formatters depend on consistent schema.
- **Reproducibility**: When a user reports an unexpected response, the exact prompt version that produced it can be identified and inspected. Without versioning, debugging reduces to guesswork.
- **Rollback safety**: Every prompt change is a revertible commit. A bad prompt deployment can be undone in seconds.
- **Auditability**: Every prompt change is traceable to a decision, a ticket, or a test result.

This document defines the complete prompt versioning lifecycle, storage strategy, template format, testing requirements, and deployment workflow for all prompts used across ARIA's agent system.

---

## 2. Prompt Lifecycle

Every prompt in the system follows a defined lifecycle. No prompt may be used in production outside this flow.

```
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐    ┌────────────┐
  │  DRAFT   │───▶│   TEST   │───▶│  REVIEW  │───▶│  VERSIONED │───▶│ DEPLOYED │───▶│ DEPRECATED │
  │          │    │          │    │          │    │            │    │          │    │            │
  │ Author   │    │ CI runs  │    │ Peer     │    │ Tagged in  │    │ Active   │    │ Replaced   │
  │ creates  │    │ tests    │    │ review   │    │ git +      │    │ in prod  │    │ by newer   │
  │ prompt   │    │ + manual │    │ + sign-  │    │ registry   │    │          │    │ version    │
  └──────────┘    └──────────┘    │ off      │    └────────────┘    └──────────┘    └────────────┘
                                  └──────────┘
```

| Stage | Description | Gate |
|---|---|---|
| **Draft** | Author writes or modifies a prompt in the `prompts/drafts/` directory | None |
| **Test** | Automated tests run against the prompt: format validation, example execution, regression checks | All tests pass |
| **Review** | Pull request with tested prompt. Peer review of wording, variable usage, output schema, and edge cases | At least 1 approval |
| **Versioned** | Prompt is assigned a semantic version, moved to `prompts/versioned/`, and committed to main | Version tag applied |
| **Deployed** | Prompt is live in production — served by the Prompt Registry to all agents | Registry activated |
| **Deprecated** | A newer version exists. Old version is retained for traceability but not used for new sessions | Registry marks `status: deprecated` |

**Exceptions**: Hotfix prompts (PATCH-level changes to fix broken output format) may skip the REVIEW stage with explicit engineering lead approval, but must still pass TEST and be VERSIONED.

---

## 3. Prompt Storage Strategy

All prompts live in the `prompts/` directory at the monorepo root, alongside `packages/` and `apps/`. This ensures prompts are versioned in git alongside the code that consumes them.

### Directory Structure

```
prompts/
├── drafts/                          # Work-in-progress prompts (not yet versioned)
│   ├── briefing-v2-test.yaml
│   └── memory-summarizer-experimental.yaml
├── versioned/                       # Released prompts (immutable once committed)
│   ├── briefing/
│   │   ├── v1.0.0.yaml
│   │   ├── v1.1.0.yaml
│   │   └── v2.0.0.yaml
│   ├── memory-summarizer/
│   │   ├── v1.0.0.yaml
│   │   └── v1.1.0.yaml
│   ├── learning-tutor/
│   │   └── v1.0.0.yaml
│   ├── opportunity-scanner/
│   │   └── v1.0.0.yaml
│   └── habit-coach/
│       └── v1.0.0.yaml
├── registry.yaml                    # Central catalog of all prompts
├── registry.schema.json             # JSON Schema for registry validation
└── tests/                           # Prompt test suites
    ├── briefing.test.yaml
    ├── memory-summarizer.test.yaml
    └── helpers/
        └── test-runner.py
```

### Git Rules

- **Every prompt file is immutable once merged to `main`**. To change a prompt, create a new versioned file. Do not edit an existing versioned file.
- **Draft prompts must never be referenced by production code**. The Prompt Registry only reads from `versioned/`.
- **YAML frontmatter** in every prompt file contains metadata (id, version, author, status, date, description). This enables the Registry to parse prompts without loading full content.

### YAML Frontmatter Example

Every prompt file begins with a YAML frontmatter block:

```yaml
---
id: briefing-daily
name: Daily Briefing Generator
version: 1.1.0
status: deployed
author: AI Engineering
created: 2026-03-15
updated: 2026-06-01
description: >
  Generates the personalized daily briefing for the user every morning.
  Includes task summary, sleep report, goal progress, and opportunity highlights.
tags: [briefing, daily, productivity]
model: claude-sonnet-4
max_tokens: 2048
temperature: 0.7
input_variables:
  - user_name
  - tasks_today
  - overdue_count
  - sleep_score
  - goal_progress
  - opportunities
output_schema:
  type: object
  properties:
    greeting: string
    summary: string
    top_tasks: array
    sleep_note: string | null
    goal_progress: array
    opportunities: array
---
```

---

## 4. Prompt Template Format

All prompts in Second Brain OS follow a standardized template structure. This ensures every prompt is self-documenting, testable, and compatible with the Prompt Registry.

### Template Structure

```markdown
# System: <role definition>
You are {agent_name}, a specialized agent within the ARIA OS ecosystem. Your purpose is {agent_purpose}.

# Context
Current user: {user_name}
Current time: {current_time}
Day of week: {day_of_week}

# Available Data
{tasks_today}
{overdue_count}
{sleep_score}
{goal_progress}

# Instructions
1. {instruction_1}
2. {instruction_2}
3. Never invent data that is not provided in the context above.
4. If data is missing, state that it is unavailable rather than guessing.

# Output Format
Respond with a JSON object matching this schema:
{
  "greeting": "A personalized greeting based on time of day",
  "summary": "1-2 sentence overview of today's most important items",
  "top_tasks": ["Task 1 title", "Task 2 title", "Task 3 title"],
  "sleep_note": "Optional note about sleep if score < 70",
  "goal_progress": [
    {"goal_name": "Goal title", "progress_pct": 65}
  ],
  "opportunities": [
    {"title": "Opportunity title", "urgency": "high|medium|low"}
  ]
}

# Examples

## Example 1: Normal morning
Input:
  user_name: "Alex"
  tasks_today: ["Complete DSA assignment", "Review pull request", "Plan weekly budget"]
  sleep_score: 82
  goal_progress: [{"name": "LeetCode 100", "progress": 45}]

Output:
{
  "greeting": "Good morning, Alex! You had solid sleep last night.",
  "summary": "You have 3 tasks today. Your LeetCode goal is at 45% — keep the momentum.",
  "top_tasks": ["Complete DSA assignment", "Review pull request", "Plan weekly budget"],
  "sleep_note": null,
  "goal_progress": [{"goal_name": "LeetCode 100", "progress_pct": 45}],
  "opportunities": []
}

## Example 2: Low sleep
Input:
  user_name: "Alex"
  tasks_today: ["DSA study session", "Team meeting", "Blog post draft"]
  sleep_score: 54
  goal_progress: [{"name": "LeetCode 100", "progress": 45}]

Output:
{
  "greeting": "Morning, Alex. Looks like sleep was rough.",
  "summary": "I've adjusted your plan. Focus on the team meeting and defer DSA if needed.",
  "top_tasks": ["Team meeting", "Blog post draft"],
  "sleep_note": "Your sleep score was 54. Consider rescheduling cognitively demanding work.",
  "goal_progress": [{"goal_name": "LeetCode 100", "progress_pct": 45}],
  "opportunities": []
}
```

### Template Components

| Section | Required | Purpose |
|---|---|---|
| System role | Yes | Defines agent identity and purpose. Never changes within a major version. |
| Context | Yes | Dynamic variables injected at runtime. Every variable used here must be declared in `input_variables` frontmatter. |
| Instructions | Yes | Ordered list of behavioral rules. Changes here typically constitute a MINOR version bump. |
| Output Format | Yes | JSON schema that the prompt must produce. Breaking changes to the schema require a MAJOR version bump. |
| Examples | Recommended | 1-3 worked examples showing input → output. Zero-shot prompts benefit greatly from examples. Crucially, examples themselves must match the current output format. |

### Variable Interpolation

Variables in prompt templates use `{variable_name}` syntax, matching Python `str.format()` or Jinja2. The Prompt Registry resolves all variables before passing the prompt to the model.

```python
# Prompt resolution in the Agent Runtime
prompt_text = load_prompt("briefing-daily", version="1.1.0")
resolved_prompt = prompt_text.format(**context_variables)
response = await ollama_client.generate(model=prompt.metadata.model, prompt=resolved_prompt)
```

If a required variable is missing at runtime, the agent must raise a `PromptVariableError` — not silently render an empty string.

---

## 5. Versioning Scheme

Prompts follow **Semantic Versioning 2.0.0**: `MAJOR.MINOR.PATCH`

### Version Bump Rules

| Bump | When to apply | Examples |
|---|---|---|
| **MAJOR** | Breaking change to output structure or schema. Existing consumers will break. | Removing a required field from the output JSON. Changing output format from JSON to markdown. Changing the model from Claude to GPT. |
| **MINOR** | Adding capabilities without breaking existing outputs. New optional fields, improved instructions, new examples. | Adding an optional `opportunities` array. Adding a new instruction to handle edge cases. Adding more examples. |
| **PATCH** | Fixes that do not change output structure. Typo fixes, clarifications, better phrasing, temperature/ token adjustments. | Fixing a grammatical error in the system message. Adjusting temperature from 0.8 to 0.7 for consistency. Adding explicit guard against hallucination. |

### Version Constraints in Code

When an agent requests a prompt, it specifies a version constraint:

```python
# Pin to exact version (safest for production)
prompt = registry.get("briefing-daily", "==1.1.0")

# Allow patch updates (safe: no output structure change)
prompt = registry.get("briefing-daily", "~1.1.0")  # >=1.1.0, <1.2.0

# Allow minor + patch (semi-safe)
prompt = registry.get("briefing-daily", "^1.0.0")  # >=1.0.0, <2.0.0
```

**Production agents must pin to exact version (`==`)**. Only development and test environments may use range constraints.

### Version History

Each prompt file's git history is its complete version history. The `git log` for a prompt file captures every change:

```bash
git log --oneline prompts/versioned/briefing/v1.1.0.yaml
> a3f2b1d feat: add optional opportunities section to briefing prompt
> b7c8d9e fix: correct JSON schema in output format section
> e4f5g6h feat: initial briefing prompt v1.0.0
```

---

## 6. Testing Prompts

All prompts must pass automated tests before they can be versioned and deployed.

### Test Categories

#### 6.1 Format Validation

Tests that the prompt produces valid output matching its declared schema. Each prompt's test suite includes:

```yaml
# prompts/tests/briefing.test.yaml
tests:
  - name: "Returns valid JSON"
    input:
      user_name: "TestUser"
      tasks_today: ["Task A"]
      overdue_count: 0
      sleep_score: 75
      goal_progress: [{"name": "Goal 1", "progress": 50}]
      opportunities: []
    assert:
      - path: "$.greeting"
        type: string
        required: true
      - path: "$.top_tasks"
        type: array
        min_length: 1
      - path: "$.summary"
        type: string
        max_length: 200

  - name: "Handles low sleep correctly"
    input:
      user_name: "TestUser"
      tasks_today: ["Task A", "Task B"]
      overdue_count: 2
      sleep_score: 45
      goal_progress: []
      opportunities: []
    assert:
      - path: "$.sleep_note"
        type: string
        required: true  # Must include sleep note when score < 70
      - path: "$.top_tasks"
        type: array
        max_length: 1  # Should reduce task count for low energy
```

#### 6.2 Regression Tests

Every time a new version is created, the test suite runs all previous test cases against the new prompt. This ensures that fixing one edge case does not break another.

```bash
python prompts/tests/helpers/test-runner.py \
  --prompt-id briefing-daily \
  --version 1.1.0 \
  --regression-suite
```

#### 6.3 A/B Testing

For significant prompt changes (new instruction strategy, completely rewritten system message), the system supports A/B testing:

```python
# In the Prompt Registry
prompt_a = registry.get("briefing-daily", "==1.0.0")  # Control
prompt_b = registry.get("briefing-daily", "==2.0.0-beta")  # Variant

# 50/50 split by user_id hash
variant = "A" if hash(user_id) % 2 == 0 else "B"
```

A/B test results are logged to `prompt_ab_tests` table in Supabase, capturing prompt version IDs, user response times, and explicit user feedback (rating/thumbs up/down).

#### 6.4 Token Budget Checks

Every prompt must declare its expected token usage:

```yaml
# In frontmatter
expected_tokens:
  system: 1200
  context: 800
  output_max: 2048
  total_max: 4096
```

The test runner verifies that actual token usage stays within 10% of the declared budget. A MAJOR version bump is required if the total exceeds 120% of the previous version's budget.

#### 6.5 CI Integration

Prompt tests run in the monorepo's CI pipeline on every PR that touches `prompts/`:

```yaml
# .github/workflows/prompt-tests.yml (example)
jobs:
  prompt-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run prompt tests
        run: python prompts/tests/helpers/test-runner.py --all
```

---

## 7. Prompt Registry

The Prompt Registry is a centralized YAML catalog of every versioned prompt in the system. It is stored at `prompts/registry.yaml` and loaded at startup by the agent runtime.

### Registry Schema

```yaml
# prompts/registry.yaml
prompts:
  - id: briefing-daily
    name: Daily Briefing Generator
    description: Generates personalized daily morning briefing
    current_version: 1.1.0
    latest_tested: 2026-06-10
    status: deployed  # draft | test | versioned | deployed | deprecated
    versions:
      - version: 1.0.0
        path: prompts/versioned/briefing/v1.0.0.yaml
        author: AI Engineering
        created: 2026-03-15
        status: deprecated
        tests_passed: true
        changelog: Initial version
      - version: 1.1.0
        path: prompts/versioned/briefing/v1.1.0.yaml
        author: AI Engineering
        created: 2026-06-01
        status: deployed
        tests_passed: true
        changelog: Added optional opportunities section, improved sleep note handling

  - id: memory-summarizer
    name: Memory Consolidation Summarizer
    description: Summarizes chat history for episodic memory storage
    current_version: 1.1.0
    latest_tested: 2026-06-08
    status: deployed
    versions:
      - version: 1.0.0
        path: prompts/versioned/memory-summarizer/v1.0.0.yaml
        author: AI Engineering
        created: 2026-04-01
        status: deprecated
        tests_passed: true
        changelog: Initial version
      - version: 1.1.0
        path: prompts/versioned/memory-summarizer/v1.1.0.yaml
        author: AI Engineering
        created: 2026-05-15
        status: deployed
        tests_passed: true
        changelog: Added entity extraction to output schema

  - id: learning-tutor
    name: Learning Tutor
    description: Explains concepts and quizzes on topics
    current_version: 1.0.0
    latest_tested: 2026-05-20
    status: deployed
    versions:
      - version: 1.0.0
        path: prompts/versioned/learning-tutor/v1.0.0.yaml
        author: AI Engineering
        created: 2026-05-20
        status: deployed
        tests_passed: true
        changelog: Initial version

  - id: opportunity-scanner
    name: Opportunity Scanner
    description: Searches and matches opportunities
    current_version: 1.0.0
    latest_tested: 2026-05-25
    status: deployed
    versions:
      - version: 1.0.0
        path: prompts/versioned/opportunity-scanner/v1.0.0.yaml
        author: AI Engineering
        created: 2026-05-25
        status: deployed
        tests_passed: true
        changelog: Initial version

  - id: habit-coach
    name: Habit Coach
    description: Provides habit tracking and encouragement
    current_version: 1.0.0
    latest_tested: 2026-05-22
    status: deployed
    versions:
      - version: 1.0.0
        path: prompts/versioned/habit-coach/v1.0.0.yaml
        author: AI Engineering
        created: 2026-05-22
        status: deployed
        tests_passed: true
        changelog: Initial version
```

### Registry Validation

The `registry.schema.json` file validates the registry structure in CI:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "prompts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "current_version", "status", "versions"],
        "properties": {
          "id": { "type": "string", "pattern": "^[a-z0-9-]+$" },
          "status": { "enum": ["draft", "test", "versioned", "deployed", "deprecated"] },
          "versions": {
            "type": "array",
            "items": {
              "required": ["version", "path", "status"],
              "properties": {
                "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" }
              }
            }
          }
        }
      }
    }
  }
}
```

### Loading the Registry at Runtime

```python
# In the Agent Runtime (packages/ai/)
import yaml
from pathlib import Path

class PromptRegistry:
    def __init__(self, registry_path: str = "prompts/registry.yaml"):
        with open(registry_path) as f:
            data = yaml.safe_load(f)
        self.registry = {p["id"]: p for p in data["prompts"]}

    def get(self, prompt_id: str, version: str | None = None) -> Prompt:
        entry = self.registry.get(prompt_id)
        if not entry:
            raise PromptNotFoundError(f"Prompt '{prompt_id}' not found in registry")

        if version:
            version_entry = next((v for v in entry["versions"] if v["version"] == version), None)
        else:
            version_entry = next(
                (v for v in entry["versions"] if v["status"] == "deployed"), None
            )

        if not version_entry:
            raise PromptVersionNotFoundError(
                f"Version {version or 'deployed'} not found for '{prompt_id}'"
            )

        return Prompt.load(version_entry["path"])
```

---

## 8. Deployment Strategy

### Gradual Rollout

New prompt versions are not deployed to all users at once. Instead, they follow a phased rollout:

| Phase | Audience | Duration | Validation |
|---|---|---|---|
| **Canary** | Internal team (developers) | 24 hours | Manual review, format checks |
| **Beta** | opt-in users (5% of users) | 48 hours | Automated format checks, error rate monitoring, latency monitoring |
| **Gradual** | 25% → 50% → 75% of users | 6 hours per tier | Error rate < 0.1%, latency < 2x baseline, user feedback score > 3.5/5 |
| **Full** | 100% of users | — | Continuous monitoring active |

### Canary Deployment

```python
# In the deployment service (hypothetical)
class PromptDeployer:
    def canary_test(self, prompt_id: str, new_version: str):
        canary_users = get_internal_users()
        for user in canary_users:
            agent_context = build_context(user)
            response = execute_prompt(prompt_id, new_version, agent_context)
            validate_response(user, prompt_id, new_version, response)

        if error_rate > 0.05:
            rollback(prompt_id, previous_version)
            notify_team(f"Canary failed for {prompt_id} v{new_version}")
```

### Instant Rollback

If a deployed prompt version causes errors, the rollback is a single configuration change:

```python
# Rollback command
registry.set_deployed_version("briefing-daily", "1.0.0")

# This changes one value in Supabase or a config file
# No code deploy needed — the registry is hot-reloaded
```

The rollback mechanism is tested monthly in non-production environments.

### Version Aliasing

The registry supports version aliases for common reference points:

```yaml
aliases:
  stable: briefing-daily@1.0.0    # Pinned stable version
  canary: briefing-daily@1.1.0    # Canary test version
```

---

## 9. Prompt Changelog

Every prompt version must document what changed from the previous version and why. This changelog is maintained in the prompt file's frontmatter and in the registry.

### Changelog Entry Template

```yaml
changelog:
  - version: 1.1.0
    date: 2026-06-01
    type: minor
    author: AI Engineering
    summary: Added optional opportunities section to output
    details:
      - Added `opportunities` field to output JSON schema
      - Added instruction to include up to 3 relevant opportunities from provided data
      - Added example demonstrating opportunity output
      - Updated max_tokens from 1024 to 2048 to accommodate longer responses
    rationale: >
      Users reported that they wanted to see relevant opportunities inline
      in their daily briefing rather than having to ask separately. This
      change makes the briefing more useful without breaking existing
      consumers (field is optional).
    tests_added:
      - Checks that opportunities array is valid when present
      - Checks that null opportunities does not error
    related_tickets:
      - SBS-427: Include opportunities in daily briefing
```

### Changelog Collection

A consolidated changelog is maintained at `prompts/CHANGELOG.md` for quick reference:

```markdown
# Prompt Changelog

## 2026-06-01
- **briefing-daily** v1.1.0 (minor): Added optional opportunities section
- **memory-summarizer** v1.0.1 (patch): Fixed typo in system message

## 2026-05-15
- **memory-summarizer** v1.1.0 (minor): Added entity extraction to output schema

## 2026-05-01
- **briefing-daily** v1.0.0 (major): Initial production version
```

---

## 10. Appendices

### Appendix A: Prompt Template Example (Complete)

```yaml
---
id: memory-summarizer
name: Memory Consolidation Summarizer
version: 1.1.0
status: deployed
author: AI Engineering
created: 2026-04-01
updated: 2026-05-15
description: >
  Summarizes a set of chat messages for storage in episodic memory.
  Extracts key facts, decisions, user preferences, and action items.
model: ollama/nomic-embed-text
max_tokens: 1024
temperature: 0.3
input_variables:
  - user_name
  - messages
  - existing_memory_context
output_schema:
  type: object
  properties:
    summary: string
    key_facts: array
    decisions: array
    preferences: array
    action_items: array
    entities: object
changelog:
  - version: 1.1.0
    date: 2026-05-15
    type: minor
    summary: Added entity extraction
    details:
      - Added entities.persons, entities.topics, entities.tools fields
    rationale: Entity extraction enables the knowledge graph agent to build better connections
---
# System
You are Memory Summarizer, a specialized agent within the ARIA OS ecosystem.
Your purpose is to summarize chat history into structured episodic memory records.

# Context
User: {user_name}
Messages to summarize: {messages}

# Existing Knowledge
{existing_memory_context}

# Instructions
1. Summarize the conversation in 1-3 sentences capturing the core topic and outcome.
2. Extract concrete facts stated by the user (e.g., "I have a DSA exam next week").
3. Identify decisions made (e.g., "Decided to reschedule study session to evening").
4. Detect new or changed preferences (e.g., "User prefers morning study for DSA").
5. List action items the user committed to (e.g., "Will complete assignment by Friday").
6. Extract named entities: people mentioned, topics discussed, tools/referenced.
7. If the conversation is empty or trivial, return a minimal record — do not fabricate.

# Output Format
{
  "summary": "string",
  "key_facts": ["string"],
  "decisions": ["string"],
  "preferences": ["string"],
  "action_items": ["string"],
  "entities": {
    "persons": ["string"],
    "topics": ["string"],
    "tools": ["string"]
  }
}
```

### Appendix B: Registry Template

```yaml
# prompts/registry.yaml
prompts:
  - id: <unique-prompt-id>
    name: <Human-readable name>
    description: <One-line description>
    current_version: <semver>
    latest_tested: <YYYY-MM-DD>
    status: <draft|test|versioned|deployed|deprecated>
    versions:
      - version: <semver>
        path: prompts/versioned/<category>/v<semver>.yaml
        author: <Team or individual>
        created: <YYYY-MM-DD>
        status: <deployed|deprecated>
        tests_passed: <true|false>
        changelog: <Short description of changes>
```

### Appendix C: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | AI Engineering | Initial document |
