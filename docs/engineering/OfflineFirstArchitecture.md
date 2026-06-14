# Offline-First Architecture — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-OFFLINE-001 |
| **Status** | Draft v0.1 |
| **Author** | Architecture Team |
| **Last Updated** | 2026-06-11 |
| **Approved By** | — |

---

## 1. Executive Summary

Second Brain OS currently requires a persistent internet connection. Users on campus WiFi, commuting, or in low-connectivity zones lose access to their tasks, habits, notes, and goals. This document specifies a **Progressive Web App (PWA)** architecture that enables full offline CRUD, a background sync engine, and conflict resolution — all within the existing Next.js 14 + Supabase stack. Target: 100% read availability offline, < 500 ms sync latency on reconnect, zero data loss.

---

## 2. Current State

- **No service worker.** App shell loads from server every time.
- **No offline storage.** All data fetched via `fetch()` / Supabase JS client.
- **No sync queue.** Network errors surface as toast messages; user retries manually.
- **No PWA manifest.** Browser cannot prompt "Add to Home Screen."
- **No background sync.** `navigator.serviceWorker.ready.sync.register()` never invoked.

---

## 3. Offline Requirements

| Requirement | Priority | Acceptance Criteria |
|---|---|---|
| Read cached data while offline | P0 | All previously loaded data visible offline |
| Cache latest data on page load | P0 | SWR responses written to IndexedDB |
| Queue writes made offline | P0 | Mutations stored in sync queue, 100% replayable |
| Sync writes on reconnect | P0 | Queue processed within 5 s of `online` event |
| Handle sync conflicts | P1 | Last-write-wins for v1; manual resolution UI for v2 |
| Install as standalone PWA | P1 | "Add to Home Screen" prompt works |
| Show offline/queued state | P1 | Banner, badge count on sync icon |

---

## 4. PWA Setup

### 4.1 Manifest

`apps/web/public/manifest.json`:

```json
{
  "name": "Second Brain OS",
  "short_name": "SB OS",
  "description": "Personal AI Productivity System",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0A0B0F",
  "theme_color": "#6366F1",
  "orientation": "portrait-primary",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "categories": ["productivity", "education"],
  "screenshots": [
    { "src": "/screenshots/dashboard.jpg", "sizes": "1280x720", "type": "image/jpeg" }
  ]
}
```

### 4.2 Service Worker Registration

`apps/web/lib/sw-register.ts`:

```typescript
export async function registerSW(): Promise<void> {
  if (!('serviceWorker' in navigator)) return

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
      updateViaCache: 'none',
    })
    console.log('[SW] Registered:', registration.scope)

    registration.addEventListener('updatefound', () => {
      const installing = registration.installing
      if (installing) {
        installing.addEventListener('statechange', () => {
          if (installing.state === 'activated') {
            console.log('[SW] Activated')
            registration.update()
          }
        })
      }
    })
  } catch (err) {
    console.error('[SW] Registration failed:', err)
  }
}
```

### 4.3 Install Prompt

```typescript
// apps/web/lib/pwa-install.ts
let deferredPrompt: BeforeInstallPromptEvent | null = null

export function listenForInstallPrompt(): void {
  window.addEventListener('beforeinstallprompt', (e: Event) => {
    e.preventDefault()
    deferredPrompt = e as BeforeInstallPromptEvent
  })
}

export async function showInstallPrompt(): Promise<boolean> {
  if (!deferredPrompt) return false
  deferredPrompt.prompt()
  const result = await deferredPrompt.userChoice
  deferredPrompt = null
  return result.outcome === 'accepted'
}
```

---

## 5. Service Worker Strategy

### 5.1 Cache-First — Static Assets

CSS, JS, fonts, icons — never changes without a new build:

```javascript
// public/sw.js — Static asset handler
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Static assets: cache-first
  if (/\.(js|css|woff2?|png|jpg|svg|ico)$/i.test(url.pathname)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        return cached || fetchAndCache(request)
      })
    )
    return
  }
})
```

### 5.2 Network-First — API Mutations

POST/PUT/DELETE must reach the server. Fallback queues the request:

```javascript
// API mutations: network-first, queue on failure
if (request.method !== 'GET') {
  event.respondWith(
    fetch(request).catch(() => {
      return queueRequest(request.clone())
    })
  )
  return
}
```

### 5.3 Stale-While-Revalidate — API Reads

GET requests serve cached data immediately, then fetch fresh data in background:

