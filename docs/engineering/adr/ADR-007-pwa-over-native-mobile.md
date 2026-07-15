## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-ADR-007 |
| Version | 1.0.0 |
| Status | Proposed |
| Last Updated | 2026-07-11 |
| Author | Developer |

# ADR-007: PWA over Native Mobile

## Status
Proposed

## Date
2024-06-10

## Context
Future mobile access is planned so users can interact with their Second Brain on the go — check tasks, log habits, view briefings, and capture ideas. Options considered: Progressive Web App (PWA), React Native, and Flutter. The primary constraint is that the project is a solo development effort with TypeScript/React on the frontend already.

## Decision

```mermaid
graph TD
    subgraph PWA["PWA (Chosen) - Single Codebase"]
        FE[@serwist/next<br/>Next.js + Service Worker]
        SW[Service Worker<br/>Offline Cache + Background Sync]
        WEB[Desktop Web]
        TAB[Tablet]
        MOB[Mobile Browser]
        FE --> SW
        FE --> WEB
        FE --> TAB
        FE --> MOB
        SW -->|Workbox| CACHE[(IndexedDB<br/>Offline Data)]
    end

    subgraph NATIVE["React Native / Flutter (Deferred)"]
        RN[Separate App Repo]
        APK[Play Store APK]
        IPA[App Store IPA]
        PUSH[Push Notifications]
        NATIVE_API[Native APIs<br/>Camera, GPS, Biometrics]
    end

    style PWA fill:#0A0B0F,stroke:#00FFA3,color:#F1F5F9
    style NATIVE fill:#0A0B0F,stroke:#EF4444,color:#F1F5F9
```

Implement the existing Next.js application as a Progressive Web App using `@serwist/next` or the built-in PWA capabilities of Next.js. The web app already uses responsive Tailwind layouts, so mobile viewport support is already partially in place. A service worker will be added for offline caching of static assets and API responses. Native apps (React Native or Flutter) are deferred until post-MVP validation.

## Consequences

### Positive
- Single codebase serves desktop web, tablet, and mobile — no separate React Native project to maintain
- Instant deployment — push to main, Vercel deploys, users get the update on next page load with zero friction
- No app store review process — bypasses Apple and Google's 24-48 hour review cycles
- Service worker enables offline access to cached content (briefings, task lists) without a network connection
- Full offline support for AI features via local Ollama — PWA can work entirely without internet

### Negative
- No push notifications on iOS — Safari on iOS does not support the Web Push API, so iOS users won't get "Briefing ready" or "Task overdue" notifications
- Limited native API access — no background geolocation, no file system access, no biometric auth beyond WebAuthn
- Performance gap — JS-heavy interactions (animations, list rendering) are slower than native equivalents, especially on low-end Android devices
- No app store discoverability — users must visit the URL and manually "Add to Home Screen"

### Neutral
- PWA can be wrapped in a WebView (via PWABuilder or similar) for a future Play Store listing without rewriting
- The existing Zustand stores and Supabase client already work on mobile viewports — no architectural changes needed
- User engagement metrics will determine whether native development is justified post-MVP
