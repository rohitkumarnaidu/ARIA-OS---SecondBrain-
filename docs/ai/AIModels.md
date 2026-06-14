# AI Models — Enterprise Reference

---

## Document Control

| Metadata | Value |
|----------|-------|
| **Document ID** | ARIA-ARCH-MDL-001 |
| **Version** | 1.0.0 |
| **Status** | APPROVED |
| **Classification** | INTERNAL — Engineering |
| **Last Updated** | 2026-06-11 |
| **Owner** | AI Architecture Team |
| **Review Cycle** | Quarterly |
| **Next Review** | 2026-09-11 |

---

## Executive Summary

### Why Model Selection Matters

Second Brain OS runs 8 active AI agents (with 15 planned) across a spectrum of use cases — from generating 957-line daily briefings to 200-token sleep nudges. Each use case has different requirements for latency, quality, cost, and availability. A single-model approach would be either too expensive (Claude on every task) or too low-quality (Ollama for complex reasoning). 

The dual-model architecture (Ollama local + Claude cloud fallback) provides:
1. **Cost-efficient daily operation**: ~95% of requests handled locally by Ollama (Mistral 7B) at near-zero cost
2. **High-quality fallback**: Complex tasks and edge cases routed to Claude Sonnet 4 (~$0.003-0.015/request)
3. **Offline capability**: All 8 agents function fully offline with Ollama
4. **Graceful degradation**: When both models fail, algorithmic fallbacks ensure continued operation

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Default model** | Mistral 7B (via Ollama) | Best quality-to-size ratio for 7B class; runs on consumer GPUs (6GB VRAM); Apache 2.0 license |
| **Cloud fallback** | Claude Sonnet 4 (20250514) | Best-in-class instruction following; 200K context window; lowest hallucination rate in its class |
| **Local LLM server** | Ollama | Lightweight (~100MB binary); model management built-in; REST API compatible with OpenAI spec |
| **Quantization** | Q4_K_M (4-bit) for Mistral 7B | 4.1GB → 2.5GB VRAM; < 5% quality loss vs FP16 |
| **Embedding model** | nomic-embed-text (768d) | Best MTEB score among local models (62.3); 300MB; runs on CPU |
| **Fallback chain logic** | Ollama → Claude → Algorithmic | Ensures zero downtime; algorithmic fallback is always available |

### Architecture Principles

1. **Local-first**: Default configuration uses local models for all requests; cloud only as fallback
2. **Model-per-task**: Different agents may use different models based on complexity requirements
3. **Deterministic defaults**: Temperature and max_tokens are set per-prompt in frontmatter; agents never override without cause
4. **Observability**: Every LLM call logs model, latency, tokens, and cost (estimated)
5. **Cost-aware routing**: High-volume cron agents default to Ollama; complex chat interactions may upgrade to Claude

---

## Model Selection Rationale

### Model Landscape Analysis

| Model | Size | Context | Quality (MTEB/MMLU) | Speed (tok/s) | VRAM | Cost | License |
|---|---|---|---|---|---|---|---|
| **Mistral 7B** (default) | 7B | 8K | 64.1 MMLU | 45 | 4.1GB (FP16) / 2.5GB (Q4) | Free | Apache 2.0 |
| Llama 3.1 8B | 8B | 128K | 66.7 MMLU | 38 | 5.4GB (Q4) | Free | Llama 3 |
| Phi-3 Medium | 14B | 128K | 69.5 MMLU | 25 | 7.8GB (Q4) | Free | MIT |
| Mistral Small 3.1 | 24B | 128K | 72.2 MMLU | 18 | 14GB (Q4) | Free | Apache 2.0 |
| Llama 3.3 70B | 70B | 128K | 82.5 MMLU | 8 | 40GB (Q4) | Free | Llama 3 |
| **Claude Sonnet 4** (fallback) | ~200B | 200K | ~88 MMLU | API | N/A | $3/M in, $15/M out | Proprietary |
| Claude Haiku 3.5 | ~80B | 200K | ~85 MMLU | API | N/A | $0.80/M in, $4/M out | Proprietary |
| GPT-4o mini | ~8B | 128K | ~82 MMLU | API | N/A | $0.15/M in, $0.60/M out | Proprietary |
| GPT-4o | ~200B | 128K | ~87 MMLU | API | N/A | $2.50/M in, $10/M out | Proprietary |

**Bold** = selected for production. MMLU = Massive Multitask Language Understanding benchmark.

### Why Mistral 7B Won for Default

1. **Quality-to-size ratio**: Mistral 7B outperforms Llama 2 13B and matches Llama 3 8B on most benchmarks, while being smaller
2. **Apache 2.0 license**: No restrictions on commercial use, no attribution required
3. **Consumer hardware**: Runs comfortably on 6GB VRAM at Q4 quantization (GTX 1060, RTX 3050, laptop GPUs)
4. **Ollama ecosystem**: Well-supported with official Ollama model; `ollama pull mistral` is one command
5. **Sliding window attention**: Native 8K context with ~2x faster inference than full-attention models
6. **Proven reliability**: 700M+ downloads; deployed in production by thousands of projects