```javascript
// API reads: stale-while-revalidate
if (url.pathname.startsWith('/api/')) {
  event.respondWith(
    caches.match(request).then((cached) => {
      const fetchPromise = fetch(request).then((response) => {
        if (response.ok) {
          const cloned = response.clone()
          caches.open('api-cache').then((cache) => {
            cache.put(request, cloned)
          })
        }
        return response
      }).catch(() => cached)

      return cached || fetchPromise
    })
  )
  return
}
```

---

## 6. IndexedDB Schema

### 6.1 Database

`apps/web/lib/db/schema.ts`:

```typescript
export const DB_NAME = 'secondbrain_offline'
export const DB_VERSION = 1

export interface OfflineStore {
  tasks: {
    keyPath: 'id'
    indexes: ['user_id', 'status', 'updated_at']
  }
  habits: {
    keyPath: 'id'
    indexes: ['user_id', 'date', 'habit_name']
  }
  goals: {
    keyPath: 'id'
    indexes: ['user_id', 'status']
  }
  sync_queue: {
    keyPath: 'id'
    indexes: ['status', 'created_at']
  }
  conflict_log: {
    keyPath: 'id'
    indexes: ['entity_type', 'entity_id', 'resolved']
  }
}
```

### 6.2 Data Store (Mirrors Supabase Tables)

Each store mirrors the corresponding Supabase table schema exactly (same columns, same types). Data is upserted on every successful API read.

### 6.3 Sync Queue

```typescript
export interface SyncQueueItem {
  id: string                    // UUID
  entity_type: string           // 'tasks' | 'habits' | 'goals'
  entity_id: string             // local UUID or null (for INSERT)
  operation: 'CREATE' | 'UPDATE' | 'DELETE'
  payload: Record<string, any>  // full entity data
  status: 'queued' | 'processing' | 'failed'
  created_at: string            // ISO 8601
  retry_count: number
  last_error?: string
}
```

### 6.4 Conflict Log

```typescript
export interface ConflictLogEntry {
  id: string
  entity_type: string
  entity_id: string
  local_version: Record<string, any>
  server_version: Record<string, any>
  resolved: boolean
  resolution?: 'local_wins' | 'server_wins' | 'manual'
  created_at: string
  resolved_at?: string
}
```

---

## 7. Sync Strategy

### 7.1 Sync Flow

```
┌──────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│  User    │    │  IndexedDB │    │  Sync      │    │  Supabase  │
│  Action  │───▶│  Queue     │───▶│  Engine    │───▶│  (Server)  │
└──────────┘    └────────────┘    └────────────┘    └────────────┘
                                       │                   │
                                       │            ┌──────┘
                                       │            ▼
                                       │       Process Queue
                                       │            │
                                       │     ┌──────┴──────┐
                                       │     │             │
                                       │  Success      Conflict
                                       │     │             │
                                       │     ▼             ▼
                                       │  Dequeue    Log Conflict
                                       │  From Queue  Resolve
                                       │     │             │
                                       │     ▼             ▼
                                       │  Update       Update
                                       │  UI Data     Conflict UI
```

### 7.2 Sync Engine

`apps/web/lib/sync/sync-engine.ts`:

```typescript
export class SyncEngine {
  private processing = false

  async start(): Promise<void> {
    window.addEventListener('online', () => this.processQueue())
    window.addEventListener('focus', () => this.processQueue())
    // Periodic: every 60 seconds while online
    setInterval(() => {
      if (navigator.onLine) this.processQueue()
    }, 60_000)
  }

  async enqueue(op: Omit<SyncQueueItem, 'id' | 'status' | 'retry_count'>): Promise<void> {
    await db.sync_queue.add({
      ...op,
      id: crypto.randomUUID(),
      status: 'queued',
      retry_count: 0,
      created_at: new Date().toISOString(),
    })
    this.processQueue()
  }

  async processQueue(): Promise<void> {
    if (this.processing || !navigator.onLine) return
    this.processing = true

    try {
      const items = await db.sync_queue
        .where('status')
        .equals('queued')
        .sortBy('created_at')

      for (const item of items) {
        await db.sync_queue.update(item.id, { status: 'processing' })

        try {
          await this.executeOperation(item)
          await db.sync_queue.delete(item.id)
        } catch (err: any) {
          if (this.isConflictError(err)) {
            await this.handleConflict(item, err)
          } else {
            const retries = item.retry_count + 1
            if (retries >= 5) {
              await db.sync_queue.update(item.id, {
                status: 'failed',
                retry_count: retries,
                last_error: err.message,
              })
            } else {
              await db.sync_queue.update(item.id, {
                status: 'queued',
                retry_count: retries,
                last_error: err.message,
              })
            }
          }
        }
      }
    } finally {
      this.processing = false
    }
  }

  private async executeOperation(item: SyncQueueItem): Promise<void> {
    switch (item.operation) {
      case 'CREATE':
        await supabase.from(item.entity_type).insert(item.payload)
        break
      case 'UPDATE':
        await supabase.from(item.entity_type).update(item.payload).eq('id', item.entity_id)
        break
      case 'DELETE':
        await supabase.from(item.entity_type).delete().eq('id', item.entity_id)
        break
    }
  }

  private isConflictError(err: any): boolean {
    return err?.code === '409' || err?.message?.includes('conflict')
  }

  private async handleConflict(item: SyncQueueItem, err: any): Promise<void> {
    // Fetch server version
    const { data: serverData } = await supabase
      .from(item.entity_type)
      .select('*')
      .eq('id', item.entity_id)
      .single()

    await db.conflict_log.add({
      id: crypto.randomUUID(),
      entity_type: item.entity_type,
      entity_id: item.entity_id!,
      local_version: item.payload,
      server_version: serverData,
      resolved: false,
      created_at: new Date().toISOString(),
    })

    // Last-write-wins (v1): server wins by default
    await db.sync_queue.delete(item.id)
  }
}
```

