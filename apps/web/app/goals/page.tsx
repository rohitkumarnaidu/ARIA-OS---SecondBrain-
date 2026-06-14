'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Target, Trash2, X, Calendar, TrendingUp, Flag, MapPin } from 'lucide-react'
import dynamic from 'next/dynamic'
import { motion, AnimatePresence } from 'framer-motion'

const RoadmapEditor = dynamic(() => import('@/components/RoadmapEditor'), { ssr: false })

interface Goal {
  id: string
  title: string
  description?: string
  roadmap_type: string
  target_date?: string
  hours_per_day: number
  days_per_week: number
  intensity: string
  status: string
  progress: number
  nodes?: any[]
  created_at: string
}

const roadmapTypes = [
  'career_skills', 'business_launch', 'exam_prep', 'study_learning', 
  'project', 'health', 'financial', 'custom'
] as const

export default function GoalsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    roadmap_type: 'career_skills' as typeof roadmapTypes[number],
    target_date: '',
    hours_per_day: 2,
    days_per_week: 5,
    intensity: 'medium',
  })

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchGoals()
    }
  }, [user, authLoading, router])

  const fetchGoals = async () => {
    setLoading(true)
    const { data, error } = await supabase
      .from('goals')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (!error && data) {
      setGoals(data)
    }
    setLoading(false)
  }

  const handleAddGoal = async () => {
    if (!newGoal.title.trim()) return
    
    const { data, error } = await supabase
      .from('goals')
      .insert({
        ...newGoal,
        target_date: newGoal.target_date ? new Date(newGoal.target_date).toISOString() : null,
        status: 'active',
        progress: 0,
        nodes: [],
      })
      .select()
    
    if (!error && data) {
      setGoals([data[0], ...goals])
      setNewGoal({
        title: '', description: '', roadmap_type: 'career_skills',
        target_date: '', hours_per_day: 2, days_per_week: 5, intensity: 'medium'
      })
      setShowAddModal(false)
    }
  }

  const handleUpdateProgress = async (id: string, progress: number) => {
    const { data, error } = await supabase
      .from('goals')
      .update({ progress: Math.min(100, Math.max(0, progress)) })
      .eq('id', id)
      .select()
    
    if (!error && data) {
      setGoals(goals.map(g => g.id === id ? data[0] : g))
    }
  }

  const handleDeleteGoal = async (id: string) => {
    const { error } = await supabase
      .from('goals')
      .delete()
      .eq('id', id)
    
    if (!error) {
      setGoals(goals.filter(g => g.id !== id))
    }
  }

  const activeGoals = goals.filter(g => g.status === 'active')
  const completedGoals = goals.filter(g => g.status === 'completed')

  const getTypeLabel = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

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
            <span className="text-gradient">Goals & Roadmaps</span>
          </h1>
          <p className="text-text-secondary">Plan your path to success</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary gap-2"
        >
          <Plus size={20} />
          Add Goal
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
          { label: 'Active', value: activeGoals.length, icon: Flag, color: 'accent-primary' },
          { label: 'Completed', value: completedGoals.length, icon: Target, color: 'accent-success' },
          { label: 'Avg Progress', value: `${activeGoals.length > 0 ? Math.round(activeGoals.reduce((acc, g) => acc + g.progress, 0) / activeGoals.length) : 0}%`, icon: TrendingUp, color: 'accent-neon' },
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

      {/* Goals Grid */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <AnimatePresence mode="popLayout">
          {activeGoals.map((goal, index) => (
            <motion.div
              key={goal.id}
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: index * 0.05 }}
              className="card card-interactive group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-text-primary group-hover:text-accent-primary transition-colors truncate">
                    {goal.title}
                  </h3>
                  <span className="text-xs px-2.5 py-1 bg-background-elevated text-text-secondary mt-2 inline-block rounded-md border border-border capitalize">
                    {getTypeLabel(goal.roadmap_type)}
                  </span>
                </div>
                <button
                  onClick={() => handleDeleteGoal(goal.id)}
                  className="p-2 hover:bg-accent-error/10 rounded-lg touch-target opacity-0 group-hover:opacity-100 transition-all"
                >
                  <Trash2 size={16} className="text-accent-error" />
                </button>
              </div>

              {goal.description && (
                <p className="text-sm text-text-tertiary mb-4 line-clamp-2">{goal.description}</p>
              )}

              {/* Progress */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-text-secondary">Progress</span>
                  <span className="text-accent-primary font-medium">{goal.progress}%</span>
                </div>
                <div className="h-2 bg-background-elevated rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${goal.progress}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className="h-full bg-gradient-to-r from-accent-primary to-accent-neon rounded-full"
                  />
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between pt-4 border-t border-border/50">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleUpdateProgress(goal.id, goal.progress - 10)}
                    className="w-8 h-8 rounded-lg bg-background-elevated border border-border hover:border-border-light flex items-center justify-center text-text-secondary hover:text-text-primary transition-all"
                  >
                    -
                  </button>
                  <button
                    onClick={() => handleUpdateProgress(goal.id, goal.progress + 10)}
                    className="w-8 h-8 rounded-lg bg-accent-primary text-white flex items-center justify-center hover:bg-accent-primaryHover transition-all"
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={() => setSelectedGoal(goal.id)}
                  className="flex items-center gap-1 text-sm text-accent-primary hover:text-accent-neon transition-colors"
                >
                  <MapPin size={14} />
                  Open Roadmap
                </button>
              </div>
            </motion.div>
          ))}

          {activeGoals.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="col-span-full card text-center py-16"
            >
              <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
                <Target size={40} className="text-accent-primary" />
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary mb-2">No goals yet</h3>
              <p className="text-text-tertiary mb-6">Create your first goal</p>
              <button onClick={() => setShowAddModal(true)} className="btn btn-primary mx-auto">
                <Plus size={20} />
                Add Goal
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Add Goal Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4" role="dialog" aria-modal="true">
          <div className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-lg">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-display font-semibold text-text-primary">Create New Goal</h2>
              <button onClick={() => setShowAddModal(false)} className="p-2 hover:bg-background-elevated rounded-lg touch-target">
                <X size={20} className="text-text-tertiary" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Title <span className="text-accent-error">*</span></label>
                <input
                  type="text"
                  value={newGoal.title}
                  onChange={e => setNewGoal({ ...newGoal, title: e.target.value })}
                  className="input"
                  placeholder="e.g., Become Full Stack Developer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Description</label>
                <textarea
                  value={newGoal.description}
                  onChange={e => setNewGoal({ ...newGoal, description: e.target.value })}
                  className="input min-h-[80px] resize-none"
                  rows={2}
                  placeholder="What's this goal about?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Roadmap Type</label>
                <select
                  value={newGoal.roadmap_type}
                  onChange={e => setNewGoal({ ...newGoal, roadmap_type: e.target.value as any })}
                  className="input capitalize"
                >
                  {roadmapTypes.map(t => (
                    <option key={t} value={t}>{getTypeLabel(t)}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Target Date</label>
                <input
                  type="date"
                  value={newGoal.target_date}
                  onChange={e => setNewGoal({ ...newGoal, target_date: e.target.value })}
                  className="input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Hours/Day</label>
                  <input
                    type="number"
                    value={newGoal.hours_per_day}
                    onChange={e => setNewGoal({ ...newGoal, hours_per_day: parseFloat(e.target.value) || 2 })}
                    className="input"
                    min={0.5}
                    max={12}
                    step={0.5}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Days/Week</label>
                  <input
                    type="number"
                    value={newGoal.days_per_week}
                    onChange={e => setNewGoal({ ...newGoal, days_per_week: parseFloat(e.target.value) || 5 })}
                    className="input"
                    min={1}
                    max={7}
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowAddModal(false)} className="btn btn-secondary flex-1">Cancel</button>
              <button onClick={handleAddGoal} disabled={!newGoal.title.trim()} className="btn btn-primary flex-1">
                Create Goal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Roadmap Editor Modal */}
      {selectedGoal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4">
          <div className="bg-background-card border border-border rounded-2xl p-4 w-full max-w-5xl max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-display font-semibold text-text-primary">Visual Roadmap</h2>
              <button onClick={() => setSelectedGoal(null)} className="p-2 hover:bg-background-elevated rounded-lg touch-target">
                <X size={20} className="text-text-tertiary" />
              </button>
            </div>
            <div className="h-[70vh]">
              <RoadmapEditor 
                goalId={selectedGoal}
                onSave={(nodes, edges) => {
                  supabase.from('goals').update({ nodes: nodes.map(n => n.data) }).eq('id', selectedGoal).then(() => {
                    setSelectedGoal(null)
                    fetchGoals()
                  })
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}