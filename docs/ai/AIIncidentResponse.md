# AI Incident Response

## Document Control

| Field | Value |
|---|---|
| Document ID | AI-IR-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Internal — AI Operations |
| Owner | Developer |
| Last Updated | 2026-07-11 |
| Review Cycle | Monthly |
| Next Review | 2026-08-11 |
| Approved By | Developer |
| Related Documents | OPS-040 Incident Response, SEC-POLICY-IR-001, SEC-POLICY-DC-001, OPS-FRB-001 Firefighter Runbooks, `prompts/system/guardrails.md`, `packages/ai/client.py` |

---

## 1. Purpose & Scope

### 1.1 Purpose

This document defines incident response procedures specific to AI agent failures, safety incidents, and service degradations in ARIA OS. Standard incident response (OPS-040) covers general infrastructure — this covers prompt injection, hallucination, bias, data leakage, and AI provider failover.

### 1.2 Scope

- All 17 AI agents (A00–A16)
- LLM providers (Ollama local, Claude cloud fallback)
- Prompt system (`prompts/` directory, 22 prompt files)
- Agent modules (`packages/ai/agents/`)
- AI client infrastructure (`packages/ai/client.py` — circuit breaker, retry, provider failover)
- Memory embeddings and vector data

### 1.3 Architecture Context

```
User → ARIA (A00 orchestrator) → Sub-agent → LLM Client → Ollama/Claude
                                       ↓
                              PromptLoader (prompts/)
                                       ↓
                              Algorithmic fallback (always available)
```

- Circuit breaker: opens after 5 consecutive failures, 60s cooldown
- Retry: 3 attempts with exponential backoff (2s, 4s, 8s)
- Provider chain: Ollama (default) → Claude (fallback) → algorithmic (degraded)

---

## 2. AI Incident Severity Definitions

| Level | Label | Definition | Examples | Response SLA | Fix SLA |
|---|---|---|---|---|---|
| **P0-AI** | Critical | AI outputs harmful content (hate, violence, illegal advice), data leakage between users/cross-context, prompt injection exfiltrates data, model jailbreak succeeds | System prompt extracted via injection, user A sees user B's data, AI recommends harmful actions | 5 min acknowledge | 30 min fix |
| **P1-AI** | High | AI consistently hallucinating (> 20% of responses), bias detected in outputs (gender/racial), service unavailability (all providers down), high latency (> 30s average) | Briefing invents facts daily, scheduler AI jobs all fail, all responses take > 30s | 15 min acknowledge | 2 hour fix |
| **P2-AI** | Medium | Single agent misbehavior, minor hallucination (< 5% of responses), token budget waste, suboptimal prompt adherence | One agent returns empty response, memory agent fails to consolidate, occasional wrong data in briefings | 1 hour acknowledge | 8 hour fix |
| **P3-AI** | Low | Suboptimal response quality, minor prompt compliance issues, cosmetic formatting errors | Briefing has awkward phrasing, nudge agent sends repetitive messages, formatting inconsistency | 24 hour acknowledge | Next sprint |

### 2.1 Severity Upgrade Rules

- Escalate P2 → P1 if affected users exceed 25%
- Escalate P1 → P0 if harmful content is confirmed (not just suspected)
- Downgrade P1 → P2 if deterministic fallback successfully mitigates
- Any confirmed data exfiltration is automatically P0

---

## 3. Detection Mechanisms

### 3.1 Automated Detection

| Mechanism | What It Detects | Where | Alert Channel |
|---|---|---|---|
| Circuit breaker state change | Provider failure cascade | `packages/ai/client.py` | Logs + Sentry |
| Token usage anomaly | Budget exceeded, runaway generation | `packages/shared/utils/cache.py` + AI logs | Sentry |
| Response time outlier | Latency > 30s | `packages/ai/client.py` | Sentry |
| Empty/malformed response | Agent failure, hallucination | `packages/ai/agents/*.py` | Logs |
| Health endpoint | Provider availability | `/health/ready` | Synthetic monitor |
| Guardrails violation | Content safety boundary crossed | `prompts/system/guardrails.md` | Logs + Sentry |