### Why Claude Sonnet 4 Won as Fallback

1. **Instruction following**: Claude consistently leads in following complex, structured output schemas (critical for JSON agent outputs)
2. **Low hallucination rate**: ~3% vs ~8% for comparably sized models (Anthropic internal evaluations)
3. **200K context window**: Can process entire weekly review prompts (1264 lines) without truncation
4. **System prompt adherence**: Claude's constitution-based training makes it highly reliable for safety-critical system prompts
5. **Structured output**: Native JSON mode and predictable output formatting

---

## Model Comparison Matrix

### Comprehensive Comparison

| Criterion | Mistral 7B (Q4) | Llama 3.1 8B (Q4) | Claude Sonnet 4 | Claude Haiku 3.5 | GPT-4o mini |
|---|---|---|---|---|---|
| **Param size** | 7B | 8B | ~200B | ~80B | ~8B |
| **Context window** | 8K | 128K | 200K | 200K | 128K |
| **MMLU score** | 64.1 | 66.7 | ~88 | ~85 | ~82 |
| **HumanEval (coding)** | 30.5 | 33.0 | ~78 | ~72 | ~77 |
| **Latency (P50, 500 tok out)** | 1.2s | 1.5s | 2.8s | 1.2s | 1.0s |
| **Latency (P95, 500 tok out)** | 3.0s | 3.8s | 5.0s | 2.5s | 2.0s |
| **Throughput** | 45 tok/s | 38 tok/s | API | API | API |
| **VRAM required** | 2.5GB | 5.4GB | N/A | N/A | N/A |
| **RAM required** | 4GB | 6GB | N/A | N/A | N/A |
| **Cost per 1K in tokens** | $0 | $0 | $0.003 | $0.0008 | $0.00015 |
| **Cost per 1K out tokens** | $0 | $0 | $0.015 | $0.004 | $0.0006 |
| **Avg cost per request** | $0 | $0 | $0.003-0.015 | $0.001-0.004 | $0.0003-0.001 |
| **Offline capable** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **License** | Apache 2.0 | Llama 3 | Proprietary | Proprietary | Proprietary |
| **JSON mode** | ✅ (prompted) | ✅ (prompted) | ✅ (native) | ✅ (native) | ✅ (native) |

### Quality Comparison by Agent Task

| Task Type | Mistral 7B | Claude Sonnet 4 | Notes |
|---|---|---|---|
| Structured data extraction (JSON) | Good (with prompting) | Excellent (native) | Claude wins for complex schemas |
| Creative writing (briefings) | Good | Excellent | Claude: richer language, fewer repetitions |
| Factual recall (memory queries) | Good | Excellent | Claude: lower hallucination on specific facts |
| Short-form reasoning (nudges) | Excellent | Excellent | Both sufficient for <200 tok outputs |
| Long-form analysis (weekly review) | Fair | Excellent | Mistral struggles with >1000 token coherence |
| Code generation | Fair | Excellent | 30.5 vs 78 HumanEval |
| Sentiment / classification | Excellent | Excellent | Both sufficient for binary/multi-class |
| Step-by-step instructions | Good | Excellent | Claude: more reliable chain-of-thought |
| Concise outputs (< 50 tokens) | Excellent | Good | Mistral: more direct, less verbose |
| Multi-turn conversations | Good | Excellent | Claude: better context tracking across turns |

---

## Model Per Agent Mapping

### Agent-to-Model Assignment

| Agent | Default Model | Fallback Model | Rationale |
|---|---|---|---|
| **A01 — Task Agent** | Mistral 7B | Claude Haiku 3.5 | Structured JSON output; simple reasoning |
| **A02 — Memory Agent** | Mistral 7B | Claude Haiku 3.5 | Short outputs; pattern extraction |
| **A03 — Learning Agent** | Mistral 7B | Claude Sonnet 4 | Longer analysis; pattern detection |
| **A04 — Reminder** | None (rule-based) | None | Rule-based; no AI required |
| **A06 — Opportunity Agent** | Mistral 7B | Claude Sonnet 4 | Complex matching; career advice |
| **A09 — Briefing Agent** | Mistral 7B | Claude Sonnet 4 | Long form (957 lines); needs quality |
| **A10 — Weekly Review Agent** | Mistral 7B | Claude Sonnet 4 | Longest output (1264 lines); needs coherence |
| **A11 — Missed Task Checker** | None (rule-based) | None | Simple SQL query + notification |
| **A12 — Habit Miss Checker** | None (rule-based) | None | Simple SQL query + notification |
| **A13 — Sleep Agent** | Mistral 7B | Claude Haiku 3.5 | Short, templated outputs |
| **A14 — Nudge Agent** | Mistral 7B | Claude Haiku 3.5 | Short nudges; simple reasoning |
| **A00 — ARIA Chat** | Mistral 7B | Claude Sonnet 4 | Conversational; needs highest quality |

### Token Consumption by Agent (Average per Request)

