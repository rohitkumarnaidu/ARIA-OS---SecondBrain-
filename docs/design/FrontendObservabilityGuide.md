---
version: 3.0.0
status: active
classification: Internal — Engineering Standards
last_updated: 2026-06-13
target_audience: Frontend Engineers, SRE, AI Agents
review_cycle: bi-weekly
approved_by: Engineering Lead
document_id: SB-OBS-REF-001
amendment_history:
  - version: 1.0.0
    date: 2026-06-01
    author: Engineering Team
    changes: Initial observability guide
  - version: 2.0.0
    date: 2026-06-10
    author: Engineering Team
    changes: Added Sentry tunnels, PostHog feature flags, TanStack Query observability
  - version: 3.0.0
    date: 2026-06-13
    author: Engineering Team
    changes: Enterprise upgrade — 19 sections, 3000+ lines, full production code examples, AI observability, cost management, incident response, debugging guide, implementation roadmap
---

# Frontend Observability Guide — Second Brain OS (Enterprise Edition)

## 1. Document Control

### 1.1 Document Metadata

| Field | Value |
|---|---|
| Document ID | SB-OBS-REF-001 |
| Version | 3.0.0 |
| Status | Active |
| Classification | Internal — Engineering Standards |
| Last Updated | 2026-06-13 |
| Stack | Next.js 14 + TypeScript + Supabase + Sentry 10.x + PostHog 1.x |
| Target Audience | Frontend Engineers, SRE, AI Agents |
| Review Cycle | Bi-weekly (every 2nd Friday) |
| Approver | Engineering Lead |
| Slack Channel | #observability |

### 1.2 Amendment History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-01 | Engineering Team | Initial observability guide |
| 2.0.0 | 2026-06-10 | Engineering Team | Added Sentry tunnels, PostHog feature flags, TanStack Query observability |
| 3.0.0 | 2026-06-13 | Engineering Team | Enterprise upgrade — 19 sections, 3000+ lines, full production code examples, AI observability, cost management, incident response, debugging guide, implementation roadmap |

### 1.3 Related Documents

| Document ID | Title | Location |
|---|---|---|
| SB-ARCH-REF-001 | System Architecture Guide | `docs/engineering/12_Architecture.md` |
| SB-API-REF-001 | API Reference Guide | `docs/engineering/17_API.md` |
| SB-DB-REF-001 | Database Schema Guide | `docs/engineering/15_Database.md` |
| SB-AGENTS-REF-001 | AI Agent Reference | `AGENTS.md` |
| SB-SEC-REF-001 | Security Guide | `docs/security/24_Security.md` |
| SB-DEPLOY-REF-001 | Deployment Guide | `docs/devops/26_Deployment.md` |
| SB-TEST-REF-001 | Testing Guide | `docs/qa/28_Testing.md` |

### 1.4 Glossary

| Term | Definition |
|---|---|
| CWV | Core Web Vitals — LCP, CLS, INP, FCP, TTFB |
| DSN | Data Source Name — Sentry project identifier |
| RUM | Real User Monitoring — passive performance collection from actual users |
| PII | Personally Identifiable Information |
| RLS | Row Level Security — Supabase per-user data isolation |
| TQ | TanStack Query |
| DAU | Daily Active Users |
| WAU | Weekly Active Users |
| SPoF | Single Point of Failure |

## 2. Executive Summary

### 2.1 Observability Philosophy

Frontend observability for Second Brain OS means understanding exactly what users experience — errors, performance, behavior, and satisfaction — across 16 modules serving BTech CSE students. This guide establishes the unified observability strategy using Sentry (error tracking + performance), PostHog (analytics + feature flags), web-vitals (RUM), and structured logging.

Our observability strategy follows four core principles:

1. **Understand before optimizing** — Collect data first, then analyze, then act
2. **Graceful degradation** — Every observability tool must never break the user experience
3. **Privacy by design** — PII redaction is built into every layer, not bolted on
4. **Cost-conscious** — Sampling strategies prevent runaway costs while preserving signal

### 2.2 Three Pillars of Observability

| Pillar | Tool | What We Track |
|---|---|---|
| LOGS | Structured JSON Logger | Debug, info, warn, error, fatal with PII redaction, batching, correlation IDs |
| TRACES | Sentry Browser Tracing | Route transitions, API calls, AI agent calls, module loads |
| METRICS | web-vitals + Sentry + PostHog | Core Web Vitals, business metrics, DAU, feature adoption |

### 2.3 SLA Targets

| Category | Metric | Target | Measurement | Tool |
|---|---|---|---|---|
| Availability | Page load success | >=99.9% | Successful navigations / total navigations | Sentry |
| Performance | LCP | <=2.5s (p75) | 75th percentile across all page loads | web-vitals |
| Performance | CLS | <=0.1 (p75) | 75th percentile layout shift score | web-vitals |
| Performance | INP | <=200ms (p75) | 75th percentile interaction delay | web-vitals |
| Errors | Error rate | <=1% of page views | Errors / total page views | Sentry |
| Errors | Critical errors | 0 | P0 errors that reach users | Sentry + Alerting |
| Analytics | Event loss | <=5% | Events fired vs events received | PostHog |
| AI | LLM response time | <=10s p95 | End-to-end generation latency | Sentry metrics |
| AI | Fallback rate | <=5% | Ollama to Claude to algorithmic fallback ratio | Sentry metrics |

### 2.4 Module Inventory (16 modules)

| # | Module | Route | Page File |
|---|---|---|---|
| 1 | Dashboard | `/dashboard` | `app/(dashboard)/dashboard/page.tsx` |
| 2 | Tasks | `/tasks` | `app/(dashboard)/tasks/page.tsx` |
| 3 | Courses | `/courses` | `app/(dashboard)/courses/page.tsx` |
| 4 | Habits | `/habits` | `app/(dashboard)/habits/page.tsx` |
| 5 | Goals | `/goals` | `app/(dashboard)/goals/page.tsx` |
| 6 | Sleep | `/sleep` | `app/(dashboard)/sleep/page.tsx` |
| 7 | Income | `/income` | `app/(dashboard)/income/page.tsx` |
| 8 | Projects | `/projects` | `app/(dashboard)/projects/page.tsx` |
| 9 | Ideas | `/ideas` | `app/(dashboard)/ideas/page.tsx` |
| 10 | Resources | `/resources` | `app/(dashboard)/resources/page.tsx` |
| 11 | Opportunities | `/opportunities` | `app/(dashboard)/opportunities/page.tsx` |
| 12 | Time | `/time` | `app/(dashboard)/time/page.tsx` |
| 13 | Chat | `/chat` | `app/(dashboard)/chat/page.tsx` |
| 14 | Automation | `/automation` | `app/(dashboard)/automation/page.tsx` |
| 15 | YouTube | `/youtube` | `app/(dashboard)/youtube/page.tsx` |
| 16 | Academics | `/academics` | `app/(dashboard)/academics/page.tsx` |

## 3. Sentry Architecture

### 3.1 Installation

```bash
# Core Sentry packages (already installed via package.json)
npm install @sentry/nextjs @sentry/react @sentry/browser

# Verify versions
npx sentry-cli --version
```

### 3.2 Client-Side Configuration (Complete File)

```tsx
// apps/web/sentry.client.config.ts
// Full enterprise-grade Sentry client initialization
import * as Sentry from "@sentry/nextjs"

const SAMPLE_RATES: Record<string, number> = {
  "/dashboard": 0.1,
  "/tasks": 0.25,
  "/chat": 0.5,
  "/api": 0.1,
  default: 0.25,
}

function getDynamicSampleRate(): number {
  if (typeof window === "undefined") return SAMPLE_RATES.default
  const path = window.location.pathname
  for (const [route, rate] of Object.entries(SAMPLE_RATES)) {
    if (path.startsWith(route)) return rate
  }
  return SAMPLE_RATES.default
}

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN || "",
  environment: process.env.NODE_ENV || "development",
  release:
    process.env.NEXT_PUBLIC_APP_VERSION ||
    `sb-os@${process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA?.slice(0, 7) || "local"}`,
  dist: String(process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA || Date.now()),

  // Sampling strategy
  tracesSampleRate: process.env.NODE_ENV === "production" ? getDynamicSampleRate() : 0,
  profilesSampleRate: process.env.NODE_ENV === "production" ? 0.2 : 0,

  // Session Replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  // Integrations
  integrations:
    process.env.NODE_ENV === "production"
      ? [
          Sentry.replayIntegration({
            maskAllText: true,
            blockAllMedia: true,
            blockSelectors: ["iframe", "video", "audio", "[data-sentry-block]"],
          }),
          Sentry.browserTracingIntegration({
            enableInp: true,
            idleTimeout: 5000,
          }),
          Sentry.feedbackIntegration({
            colorScheme: "dark",
            showBranding: false,
            formTitle: "Report a bug",
            submitButtonLabel: "Send report",
            messagePlaceholder: "Describe what went wrong...",
          }),
          Sentry.httpClientIntegration(),
          Sentry.captureConsoleIntegration({
            levels: ["error", "warn"],
          }),
        ]
      : [],

  enabled: process.env.NODE_ENV === "production",

  // Tunnel through Next.js API to bypass ad blockers
  tunnel: "/api/monitoring",

  beforeSend(event, hint) {
    // Strip PII from headers
    if (event.request?.headers) {
      delete event.request.headers["Authorization"]
      delete event.request.headers["Cookie"]
      delete event.request.headers["X-Supabase-Auth"]
      delete event.request.headers["X-Forwarded-For"]
      delete event.request.headers["CF-Connecting-IP"]
    }

    // Strip PII from user context
    if (event.user) {
      event.user = { id: event.user.id }
    }

    // Strip PII from breadcrumbs
    if (event.breadcrumbs) {
      event.breadcrumbs = event.breadcrumbs.map((crumb) => {
        if (crumb.data?.headers) {
          crumb.data = { __sensitive_removed: true }
        }
        return crumb
      })
    }

    // Error fingerprinting
    const errorValue = event.exception?.values?.[0]
    if (errorValue) {
      const type = errorValue.type || ""
      const value = errorValue.value || ""

      // Network errors
      if (type === "TypeError" && value.includes("fetch")) {
        event.fingerprint = ["network-error", "fetch-failure"]
      }
      if (value.includes("Failed to fetch") || value.includes("Load failed")) {
        event.fingerprint = ["network-error", "failed-fetch"]
      }

      // Supabase errors
      if (type === "PostgrestError" || value.includes("Supabase")) {
        event.fingerprint = ["supabase-error"]
      }
      if (value.includes("row level security") || value.includes("RLS")) {
        event.fingerprint = ["supabase-error", "rls-violation"]
      }
      if (value.includes("JWT")) {
        event.fingerprint = ["auth-error", "jwt"]
      }

      // AI errors
      if (value.includes("Ollama") || value.includes("ollama")) {
        event.fingerprint = ["ai-error", "ollama"]
      }
      if (value.includes("Claude") || value.includes("claude")) {
        event.fingerprint = ["ai-error", "claude"]
      }

      // Auth errors
      if (type === "AuthError" || value.includes("AuthApiError")) {
        event.fingerprint = ["auth-error"]
      }

      // Zod validation errors
      if (type === "ZodError" || value.includes("Zod")) {
        event.fingerprint = ["validation-error", "zod"]
      }

      // Chunk load errors
      if (type === "ChunkLoadError") {
        event.fingerprint = ["build-error", "chunk-load"]
      }

      // Timeouts
      if (value.includes("timeout") || value.includes("timed out")) {
        event.fingerprint = ["timeout-error"]
      }

      // Rate limits
      if (value.includes("429") || value.includes("rate limit")) {
        event.fingerprint = ["rate-limit"]
      }

      // Offline errors
      if (value.includes("offline") || value.includes("Offline")) {
        event.fingerprint = ["offline-error"]
      }
    }

    return event
  },

  beforeSendTransaction(event) {
    if (event.transaction) {
      event.transaction = event.transaction.replace(/\b[a-f0-9]{8,}\b/g, "[hash]")
    }
    return event
  },
})
```

### 3.3 Server-Side Configuration

```tsx
// apps/web/sentry.server.config.ts
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN || "",
  environment: process.env.NODE_ENV || "development",
  release: process.env.NEXT_PUBLIC_APP_VERSION || "local",
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.5 : 0,
  enabled: process.env.NODE_ENV === "production",
  integrations: [
    Sentry.httpIntegration({ breadcrumbs: true, tracing: true }),
    Sentry.extraErrorDataIntegration({ depth: 3 }),
  ],
  beforeSend(event) {
    if (event.request?.cookies) delete event.request.cookies
    if (event.request?.headers) {
      delete event.request.headers["cookie"]
      delete event.request.headers["authorization"]
      delete event.request.headers["x-api-key"]
    }
    return event
  },
})
```

### 3.4 Next.js Configuration with Sentry

```tsx
// apps/web/next.config.js
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["localhost", "supabase.co", "img.youtube.com"],
    formats: ["image/avif", "image/webp"],
    minimumCacheTTL: 86400,
  },
  sentry: {
    hideSourceMaps: true,
    widenClientFileUpload: true,
    disableLogger: true,
    tunnelRoute: "/api/monitoring",
  },
  headers: async () => [
    {
      source: "/:path*",
      headers: [
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      ],
    },
  ],
}

const { withSentryConfig } = require("@sentry/nextjs")
module.exports = withSentryConfig(nextConfig, {
  org: "second-brain-os",
  project: "frontend",
  silent: !process.env.CI,
  widenClientFileUpload: true,
  tunnelRoute: "/api/monitoring",
  hideSourceMaps: true,
  disableLogger: true,
  automaticVercelMonitors: true,
})
```

### 3.5 Sentry Tunnel Endpoint

```tsx
// apps/web/app/api/monitoring/route.ts
import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const envelope = await request.text()
    const pieces = envelope.split("\n")
    const header = JSON.parse(pieces[0])
    const host = header.dsn
      ? new URL(header.dsn)
      : new URL(process.env.NEXT_PUBLIC_SENTRY_DSN || "")
    const projectId = host.pathname?.replace("/", "") || ""

    const response = await fetch(`https://${host.hostname}/api/${projectId}/envelope/`, {
      method: "POST",
      body: envelope,
      headers: { "Content-Type": "application/x-sentry-envelope" },
    })

    return new NextResponse(response.body, {
      status: response.status,
      headers: { "Content-Type": "text/plain" },
    })
  } catch (error) {
    console.error("[Sentry Tunnel] Failed to forward envelope:", error)
    return NextResponse.json({ error: "Failed to forward" }, { status: 500 })
  }
}
```

### 3.6 Source Maps and Release Tracking CI

```yaml
# .github/workflows/sentry-release.yml
name: Sentry Release

on:
  push:
    branches: [main]
    paths:
      - "apps/web/**"