### 3.2 Manual Detection Signals

- User reports ARIA saying something "wrong" or "weird"
- Periodic review of AI agent outputs finds hallucinated data
- Monitoring dashboard shows sustained high token usage
- Feedback endpoint (`POST /api/v1/feedback/welcome`) negative sentiment spike

### 3.3 Hallucination Detection

```python
# Pseudo-code: integrate into agent response pipeline
async def detect_hallucination(response: dict, context: dict) -> float:
    """
    Returns confidence score 0.0–1.0.
    < 0.7 triggers investigation.
    """
    # 1. Factual consistency: check claims against known data
    consistency = check_against_database(response, context)

    # 2. Confidence: if model reports low confidence markers
    confidence = extract_confidence(response)

    # 3. Source attribution: did the agent cite specific sources?
    attribution = has_valid_sources(response, context)

    return (consistency * 0.5) + (confidence * 0.3) + (attribution * 0.2)
```

---

## 4. AI Runbook Scenarios

### RB-AI-001: Prompt Injection Attack Detected

**Severity:** P0-AI

**Detection:**
- Guardrails log violation: `GUARDRAIL_VIOLATION: injection_attempt`
- User message contains extraction phrases: "ignore previous instructions", "forget everything", "you are now..."
- Agent returns system prompt content instead of expected output

**Triage:**
```bash
# 1. Check guardrails log
Get-Content -Path logs/ai.log -Tail 100 | Select-String "GUARDRAIL_VIOLATION"

# 2. Check the injection payload
Get-Content -Path logs/ai.log -Tail 100 | Select-String "injection_attempt" | Select-Object -First 5

# 3. Check if system prompt was exposed
Get-Content -Path logs/ai.log -Tail 200 | Select-String "system_prompt|aria_system|guardrails"
```

**Mitigation:**
1. **IMMEDIATE:** Block the offending payload — add to input sanitizer blocklist
2. **IMMEDIATE:** Rotate system prompts if leaked (see `prompts/system/`)
3. **IMMEDIATE:** Revoke any exposed API keys in the user's message
4. Review guardrails prompt (`prompts/system/guardrails.md`) — tighten if needed
5. Audit chat history for the affected session: `SELECT * FROM chat_messages WHERE user_id = '<affected>' ORDER BY created_at;`
6. Run `python scripts/attack-scenarios.py InjectionAttack` to test fix

**Recovery:**
1. Update `prompts/system/guardrails.md` with new injection patterns
2. Update `packages/shared/utils/sanitizer.py` with new blocklist entries
3. File incident post-mortem within 24 hours

**Communication:**
- Internal only (no user notification unless data was exposed)
- Template: "Prompt injection attempt detected and blocked. User [ID] payload: [redacted]. Guardrails updated."

---

### RB-AI-002: Hallucination Outbreak

**Severity:** P1-AI

**Detection:**
- Multiple user reports of incorrect information in briefings/reviews
- Sentry detects empty or malformed AI responses (> 20% of calls)
- Periodic audit finds confident-sounding false statements

**Triage:**
```bash
# 1. Check recent prompt changes
cd prompts/
git log --oneline -20

# 2. Check agent output logs for affected period
Get-Content -Path logs/ai.log -Tail 500 | Select-String "response" | Select-Object -First 20

# 3. Check temperature settings
python -c "
from ai.prompt_loader import prompts
for name in prompts.list_prompts('agents'):
    p = prompts.get_agent(name)
    if p:
        temp = p.frontmatter.get('temperature', 'N/A')
        tokens = p.frontmatter.get('max_tokens', 'N/A')
        print(f'{name}: temp={temp}, max_tokens={tokens}')
"
```

