import { create } from 'zustand'
import { chatService } from '@/lib/services'
import type { ChatMessage, Conversation } from '@/lib/types'

interface ChatStore {
  messages: ChatMessage[]
  conversations: Conversation[]
  activeConversationId: string | null
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  send: (message: string, conversationId?: string) => Promise<void>
  setActiveConversation: (id: string | null) => void
  clearMessages: () => void
}

const tempId = () => `local-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  conversations: [],
  activeConversationId: null,
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await chatService.list()
      const conversations: Conversation[] = (data || []).map((c: any) => ({
        id: c.id,
        user_id: '',
        title: c.title || 'Chat',
        lastMessage: c.lastMessage || '',
        timestamp: c.timestamp || new Date().toISOString(),
        messageCount: c.messageCount || 0,
        created_at: c.timestamp || new Date().toISOString(),
        updated_at: c.timestamp || new Date().toISOString(),
      }))
      set({ conversations, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load conversations'
      set({ error: message, loading: false })
    }
  },

  send: async (message, conversationId) => {
    const cid = conversationId || get().activeConversationId
    set({ loading: true, error: null })

    const userMessage: ChatMessage = {
      id: tempId(),
      user_id: '',
      conversation_id: cid || '',
      role: 'user',
      content: message,
      status: 'sent',
      created_at: new Date().toISOString(),
    }

    set({ messages: [...get().messages, userMessage] })

    try {
      const reply = await chatService.send(message, cid || undefined)
      set({
        messages: [...get().messages, reply],
        loading: false,
        activeConversationId: reply.conversation_id || cid,
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to send message'
      set({ error: message, loading: false })
    }
  },

  setActiveConversation: (id) => set({ activeConversationId: id }),

  clearMessages: () => set({ messages: [] }),
}))
