'use client'

import { useState, useEffect, useCallback, type ChangeEvent } from 'react'
import { AlertCircle, Save, Trash2 } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import type { Memory, MemoryType, MemoryImportance, MemoryUpdate } from '@/lib/types'

interface MemoryEditModalProps {
  memory: Memory | null
  open: boolean
  onClose: () => void
  onSave: (id: string, data: MemoryUpdate) => Promise<void>
  onDelete: (id: string) => Promise<void>
}

const MEMORY_TYPES: readonly MemoryType[] = ['preference', 'pattern', 'fact', 'context', 'learning']
const IMPORTANCE_LEVELS: readonly MemoryImportance[] = ['low', 'medium', 'high', 'critical']

const FIELD_LABEL_CLASS = 'text-xs font-medium text-text-secondary'
const FIELD_CLASS =
  'w-full h-9 px-3 rounded-lg bg-background-elevated border border-border text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-accent-primary'
const TEXTAREA_CLASS =
  'w-full px-3 py-2 rounded-lg bg-background-elevated border border-border text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-accent-primary resize-y font-mono'

function toErrorMessage(err: unknown, fallback: string): string {
  return err instanceof Error && err.message ? err.message : fallback
}

/**
 * The editor works in two modes, and the mode decides how the value is encoded:
 * a memory whose stored `value` is a plain string stays a plain string on save,
 * so typing `123` never silently becomes the number 123. A memory whose value
 * is structured round-trips through JSON.
 */
function parseValue(valueStr: string, storedValue: unknown): unknown {
  const storedIsStructured = typeof storedValue !== 'string'
  if (!storedIsStructured) return valueStr
  try {
    return JSON.parse(valueStr)
  } catch {
    return valueStr
  }
}

export function MemoryEditModal({ memory, open, onClose, onSave, onDelete }: MemoryEditModalProps): JSX.Element {
  const [type, setType] = useState<MemoryType>('fact')
  const [key, setKey] = useState('')
  const [valueStr, setValueStr] = useState('')
  const [importance, setImportance] = useState<MemoryImportance>('medium')
  const [tagsStr, setTagsStr] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

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
    setSaveError(null)
    setDeleteError(null)
  }, [memory, open])

  const handleClose = useCallback(() => {
    setSaveError(null)
    setDeleteError(null)
    onClose()
  }, [onClose])

  const handleTypeChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
    setType(e.target.value as MemoryType)
  }, [])

  const handleImportanceChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
    setImportance(e.target.value as MemoryImportance)
  }, [])

  const handleSave = useCallback(async (): Promise<void> => {
    if (!memory || !key.trim()) return
    setSaving(true)
    setSaveError(null)
    try {
      await onSave(memory.id, {
        type,
        key: key.trim(),
        value: parseValue(valueStr, memory.value),
        importance,
        tags: tagsStr.split(',').map(t => t.trim()).filter(Boolean),
      })
      onClose()
    } catch (err) {
      setSaveError(toErrorMessage(err, 'Failed to save this memory. Please try again.'))
    } finally {
      setSaving(false)
    }
  }, [memory, key, valueStr, type, importance, tagsStr, onSave, onClose])

  const handleDelete = useCallback(async (): Promise<void> => {
    if (!memory) return
    setDeleting(true)
    setDeleteError(null)
    try {
      await onDelete(memory.id)
      onClose()
    } catch (err) {
      setDeleteError(toErrorMessage(err, 'Failed to delete this memory. Please try again.'))
    } finally {
      setDeleting(false)
    }
  }, [memory, onDelete, onClose])

  const busy = saving || deleting

  return (
    <Modal
      isOpen={open}
      onClose={handleClose}
      title={memory ? 'Edit Memory' : 'New Memory'}
      titleId="memory-edit-title"
      size="lg"
    >
      <div className="space-y-4">
        {(saveError ?? deleteError) && (
          <div
            role="alert"
            className="flex items-start gap-2 rounded-lg border border-accent-error/30 bg-accent-error/10 px-3 py-2 text-sm text-text-primary"
          >
            <AlertCircle size={16} className="mt-0.5 shrink-0 text-accent-error" aria-hidden="true" />
            <span>{saveError ?? deleteError}</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label htmlFor="memory-type" className={FIELD_LABEL_CLASS}>Type</label>
            <select
              id="memory-type"
              value={type}
              onChange={handleTypeChange}
              disabled={busy}
              className={FIELD_CLASS}
            >
              {MEMORY_TYPES.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="memory-importance" className={FIELD_LABEL_CLASS}>Importance</label>
            <select
              id="memory-importance"
              value={importance}
              onChange={handleImportanceChange}
              disabled={busy}
              className={FIELD_CLASS}
            >
              {IMPORTANCE_LEVELS.map(l => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="memory-key" className={FIELD_LABEL_CLASS}>Key</label>
          <input
            id="memory-key"
            type="text"
            value={key}
            onChange={e => setKey(e.target.value)}
            disabled={busy}
            placeholder="e.g. preferred_work_hours"
            className={FIELD_CLASS}
            required
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="memory-value" className={FIELD_LABEL_CLASS}>Value</label>
          <textarea
            id="memory-value"
            value={valueStr}
            onChange={e => setValueStr(e.target.value)}
            disabled={busy}
            rows={4}
            className={TEXTAREA_CLASS}
          />
          {memory && typeof memory.value !== 'string' && (
            <p className="text-xs text-text-tertiary">
              This memory stores structured data — the value is saved as JSON.
            </p>
          )}
        </div>

        <div className="space-y-1.5">
          <label htmlFor="memory-tags" className={FIELD_LABEL_CLASS}>Tags (comma-separated)</label>
          <input
            id="memory-tags"
            type="text"
            value={tagsStr}
            onChange={e => setTagsStr(e.target.value)}
            disabled={busy}
            placeholder="work, productivity, morning"
            className={FIELD_CLASS}
          />
        </div>

        <div className="flex items-center justify-between gap-3 border-t border-border pt-4">
          {memory ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              loading={deleting}
              disabled={saving}
              className="text-accent-error hover:bg-accent-error/10"
            >
              <Trash2 size={14} aria-hidden="true" />
              {deleting ? 'Deleting…' : 'Delete'}
            </Button>
          ) : (
            <span />
          )}
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleClose} disabled={busy}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleSave} disabled={!key.trim() || busy}>
              <Save size={14} aria-hidden="true" />
              {saving ? 'Saving…' : 'Save'}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  )
}
