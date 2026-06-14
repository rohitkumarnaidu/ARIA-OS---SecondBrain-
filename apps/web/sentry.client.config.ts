import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN || '',
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.25 : 0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: process.env.NODE_ENV === 'production'
    ? [Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true }), Sentry.browserTracingIntegration()]
    : [],
  enabled: process.env.NODE_ENV === 'production',
  beforeSend(event) {
    if (event.request?.headers) {
      delete event.request.headers['Authorization']
      delete event.request.headers['Cookie']
    }
    if (event.user) {
      event.user = { id: event.user.id }
    }
    return event
  },
})
