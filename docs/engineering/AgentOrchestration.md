# Agent Orchestration

## Document Control

| Property | Value |
|---|---|
| **Document ID** | DOC-ENG-008 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Author** | AI Engineering Team |
| **Last Updated** | 2026-06-11 |
| **Approved By** | — |
| **Supersedes** | ADR-004 (detailed implementation) |

---

## 1. Executive Summary

Agent orchestration is the system by which user inputs and system events are routed to the correct AI agent(s), executed with appropriate context, and composed into a coherent response. In Second Brain OS, orchestration governs how ARIA's 8 specialized sub-agents work together — or independently — to handle tasks ranging from daily briefing generation to opportunity scanning to memory consolidation.

**Why orchestration matters:**

- **Correctness**: Without orchestration, agents operate in isolation. A user greeting ("Good morning") should trigger the Briefing Agent, check sleep data, summarize tasks, and return a unified response — not require the user to invoke three separate commands.
- **Performance**: Parallel dispatch of independent agents (e.g., Task Agent + Learning Agent + Sleep Monitor) reduces response latency from sequential sum to max-of-parallel.
- **Extensibility**: A defined orchestration framework means adding a new agent (e.g., a "Project Analyzer") requires only a registration entry and an intent classifier rule — no changes to existing agents.
- **Observability**: Every orchestration decision is traceable — which agent was chosen, why, how long it took, what it returned, and whether it failed.

This document defines the agent catalog, orchestration patterns, communication protocol, lifecycle management, error handling, and scaling strategy for the Second Brain OS agent system.

---

## 2. Agent Registry

The system comprises 8 specialized sub-agents (per ADR-004, implemented as in-process async functions) plus the Orchestrator. Each agent has a defined purpose, trigger conditions, and response schema.

### Agent Catalog

| ID | Name | Purpose | Trigger | Model |
|---|---|---|---|---|
| `orchestrator` | Orchestrator Agent | Routes inputs, dispatches agents, merges responses | Every user message + system event | Claude Sonnet 4 |
| `briefing` | Briefing Agent | Generates daily morning briefing | Scheduled (6 AM daily) + on-demand | Claude Sonnet 4 |
| `planner` | Planner Agent | Schedules tasks, ranks priorities | On-demand + part of briefing | Ollama (Llama 3) |
| `task` | Task Agent | Creates, updates, queries tasks | Intent: "task.*" | Ollama (Llama 3) |
| `learning` | Learning Agent | Course tracking, spaced repetition, tutoring | Intent: "learning.*" + scheduled check-in | Claude Haiku 3.5 |
| `memory` | Memory Agent | Summarizes conversations, extracts facts, stores episodic + semantic memory | Post-interaction + scheduled consolidation | Claude Haiku 3.5 |
| `opportunity` | Opportunity Scanner | Matches user skills/ goals to external opportunities | Scheduled (daily) + on-demand | Claude Sonnet 4 |
| `radar` | Radar Agent | Scans external sources (news, GitHub, job boards) for relevant signals | Scheduled (every 6 hours) | Claude Haiku 3.5 |
| `habit` | Habit Coach | Tracks habit streaks, provides encouragement and course correction | Intent: "habit.*" + scheduled check-in | Ollama (Llama 3) |
| `sleep` | Sleep Monitor Agent | Analyzes sleep logs, adjusts daily recommendations | Intent: "sleep.*" + part of briefing | Ollama (Llama 3) |

### Agent Implementation Pattern

Every agent is a standalone async function in `packages/ai/agents/` following this interface:

```python
# packages/ai/agents/base.py
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass
class AgentContext:
    user_id: str
    user_name: str
    working_memory: dict
    prompt_registry: PromptRegistry
    supabase: SupabaseClient
    ollama_client: OllamaClient

class AgentResponse(Protocol):
    success: bool
    data: dict | str
    error: str | None
    latency_ms: int
    token_count: int

class Agent(Protocol):
    """Interface every agent must implement."""
    id: str
    async def execute(self, ctx: AgentContext, input: dict) -> AgentResponse: ...
```

### Agent Files

```
packages/ai/agents/
├── __init__.py
├── base.py                   # AgentContext, AgentResponse, Agent protocol
├── orchestrator.py           # Orchestrator agent
├── briefing.py               # Briefing Agent
├── planner.py                # Planner Agent
├── task.py                   # Task Agent
├── learning.py               # Learning Agent
├── memory.py                 # Memory Agent
├── opportunity.py            # Opportunity Scanner
├── radar.py                  # Radar Agent
├── habit.py                  # Habit Coach
├── sleep.py                  # Sleep Monitor
└── registry.py               # AgentRegistry — maps IDs to agent classes
```

---

## 3. Orchestration Patterns

The Orchestrator supports five orchestration patterns. The pattern for a given input is determined by intent classification.

### 3.1 Sequential

Agents execute one after another, with each agent's output feeding into the next agent's input.

**Use case**: Complex workflows where each step depends on the previous result.

```
User: "Summarize my week and create a report"

Orchestrator:
  1. Task Agent → collect all tasks for the week
  2. Learning Agent → collect course progress
  3. Sleep Agent → collect sleep patterns
  4. Memory Agent → summarize the combined data
  5. → Return final summary to user
```

```python
async def sequential(ctx, agents: list[str], input: dict):
    current_input = input
    for agent_id in agents:
        agent = registry.get(agent_id)
        result = await agent.execute(ctx, current_input)
        if not result.success:
            return AgentResponse(success=False, error=result.error, ...)
        current_input = result.data
    return current_input
```

### 3.2 Parallel

Independent agents execute concurrently. The Orchestrator merges results after all complete.

**Use case**: A user message that touches multiple domains (e.g., "How's my DSA progress and do I have any tasks due?").

```
User: "How's my DSA progress and do I have any tasks due?"

Orchestrator:
  ┌── Learning Agent (DSA progress) ──┐
  └── Task Agent (tasks due) ─────────┘
               ↓
           Merge results → response
```

```python
async def parallel(ctx, agents: list[str], input: dict):
    tasks = [registry.get(a).execute(ctx, input) for a in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    merged = merge_results(input, results)
    return merged
```

### 3.3 Fan-Out

One agent produces output that triggers N independent agents.

**Use case**: A daily briefing triggers data collection from all sub-agents.

```
Scheduled: Daily Briefing

Orchestrator:
  Briefing Agent (coordinator)
     ├── Task Agent → tasks due today
     ├── Sleep Agent → last night's score
     ├── Learning Agent → course progress
     ├── Opportunity Agent → new matches
     └── Radar Agent → new signals
          ↓
     Collect all → Briefing Agent generates final output
```

### 3.4 Conditional

The path through agents depends on the content of the input or the result of a previous agent.

**Use case**: "I'm feeling overwhelmed" — check what's happening before deciding action.

```
User: "I'm feeling overwhelmed"

Orchestrator:
  1. Task Agent → count overdue tasks
  2. If overdue > 5:
       → Planner Agent (reschedule and simplify)
     Else:
       → Habit Agent (encouragement + check)
  3. → Return response
```

```python
async def conditional(ctx, input: dict):
    task_result = await registry.get("task").execute(ctx, input)
    overdue_count = task_result.data.get("overdue_count", 0)

    if overdue_count > 5:
        agent = registry.get("planner")
    else:
        agent = registry.get("habit")

    return await agent.execute(ctx, {"overdue_count": overdue_count, ...})
```

### 3.5 Recursive

An agent may invoke itself (or another agent) with refined parameters based on partial results.

**Use case**: Memory Agent needs deeper summarization of a long conversation.

```
Memory Agent:
  1. Summarize first chunk of messages
  2. If total messages > threshold:
       → Recursively summarize summary + next chunk
  3. → Return final summary
```

---

## 4. Current Architecture

