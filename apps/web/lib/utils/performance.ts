export function measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
  const start = performance.now()
  return fn().finally(() => {
    const duration = performance.now() - start
    if (process.env.NODE_ENV === 'production') {
      import('@sentry/nextjs').then((Sentry) => {
        Sentry.metrics.distribution(`perf.${name}`, duration)
      })
    }
  })
}