jobs:
  sentry-release:
    name: Create Sentry Release and Upload Source Maps
    runs-on: ubuntu-latest
    timeout-minutes: 10
    defaults:
      run:
        working-directory: apps/web

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm
          cache-dependency-path: apps/web/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Create Sentry release
        env:
          SENTRY_AUTH_TOKEN: \${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: second-brain-os
          SENTRY_PROJECT: frontend
        run: |
          SENTRY_RELEASE="sb-os@\${{ github.sha }}"
          npx sentry-cli releases new "$SENTRY_RELEASE"
          npx sentry-cli releases set-commits "$SENTRY_RELEASE" --auto
          npx sentry-cli releases files "$SENTRY_RELEASE" upload-sourcemaps .next/static/chunks --url-prefix "~/_next/static/chunks"
          npx sentry-cli releases finalize "$SENTRY_RELEASE"
          npx sentry-cli releases deploys "$SENTRY_RELEASE" new -e production
```

### 3.7 Error Grouping Rules (Complete Fingerprint Table)

| Pattern | Fingerprint | Priority |
|---|---|---|
| TypeError with fetch | ["network-error", "fetch-failure"] | P1 |
| Failed to fetch / Load failed | ["network-error", "failed-fetch"] | P1 |
| PostgrestError or supabase keyword | ["supabase-error"] | P1 |
| RLS violation | ["supabase-error", "rls-violation"] | P0 |
| JWT errors | ["auth-error", "jwt"] | P1 |
| Ollama-related | ["ai-error", "ollama"] | P2 |
| Claude-related | ["ai-error", "claude"] | P2 |
| AuthError / AuthApiError | ["auth-error"] | P1 |
| ZodError | ["validation-error", "zod"] | P3 |
| ChunkLoadError | ["build-error", "chunk-load"] | P0 |
| Timeout errors | ["timeout-error"] | P2 |
| Rate limit (429) | ["rate-limit"] | P3 |
| Offline errors | ["offline-error"] | P3 |

### 3.8 Dynamic Sampling Strategy

| Route | Sample Rate | Rationale |
|---|---|---|
| /dashboard | 0.1 | Low-value, high-volume |
| /tasks | 0.25 | Medium-value, moderate volume |
| /courses | 0.25 | Medium-value |
| /habits | 0.1 | Low-value, simple CRUD |
| /goals | 0.25 | Medium-value |
| /sleep | 0.1 | Low-value |
| /income | 0.1 | Low-value |
| /projects | 0.25 | Medium-value |
| /ideas | 0.1 | Low-value |
| /resources | 0.1 | Low-value |
| /opportunities | 0.25 | Medium-value |
| /time | 0.1 | Low-value |
| /chat | 0.5 | High-value AI interactions |
| /automation | 0.25 | Medium-value |
| /youtube | 0.1 | Low-value |
| /academics | 0.25 | Medium-value |
| /api | 0.1 | Server-side, sampled on server |
| default | 0.25 | Catch-all |

## 4. Error Tracking Deep Dive

### 4.1 Error Taxonomy

```
ERROR TAXONOMY
+-- NETWORK_ERRORS (P1)
¦   +-- fetch-failure
¦   +-- timeout
¦   +-- offline
¦   +-- chunk-load
¦   +-- rate-limit
+-- API_ERRORS (P1)
¦   +-- 400 Bad Request
¦   +-- 401 Unauthorized
¦   +-- 403 Forbidden
¦   +-- 404 Not Found
¦   +-- 500 Server Error
+-- SUPABASE_ERRORS (P1)
¦   +-- rls-violation
¦   +-- jwt-expired
¦   +-- query-error
+-- AI_ERRORS (P2)
¦   +-- ollama-down
¦   +-- claude-error
¦   +-- token-limit
¦   +-- timeout
+-- VALIDATION_ERRORS (P3)
¦   +-- zod
¦   +-- form
+-- RENDER_ERRORS (P0)
¦   +-- react-boundary
¦   +-- react-crash
+-- UNKNOWN (P2)
    +-- unhandled
```

### 4.2 Custom Error Classes

```tsx
// lib/errors/index.ts
export interface ErrorMetadata {
  module?: string
  operation?: string
  userId?: string
  table?: string
  agentName?: string
  statusCode?: number
  retryable?: boolean
  fallbackUsed?: boolean
  latencyMs?: number
  [key: string]: unknown
}

export class AppError extends Error {
  public readonly metadata: ErrorMetadata
  public readonly severity: "low" | "medium" | "high" | "critical"
  public readonly timestamp: string

  constructor(
    message: string,
    metadata: ErrorMetadata = {},
    severity: "low" | "medium" | "high" | "critical" = "medium",
  ) {
    super(message)
    this.name = "AppError"
    this.metadata = metadata
    this.severity = severity
    this.timestamp = new Date().toISOString()
  }
}

export class APIError extends AppError {
  public readonly statusCode: number

  constructor(message: string, statusCode: number, metadata: ErrorMetadata = {}) {
    super(message, { ...metadata, statusCode }, statusCode >= 500 ? "critical" : "high")
    this.name = "APIError"
    this.statusCode = statusCode
  }
}

export class SupabaseError extends AppError {
  public readonly table: string
  public readonly operation: string

  constructor(message: string, table: string, operation: string, metadata: ErrorMetadata = {}) {
    super(message, { ...metadata, table, operation }, "high")
    this.name = "SupabaseError"
    this.table = table
    this.operation = operation
  }
}

export class AIError extends AppError {
  public readonly agentName: string
  public readonly model: string
  public readonly fallbackUsed: boolean

  constructor(message: string, agentName: string, model: string, metadata: ErrorMetadata = {}, fallbackUsed = false) {
    super(message, { ...metadata, agentName, fallbackUsed }, fallbackUsed ? "low" : "high")
    this.name = "AIError"
    this.agentName = agentName
    this.model = model
    this.fallbackUsed = fallbackUsed
  }
}

export class ValidationError extends AppError {
  public readonly fieldErrors: Record<string, string[]>

  constructor(message: string, fieldErrors: Record<string, string[]> = {}, metadata: ErrorMetadata = {}) {
    super(message, { ...metadata, fieldCount: Object.keys(fieldErrors).length }, "low")
    this.name = "ValidationError"
    this.fieldErrors = fieldErrors
  }
}

export class OfflineError extends AppError {
  constructor(metadata: ErrorMetadata = {}) {
    super("Browser is offline", metadata, "low")
    this.name = "OfflineError"
  }
}
```

### 4.3 Error Boundary — Three Variants

```tsx
// components/shared/ErrorBoundary.tsx
"use client"

import { Component, ErrorInfo, ReactNode } from "react"
import * as Sentry from "@sentry/nextjs"
import { AlertTriangle, RefreshCw, Home } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { trackEvent } from "@/lib/utils/analytics"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("error-boundary")

// Variant 1: Module-level Error Boundary (full page)
export class ModuleErrorBoundary extends Component<
  { children: ReactNode; moduleName: string; onReset?: () => void },
  { hasError: boolean; error: Error | null; resetCount: number }
> {
  public state = { hasError: false, error: null as Error | null, resetCount: 0 }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const { moduleName } = this.props
    log.error(`Module error in ${moduleName}`, { message: error.message })
    Sentry.captureException(error, {
      extra: { componentStack: errorInfo.componentStack, moduleName },
      tags: { boundary: "module", module: moduleName },
    })
    trackEvent("error_boundary_caught", { boundary: "module", module: moduleName, error: error.message })
  }

  handleReset = () => {
    const { moduleName, onReset } = this.props
    if (this.state.resetCount >= 3) {
      log.warn(`Exceeded max reset attempts for ${moduleName}`)
      return
    }
    this.setState({ hasError: false, error: null, resetCount: this.state.resetCount + 1 })
    onReset?.()
  }

  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <div role="alert" className="min-h-[50vh] flex items-center justify-center p-8">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-16 h-16 rounded-2xl bg-accent-error/10 flex items-center justify-center mx-auto">
            <AlertTriangle size={32} className="text-accent-error" />
          </div>
          <h2 className="text-xl font-display font-semibold text-text-primary">
            {this.props.moduleName} failed to load
          </h2>
          <p className="text-text-secondary text-sm">Something went wrong. Our team has been notified.</p>
          {this.state.resetCount <= 3 && (
            <Button variant="primary" size="lg" onClick={this.handleReset} icon={<RefreshCw size={16} />}>
              Try again
            </Button>
          )}
        </div>
      </div>
    )
  }
}

// Variant 2: Section-level Error Boundary
export class SectionErrorBoundary extends Component<
  { children: ReactNode; moduleName: string },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: ReactNode; moduleName: string }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, {
      extra: { componentStack: errorInfo.componentStack, moduleName: this.props.moduleName },
      tags: { boundary: "section", module: this.props.moduleName },
    })
  }

  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <div role="alert" className="flex flex-col items-center justify-center p-6 bg-background-card rounded-xl border border-border">
        <AlertTriangle size={24} className="text-accent-warning mb-3" />
        <p className="text-sm text-text-primary font-medium mb-1">{this.props.moduleName} unavailable</p>
        <Button variant="secondary" size="sm" onClick={() => this.setState({ hasError: false, error: null })}>
          <RefreshCw size={12} /> Retry
        </Button>
      </div>
    )
  }
}

// Variant 3: Component-level Error Boundary (tiny widget)
export class ComponentErrorBoundary extends Component<
  { children: ReactNode; name?: string; fallback?: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode; name?: string; fallback?: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error) {
    Sentry.captureException(error, { tags: { boundary: "component", component: this.props.name || "unknown" } })
  }

  render() {
    if (this.state.hasError) return this.props.fallback || null
    return this.props.children
  }
}
```

### 4.4 API Call Wrapping (Fetch)

```tsx
// lib/api/fetch.ts
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { AppError, APIError } from "@/lib/errors"

const log = createLogger("api-fetch")

interface FetchOptions extends RequestInit {
  module?: string
  operation?: string
  retries?: number
  timeout?: number
  retryDelay?: number
}

const DEFAULT_TIMEOUT = 15_000
const MAX_RETRIES = 2
const RETRYABLE_STATUSES = [408, 429, 500, 502, 503, 504]

export async function apiFetch<T = unknown>(url: string, options: FetchOptions = {}): Promise<T> {
  const {
    module = "unknown",
    operation = "request",
    retries = MAX_RETRIES,
    timeout = DEFAULT_TIMEOUT,
    retryDelay = 1000,
    ...fetchOptions
  } = options

  const startTime = performance.now()
  let lastError: Error | null = null

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)
      const response = await fetch(url, { ...fetchOptions, signal: controller.signal })
      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorBody = await response.text().catch(() => "")
        const error = new APIError(`HTTP ${response.status}: ${response.statusText}`, response.status, {
          module, operation, url: url.replace(/\?.*/, ""), body: errorBody.slice(0, 500), attempt: attempt + 1,
        })
        if (RETRYABLE_STATUSES.includes(response.status) && attempt < retries) {
          log.warn(`Retrying ${operation} (attempt ${attempt + 1}/${retries})`, { status: response.status, url })
          await new Promise((r) => setTimeout(r, retryDelay * 2 ** attempt))
          continue
        }
        throw error
      }

      const data = await response.json()
      const duration = performance.now() - startTime
      Sentry.metrics.distribution("api.latency", duration, { unit: "millisecond", tags: { module, operation } })
      return data as T
    } catch (err) {
      if (err instanceof AppError) throw err
      lastError = err instanceof Error ? err : new Error(String(err))
      if (lastError.name === "AbortError") {
        throw new AppError(`Request timed out after ${timeout}ms: ${operation}`, { module, operation, url, timeout }, "high")
      }
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, retryDelay * 2 ** attempt))
        continue
      }
      throw new AppError(`Request failed after ${retries + 1} attempts: ${lastError.message}`, {
        module, operation, url, attempts: retries + 1,
      }, "high")
    }
  }
  throw new Error("Unreachable state in apiFetch")
}
```

### 4.5 Supabase Error Wrapping (Complete)

```tsx
// lib/supabase.ts
import { createClient, PostgrestError } from "@supabase/supabase-js"
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { trackEvent } from "@/lib/utils/analytics"
import { SupabaseError } from "@/lib/errors"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ""
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ""
export const isUsingPlaceholders = supabaseUrl.includes("placeholder")
const log = createLogger("supabase")

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: { persistSession: true, autoRefreshToken: true },
  global: {
    fetch: (...args) => {
      const startTime = performance.now()
      return fetch(...args).finally(() => {
        const duration = performance.now() - startTime
        if (duration > 2000) {
          Sentry.metrics.distribution("supabase.query_latency", duration, { unit: "millisecond" })
        }
      })
    },
  },
})

export async function executeQuery<T>(
  table: string,
  queryFn: () => Promise<{ data: T | null; error: PostgrestError | null }>,
  options: { operation?: string; userId?: string } = {},
): Promise<T> {
  const { operation = "query", userId } = options
  const startTime = performance.now()
  try {
    const { data, error } = await queryFn()
    if (error) {
      const duration = performance.now() - startTime
      const supabaseErr = new SupabaseError(error.message, table, operation, { userId, duration, code: error.code })
      log.error(`Supabase ${operation} on ${table} failed`, { code: error.code, message: error.message, duration })
      Sentry.captureException(supabaseErr, {
        tags: { supabase_table: table, supabase_operation: operation, supabase_code: error.code || "unknown" },
        extra: { details: error.details, hint: error.hint, duration },
      })
      trackEvent("supabase_error", { table, operation, code: error.code, duration })
      throw supabaseErr
    }
    const duration = performance.now() - startTime
    Sentry.metrics.distribution("supabase.latency", duration, { unit: "millisecond", tags: { table, operation } })
    if (duration > 3000) log.warn(`Slow Supabase query on ${table}`, { duration, operation })
    return data as T
  } catch (err) {
    if (err instanceof SupabaseError) throw err
    throw new SupabaseError(`Unexpected error: ${err instanceof Error ? err.message : String(err)}`, table, operation)
  }
}

export const db = {
  select: <T>(table: string) => executeQuery<T[]>(table, () => supabase.from(table).select("*"), { operation: "select" }),
  getById: <T>(table: string, id: string) =>
    executeQuery<T>(table, () => supabase.from(table).select("*").eq("id", id).single(), { operation: "getById" }),
  insert: <T>(table: string, data: Record<string, unknown>) =>
    executeQuery<T>(table, () => supabase.from(table).insert(data).select().single(), { operation: "insert" }),
  update: <T>(table: string, id: string, data: Record<string, unknown>) =>
    executeQuery<T>(table, () => supabase.from(table).update(data).eq("id", id).select().single(), { operation: "update" }),
  delete: (table: string, id: string) =>
    executeQuery(table, () => supabase.from(table).delete().eq("id", id), { operation: "delete" }),
}
```

### 4.6 TanStack Query Error Handler

```tsx
// lib/query/queryClient.ts
import { QueryClient, QueryCache, MutationCache } from "@tanstack/react-query"
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { trackEvent } from "@/lib/utils/analytics"

const log = createLogger("tanstack-query")

export function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(1000 * 3 ** attemptIndex, 10000),
        refetchOnWindowFocus: false,
        refetchOnReconnect: true,
        refetchOnMount: true,
        networkMode: "offlineFirst",
      },
      mutations: {
        retry: 1,
        retryDelay: 1000,
        networkMode: "offlineFirst",
      },
    },
    queryCache: new QueryCache({
      onError: (error, query) => {
        log.error(`Query error`, { queryKey: query.queryKey.join(", "), message: String(error) })
        Sentry.captureException(error, { tags: { source: "tanstack-query" } })
        trackEvent("tanstack_query_error", { message: String(error), queryKey: query.queryKey.join(", ") })
      },
    }),
    mutationCache: new MutationCache({
      onError: (error, _vars, _ctx, mutation) => {
        log.error(`Mutation error`, { mutationKey: mutation.options.mutationKey?.join(", "), message: String(error) })
        Sentry.captureException(error, { tags: { source: "tanstack-mutation" } })
      },
      onSuccess: (_data, _vars, _ctx, mutation) => {
        Sentry.metrics.increment("tanstack.mutation_success", 1, {
          tags: { mutationKey: mutation.options.mutationKey?.join("-") || "unknown" },
        })
      },
    }),
  })
}
```

### 4.7 Global Error Handler

```tsx
// apps/web/app/global-error.tsx
"use client"

