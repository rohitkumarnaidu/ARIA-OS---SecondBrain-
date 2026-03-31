'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Play, Square, Clock, Trash2, Zap, Coffee } from 'lucide-react'

interface TimeEntry {
  id: string
  task_id?: string
  description?: string
  start_time: string
  end_time?: string
  duration_minutes?: number
  is_deep_work: boolean
}

export default function TimePage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTimer, setActiveTimer] = useState<TimeEntry | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchEntries()
  }, [user, authLoading, router])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (activeTimer) {
      interval = setInterval(() => {
        setElapsed(Math.floor((Date.now() - new Date(activeTimer.start_time).getTime()) / 1000))
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [activeTimer])

  const fetchEntries = async () => {
    setLoading(true)
    const { data } = await supabase.from('time_entries').select('*').order('start_time', { ascending: false }).limit(50)
    if (data) {
      setEntries(data)
      const active = data.find(e => !e.end_time)
      if (active) setActiveTimer(active)
    }
    setLoading(false)
  }

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  const startTimer = async (description: string) => {
    const { data } = await supabase.from('time_entries').insert({
      description: description || 'Working...',
      start_time: new Date().toISOString(),
      is_deep_work: false,
    }).select().single()
    
    if (data) {
      setActiveTimer(data)
      setElapsed(0)
    }
  }

  const stopTimer = async () => {
    if (!activeTimer) return
    
    const endTime = new Date().toISOString()
    const duration = Math.round((new Date(endTime).getTime() - new Date(activeTimer.start_time).getTime()) / 60000)
    const isDeepWork = duration >= 90
    
    await supabase.from('time_entries').update({
      end_time: endTime,
      duration_minutes: duration,
      is_deep_work: isDeepWork,
    }).eq('id', activeTimer.id)
    
    setActiveTimer(null)
    setElapsed(0)
    fetchEntries()
  }

  const totalToday = entries
    .filter(e => e.start_time.startsWith(new Date().toISOString().split('T')[0]) && e.duration_minutes)
    .reduce((sum, e) => sum + (e.duration_minutes || 0), 0)
  
  const deepWorkToday = entries
    .filter(e => e.start_time.startsWith(new Date().toISOString().split('T')[0]) && e.is_deep_work && e.duration_minutes)
    .reduce((sum, e) => sum + (e.duration_minutes || 0), 0)

  const recentEntries = entries.filter(e => e.duration_minutes).slice(0, 10)

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Time Tracker</h1>
          <p className="text-text-secondary">Track your work sessions</p>
        </div>
      </div>

      {/* Timer */}
      <div className="bg-background-card border border-border rounded-xl p-8 text-center">
        <div className="text-6xl font-bold text-text-primary mb-4 font-mono">{formatTime(elapsed)}</div>
        
        {activeTimer ? (
          <button onClick={stopTimer} className="flex items-center gap-2 mx-auto bg-accent-error text-white px-8 py-3 rounded-xl hover:bg-accent-error/90">
            <Square size={24} /> Stop
          </button>
        ) : (
          <button onClick={() => startTimer('')} className="flex items-center gap-2 mx-auto bg-accent-secondary text-white px-8 py-3 rounded-xl hover:bg-accent-secondary/90">
            <Play size={24} /> Start Timer
          </button>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{Math.round(totalToday / 60)}h {totalToday % 60}m</div><div className="text-text-secondary text-sm">Today Total</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-primary">{Math.round(deepWorkToday / 60)}h {deepWorkToday % 60}m</div><div className="text-text-secondary text-sm">Deep Work</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{recentEntries.length}</div><div className="text-text-secondary text-sm">Sessions</div></div>
      </div>

      <div className="bg-background-card border border-border rounded-xl p-4">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Recent Sessions</h2>
        <div className="space-y-3">
          {recentEntries.map(entry => (
            <div key={entry.id} className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
              <div>
                <div className="text-text-primary font-medium">{entry.description || 'Untitled'}</div>
                <div className="text-text-muted text-sm">
                  {new Date(entry.start_time).toLocaleTimeString()} • {entry.duration_minutes} min
                  {entry.is_deep_work && <span className="ml-2 text-accent-primary">Deep Work 🔥</span>}
                </div>
              </div>
              {entry.is_deep_work ? <Zap size={20} className="text-accent-warning" /> : <Coffee size={20} className="text-text-muted" />}
            </div>
          ))}
          {recentEntries.length === 0 && <p className="text-text-muted text-center py-4">No sessions yet</p>}
        </div>
      </div>
    </div>
  )
}