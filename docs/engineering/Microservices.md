# Microservices Architecture

## Document Control

| Metadata | Value |
|---|---|
| **Document ID** | ENG-ARCH-004 |
| **Status** | Draft |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-06-11 |
| **Author** | ARIA OS Engineering |
| **Approval** | Pending |
| **ADR References** | ADR-004 (Monolith First), ADR-007 (Microservices Migration Path) |

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the target microservices architecture for Second Brain OS (ARIA OS), establishes service boundaries, communication patterns, and provides a migration strategy from the current monolithic deployment.

### 1.2 Scope

Covers service decomposition, inter-service communication, API gateway design, data management strategies, infrastructure considerations, and the incremental migration path. Excludes implementation details of individual services, which are documented in their respective service specifications.

### 1.3 Current State

Second Brain OS is currently deployed as a monolithic architecture per ADR-004 (Monolith First):

- **Frontend**: Next.js 14 monolith serving the full React SPA
- **Backend**: Single FastAPI application handling all HTTP routes (`apps/api/`)
- **Scheduler**: Separate APScheduler process (`services/scheduler/`)
- **Agents**: In-process agent modules within the FastAPI application (`packages/ai/agents/`)
- **Database**: Single Supabase PostgreSQL instance shared across all modules
- **Authentication**: Supabase Auth integrated directly into the FastAPI app

The monolith serves the project well at current scale (single user, alpha stage). However, as the system grows to support multi-user, multi-tenant workloads with AI-powered background processing, the architecture must evolve toward microservices.

---

## 2. Microservices vs Monolith Analysis

| Criteria | Monolith (Current) | Microservices (Target) |
|---|---|---|
| **Deployment** | Single deployable unit | Independent deployable services |
| **Scalability** | Vertical only; entire app scales together | Horizontal per-service; high-demand services (AI, Search) scale independently |
| **Development Speed** | Fast initial velocity; slows as codebase grows | Slower initial setup; sustained velocity with clear boundaries |
| **Team Structure** | Single team | Multiple focused teams (or one team with clear ownership) |
| **Testability** | End-to-end tests cover everything; slow CI | Unit + contract tests per service; faster, isolated pipelines |
| **Fault Isolation** | One crash = full outage | Service failure isolated to that service |
| **Database** | Single shared schema | Database-per-service or bounded schemas |
| **Technology Lock-in** | Tied to FastAPI + Supabase | Each service can use optimal technology |
| **Operational Complexity** | Low (single process, single deploy) | High (service mesh, discovery, monitoring, orchestration) |
| **AI Agent Integration** | In-process agents block the event loop | Dedicated AI service with async processing, GPU scheduling |
| **Data Consistency** | Strong consistency via transactions | Eventual consistency; saga patterns required |
| **Overhead** | Minimal | Network calls, serialization, observability infrastructure |
| **Recommendation** | Correct for alpha/single-user | Target for production multi-user deployment |

### 2.1 Decision

**Stay monolith for alpha (current).** Migrate to microservices when:
1. Multi-user support requires isolated scaling
2. AI processing volume exceeds single-process capacity
3. Team size grows beyond 3-4 developers
4. Deployment frequency requires independent service releases

---

## 3. Service Decomposition Candidates

### 3.1 Identified Services

| Service | Responsibility | Dependencies | Data Store | Priority |
|---|---|---|---|---|
| **API Gateway** | Routing, auth, rate limiting, request aggregation | Auth Service | Stateless | High |
| **Auth Service** | Authentication, authorization, session management, API key management | Supabase Auth, Redis | Supabase Auth, Redis sessions | Critical |
| **Core CRUD Service** | Tasks, courses, goals, ideas, projects, resources, income, habits, sleep, time entries | Auth Service | Supabase PostgreSQL | Critical |
| **AI Service** | Agent execution, LLM inference, embedding generation, RAG pipeline | Auth Service, pgvector | PostgreSQL (pgvector), Redis | High |
| **Scheduler Service** | Cron jobs, reminder dispatch, habit resets, periodic AI tasks | Auth Service, Core CRUD | PostgreSQL (scheduler DB) | High |
| **Notification Service** | In-app, email, push, SMS delivery; template rendering; preference management | Auth Service, Redis | PostgreSQL, Redis | Medium |
| **Search Service** | Full-text search indexing, semantic search, reindex triggers | Core CRUD, pgvector | Meilisearch/Elasticsearch + pgvector | Medium |

### 3.2 Service Boundaries

