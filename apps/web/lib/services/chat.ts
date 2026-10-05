import { api } from '@/lib/api'
import type { ChatMessage, ConversationSummary, ConversationTranscript } from '@/lib/types'

const BASE = '/api/v1/chat'

export const chatService = {
  list: (): Promise<ConversationSummary[]> => api.get<ConversationSummary[]>(BASE),

  /** Full persisted transcript for one conversation, oldest first. */
  messages: (conversationId: string, limit = 100, offset = 0): Promise<ConversationTranscript> =>
    api.get<ConversationTranscript>(`${BASE}/${encodeURIComponent(conversationId)}`, {
      params: { limit, offset },
    }),

  send: (message: string, conversationId?: string): Promise<ChatMessage> =>
    api.post<ChatMessage>(BASE, { message, conversation_id: conversationId }),
}