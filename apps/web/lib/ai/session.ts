export interface SessionMetadata {
  created_at: string
  updated_at: string
  message_count: number
  topics: string[]
}

export interface SessionState {
  id: string
  lastPath: string
  lastChatId: string | null
  lastAgentCalls: number
  activePage: string
  lastAgentInteraction: string | null
  memorySnapshot: Record<string, unknown>
  resumedAt: string
  metadata: SessionMetadata
}

const STORAGE_KEY = 'aria-session-state'
const SESSION_LIST_KEY = 'aria-sessions'
const MAX_SESSION_AGE_MS = 24 * 60 * 60 * 1000

function generateId(): string {
  try {
    return crypto.randomUUID()
  } catch {
    return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
  }
}

function nowISO(): string {
  return new Date().toISOString()
}

function getAllSessions(): Record<string, SessionState> {
  try {
    const raw = localStorage.getItem(SESSION_LIST_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function saveAllSessions(sessions: Record<string, SessionState>): void {
  try {
    localStorage.setItem(SESSION_LIST_KEY, JSON.stringify(sessions))
  } catch {
    /* noop */
  }
}

function createDefaultSession(): SessionState {
  return {
    id: generateId(),
    lastPath: '/',
    lastChatId: null,
    lastAgentCalls: 0,
    activePage: 'unknown',
    lastAgentInteraction: null,
    memorySnapshot: {},
    resumedAt: nowISO(),
    metadata: {
      created_at: nowISO(),
      updated_at: nowISO(),
      message_count: 0,
      topics: [],
    },
  }
}

function loadCurrentSessionRaw(): SessionState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as SessionState) : null
  } catch {
    return null
  }
}

function saveCurrentSessionRaw(state: SessionState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    /* noop */
  }
}

function pruneExpiredSessions(): void {
  try {
    const sessions = getAllSessions()
    const now = Date.now()
    let changed = false
    for (const [id, session] of Object.entries(sessions)) {
      const updated = new Date(session.metadata.updated_at).getTime()
      if (now - updated > MAX_SESSION_AGE_MS) {
        delete sessions[id]
        changed = true
      }
    }
    if (changed) {
      saveAllSessions(sessions)
      const current = loadCurrentSessionRaw()
      if (current && !sessions[current.id]) {
        clearSession()
      }
    }
  } catch {
    /* noop */
  }
}

export function persistSession(
  path: string,
  chatId: string | null = null,
  options?: {
    activePage?: string
    agentInteraction?: string
    memorySnapshot?: Record<string, unknown>
    topic?: string
  }
): SessionState {
  pruneExpiredSessions()
  let state = loadCurrentSessionRaw()
  if (!state) {
    state = createDefaultSession()
  }
  state.lastPath = path
  state.lastChatId = chatId ?? state.lastChatId
  state.lastAgentCalls = (state.lastAgentCalls ?? 0) + 1
  state.resumedAt = nowISO()
  state.metadata.updated_at = nowISO()

  if (options?.activePage) {
    state.activePage = options.activePage
  }
  if (options?.agentInteraction) {
    state.lastAgentInteraction = options.agentInteraction
  }
  if (options?.memorySnapshot) {
    state.memorySnapshot = options.memorySnapshot
  }

  state.metadata.message_count += 1
  if (options?.topic && !state.metadata.topics.includes(options.topic)) {
    state.metadata.topics.push(options.topic)
    if (state.metadata.topics.length > 10) {
      state.metadata.topics = state.metadata.topics.slice(-10)
    }
  }

  saveCurrentSessionRaw(state)
  const sessions = getAllSessions()
  sessions[state.id] = state
  saveAllSessions(sessions)
  return state
}

export function loadSession(): SessionState | null {
  pruneExpiredSessions()
  let state = loadCurrentSessionRaw()
  if (state) return state
  try {
    const params = new URLSearchParams(window.location.search)
    const sessionId = params.get('session')
    if (sessionId) {
      const sessions = getAllSessions()
      state = sessions[sessionId] ?? null
      if (state) {
        saveCurrentSessionRaw(state)
        return state
      }
    }
  } catch {
    /* noop */
  }
  return null
}

export function getOrCreateSession(): SessionState {
  const existing = loadSession()
  if (existing) return existing
  const state = createDefaultSession()
  saveCurrentSessionRaw(state)
  const sessions = getAllSessions()
  sessions[state.id] = state
  saveAllSessions(sessions)
  return state
}

export function listSessions(): SessionState[] {
  pruneExpiredSessions()
  const sessions = getAllSessions()
  return Object.values(sessions).sort(
    (a, b) => new Date(b.metadata.updated_at).getTime() - new Date(a.metadata.updated_at).getTime()
  )
}

export function switchSession(sessionId: string): SessionState | null {
  const sessions = getAllSessions()
  const session = sessions[sessionId]
  if (!session) return null
  saveCurrentSessionRaw(session)
  return session
}

export function deleteSession(sessionId: string): void {
  const sessions = getAllSessions()
  delete sessions[sessionId]
  saveAllSessions(sessions)
  const current = loadCurrentSessionRaw()
  if (current && current.id === sessionId) {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export function clearSession(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* noop */
  }
}

export function getSessionContextForApi(): Record<string, unknown> {
  const session = loadSession()
  if (!session) return {}
  return {
    session_id: session.id,
    session_start: session.metadata.created_at,
    interaction_count: session.metadata.message_count,
    active_page: session.activePage,
    last_agent_interaction: session.lastAgentInteraction,
    topics: session.metadata.topics,
  }
}
