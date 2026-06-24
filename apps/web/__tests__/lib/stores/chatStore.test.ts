import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useChatStore } from '@/lib/stores/chatStore'

const mockList = vi.fn()
const mockSend = vi.fn()

vi.mock('@/lib/services/chat', () => ({
  chatService: {
    list: (...args: unknown[]) => mockList(...args),
    send: (...args: unknown[]) => mockSend(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useChatStore.setState({
    messages: [],
    conversations: [],
    activeConversationId: null,
    loading: false,
    error: null,
  })
})

describe('chatStore', () => {
  it('has correct initial state', () => {
    const s = useChatStore.getState()
    expect(s.messages).toEqual([])
    expect(s.conversations).toEqual([])
    expect(s.activeConversationId).toBeNull()
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetch loads conversations and sets loading', async () => {
    const conversations = [
      { id: 'c1', title: 'Chat 1', lastMessage: 'Hi', timestamp: '2026-01-01T00:00:00Z', messageCount: 2 },
    ]
    mockList.mockResolvedValueOnce(conversations)
    await useChatStore.getState().fetch()
    const s = useChatStore.getState()
    expect(s.loading).toBe(false)
    expect(s.conversations).length(1)
    expect(s.conversations[0].id).toBe('c1')
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('Network error'))
    await useChatStore.getState().fetch()
    const s = useChatStore.getState()
    expect(s.error).toBe('Network error')
    expect(s.loading).toBe(false)
  })

  it('send appends user message and reply', async () => {
    mockSend.mockResolvedValueOnce({
      id: 'r1', conversation_id: 'c1', role: 'assistant', content: 'Reply', status: 'sent', created_at: new Date().toISOString(),
    })
    await useChatStore.getState().send('Hello', 'c1')
    const s = useChatStore.getState()
    expect(s.messages).length(2)
    expect(s.messages[0].role).toBe('user')
    expect(s.messages[0].content).toBe('Hello')
    expect(s.messages[1].role).toBe('assistant')
    expect(s.loading).toBe(false)
  })

  it('send uses activeConversationId when no cid given', async () => {
    useChatStore.setState({ activeConversationId: 'c2' })
    mockSend.mockResolvedValueOnce({
      id: 'r2', conversation_id: 'c2', role: 'assistant', content: 'Yes', status: 'sent', created_at: new Date().toISOString(),
    })
    await useChatStore.getState().send('Test')
    expect(mockSend).toHaveBeenCalledWith('Test', 'c2')
  })

  it('send sets error on failure', async () => {
    mockSend.mockRejectedValueOnce(new Error('Send failed'))
    await useChatStore.getState().send('Hi', 'c1')
    expect(useChatStore.getState().error).toBe('Send failed')
    expect(useChatStore.getState().loading).toBe(false)
  })

  it('setActiveConversation updates the id', () => {
    useChatStore.getState().setActiveConversation('conv-1')
    expect(useChatStore.getState().activeConversationId).toBe('conv-1')
    useChatStore.getState().setActiveConversation(null)
    expect(useChatStore.getState().activeConversationId).toBeNull()
  })

  it('clearMessages empties messages', () => {
    useChatStore.setState({ messages: [{ id: 'm1', user_id: '', conversation_id: '', role: 'user', content: 'x', status: 'sent', created_at: '' }] })
    useChatStore.getState().clearMessages()
    expect(useChatStore.getState().messages).toEqual([])
  })
})
