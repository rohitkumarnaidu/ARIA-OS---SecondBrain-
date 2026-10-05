import { create } from 'zustand'
import { chatService } from '@/lib/services'
import { aiStream } from '@/lib/ai/client'
import type { ChatMessage, Conversation, ConversationMessageRecord, ConversationSummary } from '@/lib/types'

/** messageCount of `id` in the given state, 0 when the conversation is absent. */
function conversationMessageCount(conversations: Conversation[], id: string): number {
  return conversations.find((c) => c.id === id)?.messageCount ?? 0
}

interface ChatStore {
  /** Transcript of the ACTIVE conversation, in send order. */
  messages: ChatMessage[]
  conversations: Conversation[]
  activeConversationId: string | null
  loading: boolean
  /** True while the active conversation's persisted transcript is being read. */
  messagesLoading: boolean
  error: string | null
  streamingContent: string
  streaming: boolean
  fetch: () => Promise<void>
  loadMessages: (conversationId: string) => Promise<void>
  send: (message: string, conversationId?: string, useStreaming?: boolean) => Promise<void>
  cancelStreaming: () => void
  setActiveConversation: (id: string | null) => void
  /** Create a local conversation with a real id and make it active. */
  startConversation: () => string
  clearMessages: () => void
}

const tempId = () => `local-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`

/**
 * Mint a server-shaped conversation id.
 *
 * The old code left `activeConversationId` as `undefined` on a brand-new thread
 * (`assistantMsg.conversation_id || cid` where `cid` was `undefined`), so
 * `conversations.find(c => c.id === undefined)` never matched, `activeConversation`
 * stayed null, and the entire chat UI -- including the streaming bubble -- was
 * unreachable from the welcome screen. A new conversation now always gets a real
 * id, both the user turn and the assistant turn carry it, and an optimistic
 * conversation object exists in `conversations` so the selector resolves.
 */
const newConversationId = (): string =>
  typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `conv-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`

function summaryToConversation(c: ConversationSummary): Conversation {
  const timestamp = c.timestamp || new Date().toISOString()
  return {
    id: c.id,
    user_id: '',
    title: c.title || 'Chat',
    lastMessage: c.lastMessage || '',
    timestamp,
    messageCount: c.messageCount || 0,
    created_at: timestamp,
    updated_at: timestamp,
  }
}

function recordToMessage(r: ConversationMessageRecord, conversationId: string): ChatMessage {
  return {
    id: r.id,
    user_id: r.user_id,
    conversation_id: r.conversation_id ?? conversationId,
    role: r.role === 'assistant' ? 'assistant' : 'user',
    content: r.content,
    agent_id: r.action_taken ?? undefined,
    status: 'sent',
    created_at: r.created_at,
  }
}

/** Mirror the tail of the transcript onto the sidebar entry so it stays live. */
function withConversationUpdate(
  conversations: Conversation[],
  id: string,
  patch: Partial<Conversation>
): Conversation[] {
  return conversations.map((c) => (c.id === id ? { ...c, ...patch } : c))
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  conversations: [],
  activeConversationId: null,
  loading: false,
  messagesLoading: false,
  error: null,
  streamingContent: '',
  streaming: false,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await chatService.list()
      const summaries: ConversationSummary[] = Array.isArray(data) ? data : []
      set({ conversations: summaries.map(summaryToConversation), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load conversations'
      set({ error: message, loading: false })
    }
  },

  loadMessages: async (conversationId) => {
    set({ messagesLoading: true })
    try {
      const transcript = await chatService.messages(conversationId)
      set({
        messages: transcript.messages.map((r) => recordToMessage(r, conversationId)),
        messagesLoading: false,
      })
    } catch (err: unknown) {
      // A 404 just means the conversation has no persisted rows yet (a brand
      // new thread). Keep the local transcript intact rather than blanking it.
      const message = err instanceof Error ? err.message : 'Failed to load messages'
      set({ messagesLoading: false, error: message })
    }
  },

  startConversation: () => {
    const id = newConversationId()
    const now = new Date().toISOString()
    const conversation: Conversation = {
      id,
      user_id: '',
      title: 'New conversation',
      lastMessage: '',
      timestamp: now,
      messageCount: 0,
      created_at: now,
      updated_at: now,
    }
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      activeConversationId: id,
      messages: [],
      streamingContent: '',
      streaming: false,
      error: null,
    }))
    return id
  },

  send: async (message, conversationId, useStreaming = false) => {
    // Resolve (or mint) the conversation id up front so both turns of this
    // exchange land in the same conversation.
    let cid = conversationId ?? get().activeConversationId
    if (!cid) cid = get().startConversation()
    set({ loading: true, error: null, streamingContent: '', streaming: false })

    const userMessage: ChatMessage = {
      id: tempId(),
      user_id: '',
      conversation_id: cid,
      role: 'user',
      content: message,
      status: 'sent',
      created_at: new Date().toISOString(),
    }

    set((state) => ({
      messages: [...state.messages, userMessage],
      conversations: state.conversations.some((c) => c.id === cid)
        ? withConversationUpdate(state.conversations, cid, {
            title: message.slice(0, 60),
            lastMessage: message,
            timestamp: userMessage.created_at,
            updated_at: userMessage.created_at,
            messageCount: conversationMessageCount(state.conversations, cid) + 1,
          })
        : state.conversations,
    }))

    if (useStreaming) {
      set({ streaming: true })
      try {
        await aiStream.sendMessage(
          message,
          cid,
          (chunk: string) => {
            set((state) => ({ streamingContent: state.streamingContent + chunk }))
          },
          (fullText: string) => {
            const assistantMsg: ChatMessage = {
              id: tempId(),
              user_id: '',
              // Always `cid`, never an optional that can collapse to undefined.
              conversation_id: cid,
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
              // `cid` is a string here, so this cannot become undefined.
              activeConversationId: cid,
              conversations: withConversationUpdate(state.conversations, cid, {
                lastMessage: fullText,
                timestamp: assistantMsg.created_at,
                updated_at: assistantMsg.created_at,
                messageCount: conversationMessageCount(state.conversations, cid) + 1,
              }),
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
        const reply = await chatService.send(message, cid)
        set((state) => ({
          messages: [...state.messages, reply],
          loading: false,
          activeConversationId: reply.conversation_id || cid,
          conversations: withConversationUpdate(state.conversations, cid, {
            lastMessage: reply.content,
            timestamp: reply.created_at,
            updated_at: reply.created_at,
            messageCount: conversationMessageCount(state.conversations, cid) + 1,
          }),
        }))
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

  setActiveConversation: (id) => set({ activeConversationId: id, messages: [], error: null }),

  clearMessages: () => set({ messages: [] }),
}))