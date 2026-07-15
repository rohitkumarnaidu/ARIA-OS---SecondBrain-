'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useSleepStore } from '@/lib/stores'
import { usePredictions } from '@/hooks'
import type { SleepLog } from '@/lib/types'
import { Moon, Sun, Trash2, Clock, Battery, AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { WindDownPanel } from '@/components/sleep/WindDownPanel'
import { createLogger } from '@/lib/utils/logger'

export default function SleepPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const { items: sleepLogs, loading, error, fetch: fetchSleep, create, remove } = useSleepStore()
  const { sleep: predSleep, loading: predLoading } = usePredictions()
  const logger = createLogger('SleepPage')
  const [showLogModal, setShowLogModal] = useState(false)

  const [newSleep, setNewSleep] = useState({ bedtime: '23:00', wake_time: '07:00', quality_rating: 3 })

  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (user) fetchSleep()
  }, [user, fetchSleep])

  const calculateDuration = (bedtime: string, wake_time: string) => {
    const [bH, bM] = bedtime.split(':').map(Number)
    const [wH, wM] = wake_time.split(':').map(Number)
    let hours = wH - bH
    if (hours < 0) hours += 24
    return hours - (bM - wM) / 60
  }

  const calculateScore = (duration: number, quality: number) => {
    const durationScore = Math.min(100, duration * 12.5)
    const qualityScore = quality * 20
    return Math.round((durationScore + qualityScore) / 2)
  }

  const handleDelete = async (id: string) => {
    logger.info('Deleting sleep log', { id })
    try {
      await remove(id)
      logger.info('Sleep log deleted successfully', { id })
    } catch (err) {
      logger.error('Failed to delete sleep log', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const handleLog = async () => {
    const duration = calculateDuration(newSleep.bedtime, newSleep.wake_time)
    logger.info('Logging sleep', { bedtime: newSleep.bedtime, wake_time: newSleep.wake_time, quality_rating: newSleep.quality_rating, duration })
    
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0]
    const bedtime = new Date(dateStr + 'T' + newSleep.bedtime + ':00')
    if (newSleep.bedtime > newSleep.wake_time) bedtime.setDate(bedtime.getDate() - 1)
    
    const wake = new Date(dateStr + 'T' + newSleep.wake_time + ':00')

    try {
      await create({
        bedtime: bedtime.toISOString(),
        wake_time: wake.toISOString(),
        quality_rating: newSleep.quality_rating,
      })
      logger.info('Sleep log created successfully', { quality_rating: newSleep.quality_rating })
      setShowLogModal(false)
    } catch (err) {
      logger.error('Failed to create sleep log', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const recentLogs = sleepLogs.slice(0, 7)
  const avgScore = sleepLogs.length > 0 ? Math.round(sleepLogs.reduce((sum, s) => sum + s.sleep_score, 0) / sleepLogs.length) : 0
  const avgDuration = sleepLogs.length > 0 ? Math.round(sleepLogs.reduce((sum, s) => sum + s.duration_hours, 0) / sleepLogs.length * 10) / 10 : 0

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (authLoading || loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="relative">
        <div className="w-12 h-12 rounded-xl border-2 border-accent-primary/30 animate-pulse-glow" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-text-primary text-gradient">Sleep Monitor</h1>
          <p className="text-text-secondary">Track your sleep quality and patterns</p>
        </div>
        <Button variant="primary" icon={<Moon size={20} />} onClick={() => setShowLogModal(true)}>
          Log Sleep
        </Button>
      </motion.div>

      <WindDownPanel />

      {error && (
        <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Avg Sleep Score', value: avgScore, color: 'text-accent-primary' },
          { label: 'Avg Duration', value: `${avgDuration}h`, color: 'text-text-primary' },
          { label: 'Nights Logged', value: sleepLogs.length, color: 'text-text-primary' },
          { label: 'Sleep Debt', value: `${sleepLogs.reduce((sum, s) => sum + s.sleep_debt, 0).toFixed(1)}h`, color: 'text-accent-warning' },
        ].map((stat, i) => (
          <motion.div 
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-text-secondary text-sm">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* AI Sleep Insight */}
      {predSleep && !predLoading && predSleep.average_score > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="card"
        >
          <div className="flex items-center gap-2 mb-3">
            {predSleep.trend === 'improving' ? <TrendingUp size={16} className="text-[var(--accent-success)]" /> :
             predSleep.trend === 'declining' ? <TrendingDown size={16} className="text-accent-error" /> :
             <Minus size={16} className="text-text-tertiary" />}
            <h2 className="text-lg font-semibold text-text-primary">Sleep Insight</h2>
          </div>
          <p className="text-sm text-text-secondary">{predSleep.recommendation}</p>
          {predSleep.bedtime_prediction && (
            <div className="flex flex-wrap gap-4 mt-3 text-xs text-text-tertiary">
              <span>Optimal bedtime: <strong className="text-text-primary">{predSleep.bedtime_prediction.optimal_bedtime}</strong></span>
              <span>Optimal wake: <strong className="text-text-primary">{predSleep.bedtime_prediction.optimal_wake}</strong></span>
              <span>Expected score: <strong className="text-[var(--accent-success)]">{predSleep.bedtime_prediction.expected_score}</strong></span>
              <span className="text-text-tertiary">Confidence: {predSleep.bedtime_prediction.confidence}</span>
            </div>
          )}
        </motion.div>
      )}

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-text-primary mb-4">Recent Sleep</h2>
        <div className="space-y-3">
          <AnimatePresence>
            {recentLogs.map((log, i) => (
              <motion.div 
                key={log.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center justify-between p-3 bg-background-elevated rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <Moon size={20} className="text-accent-info" />
                  <div>
                    <div className="text-text-primary font-medium">{new Date(log.created_at).toLocaleDateString()}</div>
                    <div className="text-text-muted text-sm">{log.duration_hours}h • Quality: {log.quality_rating}/5</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className={`text-lg font-bold ${log.sleep_score >= 70 ? 'text-accent-secondary' : log.sleep_score >= 40 ? 'text-accent-warning' : 'text-accent-error'}`}>{log.sleep_score}</div>
                  <button onClick={() => handleDelete(log.id)} className="text-text-muted hover:text-accent-error transition-colors" aria-label="Delete sleep log">
                    <Trash2 size={16} />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {sleepLogs.length === 0 && <p className="text-text-muted text-center py-4">No sleep logs yet</p>}
        </div>
      </motion.div>

      <AnimatePresence>
        {showLogModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => setShowLogModal(false)}
          >
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-text-primary">Log Sleep</h2>
                <button onClick={() => setShowLogModal(false)} className="text-text-muted"><Moon size={24} /></button>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><label htmlFor="sleep-bedtime" className="block text-text-secondary text-sm mb-1">Bedtime</label><input id="sleep-bedtime" type="time" value={newSleep.bedtime} onChange={e => setNewSleep({ ...newSleep, bedtime: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                  <div><label htmlFor="sleep-waketime" className="block text-text-secondary text-sm mb-1">Wake Time</label><input id="sleep-waketime" type="time" value={newSleep.wake_time} onChange={e => setNewSleep({ ...newSleep, wake_time: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                </div>
                <div><span className="block text-text-secondary text-sm mb-1" id="sleep-quality-label">Quality Rating</span>
                  <div className="flex gap-2 mt-2">
                    {[1,2,3,4,5].map(n => (<button key={n} onClick={() => setNewSleep({ ...newSleep, quality_rating: n })} className={`flex-1 py-2 rounded-lg ${newSleep.quality_rating === n ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}>{n}</button>))}
                  </div>
                </div>
                <Button variant="primary" className="w-full" onClick={handleLog}>Log Sleep</Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}