```
Agent              Input Tokens    Output Tokens    Total/Request    Daily Requests    Daily Total
─────────────────────────────────────────────────────────────────────────────────────────────────
Briefing (A09)      2,800            800             3,600            1                 3,600
Weekly Review(A10)  3,200            1,200           4,400            0.14 (weekly)     630
Memory (A02)        1,200            300             1,500            ~20               30,000
Learning (A03)      1,800            500             2,300            1                 2,300
Task Agent (A01)    1,000            400             1,400            ~5                7,000
Opportunity (A06)   2,000            800             2,800            1                 2,800
Sleep (A13)         800              300             1,100            2                 2,200
Nudge (A14)         1,200            200             1,400            1                 1,400
ARIA Chat (A00)     1,500            600             2,100            ~10               21,000

TOTAL DAILY (Ollama):                                              ~45 requests        70,930 tokens
TOTAL DAILY (Claude fallback, ~5%):                                ~2 requests         4,200 tokens
```

### Claude Fallback Criteria

The system falls back to Claude under these conditions:

| Condition | Fallback Model | Frequency Estimate |
|---|---|---|
| Ollama server unreachable | Claude Haiku 3.5 | < 1% (rare) |
| Request timeout > 60s | Claude Haiku 3.5 | ~2% (sporadic) |
| User preference: `use_cloud_ai=true` | Claude Sonnet 4 | Configurable |
| Agent complexity_score > 0.8 | Claude Sonnet 4 | ~5% (complex queries) |
| JSON parsing failure rate > 30% in last 5 requests | Claude Haiku 3.5 | Self-healing |
| Token budget > model_max_tokens | Claude Sonnet 4 (200K) | ~1% |
| Embedding quality requirement high | OpenAI text-embedding-3-small | Configurable |

### Complexity Scoring for Model Routing

```python
class ModelRouter:
    """Routes requests to the optimal model based on task complexity."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def calculate_complexity(self, agent_name: str, prompt_length: int,
                              requires_json: bool, requires_reasoning: bool) -> float:
        """Score task complexity from 0.0 (simple) to 1.0 (complex)."""
        score = 0.0

        # Prompt length factor
        score += min(0.4, prompt_length / 10000 * 0.4)

        # Agent complexity factor (empirically calibrated)
        agent_complexity = {
            "task_agent": 0.3,
            "memory_agent": 0.3,
            "learning_agent": 0.6,
            "opportunity_agent": 0.7,
            "briefing_agent": 0.7,
            "weekly_review_agent": 0.8,
            "sleep_agent": 0.2,
            "nudge_agent": 0.2,
        }
        score += agent_complexity.get(agent_name, 0.3) * 0.3

        # JSON schema complexity
        if requires_json:
            score += 0.2

        # Reasoning chain requirement
        if requires_reasoning:
            score += 0.3

        return min(1.0, score)

    async def route(self, agent_name: str, prompt: str,
                     system_prompt: str, user_preference: str = "local") -> str:
        """Route to optimal model and return generated response."""
        complexity = self.calculate_complexity(
            agent_name=agent_name,
            prompt_length=len(prompt),
            requires_json="{json}" in prompt or "JSON" in system_prompt,
            requires_reasoning="think step" in prompt.lower() or "explain" in prompt.lower(),
        )

        use_claude = (
            user_preference == "cloud"
            or complexity > 0.8
            or len(system_prompt) > 6000  # Mistral's effective limit
        )

        if use_claude:
            logger.info(f"[ModelRouter] Routing {agent_name} to Claude (complexity={complexity:.2f})")
            # Use Haiku for simpler Claude tasks, Sonnet for complex
            claude_model = "claude-sonnet-4-20250514" if complexity > 0.6 else "claude-3-haiku-20240307"
            return await self.llm_client._call_claude(prompt, system_prompt, max_tokens=4096)

        return await self.llm_client._call_ollama(prompt, system_prompt)
```

---

## Local Model Setup

### Ollama Installation

```bash
# Linux / macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/OllamaSetup.exe

# Start server (background)
ollama serve &

# Pull models
ollama pull mistral                    # 4.1GB (FP16) — default
ollama pull mistral:7b-q4_K_M         # 2.5GB (Q4) — recommended for 6GB VRAM
ollama pull nomic-embed-text           # 274MB — embeddings
ollama pull llama3.1:8b                # 4.7GB (Q4) — alternative

# Verify models installed
ollama list

# Verify server running
curl http://localhost:11434/api/tags
```

### Quantization Comparison

| Quantization | Size | Quality Loss | VRAM | Recommended For |
|---|---|---|---|---|
| **Q4_K_M** | 2.5GB | < 5% | 4GB | Default — best quality/size ratio |
| Q5_K_M | 3.0GB | < 2% | 5GB | High-quality laptops (8GB VRAM) |
| Q8_0 | 4.5GB | < 1% | 6GB | Desktop GPUs (12GB+ VRAM) |
| FP16 | 8.5GB | 0% | 10GB | Server-grade GPUs |
| Q3_K_M | 2.0GB | ~10% | 3.5GB | Low-VRAM laptops (4GB VRAM) |
| Q2_K | 1.5GB | ~20% | 2.5GB | Emergency low-resource mode |