Each service owns its data and exposes a well-defined API. Cross-service data access is strictly via API calls or events — never via direct database access.

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Next.js FE │────▶│ API Gateway  │────▶│   Auth Service   │
└─────────────┘     └──────┬───────┘     └──────────────────┘
                           │
              ┌────────────┼────────────┬──────────────┐
              ▼            ▼            ▼              ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
       │   Core   │ │    AI    │ │Scheduler │ │ Notification │
       │CRUD Svc  │ │ Service  │ │ Service  │ │   Service    │
       └──────────┘ └──────────┘ └──────────┘ └──────────────┘
              │                                    │
              ▼                                    ▼
       ┌──────────┐                        ┌──────────────┐
       │  Search  │                        │   Message    │
       │ Service  │                        │    Queue     │
       └──────────┘                        └──────────────┘
```

---

## 4. Communication Patterns

### 4.1 Synchronous Communication (REST)

Used for request-response workflows where immediate consistency is required.

| Pattern | Protocol | Use Case |
|---|---|---|
| RESTful HTTP | HTTP/1.1, HTTPS | CRUD operations, synchronous queries |
| JSON API | JSON over HTTP | Standardized resource responses (future) |
| OpenAPI Spec | YAML/JSON | Contract-first API documentation |

**Design Rules:**
- Services communicate only via the API Gateway for external requests
- Internal service-to-service calls may bypass the gateway but must authenticate via mutual TLS
- Timeout: 5 seconds for synchronous calls; 30 seconds for AI inference calls
- Circuit breakers at the client side for all inter-service HTTP calls

### 4.2 Asynchronous Communication (Events)

Used for eventual consistency, background processing, and cross-service notifications.

| Pattern | Technology | Use Case |
|---|---|---|
| Event Bus | Redis Pub/Sub (alpha), RabbitMQ (future) | Domain events: `task.created`, `habit.completed` |
| Message Queue | Redis Queue (alpha), Celery (future) | Background job dispatch |
| Change Data Capture | Supabase Realtime / PostgreSQL LISTEN/NOTIFY | Real-time UI updates |

**Event Catalog (Initial):**

| Event | Publisher | Consumers | Payload |
|---|---|---|---|
| `task.created` | Core CRUD | Search Service, Notification Service | `{ task_id, user_id, title, priority, due_date }` |
| `task.updated` | Core CRUD | Search Service (reindex) | `{ task_id, user_id, changes }` |
| `habit.completed` | Core CRUD | Scheduler Service, AI Service | `{ habit_id, user_id, streak_count }` |
| `reminder.due` | Scheduler Service | Notification Service | `{ user_id, reminder_id, channel }` |
| `user.registered` | Auth Service | Core CRUD, Notification Service | `{ user_id, email, preferences }` |
| `ai.analysis.ready` | AI Service | Notification Service | `{ user_id, analysis_type, summary }` |

### 4.3 gRPC (Future)

Consider gRPC for high-throughput internal service communication when:
- Latency requirements tighten (< 50ms P99)
- Streaming RPCs needed (e.g., AI streaming responses)
- Strong typing via protobuf provides additional safety

### 4.4 Message Queue Broker

**Alpha Phase:** In-process memory queue (for scheduler events) + Supabase Realtime (for UI events).

**Production Phase:** RabbitMQ or Redis Streams for:
- Durable event persistence
- At-least-once delivery guarantees
- Dead letter queues for failed events
- Consumer group load balancing
- Delayed/retry queues

---

## 5. API Gateway Pattern

### 5.1 Purpose

The API Gateway acts as the single entry point for all client requests, providing:

- **Request Routing**: Route `/api/tasks/*` → Core CRUD Service, `/api/auth/*` → Auth Service
- **Authentication**: Verify JWT tokens on every request before forwarding
- **Rate Limiting**: Per-user, per-endpoint rate limits (100 req/min standard, 10 req/min for AI endpoints)
- **Request Aggregation**: Combine multiple service responses for composite views (e.g., dashboard)
- **Protocol Translation**: Convert REST to gRPC for internal services (future)
- **CORS Management**: Single CORS policy point
- **Request/Response Logging**: Centralized audit trail

### 5.2 Gateway Technology Options

| Option | Pros | Cons |
|---|---|---|
| **FastAPI-based Gateway** | Same stack as existing backend; easy to implement | Manual routing configuration; less battle-tested as gateway |
| **Kong Gateway** | Battle-tested, plugin ecosystem, declarative config | Additional infrastructure; Lua/Go plugin language |
| **KrakenD** | High performance, configuration-driven, no vendor lock | Smaller community; limited dynamic routing |
| **Nginx + Lua** | Universal, proven at scale, low resource usage | Lua scripting complexity; manual configuration |

**Recommendation:** Custom FastAPI gateway for alpha (maintains stack一致性). Migrate to Kong or KrakenD when multi-service routing complexity increases.

### 5.3 Authentication Flow

```
Client ──▶ Gateway ──▶ Auth Service ──▶ Supabase Auth
            │               │
            │   JWT Claims  │
            │◀──────────────│
            │
            │ Forward Request + User Context
            ▼
      Target Service
```

1. Client sends request with `Authorization: Bearer <JWT>`
2. Gateway validates JWT against Auth Service (or caches public keys)
3. Gateway attaches `X-User-Id`, `X-User-Role` headers
4. Downstream services trust these headers (enforced via network policy)
5. Gateway rejects requests with invalid/expired tokens (401)

### 5.4 Rate Limiting Strategy

| Tier | Rate Limit | Burst | Applied To |
|---|---|---|---|
| Standard | 100 req/min | 20 | Most CRUD endpoints |
| AI Inference | 10 req/min | 3 | AI analysis, generation |
| Search | 60 req/min | 10 | Search queries |
| Webhook | 300 req/min | 50 | Internal service webhooks |

Rate limits are stored in Redis and keyed by `user_id` or `api_key`.

---

## 6. Service Discovery & Registry

### 6.1 Approach by Phase

| Phase | Method | Description |
|---|---|---|
| **Alpha** | Environment variables | `TASK_SERVICE_URL=http://localhost:8001` — hardcoded in docker-compose |
| **Beta** | DNS-based discovery | `task-service.internal` via Docker DNS or Kubernetes Services |
| **Production** | Service Registry | Consul or Kubernetes-native service discovery |

### 6.2 Health Checks

Each service exposes a `/health` endpoint returning:

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "uptime_seconds": 3600,
  "dependencies": {
    "database": { "status": "healthy", "latency_ms": 2 },
    "redis": { "status": "healthy", "latency_ms": 1 }
  }
}
```

The API Gateway or orchestrator polls `/health` at 10-second intervals. A service is considered unhealthy after 3 consecutive failures and is removed from the routing pool.

---

## 7. Data Management

### 7.1 Database Strategy

| Phase | Pattern | Rationale |
|---|---|---|
| **Alpha** | Shared Supabase instance, schema-per-service | Single team, low complexity, Supabase RLS reduces isolation needs |
| **Beta** | Shared instance, strict schema ownership | Clearer boundaries without operational overhead of multiple DBs |
| **Production** | Database-per-service | Full isolation, independent scaling, technology choice per service |

### 7.2 CQRS Considerations

CQRS is **not recommended** for alpha/beta. The system's read and write patterns are not sufficiently divergent to justify the complexity. However, the Search Service is a natural CQRS boundary — it maintains its own read-optimized indexes populated via domain events.

### 7.3 Event Sourcing

Event sourcing is **not recommended** for this project. The data model (tasks, habits, goals) is mutable and current-state-oriented rather than event-log-oriented. The operational cost of rebuilding state from events outweighs the benefits for this domain.

### 7.4 Cross-Service Data Consistency

For workflows spanning multiple services (e.g., "Create task with AI-generated subtasks"):

1. **Saga Pattern** — Choreography-based sagas via domain events
2. **Compensating Transactions** — Each service publishes `*.failed` events for rollback
3. **Idempotency Keys** — All write endpoints accept `Idempotency-Key` headers for safe retries

---

## 8. Migration Strategy

### 8.1 Strangler Fig Pattern

The migration follows the Strangler Fig pattern — incrementally extracting services from the monolith while maintaining backward compatibility.

```
Phase 1: Monolith          Phase 2: Extract Service     Phase 3: Full Microservices
┌──────────────────┐       ┌──────────────────┐          ┌──────────────────┐
│                  │       │                  │          │  API Gateway     │
│    Monolith      │       │  Monolith        │          ├──────────────────┤
│  (All Features)  │       │  (Most Features) │          │  Auth Service    │
│                  │       │                  │          ├──────────────────┤
│                  │       │  ┌────────────┐  │          │  Core CRUD       │
│                  │       │  │ Extracted  │  │          ├──────────────────┤
│                  │       │  │ Service    │  │          │  AI Service      │
│                  │       │  └────────────┘  │          ├──────────────────┤
│                  │       │                  │          │  Scheduler       │
│                  │       │  (Calls internal │          ├──────────────────┤
│                  │       │   + new service) │          │  Notification    │
│                  │       │                  │          ├──────────────────┤
│                  │       │                  │          │  Search Service  │
└──────────────────┘       └──────────────────┘          └──────────────────┘
```

### 8.2 Migration Sequence

| Phase | Services Extracted | Timeline | Effort |
|---|---|---|---|
| **Phase 0** | Monolith (current) | Current | N/A |
| **Phase 1** | Scheduler Service | Week 1-2 | Extract existing `services/scheduler/` |
| **Phase 2** | AI Service | Week 3-5 | Move `packages/ai/agents/` into standalone service |
| **Phase 3** | Notification Service | Week 6-7 | Implement notification service (see NotificationSystem.md) |
| **Phase 4** | Search Service | Week 8-10 | Implement search service (see SearchArchitecture.md) |
| **Phase 5** | Auth Service + API Gateway | Week 11-14 | Build gateway, extract auth |
| **Phase 6** | Core CRUD Service | Week 15-20 | Extract remaining monolith logic |
| **Phase 7** | Full migration complete | Week 20+ | Monolith decommissioned |

### 8.3 Migration Prerequisites

Before each service extraction:
1. CI/CD pipeline for the new service
2. Database migration scripts (backward-compatible schema changes)
3. Feature flag to toggle between monolith and new service
4. Canary deployment strategy (route 10% of traffic to new service)
5. Rollback plan with verified restore procedures

---

## 9. Service Mesh

### 9.1 Assessment

A service mesh (Istio, Linkerd) is **not needed** during alpha/beta. The operational complexity and resource overhead are not justified at current scale.

### 9.2 Future Evaluation Criteria

Consider service mesh when:
- 6+ microservices in production
- Traffic exceeds 1,000 requests/second
- mTLS requirements for all inter-service communication
- Advanced traffic splitting for canary deployments
- Distributed tracing requirements exceed application-level instrumentation

### 9.3 Recommended Mesh (Future)

| Mesh | Strengths | Recommendation |
|---|---|---|
| **Istio** | Feature-rich, Envoy-based, large ecosystem | Preferred for Kubernetes deployments |
| **Linkerd** | Lightweight, simpler, Rust-based data plane | Strong alternative if Istio complexity is too high |
| **Consul Connect** | Tight HashiCorp integration | If Consul is already used for service discovery |

---

## 10. Anti-Patterns

### 10.1 Distributed Monolith

**Symptom:** Services that require coordinated deployments, shared databases, or synchronous calls for every operation.

**Prevention:**
- Each service must have its own data store (or isolated schema by Phase 7)
- Deployments must be independent — no "deploy services A+B together"
- If two services require a synchronous call for >50% of operations, consider merging them

### 10.2 Chatty Services

**Symptom:** A client needs to call multiple services sequentially to perform a single logical operation.

**Prevention:**
- API Gateway aggregation endpoints for composite views
- API Composition pattern over client-side orchestration
- Cache service responses at the gateway level

### 10.3 Wrong-Sized Services

**Symptom:** Services that are too fine-grained (e.g., `TitleService`, `DescriptionService`) or too coarse (entire monolith rebranded as one service).

**Prevention:**
- Service boundaries should align with domain boundaries (bounded contexts)
- A service should own a complete business capability
- If a service has <5 endpoints, it is likely too small
- If a service has >50 endpoints, it is likely too large

### 10.4 Shared Database

**Symptom:** Multiple services directly accessing the same database tables.

**Prevention:**
- Enforce the rule: "No service accesses another service's database directly"
- Use API calls or event consumers for cross-service data needs
- Database views or read replicas are acceptable for read-only access when approved

### 10.5 Synchronous Chain

**Symptom:** A → B → C → D synchronous call chain with deep coupling.

**Prevention:**
- Maximum synchronous call depth: 3 services
- For deeper workflows, use asynchronous event-driven choreography
- Implement timeout and circuit breaker at each hop

---

## 11. Appendices

### 11.1 ADR References

| ADR | Title | Status |
|---|---|---|
| ADR-004 | Monolith First | Approved |
| ADR-007 | Microservices Migration Path | Draft |
| ADR-012 | API Gateway Selection | Draft |
| ADR-015 | Inter-Service Communication Protocol | Pending |

### 11.2 Migration Roadmap (Summary)

Phase 0: Monolith (Current — Q2 2026)
Phase 1: Scheduler Extraction (Q3 2026)
Phase 2: AI Service Extraction (Q3 2026)
Phase 3: Notification Service (Q4 2026)
Phase 4: Search Service (Q4 2026)
Phase 5: Auth Service + Gateway (Q1 2027)
Phase 6: Core CRUD Service (Q1-Q2 2027)
Phase 7: Full Migration (Q2 2027)

### 11.3 Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | ARIA OS Engineering | Initial draft |