### 7.3 Online/Offline Detection

```typescript
// apps/web/hooks/useOnlineStatus.ts
import { useState, useEffect } from 'react'

export function useOnlineStatus(): boolean {
  const [online, setOnline] = useState(navigator.onLine)

  useEffect(() => {
    const goOnline = () => setOnline(true)
    const goOffline = () => setOnline(false)

    window.addEventListener('online', goOnline)
    window.addEventListener('offline', goOffline)

    return () => {
      window.removeEventListener('online', goOnline)
      window.removeEventListener('offline', goOffline)
    }
  }, [])

  return online
}
```

---

## 8. Conflict Resolution

### 8.1 Strategy Tiers

| Version | Strategy | When |
|---|---|---|
| v1 (MVP) | Last-write-wins (server wins) | All entities. Acceptable for single-user. |
| v2 (Q3 2026) | CRDT-based merge | Collaborative notes, shared projects. |
| v3 (Future) | Three-way merge UI | Manual resolution panel in settings. |

### 8.2 Last-Write-Wins (v1)

On conflict:
1. Server version replaces local version in IndexedDB.
2. Conflict logged with both versions.
3. UI shows toast: *"Your changes to [entity] conflicted with server. Server version kept."*
4. User can review conflict log and manually re-apply if needed.

### 8.3 CRDT Integration Path (v2)

- Use `yjs` or `automerge` for real-time collaborative note editing.
- Store CRDT state in IndexedDB alongside Supabase data.
- Sync via WebSocket (Supabase Realtime) for live collaboration.

---

## 9. Offline UX

### 9.1 Offline Banner

```typescript
// apps/web/components/OfflineBanner.tsx
export function OfflineBanner({ isOnline, queueCount }: Props) {
  if (isOnline && queueCount === 0) return null

  return (
    <motion.div
      initial={{ y: -60 }}
      animate={{ y: 0 }}
      className="fixed top-0 inset-x-0 z-50 px-4 py-2 bg-accent-neon/10 backdrop-blur-lg border-b border-accent-neon/30"
    >
      <p className="text-center text-sm text-accent-neon">
        {!isOnline
          ? 'You are offline. Changes will sync when reconnected.'
          : `${queueCount} change${queueCount > 1 ? 's' : ''} waiting to sync.`}
      </p>
    </motion.div>
  )
}
```

### 9.2 Queued Changes Indicator

- Sidebar icon shows badge with `sync_queue` count (status = queued).
- Sync icon shows spinning animation during `processing`.
- Toast on each successful sync: *"3 changes synced."*

### 9.3 Read-Only vs Full Offline CRUD

| State | Read | Create | Update | Delete |
|---|---|---|---|---|
| Online (connected) | Live data | ✓ | ✓ | ✓ |
| Online (slow) | Stale + revalidate | ✓ | ✓ | ✓ |
| Offline (cached) | Cached data | Queued | Queued | Queued |
| Offline (uncached) | Empty state | Blocked | Blocked | Blocked |

For offline CRUD, optimistic UI immediately reflects the change in IndexedDB, then the sync engine replays the mutation when reconnected.

---

## 10. Background Sync

### 10.1 Periodic Sync

