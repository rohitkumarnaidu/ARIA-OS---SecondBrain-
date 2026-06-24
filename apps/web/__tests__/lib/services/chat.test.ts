import { describe, it, expect, vi, beforeEach } from 'vitest'
import { chatService } from '@/lib/services/chat'

const mockGet = vi.fn()
const mockPost = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('chatService', () => {
  describe('list', () => {
    it('returns chat messages', async () => {
      const messages = [{ id: '1', role: 'user', content: 'Hello' }]
      mockGet.mockResolvedValueOnce(messages)
      const result = await chatService.list()
      expect(result).toEqual(messages)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/chat')
    })

    it('returns empty array when no messages', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await chatService.list()
      expect(result).toEqual([])
    })
  })

  describe('send', () => {
    it('sends a message and returns response', async () => {
      const response = { id: '2', role: 'assistant', content: 'Hello back' }
      mockPost.mockResolvedValueOnce(response)
      const result = await chatService.send('Hello')
      expect(result).toEqual(response)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/chat', { message: 'Hello', conversation_id: undefined })
    })

    it('sends message with conversation id', async () => {
      const response = { id: '3', role: 'assistant', content: 'Response' }
      mockPost.mockResolvedValueOnce(response)
      const result = await chatService.send('Hi', 'conv-1')
      expect(result).toEqual(response)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/chat', { message: 'Hi', conversation_id: 'conv-1' })
    })

    it('handles API error', async () => {
      mockPost.mockRejectedValueOnce(new Error('AI unavailable'))
      await expect(chatService.send('test')).rejects.toThrow('AI unavailable')
    })
  })
})
