import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, useQueryClient } from '@tanstack/react-query'
import { QueryProvider } from '@/lib/query/QueryProvider'

describe('QueryProvider', () => {
  it('renders children', () => {
    render(
      <QueryProvider>
        <div data-testid="child">Hello</div>
      </QueryProvider>,
    )
    expect(screen.getByTestId('child')).toBeTruthy()
    expect(screen.getByText('Hello')).toBeTruthy()
  })

  it('provides query client context', () => {
    function Consumer() {
      const queryClient = useQueryClient()
      return <div data-testid="consumer">{queryClient ? 'has client' : 'no client'}</div>
    }

    render(
      <QueryProvider>
        <Consumer />
      </QueryProvider>,
    )
    expect(screen.getByTestId('consumer').textContent).toBe('has client')
  })

  it('query client has default staleTime', () => {
    let capturedClient: QueryClient | null = null

    function Consumer() {
      capturedClient = useQueryClient()
      return null
    }

    render(
      <QueryProvider>
        <Consumer />
      </QueryProvider>,
    )
    expect(capturedClient).not.toBeNull()
    expect(capturedClient!.getDefaultOptions().queries?.staleTime).toBe(30 * 1000)
  })

  it('renders complex children', () => {
    render(
      <QueryProvider>
        <div data-testid="parent">
          <span data-testid="child1">A</span>
          <span data-testid="child2">B</span>
        </div>
      </QueryProvider>,
    )
    expect(screen.getByTestId('parent')).toBeTruthy()
    expect(screen.getByTestId('child1')).toBeTruthy()
    expect(screen.getByTestId('child2')).toBeTruthy()
  })
})
