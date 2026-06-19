export interface AIStreamChunk {
  content: string
  agent?: string
  done?: boolean
  error?: string
}

export interface AIRequest {
  message: string
  thread_id?: string
  context?: Record<string, unknown>
}

export interface AIResponse {
  message: string
  thread_id: string
  agent: string
  timestamp: string
}

export interface AIAgentResult {
  agent_id: string
  agent_name: string
  status: 'idle' | 'thinking' | 'streaming' | 'done' | 'error'
  preview?: string
  confidence?: number
}

export type AIConnectionState = 'disconnected' | 'connecting' | 'streaming' | 'connected' | 'error'
