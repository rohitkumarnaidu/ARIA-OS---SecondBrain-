## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-ADR09-001 |
| Version | 1.0.0 |
| Status | Accepted |
| Last Updated | 2026-07-11 |

# ADR-009: Prompt Loader Architecture

## Document Control

| Field | Value |
|---|---|
| ADR Number | 009 |
| Status | Accepted |
| Date | 2026-07-10 |
| Deciders | Developer |
| Replaces | None |
| Superseded By | None |
| Category | AI Architecture |

---

## 1. Title

Prompt Loader Architecture â€” Externalized AI Prompt Management with YAML Frontmatter

---

## 2. Context

Second Brain OS has 11 AI agent modules (plus 8 skill sub-agents), each requiring structured system prompts. Initially, prompts were hardcoded as Python strings in agent modules:

```python
# BAD: Hardcoded prompts (initial approach)
SYSTEM_PROMPT = """
You are a briefing agent...
...
"""
```

This approach had several problems:

1. **No versioning** â€” Changes to prompts were invisible in git history (just code diffs)
2. **No metadata** â€” No model, token budget, or temperature associated with prompts
3. **Hard to review** â€” Non-technical prompt edits required code changes
4. **No validation** â€” Malformed prompts caused runtime errors
5. **No fallback** â€” If a prompt failed to load, the entire agent crashed
6. **Coupling** â€” Agent logic and prompt content were tightly coupled

---

## 3. Decision

Implement a **PromptLoader** system that:
- Stores all prompts as Markdown files in a `prompts/` directory
- Parses YAML frontmatter for metadata (model, tokens, temperature, etc.)
- Loads prompts at import time (singleton)
- Provides typed access via `PromptEntry` objects
- Has built-in validation for frontmatter fields
- Falls back to inline defaults when prompt files are unavailable
- Supports `render(**kwargs)` for dynamic content

---

## 4. Detailed Design

### 4.1 Directory Structure

```
prompts/
â”œâ”€â”€ system/
â”‚   â”œâ”€â”€ aria_system.md          # Core orchestration prompt
â”‚   â””â”€â”€ guardrails.md           # Safety guardrails
â”œâ”€â”€ agents/
â”‚   â”œâ”€â”€ briefing_agent.md       # Daily briefing
â”‚   â”œâ”€â”€ memory_agent.md         # Memory consolidation
â”‚   â”œâ”€â”€ task_agent.md           # Task breakdown
â”‚   â””â”€â”€ ... (10 total)
â””â”€â”€ templates/
    â”œâ”€â”€ context_assembly.md     # Data context builder
    â””â”€â”€ email_templates.md      # Email templates
```

### 4.2 Prompt File Format

```markdown
---
version: 2.1.0
status: active
model: ollama/mistral:7b
max_tokens: 4096
temperature: 0.5
description: "Generates daily briefings with task/habit/goal summary"
last_updated: 2026-06-11
tags: [briefing, daily, productivity]
---

# Daily Briefing Agent

## Role Definition
You are ARIA's daily briefing agent...
```

### 4.3 Core API

```python
from ai.prompt_loader import prompts

# Get a prompt (returns None if not found)
entry = prompts.get_agent("briefing_agent")
if entry:
    system_prompt = entry.system_prompt
    metadata = entry.frontmatter

# Get required prompt (raises if not found)
entry = prompts.get_required("briefing_agent")
system = entry.render(user_name="Alice", date="2026-07-10")

# List available prompts
all_prompts = prompts.list_prompts()
```

### 4.4 PromptEntry Properties

| Property | Type | Description |
|---|---|---|
| `frontmatter` | dict | Parsed YAML frontmatter |
| `body` | str | Markdown body (prompt content) |
| `name` | str | Stem of filename |
| `file_path` | Path | Full path to prompt file |
| `category` | str | system / agents / templates |
| `system_prompt` | str | Alias for body |
| `agent_prompt` | str | Alias for body |

### 4.5 Fallback Mechanism

```python
async def briefing_agent(user_id: str) -> dict:
    """Generate daily briefing."""
    loaded = prompts.get_agent("briefing_agent")
    
    if loaded:
        system = loaded.body
    else:
        # Inline fallback â€” always works
        system = "You are a helpful briefing assistant. Generate a daily summary."
    
    try:
        return await llm.generate_json(user_prompt, system=system)
    except LLMError:
        return algorithmic_fallback()  # Always works
```

---

## 5. Alternatives Considered

### Alternative 1: Database-Stored Prompts

