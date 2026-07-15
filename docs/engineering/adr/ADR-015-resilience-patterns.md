## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-ADR15-001 |
| Version | 1.0.0 |
| Status | Accepted |
| Last Updated | 2026-07-11 |

# ADR-015: Resilience Patterns

## Document Control

| Field | Value |
|---|---|
| ADR Number | 015 |
| Status | Accepted |
| Date | 2026-07-10 |
| Deciders | Developer |
| Replaces | None |
| Superseded By | None |
| Category | System Architecture |

---

## 1. Title

Resilience Patterns â€” Circuit Breakers, Retries, and Timeouts for AI-First Architecture

---

## 2. Context

Second Brain OS depends on multiple external services (AI providers, Supabase, notification services) that can fail in unpredictable ways. The system must remain operational despite these failures.

**Failure modes to handle:**
- **AI provider**: Service down, rate limited, slow response, garbage output
- **Database**: Connection timeout, query timeout, rate limited
- **Network**: Packet loss, high latency, DNS failure
- **Third-party API**: HTTP errors, quota exhausted

---

## 3. Decision

Implement **four resilience patterns** consistently across all external service calls:

| Pattern | Purpose | Applied to |
|---|---|---|
| **Timeouts** | Prevent unbounded waits | Every external call |
| **Retries with Backoff** | Recover from transient failures | AI, DB, Network |
| **Circuit Breakers** | Fail fast, prevent cascading | AI providers |
| **Fallbacks** | Graceful degradation | All features |

---

## 4. Detailed Design

### 4.1 Timeout Configuration

| Service | Timeout | Rationale |
|---|---|---|
| AI Provider (any) | 30s | LLM generation can be slow |
| Supabase query | 10s | Should complete quickly |
| HTTP notification | 5s | Push/email should be fast |
| Health checks | 3s | Must be quick |
| Internal computation | 30s | Complex algorithmic fallback |

```python
# packages/shared/utils/timeout.py
import asyncio

DEFAULT_TIMEOUTS = {
    "ai": 30,
    "database": 10,
    "notification": 5,
    "health": 3,
    "internal": 30,
}

async def with_timeout(coro, service: str = "internal"):
    """Execute coroutine with service-appropriate timeout."""
    timeout = DEFAULT_TIMEOUTS.get(service, 10)
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Timeout after {timeout}s for {service}")
        raise
```

### 4.2 Retry with Exponential Backoff

```python
# packages/shared/utils/retry.py
import asyncio
import random

async def retry_with_backoff(
    fn,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
):
    """
    Retry a function with exponential backoff and jitter.
    
    Retry schedule: 2s, 4s, 8s (with Â±25% jitter)
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await fn()
        except RetryableError as e:
            last_exception = e
            
            if attempt < max_retries:
                delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                if jitter:
                    delay *= 1 + random.uniform(-0.25, 0.25)
                
                logger.info(
                    f"Retry attempt {attempt + 1}/{max_retries} "
                    f"after {delay:.1f}s. Error: {e}"
                )
                await asyncio.sleep(delay)
    
    raise last_exception
```

### 4.3 Circuit Breaker

```python
# packages/shared/utils/circuit_breaker.py
import time
import asyncio
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker with configurable threshold and cooldown.
    
    CLOSED â†’ OPEN: After `failure_threshold` consecutive failures
    OPEN â†’ HALF_OPEN: After `cooldown` seconds
    HALF_OPEN â†’ CLOSED: Single successful request
    HALF_OPEN â†’ OPEN: Single failed request
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        cooldown: float = 60.0,
        half_open_max_requests: int = 1,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.half_open_max_requests = half_open_max_requests
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0
        self._half_open_requests = 0
    
    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.cooldown:
                self._state = CircuitState.HALF_OPEN
                self._half_open_requests = 0
                logger.info(f"CB {self.name}: OPEN â†’ HALF_OPEN")
        return self._state
    
    async def call(self, fn, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(f"CB {self.name} is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            if self._half_open_requests >= self.half_open_max_requests:
                raise CircuitBreakerOpenError(
                    f"CB {self.name} HALF_OPEN: max test requests reached"
                )
            self._half_open_requests += 1
        
        try:
            result = await fn(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise
    
    def _record_success(self):
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            logger.info(f"CB {self.name}: HALF_OPEN â†’ CLOSED (recovered)")
    
    def _record_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(f"CB {self.name}: HALF_OPEN â†’ OPEN (test failed)")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                f"CB {self.name}: CLOSED â†’ OPEN "
                f"({self._failure_count} failures)"
            )
```

