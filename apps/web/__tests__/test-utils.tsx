import { type ReactElement, type ReactNode } from 'react'
import { render as rtlRender, type RenderOptions, type RenderResult, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent, { type UserEvent } from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/theme/ThemeProvider'

// ─── Providers ──────────────────────────────────────────────────────────────

interface AllProvidersProps {
  children: ReactNode
  queryClient?: QueryClient
}

function AllTheProviders({ children, queryClient }: AllProvidersProps) {
  const qc = queryClient ?? createTestQueryClient()

  return (
    <QueryClientProvider client={qc}>
      <ThemeProvider>{children}</ThemeProvider>
    </QueryClientProvider>
  )
}

// ─── QueryClient ────────────────────────────────────────────────────────────

function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
        refetchOnWindowFocus: false,
      },
    },
  })
}

// ─── Custom Render ──────────────────────────────────────────────────────────

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  withTheme?: boolean
  withQuery?: boolean
}

function render(ui: ReactElement, options?: CustomRenderOptions): RenderResult {
  const { withTheme = true, withQuery = true, ...rtlOptions } = options ?? {}

  if (!withTheme && !withQuery) {
    return rtlRender(ui, rtlOptions)
  }

  const queryClient = createTestQueryClient()

  function Wrapper({ children }: { children: ReactNode }) {
    let content = children
    if (withQuery) {
      content = <QueryClientProvider client={queryClient}>{content}</QueryClientProvider>
    }
    if (withTheme) {
      content = <ThemeProvider>{content}</ThemeProvider>
    }
    return <>{content}</>
  }

  return rtlRender(ui, { wrapper: Wrapper, ...rtlOptions })
}

// ─── User Event ──────────────────────────────────────────────────────────────

function createUser(): UserEvent {
  return userEvent.setup()
}

// ─── Re-exports ──────────────────────────────────────────────────────────────

export { render, createUser, createTestQueryClient }
export { screen, cleanup, act, fireEvent, waitFor, within } from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
export type { UserEvent }
