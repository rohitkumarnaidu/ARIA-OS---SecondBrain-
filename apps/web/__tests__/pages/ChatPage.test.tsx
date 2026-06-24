import { describe, it, vi, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({ user: { id: '1' }, loading: false })),
}))

vi.mock('@/lib/ai/orchestrator', () => ({
  orchestrator: { processMessage: vi.fn() },
}))

vi.mock('@/lib/stores', () => ({
  useChatStore: vi.fn(() => ({
    conversations: [], activeConversationId: null, loading: false, error: null,
    send: vi.fn(), fetch: vi.fn(), setActiveConversation: vi.fn(),
  })),
  useTaskStore: vi.fn(() => ({
    tasks: [], loading: false, error: null,
    fetchTasks: vi.fn(), getById: vi.fn(),
    addTask: vi.fn(), updateTask: vi.fn(),
    deleteTask: vi.fn(), completeTask: vi.fn(),
  })),
  useHabitStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(), log: vi.fn(),
  })),
  useMemoryStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), remove: vi.fn(), update: vi.fn(),
  })),
  useCourseStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
  useGoalStore: vi.fn(() => ({
    items: [], loading: false, error: null,
    fetch: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn(),
  })),
}))

vi.mock('@/components/ai/GhostHint', () => ({
  GhostHint: () => <div data-testid="ghost-hint" />,
}))

vi.mock('@/components/ai/SuggestionChips', () => ({
  SuggestionChips: () => <div data-testid="suggestion-chips" />,
}))

vi.mock('@/components/feedback/FeedbackWidget', () => ({
  FeedbackWidget: () => <div data-testid="feedback-widget" />,
}))

import ChatPage from '../../app/(dashboard)/chat/page'

describe('ChatPage', () => {
  it('renders without crashing', () => {
    const { container } = render(<ChatPage />)
    expect(container).toBeTruthy()
  })
})