### 4.4 Combining Patterns

```python
# packages/ai/client.py

async def generate_json(self, prompt: str, system: str = "") -> dict:
    """Generate JSON with full resilience stack."""
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def call_provider(provider):
        return await with_timeout(
            provider.generate(prompt, system),
            service="ai"
        )
    
    for provider in self.providers:
        try:
            return await provider.circuit_breaker.call(
                call_provider, provider
            )
        except (CircuitBreakerOpenError, TimeoutError, ProviderError) as e:
            logger.warning(f"Provider {provider.name} failed: {e}")
            continue
    
    # All providers exhausted â†’ fallback
    return self.fallback.generate(prompt)
```

---

## 5. Alternatives Considered

### Alternative 1: Synchronous-Only, No Resilience

**Approach:** Block on every external call, no retry, no circuit breaker.

**Pros:** Simple, no async complexity
**Cons:** Blocks entire process on failure, no recovery
**Decision:** Rejected â€” unacceptable for AI-first architecture

### Alternative 2: Unlimited Retries

**Approach:** Keep retrying until success.

**Pros:** Eventual consistency
**Cons:** Can retry forever on permanent failure, resource exhaustion
**Decision:** Rejected â€” bounded retries with backoff

### Alternative 3: Third-Party Resilience Library (e.g., resilience4j, tenacity)

**Approach:** Use established resilience library.

**Pros:** Battle-tested, feature-rich
**Cons:** Another dependency, configuration overhead
**Decision:** Accepted for `tenacity` (Python) for retry logic; custom circuit breaker for simplicity

---

## 6. Consequences

### Positive

| Benefit | Description |
|---|---|
| **Self-healing** | System recovers from transient failures automatically |
| **Fail-fast** | Circuit breakers prevent wasted time on failing services |
| **Predictable latency** | Timeouts bound worst-case response time |
| **Observability** | Every pattern logs state transitions |
| **Single-user resilience** | System never shows error screen to user |

### Negative

| Cost | Mitigation |
|---|---|
| **Code complexity** | ~200 lines for resilience primitives |
| **Async everywhere** | All external calls must be async |
| **Debugging complexity** | Retries mask transient issues |
| **Resource usage** | Retry queue + circuit breaker state |

---

## 7. Performance Targets

| Pattern | Overhead | Benefit |
|---|---|---|
| Timeout | 0ms (check only) | Bounds latency |
| Retry backoff | ~14s max (2s+4s+8s) | Recovers 90%+ transient failures |
| Circuit breaker | < 1ms per call | Prevents cascading failures |
| Fallback | < 100ms | Never shows error |

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Retry storm (all services retry simultaneously) | Low | Medium | Jitter, staggered retry groups |
| Circuit breaker never recovers | Low | Medium | Manual reset endpoint |
| Timeout too short for legitimate slow operation | Medium | Low | Configurable per service type |
| Memory leak from retry queue | Low | Low | Bounded retry count |

---

## 9. Related Decisions

| ADR | Relation |
|---|---|
| ADR-010: AI Provider Failover | Uses circuit breaker pattern |
| ADR-011: Graceful Degradation | Fallback after resilience patterns |
| ADR-006: Error Handling | Error types for retryable vs non-retryable |

---

## 10. References

| Reference | Link |
|---|---|
| Implementation | `packages/shared/utils/retry.py` |
| Implementation | `packages/shared/utils/circuit_breaker.py` |
| Implementation | `packages/shared/utils/timeout.py` |
| Tests | `tests/test_llm_client.py` (51 tests â€” CB + retry) |
| Microsoft Resilience Pattern | https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker |
