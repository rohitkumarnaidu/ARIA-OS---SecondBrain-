---
version: 2.0.0
status: active
description: Central governance document for the prompts/ directory — file reference, dev workflow, testing, version management, integration map, maintenance schedule, and change approval matrix
model: none
max_tokens: 0
temperature: 0.0
last_updated: 2026-06-11
approved_by: architecture-review
classification: internal
governance_level: project-wide
---

# Prompts Directory — Enterprise Governance Guide

Single source of truth for every AI prompt template in ARIA OS. Changes have system-wide impact.

---

## 1. File Reference

### System (`prompts/system/`) — Loaded at start, cached.

| File                   | Ver    | Purpose                                      | Tokens |
|------------------------|--------|----------------------------------------------|--------|
| `aria_system.md`       | 2.0.0  | ARIA persona, capabilities, tone, output fmt | 4096   |
| `guardrails.md`        | 2.0.0  | Refusal categories, PII redaction, boundaries| 2048   |

### Agents (`prompts/agents/`) — Per-agent + system + context at runtime.

| File                            | Ver   | Purpose                                    | Tokens | Context Used               |
|---------------------------------|-------|--------------------------------------------|--------|-----------------------------|
| `briefing_agent.md`             | 2.0.0 | Daily briefing generation                  | 2048   | All except courses          |
| `weekly_review_agent.md`        | 2.0.0 | Weekly productivity review                 | 2048   | All                         |
| `opportunity_radar_agent.md`    | 2.0.0 | Career scanning & matching                 | 2048   | Profile, skills, goals      |
| `memory_agent.md`               | 1.2.0 | Memory consolidation                       | 2048   | Chat history, profile       |
| `learning_agent.md`             | 1.1.0 | Study patterns, peak windows               | 2048   | Courses, habits, sleep      |
| `task_agent.md`                 | 1.3.0 | Task decomposition, estimation             | 2048   | Tasks, goals                |
| `sleep_agent.md`                | 1.1.0 | Sleep analysis, wind-down routines         | 1536   | Sleep logs, habits          |
| `nudge_agent.md`                | 2.0.0 | Course/habit nudges with escalation        | 2048   | All                         |
| `onboarding_agent.md`           | 1.0.0 | First-time user onboarding                 | 2048   | Profile only                |

### Templates (`prompts/templates/`) — Formatting specs for client.py and scheduler.

| File                     | Ver   | Purpose                                      | Budget       |
|--------------------------|-------|----------------------------------------------|--------------|
| `context_assembly.md`    | 2.0.0 | Context packet structure, budgets, freshness | 7800 tokens  |
| `email_templates.md`     | 2.0.0 | 9 email templates, A/B, tracking, compliance | 150ms render |

### Token Budget by Agent

| Agent                  | S+Guard | Context | Agent  | Total   |
|------------------------|---------|---------|--------|---------|
| briefing_agent         | 1,600   | 7,800   | 2,048  | ~11,448 |
| weekly_review_agent    | 1,600   | 7,800   | 2,048  | ~11,448 |
| nudge_agent            | 1,600   | 7,800   | 2,048  | ~11,448 |
| memory_agent           | 1,600   | 2,500   | 2,048  | ~6,148  |
| task_agent             | 1,600   | 1,600   | 2,048  | ~5,248  |
| opportunity_radar_agent| 1,600   | 1,800   | 2,048  | ~5,448  |
| learning_agent         | 1,600   | 1,300   | 2,048  | ~4,948  |
| sleep_agent            | 1,600   | 600     | 1,536  | ~3,736  |
| onboarding_agent       | 1,600   | 600     | 2,048  | ~4,248  |

---

## 2. Quick Start — Adding a New Prompt

1. Create file in `system/` / `agents/` / `templates/`
2. Add YAML frontmatter (version, status, description, model, max_tokens, temperature, last_updated, approved_by)
3. Follow style: `##` headings, `{variables}`, triple-backtick blocks, <120 char lines
4. Add entry to this README (section 1)
5. Register in `packages/ai/client.py` (if agent)
6. Write test in `tests/test_prompts/`
7. Run: `python scripts/validate_prompt.py`
8. Open PR with governance label (section 8)

### Frontmatter Template
```yaml
version: 1.0.0
status: draft          # draft → active → deprecated
description: "Purpose"
model: ollama/mistral:7b
max_tokens: 2048
temperature: 0.5
last_updated: 2026-06-11
approved_by: developer
```

---

## 3. Development Workflow

### WRITE → TEST → VERSION → APPROVE → DEPLOY

| Stage   | Actions                                      | Gate                         |
|---------|----------------------------------------------|------------------------------|
| WRITE   | Create/modify, validate syntax               | `validate_prompt.py` passes  |
| TEST    | Unit tests, regression, A/B if needed        | All tests pass               |
| VERSION | Bump semver, update changelog, sync versions | `check_versions.py` passes   |
| APPROVE | PR review per severity (section 8)           | Approvals obtained           |
| DEPLOY  | Squash-merge to main, CI validates           | PR merged                    |

---

## 4. Testing Protocol