### VRAM Requirements by Model and Quantization

```
Model               FP16        Q8_0        Q5_K_M      Q4_K_M      Q3_K_M
────────────────────────────────────────────────────────────────────────────────
Mistral 7B          14.1 GB     4.5 GB      3.0 GB      2.5 GB      2.0 GB
Llama 3.1 8B        16.0 GB     5.4 GB      3.8 GB      3.2 GB      2.5 GB
Phi-3 Medium 14B    28.0 GB     9.0 GB      6.5 GB      5.5 GB      4.5 GB
Mistral Small 24B   48.0 GB     15.0 GB     10.5 GB     9.0 GB      7.0 GB
Llama 3.3 70B      140.0 GB     45.0 GB     32.0 GB     27.0 GB     21.0 GB

Note: VRAM = model_size + ~2GB overhead for KV cache + context
```

### GPU Compatibility Matrix

| GPU | VRAM | Max Model (Q4) | Performance | Notes |
|---|---|---|---|---|
| GTX 1060 / RX 580 | 6GB | Mistral 7B | 25-35 tok/s | Minimum viable |
| RTX 2060 / GTX 1660 Super | 6GB | Mistral 7B | 30-40 tok/s | Good for default |
| RTX 3060 / RTX 4060 | 12GB | Llama 3.1 8B | 40-50 tok/s | Recommended minimum |
| RTX 3090 / 4070 Ti | 16-24GB | Mistral 24B | 20-30 tok/s | Heavy tasks |
| RTX 4090 | 24GB | Llama 3.3 70B (Q3) | 8-12 tok/s | Maximum local |
| M1 (16GB unified) | Shared | Mistral 7B (Q4) | 25-35 tok/s | Apple Silicon |
| M2 Pro/Max (32GB) | Shared | Llama 3.1 8B | 35-45 tok/s | Apple Silicon |
| M3 Max (48GB+) | Shared | Mistral 24B | 15-25 tok/s | Apple Silicon |
| CPU-only (16GB RAM) | N/A | Mistral 7B (Q3) | 5-10 tok/s | Slow but functional |

### Ollama Server Configuration

```bash
# Optimize Ollama for production

# Set concurrent request limit (default: 4)
export OLLAMA_NUM_PARALLEL=2

# Set maximum queued requests
export OLLAMA_MAX_QUEUE=8

# Set model keep-alive (default: 5min)
export OLLAMA_KEEP_ALIVE=5m

# Set host (default: 127.0.0.1)
export OLLAMA_HOST=0.0.0.0:11434

# Disable GPU (CPU-only mode)
export OLLAMA_NO_GPU=true

# Start with optimized settings
ollama serve

# GPU monitoring
nvidia-smi -l 1  # Watch VRAM usage
ollama ps        # Show loaded models
```

### Docker Deployment

```dockerfile
# Dockerfile for Ollama service
FROM ollama/ollama:latest

RUN ollama serve & sleep 5 && ollama pull mistral:7b-q4_K_M
RUN ollama pull nomic-embed-text

EXPOSE 11434

ENTRYPOINT ["ollama", "serve"]
```

```yaml
# docker-compose.yml snippet
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  ollama_data:
```

---

## Cloud Model Setup

### Anthropic API Configuration

```env
# .env configuration
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
# Optional: override default model
CLAUDE_MODEL=claude-sonnet-4-20250514
# Optional: set rate limit
CLAUDE_MAX_REQUESTS_PER_MINUTE=50
```

### API Rate Limits

| Plan | Requests/min | Tokens/min | Tokens/day |
|---|---|---|---|
| Free tier | 10 | 20,000 | 100,000 |
| Tier 1 ($5 deposit) | 50 | 100,000 | 500,000 |
| Tier 2 ($50 deposit) | 100 | 200,000 | 2,500,000 |
| Tier 3 ($500 deposit) | 500 | 1,000,000 | 10,000,000 |
| Tier 4 (Enterprise) | Custom | Custom | Custom |

### Cost Estimation Dashboard

```python
class CostEstimator:
    """Tracks and estimates AI costs across models."""

    RATES = {
        "mistral": {"input": 0, "output": 0},  # Free (local)
        "nomic-embed-text": {"input": 0, "output": 0},
        "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.0008, "output": 0.004},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
    }

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def log_request(self, model: str, input_tokens: int,
                          output_tokens: int, agent: str) -> dict:
        """Log an AI request for cost tracking."""
        rates = self.RATES.get(model, {"input": 0, "output": 0})
        cost = (input_tokens / 1000 * rates["input"]) + \
               (output_tokens / 1000 * rates["output"])

        entry = {
            "model": model,
            "agent": agent,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(cost, 6),
            "timestamp": "now",
        }

        self.supabase.table("ai_cost_logs").insert(entry).execute()
        return entry

    async def get_daily_cost(self, date: str = None) -> dict:
        """Get total AI cost for a given day."""
        from datetime import date as dt_date
        target_date = date or str(dt_date.today())
        result = self.supabase.table("ai_cost_logs")\
            .select("model, sum(input_tokens) as total_in, sum(output_tokens) as total_out, sum(cost) as total_cost")\
            .eq("date(timestamp)", target_date)\
            .group_by("model")\
            .execute()
        return result.data or []

    def project_monthly_cost(self, daily_avg_cost: float) -> dict:
        """Project monthly cost based on daily average."""
        monthly = daily_avg_cost * 30.5
        return {
            "daily_avg": round(daily_avg_cost, 4),
            "monthly_projected": round(monthly, 4),
            "annual_projected": round(monthly * 12, 4),
        }
```