**Approach:** Store prompts in Supabase with version history.

**Pros:** Version history, runtime editing, A/B testing
**Cons:** Database dependency at startup, latency on load, complex migrations
**Decision:** Rejected â€” adds unnecessary complexity for single-user system

### Alternative 2: JSON-Only Configuration

**Approach:** Store prompts in JSON files with all metadata.

**Pros:** Machine-readable, easy to parse
**Cons:** Cannot include rich Markdown formatting, harder to read/edit
**Decision:** Rejected â€” Markdown is more natural for prompt content

### Alternative 3: Single File with All Prompts

**Approach:** One large file containing all prompts with separators.

**Pros:** Single file to manage
**Cons:** Monolithic, hard to review individual prompts, merge conflicts
**Decision:** Rejected â€” violates separation of concerns

---

## 6. Consequences

### Positive

| Benefit | Description |
|---|---|
| **Versioned prompts** | Each prompt file has independent semver in YAML |
| **Self-documenting** | Metadata describes purpose, model, constraints |
| **Validation** | CI validates all frontmatter fields |
| **Graceful fallback** | Agents work without prompt files |
| **Separation of concerns** | Agent logic â‰  prompt content |
| **Easy editing** | Non-developers can edit Markdown files |
| **Git-friendly** | Changes to prompts visible as file diffs |

### Negative

| Cost | Mitigation |
|---|---|
| **File management overhead** | Automated validation, pre-commit hooks |
| **Double parsing (YAML + Markdown)** | Negligible performance cost |
| **Loading order** | Singleton pattern, loaded once at import |
| **Schema drift** | Validation script in CI enforces consistency |

---

## 7. Implementation Details

### 7.1 Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **File format** | `.md` with YAML frontmatter | Familiar, human-readable, widely supported |
| **Loading strategy** | Import-time singleton | Zero runtime overhead, fail fast |
| **Parsing** | `yaml.safe_load()` for frontmatter | Secure, no arbitrary code execution |
| **Error handling** | Returns None on missing file | Graceful degradation |
| **Encoding** | UTF-8 (BOM auto-stripped) | Cross-platform compatibility |
| **Naming convention** | snake_case matching agent module | Convention over configuration |

### 7.2 Testing Strategy

| Test Category | Count | What It Validates |
|---|---|---|
| Frontmatter validation | 16 | Required fields, types, values |
| Content checks | 14 | Min body length, keywords, tags |
| Loading edge cases | 5 | Missing files, malformed YAML, empty files |
| Rendering | 4 | Template substitution with kwargs |
| Fallback behavior | 3 | Graceful handling when prompt missing |
| **Total** | **42** | |

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| YAML parsing error in production | Low | Medium | Fallback to inline prompts |
| File encoding issues | Low | Low | BOM auto-strip, UTF-8 enforcement |
| Prompt file not deployed | Low | High | CI validates file presence |
| Schema changes to frontmatter | Low | Medium | Validation catches mismatches |

---

## 9. Related Decisions

| ADR | Relation |
|---|---|
| ADR-004: Agent as In-Process Functions | Agents use PromptLoader for prompts |
| ADR-001: Monorepo Structure | Prompts in top-level directory |
| ADR-002: Frontend Framework | Not affected |
| ADR-003: Database Choice | Not affected |

---

## 10. References

| Reference | Link |
|---|---|
| YAML Frontmatter Spec | https://jekyllrb.com/docs/front-matter/ |
| PyYAML Documentation | https://pyyaml.org/ |
| PromptLoader Implementation | `packages/ai/prompt_loader.py` |
| Prompt Files | `prompts/` directory |
| Validation Script | `scripts/validate_prompts.py` |
| Tests | `tests/test_prompt_loader.py`, `tests/test_agent_prompts.py` |

---

## 11. Appendices

### 11.1 Prompt File Checklist

- [ ] YAML frontmatter with 5 required fields
- [ ] `version` follows semver
- [ ] `status` is active/draft/deprecated
- [ ] `tags` present on system and agent prompts
- [ ] Body content > 1000 chars (agent prompts)
- [ ] No BOM (auto-stripped)
- [ ] UTF-8 encoding
- [ ] Renamed file if agent module name changes

### 11.2 Migration Path for Existing Hardcoded Prompts

1. Create `.md` file in `prompts/agents/` with frontmatter
2. Replace hardcoded string with `prompts.get_agent()`
3. Add inline fallback prompt
4. Validate with `make validate-prompts`
5. Add tests to `test_agent_prompts.py`
6. Remove old hardcoded string
