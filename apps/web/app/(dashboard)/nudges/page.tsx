'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { nudgeService } from '@/lib/services/nudges'
import type { NudgeEntry } from '@/lib/types'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen, Target, AlertTriangle, BellRing, CheckCheck, RefreshCw, ChevronRight } from 'lucide-react'

const severityConfig = {
  info: { badge: 'info' as const, icon: BellRing, label: 'Info' },
  warning: { badge: 'warning' as const, icon: AlertTriangle, label: 'Warning' },
  critical: { badge: 'error' as const, icon: AlertTriangle, label: 'Critical' },
}

const typeIcon = {
  course: BookOpen,
  habit: Target,
  task: BellRing,
}

function relativeTime(dateStr: string): string {
  const now = Date.now()
  const date = new Date(dateStr).getTime()
  const diff = now - date
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}

function NudgeCard({ nudge, onMarkRead }: { nudge: NudgeEntry; onMarkRead: (id: string) => void }) {
  const sev = severityConfig[nudge.severity] || severityConfig.info
  const SevIcon = sev.icon
  const TypeIcon = typeIcon[nudge.type] || BellRing

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      <Card
        variant="interactive"
        className={nudge.read ? 'opacity-60 hover:opacity-80' : ''}
        onClick={() => { if (!nudge.read) onMarkRead(nudge.id) }}
      >
        <div className="flex items-start gap-4">
          <div className={`shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${
            nudge.severity === 'critical'
              ? 'bg-accent-error/10'
              : nudge.severity === 'warning'
              ? 'bg-accent-warning/10'
              : 'bg-accent-info/10'
          }`}>
            <TypeIcon size={20} className={
              nudge.severity === 'critical'
                ? 'text-accent-error'
                : nudge.severity === 'warning'
                ? 'text-accent-warning'
                : 'text-accent-info'
            } />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h3 className="text-sm font-semibold text-text-primary font-display truncate">
                {nudge.title}
              </h3>
              <Badge variant={sev.badge} className="shrink-0">
                <SevIcon size={10} className="mr-1" />
                {sev.label}
              </Badge>
            </div>
            <p className="text-xs text-text-secondary leading-relaxed line-clamp-2 mb-2">
              {nudge.message}
            </p>
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-text-tertiary font-mono">
                {relativeTime(nudge.created_at)}
              </span>
              {nudge.action_url && (
                <Link
                  href={nudge.action_url}
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center gap-1 text-xs font-medium text-accent-primary hover:text-accent-primaryHover transition-colors"
                >
                  Go to
                  <ChevronRight size={12} />
                </Link>
              )}
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

function NudgeSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="flex items-start gap-4">
          <Skeleton variant="circle" className="w-10 h-10 shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" className="w-3/5 h-4" />
            <Skeleton variant="text" className="w-full h-3" />
            <Skeleton variant="text" className="w-1/4 h-3" />
          </div>
        </Card>
      ))}
    </div>
  )
}

export default function NudgesPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [nudges, setNudges] = useState<NudgeEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active')

  const fetchNudges = useCallback(async () => {
    if (!user) return
    setLoading(true)
    setError(null)
    try {
      const data = await nudgeService.list()
      setNudges(data)
    } catch (err) {
      setError('Couldn\'t load nudges')
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    if (user) fetchNudges()
  }, [user, fetchNudges])

  const handleMarkRead = async (id: string) => {
    try {
      await nudgeService.markRead(id)
      setNudges((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)))
    } catch { }
  }

  const handleMarkAllRead = async () => {
    try {
      await nudgeService.markAllRead()
      setNudges((prev) => prev.map((n) => ({ ...n, read: true })))
    } catch { }
  }

  const unreadCount = nudges.filter((n) => !n.read).length
  const activeNudges = nudges.filter((n) => !n.read)
  const historyNudges = nudges.filter((n) => n.read)
  const displayNudges = activeTab === 'active' ? activeNudges : historyNudges

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="relative">
          <div className="w-12 h-12 rounded-xl border-2 border-accent-primary/30 animate-pulse-glow" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div className="space-y-1">
          <h1 className="text-3xl font-display font-bold">
            <span className="text-gradient">Nudge Engine</span>
          </h1>
          <p className="text-text-secondary">Course and habit nudges to keep you on track</p>
        </div>
        {unreadCount > 0 && (
          <Button onClick={handleMarkAllRead} variant="secondary" className="gap-2">
            <CheckCheck size={16} />
            Mark All Read
          </Button>
        )}
      </motion.div>

      {/* Error State */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-3 p-4 rounded-xl border border-accent-error/20 bg-accent-error/5"
        >
          <AlertTriangle size={18} className="text-accent-error shrink-0" />
          <p className="text-sm text-text-primary">{error}</p>
          <Button onClick={fetchNudges} variant="ghost" size="sm" className="ml-auto gap-1">
            <RefreshCw size={14} />
            Retry
          </Button>
        </motion.div>
      )}

      {/* Tabs */}
      {!error && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="flex gap-1 p-1 rounded-xl bg-background-elevated border border-border w-fit"
        >
          <button
            onClick={() => setActiveTab('active')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'active'
                ? 'bg-accent-primary text-white shadow-glow-sm'
                : 'text-text-tertiary hover:text-text-primary'
            }`}
          >
            Active
            {unreadCount > 0 && (
              <span className="ml-2 px-1.5 py-0.5 text-[10px] rounded-full bg-accent-error/20 text-accent-error">
                {unreadCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-accent-primary text-white shadow-glow-sm'
                : 'text-text-tertiary hover:text-text-primary'
            }`}
          >
            History
          </button>
        </motion.div>
      )}

      {/* Loading State */}
      {loading && <NudgeSkeleton />}

      {/* Nudge List */}
      {!loading && !error && (
        <AnimatePresence mode="popLayout">
          {displayNudges.length > 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {displayNudges.map((nudge, i) => (
                <motion.div
                  key={nudge.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04, duration: 0.3, ease: 'easeOut' }}
                >
                  <NudgeCard nudge={nudge} onMarkRead={handleMarkRead} />
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card text-center py-16"
            >
              <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
                <Target size={40} className="text-accent-primary" />
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary mb-2">
                {activeTab === 'active' ? 'All caught up!' : 'No nudge history'}
              </h3>
              <p className="text-text-tertiary mb-6">
                {activeTab === 'active'
                  ? 'No nudges right now. You\'re on track!'
                  : 'Past nudges will appear here once generated.'}
              </p>
              <Link href="/dashboard">
                <Button variant="primary">
                  Back to Dashboard
                </Button>
              </Link>
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  )
}
