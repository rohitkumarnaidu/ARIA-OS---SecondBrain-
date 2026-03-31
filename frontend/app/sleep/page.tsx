'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Moon, Sun, Trash2, Clock, Battery, AlertCircle } from 'lucide-react'

interface SleepLog {
  id: string
  bedtime: string
  wake_time: string
  quality_rating: number
  duration_hours: number
  sleep_score: number
  sleep_debt: number
  created_at: string
}

export default function SleepPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [sleepLogs, setSleepLogs] = useState<SleepLog[]>([])
  const [loading, setLoading] = useState(true)
  const [showLogModal, setShowLogModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newSleep, setNewSleep] = useState({ bedtime: '23:00', wake_time: '07:00', quality_rating: 3 })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchSleep()
  }, [user, authLoading, router])

  const fetchSleep = async () => {
    setLoading(true)
    const { data } = await supabase.from('sleep_logs').select('*').order('created_at', { ascending: false }).limit(30)
    if (data) setSleepLogs(data)
    setLoading(false)
  }

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

  const handleLog = async () => {
    const duration = calculateDuration(newSleep.bedtime, newSleep.wake_time)
    const score = calculateScore(duration, newSleep.quality_rating)
    
    const now = new Date()
    const bedtime = new Date(now.toISOString().split('T')[0] + 'T' + newSleep.bedtime + ':00')
    if (newSleep.bedtime > newSleep.wake_time) bedtime.setDate(bedtime.getDate() - 1)
    
    const wake = new Date(now.toISOString().split('T')[0] + 'T' + newSleep.wake_time + ':00')

    await supabase.from('sleep_logs').insert({
      bedtime: bedtime.toISOString(),
      wake_time: wake.toISOString(),
      quality_rating: newSleep.quality_rating,
      duration_hours: Math.round(duration * 10) / 10,
      sleep_score: score,
      sleep_debt: Math.max(0, 8 - duration),
    })
    setShowLogModal(false)
    fetchSleep()
  }

  const recentLogs = sleepLogs.slice(0, 7)
  const avgScore = sleepLogs.length > 0 ? Math.round(sleepLogs.reduce((sum, s) => sum + s.sleep_score, 0) / sleepLogs.length) : 0
  const avgDuration = sleepLogs.length > 0 ? Math.round(sleepLogs.reduce((sum, s) => sum + s.duration_hours, 0) / sleepLogs.length * 10) / 10 : 0

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Sleep Monitor</h1>
          <p className="text-text-secondary">Track your sleep quality and patterns</p>
        </div>
        <button onClick={() => setShowLogModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Moon size={20} /> Log Sleep
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-primary">{avgScore}</div><div className="text-text-secondary text-sm">Avg Sleep Score</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{avgDuration}h</div><div className="text-text-secondary text-sm">Avg Duration</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{sleepLogs.length}</div><div className="text-text-secondary text-sm">Nights Logged</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-warning">{sleepLogs.reduce((sum, s) => sum + s.sleep_debt, 0).toFixed(1)}h</div><div className="text-text-secondary text-sm">Sleep Debt</div></div>
      </div>

      <div className="bg-background-card border border-border rounded-xl p-4">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Recent Sleep</h2>
        <div className="space-y-3">
          {recentLogs.map(log => (
            <div key={log.id} className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
              <div className="flex items-center gap-4">
                <Moon size={20} className="text-accent-info" />
                <div>
                  <div className="text-text-primary font-medium">{new Date(log.created_at).toLocaleDateString()}</div>
                  <div className="text-text-muted text-sm">{log.duration_hours}h • Quality: {log.quality_rating}/5</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className={`text-lg font-bold ${log.sleep_score >= 70 ? 'text-accent-secondary' : log.sleep_score >= 40 ? 'text-accent-warning' : 'text-accent-error'}`}>{log.sleep_score}</div>
              </div>
            </div>
          ))}
          {sleepLogs.length === 0 && <p className="text-text-muted text-center py-4">No sleep logs yet</p>}
        </div>
      </div>

      {showLogModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Log Sleep</h2>
              <button onClick={() => setShowLogModal(false)} className="text-text-muted"><Moon size={24} /></button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">Bedtime</label><input type="time" value={newSleep.bedtime} onChange={e => setNewSleep({ ...newSleep, bedtime: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Wake Time</label><input type="time" value={newSleep.wake_time} onChange={e => setNewSleep({ ...newSleep, wake_time: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <div><label className="block text-text-secondary text-sm mb-1">Quality Rating</label>
                <div className="flex gap-2 mt-2">
                  {[1,2,3,4,5].map(n => (<button key={n} onClick={() => setNewSleep({ ...newSleep, quality_rating: n })} className={`flex-1 py-2 rounded-lg ${newSleep.quality_rating === n ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}>{n}</button>))}
                </div>
              </div>
              <button onClick={handleLog} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Log Sleep</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}