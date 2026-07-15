'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import { Flag, Plus, Search, Trash2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { NewFlagModal } from '@/components/flags/NewFlagModal'
import { showSuccess, showError } from '@/lib/toast'
import { featureFlagService } from '@/lib/services/feature-flags'
import type { FeatureFlag } from '@/types/feature-flags'

function FlagCard({
  flag,
  onToggle,
  onDelete,
}: {
  flag: FeatureFlag
  onToggle: (key: string, enabled: boolean) => void
  onDelete: (key: string) => void
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
    >
      <Card variant="default" className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1 space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <code className="text-xs font-mono px-1.5 py-0.5 rounded bg-background-elevated text-accent-secondary border border-border-default">
                {flag.key}
              </code>
              {flag.enabled ? (
                <Badge variant="success">Enabled</Badge>
              ) : (
                <Badge variant="outline">Disabled</Badge>
              )}
            </div>
            <p className="text-sm font-medium text-text-primary truncate">{flag.name}</p>
            {flag.description && (
              <p className="text-xs text-text-secondary line-clamp-2">{flag.description}</p>
            )}
            <div className="flex items-center gap-3 pt-1 text-xs text-text-secondary">
              <span>Rollout: <span className="font-mono text-accent-primary">{flag.rollout_percentage}%</span></span>
              {flag.user_segments.length > 0 && (
                <span>Segments: <span className="font-mono">{flag.user_segments.length}</span></span>
              )}
              <span>Updated: {new Date(flag.updated_at).toLocaleDateString()}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Switch
              checked={flag.enabled}
              onChange={(v) => onToggle(flag.key, v)}
            />
            <button
              onClick={() => onDelete(flag.key)}
              className="p-2 rounded-lg text-text-secondary hover:text-accent-error hover:bg-accent-error/10 transition-colors"
              aria-label={`Delete flag ${flag.key}`}
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <Card key={i} className="p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2 flex-1">
              <Skeleton variant="text" className="w-32 h-4" />
              <Skeleton variant="text" className="w-48 h-4" />
              <Skeleton variant="text" className="w-64 h-3" />
            </div>
            <Skeleton variant="text" className="w-10 h-6 rounded-full" />
          </div>
        </Card>
      ))}
    </div>
  )
}

export default function FeatureFlagsPage() {
  const [flags, setFlags] = useState<FeatureFlag[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)

  const fetchFlags = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await featureFlagService.list()
      setFlags(res.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load feature flags')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchFlags()
  }, [fetchFlags])

  const filteredFlags = useMemo(() => {
    if (!search.trim()) return flags
    const q = search.toLowerCase()
    return flags.filter(
      f => f.key.toLowerCase().includes(q) || f.name.toLowerCase().includes(q),
    )
  }, [flags, search])

  const handleToggle = useCallback(async (key: string, enabled: boolean) => {
    setFlags(prev => prev.map(f => f.key === key ? { ...f, enabled } : f))
    try {
      await featureFlagService.update(key, { enabled })
      showSuccess(`Flag "${key}" ${enabled ? 'enabled' : 'disabled'}`)
    } catch (err) {
      setFlags(prev => prev.map(f => f.key === key ? { ...f, enabled: !enabled } : f))
      showError(err instanceof Error ? err.message : 'Failed to update flag')
    }
  }, [])

  const handleDelete = useCallback(async (key: string) => {
    try {
      await featureFlagService.delete(key)
      setFlags(prev => prev.filter(f => f.key !== key))
      showSuccess(`Flag "${key}" deleted`)
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to delete flag')
    }
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Flag size={22} className="text-accent-primary" />
          <div>
            <h1 className="text-2xl font-semibold text-text-primary">Feature Flags</h1>
            <p className="text-sm text-text-secondary">Manage feature toggles and rollouts</p>
          </div>
        </div>
        <Button variant="primary" onClick={() => setModalOpen(true)} icon={<Plus size={16} />}>
          Add Flag
        </Button>
      </div>

      <Input
        placeholder="Search flags by name or key..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      {loading && <LoadingSkeleton />}

      {error && (
        <Card className="p-6 text-center">
          <p className="text-accent-error text-sm mb-3">{error}</p>
          <Button variant="outline" onClick={fetchFlags}>Retry</Button>
        </Card>
      )}

      {!loading && !error && filteredFlags.length === 0 && (
        <Card className="p-12 text-center">
          <Flag size={40} className="mx-auto text-text-secondary opacity-40 mb-3" />
          <p className="text-text-primary font-medium mb-1">
            {search ? 'No matching flags' : 'No feature flags yet'}
          </p>
          <p className="text-sm text-text-secondary mb-4">
            {search ? 'Try a different search term' : 'Create your first flag to get started'}
          </p>
          {!search && (
            <Button variant="primary" onClick={() => setModalOpen(true)} icon={<Plus size={16} />}>
              Create Flag
            </Button>
          )}
        </Card>
      )}

      {!loading && !error && filteredFlags.length > 0 && (
        <AnimatePresence mode="popLayout">
          <div className="space-y-3">
            {filteredFlags.map(flag => (
              <FlagCard
                key={flag.key}
                flag={flag}
                onToggle={handleToggle}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </AnimatePresence>
      )}

      {!loading && !error && (
        <p className="text-xs text-text-secondary text-center">
          {filteredFlags.length} of {flags.length} flag{flags.length !== 1 ? 's' : ''}
        </p>
      )}

      <NewFlagModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={fetchFlags}
      />
    </div>
  )
}
