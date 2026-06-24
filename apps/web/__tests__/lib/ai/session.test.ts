import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  persistSession,
  loadSession,
  getOrCreateSession,
  listSessions,
  switchSession,
  deleteSession,
  clearSession,
  getSessionContextForApi,
} from '@/lib/ai/session'

describe('session management', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-06-24T12:00:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // ─── getOrCreateSession ──────────────────────────────────────────────────

  it('getOrCreateSession creates a new session when none exists', () => {
    const session = getOrCreateSession()
    expect(session.id).toBeDefined()
    expect(session.lastPath).toBe('/')
    expect(session.lastChatId).toBeNull()
    expect(session.lastAgentCalls).toBe(0)
    expect(session.activePage).toBe('unknown')
    expect(session.metadata.created_at).toBe('2026-06-24T12:00:00.000Z')
    expect(session.metadata.message_count).toBe(0)
    expect(session.metadata.topics).toEqual([])
  })

  it('getOrCreateSession returns existing session', () => {
    const first = getOrCreateSession()
    const second = getOrCreateSession()
    expect(second.id).toBe(first.id)
  })

  // ─── persistSession ──────────────────────────────────────────────────────

  it('persistSession creates a session and updates path', () => {
    const session = persistSession('/dashboard/tasks', 'chat-1')
    expect(session.lastPath).toBe('/dashboard/tasks')
    expect(session.lastChatId).toBe('chat-1')
    expect(session.metadata.message_count).toBe(1)
  })

  it('persistSession updates existing session', () => {
    const first = persistSession('/page1', 'chat-1')
    const second = persistSession('/page2', 'chat-2')
    expect(second.id).toBe(first.id)
    expect(second.lastPath).toBe('/page2')
    expect(second.lastChatId).toBe('chat-2')
    expect(second.metadata.message_count).toBe(2)
  })

  it('persistSession accepts options', () => {
    const session = persistSession('/dashboard', null, {
      activePage: 'tasks',
      agentInteraction: 'planning',
      memorySnapshot: { tasks: [] },
      topic: 'work',
    })
    expect(session.activePage).toBe('tasks')
    expect(session.lastAgentInteraction).toBe('planning')
    expect(session.memorySnapshot).toEqual({ tasks: [] })
    expect(session.metadata.topics).toContain('work')
  })

  it('persistSession deduplicates topics', () => {
    persistSession('/a', null, { topic: 'work' })
    const session = persistSession('/a', null, { topic: 'work' })
    expect(session.metadata.topics).toEqual(['work'])
  })

  it('persistSession limits topics to 10', () => {
    for (let i = 0; i < 15; i++) {
      persistSession('/a', null, { topic: `topic-${i}` })
    }
    const s = persistSession('/a', null, { topic: 'final' })
    expect(s.metadata.topics.length).toBeLessThanOrEqual(10)
  })

  it('persistSession increments message_count', () => {
    const s1 = persistSession('/a')
    expect(s1.metadata.message_count).toBe(1)
    const s2 = persistSession('/b')
    expect(s2.metadata.message_count).toBe(2)
  })

  it('persistSession saves to session list', () => {
    persistSession('/a')
    const raw = localStorage.getItem('aria-sessions')
    expect(JSON.parse(raw || '{}')).toBeDefined()
  })

  // ─── loadSession ─────────────────────────────────────────────────────────

  it('loadSession returns current session', () => {
    const created = persistSession('/test')
    const loaded = loadSession()
    expect(loaded?.id).toBe(created.id)
  })

  it('loadSession returns null when no session exists', () => {
    const loaded = loadSession()
    expect(loaded).toBeNull()
  })

  it('loadSession loads from URL param', () => {
    const created = persistSession('/test')
    localStorage.removeItem('aria-session-state')
    Object.defineProperty(window, 'location', {
      value: { search: `?session=${created.id}` },
      writable: true,
      configurable: true,
    })
    const loaded = loadSession()
    expect(loaded?.id).toBe(created.id)
  })

  // ─── listSessions ────────────────────────────────────────────────────────

  it('listSessions returns all sessions sorted by updated_at desc', () => {
    // Need clearSession between each to create distinct sessions
    vi.setSystemTime(new Date('2026-06-24T10:00:00Z'))
    persistSession('/a')
    clearSession()

    vi.setSystemTime(new Date('2026-06-24T12:00:00Z'))
    persistSession('/b')
    clearSession()

    vi.setSystemTime(new Date('2026-06-24T11:00:00Z'))
    persistSession('/c')

    const sessions = listSessions()
    expect(sessions.length).toBe(3)
    // 12:00 > 11:00 > 10:00
    expect(sessions[0].lastPath).toBe('/b')
    expect(sessions[1].lastPath).toBe('/c')
    expect(sessions[2].lastPath).toBe('/a')
  })

  it('listSessions returns empty array when no sessions', () => {
    expect(listSessions()).toEqual([])
  })

  // ─── switchSession ───────────────────────────────────────────────────────

  it('switchSession activates a different session', () => {
    const first = persistSession('/first')
    clearSession()
    const second = persistSession('/second')
    const switched = switchSession(first.id)
    expect(switched?.id).toBe(first.id)
  })

  it('switchSession returns null for unknown session', () => {
    expect(switchSession('nonexistent')).toBeNull()
  })

  // ─── deleteSession ───────────────────────────────────────────────────────

  it('deleteSession removes session from list', () => {
    const session = persistSession('/test')
    deleteSession(session.id)
    const sessions = listSessions()
    expect(sessions.find(s => s.id === session.id)).toBeUndefined()
  })

  it('deleteSession clears current if it matches', () => {
    const session = persistSession('/test')
    deleteSession(session.id)
    expect(localStorage.getItem('aria-session-state')).toBeNull()
  })

  // ─── clearSession ────────────────────────────────────────────────────────

  it('clearSession removes current session from storage', () => {
    persistSession('/test')
    clearSession()
    expect(localStorage.getItem('aria-session-state')).toBeNull()
  })

  // ─── getSessionContextForApi ─────────────────────────────────────────────

  it('getSessionContextForApi returns empty object when no session', () => {
    expect(getSessionContextForApi()).toEqual({})
  })

  it('getSessionContextForApi returns session context', () => {
    persistSession('/dashboard', 'chat-1', {
      activePage: 'tasks',
      agentInteraction: 'briefing',
      topic: 'work',
    })
    const ctx = getSessionContextForApi()
    expect(ctx.session_id).toBeDefined()
    expect(ctx.interaction_count).toBe(1)
    expect(ctx.active_page).toBe('tasks')
    expect(ctx.last_agent_interaction).toBe('briefing')
    expect(ctx.topics).toContain('work')
  })

  // ─── Edge cases ──────────────────────────────────────────────────────────

  it('prunes sessions older than 24 hours', () => {
    const id1 = persistSession('/old').id
    vi.advanceTimersByTime(25 * 60 * 60 * 1000)
    persistSession('/new')
    const sessions = listSessions()
    expect(sessions.find(s => s.id === id1)).toBeUndefined()
    expect(sessions.length).toBe(1)
  })

  it('clearSession is safe when no session exists', () => {
    expect(() => clearSession()).not.toThrow()
  })

  it('handles localStorage getItem errors gracefully', () => {
    const orig = localStorage.getItem
    localStorage.getItem = vi.fn(() => { throw new Error('storage error') })
    expect(loadSession()).toBeNull()
    expect(listSessions()).toEqual([])
    localStorage.getItem = orig
  })

  it('handles localStorage setItem errors gracefully', () => {
    const orig = localStorage.setItem
    localStorage.setItem = vi.fn(() => { throw new Error('quota exceeded') })
    expect(() => persistSession('/test')).not.toThrow()
    localStorage.setItem = orig
  })

  it('persistSession preserves previous chatId when null passed', () => {
    const s1 = persistSession('/a', 'chat-keep')
    const s2 = persistSession('/b', null)
    expect(s2.lastChatId).toBe('chat-keep')
  })
})
