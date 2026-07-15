import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '@/__tests__/mocks/server'
import ChatPage from '@/app/(dashboard)/chat/page'

const mockSetActiveConversation = vi.fn()
const mockSend = vi.fn()
const mockFetch = vi.fn()

const mockStore = {
  conversations: [],
  activeConversationId: null,
  loading: false,
  error: null,
  setActiveConversation: mockSetActiveConversation,
  send: mockSend,
  fetch: mockFetch,
}

vi.mock('@/lib/stores/chatStore', () => ({
  useChatStore: (selector?: (s: Record<string, unknown>) => unknown) => selector ? selector(mockStore) : mockStore,
}))

function mockStoreSelector<T>(store: T) {
  return (selector?: (s: T) => unknown) => (selector ? selector(store) : store)
}

vi.mock('@/lib/stores/taskStore', () => ({
  useTaskStore: mockStoreSelector({ tasks: [], fetchTasks: vi.fn() }),
}))

vi.mock('@/lib/stores/habitStore', () => ({
  useHabitStore: mockStoreSelector({ items: [], fetch: vi.fn() }),
}))

vi.mock('@/lib/stores/memoryStore', () => ({
  useMemoryStore: mockStoreSelector({ items: [], fetch: vi.fn() }),
}))

vi.mock('@/lib/stores/courseStore', () => ({
  useCourseStore: mockStoreSelector({ items: [], fetch: vi.fn() }),
}))

vi.mock('@/lib/stores/goalStore', () => ({
  useGoalStore: (selector?: (s: Record<string, unknown>) => unknown) =>
    selector ? selector({ items: [], fetch: vi.fn() }) : { items: [], fetch: vi.fn() },
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn(), forward: vi.fn(), refresh: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => '/chat',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}))

vi.mock('@/components/ai/GhostHint', () => ({
  GhostHint: ({ state, onAccept, onDismiss }: { state: string; onAccept: () => void; onDismiss: () => void }) =>
    state === 'visible' ? <div data-testid="ghost-hint">Ghost Hint</div> : null,
}))

vi.mock('@/components/ai/SuggestionChips', () => ({
  SuggestionChips: ({ suggestions, onSelect }: { suggestions: Array<{ id: string; label: string }>; onSelect: (id: string) => void }) => (
    <div data-testid="suggestion-chips">
      {suggestions.map(s => (
        <button key={s.id} onClick={() => onSelect(s.id)} data-testid={`chip-${s.id}`}>{s.label}</button>
      ))}
    </div>
  ),
  default: undefined,
}))

vi.mock('@/components/feedback/FeedbackWidget', () => ({
  FeedbackWidget: () => null,
}))

vi.mock('@/lib/utils/logger', () => ({
  createLogger: () => ({ info: vi.fn(), error: vi.fn() }),
}))

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => { server.resetHandlers(); vi.clearAllMocks() })
afterAll(() => server.close())

describe('AI Chat Flow Integration', () => {
  it('renders welcome screen when no active conversation', () => {
    render(<ChatPage />)
    expect(screen.getByText('How can I help you today?')).toBeInTheDocument()
  })

  it('renders branding and subtitle', () => {
    render(<ChatPage />)
    expect(screen.getByText('ARIA')).toBeInTheDocument()
    expect(screen.getByText(/tasks, goals, courses/i)).toBeInTheDocument()
  })

  it('renders suggestion chips on welcome screen', () => {
    render(<ChatPage />)
    expect(screen.getByTestId('chip-plan-week')).toBeInTheDocument()
    expect(screen.getByTestId('chip-review-tasks')).toBeInTheDocument()
    expect(screen.getByTestId('chip-find-opportunities')).toBeInTheDocument()
  })

  it('renders quick action cards', () => {
    render(<ChatPage />)
    expect(screen.getByText('Generate Briefing')).toBeInTheDocument()
    expect(screen.getByText('Run Weekly Review')).toBeInTheDocument()
    expect(screen.getByText('Check Radar')).toBeInTheDocument()
  })

  it('renders conversation sidebar', () => {
    render(<ChatPage />)
    expect(screen.getByText('Conversations')).toBeInTheDocument()
    expect(screen.getByText('New Thread')).toBeInTheDocument()
  })

  it('renders session context panel', () => {
    render(<ChatPage />)
    expect(screen.getByText('Session Context')).toBeInTheDocument()
    expect(screen.getByText('System Context')).toBeInTheDocument()
    expect(screen.getByText('Memory Stats')).toBeInTheDocument()
  })

  it('renders New Thread button', () => {
    render(<ChatPage />)
    const newThreadBtn = screen.getByRole('button', { name: /start new conversation/i })
    expect(newThreadBtn).toBeInTheDocument()
  })

  it('calls fetch on mount', () => {
    render(<ChatPage />)
    expect(mockFetch).toHaveBeenCalled()
  })
})
