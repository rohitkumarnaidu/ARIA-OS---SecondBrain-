import { api } from '@/lib/api'
import type { ChatMessage } from '@/lib/types'

const BASE = '/api/v1/chat'

export const chatService = {
  list: () =>
    api.get<any[]>(BASE),

  send: (message: string, conversationId?: string) =>
    api.post<ChatMessage>(BASE, { message, conversation_id: conversationId }),
}
