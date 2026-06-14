'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { showError } from '@/lib/toast'
import { Plus, Moon, Trash2, X, Flame, Target, Activity, Zap, Timer } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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
    if (user) fetchHabits()
  }, [user])

  const fetchHabits = async () => {
    setLoading(true)
    try {
      const { data } = await supabase.from('habits').select('*').order('created_at', { ascending: false })
      if (data) setHabits(data)
    } catch (err) {
      console.error('Failed to fetch habits:', err)
      showError('Failed to load habits. Please try again.')
    }
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
  const avgConsistency = activeHabits.length > 0 
    ? Math.round(activeHabits.reduce((sum, h) => sum + h.consistency_percentage, 0) / activeHabits.length)
    : 0

  if (!mounted || authLoading || loading) {
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
            <span className="text-gradient">Habit Engine</span>
          </h1>
          <p className="text-text-secondary">Build consistent daily habits</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn btn-primary gap-2">
          <Plus size={20} />
          Add Habit
        </button>
      </motion.div>

      {/* Stats */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-3 gap-4"
      >
        {[
          { label: 'Active', value: activeHabits.length, icon: Activity, color: 'accent-primary' },
          { label: 'Streak', value: totalStreak, icon: Flame, color: 'accent-warning' },
          { label: 'Consistency', value: `${avgConsistency}%`, icon: Target, color: 'accent-success' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className="card group hover:border-accent-primary/30 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">{stat.label}</span>
              <stat.icon size={18} className={`text-${stat.color} opacity-60 group-hover:opacity-100 transition-opacity`} />
            </div>
            <div className="text-3xl font-display font-bold text-text-primary">{stat.value}</div>
          </motion.div>
        ))}
      </motion.div>

      {/* Habits Grid */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <AnimatePresence mode="popLayout">
          {habits.map((habit, index) => (
            <motion.div
              key={habit.id}
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: index * 0.05 }}
              className={`card card-interactive group ${!habit.is_active ? 'opacity-50' : ''}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-neon/10 flex items-center justify-center">
                  <Moon size={24} className="text-accent-primary" />
                </div>
                <button 
                  onClick={() => handleDelete(habit.id)} 
                  className="p-2 hover:bg-accent-error/10 rounded-lg touch-target opacity-0 group-hover:opacity-100 transition-all"
                >
                  <Trash2 size={16} className="text-accent-error" />
                </button>
              </div>

              <h3 className="text-lg font-semibold text-text-primary mb-2 group-hover:text-accent-primary transition-colors">
                {habit.name}
              </h3>

              <div className="flex items-center gap-3 text-sm text-text-tertiary mb-4">
                <span className="flex items-center gap-1 capitalize">
                  <Timer size={14} />
                  {habit.frequency}
                </span>
                {habit.time_target_minutes && (
                  <span className="flex items-center gap-1">
                    <Zap size={14} />
                    {habit.time_target_minutes} min
                  </span>
                )}
              </div>

              {/* Streak & Consistency */}
              <div className="flex items-center justify-between pt-4 border-t border-border/50">
                <div className="flex items-center gap-2">
                  <Flame size={18} className="text-accent-warning" />
                  <span className="text-lg font-bold text-text-primary">{habit.current_streak}</span>
                  <span className="text-xs text-text-tertiary">streak</span>
                </div>
                <button 
                  onClick={() => handleToggleActive(habit.id, habit.is_active)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    habit.is_active 
                      ? 'bg-accent-success/10 text-accent-success border-accent-success/30' 
                      : 'bg-background-elevated text-text-tertiary border-border'
                  }`}
                >
                  {habit.is_active ? 'Active' : 'Paused'}
                </button>
              </div>
            </motion.div>
          ))}

          {habits.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="col-span-full card text-center py-16"
            >
              <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
                <Moon size={40} className="text-accent-primary" />
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary mb-2">No habits yet</h3>
              <p className="text-text-tertiary mb-6">Build your first habit today</p>
              <button onClick={() => setShowAddModal(true)} className="btn btn-primary mx-auto">
                <Plus size={20} />
                Add Habit
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Add Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4"
            role="dialog"
            aria-modal="true"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-display font-semibold text-text-primary">Add New Habit</h2>
                <button onClick={() => setShowAddModal(false)} className="p-2 hover:bg-background-elevated rounded-lg touch-target">
                  <X size={20} className="text-text-tertiary" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Habit Name <span className="text-accent-error">*</span>
                  </label>
                  <input
                    type="text"
                    value={newHabit.name}
                    onChange={e => setNewHabit({ ...newHabit, name: e.target.value })}
                    className="input"
                    placeholder="e.g., Morning coding"
                    autoFocus
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Frequency</label>
                    <select
                      value={newHabit.frequency}
                      onChange={e => setNewHabit({ ...newHabit, frequency: e.target.value })}
                      className="input"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekdays">Weekdays</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Time (min)</label>
                    <input
                      type="number"
                      value={newHabit.time_target_minutes}
                      onChange={e => setNewHabit({ ...newHabit, time_target_minutes: parseInt(e.target.value) || 30 })}
                      className="input"
                      min={1}
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowAddModal(false)} className="btn btn-secondary flex-1">Cancel</button>
                <button onClick={handleAdd} disabled={!newHabit.name.trim()} className="btn btn-primary flex-1">
                  Add Habit
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}