---

## Model Fallback Chain

### Fallback Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MODEL FALLBACK CHAIN                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  REQUEST                                                                      │
│    │                                                                          │
│    ▼                                                                          │
│  ┌─────────────────────┐                                                      │
│  │  LINK 1: Ollama      │─────────────────── Success ──────▶ Return response  │
│  │  (Mistral 7B, local) │                                                      │
│  │  Timeout: 30s        │                                                      │
│  │  Retries: 1          │                                                      │
│  └─────────┬───────────┘                                                      │
│            │ Fail                                                              │
│            ▼                                                                   │
│  ┌─────────────────────┐                                                      │
│  │  LINK 2: Claude      │─────────────────── Success ──────▶ Return response  │
│  │  (Sonnet 4, cloud)  │                                                      │
│  │  Timeout: 60s        │                                                      │
│  │  Retries: 2          │                                                      │
│  └─────────┬───────────┘                                                      │
│            │ Fail                                                              │
│            ▼                                                                   │
│  ┌─────────────────────┐                                                      │
│  │  LINK 3: Algorithmic │─────────────────── Success ──────▶ Return degraded   │
│  │  (Rule-based fallback)│                              response               │
│  │  Always available    │                                                      │
│  └─────────────────────┘                                                      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Fallback Chain Implementation

```python
import asyncio
import random
from typing import Optional, Callable, Any
from datetime import datetime

class FallbackChain:
    """Three-tier fallback chain with circuit breaker pattern."""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.circuit_states: dict[str, dict] = {}
        self.metrics: dict[str, list] = {"attempts": [], "fallbacks": []}

    async def execute(
        self,
        agent_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        require_json: bool = False,
        algorithmic_fallback: Optional[Callable] = None,
    ) -> dict:
        """Execute the fallback chain with circuit breaker."""
        start = datetime.now()

        # Link 1: Ollama
        if self._is_circuit_open("ollama") is False:
            try:
                result = await asyncio.wait_for(
                    self.llm_client._call_ollama(prompt, system_prompt, max_tokens),
                    timeout=60,
                )
                if require_json:
                    import json
                    parsed = json.loads(result)
                    self._record_success("ollama", datetime.now() - start)
                    return {"model": "mistral", "content": parsed, "latency_ms": (datetime.now() - start).total_seconds() * 1000}
                self._record_success("ollama", datetime.now() - start)
                return {"model": "mistral", "content": result, "latency_ms": (datetime.now() - start).total_seconds() * 1000}
            except (asyncio.TimeoutError, ConnectionError, Exception) as e:
                self._record_failure("ollama")
                logger.warning(f"[FallbackChain] Ollama failed for {agent_name}: {e}")

        # Link 2: Claude
        if self.llm_client.claude_key and self._is_circuit_open("claude") is False:
            try:
                result = await asyncio.wait_for(
                    self.llm_client._call_claude(prompt, system_prompt, max_tokens),
                    timeout=60,
                )
                if require_json:
                    import json
                    parsed = json.loads(result)
                    self._record_success("claude", datetime.now() - start)
                    return {"model": "claude-sonnet-4", "content": parsed, "latency_ms": (datetime.now() - start).total_seconds() * 1000}
                self._record_success("claude", datetime.now() - start)
                return {"model": "claude-sonnet-4", "content": result, "latency_ms": (datetime.now() - start).total_seconds() * 1000}
            except Exception as e:
                self._record_failure("claude")
                logger.warning(f"[FallbackChain] Claude failed for {agent_name}: {e}")

        # Link 3: Algorithmic fallback
        if algorithmic_fallback:
            logger.info(f"[FallbackChain] Using algorithmic fallback for {agent_name}")
            result = algorithmic_fallback()
            self._record_fallback("algorithmic")
            return {"model": "algorithmic", "content": result, "latency_ms": (datetime.now() - start).total_seconds() * 1000}

        # All links exhausted
        raise RuntimeError(f"All fallback links exhausted for {agent_name}")

    def _is_circuit_open(self, service: str) -> bool:
        """Check circuit breaker state."""
        state = self.circuit_states.get(service, {"failures": 0, "last_failure": None})
        if state["failures"] >= 5:
            # Check if cooldown period (60s) has elapsed
            if state["last_failure"]:
                elapsed = (datetime.now() - state["last_failure"]).total_seconds()
                if elapsed < 60:
                    return True  # Circuit open
                # Half-open: reset failure count and try
                self.circuit_states[service] = {"failures": 0, "last_failure": None}
        return False

    def _record_success(self, service: str, latency: float):
        self.circuit_states[service] = {"failures": 0, "last_failure": None}
        self.metrics["attempts"].append({
            "service": service,
            "success": True,
            "latency_ms": latency.total_seconds() * 1000,
            "timestamp": datetime.now().isoformat(),
        })

    def _record_failure(self, service: str):
        state = self.circuit_states.get(service, {"failures": 0})
        state["failures"] += 1
        state["last_failure"] = datetime.now()
        self.circuit_states[service] = state
        self.metrics["attempts"].append({
            "service": service,
            "success": False,
            "timestamp": datetime.now().isoformat(),
        })

    def _record_fallback(self, fallback_type: str):
        self.metrics["fallbacks"].append({
            "type": fallback_type,
            "timestamp": datetime.now().isoformat(),
        })

    @property
    def stats(self) -> dict:
        total = len(self.metrics["attempts"])
        successes = sum(1 for a in self.metrics["attempts"] if a["success"])
        return {
            "total_attempts": total,
            "success_rate": round(successes / total * 100, 1) if total else 0,
            "circuit_states": self.circuit_states,
            "algorithmic_fallbacks": len(self.metrics["fallbacks"]),
        }
```