**Mitigation:**
1. Reduce temperature: set all agent prompts to `temperature: 0.3` (default 0.5)
2. Add guardrails to affected agent: update its prompt with stricter factual constraints
3. If > 30% hallucination: switch to deterministic algorithmic fallback for the affected agent
4. If provider-specific (Ollama vs Claude): flip `USE_LOCAL_AI` env var to switch provider
5. Check model version: `ollama show mistral:latest` — consider rolling back model version

**Recovery:**
1. Gradually restore temperature to normal (0.3 → 0.4 → 0.5) over 48 hours
2. Add factual consistency checks to the agent's output pipeline
3. Update agent prompt with examples of what NOT to do (anti-patterns section)
4. File incident with reproduction: "When asked [X], agent returns [Y] which is factually incorrect"

---

### RB-AI-003: Bias Detected in Responses

**Severity:** P1-AI

**Detection:**
- Periodic audit reveals systematic bias in AI outputs
- User reports discriminatory or stereotypical content
- Monitoring dashboard shows uneven treatment across user segments

**Triage:**
```bash
# 1. Log the biased response patterns
Get-Content -Path logs/ai.log -Tail 1000 | Select-String "bias|stereotype|discriminat" | Select-Object -First 20

# 2. Identify affected agents and prompts
# Look for patterns in recent outputs

# 3. Check which model is producing the biased outputs
python -c "
from ai.client import llm
print(f'Using Ollama: {llm.use_local_ai}')
print(f'Ollama circuit: {llm.ollama_circuit.state}')
print(f'Claude circuit: {llm.claude_circuit.state}')
"
```

**Mitigation:**
1. **IMMEDIATE:** Disable the affected agent via feature flag or by commenting out its registration in `packages/ai/agents/__init__.py`
2. Update the agent's prompt with explicit anti-bias instructions in the Anti-Patterns section
3. Add bias detection keywords to guardrails prompt
4. If model-specific (e.g., bias only in Claude): switch provider
5. Run bias audit test suite: `python scripts/attack-scenarios.py BiasAudit`

**Recovery:**
1. Update prompt with corrective examples
2. Add bias checks to CI pipeline for prompt changes
3. Re-enable agent after verified fix (48 hour observation period)
4. File post-mortem documenting the bias pattern and fix

**Communication:**
- If bias affected user-facing content: notify affected users with apology
- Template: "Our AI assistant generated content that did not meet our quality standards. We've identified the root cause and deployed a fix. We apologize for the experience."

---

### RB-AI-004: Data Leakage (Cross-User Context)

**Severity:** P0-AI

**Detection:**
- User reports seeing another user's data in their chat
- Logs show user_id mismatch in AI context assembly
- Embedding queries return results from another user's namespace

**Triage:**
```bash
# 1. IMMEDIATE: Shut down AI chat service
# Comment out chat router or disable via /feature-flags
# 2. Check context assembly logs
Get-Content -Path logs/ai.log -Tail 100 | Select-String "context_assembly|user_id" | Select-Object -First 20

# 3. Identify affected users
python -c "
# Check chat_messages for cross-user data
# SELECT user_id, COUNT(*) FROM chat_messages GROUP BY user_id;
"

# 4. Check embedding isolation
# Verify memory queries filter by user_id
```

**Mitigation:**
1. **IMMEDIATE:** Shut down chat endpoint (feature flag or API gateway block)
2. **IMMEDIATE:** Rotate all embedding vectors if cross-contamination suspected
3. **IMMEDIATE:** Force re-authentication for all users
4. Audit every session for the past 24 hours: check `chat_messages`, `memory` tables
5. Review `packages/ai/prompt_loader.py` context assembly — verify user_id isolation
6. Check all agent modules: `grep -r "user_id" packages/ai/agents/*.py` — every agent must filter by user_id

**Recovery:**
1. Fix the isolation bug (likely in context assembly or memory retrieval)
2. Re-embed all user data with verified isolation
3. Run integration test: `pytest tests/test_integration.py::test_user_isolation -v`
4. Gradual rollout: enable chat for internal testing first
5. Monitor cross-user queries for 7 days post-recovery

