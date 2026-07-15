# AI/Agent Development Learning Path

## Document Control

| Field | Value |
|---|---|
| Document ID | LRN-AI-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-12 |
| Classification | Internal |

---

## Module 1: AI Architecture Overview

**Estimated time:** 0.5 day

### Learning Objectives
- Understand the 11-agent architecture and how ARIA orchestrates them
- Know the difference between cron-triggered and on-demand agents
- Understand how PromptLoader loads and manages 22 prompt files
- Be able to list all agents and their triggers from memory

### Reading Materials
- `AGENTS.md` Section 9 (AI Agent Architecture) — agent registry, orchestration
- `AGENTS.md` Section 10 (Prompt System Architecture) — PromptLoader API
- `packages/ai/agents/__init__.py` — agent module exports
- `packages/ai/prompt_loader.py` — PromptLoader implementation
- `services/scheduler/main.py` — 15 cron jobs that trigger agents

### Agent Categories
| Category | Agents | Example |
|---|---|---|
| Cron-triggered | Briefing, Weekly Review, Sleep, Nudge, Opportunity Radar | A09 runs at 7 AM daily |
| On-demand | Memory, Learning, Roadmap, Opportunity Matching | A02 fires on every chat |
| Service | Task Agent, Opportunity Matching | A01 triggered by user action |
| Non-AI | Reminder, Missed Task Checker, Habit Miss Checker | Rule-based, no LLM |

### Practice Exercise
1. Read the agent registry in `AGENTS.md` Section 9.3
2. Browse all agent modules in `packages/ai/agents/`
3. Browse all prompt files in `prompts/agents/`
4. Run `python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"` to verify loading
5. Open 2 agent modules and identify the common pattern (load prompt → call LLM → fallback)

---

## Module 2: Prompt Engineering

**Estimated time:** 1 day

### Learning Objectives
- Understand YAML frontmatter schema (required fields per category)
- Know how to create and validate prompt frontmatter
- Understand the `render(**kwargs)` method for template variables
- Be able to write a prompt following the standard 9-section structure

### Reading Materials
- `AGENTS.md` Section 4.3 (Prompt YAML Frontmatter Style)
- `AGENTS.md` Section 10.4 (Frontmatter Schema) — required fields per category
- `AGENTS.md` Section 11 (Prompt Development Guide) — creating, editing, testing
- `prompts/agents/briefing_agent.md` — the best example (957 lines)
- `scripts/validate_prompts.py` — CI validation script

### Prompt Structure Template
1. **Role Definition** — Who the agent is, purpose, tone
2. **Input Schema** — All input fields with types, defaults
3. **Output JSON Schema** — Required/optional fields, validation
4. **Detailed Instructions** — Step-by-step reasoning chain
5. **Few-Shot Examples** — 3-5 realistic input/output pairs
6. **Edge Cases** — Empty data, missing fields, contradictions
7. **Anti-Patterns** — What NOT to do with examples
8. **Quality Criteria** — Self-verification checklist
9. **Error Recovery** — What to do on failure

### Practice Exercise
1. Read a complete prompt file (e.g., `briefing_agent.md`) and identify all 9 sections
2. Run `make validate-prompts` to verify all prompts pass
3. Read the frontmatter of 3 different prompts and note the `version`, `status`, `model`, `max_tokens`, `temperature`
4. Use the `render` method in Python to render a template with custom kwargs
5. Write a simple test in `tests/test_agent_prompts.py` that checks for a keyword in a prompt

---

## Module 3: Implementing an Agent

**Estimated time:** 1.5 days

### Learning Objectives
- Walk through creating a new agent module from scratch
- Understand the agent pattern: Load prompt → Build context → Call LLM → Parse → Fallback
- Know how to register a new agent in the codebase

### Reading Materials
- `packages/ai/agents/briefing_agent.py` — the canonical agent example
- `AGENTS.md` Section 12.3 (Adding a New Agent + Prompt) — step-by-step
- `AGENTS.md` Section 9.4 (Prompt Files Inventory) — prompt naming convention
- `packages/ai/agents/__init__.py` — registration pattern

### Agent Implementation Pattern

```python
from ai.client import llm
from ai.prompt_loader import prompts

async def new_agent(user_id: str, **kwargs) -> dict:
    # 1. Load the prompt (with fallback)
    loaded = prompts.get_agent("new_agent")
    system = loaded.system_prompt if loaded else "Fallback system prompt"

    # 2. Build user prompt with context
    user = construct_user_prompt(user_id, kwargs)

    # 3. Call LLM with retry/circuit breaker
    try:
        result = await llm.generate_json(user, system=system)
        return result
    except LLMProviderUnavailableError:
        # 4. Algorithmic fallback (always works)
        return algorithmic_fallback(user_id)
```