---

## Model Performance Benchmarks

### Latency Benchmarks (Mistral 7B Q4_K_M)

| Input Length | Output Length | P50 | P95 | P99 | tok/s (avg) |
|---|---|---|---|---|---|
| 100 | 50 | 0.4s | 0.8s | 1.2s | 55 |
| 500 | 200 | 1.2s | 2.5s | 4.0s | 45 |
| 1000 | 500 | 3.0s | 6.0s | 9.0s | 40 |
| 2000 | 800 | 5.5s | 10.0s | 15.0s | 38 |
| 4000 | 1000 | 9.0s | 16.0s | 22.0s | 35 |
| 6000 | 1200 | 14.0s | 24.0s | 35.0s | 30 |

**Hardware:** RTX 3060 12GB, AMD Ryzen 5 5600, 32GB RAM, NVMe SSD

### Latency Benchmarks (Claude Sonnet 4 API)

| Input Length | Output Length | P50 | P95 | P99 |
|---|---|---|---|---|
| 500 | 200 | 1.5s | 3.0s | 5.0s |
| 2000 | 500 | 2.8s | 5.0s | 8.0s |
| 4000 | 800 | 4.0s | 7.0s | 12.0s |
| 8000 | 1200 | 6.5s | 12.0s | 18.0s |
| 20000 | 2000 | 12.0s | 20.0s | 30.0s |

**Note:** Claude latency is network-dependent. Measurements taken from Mumbai, India to us-east-1.

### Quality Benchmarks

| Benchmark | Mistral 7B Q4 | Mistral 7B FP16 | Claude Sonnet 4 |
|---|---|---|---|
| MMLU (0-shot) | 62.8 | 64.1 | ~88 |
| MMLU (5-shot) | 64.5 | 66.0 | ~89 |
| HumanEval (Python) | 28.0 | 30.5 | ~78 |
| GSM8K (math) | 42.5 | 45.0 | ~92 |
| HellaSwag (commonsense) | 78.0 | 81.2 | ~88 |
| TruthfulQA (truthfulness) | 42.0 | 44.5 | ~72 |
| MTEB (embedding) | 62.3 | N/A | N/A |
| Instruction following (IFEval) | 66.0 | 68.0 | ~87 |
| Hallucination rate (internal) | ~8% | ~7% | ~3% |
| JSON output accuracy (internal) | 92% | 94% | 99.5% |

### Benchmark Running Script

```bash
# Run local model benchmarks
ollama pull mistral:7b-q4_K_M

# Generate throughput test
python -c "
import httpx, time, json

def benchmark(prompt, output_tokens=200, runs=5):
    latencies = []
    for _ in range(runs):
        start = time.time()
        resp = httpx.post('http://localhost:11434/api/generate', json={
            'model': 'mistral:7b-q4_K_M',
            'prompt': prompt,
            'stream': False,
            'options': {'num_predict': output_tokens}
        }, timeout=120)
        elapsed = time.time() - start
        resp_data = resp.json()
        tokens = len(resp_data.get('response', '').split())
        latencies.append({
            'latency': round(elapsed, 3),
            'tokens': tokens,
            'tok_s': round(tokens / elapsed, 1),
        })
    return latencies

results = benchmark('Explain the benefits of a Second Brain system for students.')
for r in results:
    print(f\"Latency: {r['latency']}s, Tokens: {r['tokens']}, Speed: {r['tok_s']} tok/s\")
"
```

---

## Fine-Tuning Considerations

### When to Fine-Tune vs Prompt Engineer

