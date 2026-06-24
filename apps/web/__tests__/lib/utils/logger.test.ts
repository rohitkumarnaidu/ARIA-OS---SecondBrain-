import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createLogger } from '@/lib/utils/logger'

const OLD_ENV = process.env.NODE_ENV

beforeEach(() => {
  vi.restoreAllMocks()
  process.env.NODE_ENV = 'development'
})

afterEach(() => {
  process.env.NODE_ENV = OLD_ENV
})

describe('createLogger', () => {
  it('creates a logger with a module name', () => {
    const logger = createLogger('test-module')
    expect(logger).toBeDefined()
  })

  it('different instances have different module prefixes', () => {
    const logger1 = createLogger('module-a')
    const logger2 = createLogger('module-b')
    // Both work independently
    const spy1 = vi.spyOn(console, 'debug').mockImplementation(() => {})
    logger1.debug('msg')
    expect(spy1).toHaveBeenCalledWith('[module-a]', 'msg', '')
  })
})

describe('log levels', () => {
  it('debug logs in development', () => {
    const spy = vi.spyOn(console, 'debug').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.debug('test message')
    expect(spy).toHaveBeenCalledWith('[test]', 'test message', '')
  })

  it('debug does not log in production', () => {
    process.env.NODE_ENV = 'production'
    const spy = vi.spyOn(console, 'debug').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.debug('test message')
    expect(spy).not.toHaveBeenCalled()
  })

  it('info logs in any environment', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('info message')
    expect(spy).toHaveBeenCalledWith('[test]', 'info message', '')
  })

  it('warn logs in any environment', () => {
    const spy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.warn('warn message')
    expect(spy).toHaveBeenCalledWith('[test]', 'warn message', '')
  })

  it('error logs in any environment', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.error('error message')
    expect(spy).toHaveBeenCalledWith('[test]', 'error message', '')
  })
})

describe('structured log format', () => {
  it('includes context object when provided', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('msg', { userId: '123', action: 'login' })
    expect(spy).toHaveBeenCalledWith('[test]', 'msg', { userId: '123', action: 'login' })
  })

  it('includes empty string when context is omitted', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('msg')
    expect(spy).toHaveBeenCalledWith('[test]', 'msg', '')
  })

  it('handles undefined context gracefully', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('msg', undefined)
    expect(spy).toHaveBeenCalledWith('[test]', 'msg', '')
  })
})

describe('redaction', () => {
  it('redacts password field', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('login', { password: 'supersecret' })
    expect(spy).toHaveBeenCalledWith('[test]', 'login', { password: '[REDACTED]' })
  })

  it('redacts token field', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('auth', { access_token: 'abc123' })
    expect(spy).toHaveBeenCalledWith('[test]', 'auth', { access_token: '[REDACTED]' })
  })

  it('redacts secret field', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('config', { secret_key: 'my-key' })
    expect(spy).toHaveBeenCalledWith('[test]', 'config', { secret_key: '[REDACTED]' })
  })

  it('redacts authorization field', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('request', { Authorization: 'Bearer xxx' })
    expect(spy).toHaveBeenCalledWith('[test]', 'request', { Authorization: '[REDACTED]' })
  })

  it('does not redact non-sensitive fields', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('event', { userId: '123', email: 'test@example.com' })
    expect(spy).toHaveBeenCalledWith('[test]', 'event', { userId: '123', email: 'test@example.com' })
  })

  it('redacts key field (any casing)', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('api', { API_KEY: 'sk-xxx' })
    expect(spy).toHaveBeenCalledWith('[test]', 'api', { API_KEY: '[REDACTED]' })
  })

  it('redacts cookie field', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    logger.info('req', { cookie: 'session=abc' })
    expect(spy).toHaveBeenCalledWith('[test]', 'req', { cookie: '[REDACTED]' })
  })

  it('preserves non-sensitive values unchanged', () => {
    const spy = vi.spyOn(console, 'info').mockImplementation(() => {})
    const logger = createLogger('test')
    const context = { userId: '456', role: 'admin', count: 42 }
    logger.info('test', context)
    expect(spy).toHaveBeenCalledWith('[test]', 'test', context)
  })
})
