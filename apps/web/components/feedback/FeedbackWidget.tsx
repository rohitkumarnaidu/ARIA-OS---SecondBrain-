'use client'

import { useState, useCallback } from 'react'
import { ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { showSuccess } from '@/lib/toast'

interface FeedbackWidgetProps {
  source: string
  targetId: string
  className?: string
}

export function FeedbackWidget({ source, targetId, className = '' }: FeedbackWidgetProps) {
  const [submitted, setSubmitted] = useState<'up' | 'down' | null>(null)
  const [loading, setLoading] = useState(false)

  const handleFeedback = useCallback(async (rating: number) => {
    if (submitted || loading) return
    setLoading(true)
    try {
      await api.post('/api/v1/feedback', { source, target_id: targetId, rating })
      setSubmitted(rating >= 4 ? 'up' : 'down')
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [source, targetId, submitted, loading])

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <button
        onClick={() => handleFeedback(5)}
        disabled={!!submitted || loading}
        className={`p-1 rounded transition-colors ${
          submitted === 'up' ? 'text-accent-success' : 'text-text-tertiary hover:text-text-primary'
        } disabled:opacity-50`}
        aria-label="Thumbs up"
      >
        {loading ? <Loader2 size={14} className="animate-spin" /> : <ThumbsUp size={14} />}
      </button>
      <button
        onClick={() => handleFeedback(1)}
        disabled={!!submitted || loading}
        className={`p-1 rounded transition-colors ${
          submitted === 'down' ? 'text-accent-error' : 'text-text-tertiary hover:text-text-primary'
        } disabled:opacity-50`}
        aria-label="Thumbs down"
      >
        <ThumbsDown size={14} />
      </button>
    </div>
  )
}
