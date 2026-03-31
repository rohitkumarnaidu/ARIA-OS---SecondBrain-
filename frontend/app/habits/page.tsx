'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Moon, Trash2, X, Flame, Target } from 'lucide-react'

interface Habit {
  id: string
  name: string
  frequency: string
  custom_days?: number[]
  time_target_minutes?: number
  goal_id?: string
  is_active: boolean
  current_streak: number
  best_streak: number
  consistency_percentage: number
}

export default function HabitsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [habits, setHabits] = useState<Habit[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newHabit, setNewHabit] = useState({ name: '', frequency: 'daily', time_target_minutes: 30 })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchHabits()
  }, [user, authLoading, router])

  const fetchHabits = async () => {
    setLoading(true)
    const { data } = await supabase.from('habits').select('*').order('created_at', { ascending: false })
    if (data) setHabits(data)
    setLoading(false)
  }

  const handleAdd = async () => {
    if (!newHabit.name.trim()) return
    await supabase.from('habits').insert({ ...newHabit, is_active: true, current_streak: 0, best_streak: 0, consistency_percentage: 0 })
    setNewHabit({ name: '', frequency: 'daily', time_target_minutes: 30 })
    setShowAddModal(false)
    fetchHabits()
  }

  const handleDelete = async (id: string) => {
    await supabase.from('habits').delete().eq('id', id)
    setHabits(habits.filter(h => h.id !== id))
  }

  const handleToggleActive = async (id: string, isActive: boolean) => {
    await supabase.from('habits').update({ is_active: !isActive }).eq('id', id)
    setHabits(habits.map(h => h.id === id ? { ...h, is_active: !isActive } : h))
  }

  const activeHabits = habits.filter(h => h.is_active)
  const totalStreak = activeHabits.reduce((sum, h) => sum + h.current_streak, 0)

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Habit Engine</h1>
          <p className="text-text-secondary">Build consistent daily habits</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Plus size={20} /> Add Habit
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{activeHabits.length}</div><div className="text-text-secondary text-sm">Active Habits</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-warning">{totalStreak}</div><div className="text-text-secondary text-sm">Total Streak Days</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-secondary">{Math.round(activeHabits.reduce((sum, h) => sum + h.consistency_percentage, 0) / (activeHabits.length || 1))}%</div><div className="text-text-secondary text-sm">Avg Consistency</div></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {habits.map(habit => (
          <div key={habit.id} className={`bg-background-card border border-border rounded-xl p-4 ${!habit.is_active ? 'opacity-50' : ''}`}>
            <div className="flex items-start justify-between mb-2">
              <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center"><Moon size={20} className="text-accent-primary" /></div>
              <button onClick={() => handleDelete(habit.id)}><Trash2 size={16} className="text-accent-error" /></button>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">{habit.name}</h3>
            <div className="flex items-center gap-4 text-sm text-text-muted mb-3">
              <span className="capitalize">{habit.frequency}</span>
              {habit.time_target_minutes && <span>{habit.time_target_minutes} min</span>}
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Flame size={16} className="text-accent-warning" /><span className="text-sm font-medium">{habit.current_streak}</span>
                <span className="text-xs text-text-muted">streak</span>
              </div>
              <button onClick={() => handleToggleActive(habit.id, habit.is_active)} className={`text-xs px-2 py-1 rounded ${habit.is_active ? 'bg-accent-secondary text-white' : 'bg-background-elevated text-text-muted'}`}>{habit.is_active ? 'Active' : 'Paused'}</button>
            </div>
          </div>
        ))}
      </div>

      {habits.length === 0 && <div className="text-center py-12"><Moon size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No habits yet</p></div>}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4"><h2 className="text-xl font-semibold text-text-primary">Add Habit</h2><button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button></div>
            <div className="space-y-4">
              <div><label className="block text-text-secondary text-sm mb-1">Habit Name *</label><input type="text" value={newHabit.name} onChange={e => setNewHabit({ ...newHabit, name: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="e.g., Morning coding" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">Frequency</label><select value={newHabit.frequency} onChange={e => setNewHabit({ ...newHabit, frequency: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"><option value="daily">Daily</option><option value="weekdays">Weekdays</option><option value="custom">Custom</option></select></div>
                <div><label className="block text-text-secondary text-sm mb-1">Time (min)</label><input type="number" value={newHabit.time_target_minutes} onChange={e => setNewHabit({ ...newHabit, time_target_minutes: parseInt(e.target.value) || 30 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <button onClick={handleAdd} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Add Habit</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}