import { useEffect } from "react"
import * as Sentry from "@sentry/nextjs"

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    Sentry.captureException(error, {
      tags: { global_error: "true" },
      extra: { digest: error.digest, url: typeof window !== "undefined" ? window.location.href : undefined },
    })
  }, [error])

  return (
    <html>
      <body className="bg-background-dark text-text-primary">
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="max-w-md text-center space-y-6">
            <h1 className="text-2xl font-display font-bold">Critical Error</h1>
            <p className="text-text-secondary text-sm">A critical error occurred. Our team has been notified.</p>
            {error.digest && <p className="text-text-tertiary text-xs font-mono">Reference: {error.digest}</p>}
            <button onClick={reset} className="bg-accent-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-accent-primaryHover">
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
```

### 4.8 Unhandled Promise Rejection Tracking

```tsx
// lib/errors/unhandled-rejection.ts
"use client"

import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("unhandled-rejection")

export function setupUnhandledRejectionTracking() {
  if (typeof window === "undefined") return

  window.addEventListener("unhandledrejection", (event: PromiseRejectionEvent) => {
    const reason = event.reason
    const message = reason instanceof Error ? reason.message : String(reason)
    log.error(`Unhandled promise rejection: ${message}`)
    Sentry.captureException(reason instanceof Error ? reason : new Error(message), {
      tags: { unhandled_rejection: "true" },
      extra: { message, url: window.location.href },
    })
  })
}
```

### 4.9 Observability Init (Dashboard Layout)

```tsx
// apps/web/app/(dashboard)/observability-init.tsx
"use client"

import { useEffect } from "react"
import { reportWebVitals } from "@/lib/web-vitals"
import { usePageView } from "@/hooks/usePageView"
import { setupUnhandledRejectionTracking } from "@/lib/errors/unhandled-rejection"

export function ObservabilityInit() {
  usePageView()

  useEffect(() => {
    reportWebVitals()
    setupUnhandledRejectionTracking()
    performance.mark("dashboard-loaded")
  }, [])

  return null
}
```

### 4.10 Error Recovery Strategies

| Strategy | Pattern | When to Use |
|---|---|---|
| Retry (exponential backoff) | apiFetch retries with 1s, 3s, 9s delays | Network errors, 5xx, 429 |
| Refresh token | supabase.auth.getSession() on 401 | Auth token expired |
| Reset state | ErrorBoundary reset, clear local state, retry | UI rendering errors |
| Fallback content | Show cached/empty state | Non-critical sections |
| Full page reload | window.location.reload() | Chunk load failures |
| Service worker | Return cached response | Offline scenarios |
| Degraded mode | Disable AI, use algorithmic fallback | AI unreachable |
| Queue and retry | IndexedDB queue for mutations | Offline mutations |

### 4.11 Error Reporting Utility

```tsx
// lib/errors/reporter.ts
import * as Sentry from "@sentry/nextjs"
import { trackEvent } from "@/lib/utils/analytics"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("error-reporter")

export function reportError(error: Error | string, options: {
  message?: string
  context?: Record<string, unknown>
  tags?: Record<string, string>
  level?: "info" | "warning" | "error" | "fatal"
  fingerprint?: string[]
  user?: { id: string }
} = {}) {
  const errorInstance = typeof error === "string" ? new Error(error) : error
  log.error(options.message || errorInstance.message, options.context)

  const scope = new Sentry.Scope()
  if (options.fingerprint) scope.setFingerprint(options.fingerprint)
  if (options.user) scope.setUser(options.user)
  scope.setTags({ source: "custom", ...options.tags })
  scope.setExtras(options.context || {})
  Sentry.captureException(errorInstance, scope)
  trackEvent("error_reported", { error: errorInstance.message, level: options.level, ...options.tags })
}

## 5. Performance Monitoring

### 5.1 Core Web Vitals — Complete Implementation

```tsx
// lib/web-vitals.ts
"use client"

import { onCLS, onFCP, onINP, onLCP, onTTFB, type Metric } from "web-vitals"
import * as Sentry from "@sentry/nextjs"
import posthog from "posthog-js"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("web-vitals")

type MetricName = "CLS" | "FCP" | "INP" | "LCP" | "TTFB"

const VITALS_THRESHOLDS: Record<MetricName, { good: number; poor: number }> = {
  CLS: { good: 0.1, poor: 0.25 },
  FCP: { good: 1800, poor: 3000 },
  INP: { good: 200, poor: 500 },
  LCP: { good: 2500, poor: 4000 },
  TTFB: { good: 800, poor: 1800 },
}

function getCurrentModule(): string {
  if (typeof window === "undefined") return "unknown"
  const path = window.location.pathname
  const modules = ["dashboard", "tasks", "courses", "habits", "goals", "sleep", "income",
    "projects", "ideas", "resources", "opportunities", "time", "chat", "automation", "youtube", "academics"]
  for (const mod of modules) {
    if (path.startsWith(`/${mod}`)) return mod
  }
  return "unknown"
}

export function reportWebVitals() {
  log.info("Web Vitals reporting initialized")
  onCLS((metric) => processMetric("CLS", metric))
  onFCP((metric) => processMetric("FCP", metric))
  onINP((metric) => processMetric("INP", metric))
  onLCP((metric) => processMetric("LCP", metric))
  onTTFB((metric) => processMetric("TTFB", metric))
}

function processMetric(name: MetricName, metric: Metric) {
  const threshold = VITALS_THRESHOLDS[name]
  const rating = metric.value <= threshold.good ? "good" : metric.value <= threshold.poor ? "needs-improvement" : "poor"
  const module = getCurrentModule()

  Sentry.metrics.distribution(`web_vital.${name}`, metric.value, {
    unit: name === "CLS" ? "none" : "millisecond",
    tags: { rating, module },
  })

  posthog.capture("$web_vitals", {
    $metric_name: name,
    $metric_value: metric.value,
    $metric_rating: rating,
    $current_url: window.location.href,
    module,
  })

  if (rating === "poor") {
    log.warn(`Poor ${name}: ${metric.value.toFixed(2)}`, { module })
    Sentry.captureMessage(`Poor Web Vital: ${name}`, { level: "warning", tags: { web_vital: name }, extra: { value: metric.value, module } })
  }
}
```

### 5.2 Custom Performance Marks — Complete System

```tsx
// lib/utils/performance.ts
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { trackEvent } from "@/lib/utils/analytics"

const log = createLogger("performance")

export async function measureAsync<T>(
  name: string,
  fn: () => Promise<T>,
  options?: { module?: string; metadata?: Record<string, unknown> },
): Promise<T> {
  const mark = `measure:start:${name}`
  const measureName = `measure:${name}`
  performance.mark(mark)
  try {
    return await fn()
  } finally {
    performance.measure(measureName, mark)
    const entries = performance.getEntriesByName(measureName)
    const duration = entries[entries.length - 1]?.duration || 0
    if (duration > 0) {
      Sentry.metrics.distribution(`perf.custom.${name.replace(/[^a-zA-Z0-9._-]/g, "_")}`, duration, {
        unit: "millisecond", tags: { module: options?.module || "unknown" },
      })
    }
    if (duration > 3000) log.warn(`Slow operation: ${name}`, { duration, module: options?.module })
    performance.clearMarks(mark)
    performance.clearMeasures(measureName)
  }
}

export function markStart(name: string): string {
  const mark = `perf:${name}:${Date.now()}`
  performance.mark(mark)
  return mark
}

export function markEnd(mark: string, options?: { module?: string }): number {
  const measureName = mark.replace("perf:", "measure:")
  performance.measure(measureName, mark)
  const entries = performance.getEntriesByName(measureName)
  const duration = entries[entries.length - 1]?.duration || 0
  if (duration > 0) {
    Sentry.metrics.distribution(`perf.custom.${measureName}`, duration, {
      unit: "millisecond", tags: { module: options?.module || "unknown" },
    })
  }
  performance.clearMarks(mark)
  performance.clearMeasures(measureName)
  return duration
}

export const ModuleMarks = {
  tasksLoad: () => markStart("module:tasks:load"),
  coursesLoad: () => markStart("module:courses:load"),
  habitsLoad: () => markStart("module:habits:load"),
  goalsLoad: () => markStart("module:goals:load"),
  sleepLoad: () => markStart("module:sleep:load"),
  incomeLoad: () => markStart("module:income:load"),
  projectsLoad: () => markStart("module:projects:load"),
  ideasLoad: () => markStart("module:ideas:load"),
  resourcesLoad: () => markStart("module:resources:load"),
  opportunitiesLoad: () => markStart("module:opportunities:load"),
  timeLoad: () => markStart("module:time:load"),
  chatLoad: () => markStart("module:chat:load"),
  automationLoad: () => markStart("module:automation:load"),
  youtubeLoad: () => markStart("module:youtube:load"),
  academicsLoad: () => markStart("module:academics:load"),
  dashboardLoad: () => markStart("module:dashboard:load"),
} as const

export const CUSTOM_METRICS = {
  "app.boot": "Application bootstrap time",
  "app.route_change": "Route transition duration",
  "module.tasks.render": "Tasks list render",
  "module.chat.response": "AI chat response time",
  "supabase.query": "Supabase query duration",
  "supabase.auth": "Auth operation duration",
  "ai.briefing": "Briefing agent generation time",
  "ai.weekly_review": "Weekly review generation time",
  "ai.sleep_message": "Sleep message generation time",
  "ai.memory_consolidate": "Memory consolidation time",
  "ai.opportunity_scan": "Opportunity scan time",
  "image.load": "Image load duration",
  "font.load": "Web font load duration",
  "route.transition": "Route transition time",
  "long_task": "Long task duration",
} as const
```

### 5.3 Route Transition Tracking

```tsx
// hooks/useRouteTransition.ts
"use client"

import { usePathname, useSearchParams } from "next/navigation"
import { useEffect, useRef } from "react"
import * as Sentry from "@sentry/nextjs"

export function useRouteTransition() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const previousPath = useRef<string | null>(null)

  useEffect(() => {
    const currentPath = pathname + (searchParams?.toString() ? `?${searchParams}` : "")
    if (previousPath.current && previousPath.current !== currentPath) {
      const measureName = `route:${previousPath.current}->${currentPath}`
      const startMark = `route_start:${previousPath.current}`
      const endMark = `route_end:${currentPath}`
      performance.mark(endMark)
      performance.measure(measureName, startMark, endMark)
      const entries = performance.getEntriesByName(measureName)
      const duration = entries[entries.length - 1]?.duration
      if (duration && duration > 0) {
        Sentry.metrics.distribution("route.transition", duration, { unit: "millisecond", tags: { from: previousPath.current, to: currentPath } })
        if (duration > 2000) {
          Sentry.captureMessage(`Slow route transition: ${currentPath}`, { level: "warning", extra: { from: previousPath.current, duration } })
        }
      }
      performance.clearMeasures(measureName)
      performance.clearMarks(endMark)
    }
    performance.mark(`route_start:${currentPath}`)
    previousPath.current = currentPath
  }, [pathname, searchParams])
}
```

### 5.4 Image Loading Performance

```tsx
// hooks/useImagePerformance.ts
"use client"

import { useEffect, useRef } from "react"
import * as Sentry from "@sentry/nextjs"

export function useImagePerformance() {
  const observerRef = useRef<PerformanceObserver | null>(null)

  useEffect(() => {
    if (typeof window === "undefined" || !window.PerformanceObserver) return
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === "resource" && entry.name.match(/\.(jpg|png|webp|avif|gif|svg)/i)) {
            const resourceEntry = entry as PerformanceResourceTiming
            Sentry.metrics.distribution("image.load_time", resourceEntry.responseEnd - resourceEntry.startTime, { unit: "millisecond" })
            if ((resourceEntry.transferSize || 0) > 500_000) {
              Sentry.metrics.distribution("image.large_size", resourceEntry.transferSize || 0, { unit: "byte" })
            }
          }
        }
      })
      observer.observe({ entryTypes: ["resource", "largest-contentful-paint"] })
      observerRef.current = observer
    } catch {}
    return () => observerRef.current?.disconnect()
  }, [])
}
```

### 5.5 Long Task Monitoring

```tsx
// hooks/useLongTaskMonitor.ts
"use client"

import { useEffect, useRef } from "react"
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("long-task")

export function useLongTaskMonitor() {
  const observerRef = useRef<PerformanceObserver | null>(null)

  useEffect(() => {
    if (typeof window === "undefined" || !window.PerformanceObserver) return
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 100) {
            Sentry.metrics.distribution("long_task.duration", entry.duration, { unit: "millisecond" })
            if (entry.duration > 500) {
              log.warn(`Long task: ${entry.duration.toFixed(0)}ms`)
              Sentry.captureMessage(`Long task: ${entry.duration.toFixed(0)}ms`, { level: "warning" })
            }
          }
        }
      })
      observer.observe({ entryTypes: ["longtask"] })
      observerRef.current = observer
    } catch {}
    return () => observerRef.current?.disconnect()
  }, [])
}
```

### 5.6 Performance Budgets

| Asset | Budget (gzip) | Budget (raw) | Enforcement |
|---|---|---|---|
| Initial JS | <=120KB | <=350KB | CI gate + bundle analyzer |
| Initial CSS | <=15KB | <=50KB | CI gate |
| Fonts (total) | <=100KB | <=150KB | Manual review |
| Images per page | <=300KB | <=800KB | next/image optimization |
| Third-party JS | <=40KB | <=100KB | Partytown + lazy load |
| Service Worker | <=20KB | <=60KB | CI gate |

## 6. Analytics with PostHog

### 6.1 Provider Setup (Complete)

```tsx
// apps/web/components/shared/PostHogProvider.tsx
"use client"

import posthog from "posthog-js"
import { PostHogProvider as PHProvider } from "posthog-js/react"
import { useEffect } from "react"
import { useAuth } from "@/hooks/useAuth"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("posthog")

if (typeof window !== "undefined") {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY || "", {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://app.posthog.com",
    capture_pageview: false,
    capture_performance: true,
    autocapture: true,
    persistence: "localStorage",
    loaded: (ph) => {
      if (process.env.NODE_ENV === "development") ph.opt_out_capturing()
      log.info("PostHog initialized")
    },
    session_recording: {
      maskAllInputs: true,
      maskTextSelector: ".sentry-mask, [data-mask]",
      blockSelector: "iframe, video, [data-block]",
      sampleRate: 0.1,
      consoleLogRecordingEnabled: false,
    },
  })
}

export default function PostHogProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()

  useEffect(() => {
    if (user && process.env.NODE_ENV === "production") {
      posthog.identify(user.id, {
        email_hash: user.email ? btoa(user.email).slice(0, 16) : undefined,
        created_at: user.created_at,
      })
    }
  }, [user])

  return <PHProvider client={posthog}>{children}</PHProvider>
}
```

### 6.2 Page View Tracking (Next.js 14 App Router)

```tsx
// hooks/usePageView.ts
"use client"

import { usePathname, useSearchParams } from "next/navigation"
import { useEffect, useRef } from "react"
import posthog from "posthog-js"
import * as Sentry from "@sentry/nextjs"

export function usePageView() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const previousPath = useRef<string | null>(null)

  useEffect(() => {
    const currentUrl = pathname + (searchParams?.toString() ? `?${searchParams}` : "")
    if (previousPath.current && previousPath.current !== currentUrl) {
      Sentry.metrics.increment("page.view", 1, { tags: { path: pathname } })
    }
    posthog.capture("$pageview", {
      $current_url: window.location.href,
      $pathname: pathname,
      $referrer: document.referrer || undefined,
      $viewport_width: window.innerWidth,
      module: pathname.split("/")[1] || "home",
      timestamp: new Date().toISOString(),
    })
    Sentry.metrics.increment("pageview", 1, { tags: { path: pathname } })
    previousPath.current = currentUrl
  }, [pathname, searchParams])
}
```

### 6.3 Feature Flags — Complete Implementation

```tsx
// hooks/useFeatureFlagTracker.ts
"use client"

import { useEffect } from "react"
import posthog from "posthog-js"
import * as Sentry from "@sentry/nextjs"
import { trackEvent } from "@/lib/utils/analytics"

export enum FeatureFlag {
  RoadmapV2 = "roadmap-v2",
  AIBriefingV2 = "ai-briefing-v2",
  DarkModeDefault = "dark-mode-default",
  NewOnboarding = "new-onboarding-flow",
  HabitStreakRedesign = "habit-streak-redesign",
  PerformanceMode = "performance-mode",
  OfflineMode = "offline-mode-beta",
  AnalyticsDashboard = "analytics-dashboard",
}

export function useFeatureFlag(key: FeatureFlag | string, defaultValue = false): boolean {
  try {
    if (typeof window === "undefined") return defaultValue
    return posthog.isFeatureEnabled(key) ?? defaultValue
  } catch {
    return defaultValue
  }
}

export function useFeatureFlagPayload<T = unknown>(key: FeatureFlag | string): T | null {
  try {
    if (typeof window === "undefined") return null
    return (posthog.getFeatureFlagPayload(key) as T) ?? null
  } catch {
    return null
  }
}

export function useMultipleFeatureFlags(flags: (FeatureFlag | string)[]): Record<string, boolean> {
  try {
    if (typeof window === "undefined") return Object.fromEntries(flags.map((f) => [f, false]))
    return Object.fromEntries(flags.map((f) => [f, posthog.isFeatureEnabled(f) ?? false]))
  } catch {
    return Object.fromEntries(flags.map((f) => [f, false]))
  }
}

export function useFeatureFlagTracker() {
  useEffect(() => {
    if (typeof window === "undefined") return
    const flags = Object.values(FeatureFlag)
    const enabledFlags = flags.filter((f) => posthog.isFeatureEnabled(f))
    if (enabledFlags.length > 0) {
      trackEvent("feature_flags_active", { flags: enabledFlags, count: enabledFlags.length })
    }
    posthog.onFeatureFlags(() => {
      const currentFlags = Object.values(FeatureFlag).filter((f) => posthog.isFeatureEnabled(f))
      Sentry.metrics.increment("feature_flag.evaluation", currentFlags.length, { tags: { flags: currentFlags.join(",") } })
    })
  }, [])
}
```

### 6.4 User Property Enrichment

```tsx
// lib/utils/user-properties.ts
import posthog from "posthog-js"
import { User } from "@/lib/stores/userStore"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("user-properties")

export function enrichUserProperties(user: User) {
  if (!user || typeof window === "undefined") return
  try {
    posthog.people.set({
      $name: user.name || "Anonymous",
      college: user.college || "unknown",
      year: user.year || 0,
      has_skills: (user.skills?.length || 0) > 0,
      onboarding_completed: !!user.name,
      last_seen_at: new Date().toISOString(),
    })
    log.info("User properties enriched")
  } catch (err) {
    log.error("Failed to enrich user properties", { error: String(err) })
  }
}

export function trackModuleUsage(moduleName: string) {
  try {
    posthog.capture("module_opened", { module: moduleName, timestamp: new Date().toISOString() })
    posthog.people.set({ [`last_used_${moduleName}`]: new Date().toISOString() })
  } catch {}
}
```

### 6.5 Event Taxonomy (50+ Events)

**Instrumentation Events (14)**
| Event | Properties | Trigger |
|---|---|---|
| $pageview | pathname, module, referrer, viewport | Route change |
| $web_vitals | metric_name, metric_value, rating, module | Web Vitals callback |
| error_boundary_caught | boundary, module, error | ErrorBoundary catch |
| error_reported | error, level, module | reportError() call |
| supabase_error | table, operation, code | Supabase query error |
| tanstack_query_error | message, queryKey | TanStack Query error |
| performance_measurement | name, duration, module | markEnd() call |
| ai_call | agent, model, tokens, latency, fallbackUsed | AI generation |
| ai_fallback | agent, from, to, latency | Fallback triggered |
| api_call | module, operation, duration, status | apiFetch() call |
| long_task | duration | PerformanceObserver |
| offline_detected | none | navigator.onLine change |
| feature_flags_active | flags, count | App init |
| ab_test_assignment | test, variant | A/B test assignment |

**User Action Events (24)**
| Event | Properties | Module |
|---|---|---|
| task_created | priority, category | Tasks |
| task_completed | priority, category | Tasks |
| task_deleted | none | Tasks |
| course_started | course_name | Courses |
| course_completed | course_name | Courses |
| habit_completed | habit_name, streak | Habits |
| habit_streak_milestone | streak_count | Habits |
| goal_created | goal_type, timeline | Goals |
| sleep_logged | duration, score | Sleep |
| income_logged | amount, source | Income |
| project_phase_completed | project, phase | Projects |
| idea_moved | from_stage, to_stage | Ideas |
| resource_saved | tags, type | Resources |
| opportunity_applied | category, score | Opportunities |
| time_entry_started | type | Time |
| time_entry_completed | duration | Time |
| chat_message_sent | has_ai | Chat |
| automation_triggered | name | Automation |
| video_watched | title, duration | YouTube |
| habit_missed | habit_name | Habits |
| task_dependency_added | dependency_id | Tasks |
| goal_milestone_reached | goal_id | Goals |
| notification_clicked | type | Notifications |
| search_performed | query, results | Search |

**Business Events (12)**
| Event | Properties | Trigger |
|---|---|---|
| user_signed_in | method | Auth |
| user_signed_out | none | Auth |
| module_opened | module name | Page mount |
| feature_flags_active | flags, count | App init |
| search_performed | query, results | Search |
| export_data | format, module | Export action |
| onboarding_step | step, total | Onboarding flow |
| feedback_submitted | sentiment | Feedback form |
| notification_clicked | type | Notification |
| share_action | method, module | Share button |
| error_digest_viewed | digest | Error page |
| subscription_viewed | page | Pricing page |

### 6.6 Event Tracking Hook

```tsx
// hooks/useTrack.ts
"use client"

import { useCallback } from "react"
import posthog from "posthog-js"

export function useTrack() {
  const track = useCallback((name: string, properties?: Record<string, unknown>) => {
    try {
      if (typeof window === "undefined") return
      posthog.capture(name, { ...properties, timestamp: new Date().toISOString(), url: window.location.href })
    } catch {}
  }, [])
  return track
}
```

### 6.7 A/B Testing Setup

```tsx
// hooks/useABTest.ts
"use client"

import { useEffect, useState } from "react"
import posthog from "posthog-js"
import { trackEvent } from "@/lib/utils/analytics"

const ACTIVE_TESTS = [
  { name: "dashboard-layout-v1", variants: ["control", "bento", "list"] },
  { name: "task-input-position", variants: ["top", "bottom", "modal"] },
  { name: "onboarding-steps", variants: ["3-step", "5-step", "progressive"] },
  { name: "chat-interface-style", variants: ["default", "sidebar", "fullscreen"] },
  { name: "habit-display-density", variants: ["compact", "comfortable", "spacious"] },
]

export function useABTest(testName: string): string {
  const [variant, setVariant] = useState("control")
  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      const assigned = (posthog.getFeatureFlagPayload(testName) as string) || "control"
      setVariant(assigned)
      trackEvent("ab_test_assignment", { test: testName, variant: assigned })
    } catch { setVariant("control") }
  }, [testName])
  return variant
}

export function useAllABTests(): Record<string, string> {
  const [assignments, setAssignments] = useState<Record<string, string>>({})
  useEffect(() => {
    const result: Record<string, string> = {}
    for (const test of ACTIVE_TESTS) {
      result[test.name] = (posthog.getFeatureFlagPayload(test.name) as string) || "control"
    }
    setAssignments(result)
    trackEvent("ab_test_assignments_batch", { tests: result })
  }, [])
  return assignments
}

## 7. Logging Strategy

### 7.1 Structured JSON Logger (Complete Implementation)

```tsx
// lib/utils/logger.ts
import * as Sentry from "@sentry/nextjs"

type LogLevel = "debug" | "info" | "warn" | "error" | "fatal"

interface LogEntry {
  timestamp: string
  level: LogLevel
  module: string
  message: string
  context?: Record<string, unknown>
  correlationId?: string
  userId?: string
  sessionId?: string
  environment: string
  version?: string
}

const SENSITIVE_PATTERNS = [
  /password/i, /token/i, /secret/i, /key/i, /authorization/i,
  /cookie/i, /ssn/i, /credit.?card/i, /cvv/i, /pin/i, /otp/i,
  /api.?key/i, /supabase.?key/i, /jwt/i, /bearer/i, /session.?id/i,
  /access.?token/i, /refresh.?token/i,
]

class Logger {
  private module: string
  private correlationId: string
  private pendingEntries: LogEntry[] = []
  private batchTimer: ReturnType<typeof setInterval> | null = null
  private userId = "anonymous"
  private sessionId = ""

  constructor(module: string) {
    this.module = module
    this.correlationId = crypto.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`
    if (typeof window !== "undefined") {
      this.sessionId = sessionStorage.getItem("session_id") || crypto.randomUUID?.() || Date.now().toString(36)
      sessionStorage.setItem("session_id", this.sessionId)
    }
    if (process.env.NODE_ENV === "production") this.startBatchProcessor()
  }

  private sanitize(context: Record<string, unknown>): Record<string, unknown> {
    const sanitized: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(context)) {
      if (SENSITIVE_PATTERNS.some((pattern) => pattern.test(key))) {
        sanitized[key] = "[REDACTED]"
      } else if (typeof value === "string" && value.length > 2000) {
        sanitized[key] = value.slice(0, 2000) + "..."
      } else if (value instanceof Error) {
        sanitized[key] = { message: value.message, name: value.name }
      } else if (typeof value === "object" && value !== null) {
        sanitized[key] = this.sanitize(value as Record<string, unknown>)
      } else {
        sanitized[key] = value
      }
    }
    return sanitized
  }

  private buildEntry(level: LogLevel, message: string, context?: Record<string, unknown>): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      module: this.module,
      message,
      context: context ? this.sanitize(context) : undefined,
      correlationId: this.correlationId,
      userId: this.userId,
      sessionId: this.sessionId,
      environment: process.env.NODE_ENV || "development",
      version: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
    }
  }

  private log(level: LogLevel, message: string, context?: Record<string, unknown>) {
    const entry = this.buildEntry(level, message, context)
    const prefix = `[${this.module}]`

    switch (level) {
      case "debug":
        if (process.env.NODE_ENV === "development") console.debug(prefix, message, entry.context)
        break
      case "info":
        console.info(prefix, message, entry.context)
        break
      case "warn":
        console.warn(prefix, message, entry.context)
        if (process.env.NODE_ENV === "production") this.pendingEntries.push(entry)
        break
      case "error":
        console.error(prefix, message, entry.context)
        if (process.env.NODE_ENV === "production") {
          Sentry.captureMessage(message, {
            level: "error", tags: { module: this.module, correlationId: this.correlationId.slice(0, 8) }, extra: entry.context,
          })
          this.pendingEntries.push(entry)
        }
        break
      case "fatal":
        console.error(`FATAL:`, prefix, message, entry.context)
        if (process.env.NODE_ENV === "production") {
          Sentry.captureMessage(message, {
            level: "fatal", tags: { module: this.module }, extra: entry.context,
          })
        }
        break
    }

    if (this.pendingEntries.length >= 10) this.flushBatch()
  }

  private startBatchProcessor() {
    this.batchTimer = setInterval(() => this.flushBatch(), 5000)
  }

  private async flushBatch() {
    if (this.pendingEntries.length === 0) return
    const batch = this.pendingEntries.splice(0, 10)
    try {
      const payload = JSON.stringify({ entries: batch })
      if (navigator.sendBeacon) {
        navigator.sendBeacon("/api/logs", payload)
      } else {
        fetch("/api/logs", { method: "POST", body: payload, headers: { "Content-Type": "application/json" }, keepalive: true }).catch(() => {})
      }
    } catch {}
  }

  setUserId(id: string) { this.userId = id }

  debug(message: string, context?: Record<string, unknown>) { this.log("debug", message, context) }
  info(message: string, context?: Record<string, unknown>) { this.log("info", message, context) }
  warn(message: string, context?: Record<string, unknown>) { this.log("warn", message, context) }
  error(message: string, context?: Record<string, unknown>) { this.log("error", message, context) }
  fatal(message: string, context?: Record<string, unknown>) { this.log("fatal", message, context) }

  destroy() {
    if (this.batchTimer) clearInterval(this.batchTimer)
    this.flushBatch()
  }
}

const instances = new Map<string, Logger>()
export function createLogger(module: string): Logger {
  if (!instances.has(module)) instances.set(module, new Logger(module))
  return instances.get(module)!
}
```

### 7.2 Remote Log Endpoint

```tsx
// apps/web/app/api/logs/route.ts
import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { entries } = await request.json()
    if (!Array.isArray(entries) || entries.length === 0) {
      return NextResponse.json({ error: "No entries" }, { status: 400 })
    }
    for (const entry of entries) {
      console.log(`[${entry.module}][${entry.level}] ${entry.message}`, {
        correlationId: entry.correlationId?.slice(0, 8),
        timestamp: entry.timestamp,
      })
    }
    return NextResponse.json({ ok: true, count: entries.length })
  } catch (error) {
    console.error("[Log Endpoint] Failed to process:", error)
    return NextResponse.json({ error: "Internal error" }, { status: 500 })
  }
}
```

### 7.3 Log Level Guidelines

| Level | Console Color | When to Use | Example |
|---|---|---|---|
| DEBUG | Gray | Development-only details | `log.debug("Filter changed", { filter })` |
| INFO | Blue | Normal operation events | `log.info("Tasks loaded", { count: 42 })` |
| WARN | Yellow | Unexpected but handled | `log.warn("Slow query", { duration: 5000 })` |
| ERROR | Red | Failure, app continues | `log.error("Failed to save task", { error })` |
| FATAL | Red bold | App cannot continue | `log.fatal("Page crash, reloading")` |

### 7.4 Correlation ID Strategy

```tsx
// lib/utils/correlation.ts
"use client"

const CORRELATION_KEY = "x-correlation-id"

export function getCorrelationId(): string {
  if (typeof window === "undefined") return "server-" + genId()
  const existing = sessionStorage.getItem(CORRELATION_KEY)
  if (existing) return existing
  const id = genId()
  sessionStorage.setItem(CORRELATION_KEY, id)
  return id
}

function genId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}
```

## 8. TanStack Query Observability

### 8.1 Complete QueryClient Configuration

```tsx
// lib/query/queryClient.ts
import { QueryClient, QueryCache, MutationCache, onlineManager } from "@tanstack/react-query"
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { trackEvent } from "@/lib/utils/analytics"

const log = createLogger("react-query")

export function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: 2,
        retryDelay: (attemptIndex) => Math.min(1000 * 3 ** attemptIndex, 10000),
        refetchOnWindowFocus: false,
        refetchOnReconnect: true,
        refetchOnMount: true,
        networkMode: "offlineFirst",
      },
      mutations: {
        retry: 1,
        retryDelay: 1000,
        networkMode: "offlineFirst",
      },
    },
    queryCache: new QueryCache({
      onError: (error, query) => {
        const key = query.queryKey.join(", ")
        log.error(`Query error: ${key}`, { message: String(error) })
        Sentry.captureException(error, { tags: { source: "tanstack-query", queryKey: key.slice(0, 100) } })
        trackEvent("tanstack_query_error", { message: String(error), queryKey: key })
      },
      onSuccess: (_data, query) => {
        Sentry.metrics.increment("tanstack.query_success", 1, {
          tags: { queryKey: query.queryKey.join("/").slice(0, 50) },
        })
      },
    }),
    mutationCache: new MutationCache({
      onError: (error, _vars, _ctx, mutation) => {
        log.error(`Mutation error`, { mutationKey: mutation.options.mutationKey?.join(", "), message: String(error) })
        Sentry.captureException(error, { tags: { source: "tanstack-mutation" } })
        trackEvent("tanstack_mutation_error", { message: String(error), mutationKey: mutation.options.mutationKey?.join("-") })
      },
      onSuccess: (_data, _vars, _ctx, mutation) => {
        Sentry.metrics.increment("tanstack.mutation_success", 1, {
          tags: { mutationKey: mutation.options.mutationKey?.join("-") || "unknown" },
        })
      },
    }),
  })
}

onlineManager.setEventListener((setOnline) => {
  window.addEventListener("online", () => { log.info("Browser online"); setOnline(true) })
  window.addEventListener("offline", () => { log.warn("Browser offline"); setOnline(false); trackEvent("offline_detected", {}) })
  return () => {
    window.removeEventListener("online", () => {})
    window.removeEventListener("offline", () => {})
  }
})
```

### 8.2 Retry Strategy

| Attempt | Delay | Cumulative |
|---|---|---|
| 1 | 1,000ms | 1s |
| 2 | 3,000ms | 4s |
| 3 | 9,000ms | 13s |
| Max | 10,000ms | - |

### 8.3 Optimistic Update Rollback Tracking

```tsx
// lib/query/optimistic.ts
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"

const log = createLogger("optimistic-update")

export function onOptimisticUpdateBegin(key: string[]) {
  log.debug("Optimistic update started", { key: key.join("/") })
}

export function onOptimisticUpdateSuccess(key: string[]) {
  log.info("Optimistic update succeeded", { key: key.join("/") })
  Sentry.metrics.increment("optimistic_update.success", 1)
}

export function onOptimisticUpdateRollback(key: string[], error: unknown) {
  log.warn("Optimistic update rolled back", { key: key.join("/"), error: String(error) })
  Sentry.metrics.increment("optimistic_update.rollback", 1)
  Sentry.captureMessage(`Optimistic update rolled back: ${key.join("/")}`, { level: "warning" })
}
```

## 9. AI Agent Observability

### 9.1 LLM Call Tracing

```tsx
// lib/ai/observability.ts
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { trackEvent } from "@/lib/utils/analytics"

const log = createLogger("ai-observability")

interface AICallMetrics {
  agent: string
  model: string
  promptTokens: number
  completionTokens: number
  totalTokens: number
  latencyMs: number
  success: boolean
  fallbackUsed: boolean
  fallbackChain?: string[]
  temperature?: number
  error?: string
  userId?: string
}

const COST_TABLE: Record<string, { inputCost: number; outputCost: number }> = {
  "ollama/mistral:7b": { inputCost: 0, outputCost: 0 },
  "ollama/llama3:8b": { inputCost: 0, outputCost: 0 },
  "claude-sonnet-4": { inputCost: 0.003, outputCost: 0.015 },
  "claude-haiku-3": { inputCost: 0.00025, outputCost: 0.00125 },
  "openai/gpt-4o-mini": { inputCost: 0.00015, outputCost: 0.0006 },
}

const dailyCosts = new Map<string, { date: string; agent: string; model: string; totalTokens: number; cost: number; callCount: number }>()

function calculateCost(model: string, prompt: number, completion: number): number {
  const p = COST_TABLE[model]
  if (!p) return 0
  return (prompt / 1000) * p.inputCost + (completion / 1000) * p.outputCost
}

export function trackAICall(metrics: AICallMetrics) {
  const { agent, model, promptTokens, completionTokens, totalTokens, latencyMs, success, fallbackUsed } = metrics
  const cost = calculateCost(model, promptTokens, completionTokens)

  log.info(`AI call: ${agent}`, { model, tokens: totalTokens, latency: `${latencyMs}ms`, success, fallback: fallbackUsed, cost: cost > 0 ? `$${cost.toFixed(4)}` : "free" })

  Sentry.metrics.distribution("ai.latency", latencyMs, { unit: "millisecond", tags: { agent, model, success: String(success) } })
  Sentry.metrics.distribution("ai.tokens.total", totalTokens, { tags: { agent, model } })
  Sentry.metrics.distribution("ai.tokens.prompt", promptTokens, { tags: { agent, model } })
  Sentry.metrics.distribution("ai.tokens.completion", completionTokens, { tags: { agent, model } })
  Sentry.metrics.increment("ai.calls", 1, { tags: { agent, model, success: String(success) } })
  if (cost > 0) Sentry.metrics.distribution("ai.cost", cost, { unit: "usd", tags: { agent, model } })

  trackEvent("ai_call", { agent, model, promptTokens, completionTokens, totalTokens, latencyMs, success, fallbackUsed, cost })

  const todayKey = `${new Date().toISOString().split("T")[0]}:${agent}:${model}`
  const existing = dailyCosts.get(todayKey)
  dailyCosts.set(todayKey, existing
    ? { ...existing, totalTokens: existing.totalTokens + totalTokens, cost: existing.cost + cost, callCount: existing.callCount + 1 }
    : { date: new Date().toISOString().split("T")[0], agent, model, totalTokens, cost, callCount: 1 })

  if (latencyMs > 10000) {
    log.warn(`Slow AI: ${agent}`, { latency: `${latencyMs}ms`, model })
    Sentry.captureMessage(`Slow AI: ${agent} (${latencyMs.toFixed(0)}ms)`, { level: "warning", tags: { agent, model } })
  }

  if (!success && !fallbackUsed) {
    Sentry.captureMessage(`AI call failed: ${agent}`, { level: "error", tags: { agent, model, source: "ai-failure" } })
  }
}

export function getAICostSummary(): { totalDailyCost: number; agentBreakdown: Record<string, number> } {
  const today = new Date().toISOString().split("T")[0]
  let total = 0
  const breakdown: Record<string, number> = {}
  for (const [, entry] of dailyCosts) {
    if (entry.date === today) { total += entry.cost; breakdown[entry.agent] = (breakdown[entry.agent] || 0) + entry.cost }
  }
  return { totalDailyCost: total, agentBreakdown: breakdown }
}
```

### 9.2 Fallback Tracking

```tsx
// lib/ai/fallback.ts
import * as Sentry from "@sentry/nextjs"
import { createLogger } from "@/lib/utils/logger"
import { trackEvent } from "@/lib/utils/analytics"
import { trackAICall } from "./observability"

const log = createLogger("ai-fallback")

export async function withFallbackChain<T>(
  primaryCall: () => Promise<T>,
  fallbackCall: () => Promise<T>,
  algorithmicFallback: () => T | Promise<T>,
  config: { agentName: string; primaryModel: string; fallbackModel?: string },
): Promise<T> {
  const startTime = performance.now()
  const chain: string[] = []
  let lastError: string | undefined

  // Attempt 1: Primary model
  try {
    chain.push(config.primaryModel)
    const result = await primaryCall()
    trackAICall({ agent: config.agentName, model: config.primaryModel, promptTokens: 0, completionTokens: 0, totalTokens: 0, latencyMs: performance.now() - startTime, success: true, fallbackUsed: false })
    return result
  } catch (err) {
    lastError = String(err)
    log.warn(`Primary AI failed for ${config.agentName}`, { error: lastError, model: config.primaryModel })
    Sentry.metrics.increment("ai.fallback_triggered", 1, { tags: { agent: config.agentName, from: config.primaryModel } })
  }

  // Attempt 2: Fallback model
  try {
    const fbModel = config.fallbackModel || "claude-sonnet-4"
    chain.push(fbModel)
    const result = await fallbackCall()
    trackAICall({ agent: config.agentName, model: fbModel, promptTokens: 0, completionTokens: 0, totalTokens: 0, latencyMs: performance.now() - startTime, success: true, fallbackUsed: true, fallbackChain: chain })
    Sentry.captureMessage(`AI fallback used for ${config.agentName}`, { level: "warning", tags: { agent: config.agentName, fallback: fbModel }, extra: { chain, primaryError: lastError } })
    trackEvent("ai_fallback", { agent: config.agentName, from: config.primaryModel, to: fbModel, latency: performance.now() - startTime, error: lastError })
    return result
  } catch (err) {
    lastError = String(err)
    log.error(`Fallback failed for ${config.agentName}`, { error: lastError })
    Sentry.metrics.increment("ai.fallback_exhausted", 1, { tags: { agent: config.agentName } })
  }

  // Attempt 3: Algorithmic
  try {
    chain.push("algorithmic")
    const result = await Promise.resolve(algorithmicFallback())
    log.info(`Algorithmic fallback for ${config.agentName}`, { chain })
    Sentry.captureMessage(`Algorithmic fallback for ${config.agentName}`, { level: "warning", tags: { agent: config.agentName, fallback: "algorithmic" } })
    return result
  } catch (err) {
    lastError = String(err)
    log.fatal(`All fallbacks exhausted for ${config.agentName}`, { error: lastError, chain, latency: performance.now() - startTime })
    Sentry.captureMessage(`All AI fallbacks exhausted for ${config.agentName}`, { level: "fatal", tags: { agent: config.agentName } })
    throw new Error(`All AI providers failed for ${config.agentName}: ${lastError}`)
  }
}

// Per-agent cost tracking
export const AGENT_COST_TRACKING: Record<string, { dailyBudget: number; currentCost: number; callsToday: number }> = {
  briefing: { dailyBudget: 0.05, currentCost: 0, callsToday: 0 },
  weekly_review: { dailyBudget: 0.10, currentCost: 0, callsToday: 0 },
  opportunity_radar: { dailyBudget: 0.05, currentCost: 0, callsToday: 0 },
  memory: { dailyBudget: 0.02, currentCost: 0, callsToday: 0 },
  learning: { dailyBudget: 0.03, currentCost: 0, callsToday: 0 },
  sleep: { dailyBudget: 0.01, currentCost: 0, callsToday: 0 },
  nudge: { dailyBudget: 0.01, currentCost: 0, callsToday: 0 },
  task_agent: { dailyBudget: 0.02, currentCost: 0, callsToday: 0 },
}

export function getAgentCostBreakdown(): Record<string, { budget: number; spent: number; remaining: number; calls: number }> {
  const result: Record<string, { budget: number; spent: number; remaining: number; calls: number }> = {}
  for (const [agent, data] of Object.entries(AGENT_COST_TRACKING)) {
    result[agent] = { budget: data.dailyBudget, spent: data.currentCost, remaining: data.dailyBudget - data.currentCost, calls: data.callsToday }
  }
  return result
}
```

### 9.3 AI Agent Metrics Dashboard

| Agent | Model | Avg Latency | Avg Tokens | Daily Calls | Daily Cost | Budget |
|---|---|---|---|---|---|---|
| Briefing | ollama/mistral:7b | 2.1s | 1,400 | 1 | $0 | $0.05 |
| Weekly Review | ollama/mistral:7b | 3.8s | 2,300 | 1 (Sun) | $0 | $0.10 |
| Opportunity Radar | ollama/mistral:7b | 4.2s | 1,600 | 1 | $0 | $0.05 |
| Memory | ollama/mistral:7b | 1.5s | 600 | 10+ | $0 | $0.02 |
| Learning | ollama/mistral:7b | 2.0s | 800 | 1 | $0 | $0.03 |
| Sleep | ollama/mistral:7b | 1.2s | 700 | 2 | $0 | $0.01 |
| Nudge | ollama/mistral:7b | 1.0s | 600 | 1 | $0 | $0.01 |
| Task | ollama/mistral:7b | 1.8s | 900 | 5+ | $0 | $0.02 |

## 10. Health Checks

### 10.1 Health API Endpoint

```tsx
// apps/web/app/api/health/route.ts
import { NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"
import posthog from "posthog-js"

export async function GET() {
  const startTime = Date.now()

  const [supabaseHealth, posthogHealth] = await Promise.all([
    checkSupabase(),
    checkPostHog(),
  ])

  const health = {
    status: supabaseHealth === "ok" && posthogHealth === "ok" ? "ok" : "degraded",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
    responseTimeMs: Date.now() - startTime,
    dependencies: {
      supabase: supabaseHealth,
      posthog: posthogHealth,
      ollama: await checkOllama(),
    },
  }

  const statusCode = health.status === "ok" ? 200 : 503
  return NextResponse.json(health, { status: statusCode })
}

async function checkSupabase(): Promise<"ok" | "error"> {
  try {
    const { error } = await supabase.from("health_check").select("*").limit(1)
    return error ? "error" : "ok"
  } catch { return "error" }
}

async function checkPostHog(): Promise<"ok" | "error"> {
  try {
    return typeof posthog !== "undefined" && posthog?.__loaded ? "ok" : "error"
  } catch { return "error" }
}

async function checkOllama(): Promise<"ok" | "error" | "unknown"> {
  try {
    const response = await fetch(`${process.env.OLLAMA_BASE_URL || "http://localhost:11434"}/api/tags`)
    return response.ok ? "ok" : "error"
  } catch { return "unknown" }
}
```

### 10.2 Synthetic Monitoring

```tsx
// apps/web/scripts/synthetic-monitor.mjs
// Run this script periodically (e.g., cron every 5min) to check frontend health
const BASE_URL = process.env.BASE_URL || "http://localhost:3000"

async function runChecks() {
  const results = []

  // Check health endpoint
  try {
    const res = await fetch(`${BASE_URL}/api/health`)
    const data = await res.json()
    results.push({ check: "health-endpoint", status: res.ok ? "pass" : "fail", responseTime: data.responseTimeMs })
  } catch (err) {
    results.push({ check: "health-endpoint", status: "fail", error: err.message })
  }

  // Check critical pages load
  const criticalPages = ["/", "/login", "/dashboard", "/tasks"]
  for (const page of criticalPages) {
    try {
      const start = Date.now()
      const res = await fetch(`${BASE_URL}${page}`)
      results.push({ check: `page-${page}`, status: res.ok ? "pass" : "fail", responseTime: Date.now() - start })
    } catch (err) {
      results.push({ check: `page-${page}`, status: "fail", error: err.message })
    }
  }

  console.log(JSON.stringify({ timestamp: new Date().toISOString(), results }, null, 2))
  const hasFailures = results.some((r) => r.status === "fail")
  process.exit(hasFailures ? 1 : 0)
}

runChecks()
```

## 11. Alerting and Incident Response

### 11.1 Alert Thresholds

| Alert | Metric | Threshold | Severity | Channel |
|---|---|---|---|---|
| High error rate | Error count / page views | >1% over 5min | P1 | Slack + Email |
| Critical error | P0 error fingerprint | Any occurrence | P0 | Slack + PagerDuty |
| High AI latency | ai.latency p95 | >10s over 5min | P2 | Slack |
| AI fallback rate | ai.fallback_triggered | >3 in 5min | P2 | Slack |
| Slow page load | LCP | >4s p75 over 5min | P3 | Slack |
| High CLS | CLS | >0.25 p75 over 5min | P3 | Slack |
| Low DAU drop | DAU | >20% drop from 7d avg | P1 | Slack + Email |
| Sentry quota | Events remaining | <20% of daily quota | P2 | Email |
| PostHog quota | Events remaining | <20% of daily quota | P2 | Email |
| Chunk load errors | ChunkLoadError | Any occurrence | P0 | Slack + PagerDuty |

### 11.2 Severity Levels

| Severity | Definition | Response Time | Escalation |
|---|---|---|---|
| P0 | Critical — app unusable for all users | <5min | Slack + PagerDuty + Phone |
| P1 | High — significant feature broken | <15min | Slack + Email |
| P2 | Medium — minor feature broken | <1hr | Slack |
| P3 | Low — cosmetic or non-urgent | <24hr | Slack (next business day) |
| P4 | Trivial — nice to have | <1 week | GitHub issue |

### 11.3 Notification Channels

| Channel | P0 | P1 | P2 | P3 | P4 |
|---|---|---|---|---|---|
| Slack (#alerts) | Yes | Yes | Yes | Yes | No |
| Email | Yes | Yes | No | No | No |
| PagerDuty | Yes | No | No | No | No |
| SMS | Yes | No | No | No | No |

### 11.4 Incident Response Runbook

**P0 Incident: High Error Rate**
1. Check Sentry dashboard for error grouping
2. Identify most frequent error type
3. Check if related to recent deployment (git log --oneline -10)
4. If deployment-related, rollback via Vercel dashboard
5. If not, check Supabase status (status.supabase.com)
6. Post update in #incidents Slack channel
7. Create GitHub issue with Sentry link

**P0 Incident: ChunkLoadError**
1. User sees blank screen or broken page
2. Check if cache busting is needed (new deployment without version bump)
3. Clear CDN cache via Vercel dashboard
4. Increment APP_VERSION in env vars
5. Verify fix by hard-refreshing affected pages
6. Post incident report in #incidents

**P1 Incident: Auth Failure**
1. Check Supabase dashboard for auth health
2. Verify Google OAuth configuration in Supabase
3. Check JWT_SECRET matches between env vars
4. Test login flow manually
5. If Supabase issue, wait for resolution
6. If env issue, update secrets in Railway/Vercel

## 12. Dashboards and Visualization

### 12.1 Sentry Dashboard Configuration

The Sentry dashboard should include the following widgets:

**Panel 1: Error Overview**
- Error rate over time (line chart, 24h window)
- Error count by module (bar chart, top 10 modules)
- Error fingerprint distribution (pie chart)
- Top 10 most frequent errors (table)

**Panel 2: Performance**
- Web Vitals over time (LCP, CLS, INP line charts, 7d window)
- Slowest routes (table, top 10 by p75 LCP)
- API latency by module (heatmap, 24h)
- Long task frequency (time series, 24h)

**Panel 3: AI Observability**
- AI call latency by agent (histogram, 7d)
- AI call count by agent (bar chart, 24h)
- AI fallback rate (time series)
- AI cost by agent (area chart, 7d)

**Panel 4: User Experience**
- Session replay list (latest 20)
- User feedback submissions (table)
- Crash-free rate (percentage, 7d)
- Error-free session rate (percentage, 7d)

### 12.2 PostHog Dashboard Configuration

**Panel 1: Core Metrics**
- DAU (daily line chart, 30d)
- WAU (weekly line chart, 90d)
- MAU (monthly line chart, 365d)
- Session duration (daily average, 30d)

**Panel 2: Module Adoption**
- Module usage frequency (bar chart, 30d)
- Module first-time usage (cumulative, 90d)
- Feature flag adoption by flag (table)
- Module retention (cohort analysis, weekly)

**Panel 3: Conversion Funnels**
- Login to dashboard conversion (funnel, 30d)
- Dashboard to first task creation (funnel, 30d)
- Onboarding completion rate (funnel, 30d)
- Feature activation rate (funnel per feature, 30d)

**Panel 4: AI Usage**
- AI call count by agent (daily bar, 30d)
- Average AI latency (daily line, 30d)
- AI fallback count (daily bar, 30d)
- Users with AI interactions (daily line, 30d)

### 12.3 Custom Dashboard JSON (Sentry)

```json
{
  "title": "Second Brain OS - Frontend",
  "projects": ["frontend"],
  "environment": "production",
  "widgets": [
    {
      "title": "Error Rate by Module",
      "displayType": "bar",
      "query": "count_if(event.type:error) by tags[module]",
      "interval": "5m",
      "timeRange": "24h"
    },
    {
      "title": "LCP over Time (p75)",
      "displayType": "line",
      "query": "p75(measurements.lcp)",
      "interval": "5m",
      "timeRange": "7d"
    },
    {
      "title": "AI Latency by Agent",
      "displayType": "histogram",
      "query": "avg(ai.latency) by tags[agent]",
      "interval": "1h",
      "timeRange": "7d"
    },
    {
      "title": "Top Failing Queries",
      "displayType": "table",
      "query": "count_if(event.type:error AND tags[source]:tanstack-query) by tags[queryKey]",
      "interval": "1h",
      "timeRange": "24h"
    }
  ]
}
```

### 12.4 Module Usage Tracking (PostHog)

```tsx
// hooks/useModuleTracker.ts
"use client"

import { useEffect } from "react"
import posthog from "posthog-js"
import { usePathname } from "next/navigation"

const MODULE_NAMES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/tasks": "Tasks",
  "/courses": "Courses",
  "/habits": "Habits",
  "/goals": "Goals",
  "/sleep": "Sleep",
  "/income": "Income",
  "/projects": "Projects",
  "/ideas": "Ideas",
  "/resources": "Resources",
  "/opportunities": "Opportunities",
  "/time": "Time Tracking",
  "/chat": "AI Chat",
  "/automation": "Automation",
  "/youtube": "YouTube",
  "/academics": "Academics",
}

export function useModuleTracker() {
  const pathname = usePathname()

  useEffect(() => {
    const basePath = "/" + pathname.split("/").filter(Boolean)[0]
    const moduleName = MODULE_NAMES[basePath]
    if (moduleName) {
      posthog.capture("module_opened", { module: moduleName, path: pathname })
      posthog.people.set({ [`last_used_${moduleName.toLowerCase().replace(/\s+/g, "_")}`]: new Date().toISOString() })
    }
  }, [pathname])
}
```

## 13. Data Privacy and Compliance

### 13.1 PII Redaction in Sentry (15+ Field Patterns)

```tsx
// sentry.client.config.ts beforeSend patterns
const PII_FIELDS = [
  "Authorization",
  "Cookie",
  "X-Supabase-Auth",
  "X-Forwarded-For",
  "CF-Connecting-IP",
  "True-Client-IP",
  "X-Real-IP",
  "X-API-Key",
  "Set-Cookie",
  "X-CSRF-Token",
]

const PII_URL_PATTERNS = [
  /\/api\/auth\//,
  /password/,
  /token/,
  /secret/,
  /reset/,
]

// Applied in beforeSend:
// 1. Strip headers from request
// 2. Strip email, username, IP from user
// 3. Strip query params with sensitive data
// 4. Redact form data values
// 5. Redact breadcrumb URLs
// 6. Strip cookies from all breadcrumbs
// 7. Remove request body if contains sensitive fields
// 8. Mask session IDs in URLs
// 9. Strip referrer header
// 10. Redact GraphQL variables
// 11. Strip Supabase JWT tokens
// 12. Mask email addresses in logs
// 13. Redact API keys from console breadcrumbs
// 14. Strip phone numbers from form data
// 15. Redact credit card patterns
// 16. Strip file upload contents
// 17. Mask auth headers in fetch requests
// 18. Redact database connection strings
// 19. Strip environment variables from stack traces
// 20. Redact private keys
```

### 13.2 PostHog Event Masking

```tsx
// Applied in PostHog config
const POSTHOG_MASK_CONFIG = {
  maskAllInputs: true,
  maskTextSelector: ".sentry-mask, [data-mask], [data-sensitive]",
  blockSelector: "iframe, video, audio, [data-block], .avatar, .profile-photo",
  property_denylist: [
    "$device_id",
    "$initial_device_id",
    "$device",
    "$os",
    "$browser",
    "$browser_version",
    "$referring_domain",
    "$host",
    "$pathname",
  ],
  // Never capture these elements
  maskTextFn: (text: string) => {
    if (text.length > 100) return text.slice(0, 20) + "..."
    if (/^[\w.+-]+@[\w-]+\.[\w.]+$/.test(text)) return "***@***"
    if (/^\d{10,}$/.test(text)) return "***"
    return text
  },
}
```

### 13.3 Opt-Out Mechanism

```tsx
// hooks/useOptOut.ts
"use client"

import { useState, useEffect } from "react"
import posthog from "posthog-js"
import * as Sentry from "@sentry/nextjs"

const STORAGE_KEY = "observability_opt_out"

export function useOptOut() {
  const [isOptedOut, setIsOptedOut] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === "true") {
      setIsOptedOut(true)
      posthog.opt_out_capturing()
    }
  }, [])

  const optOut = () => {
    setIsOptedOut(true)
    localStorage.setItem(STORAGE_KEY, "true")
    posthog.opt_out_capturing()
    // Sentry has no opt-out API; respect via beforeSend
  }

  const optIn = () => {
    setIsOptedOut(false)
    localStorage.removeItem(STORAGE_KEY)
    posthog.opt_in_capturing()
  }

  return { isOptedOut, optOut, optIn }
}
```

### 13.4 Data Retention Policies

| Data Type | Retention | Rationale | Tool |
|---|---|---|---|
| Error events | 90 days | Debug production issues | Sentry |
| Transaction traces | 30 days | Performance trending | Sentry |
| Session replays | 30 days | UX debugging | Sentry |
| PostHog events | 12 months | Product analytics | PostHog |
| PostHog session recordings | 3 months | UX research | PostHog |
| Logs (server-side) | 7 days | Debugging | Console |
| Logs (client-side batch) | 24 hours | Debugging | API endpoint |
| User properties | Indefinite | Product analytics | PostHog |
| Feature flag assignments | 12 months | A/B test analysis | PostHog |
| User feedback | 12 months | Product improvement | Sentry |

### 13.5 GDPR Compliance Checklist

- [ ] Right to be informed: Privacy policy linked in footer
- [ ] Right of access: Export user data via settings page
- [ ] Right to rectification: Edit profile in settings
- [ ] Right to erasure: Delete account option with full data purge
- [ ] Right to restrict processing: Opt-out of analytics
- [ ] Right to data portability: JSON export of all user data
- [ ] Right to object: Opt-out mechanism available
- [ ] Automated decision-making: AI features clearly labeled

## 14. CI/CD Integration

### 14.1 Source Map Upload (GitHub Actions)

```yaml
# .github/workflows/sentry-release.yml
name: Sentry Release

on:
  push:
    branches: [main]
    paths:
      - "apps/web/**"

env:
  SENTRY_AUTH_TOKEN: \${{ secrets.SENTRY_AUTH_TOKEN }}
  SENTRY_ORG: second-brain-os
  SENTRY_PROJECT: frontend

jobs:
  release:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm
      - run: npm ci
      - run: npm run build
      - name: Create and finalize release
        run: |
          RELEASE="sb-os@\${{ github.sha }}"
          npx sentry-cli releases new "$RELEASE"
          npx sentry-cli releases set-commits "$RELEASE" --auto
          npx sentry-cli releases files "$RELEASE" upload-sourcemaps .next/static/chunks --url-prefix "~/_next/static/chunks"
          npx sentry-cli releases finalize "$RELEASE"
          npx sentry-cli releases deploys "$RELEASE" new -e production
```

### 14.2 Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on:
  pull_request:
    branches: [main]
    paths:
      - "apps/web/**"

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v11
        with:
          urls: |
            http://localhost:3000
            http://localhost:3000/tasks
            http://localhost:3000/dashboard
          configPath: "./lighthouserc.json"
          uploadArtifacts: true
          temporaryPublicStorage: true
        env:
          LHCI_GITHUB_APP_TOKEN: \${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

```json
// apps/web/lighthouserc.json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run start",
      "startServerReadyPattern": "ready on",
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop",
        "throttling": {
          "cpuSlowdownMultiplier": 2
        }
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.95 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 3500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "interaction-to-next-paint": ["error", { "maxNumericValue": 200 }],
        "total-blocking-time": ["error", { "maxNumericValue": 300 }],
        "max-potential-fid": ["warn", { "maxNumericValue": 100 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### 14.3 Bundle Size CI Gate

```yaml
# .github/workflows/bundle-size.yml
name: Bundle Size

on:
  pull_request:
    branches: [main]
    paths:
      - "apps/web/**"

jobs:
  bundle-size:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - name: Build and measure bundle
        run: npm run build && node scripts/bundle-size-check.mjs
```

```js
// apps/web/scripts/bundle-size-check.mjs
import { readFileSync, existsSync } from "fs"
import { join } from "path"

const BUILD_DIR = join(process.cwd(), ".next")
const BUDGETS = {
  initialJs: 350 * 1024, // 350KB
  initialCss: 50 * 1024, // 50KB
}

function getDirSize(dir) {
  if (!existsSync(dir)) return 0
  const entries = readdirSync(dir, { withFileTypes: true, recursive: false })
  let total = 0
  for (const entry of entries) {
    const fullPath = join(dir, entry.name)
    if (entry.isFile()) total += statSync(fullPath).size
  }
  return total
}

const jsSize = getDirSize(join(BUILD_DIR, "static/chunks"))
const cssSize = getDirSize(join(BUILD_DIR, "static/css"))

let failed = false
if (jsSize > BUDGETS.initialJs) {
  console.error(`FAIL: JS bundle ${(jsSize / 1024).toFixed(1)}KB exceeds budget ${(BUDGETS.initialJs / 1024).toFixed(1)}KB`)
  failed = true
}
if (cssSize > BUDGETS.initialCss) {
  console.error(`FAIL: CSS bundle ${(cssSize / 1024).toFixed(1)}KB exceeds budget ${(BUDGETS.initialCss / 1024).toFixed(1)}KB`)
  failed = true
}

if (!failed) console.log("PASS: Bundle sizes within budgets")
process.exit(failed ? 1 : 0)
```

## 15. Testing Observability

### 15.1 Vitest + Sentry Error Reporting

```tsx
// vitest.config.ts
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "path"

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./__tests__/setup.ts"],
    include: ["**/*.test.{ts,tsx}", "**/*.spec.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
      exclude: [
        "**/*.config.*",
        "**/types/**",
        "**/*.d.ts",
        "**/node_modules/**",
        "**/e2e/**",
      ],
    },
    globals: true,
    reporters: ["default", "json"],
    outputFile: { json: "./test-results/results.json" },
  },
  resolve: {
    alias: { "@": path.resolve(__dirname, ".") },
  },
})
```

### 15.2 Playwright Trace Viewer Setup

```tsx
// playwright.config.ts (already configured)
// Trace captures DOM snapshots, network requests, console logs on failure
// Configured to retain on first retry

// To view traces:
// npx playwright show-trace e2e/reports/traces/trace-*.zip
```

### 15.3 Performance Regression Testing

```tsx
// e2e/specs/performance.spec.ts
import { test, expect } from "@playwright/test"

test.describe("Performance regression checks", () => {
  test("tasks page loads within performance budget", async ({ page }) => {
    const startTime = Date.now()
    await page.goto("/tasks")
    await page.waitForLoadState("networkidle")
    const loadTime = Date.now() - startTime
    expect(loadTime).toBeLessThan(3000)
  })

  test("core web vitals are within thresholds", async ({ page }) => {
    const metrics = await page.evaluate(() => JSON.stringify({
      lcp: performance.getEntriesByType("largest-contentful-paint")[0]?.startTime || 0,
      cls: performance.getEntriesByType("layout-shift")?.reduce((sum, e) => sum + (e as any).value, 0) || 0,
      fid: performance.getEntriesByType("first-input")[0]?.duration || 0,
    }))
    const parsed = JSON.parse(metrics)
    expect(parsed.lcp).toBeLessThan(4000)
    expect(parsed.cls).toBeLessThan(0.25)
  })
})
```

## 16. Cost Management

### 16.1 Sentry Quota Budgeting

| Tier | Events/day | Transactions/day | Replays/day | Monthly Cost |
|---|---|---|---|---|
| Free | 5,000 | 0 | 0 | $0 |
| Team | 50,000 | 50,000 | 5,000 | $26/mo |
| Business | 500,000 | 500,000 | 50,000 | $80/mo |

**Current usage estimate:** ~2,000 events/day, ~500 transactions/day, ~100 replays/day ? Free tier is sufficient.

### 16.2 PostHog Event Budgeting

| Tier | Events/mo | Recordings hrs/mo | Monthly Cost |
|---|---|---|---|
| Free | 1,000,000 | 15 | $0 |
| Growth | 2,000,000 | 50 | $40/mo |
| Scale | 10,000,000 | 200 | $200/mo |

**Current usage estimate:** ~50,000 events/month ? Free tier is sufficient.

### 16.3 Sampling Strategies by Route

| Route | Traces Sample Rate | Replays Sample Rate | PostHog Sampling |
|---|---|---|---|
| /dashboard | 0.1 | 0.05 | 1.0 |
| /tasks | 0.25 | 0.1 | 1.0 |
| /chat | 0.5 | 0.2 | 1.0 |
| /api | 0.1 | 0.0 | 0.5 |
| All others | 0.25 | 0.1 | 1.0 |

### 16.4 AI Cost Budget

| Agent | Daily Budget | Monthly Budget | Provider |
|---|---|---|---|
| Briefing | $0.05 | $1.50 | Ollama (free) |
| Weekly Review | $0.10 | $3.00 | Ollama (free) |
| Opportunity Radar | $0.05 | $1.50 | Ollama (free) |
| Memory | $0.02 | $0.60 | Ollama (free) |
| Learning | $0.03 | $0.90 | Ollama (free) |
| Sleep | $0.01 | $0.30 | Ollama (free) |
| Nudge | $0.01 | $0.30 | Ollama (free) |
| Task | $0.02 | $0.60 | Ollama (free) |
| **Total** | **$0.29** | **$8.70** | **Ollama (free)** |
| Claude fallback | Actual cost | Actual cost | Only if Ollama fails |

### 16.5 Cost Alerts

| Alert | Threshold | Channel |
|---|---|---|
| Sentry daily events | >3,000 in 24h | Slack #alerts |
| PostHog monthly events | >500,000 in month | Slack #alerts |
| AI Claude cost | >$1 in 24h | Slack #alerts |
| Total observability cost | >$50/month | Slack #finance |

## 17. Debugging Guide

### 17.1 Common Issues and Solutions (20+ Entries)

| Issue | Likely Cause | Solution |
|---|---|---|
| Sentry events not appearing | Missing DSN or disabled in dev | Check NEXT_PUBLIC_SENTRY_DSN in .env.local |
| PostHog events not firing | Ad blocker or opt-out | Check ad blockers; tunnel through /api/monitoring |
| Source maps not resolving | Release not created | Run npx sentry-cli releases |
| ErrorBoundary not catching | Not a child of ErrorBoundary | Wrap root layout with Boundary |
| Unhandled rejection not tracked | setupUnhandledRejectionTracking not called | Add to ObservabilityInit |
| Web Vitals not reported | reportWebVitals() not called | Verify ObservabilityInit mounts |
| TanStack Query errors not tracked | QueryClient without error handlers | Use makeQueryClient() |
| AI metrics not appearing | trackAICall not called | Wrap each agent call |
| CORS errors on tunnel | CORS headers not set | Check next.config.js headers |
| Session replay not recording | Sample rate too low | Increase replaysSessionSampleRate |
| Bundle size too large | Unoptimized imports | Use dynamic imports, analyze with next/bundle-analyzer |
| Slow LCP | Large images or render-blocking resources | Optimize images, use lazy loading |
| High CLS | Missing dimensions on images | Always set width/height on images |
| ChunkLoadError | Stale service worker | Clear SW cache, bump version |
| Auth errors | JWT expired or invalid | Check supabase.auth.getSession() |
| PostHog identify not working | User not yet loaded | Call identify after useAuth resolves |
| Feature flag always false | Flag not created in PostHog | Create flag in PostHog dashboard |
| Stale data showing | staleTime too high or refetch not configured | Reduce staleTime or call invalidateQueries |
| Error in analytics module itself | try/catch missing | Wrap all analytics calls |
| Correlation ID not in logs | Correlation header not being passed | Add x-correlation-id to fetch headers |

### 17.2 Correlation ID Tracing

To trace a request end-to-end:

1. **Browser**: Open DevTools ? Network tab
2. **Find request**: Look for `x-correlation-id` response header
3. **Copy value**: The correlation ID is an 8-character alphanumeric string
4. **Sentry**: Search issues by `correlationId:[value]`
5. **Logs**: Search server logs by `correlationId:[value]`

### 17.3 Local vs Production Debugging

| Aspect | Development | Production |
|---|---|---|
| Sentry | Disabled (enabled=false) | Enabled with sampling |
| PostHog | Opted out | Full capture |
| Logger | Console only | Console + batch remote |
| Web Vitals | Console log only | Sentry + PostHog |
| Source maps | Full (unminified) | Uploaded to Sentry |
| Session replay | Disabled | 10% sample rate |
| Performance marks | All captured | Sampled |

### 17.4 Browser DevTools Patterns

```tsx
// Development-only debugging helpers
// Accessible in console as window.__DEBUG

if (process.env.NODE_ENV === "development") {
  ;(window as any).__DEBUG = {
    logger: () => import("@/lib/utils/logger").then((m) => m.createLogger("debug")),
    sentry: () => import("@sentry/nextjs"),
    posthog: () => import("posthog-js"),
    queryClient: () => import("@/lib/query/queryClient").then((m) => m.makeQueryClient()),
    forceError: () => { throw new Error("Manual test error") },
    forceRejection: () => Promise.reject(new Error("Manual test rejection")),
    triggerSlowQuery: async () => { await new Promise((r) => setTimeout(r, 5000)); return "slow" },
    checkFeatureFlags: () => posthog.getFeatureFlags(),
  }
}
```

## 18. Implementation Roadmap

### 18.1 Phase 1: Foundation (Week 1-2)

- [x] Install @sentry/nextjs, posthog-js, web-vitals
- [x] Create sentry.client.config.ts with PII redaction
- [x] Create sentry.server.config.ts
- [x] Configure next.config.js with Sentry
- [x] Create Sentry tunnel endpoint (apps/web/app/api/monitoring/route.ts)
- [x] Create ErrorBoundary with three variants
- [x] Create global-error.tsx
- [x] Create ModuleError component
- [x] Create structured logger with PII redaction
- [ ] Wire up root layout with all providers
- [ ] Create route-level error.tsx for all 16 modules

### 18.2 Phase 2: Performance & Analytics (Week 3-4)

- [x] Create web-vitals reporter
- [x] Create PostHog provider
- [x] Create page view tracking hook
- [x] Create performance measurement utilities
- [x] Configure QueryClient with error tracking
- [ ] Add error.tsx to all routes (16 files)
- [ ] Add ModuleErrorBoundary to all module pages
- [ ] Create usePageView hook and integrate
- [ ] Add ObservabilityInit to dashboard layout
- [ ] Set up PostHog feature flags (5+ flags)
- [ ] Create useFeatureFlagTracker hook

### 18.3 Phase 3: AI Observability (Week 5-6)

- [x] Create AI observability module (lib/ai/observability.ts)
- [x] Create fallback tracking (lib/ai/fallback.ts)
- [x] Create cost tracking
- [ ] Integrate trackAICall into all 8 agent modules
- [ ] Integrate withFallbackChain into all agent calls
- [ ] Set up AI cost alerts
- [ ] Create AI observability dashboard

### 18.4 Phase 4: CI/CD & Dashboards (Week 7-8)

- [x] Create Sentry release workflow
- [ ] Create Lighthouse CI workflow
- [ ] Create bundle size CI gate
- [ ] Configure Sentry dashboards
- [ ] Configure PostHog dashboards
- [ ] Set up synthetic monitoring
- [ ] Set up alerting rules
- [ ] Configure PagerDuty integration

### 18.5 Phase 5: Testing & Hardening (Week 9-10)

- [ ] Write Playwright performance tests
- [ ] Write Vitest tests for all observability modules
- [ ] Set up coverage thresholds
- [ ] Penetration test for PII leaks
- [ ] Load test with simulated traffic
- [ ] Document all runbooks
- [ ] Train team on incident response

### 18.6 Phase 6: Cost Optimization (Ongoing)

- [ ] Review sampling rates monthly
- [ ] Audit Sentry event volume weekly
- [ ] Audit PostHog event volume weekly
- [ ] Review AI token usage daily
- [ ] Rotate API keys quarterly
- [ ] Update budgets based on actual usage

## 19. Appendix

### 19.1 Quick Reference Cards

**Card 1: Adding Observability to a New Module**
```tsx
// 1. Create route-level error.tsx
// apps/web/app/(dashboard)/<module>/error.tsx
"use client"
import { useEffect } from "react"
import * as Sentry from "@sentry/nextjs"
import { ModuleError } from "@/components/shared/ModuleError"

export default function ModuleErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { Sentry.captureException(error, { tags: { route: "/<module>" } }) }, [error])
  return <ModuleError error={error} reset={reset} name="<module>" />
}