Per **ADR-004**, all agents are in-process async functions within the same FastAPI application. There is no separate agent service, no message queue, and no inter-process communication.

### Architecture Diagram

```
FastAPI App (single uvicorn process)
┌─────────────────────────────────────────────────────────────────┐
│  apps/api/app/api/                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Route Handler (e.g., /api/chat)                        │    │
│  │  1. Parse request                                       │    │
│  │  2. Build AgentContext (user_id, working_memory, etc.)  │    │
│  │  3. Call orchestrator.execute(ctx, input)               │    │
│  │  4. Return response                                     │    │
│  └──────────────┬──────────────────────────────────────────┘    │
│                 │                                               │
│                 ▼                                               │
│  packages/ai/agents/                                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Orchestrator Agent                                     │    │
│  │  1. Intent classification                                │    │
│  │  2. Pattern selection (sequential/parallel/conditional)  │    │
│  │  3. Agent dispatch                                       │    │
│  │  4. Output synthesis                                     │    │
│  └──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────┘    │
│         │      │      │      │      │      │      │             │
│  ┌──────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐            │
│  │Brief││Plan││Task││Learn││Mem ││Opp ││Radar││Habit│            │
│  └──────┘└────┘└────┘└────┘└────┘└────┘└────┘└────┘            │
│         │      │      │      │      │      │      │             │
│         ▼      ▼      ▼      ▼      ▼      ▼      ▼             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Shared Infrastructure                                  │    │
│  │  - OllamaClient (localhost:11434)                       │    │
│  │  - ClaudeClient (API key in vault)                      │    │
│  │  - SupabaseClient (connection pool)                     │    │
│  │  - PromptRegistry (prompts/registry.yaml)               │    │
│  │  - Cache (in-memory TTL cache)                          │    │
│  │  - Logger (structured JSON)                             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Single event loop**: All async agents share the same event loop. I/O-bound operations (HTTP calls to Ollama, Supabase queries) do not block.
- **No inter-agent serialization**: Agents pass Python dicts directly. No JSON marshal/unmarshal overhead.
- **Shared imports**: Every agent imports shared utilities (logger, cache, rate limiter) directly — no duplication.
- **BackgroundTasks for long work**: CPU-intensive or long-running agent work (e.g., Radar scanning 5 sources) uses `asyncio.create_task()` or FastAPI `BackgroundTasks` to avoid blocking the request cycle.

---

## 5. Agent Communication Protocol

Agents communicate through a standardized message format. Every input and output conforms to this schema.

### Message Format

```json
{
  "intent": "task.create | task.query | learning.progress | sleep.log | ...",
  "payload": {
    // Domain-specific data
  },
  "context": {
    "user_id": "uuid",
    "conversation_id": "uuid",
    "message_id": "uuid",
    "timestamp": "2026-06-11T06:00:00Z",
    "source": "user | system | agent",
    "trace_id": "uuid"
  },
  "metadata": {
    "model": "claude-sonnet-4 | ollama/llama3",
    "max_tokens": 1024,
    "temperature": 0.7
  }
}
```

### Response Schema

```json
{
  "success": true,
  "data": {
    // Agent-specific response payload
  },
  "error": null,
  "metrics": {
    "latency_ms": 1234,
    "token_count": 567,
    "model": "claude-sonnet-4"
  },
  "trace_id": "uuid"
}
```

### Supported Intents

| Intent Pattern | Agents | Description |
|---|---|---|
| `greeting.*` | orchestrator → briefing | User greeting, triggers briefing if morning |
| `task.*` | orchestrator → task | CRUD operations on tasks |
| `learning.*` | orchestrator → learning | Course tracking, tutoring, quiz requests |
| `memory.*` | orchestrator → memory | Explicit memory query or store |
| `sleep.*` | orchestrator → sleep | Sleep log query or analysis |
| `habit.*` | orchestrator → habit | Habit tracking, streak check |
| `opportunity.*` | orchestrator → opportunity | Opportunity search/match |
| `planner.*` | orchestrator → planner | Scheduling, prioritization |
| `system.*` | orchestrator | System-level commands (status, config) |
| `fallback.*` | orchestrator → LLM general | Unrecognized intent → general chat |

---

## 6. Orchestrator Engine

The Orchestrator Engine is the core dispatch logic that processes every incoming message.

### Pipeline

```
Input → Intent Classification → Context Assembly → Agent Dispatch → Output Synthesis → Response
```

### Stage 1: Intent Classification

The first step is determining what the user wants. This is done by a lightweight classifier (not a full LLM call) to minimize latency.

```python
class IntentClassifier:
    def classify(self, message: str, context: AgentContext) -> str:
        # Pattern matching for known intents
        if message.lower().startswith(("hello", "hi", "good morning", "good evening")):
            return "greeting.basic"

        if message.lower().startswith(("create task", "add task", "new task")):
            return "task.create"

        if message.lower().startswith(("show tasks", "my tasks", "what's due")):
            return "task.query"

        if message.lower().startswith(("explain", "teach me", "what is", "quiz me")):
            return "learning.tutor"

        # Regex-based intent detection
        if re.search(r"(sleep|slept|insomnia|tired)", message.lower()):
            return "sleep.check"

        # Fallback: use a small LLM call for ambiguous intents
        if self._is_ambiguous(message):
            return self._llm_classify(message, context)

        return "fallback.general"
