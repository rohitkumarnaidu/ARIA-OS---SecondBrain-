'use client'

import { useState, useCallback } from 'react'
import { Plus, Sparkles, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { parseCommand } from '@/lib/ai/nlp'
import { showSuccess, showError } from '@/lib/toast'

export function QuickAddTask() {
  const [value, setValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [focused, setFocused] = useState(false)

  const handleSubmit = useCallback(async () => {
    const text = value.trim()
    if (!text || loading) return

    const parsed = parseCommand(text)
    if (parsed.type === 'unknown' || parsed.confidence < 0.5) {
      showError("Couldn't understand that. Try: 'create task review PR by Friday'")
      return
    }

    setLoading(true)
    try {
      const res = await api.post<{ success: boolean; message: string }>('/api/v1/nlp/execute', {
        type: parsed.type,
        task: parsed.task,
      })
      if (res.success) {
        showSuccess(res.message)
        setValue('')
      }
    } catch {
      showError('Failed to create task. Try again.')
    } finally {
      setLoading(false)
    }
  }, [value, loading])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault()
        handleSubmit()
      }
    },
    [handleSubmit],
  )

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border px-4 py-3 transition-all duration-200 ${
        focused ? 'border-accent-primary/50 bg-background-card' : 'border-border-default bg-background-card/60'
      }`}
    >
      <Sparkles size={16} className="text-accent-primary shrink-0" aria-hidden="true" />
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder="Add task in plain English — e.g. review PR by Friday at 5pm..."
        disabled={loading}
        className="flex-1 bg-transparent border-none outline-none text-sm text-text-primary placeholder:text-text-tertiary disabled:opacity-50"
        aria-label="Quick add task using natural language"
      />
      {loading ? (
        <Loader2 size={16} className="text-accent-primary animate-spin shrink-0" />
      ) : (
        <button
          onClick={handleSubmit}
          disabled={!value.trim() || loading}
          className="p-1 rounded-lg hover:bg-background-elevated transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          aria-label="Add task"
        >
          <Plus size={16} className="text-accent-primary" />
        </button>
      )}
    </div>
  )
}