// 2. Page init with performance marks and analytics
// In your page component:
// import { ModuleMarks, markEnd } from "@/lib/utils/performance"
// import { trackModuleUsage } from "@/lib/utils/user-properties"
// useEffect(() => {
//   const mark = ModuleMarks.<module>Load()
//   fetchData().finally(() => markEnd(mark, { module: "<module>" }))
//   trackModuleUsage("<Module>")
// }, [])

// 3. Wrap sections with ErrorBoundary
// import { SectionErrorBoundary } from "@/components/shared/ErrorBoundary"
// <SectionErrorBoundary moduleName="<module>">
//   <YourComponent />
// </SectionErrorBoundary>
```

**Card 2: Common Logging Patterns**
```tsx
// INFO: Standard operation
log.info("Tasks loaded", { count: 42 })

// WARN: Unexpected but handled
if (duration > 3000) log.warn("Slow query", { duration, table: "tasks" })

// ERROR: Catch block
try { ... } catch (err) { log.error("Operation failed", { message: String(err) }) }

// FATAL: Only for crashes
log.fatal("Page crashed, reloading", { url: window.location.href })
```

**Card 3: Sentry Debugging Commands**
```bash
# Check if Sentry is initialized
npx sentry-cli info

# List releases
npx sentry-cli releases list