```

### Stage 2: Context Assembly

Before dispatching to sub-agents, the Orchestrator builds the working memory context (see Memory Architecture DOC-AI-004):

```python
async def assemble_context(self, user_id: str) -> AgentContext:
    user = await self.supabase.from_("users").select("*").eq("id", user_id).single().execute()

    working_memory = {
        "identity": {
            "user_name": user.data["name"],
            "last_interaction": user.data["last_interaction"],
        },
        "temporal": {
            "current_time": datetime.utcnow().isoformat(),
            "day_of_week": datetime.utcnow().strftime("%A"),
            "time_of_day": self._time_of_day(),
        },
        "session": {
            "message_count_today": await self._message_count_today(user_id),
            "last_3_messages": await self._last_n_messages(user_id, 3),
        },
        "state": {
            "tasks_today_count": await self._tasks_due_count(user_id),
            "overdue_count": await self._overdue_count(user_id),
            "sleep_score": await self._latest_sleep_score(user_id),
            "active_goals_count": await self._active_goals_count(user_id),
        },
    }

    return AgentContext(
        user_id=user_id,
        user_name=user.data["name"],
        working_memory=working_memory,
        prompt_registry=self.prompt_registry,
        supabase=self.supabase,
        ollama_client=self.ollama_client,
    )
```

### Stage 3: Agent Dispatch

Based on the intent and the selected orchestration pattern, the Orchestrator dispatches to one or more agents:

```python
async def dispatch(self, ctx: AgentContext, intent: str, payload: dict) -> dict:
    match intent:
        case "greeting.basic":
            # Parallel: check tasks + sleep + learning progress
            return await self._parallel(ctx, ["task", "sleep", "learning"], payload)

        case "task.create":
            return await self._sequential(ctx, ["task"], payload)

        case "learning.tutor":
            return await self._sequential(ctx, ["learning"], payload)

        case _:
            return await self._sequential(ctx, ["fallback"], payload)
```

### Stage 4: Output Synthesis

After all agents complete, the Orchestrator merges results into a single response. For parallel patterns, this involves combining multiple agent outputs into a coherent message:

```python
async def synthesize(self, intent: str, results: list[AgentResponse]) -> str:
    if len(results) == 1:
        return results[0].data

    # Multiple results — merge into a single narrative
    merge_prompt = self.prompt_registry.get("response-merger", "==1.0.0")
    resolved = merge_prompt.format(results=results)
    final_response = await self.ollama_client.generate(
        model="claude-sonnet-4",
        prompt=resolved,
        max_tokens=1024,
    )
    return final_response
```

---

## 7. Agent Lifecycle

Every agent invocation follows a defined lifecycle. This lifecycle is enforced by the base agent infrastructure.

```
IDLE → TRIGGERED → CONTEXT_LOADING → EXECUTING → RESPONDING → CLEANUP → IDLE
```

| Stage | Description | Duration Limit |
|---|---|---|
| **IDLE** | Agent is registered but not active. No resources consumed. | ∞ |
| **TRIGGERED** | Intent classifier has selected this agent. Dispatch is initiated. | < 10ms |
| **CONTEXT_LOADING** | AgentContext is assembled: working memory built, Supabase queried, prompt loaded. | < 1s |
| **EXECUTING** | LLM call is made (Ollama or Claude). Agent processes the response. | < 5s (configurable timeout) |
| **RESPONDING** | Agent output is validated against schema and returned to Orchestrator. | < 100ms |
| **CLEANUP** | Temporary resources released, metrics logged, memory consolidation triggered if needed. | < 500ms |

### Lifecycle Hook Points

```python
# packages/ai/agents/base.py
class BaseAgent:
    async def execute(self, ctx: AgentContext, input: dict) -> AgentResponse:
        start = time.monotonic()
        trace_id = input.get("context", {}).get("trace_id", str(uuid.uuid4()))

        try:
            # 1. TRIGGERED
            logger.log_agent_event(self.id, "triggered", trace_id=trace_id)

            # 2. CONTEXT_LOADING
            agent_context = await self._load_context(ctx, input)
            prompt = self._load_prompt(ctx, agent_context)

            # 3. EXECUTING
            model_output = await self._call_llm(ctx, prompt, agent_context)
            validated = self._validate_output(model_output)

            # 4. RESPONDING
            elapsed = int((time.monotonic() - start) * 1000)
            response = AgentResponse(
                success=True,
                data=validated,
                error=None,
                latency_ms=elapsed,
                token_count=model_output.token_count,
            )

            # 5. CLEANUP
            await self._cleanup(ctx, response)
            logger.log_agent_response(self.id, response, trace_id=trace_id)

            return response

        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.log_agent_error(self.id, str(e), trace_id=trace_id)
            return AgentResponse(
                success=False,
                data={},
                error=str(e),
                latency_ms=elapsed,
                token_count=0,
            )
```

---

## 8. Error Handling

Agents must handle failures gracefully. The system defines four layers of error handling:

### 8.1 Agent Timeout (5s)

Every agent call has a 5-second timeout. If the LLM does not respond within 5 seconds, the agent returns a timeout error.

```python
async def _call_llm(self, ctx, prompt, context) -> ModelOutput:
    try:
        return await asyncio.wait_for(
            ctx.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                max_tokens=self.max_tokens,
            ),
            timeout=5.0,  # 5-second timeout
        )
    except asyncio.TimeoutError:
        raise AgentTimeoutError(f"Agent {self.id} timed out after 5s")
```

### 8.2 Retry (1x)

Agents automatically retry once on transient failures (network errors, HTTP 5xx, timeout).

```python
async def execute_with_retry(self, ctx, input, max_retries=1):
    for attempt in range(max_retries + 1):
        try:
            return await self.execute(ctx, input)
        except (HTTPError, TimeoutError) as e:
            if attempt < max_retries:
                logger.log_agent_retry(self.id, attempt + 1)
                await asyncio.sleep(0.5 * (attempt + 1))  # Simple backoff
                continue
            raise
```

### 8.3 Circuit Breaker

If an agent fails 5 consecutive times, the circuit breaker opens and the agent is not called for 60 seconds. During this period, the Orchestrator returns a graceful degradation message.

```python
class CircuitBreaker:
    def __init__(self, threshold=5, recovery_time=60):
        self.failures = {}
        self.open_until = {}

    def is_open(self, agent_id: str) -> bool:
        if agent_id in self.open_until:
            if time.monotonic() < self.open_until[agent_id]:
                return True
            del self.open_until[agent_id]
        return False

    def record_failure(self, agent_id: str):
        self.failures[agent_id] = self.failures.get(agent_id, 0) + 1
        if self.failures[agent_id] >= 5:
            self.open_until[agent_id] = time.monotonic() + 60
            self.failures[agent_id] = 0