**Communication:**
- **Mandatory:** Notify all affected users with details of what data was exposed
- Internal: Full incident report within 24 hours
- If P0 confirmed: consider legal notification requirements per jurisdiction

---

### RB-AI-005: AI Provider Failover Chain

**Severity:** P1-AI

**Detection:**
- Circuit breaker opens for primary provider
- `/health/ready` shows provider degradation
- Agent responses become slow or fail
- Scheduler jobs report AI provider errors

**Triage:**
```bash
# 1. Check circuit breaker state
python -c "
from ai.client import llm
print(f'Ollama circuit: {llm.ollama_circuit.state} (failures: {getattr(llm.ollama_circuit, \"failure_count\", \"?\")})')
print(f'Claude circuit: {llm.claude_circuit.state} (failures: {getattr(llm.claude_circuit, \"failure_count\", \"?\")})')
print(f'Using local AI: {llm.use_local_ai}')
"

# 2. Check provider health
curl -s http://localhost:11434/api/tags 2>&1 | Select-String "models"
curl -s https://api.anthropic.com/v1/messages -H "x-api-key: $env:CLAUDE_API_KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

**Failover Chain:**

```
Ollama (default)
  → [5 failures] → Circuit breaker OPEN (60s cooldown)
    → Claude (fallback)
      → [5 failures] → Circuit breaker OPEN (60s cooldown)
        → Deterministic algorithmic fallback (degraded mode)
          → All agents work without AI (different quality)
```

**Mitigation:**
1. If Ollama down: `ollama serve`; wait for circuit breaker cooldown (60s)
2. If Claude down: check API key validity, billing status at https://console.anthropic.com
3. If both down: system runs in degraded mode — all agents use algorithmic fallback
4. To force provider switch immediately:
   ```python
   # Force Claude
   $env:USE_LOCAL_AI = "false"
   # Force Ollama (reset circuit breaker)
   python -c "from ai.client import llm; llm.ollama_circuit.reset(); llm.claude_circuit.reset()"
   ```

**Recovery:**
1. Verify restored provider with `/health/ready`
2. Test agent: `python -c "import asyncio; from ai.client import llm; print(asyncio.run(llm.generate('hello')))"`
3. Monitor token usage for first hour after recovery

---

### RB-AI-006: Token Budget Exceeded

**Severity:** P2-AI

**Detection:**
- AI responses truncated mid-sentence
- `max_tokens` limit warning in logs
- Token usage anomaly alert in Sentry
- Agent returns partial JSON (malformed, unparseable)

**Triage:**
```bash
# 1. Check which agent exceeds budget
Get-Content -Path logs/ai.log -Tail 200 | Select-String "token|budget|truncat" | Select-Object -First 10

# 2. Check current max_tokens per prompt
python -c "
from ai.prompt_loader import prompts
for name in prompts.list_prompts('agents'):
    p = prompts.get_agent(name)
    if p:
        print(f'{name}: max_tokens={p.frontmatter.get(\"max_tokens\", \"N/A\")}, output_tokens_estimate=N/A')
"
```

**Mitigation:**
1. Increase `max_tokens` in the affected prompt's frontmatter (if headroom exists)
2. Reduce prompt complexity: trim few-shot examples, shorter instructions
3. Simplify agent input context (less data passed to LLM)
4. If repeated: add token counting pre-check before sending to LLM
5. Circuit breaker: if token waste detected (repeated truncation), break and fallback

**Recovery:**
1. Update affected prompt with realistic `max_tokens` value
2. Add output length validation in the agent module
3. Monitor output token usage for 7 days

---

## 5. Communication Templates

### 5.1 Internal Alert Template

```
🔴 AI INCIDENT: [SEVERITY] — [BRIEF TITLE]

Time: <UTC timestamp>
Detected by: <sentry|manual|user report>
Severity: P<0-3>-AI
Affected: <agent(s)>
Provider: <Ollama|Claude|both>
Status: <investigating|mitigating|resolved>

Summary:
<2-3 sentence description>

Actions taken:
- <action 1>
- <action 2>