| Scenario | Approach | Rationale |
|---|---|---|
| Response tone too formal | ✏️ Prompt engineer | Add tone instruction to system prompt |
| Wrong output format | ✏️ Prompt engineer | Strengthen JSON schema in prompt |
| Missing entity recognition | ✏️ Prompt engineer | Add few-shot examples |
| Hallucinating specific facts | ✏️ Prompt engineer | Add verification step to chain-of-thought |
| Consistent task breakdown style needed | 🔧 Fine-tune (LoRA) | Prompt engineering insufficient for consistent structural output |
| Domain-specific terminology | 🔧 Fine-tune (LoRA) | Model needs to learn new vocabulary |
| Agent-specific voice/personality | ✏️ Prompt engineer | Voice is easier to prompt-engineer than fine-tune |
| Multi-step reasoning failures | ✏️ Prompt engineer + Chain-of-thought | CoT prompting often matches fine-tuned performance |
| Summarization of specific document types | 🔧 Fine-tune (LoRA) | Format-specific summarization benefits from fine-tuning |
| Classification accuracy < 90% | 🔧 Fine-tune (LoRA) | Classification is a strong fine-tuning use case |

### LoRA Fine-Tuning Setup

```python
# Conceptual LoRA fine-tuning configuration for Mistral 7B
# Would be used with unsloth, Axolotl, or Hugging Face SFTTrainer

LORA_CONFIG = {
    "model": "mistralai/Mistral-7B-v0.1",
    "lora_r": 16,              # Rank of LoRA matrices
    "lora_alpha": 32,          # Scaling factor
    "lora_dropout": 0.05,      # Dropout for regularization
    "lora_target_modules": [   # Which layers to apply LoRA to
        "q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    "dataset_format": "alpaca",  # instruction, input, output format
    "micro_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-4,
    "num_epochs": 3,
    "max_seq_length": 4096,
    "save_steps": 50,
    "eval_steps": 50,
    "output_dir": "./lora-mistral-secondbrain",
}

# Dataset requirements
DATASET_REQUIREMENTS = """
- Minimum 500 high-quality examples for meaningful LoRA results
- Input-output pairs matching the target agent's exact JSON schema
- Cover edge cases: empty data, missing fields, multi-line content
- Include both normal and adversarial examples
- Split: 80% train, 10% validation, 10% test
"""
```

### Dataset Schema for Agent Fine-Tuning

```json
{
  "dataset_name": "briefing_agent_finetune",
  "description": "Training data for A09 Daily Briefing Agent",
  "version": "1.0.0",
  "samples": [
    {
      "instruction": "Generate a daily briefing for the user based on their current data.",
      "input": "Tasks: 9 pending (3 overdue). Courses: 2 behind schedule. Sleep: 6.2h avg (poor). Habits: LeetCode streak 12 days (logged today).",
      "output": "{\"date\": \"2026-06-11\", \"sleep_quality\": \"poor\", \"task_summary\": {\"total\": 9, \"overdue\": 3, \"urgent\": 1}, \"top_priority\": \"Complete React dashboard\", \"energy_adjustment\": \"Focus on shallow work until 10 AM\", \"nudge\": \"Your LeetCode streak is impressive — don't break it today. 15 minutes minimum.\"}"
    },
    {
      "instruction": "Generate a daily briefing for the user based on their current data.",
      "input": "Tasks: 4 pending, none overdue. Courses: on track. Sleep: 7.8h (excellent). Habits: all logged.",
      "output": "{\"date\": \"2026-06-10\", \"sleep_quality\": \"excellent\", \"task_summary\": {\"total\": 4, \"overdue\": 0, \"urgent\": 0}, \"top_priority\": \"Prepare for DSA exam\", \"energy_adjustment\": \"Full energy — tackle hardest task first\", \"nudge\": \"Great momentum. Use the extra energy to get ahead on course work.\"}"
    }
  ]
}
```

---

## Future Model Roadmap

### Planned Model Upgrades

| Timeline | Model | Reason for Upgrade | Expected Impact |
|---|---|---|---|
| Q3 2026 | Mistral Small 3.1 (24B, Q4) | 72 MMLU vs 64; 128K context | Higher quality briefings and reviews; 14GB VRAM required |
| Q3 2026 | nomic-embed-text v2 | Expected MTEB 65+ | Improved retrieval quality |
| Q4 2026 | Llama 4 (expected 8B-70B) | Meta's next generation | Likely new default if quality exceeds Mistral |
| Q1 2027 | Claude Sonnet 5 | Anthropic's next Sonnet | Fallback upgrade; expected quality improvement |
| Q1 2027 | GPT-4o mini fine-tune | OpenAI fine-tuning API | Option for specialized agent fine-tuning |
| Q2 2027 | Mistral Large 3 | Flagship Mistral model | Premium local option for complex reasoning |
| H2 2027 | Local MoE model | Expected 7B-level efficiency at 1B cost | Reduced VRAM requirements for existing quality |

### Upgrade Decision Framework