```

### 8.4 Graceful Degradation

When an agent fails (or the circuit is open), the Orchestrator does not crash. It returns a partial response:

```python
# In orchestrator dispatch
try:
    result = await agent.execute(ctx, input)
except Exception:
    return AgentResponse(
        success=False,
        data={
            "error": f"Agent {agent.id} is currently unavailable.",
            "fallback": "I'll process this manually and get back to you.",
        },
        error="Agent circuit breaker open",
        ...
    )
```

---

## 9. Observability

Every agent invocation produces structured logs and metrics. These are collected in Supabase and visualized in a dashboard.

### Agent Trace Log

```json
{
  "trace_id": "a1b2c3d4-...",
  "user_id": "user-uuid",
  "intent": "greeting.basic",
  "pattern": "parallel",
  "agents": [
    {
      "agent_id": "task",
      "status": "success",
      "latency_ms": 234,
      "token_count": 156,
      "model": "ollama/llama3"
    },
    {
      "agent_id": "sleep",
      "status": "success",
      "latency_ms": 187,
      "token_count": 98,
      "model": "ollama/llama3"
    },
    {
      "agent_id": "learning",
      "status": "timeout",
      "latency_ms": 5000,
      "token_count": 0,
      "model": "ollama/llama3",
      "error": "Agent timed out after 5s"
    }
  ],
  "total_latency_ms": 5421,
  "total_tokens": 254,
  "timestamp": "2026-06-11T06:00:00Z"
}
```

### Stored in Supabase

```sql
CREATE TABLE agent_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    intent VARCHAR(64),
    pattern VARCHAR(32),
    total_latency_ms INTEGER,
    total_tokens INTEGER,
    agent_details JSONB,  -- array of per-agent metrics
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL,
    agent_id VARCHAR(64) NOT NULL,
    error_type VARCHAR(64),  -- timeout, model_error, validation_error
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Key Metrics

| Metric | Source | Alert Threshold |
|---|---|---|
| Per-agent latency P95 | `agent_traces` | > 3s |
| Agent error rate | `agent_errors` | > 5% |
| Token usage per session | `agent_traces` | > 4096 |
| Circuit breaker events | `agent_errors` (type=circuit_breaker) | Any |
| Intent classification accuracy | Manual audit sample | < 90% |

---

## 10. Multi-Agent Coordination

### 10.1 Handoff Patterns

When an agent determines that another agent should handle part of the work, it can request a handoff:

```python
# Example: Briefing Agent realizes user hasn't slept well, delegates to Sleep Agent
class BriefingAgent(BaseAgent):
    async def execute(self, ctx, input):
        briefing = await self._generate_briefing(ctx, input)

        if briefing.get("sleep_score", 100) < 60:
            # Handoff to Sleep Agent for deeper analysis
            sleep_analysis = await ctx.orchestrator.dispatch(
                ctx, "sleep.analyze", {"score": briefing["sleep_score"], ...}
            )
            briefing["sleep_analysis"] = sleep_analysis.data

        return AgentResponse(success=True, data=briefing)
```

### 10.2 Shared Context

All agents in a dispatch chain share the same `AgentContext`. This ensures:

- Consistent user identity
- Consistent temporal awareness
- Shared access to Supabase (without re-authenticating)
- Consistent model configuration

The context is read-only during execution. Agents must not mutate the shared context — only read from it and return data in their response.

### 10.3 Conflict Resolution

When two agents return conflicting information (e.g., Planner recommends task A, but based on new input Learning says task B is more urgent), the Orchestrator applies conflict resolution rules:

```python
class ConflictResolver:
    PRIORITY = {
        "orchestrator": 10,
        "sleep": 8,
        "learning": 7,
        "task": 6,
        "planner": 5,
        "habit": 4,
        "opportunity": 3,
        "radar": 2,
        "memory": 1,
    }

    def resolve(self, conflicts: list[Conflict]) -> Resolution:
        # Highest priority agent wins
        winner = max(conflicts, key=lambda c: self.PRIORITY.get(c.agent_id, 0))
        return Resolution(winning_response=winner.response, overridden=conflicts)
```

---

## 11. Scaling Agents

### 11.1 Current: In-Process (ADR-004)

All agents run in the same FastAPI process. This is the current architecture and is appropriate for single-user or small-team usage. Limitations:

- No fault isolation between agents
- No independent scaling
- Event loop contention from CPU-heavy work

### 11.2 Near-Term: Background Workers

CPU-heavy agent work (Radar scanning, Memory consolidation) is offloaded to background workers via Supabase queue or APScheduler:

```python
# apps/api/app/api/agents.py
@router.post("/trigger/radar-scan")
async def trigger_radar_scan(user_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(radar_agent.full_scan, user_id)
    return {"status": "scan_started"}
```

### 11.3 Future: Distributed Agent Workers

If the system needs to scale to hundreds of concurrent users, agents can be extracted into independent services:

```
                           ┌──────────────────┐
                           │   API Gateway    │
                           │   (FastAPI)      │
                           └────────┬─────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Agent Worker 1  │     │  Agent Worker 2  │     │  Agent Worker 3  │
│  (Briefing)      │     │  (Memory)        │     │  (Radar)         │
│  uvicorn:8001    │     │  uvicorn:8002    │     │  uvicorn:8003    │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                       ┌──────────────────┐
                       │  Message Queue   │
                       │  (Redis/NATS)    │
                       └──────────────────┘
```

The agent interface (`Agent.execute(ctx, input)`) does not change when moving from in-process to distributed — only the transport mechanism differs. The same `AgentContext` and `AgentResponse` types are used, serialized to JSON for network transport.

---

## 12. Appendices

### Appendix A: Agent Catalog Detail

| Agent | File | Model | Timeout | Retry | Circuit Breaker |
|---|---|---|---|---|---|
| Orchestrator | `orchestrator.py` | Claude Sonnet 4 | 5s | No | No (critical path) |
| Briefing | `briefing.py` | Claude Sonnet 4 | 10s | 1x | Yes |
| Planner | `planner.py` | Ollama (Llama 3) | 5s | 1x | Yes |
| Task | `task.py` | Ollama (Llama 3) | 3s | 1x | Yes |
| Learning | `learning.py` | Claude Haiku 3.5 | 5s | 1x | Yes |
| Memory | `memory.py` | Claude Haiku 3.5 | 8s | 1x | Yes |
| Opportunity | `opportunity.py` | Claude Sonnet 4 | 10s | 1x | Yes |
| Radar | `radar.py` | Claude Haiku 3.5 | 15s | 0 (long background) | Yes |
| Habit | `habit.py` | Ollama (Llama 3) | 3s | 1x | Yes |
| Sleep | `sleep.py` | Ollama (Llama 3) | 3s | 1x | Yes |

### Appendix B: Message Schemas

```python
# From packages/ai/agents/base.py

@dataclass
class AgentContext:
    user_id: str
    user_name: str
    working_memory: dict
    prompt_registry: PromptRegistry
    supabase: SupabaseClient
    ollama_client: OllamaClient
    claude_client: ClaudeClient

@dataclass
class AgentResponse:
    success: bool
    data: dict | str
    error: str | None
    latency_ms: int
    token_count: int
    trace_id: str

@dataclass
class AgentRequest:
    intent: str
    payload: dict
    context: dict  # user_id, conversation_id, trace_id, etc.
    metadata: dict  # model, max_tokens, temperature, etc.
```

### Appendix C: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | AI Engineering | Initial document |
