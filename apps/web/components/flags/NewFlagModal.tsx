'use client'

import { useState, useCallback } from 'react'
import { Modal } from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { Slider } from '@/components/ui/Slider'
import { showSuccess, showError } from '@/lib/toast'
import { featureFlagService } from '@/lib/services/feature-flags'

interface NewFlagModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: () => void
}

export function NewFlagModal({ isOpen, onClose, onCreated }: NewFlagModalProps) {
  const [name, setName] = useState('')
  const [key, setKey] = useState('')
  const [description, setDescription] = useState('')
  const [enabled, setEnabled] = useState(false)
  const [rolloutPercentage, setRolloutPercentage] = useState(100)
  const [userSegments, setUserSegments] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const generateKey = useCallback((val: string) => {
    return val
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '.')
      .replace(/^\.+|\.+$/g, '')
  }, [])

  const handleNameChange = useCallback((val: string) => {
    setName(val)
    if (!key || key === generateKey(name)) {
      setKey(generateKey(val))
    }
  }, [key, name, generateKey])

  const validate = (): boolean => {
    const errs: Record<string, string> = {}
    if (!name.trim()) errs.name = 'Name is required'
    if (!key.trim()) errs.key = 'Key is required'
    if (!/^[a-z][a-z0-9._-]*$/.test(key)) errs.key = 'Key must start with a letter and contain only lowercase letters, numbers, dots, hyphens, and underscores'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) return
    setSubmitting(true)
    try {
      await featureFlagService.create({
        key: key.trim(),
        name: name.trim(),
        description: description.trim(),
        enabled,
        rollout_percentage: rolloutPercentage,
        user_segments: userSegments
          .split(',')
          .map(s => s.trim())
          .filter(Boolean),
      })
      showSuccess(`Feature flag "${name}" created`)
      onCreated()
      onClose()
      setName(''); setKey(''); setDescription('')
      setEnabled(false); setRolloutPercentage(100); setUserSegments('')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to create feature flag')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Feature Flag" size="lg">
      <div className="space-y-5">
        <Input
          label="Name"
          placeholder="e.g., New Dashboard"
          value={name}
          onChange={e => handleNameChange(e.target.value)}
          error={errors.name}
          required
        />
        <Input
          label="Key"
          placeholder="e.g., new.dashboard"
          value={key}
          onChange={e => setKey(e.target.value)}
          error={errors.key}
          required
          helperText="Auto-generated from name. Used in code to check the flag."
        />
        <Input
          label="Description"
          placeholder="What does this flag control?"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-text-primary">Enabled</span>
          <Switch checked={enabled} onChange={setEnabled} />
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-text-primary">Rollout Percentage</span>
            <span className="text-sm font-mono text-text-secondary">{rolloutPercentage}%</span>
          </div>
          <Slider value={rolloutPercentage} onChange={setRolloutPercentage} min={0} max={100} step={1} />
        </div>
        <Input
          label="User Segments"
          placeholder="Comma-separated user IDs"
          value={userSegments}
          onChange={e => setUserSegments(e.target.value)}
          helperText="Optional: limit to specific user IDs"
        />
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit} loading={submitting}>
            Create Flag
          </Button>
        </div>
      </div>
    </Modal>
  )
}