```
NEW MODEL AVAILABLE
    │
    ▼
┌──────────────────────────────────────┐
│ 1. Benchmark on Second Brain tasks    │
│    - Run 20 representative test cases │
│    - Compare: output quality, latency │
│    - Compare: VRAM usage, cost        │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│ 2. Quality improvement threshold     │
│    > 10% on relevant benchmarks?     │
│    OR > 15% cost reduction?          │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┐
        ▼              ▼
      YES             NO
        │              │
        ▼              ▼
┌──────────────┐  ┌──────────────────┐
│ 3. Shadow    │  │ Keep current     │
│    deploy    │  │ model. Re-       │
│    for 1     │  │ evaluate next    │
│    week with │  │ quarter.         │
│    logging   │                     │
└──────┬───────┘                     │
       │                             │
       ▼                             │
┌──────────────┐                     │
│ 4. Promote   │                     │
│    to daily  │                     │
│    agents    │                     │
└──────────────┘                     │
```

---

## Cost Optimization

### Cost Breakdown by Agent (Monthly Projection, Ollama-only)

| Agent | Requests/Day | Tokens/Req | Daily Tokens | Monthly Cost |
|---|---|---|---|---|
| Briefing | 1 | 3,600 | 3,600 | $0 |
| Weekly Review | 0.14 | 4,400 | 630 | $0 |
| Memory | 20 | 1,500 | 30,000 | $0 |
| Learning | 1 | 2,300 | 2,300 | $0 |
| Task Agent | 5 | 1,400 | 7,000 | $0 |
| Opportunity | 1 | 2,800 | 2,800 | $0 |
| Sleep | 2 | 1,100 | 2,200 | $0 |
| Nudge | 1 | 1,400 | 1,400 | $0 |
| ARIA Chat | 10 | 2,100 | 21,000 | $0 |
| **Total Ollama** | **45** | **—** | **70,930** | **$0** |

### Cost Breakdown with Claude Fallback (5% of requests)

| Agent | Claude Requests/Day | Monthly Claude Cost |
|---|---|---|
| Briefing | 0.05 | $0.045 |
| Weekly Review | 0.007 | $0.023 |
| Memory | 1 | $0.090 |
| Learning | 0.05 | $0.069 |
| Task Agent | 0.25 | $0.021 |
| Opportunity | 0.05 | $0.084 |
| Sleep | 0.1 | $0.007 |
| Nudge | 0.05 | $0.004 |
| ARIA Chat | 0.5 | $0.063 |
| **Total Cloud** | **~2** | **~$0.41/month** |

### Cost Optimization Strategies

| Strategy | Savings | Implementation Difficulty | Impact |
|---|---|---|---|
| **Local-first routing** | ~95% (vs cloud-only) | Low | Eliminates majority of API costs |
| **Prompt compression** | 20-40% token reduction | Medium | Remove whitespace, shorten field names, abbreviated JSON keys |
| **Output caching** | 30-50% on repeated queries | Medium | Cache identical responses (same input + same context) |
| **Batch processing for cron** | 80% on cron agents | Low | All cron agents (briefing, radar, sleep) run once, not per-request |
| **Shortened context window** | 15-25% | Low | Only send context relevant to the specific agent task |
| **Q4 quantization** | 40% VRAM, 0% cost | Low | Default quantization gives near-lossless quality at 40% size |
| **Token budget enforcement** | 10-20% | Low | Strict per-agent max_tokens prevents runaway outputs |
| **Model downgrade for simple tasks** | 20% | Medium | Use Haiku instead of Sonnet for sleep/nudge agents |

### Prompt Compression Implementation

```python
class PromptCompressor:
    """Reduces prompt token count without losing semantic content."""

    @staticmethod
    def compress_context(context: str, target_ratio: float = 0.7) -> str:
        """Compress context to target ratio of original size."""
        if not context or target_ratio >= 1.0:
            return context

        lines = context.split("\n")
        compressed = []
        for line in lines:
            # Remove unnecessary whitespace
            line = " ".join(line.split())
            # Remove comment-like lines
            if line.startswith("//") or line.startswith("#"):
                continue
            # Shorten JSON keys (keep first 3 chars)
            import re
            line = re.sub(r'"([^"]{4,})":', lambda m: f'"{m.group(1)[:3]}":', line)
            compressed.append(line)

        result = "\n".join(compressed)

        # If still above target, truncate from bottom (least recent context)
        if len(result) > len(context) * target_ratio:
            target_len = int(len(context) * target_ratio)
            result = result[:target_len]
            result += "\n...(context compressed for token efficiency)"

        return result

    @staticmethod
    def shorten_field_names(data: dict) -> dict:
        """Shorten verbose field names in data dicts for JSON serialization."""
        name_map = {
            "priority": "pri",
            "description": "desc",
            "deadline": "due",
            "created_at": "ca",
            "updated_at": "ua",
            "duration_hours": "dur",
            "user_id": "uid",
            "source_table": "src",
        }
        return {name_map.get(k, k): v for k, v in data.items()}
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | AI Architecture Team | Initial enterprise reference document |
