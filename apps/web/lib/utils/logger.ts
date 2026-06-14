type LogLevel = 'debug' | 'info' | 'warn' | 'error'

class Logger {
  constructor(private module: string) {}

  private sanitize(context: Record<string, unknown>): Record<string, unknown> {
    const sensitive = ['password', 'token', 'secret', 'key', 'authorization', 'cookie']
    const result: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(context)) {
      result[key] = sensitive.some((s) => key.toLowerCase().includes(s)) ? '[REDACTED]' : value
    }
    return result
  }

  private log(level: LogLevel, message: string, context?: Record<string, unknown>) {
    const sanitized = context ? this.sanitize(context) : undefined
    const prefix = `[${this.module}]`

    switch (level) {
      case 'debug':
        if (process.env.NODE_ENV === 'development') console.debug(prefix, message, sanitized || '')
        break
      case 'info':
        console.info(prefix, message, sanitized || '')
        break
      case 'warn':
        console.warn(prefix, message, sanitized || '')
        break
      case 'error':
        console.error(prefix, message, sanitized || '')
        if (process.env.NODE_ENV === 'production') {
          import('@sentry/nextjs').then((Sentry) => {
            Sentry.captureMessage(message, { level: 'error', tags: { module: this.module }, extra: sanitized })
          })
        }
        break
    }
  }

  debug(message: string, context?: Record<string, unknown>) { this.log('debug', message, context) }
  info(message: string, context?: Record<string, unknown>) { this.log('info', message, context) }
  warn(message: string, context?: Record<string, unknown>) { this.log('warn', message, context) }
  error(message: string, context?: Record<string, unknown>) { this.log('error', message, context) }
}

export function createLogger(module: string) {
  return new Logger(module)
}
