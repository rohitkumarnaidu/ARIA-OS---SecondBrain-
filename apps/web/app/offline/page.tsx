'use client'

import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  WifiOff,
  RefreshCw,
  LayoutDashboard,
  CheckSquare,
  Calendar,
  BookOpen,
  Clock,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { syncManager } from '@/lib/offline'

const quickLinks = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/tasks', label: 'Tasks', icon: CheckSquare },
  { href: '/habits', label: 'Habits', icon: Calendar },
  { href: '/courses', label: 'Courses', icon: BookOpen },
]

function formatTime(date: Date): string {
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatDate(date: Date): string {
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatRelative(isoString: string): string {
  const d = new Date(isoString)
  return `${formatDate(d)} at ${formatTime(d)}`
}

export default function OfflinePage() {
  const router = useRouter()
  const [lastSync, setLastSync] = useState<string | null>(null)
  const [pendingMutations, setPendingMutations] = useState(0)
  const [failedMutations, setFailedMutations] = useState(0)
  const [trying, setTrying] = useState(false)

  useEffect(() => {
    const load = async () => {
      const fromDb = await syncManager.getLastSyncTime()
      if (fromDb) {
        setLastSync(formatRelative(fromDb))
      } else {
        const stored = localStorage.getItem('aria-last-sync')
        if (stored) {
          setLastSync(formatRelative(stored))
        }
      }
      const pending = await syncManager.getPendingMutationCount()
      setPendingMutations(pending)
      const failed = await syncManager.getFailedMutationCount()
      setFailedMutations(failed)
    }
    load()
  }, [])

  const handleTryAgain = useCallback(() => {
    setTrying(true)
    if (navigator.onLine) {
      router.push('/dashboard')
    } else {
      setTimeout(() => setTrying(false), 2000)
    }
  }, [router])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background-page px-4">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="flex w-full max-w-md flex-col items-center gap-6 text-center"
      >
        <motion.div
          variants={itemVariants}
          className="flex h-20 w-20 items-center justify-center rounded-2xl bg-accent-primary/10"
        >
          <WifiOff className="h-10 w-10 text-accent-primary" />
        </motion.div>

        <motion.div variants={itemVariants} className="space-y-2">
          <h1 className="font-display text-2xl font-bold text-gradient">
            You&apos;re Offline
          </h1>
          <p className="text-sm text-text-secondary">
            Some features may be unavailable. Your data will sync automatically
            when you&apos;re back online.
          </p>
        </motion.div>

        {lastSync && (
          <motion.div
            variants={itemVariants}
            className="flex items-center gap-2 rounded-lg bg-background-elevated px-3 py-2 text-xs text-text-tertiary"
          >
            <Clock size={12} className="shrink-0" />
            Last synced: {lastSync}
          </motion.div>
        )}

        {pendingMutations > 0 && (
          <motion.div
            variants={itemVariants}
            className="flex w-full items-center gap-2 rounded-lg border border-accent-warning/20 bg-accent-warning/5 px-4 py-3 text-sm"
          >
            <AlertTriangle size={16} className="shrink-0 text-accent-warning" />
            <span className="text-text-primary">
              {pendingMutations} change{pendingMutations !== 1 ? 's' : ''} pending sync
            </span>
          </motion.div>
        )}

        {failedMutations > 0 && (
          <motion.div
            variants={itemVariants}
            className="flex w-full items-center gap-2 rounded-lg border border-accent-danger/20 bg-accent-danger/5 px-4 py-3 text-sm"
          >
            <AlertTriangle size={16} className="shrink-0 text-accent-danger" />
            <span className="text-text-primary">
              {failedMutations} failed sync{failedMutations !== 1 ? 's' : ''}. Data may be incomplete.
            </span>
          </motion.div>
        )}

        {pendingMutations === 0 && failedMutations === 0 && (
          <motion.div
            variants={itemVariants}
            className="flex w-full items-center gap-2 rounded-lg border border-accent-neon/20 bg-accent-neon/5 px-4 py-3 text-sm"
          >
            <CheckCircle2 size={16} className="shrink-0 text-accent-neon" />
            <span className="text-text-primary">
              All local data is up to date
            </span>
          </motion.div>
        )}

        <motion.div variants={itemVariants} className="w-full space-y-3">
          <p className="text-xs font-medium uppercase tracking-wider text-text-tertiary">
            Available offline
          </p>
          <div className="grid grid-cols-2 gap-3">
            {quickLinks.map((link) => {
              const Icon = link.icon
              return (
                <Link key={link.href} href={link.href}>
                  <Card variant="interactive" className="flex flex-col items-center gap-2 p-4">
                    <Icon size={20} className="text-accent-primary" aria-hidden="true" />
                    <span className="text-xs font-medium text-text-primary">
                      {link.label}
                    </span>
                  </Card>
                </Link>
              )
            })}
          </div>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Button
            variant="primary"
            size="lg"
            className="gap-2"
            onClick={handleTryAgain}
            loading={trying}
          >
            <RefreshCw size={16} />
            Try Again
          </Button>
        </motion.div>
      </motion.div>
    </main>
  )
}