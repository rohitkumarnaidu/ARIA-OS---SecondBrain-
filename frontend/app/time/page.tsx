'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Play, Square, Clock, Trash2, Zap, Coffee, Timer, Target, Eye } from 'lucide-react'

interface TimeEntry {
  id: string
  task_id?: string
  description?: string
  start_time: string
  end_time?: string
  duration_minutes?: number
  is_deep_work: boolean
  category: string
}

export default function TimePage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTimer, setActiveTimer] = useState<TimeEntry | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [mounted, setMounted] = useState(false)
  const [pomodoroMode, setPomodoroMode] = useState(false)
  const [pomodoroPhase, setPomodoroPhase] = useState<'work' | 'break'>('work')
  const [pomodoroTimeLeft, setPomodoroTimeLeft] = useState(25 * 60)
  const [showIdleWarning, setShowIdleWarning] = useState(false)
  const [lastActivity, setLastActivity] = useState(Date.now())
  const [focusHours, setFocusHours] = useState<{hour: number, count: number}[]>([])
  const idleCheckRef = useRef<NodeJS.Timeout>()

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
        const now = Date.now()
        if (now - lastActivity > 15 * 60 * 1000) {
          setShowIdleWarning(true)
        }
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [activeTimer, lastActivity])

  useEffect(() => {
    if (pomodoroMode) {
      const timer = setInterval(() => {
        setPomodoroTimeLeft(prev => {
          if (prev <= 1) {
            if (pomodoroPhase === 'work') {
              setPomodoroPhase('break')
              return 5 * 60
            } else {
              setPomodoroPhase('work')
              return 25 * 60
            }
          }
          return prev - 1
        })
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [pomodoroMode, pomodoroPhase])

  useEffect(() => {
    const hourCounts: Record<number, number> = {}
    entries.forEach(e => {
      if (e.duration_minutes && e.is_deep_work) {
        const hour = new Date(e.start_time).getHours()
        hourCounts[hour] = (hourCounts[hour] || 0) + e.duration_minutes
      }
    })
    const hours = Object.entries(hourCounts).map(([h, c]) => ({ hour: parseInt(h), count: c }))
    setFocusHours(hours.sort((a, b) => b.count - a.count).slice(0, 5))
  }, [entries])

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
        <div className="flex items-center gap-2">
          <button
            onClick={() => { setPomodoroMode(!pomodoroMode); setPomodoroPhase('work'); setPomodoroTimeLeft(25 * 60) }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${pomodoroMode ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}
          >
            <Timer size={18} /> Pomodoro {pomodoroMode ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Pomodoro Display */}
      {pomodoroMode && (
        <div className="bg-gradient-to-r from-accent-primary/20 to-accent-secondary/20 border border-border rounded-xl p-6 text-center">
          <div className="text-sm text-text-secondary mb-2">{pomodoroPhase === 'work' ? '🍅 Focus Time' : '☕ Break Time'}</div>
          <div className={`text-5xl font-bold font-mono mb-2 ${pomodoroPhase === 'work' ? 'text-accent-primary' : 'text-accent-secondary'}`}>
            {formatTime(pomodoroTimeLeft)}
          </div>
          <div className="text-text-muted text-sm">Session {pomodoroPhase === 'work' ? '25 min' : '5 min'}</div>
        </div>
      )}

      {/* Idle Warning */}
      {showIdleWarning && (
        <div className="bg-accent-warning/20 border border-accent-warning rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Eye className="text-accent-warning" size={20} />
            <span className="text-text-primary">No activity detected for 15+ minutes</span>
          </div>
          <button onClick={() => { setShowIdleWarning(false); setLastActivity(Date.now()) }} className="text-accent-primary text-sm">I'm still working</button>
        </div>
      )}

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

      {/* Focus Hours */}
      {focusHours.length > 0 && (
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center gap-2 mb-4">
            <Target size={18} className="text-accent-primary" />
            <h2 className="text-lg font-semibold text-text-primary">Your Peak Focus Hours</h2>
          </div>
          <div className="flex gap-3 overflow-x-auto">
            {focusHours.map(f => (
              <div key={f.hour} className="flex-shrink-0 bg-background-elevated rounded-lg p-3 text-center min-w-[80px]">
                <div className="text-lg font-bold text-accent-primary">{f.hour}:00</div>
                <div className="text-xs text-text-muted">{Math.round(f.count / 60)}h deep work</div>
              </div>
            ))}
          </div>
        </div>
      )}

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