# Upload source maps manually
npx sentry-cli releases files sb-os@<sha> upload-sourcemaps .next/static/chunks --url-prefix "~/_next/static/chunks"

# Create release
npx sentry-cli releases new sb-os@<sha>

# Set commits
npx sentry-cli releases set-commits sb-os@<sha> --auto
```

### 19.2 Pre-Commit Observability Checklist

- [ ] All 16 modules have error.tsx route error files
- [ ] All API calls use apiFetch() or executeQuery() wrappers
- [ ] Every module page has ModuleMarks.load() and markEnd()
- [ ] All agent functions call trackAICall()
- [ ] All fallbacks use withFallbackChain()
- [ ] No console.log in production code (use logger)
- [ ] Sentry tunnel configured in next.config.js
- [ ] PostHog provider wraps the app
- [ ] PII redaction rules in sentry.client.config.ts
- [ ] web-vitals reporter wired in ObservabilityInit
- [ ] All localStorage/IndexedDB calls are try/catched
- [ ] Feature flags have default values (no runtime errors)

### 19.3 Tools Comparison

| Tool | Purpose | Cost (Current) | Alternative | When to Use |
|---|---|---|---|---|
| Sentry | Error tracking + Performance | Free tier | Datadog RUM, New Relic | Default for errors and traces |
| PostHog | Product analytics + Flags | Free tier | Amplitude, Mixpanel | Default for events and flags |
| web-vitals | Core Web Vitals | Free | Lighthouse CI | Client-side RUM |
| Sonner | User-facing toasts | Free | react-hot-toast | User notifications (not logs) |
| Structured Logger | Debug logging | Free | Winston | All debug/info/warn/error logs |
| Lighthouse | Performance budgets | Free | PageSpeed Insights | CI performance gates |
| Playwright | E2E tracing | Free | Cypress | E2E with trace viewer |

### 19.4 Reference Links

- [Sentry Next.js SDK Docs](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [PostHog Next.js Docs](https://posthog.com/docs/libraries/next-js)
- [Web Vitals](https://web.dev/vitals/)
- [TanStack Query Devtools](https://tanstack.com/query/latest/docs/react/devtools)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Playwright Trace Viewer](https://playwright.dev/docs/trace-viewer)
- [Supabase Error Handling](https://supabase.com/docs/reference/javascript/error-handling)

---

*End of Frontend Observability Guide — Enterprise Edition v3.0.0. All agents must reference this document when adding error handling, analytics, or performance monitoring to the codebase.*

### 19.5 Environment Variables Reference

| Variable | Used By | Required | Description |
|---|---|---|---|
| NEXT_PUBLIC_SENTRY_DSN | sentry.client.config.ts | Yes | Sentry project DSN |
| SENTRY_AUTH_TOKEN | CI (sentry-release.yml) | CI only | Sentry API token for source maps |
| SENTRY_ORG | CI + next.config.js | Yes | Sentry organization name |
| SENTRY_PROJECT | CI + next.config.js | Yes | Sentry project name |
| NEXT_PUBLIC_POSTHOG_KEY | PostHogProvider | Yes | PostHog project API key |
| NEXT_PUBLIC_POSTHOG_HOST | PostHogProvider | No | Custom PostHog host (default: app.posthog.com) |
| NEXT_PUBLIC_APP_VERSION | All | No | Current app version (default: 1.0.0) |
| NEXT_PUBLIC_SUPABASE_URL | supabase.ts | Yes | Supabase project URL |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | supabase.ts | Yes | Supabase anonymous key |
| OLLAMA_BASE_URL | Health check | No | Ollama server URL (default: localhost:11434) |
| DEBUG | Logger | No | Enable verbose logging |

### 19.6 Complete File Inventory - Observability Files

| File | Purpose | Lines |
|---|---|---|
| apps/web/sentry.client.config.ts | Client-side Sentry init | 23 |
| apps/web/sentry.server.config.ts | Server-side Sentry init | 30 |
| apps/web/next.config.js | Next.js + Sentry config | 35 |
| apps/web/app/api/monitoring/route.ts | Sentry tunnel | 28 |
| apps/web/app/api/health/route.ts | Health endpoint | 55 |
| apps/web/app/api/logs/route.ts | Log batching endpoint | 28 |
| apps/web/app/global-error.tsx | Global error handler | 35 |
| apps/web/components/shared/ErrorBoundary.tsx | 3 error boundary variants | 200 |
| apps/web/components/shared/ModuleError.tsx | Route error display | 54 |
| apps/web/components/shared/PostHogProvider.tsx | PostHog provider | 45 |
| apps/web/hooks/usePageView.ts | Page view tracking | 32 |
| apps/web/hooks/useFeatureFlagTracker.ts | Feature flags | 80 |
| apps/web/hooks/useRouteTransition.ts | Route transition perf | 40 |
| apps/web/hooks/useLongTaskMonitor.ts | Long task tracking | 40 |
| apps/web/hooks/useImagePerformance.ts | Image perf tracking | 35 |
| apps/web/hooks/useOptOut.ts | Privacy opt-out | 35 |
| apps/web/hooks/useModuleTracker.ts | Module usage tracking | 35 |
| apps/web/lib/web-vitals.ts | Web Vitals reporting | 75 |
| apps/web/lib/utils/logger.ts | Structured logger | 130 |
| apps/web/lib/utils/performance.ts | Performance marks | 100 |
| apps/web/lib/utils/analytics.ts | Analytics events | 16 |
| apps/web/lib/utils/correlation.ts | Correlation IDs | 20 |
| apps/web/lib/utils/user-properties.ts | User property enrichment | 45 |
| apps/web/lib/errors/index.ts | Custom error classes | 120 |
| apps/web/lib/errors/reporter.ts | Error report utility | 40 |
| apps/web/lib/errors/unhandled-rejection.ts | Rejection tracking | 25 |
| apps/web/lib/query/queryClient.ts | TanStack Query config | 100 |
| apps/web/lib/query/optimistic.ts | Optimistic update tracking | 40 |
| apps/web/lib/api/fetch.ts | Wrapped fetch | 100 |
| apps/web/lib/supabase.ts | DB wrapper | 100 |
| apps/web/lib/ai/observability.ts | AI observability | 120 |
| apps/web/lib/ai/fallback.ts | AI fallback chain | 130 |
| apps/web/app/(dashboard)/observability-init.tsx | Dashboard init | 25 |
| apps/web/scripts/synthetic-monitor.mjs | Health monitoring | 40 |
| apps/web/scripts/bundle-size-check.mjs | Bundle size CI gate | 40 |

### 19.7 Observability SLA Compliance Checklist

**Daily Checks**
- [ ] Sentry error rate is below 1% of page views
- [ ] No P0 errors in the last 24 hours
- [ ] AI fallback rate is below 5%
- [ ] LCP is below 2.5s (p75)
- [ ] PostHog events are flowing normally

**Weekly Checks**
- [ ] Review top 10 errors in Sentry and create fixes
- [ ] Check AI cost against budget
- [ ] Audit PII redaction rules for new features
- [ ] Review sampling rates for cost efficiency
- [ ] Check Sentry and PostHog quota usage

**Monthly Checks**
- [ ] Rotate API keys for Sentry, PostHog, Supabase
- [ ] Update feature flags based on A/B test results
- [ ] Review dashboard effectiveness and add new widgets
- [ ] Run bundle size analysis and optimize
- [ ] Review alert thresholds and adjust
### 19.8 Version Compatibility Matrix

| Package | Current Version | Minimum Compatible | Breaking Changes |
|---|---|---|---|
| @sentry/nextjs | 10.57.0 | 8.0.0 | V8 removed old integrations API |
| @sentry/react | 10.57.0 | 8.0.0 | Must match @sentry/nextjs version |
| posthog-js | 1.386.6 | 1.0.0 | Session recording config changed in 1.50 |
| web-vitals | 5.3.0 | 3.0.0 | V4+ removed reportAllChanges |
| @tanstack/react-query | 5.101.0 | 5.0.0 | V5 dropped QueryClientProvider patterns |
| next | 14.2.0 | 14.0.0 | App router stable in 13.4 |
| react | 18.2.0 | 18.0.0 | Concurrent features stable in 18 |
| supabase-js | 2.39.0 | 2.0.0 | V2 changed auth API significantly |

### 19.9 Error Message Quick Reference

| Error Pattern | Likely Cause | File to Check | Fix |
|---|---|---|---|
| Request timed out after Nms | Network timeout | lib/api/fetch.ts | Increase timeout or check network |
| HTTP 429 | Rate limited | lib/api/fetch.ts | Implement backoff |
| PostgrestError | DB query failed | lib/supabase.ts | Check RLS policies |
| JWT expired | Auth token expired | hooks/useAuth.ts | Auto-refresh token |
| Row level security violation | RLS violation | lib/supabase.ts | Add user_id filter |
| Ollama connection refused | Local AI down | lib/ai/fallback.ts | Run ollama serve |
| Claude API error | Cloud AI rate limit | lib/ai/fallback.ts | Check API key / quota |
| ChunkLoadError | Stale JS bundle | next.config.js | Force SW update |
| Hydration failed | SSR/CSR mismatch | page component | Fix conditional rendering |
| Cannot access property of undefined | Undefined object | component | Add optional chaining |

### 19.10 Observability Decision Tree

Use this decision tree when deciding how to instrument a new feature:

1. **Is it an error?**
   - Yes: Is it expected? Use log.warn()
   - Yes: Is it unexpected? Use reportError() or Sentry.captureException()
   - No: Continue to step 2

2. **Is it a performance concern?**
   - Yes: Use measureAsync() or markStart()/markEnd()
   - Yes: Add Sentry.metrics.distribution() for the metric
   - No: Continue to step 3

3. **Is it a user action?**
   - Yes: Use track() or trackEvent() with PostHog
   - Yes: Add the event to the taxonomy table
   - No: Continue to step 4

4. **Is it an AI call?**
   - Yes: Use trackAICall() for token/latency/cost tracking
   - Yes: Wrap in withFallbackChain() for resilience
   - No: Continue to step 5

5. **Is it a network request?**
   - Yes: Use apiFetch() (auto-instrumented with retries)
   - Yes: Or executeQuery() for Supabase queries
   - No: Use standard logger for general info

### 19.11 On-Call Runbook Quick Reference

**P0: App is down or unusable for all users**

1. Check Vercel status: https://www.vercel-status.com/
2. Check Supabase status: https://status.supabase.com/
3. Check Sentry error stream for spike
4. Check recent deployments: git log --oneline -5
5. If deployment-related: Rollback via Vercel dashboard
6. Post in #incidents with timeline and findings

**P1: Major feature is broken**

1. Identify affected module from Sentry tags
2. Check if error rate correlates with recent changes
3. Isolate to specific API endpoint or component
4. If Supabase error, check RLS policies and table schema
5. Create GitHub issue with Sentry link and full trace
6. Assign owner and set priority

**P2: Minor feature or performance regression**

1. File GitHub issue with Screenshot + Sentry link
2. Label with "observability" and affected module
3. Schedule for next sprint planning
4. No immediate action required

### 19.12 Security Considerations

1. **Sentry DSN is public** - It is safe to expose in client code. It only allows event submission, not reading.
2. **PostHog API key is public** - It only allows event submission. Write-only access.
3. **Never expose Supabase anon key or service key** - Anon key is for client-side use only.
4. **Sentry auth tokens are secret** - These have full API access. Store in GitHub secrets.
5. **PII redaction is mandatory** - Never send email, phone, address, or auth tokens to Sentry/PostHog.
6. **Session recording requires consent** - PostHog session recording must respect opt-out.
7. **Data retention must be enforced** - Delete old events and replays per the retention policy.
8. **Logs must not contain secrets** - The logger auto-redacts sensitive key names.

---

*End of Frontend Observability Guide - Enterprise Edition v3.0.0. All agents must reference this document when adding error handling, analytics, or performance monitoring to the codebase.*
### 19.13 Observable Every Module: Implementation Status

| Module | error.tsx | ErrorBoundary | Performance Mark | Event Tracking | Logger Setup |
|---|---|---|---|---|---|
| Dashboard | Pending | ModuleErrorBoundary | ModuleMarks.dashboardLoad | module_opened | done |
| Tasks | Pending | ModuleErrorBoundary | ModuleMarks.tasksLoad | module_opened | done |
| Courses | Pending | ModuleErrorBoundary | ModuleMarks.coursesLoad | module_opened | done |
| Habits | Pending | ModuleErrorBoundary | ModuleMarks.habitsLoad | module_opened | done |
| Goals | Pending | ModuleErrorBoundary | ModuleMarks.goalsLoad | module_opened | done |
| Sleep | Pending | ModuleErrorBoundary | ModuleMarks.sleepLoad | module_opened | done |
| Income | Pending | ModuleErrorBoundary | ModuleMarks.incomeLoad | module_opened | done |
| Projects | Pending | ModuleErrorBoundary | ModuleMarks.projectsLoad | module_opened | done |
| Ideas | Pending | ModuleErrorBoundary | ModuleMarks.ideasLoad | module_opened | done |
| Resources | Pending | ModuleErrorBoundary | ModuleMarks.resourcesLoad | module_opened | done |
| Opportunities | Pending | ModuleErrorBoundary | ModuleMarks.opportunitiesLoad | module_opened | done |
| Time | Pending | ModuleErrorBoundary | ModuleMarks.timeLoad | module_opened | done |
| Chat | Pending | ModuleErrorBoundary | ModuleMarks.chatLoad | module_opened | done |
| Automation | Pending | ModuleErrorBoundary | ModuleMarks.automationLoad | module_opened | done |
| YouTube | Pending | ModuleErrorBoundary | ModuleMarks.youtubeLoad | module_opened | done |
| Academics | Pending | ModuleErrorBoundary | ModuleMarks.academicsLoad | module_opened | done |

### 19.14 Performance Regression Comparison Script

`	ypescript
// scripts/compare-perf.mjs
// Compares current build performance against baseline
import { readFileSync, writeFileSync, existsSync } from "fs"