### Practice Exercise
1. Read `briefing_agent.py` end-to-end and trace the execution flow
2. Create a new agent module following the pattern above (copy the simplest agent)
3. Create the corresponding prompt file in `prompts/agents/` with valid frontmatter
4. Register the agent in `packages/ai/agents/__init__.py`
5. Run `make validate-prompts` to verify frontmatter

---

## Module 4: LLM Client & Failover

**Estimated time:** 1 day

### Learning Objectives
- Understand the LLMClient architecture (retry, circuit breaker, provider failover)
- Know how Ollama (local, free) and Claude (cloud, fallback) are configured
- Understand circuit breaker states: CLOSED → OPEN → HALF_OPEN
- Be able to interpret LLMClient logs and debug failures

### Reading Materials
- `packages/ai/client.py` — LLMClient implementation
- `AGENTS.md` Section 18 (Cost & Performance) — token budgets, caching, rate limits
- `AGENTS.md` Section 9.1 (ARIA Orchestrator) — resilience defaults
- `packages/shared/utils/retry.py` — exponential backoff + circuit breaker
- `AGENTS.md` Section 19 (Debugging Guide) — common AI issues

### LLMClient Configuration
| Setting | Value | Purpose |
|---|---|---|
| Default AI | Ollama (Mistral 7B) | Free, local, no data leaves machine |
| Fallback | Claude Sonnet 4 | Cloud, ~$0.015/request |
| Circuit breaker | 5 failures → 60s cooldown | Prevents cascading failures |
| Retry | 3 attempts (2s, 4s, 8s) | Handles transient failures |
| Timeout | 30s per request | Prevents hanging |

### Circuit Breaker States
```
CLOSED → [5 failures] → OPEN → [60s timer] → HALF_OPEN → [success] → CLOSED
                                                          [failure] → OPEN
```

### Practice Exercise
1. Read `packages/ai/client.py` — understand the full LLMClient implementation
2. Simulate an Ollama failure by stopping the Ollama service
3. Observe the circuit breaker opening in the logs
4. Verify Claude fallback activates
5. Check the circuit breaker state with: `python -c "from ai.client import llm; print(llm.ollama_circuit.state)"`
6. Restart Ollama and verify circuit breaker resets

---

## Module 5: Testing AI

**Estimated time:** 1 day

### Learning Objectives
- Understand how to test agent modules (mocked LLM calls)
- Know how to validate prompt frontmatter
- Understand fallback testing (ensure algorithmic fallback works)
- Be able to interpret test coverage for AI modules

### Reading Materials
- `tests/test_agents.py` — 86 tests for per-agent logic
- `tests/test_agent_prompts.py` — 42 tests for prompt content
- `tests/test_prompt_loader.py` — 31 tests for PromptLoader
- `tests/test_llm_client.py` — 51 tests for retry, circuit breaker, JSON parsing
- `tests/test_ai_modules.py` — 55 tests for orchestrator, context assembly
- `AGENTS.md` Section 16.3 (Writing Tests) — test example patterns

### Test Patterns
```python
# Agent fallback test
async def test_agent_fallback_when_llm_unavailable(mock_llm_failure):
    result = await my_agent(user_id="test-user")
    assert result["fallback"] is True
    assert "data" in result

# Prompt content test
def test_agent_prompt_has_required_sections():
    prompt = loader.get_agent("my_agent")
    assert len(prompt.body) > 1000
    assert "## Role Definition" in prompt.body
    assert "## Few-Shot Examples" in prompt.body

# PromptLoader frontmatter test
def test_prompt_frontmatter_valid():
    entry = loader.get_agent("my_agent")
    assert entry.frontmatter["status"] == "active"
    assert isinstance(entry.frontmatter["max_tokens"], int)
```

### Practice Exercise
1. Run `pytest tests/test_agents.py -v` and observe the test output
2. Run `pytest tests/test_llm_client.py -v` — focus on circuit breaker tests
3. Run `pytest tests/test_agent_prompts.py -v` — prompt content validation
4. Read 3 agent test files and understand the mocking pattern
5. Write a test that verifies an agent's fallback behavior when LLM is unavailable
6. Run `make test-coverage` and check the AI packages coverage (target: 100%)
