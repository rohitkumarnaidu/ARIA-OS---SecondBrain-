import { QueryClient } from '@tanstack/react-query'

function queryErrorHandler(error: unknown) {
  if (process.env.NODE_ENV === 'production') {
    import('@sentry/nextjs').then((Sentry) => {
      Sentry.captureException(error, { tags: { source: 'tanstack-query' } })
    })
  }
}

export function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: 2,
        retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10000),
        refetchOnWindowFocus: false,
      },
      mutations: {
        onError: queryErrorHandler,
      },
    },
  })
}
