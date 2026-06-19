# Integration Tests

This directory contains integration tests that exercise full component flows
with MSW (Mock Service Worker) intercepting network requests at the HTTP level.

## Pattern

```ts
import { beforeAll, afterAll, afterEach } from 'vitest'
import { server } from '@/__tests__/mocks'
import { render, screen } from '@/__tests__/test-utils'
import { buildTask, buildList } from '@/__tests__/factories'

// Start MSW before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

it('loads and displays data', async () => {
  // Use factories for test data
  const tasks = buildList(buildTask, 3)
  server.use(http.get('*/rest/v1/tasks', () => HttpResponse.json(tasks)))

  // Render with providers
  render(<Component />)

  // Assert loading → data states
  expect(screen.getByRole('status')).toBeInTheDocument()
  await waitFor(() => {
    expect(screen.getByText(tasks[0].title)).toBeInTheDocument()
  })
})
```

## Running

```bash
npm run test:integration
```