```javascript
// public/sw.js — Periodic background sync
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'sync-secondbrain') {
    event.waitUntil(syncData())
  }
})

// Register from main thread
async function registerPeriodicSync() {
  const registration = await navigator.serviceWorker.ready
  if ('periodicSync' in registration) {
    await registration.periodicSync.register('sync-secondbrain', {
      minInterval: 15 * 60 * 1000 // 15 minutes
    })
  }
}
```

### 10.2 Sync on Reconnect

```javascript
window.addEventListener('online', () => {
  syncEngine.processQueue()
  // Also refresh data from server
  refreshCachedData()
})
```

### 10.3 Push Sync Trigger

Future enhancement: Supabase Realtime sends a push notification when data changes, triggering a cache refresh:

```typescript
supabase
  .channel('tasks_changes')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'tasks', filter: `user_id=eq.${userId}` },
    () => syncEngine.processQueue()
  )
  .subscribe()
```

---

## 11. Testing Offline

### 11.1 Chrome DevTools Offline Mode

- **DevTools > Network > Offline** — simulate disconnected state.
- **DevTools > Application > Service Workers** — inspect SW state, unregister, update on reload.
- **DevTools > Application > Cache Storage** — inspect cached API responses.
- **DevTools > Application > IndexedDB** — inspect offline data and sync queue.

### 11.2 Service Worker Tests (Vitest + `puppeteer`)

```typescript
// tests/offline/service-worker.test.ts
import { describe, it, expect } from 'vitest'

describe('Service Worker', () => {
  it('registers successfully', async () => {
    const registrations = await navigator.serviceWorker.getRegistrations()
    expect(registrations.length).toBe(1)
  })

  it('caches static assets on install', async () => {
    const cache = await caches.open('static-v1')
    const keys = await cache.keys()
    expect(keys.length).toBeGreaterThan(0)
  })
})
```

### 11.3 Sync Engine Tests

```typescript
// tests/offline/sync-engine.test.ts
describe('SyncEngine', () => {
  it('enqueues a CREATE operation', async () => {
    await syncEngine.enqueue({
      entity_type: 'tasks',
      entity_id: null,
      operation: 'CREATE',
      payload: { title: 'Test task', user_id: 'test_user' },
    })

    const queue = await db.sync_queue.toArray()
    expect(queue.length).toBe(1)
    expect(queue[0].status).toBe('queued')
  })

  it('processes queue when online', async () => {
    // Mock supabase to succeed
    mockSupabase.from('tasks').insert.mockResolvedValue({ data: [], error: null })

    await syncEngine.processQueue()
    const queue = await db.sync_queue.toArray()
    expect(queue.length).toBe(0) // dequeued
  })

  it('handles conflict with last-write-wins', async () => {
    // Mock version conflict
    mockSupabase.from('tasks').insert.mockRejectedValue({
      code: '409',
      message: 'version conflict',
    })

    await syncEngine.processQueue()
    const conflicts = await db.conflict_log.toArray()
    expect(conflicts.length).toBe(1)
    expect(conflicts[0].resolved).toBe(true) // server wins
  })
})
```

---

## 12. Appendices

### 12.1 IndexedDB Schema — Full Store Definitions

```typescript
interface DBSchema {
  tasks: {
    key: string
    indexes: {
      'by-user': string
      'by-status': string
      'by-updated': string
    }
  }
  habits: {
    key: string
    indexes: {
      'by-user': string
      'by-date': string
      'by-habit': string
    }
  }
  goals: {
    key: string
    indexes: {
      'by-user': string
      'by-status': string
    }
  }
  sync_queue: {
    key: string
    indexes: {
      'by-status': string
      'by-created': string
    }
  }
  conflict_log: {
    key: string
    indexes: {
      'by-entity': [string, string]
      'by-resolved': boolean
    }
  }
}
```

### 12.2 Service Worker Lifecycle

```
Installing  ──▶  Installed  ──▶  Activating  ──▶  Activated
    │                │                 │                │
    │          (waiting for           │           (handles all
    │           old SW to             │            fetches)
    │           release)              │
    ▼                                 ▼
  Fail                               Idle
                                       │
                                  (terminated
                                   after 30 s)
```

- **Install:** Cache static assets (app shell, fonts, icons).
- **Activate:** Delete old caches, claim uncontrolled clients.
- **Fetch:** Apply cache strategies (§5).
- **Message:** Receive sync triggers from main thread.

### 12.3 Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-06-11 | Architecture Team | Initial draft |
| — | — | — | — |

---

*End of Document — ENG-OFFLINE-001*