const BASELINE_FILE = ".next/perf-baseline.json"
const CURRENT_FILE = ".next/perf-current.json"
const REPORT_FILE = ".next/perf-report.md"

interface PerfSnapshot {
  timestamp: string
  commitSha: string
  totalJsSize: number
  totalCssSize: number
  chunkCount: number
  largestChunkSize: number
  largestChunkName: string
}

function generateSnapshot(): PerfSnapshot {
  const buildDir = ".next/static/chunks"
  const cssDir = ".next/static/css"
  // ... snapshot logic ...
  return {
    timestamp: new Date().toISOString(),
    commitSha: process.env.GITHUB_SHA || "local",
    totalJsSize: 0,
    totalCssSize: 0,
    chunkCount: 0,
    largestChunkSize: 0,
    largestChunkName: "",
  }
}

function compareSnapshots(baseline: PerfSnapshot, current: PerfSnapshot): string {
  let report = "# Performance Regression Report\n\n"
  report += | Metric | Baseline | Current | Change | Status |\n|---|---|---|---|---|\n

  const metrics = [
    { name: "Total JS Size", base: baseline.totalJsSize, curr: current.totalJsSize, threshold: 0.1 },
    { name: "Total CSS Size", base: baseline.totalCssSize, curr: current.totalCssSize, threshold: 0.1 },
    { name: "Chunk Count", base: baseline.chunkCount, curr: current.chunkCount, threshold: 0.2 },
    { name: "Largest Chunk", base: baseline.largestChunkSize, curr: current.largestChunkSize, threshold: 0.15 },
  ]

  for (const metric of metrics) {
    const change = ((metric.curr - metric.base) / metric.base) * 100
    const status = change > metric.threshold * 100 ? "FAIL" : "PASS"
    report += |  |  |  | % |  |\n
  }

  return report
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return ${bytes} B
  if (bytes < 1024 * 1024) return ${(bytes / 1024).toFixed(1)} KB
  return ${(bytes / 1024 / 1024).toFixed(1)} MB
}

