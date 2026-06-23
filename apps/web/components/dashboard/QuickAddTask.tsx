'use client'

import { useState, useCallback } from 'react'
import { Plus, Sparkles, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { parseCommand } from '@/lib/ai/nlp'
import { showSuccess, showError } from '@/lib/toast'
import { AIActionConfirm } from '@/components/ai/AIActionConfirm'

export function QuickAddTask() {
  const [value, setValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [focused, setFocused] = useState(false)
  const [confirm, setConfirm] = useState<{ title: string; description: string; parsed: ReturnType<typeof parseCommand> } | null>(null)

  const execute = useCallback(async (parsed: ReturnType<typeof parseCommand>) => {
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
      showError('Failed to execute. Try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleSubmit = useCallback(() => {
    const text = value.trim()
    if (!text || loading) return

    const parsed = parseCommand(text)
    if (parsed.type === 'unknown' || parsed.confidence < 0.5) {
      showError("Couldn't understand that. Try: 'create task review PR by Friday'")
      return
    }

    setConfirm({
      title: parsed.type === 'create_task' ? 'Create Task' : parsed.type === 'schedule' ? 'Schedule Entry' : 'Execute Action',
      description: parsed.type === 'create_task'
        ? `Create task: "${parsed.task?.title}"${parsed.task?.dueDate ? ` due ${parsed.task.dueDate}` : ''}`
        : `Execute ${parsed.type} action from your input?`,
      parsed,
    })
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
    <>
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

      <AIActionConfirm
        open={!!confirm}
        title={confirm?.title || ''}
        description={confirm?.description || ''}
        onConfirm={async () => {
          if (!confirm) return
          await execute(confirm.parsed)
          setConfirm(null)
        }}
        onCancel={() => setConfirm(null)}
      />
    </>
  )
}