### Unit Tests (`tests/test_prompts/`)
| File                          | Tests For                             | Coverage    |
|-------------------------------|---------------------------------------|-------------|
| `test_yaml_frontmatter.py`    | Valid YAML on all files               | 100%        |
| `test_token_budget.py`        | Token estimates match budgets         | 100% agents |
| `test_variable_coverage.py`   | No undefined template variables       | 100%        |
| `test_email_render.py`        | Email renders without errors          | All temps   |
| `test_context_assembly.py`    | Assembler produces valid packet       | All sections|

Run: `pytest tests/test_prompts/ -v --timeout=30`

### Regression & A/B
- Regression: snapshot-based output comparison. Snapshots auto-updated on version bump (review in PR).
- A/B: 50% split, min 200/variant, 3-day run. Deploy at 95% confidence. Tool: `scripts/evaluate_prompt_ab.py`

### Validation
```bash
python scripts/validate_prompt.py --dir prompts/ --strict
```
Checks: valid YAML, semver, no orphaned vars, consistent budgets, valid approved_by.

---

## 5. Version Management

| Bump  | Criteria                                          | Example      |
|-------|---------------------------------------------------|-------------|
| MAJOR | Breaking: output format, context structure, model | 1.0.0→2.0.0 |
| MINOR | New: section, field, agent, non-breaking expansion| 1.0.0→1.1.0 |
| PATCH | Fixes: wording, bugs, token optimization, docs    | 1.0.0→1.0.1 |

Changelog categories: `Added`, `Changed`, `Fixed`, `Removed`, `Security`. YAML = source of truth. CI enforces sync. Pre-commit: `check_versions.py`.

---

## 6. Integration Guide

### → `packages/ai/client.py`
Loads system prompt + guardrails at init, uses `ContextAssembler` for context, loads agent prompt per request. Full flow in `generate_for_agent()`.

### → `docs/ai/PromptVersioning.md`
Global version registry. Bump prompt → update both files. `scripts/sync_versions.py` writes both.

### → `services/scheduler/`
`EmailRenderer("prompts/templates/email_templates.md")` renders email specs at schedule time.

---

## 7. Maintenance

### Quarterly Review
| Quarter | Window       | Focus                                    | Owner                |
|---------|--------------|------------------------------------------|----------------------|
| Q1      | Jan 15—Feb 1 | Guardrails audit, metrics baseline       | Security Team        |
| Q2      | Apr 1—Apr 15 | Token budget optimization, freshness     | Architecture Team    |
| Q3      | Jul 1—Jul 15 | A/B analysis, template consolidation     | Product Team         |
| Q4      | Oct 1—Oct 15 | Full audit, version cleanup, deprecation | Architecture Team    |

### Health Metrics
| Metric                    | Target   | Alert     |
|---------------------------|----------|-----------|
| Token budget utilization  | 70-85%   | >90%/50%  |
| Assembly success rate     | >99.5%   | <99%      |
| Assembly time             | <200ms   | >300ms P99|
| Missing variable rate     | <0.1%    | >1%       |
| Email delivery rate       | >97%     | <95%      |
| Output quality score      | >4.0/5.0 | <3.5/5.0  |
| Version drift             | 0 files  | >2        |

### Hygiene — Deprecated: rename `.deprecated`, set `status: deprecated`. Archive after 2 quarters. Max file: 15KB soft, 25KB hard.

---

## 8. Governance — Change Approval Matrix

### Severity Levels
| Level    | Definition                              | Examples                                    |
|----------|-----------------------------------------|---------------------------------------------|
| CRITICAL | Breaking, security, user safety         | Guardrails, PII, format break, model swap   |
| HIGH     | Material behavior, new agent, budget    | New prompt, token reallocation, section     |
| MEDIUM   | Non-material behavior                   | Wording, examples, docs                     |
| LOW      | Cosmetic, formatting, typo              | Whitespace, markdown                        |

### Approvals Required
| Level    | Reviewer                | Additional          | SLA        |
|----------|-------------------------|---------------------|------------|
| CRITICAL | Security Lead           | Architecture Mtg    | 5 biz days |
| HIGH     | Architecture Team       | Product Lead (opt)  | 3 biz days |
| MEDIUM   | Any Architecture Team   | None                | 2 biz days |
| LOW      | Self-review             | None                | 1 biz day  |

### Enforcement — Branch protection on `prompts/`. CODEOWNERS: `@architecture-team`. CI: `validate_prompt.py --strict`. Emergency bypass: Security Lead approves (doc within 24h).

---

## 9. Related Resources
- `docs/ai/PromptVersioning.md` — Global version registry, deps
- `docs/engineering/ai_client.md` — Runtime loading, assembly
- `docs/engineering/email.md` — Rendering pipeline, delivery
- `docs/security/guardrails.md` — Safety rules
- `scripts/validate_prompt.py` — Syntax, variables, budgets
- `scripts/check_versions.py` — Assert versions match
- `scripts/sync_versions.py` — Bump version across docs
- `scripts/render_test.py` — Test-render email templates
- `scripts/evaluate_prompt_ab.py` — A/B evaluation

---

## 10. Version History

| Version | Date       | Author             | Changes                                    |
|---------|------------|--------------------|--------------------------------------------|
| 2.0.0   | 2026-06-11 | Architecture Team  | Full governance: ref, workflow, testing, versions, integration, maintenance, approvals |
| 1.0.0   | 2026-01-15 | Initial            | Basic directory listing                    |