Next steps:
- <step 1>
- <step 2>

Incident channel: <Slack/Discord link>
```

### 5.2 User Notification Template (P0 Data Leakage)

```
Subject: Security Notice — Second Brain OS

We identified and contained a security incident that may have exposed some of your data.

What happened:
<Brief, honest description of what occurred>

What we did:
- Immediately shut down the affected service
- Rotated all credentials
- Fixed the underlying isolation issue

What you should do:
- Your account is secure — no password change needed
- If you notice anything unusual, report it to developer@secondbrain-os.com

We apologize for this experience. We take your data security seriously and have implemented additional safeguards.

Questions? Contact developer@secondbrain-os.com
```

### 5.3 User Notification Template (P1 Hallucination/Bias)

```
Subject: Service Quality Notice — AI Assistant

Our AI assistant recently generated responses that did not meet our quality standards.

What happened:
<Brief description, e.g., "The assistant occasionally produced incorrect information">

What we did:
- Identified the root cause (model configuration)
- Updated our AI prompts with stricter accuracy guidelines
- Switched to a more reliable response mode

No action is needed on your part. We continuously monitor and improve our AI.

Questions? Contact developer@secondbrain-os.com
```

---

## 6. Post-AI-Incident Review Template

```markdown
# AI Incident Post-Mortem: [Title]

**Date:** YYYY-MM-DD
**Severity:** P0-AI / P1-AI / P2-AI / P3-AI
**Duration:** HH:MM
**Agents Affected:** [list]
**Provider:** Ollama / Claude / Both
**Responder:** @developer

## Summary
(2-3 sentences)

## Timeline
- HH:MM - Detection
- HH:MM - Triage complete
- HH:MM - Mitigation applied
- HH:MM - Resolution confirmed
- HH:MM - User notified (if applicable)

## Root Cause
(What caused the incident — be specific)

## Impact
- Users affected: #
- Harmful content generated: Yes/No (details)
- Data exposure: Yes/No (details)
- Downtime: HH:MM

## Detection Gap
(How was it detected? How could it have been detected sooner?)

## Action Items
| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| 1 | [Fix description] | Developer | YYYY-MM-DD | [Open/Done] |
| 2 | [Monitoring improvement] | Developer | YYYY-MM-DD | [Open/Done] |
| 3 | [Test added] | Developer | YYYY-MM-DD | [Open/Done] |

## Prompt Changes
| Prompt | Version Before | Version After | Change |
|---|---|---|---|
| `prompts/agents/<name>.md` | X.Y.Z | X.Y.Z+1 | Description of change |

## Lessons Learned
(What went well, what could be improved, process changes needed)

## Appendices
- Link to incident logs
- Link to affected commits/PRs
- Link to test results post-fix
```

---

## 7. Prevention Measures

| Measure | Frequency | Owner |
|---|---|---|
| Prompt injection testing | Every prompt change | Developer |
| Hallucination audit (sampled outputs) | Weekly | Developer |
| Bias audit (prompt content review) | Every prompt change | Developer |
| Circuit breaker drill | Monthly | Developer |
| Provider failover test | Monthly | Developer |
| User feedback review | Daily | Automated |
| Prompt content review | Per prompt change (via CI) | Developer |
| Guardrails update | Monthly or after injection incident | Developer |

---

## 8. Escalation Matrix

| Situation | Escalate To | Method | Timing |
|---|---|---|---|
| P0-AI (harmful content / data leak) | Developer | Phone / SMS | Immediate |
| P1-AI (hallucination / bias / outage) | Developer | Slack DM | Within 15 min |
| P2-AI (single agent issue) | Developer | GitHub Issue | Within 1 hour |
| P3-AI (quality issue) | Developer | GitHub Issue | Next business day |
| Prompt injection variant not in guardrails | Developer | Slack DM | Within 1 hour |
| Provider billing / account issue | Anthropic / Ollama support | Email | Within 24 hours |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial AI incident response document: 6 runbook scenarios, severity definitions, communication templates, post-mortem template |
