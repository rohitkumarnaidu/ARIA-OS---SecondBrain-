# Ollama Integration

## Document Control

| Field | Value |
|---|---|
| Document ID | INT-OLL-007 |
| Version | 1.0.0 |
| Status | Approved |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Integration Overview](#2-integration-overview)
3. [API Configuration](#3-api-configuration)
4. [Supported Models](#4-supported-models)
5. [Architecture Diagram](#5-architecture-diagram)
6. [Request/Response Format](#6-requestresponse-format)
7. [Use Cases by Agent](#7-use-cases-by-agent)
8. [Cost Analysis](#8-cost-analysis)
9. [Circuit Breaker Integration](#9-circuit-breaker-integration)
10. [Fallback Chain Position](#10-fallback-chain-position)
11. [Installation & Setup](#11-installation--setup)
12. [Error Handling](#12-error-handling)
13. [Security Considerations](#13-security-considerations)
14. [Monitoring & Observability](#14-monitoring--observability)
15. [Resource Requirements](#15-resource-requirements)
16. [Testing Strategy](#16-testing-strategy)
17. [Edge Cases](#17-edge-cases)
18. [Failure Scenarios](#18-failure-scenarios)
19. [Configuration Reference](#19-configuration-reference)
20. [References](#20-references)

---

## 1. Executive Summary

Ollama is the **default AI provider** for Second Brain OS, running locally on the developer's machine. It provides free, private, offline-capable LLM inference for all agent tasks. No data ever leaves the machine when Ollama is the active provider. It handles the majority of AI requests including ARIA chat, video summarization, resource tagging, and habit reporting.

---

## 2. Integration Overview

| Property | Value |
|---|---|
| Provider | Ollama (local) |
| API Endpoint | `http://localhost:11434/api/generate` |
| Auth Method | None (localhost only) |
| Default Model | `mistral:7b` |
| Protocol | HTTP POST (JSON) |
| SDK | `httpx` (direct REST) |
| Cost | Free (local hardware) |
| Status | **Primary (default) AI provider** |

---

## 3. API Configuration

```python
import httpx
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
```

---

## 4. Supported Models

| Model | Parameters | RAM Required | Use Case |
|---|---|---|---|
| `mistral:7b` | 7B | 8 GB | **Default** — general chat, summarization |
| `llama3.1:8b` | 8B | 8 GB | Alternative — better reasoning |
| `llama3.2:3b` | 3B | 4 GB | Fast responses, lightweight tasks |
| `nomic-embed-text` | 137M | 1 GB | Text embeddings |
| `phi3:mini` | 3.8B | 4 GB | Quick structured output |

---

## 5. Architecture Diagram

```mermaid
graph TD
    subgraph Machine["Developer Machine"]
        App["Second Brain OS<br/>FastAPI Backend"]
        Ollama["Ollama Service<br/>localhost:11434"]
        Models["Model Storage<br/>~4 GB per model"]
    end

    subgraph Agents["Agent Modules"]
        A01["Planner Agent"]
        A09["Daily Briefing"]
        A02["Memory Agent"]
        A03["Learning Agent"]
        A13["Sleep Agent"]
        A14["Nudge Agent"]
    end

    App -->|HTTP POST /api/generate| Ollama
    Ollama -->|Load/Infer| Models
    Agents -->|generate() / generate_json()| App

    style Ollama fill:#1A1D24,stroke:#00FFA3,color:#F1F5F9
    style Models fill:#1A1D24,stroke:#94A3B8,color:#F1F5F9
```

---

## 6. Request/Response Format

### Request

```json
{
  "model": "mistral:7b",
  "prompt": "Generate a daily briefing based on my tasks.",
  "system": "You are ARIA, the AI core of Second Brain OS.",
  "stream": false,
  "options": {
    "temperature": 0.5,
    "num_predict": 4096,
    "top_p": 0.9
  }
}
```

### Response

```json
{
  "model": "mistral:7b",
  "created_at": "2026-07-10T06:00:00Z",
  "response": "Good morning! Here is your daily briefing...",
  "done": true,
  "context": [123, 456, 789],
  "total_duration": 2345678900,
  "load_duration": 123456789,
  "prompt_eval_count": 850,
  "eval_count": 320,
  "eval_duration": 2200000000
}
```

---

## 7. Use Cases by Agent

| Agent | Model | Frequency | Priority |
|---|---|---|---|
| A01 — Planner | `mistral:7b` | On-demand | High |
| A02 — Memory | `mistral:7b` | Per chat | High |
| A03 — Learning | `llama3.1:8b` | Daily | Medium |
| A09 — Daily Briefing | `mistral:7b` | Daily (7 AM) | High |
| A13 — Sleep | `mistral:7b` | Daily (9:30 PM) | Low |
| A14 — Nudge | `mistral:7b` | Daily (6 PM) | Medium |
| Resource tagging | `mistral:7b` | On-demand | Low |
| Video summaries | `llama3.1:8b` | On-demand | Low |

---

## 8. Cost Analysis

| Expense | Value |
|---|---|
| Token cost | $0.00 (local hardware) |
| RAM cost | 8-16 GB dedicated |
| Storage cost | ~4 GB per model |
| Power cost | ~$5-10/month (electricity) |
| **Total** | **$5-10/month (hardware only)** |

No API costs — all inference runs on local hardware.

---

## 9. Circuit Breaker Integration

```python
self.ollama_circuit = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=(httpx.RequestError, httpx.TimeoutException),
)
```

**States:**
- **CLOSED**: Normal operation — requests pass through
- **OPEN**: After 5 consecutive failures — all requests rejected for 60s
- **HALF_OPEN**: After 60s cooldown — single test request allowed
  - Success → CLOSED (resume normal)
  - Failure → OPEN (another 60s cooldown)

---

## 10. Fallback Chain Position

Ollama is the **first position** in the provider chain:

| Position | Provider | Condition | Circuit Breaker | Timeout |
|---|---|---|---|---|
| **1** | **Ollama** | **`USE_LOCAL_AI=True`** | **5 failures → 60s** | **60s** |
| 2 | Claude | `CLAUDE_API_KEY` set | 3 failures → 120s | 120s |
| 3 | OpenAI/Gemini | API key set | 3 failures → 60s | 60s |
| 4 | Raise error | All exhausted | — | — |

---

## 11. Installation & Setup

### Windows

```powershell
# Download from https://ollama.com/download/windows
# Run installer — adds Ollama to PATH

# Start service
ollama serve

# Pull default model
ollama pull mistral:7b

# Pull embedding model
ollama pull nomic-embed-text

# Verify
ollama list
# → mistral:7b, nomic-embed-text
```

### macOS / Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull mistral:7b
```

---

## 12. Error Handling

| Error | Cause | Action |
|---|---|---|
| Connection refused | Ollama not running | Start `ollama serve` |
| Model not found | Model not pulled | `ollama pull mistral:7b` |
| Timeout (>60s) | Model loading or slow inference | Increase timeout or use smaller model |
| Out of memory | Insufficient RAM | Use 3B or 7B model instead of 13B+ |
| GPU not available | Fallback to CPU | Slower but functional |

---

## 13. Security Considerations

- Ollama runs on localhost only — not exposed to network by default
- No authentication required (localhost-only)
- All data stays on local machine — no privacy risk
- No API keys or secrets involved
- Can be air-gapped (no internet connection needed)

---

## 14. Monitoring & Observability

| Metric | Source | Action |
|---|---|---|
| Response time | Client timing | Alert if > 30s |
| Model load time | Response metadata | Monitor after restart |
| Error rate | Client logs | > 10% → fallback to Claude |
| Circuit breaker state | Health endpoint | OPEN → investigate Ollama |
| RAM usage | System monitor | > 80% → use smaller model |

---

## 15. Resource Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Storage | 4 GB per model | 8 GB (2 models) |
| CPU | 4 cores | 8 cores |
| GPU | Optional | NVIDIA 6GB+ VRAM |
| Network | None (localhost) | Internet for model download |

---

## 16. Testing Strategy

| Test Type | Scope |
|---|---|
| Unit | Request formatting, response parsing |
| Mock | Ollama responses for agent testing |
| Integration | Full fallback chain (Ollama → Claude) |
| Circuit breaker | State transitions (closed → open → half-open → closed) |

---

## 17. Edge Cases

- First request after startup is slow (model loading) → Warm-up call on app start
- GPU unavailable → Auto-detect and fall back to CPU mode
- Multiple concurrent requests → Ollama queues requests by default; configure `OLLAMA_NUM_PARALLEL` for concurrent handling
- Model unloading → `ollama stop mistral:7b` to free RAM; auto-loaded on next request

---

## 18. Failure Scenarios

| Scenario | Impact | Mitigation |
|---|---|---|
| Ollama not installed | No local AI | Error message with install instructions |
| Insufficient RAM | Model fails to load | Auto-detect and use smaller model |
| Model deleted | Request fails | Auto-pull on missing model error |
| Service crash | All AI features down | Fallback to Claude API |
| GPU memory exhausted | Model crashes | Fall back to CPU-only mode |

---

## 19. Configuration Reference

```env
USE_LOCAL_AI=True
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b
OLLAMA_TIMEOUT=60
```

Ollama-specific settings:
```bash
# Set number of parallel requests (default: 1)
$env:OLLAMA_NUM_PARALLEL = "2"

# Set max loaded models (default: 1)
$env:OLLAMA_MAX_LOADED_MODELS = "2"

# Enable debug logging
$env:OLLAMA_DEBUG = "1"
```

---

## 20. References

| Resource | URL |
|---|---|
| Ollama GitHub | https://github.com/ollama/ollama |
| Ollama API Docs | https://github.com/ollama/ollama/blob/main/docs/api.md |
| Ollama Model Library | https://ollama.com/library |
| Integration Architecture | `docs/engineering/37_IntegrationArchitecture.md` |
| LLM Client | `packages/ai/client.py` |