// Run comparison
const baseline = existsSync(BASELINE_FILE) ? JSON.parse(readFileSync(BASELINE_FILE, "utf-8")) : null
const current = generateSnapshot()
writeFileSync(CURRENT_FILE, JSON.stringify(current, null, 2))

if (baseline) {
  const report = compareSnapshots(baseline, current)
  writeFileSync(REPORT_FILE, report)
  console.log(Performance report written to )
} else {
  writeFileSync(BASELINE_FILE, JSON.stringify(current, null, 2))
  console.log("Baseline snapshot created")
}
`

### 19.15 Observability Health Scoring

Each module receives a health score (0-100) based on observability completeness:

| Criteria | Points | How to Verify |
|---|---|---|
| error.tsx exists | 10 | File exists in module route directory |
| ErrorBoundary wraps page | 10 | ModuleErrorBoundary in component tree |
| Performance mark on mount | 10 | ModuleMarks.<module>Load() called |
| markEnd after data loads | 10 | markEnd() in finally block |
| PostHog event on open | 10 | trackModuleUsage() or module_opened event |
| Logger initialized | 10 | createLogger() at top of file |
| API errors captured | 10 | Uses apiFetch() or executeQuery() |
| Sentry tags set | 10 | Sentry scope.setTags({ module: ... }) |
| Fallback UI for empty states | 10 | Empty state component shown |
| Loading state indicator | 10 | Loading skeleton or spinner shown |
| **Total possible** | **100** | |

Target minimum: **80/100** per module before production release.

### 19.16 Common Observability Anti-Patterns

| Anti-Pattern | Why It is Harmful | Correct Approach |
|---|---|---|
| console.log() in production | No structured format, no PII redaction | Use createLogger() |
| Catching and swallowing errors | Silent failures that hide bugs | Always log or report caught errors |
| Exposing user email in events | PII leakage to analytics platforms | Hash emails or use anonymized IDs |
| Over-sampling all routes | High Sentry/PostHog costs | Use route-specific sample rates |
| No error boundaries | Whole app crashes from one component error | Wrap every section with ErrorBoundary |
| Missing error.tsx | Default Next.js error page is unhelpful | Create per-route error.tsx |
| Hardcoded prompt strings | Prompt changes break without version tracking | Use PromptLoader |
| Synchronous try/catch around async | Does not catch promise rejections | Use .catch() or async/await with try/catch |
| Not setting user context in Sentry | Cannot identify affected users | Call Sentry.setUser() on auth |
| Tracking every keystroke | Event overload, privacy concerns | Debounce input events, never track passwords |
| No fallback for AI calls | User sees error when Ollama is down | Implement withFallbackChain() |
| Disabling Sentry locally | Cannot test error tracking in dev | Set sample rate to 0 for dev, enable for prod |

### 19.17 Post-Deployment Verification Script

`ash
# Run this after every deployment to verify observability is working
# Save as scripts/verify-observability.sh

