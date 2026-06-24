import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

const localStorageMap = new Map<string, string>()
const OLD_ENV_NODE = process.env.NODE_ENV
const OLD_ENV_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
const OLD_ENV_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST

beforeEach(() => {
  localStorageMap.clear()
  vi.spyOn(crypto, 'randomUUID').mockReturnValue('mock-uuid-123')
  vi.spyOn(console, 'debug').mockImplementation(() => {})
  vi.spyOn(console, 'warn').mockImplementation(() => {})
  vi.spyOn(console, 'error').mockImplementation(() => {})

  vi.spyOn(Storage.prototype, 'getItem').mockImplementation(
    (key: string) => localStorageMap.get(key) ?? null,
  )
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(
    (key: string, value: string) => { localStorageMap.set(key, value) },
  )
  vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(
    (key: string) => { localStorageMap.delete(key) },
  )
})

afterEach(() => {
  process.env.NODE_ENV = OLD_ENV_NODE
  process.env.NEXT_PUBLIC_POSTHOG_KEY = OLD_ENV_KEY
  process.env.NEXT_PUBLIC_POSTHOG_HOST = OLD_ENV_HOST
})

describe('analytics.sendEvent', () => {
  it('is a no-op without POSTHOG_KEY', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = ''
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.sendEvent('test_event')

    expect(console.debug).not.toHaveBeenCalled()
  })

  it('logs to console.debug in development mode', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.sendEvent('test_event', { key: 'val' })

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', 'test_event', { key: 'val' })
  })

  it('fires with event name only', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.sendEvent('test_event')

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', 'test_event', {})
  })
})

describe('analytics.trackPageView', () => {
  it('calls sendEvent with $pageview', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.trackPageView({ path: '/tasks', title: 'Tasks', referrer: 'https://example.com' })

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', '$pageview', {
      $pathname: '/tasks',
      $title: 'Tasks',
      $referrer: 'https://example.com',
    })
  })
})

describe('analytics.trackAction', () => {
  it('tracks action with name only', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.trackAction({ name: 'task_created' })

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', 'task_created', {})
  })

  it('tracks action with properties', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.trackAction({ name: 'task_completed', properties: { taskId: '123' } })

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', 'task_completed', { taskId: '123' })
  })
})

describe('analytics.identifyUser', () => {
  it('identifies user with $identify event', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.identifyUser('user-456')

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', '$identify', { $user_id: 'user-456' })
  })

  it('identifies user with traits', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.identifyUser('user-789', { email: 'test@example.com' })

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', '$identify', {
      $user_id: 'user-789',
      email: 'test@example.com',
    })
  })
})

describe('analytics - localStorage ID', () => {
  it('persists and reuses distinct ID', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()

    localStorageMap.set('sb-analytics-id', 'persisted-uuid-999')
    const { analytics } = await import('@/lib/analytics/index')

    analytics.sendEvent('test_event')

    expect(console.debug).toHaveBeenCalledWith('[Analytics]', 'test_event', {})
    expect(localStorageMap.get('sb-analytics-id')).toBe('persisted-uuid-999')
  })

  it('creates new ID if none exists', async () => {
    process.env.NEXT_PUBLIC_POSTHOG_KEY = 'test-key'
    process.env.NODE_ENV = 'development'
    vi.resetModules()
    const { analytics } = await import('@/lib/analytics/index')

    analytics.sendEvent('test_event')

    expect(localStorageMap.get('sb-analytics-id')).toBe('mock-uuid-123')
  })
})
