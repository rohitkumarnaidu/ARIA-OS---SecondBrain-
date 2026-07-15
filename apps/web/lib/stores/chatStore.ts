import { create } from 'zustand'
import { chatService } from '@/lib/services'
import { aiStream } from '@/lib/ai/client'
import type { ChatMessage, Conversation } from '@/lib/types'

interface ChatStore {
  messages: ChatMessage[]
  conversations: Conversation[]
  activeConversationId: string | null
  loading: boolean
  error: string | null
  streamingContent: string
  streaming: boolean
  fetch: () => Promise<void>
  send: (message: string, conversationId?: string, useStreaming?: boolean) => Promise<void>
  cancelStreaming: () => void
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
  streamingContent: '',
  streaming: false,

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

  send: async (message, conversationId, useStreaming = false) => {
    const cid = conversationId || get().activeConversationId
    set({ loading: true, error: null, streamingContent: '', streaming: false })

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

    if (useStreaming) {
      set({ streaming: true })
      try {
        await aiStream.sendMessage(
          message,
          cid || undefined,
          (chunk: string) => {
            set((state) => ({ streamingContent: state.streamingContent + chunk }))
          },
          (fullText: string) => {
            const assistantMsg: ChatMessage = {
              id: tempId(),
              user_id: '',
              conversation_id: cid || '',
              role: 'assistant',
              content: fullText,
              status: 'sent',
              created_at: new Date().toISOString(),
            }
            set((state) => ({
              messages: [...state.messages, assistantMsg],
              loading: false,
              streaming: false,
              streamingContent: '',
              activeConversationId: assistantMsg.conversation_id || cid,
            }))
          },
          (error: Error) => {
            set({ error: error.message, loading: false, streaming: false, streamingContent: '' })
          },
        )
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to send message'
        set({ error: msg, loading: false, streaming: false, streamingContent: '' })
      }
    } else {
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
    }
  },

  cancelStreaming: () => {
    aiStream.cancel()
    set({ loading: false, streaming: false, streamingContent: '' })
  },

  setActiveConversation: (id) => set({ activeConversationId: id }),

  clearMessages: () => set({ messages: [] }),
}))