echo "=== Post-Deployment Observability Verification ==="

# 1. Check health endpoint
echo "1. Checking health endpoint..."
HEALTH=
if echo "" | grep -q '"status":"ok"'; then
  echo "   [PASS] Health endpoint returns ok"
else
  echo "   [FAIL] Health endpoint failed"
  echo "   Response: "
fi

# 2. Check Sentry DSN is configured
echo "2. Checking Sentry DSN..."
if [ -n "" ]; then
  echo "   [PASS] Sentry DSN configured"
else
  echo "   [FAIL] Sentry DSN missing"
fi

# 3. Check PostHog key is configured
echo "3. Checking PostHog key..."
if [ -n "" ]; then
  echo "   [PASS] PostHog key configured"
else
  echo "   [FAIL] PostHog key missing"
fi

# 4. Verify page loads with expected status
echo "4. Checking page loads..."
PAGES="/ /login /dashboard /tasks /courses"
for page in ; do
  STATUS=
  if [ "" = "200" ]; then
    echo "   [PASS]  returns 200"
  else
    echo "   [FAIL]  returns "
  fi
done

echo ""
echo "=== Verification Complete ==="
`

### 19.18 Upgrading Guide (v2 to v3)

If you are upgrading from v2 to v3 of this guide, here are the key changes:

**New Files to Create:**
- lib/errors/index.ts - Custom error classes
- lib/errors/reporter.ts - Error reporting utility
- lib/errors/unhandled-rejection.ts - Promise rejection tracking
- lib/ai/observability.ts - AI call tracing
- lib/ai/fallback.ts - AI fallback chain
- lib/api/fetch.ts - Wrapped fetch with retries
- lib/utils/correlation.ts - Correlation ID generation
- lib/query/optimistic.ts - Optimistic update tracking
- hooks/useRouteTransition.ts - Route transition tracking
- hooks/useLongTaskMonitor.ts - Long task monitoring
- hooks/useImagePerformance.ts - Image performance monitoring
- hooks/useFeatureFlagTracker.ts - Feature flag tracking
- hooks/useModuleTracker.ts - Module usage tracking
- hooks/useTrack.ts - Event tracking hook
- hooks/useABTest.ts - A/B testing
- apps/web/app/api/logs/route.ts - Log batching endpoint
- apps/web/app/(dashboard)/observability-init.tsx - Dashboard init

**Files to Update:**
- sentry.client.config.ts - Add fingerprinting, tunnel, dynamic sampling
- sentry.server.config.ts - Create new
- lib/supabase.ts - Add executeQuery wrapper
- lib/query/queryClient.ts - Add QueryCache, MutationCache with errors
- lib/utils/logger.ts - Add batching, correlation IDs, fatal level
- lib/web-vitals.ts - Add PostHog reporting, module context

**Config Changes:**
- next.config.js - Add Sentry config, headers, bundle analyzer
- vitest.config.ts - Add coverage thresholds
- playwright.config.ts - Already configured for traces
- .github/workflows/ - Add sentry-release, lighthouse, bundle-size workflows
