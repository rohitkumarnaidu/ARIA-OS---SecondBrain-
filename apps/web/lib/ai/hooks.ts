'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { aiStream } from './client'
import type { AIAgentResult, AIConnectionState } from './types'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  threadId?: string
  timestamp: number
}

const MESSAGES_KEY = 'aria-chat-history'
const MAX_HISTORY = 50

function loadPersistedMessages(): ChatMessage[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(MESSAGES_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function persistMessages(messages: ChatMessage[]): void {
  try {
    const trimmed = messages.slice(-MAX_HISTORY)
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(trimmed))
  } catch {
    // Storage full or unavailable — degrade gracefully
  }
}

export function useStreamingChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(loadPersistedMessages)
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [connectionState, setConnectionState] = useState<AIConnectionState>('disconnected')
  const threadIdRef = useRef<string | undefined>(undefined)
  const retryCountRef = useRef(0)

  useEffect(() => {
    persistMessages(messages)
  }, [messages])

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = { role: 'user', content, timestamp: Date.now() }
    setMessages(prev => [...prev, userMessage])
    setIsStreaming(true)
    setError(null)
    setConnectionState('connecting')

    let accumulated = ''
    const attemptSend = () => {
      aiStream.sendMessage(
        content,
        threadIdRef.current,
        (chunk) => {
          retryCountRef.current = 0
          setConnectionState('streaming')
          accumulated += chunk
          setMessages(prev => {
            const next = [...prev]
            const last = next[next.length - 1]
            if (last?.role === 'assistant') {
              next[next.length - 1] = { ...last, content: accumulated, timestamp: Date.now() }
            } else {
              next.push({ role: 'assistant', content: accumulated, threadId: threadIdRef.current, timestamp: Date.now() })
            }
            return next
          })
        },
        (fullText) => {
          setIsStreaming(false)
          setConnectionState(retryCountRef.current > 0 ? 'connected' : 'connected')
          threadIdRef.current = threadIdRef.current || crypto.randomUUID()
          setMessages(prev => {
            const next = [...prev]
            const last = next[next.length - 1]
            if (last?.role === 'assistant') {
              next[next.length - 1] = { ...last, content: fullText, threadId: threadIdRef.current }
            }
            return next
          })
        },
        (err) => {
          retryCountRef.current++
          if (retryCountRef.current <= 3) {
            setTimeout(attemptSend, 1000 * retryCountRef.current)
            return
          }
          setIsStreaming(false)
          setConnectionState('error')
          setError(err.message)
          retryCountRef.current = 0
        },
      )
    }

    attemptSend()
  }, [])

  const cancelStream = useCallback(() => {
    aiStream.cancel()
    setIsStreaming(false)
    setConnectionState('disconnected')
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
    threadIdRef.current = undefined
    localStorage.removeItem(MESSAGES_KEY)
  }, [])

  const retry = useCallback(() => {
    setError(null)
    setConnectionState('disconnected')
  }, [])

  return { messages, isStreaming, error, connectionState, sendMessage, cancelStream, clearMessages, retry }
}

export function useAIAgents() {
  const [agents, setAgents] = useState<AIAgentResult[]>([
    { agent_id: 'planner', agent_name: 'Planner', status: 'idle' },
    { agent_id: 'memory', agent_name: 'Memory', status: 'idle' },
    { agent_id: 'learning', agent_name: 'Learning', status: 'idle' },
    { agent_id: 'briefing', agent_name: 'Daily Briefing', status: 'idle' },
    { agent_id: 'opportunity', agent_name: 'Opportunity Radar', status: 'idle' },
    { agent_id: 'sleep', agent_name: 'Sleep Coach', status: 'idle' },
    { agent_id: 'nudge', agent_name: 'Nudge Engine', status: 'idle' },
    { agent_id: 'roadmap', agent_name: 'Roadmap Optimizer', status: 'idle' },
  ])

  const updateAgent = useCallback((agentId: string, updates: Partial<AIAgentResult>) => {
    setAgents(prev => prev.map(a => (a.agent_id === agentId ? { ...a, ...updates } : a)))
  }, [])

  const resetAgents = useCallback(() => {
    setAgents(prev => prev.map(a => ({ ...a, status: 'idle' as const, preview: undefined, confidence: undefined })))
  }, [])

  return { agents, updateAgent, resetAgents }
}

export function useAIAction<TArgs extends unknown[]>(action: (...args: TArgs) => Promise<unknown>) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const execute = useCallback(
    async (...args: TArgs) => {
      setIsLoading(true)
      setError(null)
      try {
        return await action(...args)
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'AI action failed. Please try again.'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [action],
  )

  return { execute, isLoading, error }
}
