'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Brain, Save, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import type { Memory, MemoryUpdate } from '@/lib/types'

interface MemoryEditModalProps {
  memory: Memory | null
  open: boolean
  onClose: () => void
  onSave: (id: string, data: MemoryUpdate) => Promise<void>
  onDelete: (id: string) => Promise<void>
}

const MEMORY_TYPES = ['preference', 'pattern', 'fact', 'context', 'learning'] as const
const IMPORTANCE_LEVELS = ['low', 'medium', 'high', 'critical'] as const

export function MemoryEditModal({ memory, open, onClose, onSave, onDelete }: MemoryEditModalProps) {
  const [type, setType] = useState<string>('fact')
  const [key, setKey] = useState('')
  const [valueStr, setValueStr] = useState('')
  const [importance, setImportance] = useState<string>('medium')
  const [tagsStr, setTagsStr] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (memory) {
      setType(memory.type)
      setKey(memory.key)
      setValueStr(typeof memory.value === 'string' ? memory.value : JSON.stringify(memory.value, null, 2))
      setImportance(memory.importance)
      setTagsStr((memory.tags ?? []).join(', '))
    } else {
      setType('fact')
      setKey('')
      setValueStr('')
      setImportance('medium')
      setTagsStr('')
    }
  }, [memory, open])

  const handleSave = async () => {
    if (!memory || !key.trim()) return
    setSaving(true)
    try {
      let parsedValue: unknown = valueStr
      try { parsedValue = JSON.parse(valueStr) } catch { parsedValue = valueStr }
      await onSave(memory.id, {
        type: type as any,
        key: key.trim(),
        value: parsedValue,
        importance: importance as any,
        tags: tagsStr.split(',').map(t => t.trim()).filter(Boolean),
      })
      onClose()
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!memory) return
    setDeleting(true)
    try {
      await onDelete(memory.id)
      onClose()
    } finally {
      setDeleting(false)
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[var(--z-modal)] p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="memory-edit-title"
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="bg-[var(--background-card)] border border-[var(--border)] rounded-2xl w-full max-w-lg overflow-hidden"
          >
            <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
              <div className="flex items-center gap-2">
                <Brain size={16} className="text-[var(--accent-primary)]" />
                <h2 id="memory-edit-title" className="text-sm font-display font-semibold text-[var(--text-primary)]">
                  {memory ? 'Edit Memory' : 'New Memory'}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-1 rounded-lg hover:bg-[var(--background-elevated)] text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
                aria-label="Close"
              >
                <X size={16} />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-[var(--text-secondary)]">Type</label>
                  <select
                    value={type}
                    onChange={e => setType(e.target.value)}
                    className="w-full h-9 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                  >
                    {MEMORY_TYPES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-[var(--text-secondary)]">Importance</label>
                  <select
                    value={importance}
                    onChange={e => setImportance(e.target.value)}
                    className="w-full h-9 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                  >
                    {IMPORTANCE_LEVELS.map(l => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-[var(--text-secondary)]">Key</label>
                <input
                  type="text"
                  value={key}
                  onChange={e => setKey(e.target.value)}
                  placeholder="e.g. preferred_work_hours"
                  className="w-full h-9 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-[var(--text-secondary)]">Value</label>
                <textarea
                  value={valueStr}
                  onChange={e => setValueStr(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] resize-y font-mono"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-[var(--text-secondary)]">Tags (comma-separated)</label>
                <input
                  type="text"
                  value={tagsStr}
                  onChange={e => setTagsStr(e.target.value)}
                  placeholder="work, productivity, morning"
                  className="w-full h-9 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border-t border-[var(--border)]">
              {memory ? (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="text-[var(--accent-error)] hover:bg-[var(--accent-error)]/10"
                >
                  <Trash2 size={14} />
                  {deleting ? 'Deleting...' : 'Delete'}
                </Button>
              ) : (
                <div />
              )}
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={onClose}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" onClick={handleSave} disabled={!key.trim() || saving}>
                  <Save size={14} />
                  {saving ? 'Saving...' : 'Save'}
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
