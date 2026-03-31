'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Target, Trash2, X, Calendar, TrendingUp } from 'lucide-react'
import dynamic from 'next/dynamic'

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
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Goals & Roadmaps</h1>
          <p className="text-text-secondary">Plan your path to success</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90"
        >
          <Plus size={20} />
          Add Goal
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{activeGoals.length}</div>
          <div className="text-text-secondary text-sm">Active Goals</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{completedGoals.length}</div>
          <div className="text-text-secondary text-sm">Completed</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">
            {activeGoals.length > 0 
              ? Math.round(activeGoals.reduce((acc, g) => acc + g.progress, 0) / activeGoals.length)
              : 0}%
          </div>
          <div className="text-text-secondary text-sm">Avg Progress</div>
        </div>
      </div>

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {activeGoals.map(goal => (
          <div key={goal.id} className="bg-background-card border border-border rounded-xl p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-text-primary font-semibold">{goal.title}</h3>
                <span className="text-xs px-2 py-0.5 bg-background-elevated rounded text-text-secondary mt-1 inline-block">
                  {getTypeLabel(goal.roadmap_type)}
                </span>
              </div>
              <button
                onClick={() => handleDeleteGoal(goal.id)}
                className="p-1 hover:bg-background-elevated rounded"
              >
                <Trash2 size={16} className="text-accent-error" />
              </button>
            </div>

            {goal.description && (
              <p className="text-text-muted text-sm mb-3 line-clamp-2">{goal.description}</p>
            )}

            {/* Progress */}
            <div className="mb-3">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-text-secondary">Progress</span>
                <span className="text-text-primary">{goal.progress}%</span>
              </div>
              <div className="h-2 bg-background-elevated rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full"
                  style={{ width: `${goal.progress}%` }}
                />
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleUpdateProgress(goal.id, goal.progress - 10)}
                  className="w-8 h-8 flex items-center justify-center bg-background-elevated rounded hover:bg-border text-text-secondary"
                >
                  -
                </button>
                <button
                  onClick={() => handleUpdateProgress(goal.id, goal.progress + 10)}
                  className="w-8 h-8 flex items-center justify-center bg-accent-primary text-white rounded hover:bg-accent-primary/90"
                >
                  +
                </button>
              </div>
              <button
                onClick={() => setSelectedGoal(goal.id)}
                className="text-xs text-accent-primary hover:underline"
              >
                Open Roadmap →
              </button>
            </div>
          </div>
        ))}
      </div>

      {activeGoals.length === 0 && (
        <div className="text-center py-12">
          <Target size={48} className="text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No goals yet</p>
          <p className="text-text-muted text-sm">Create a goal to start building your roadmap</p>
        </div>
      )}

      {/* Add Goal Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Add Goal</h2>
              <button onClick={() => setShowAddModal(false)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-text-secondary text-sm mb-1">Goal Title *</label>
                <input
                  type="text"
                  value={newGoal.title}
                  onChange={e => setNewGoal({ ...newGoal, title: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  placeholder="e.g., Become Full Stack Developer"
                />
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Description</label>
                <textarea
                  value={newGoal.description}
                  onChange={e => setNewGoal({ ...newGoal, description: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  rows={2}
                  placeholder="What's this goal about?"
                />
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Roadmap Type</label>
                <select
                  value={newGoal.roadmap_type}
                  onChange={e => setNewGoal({ ...newGoal, roadmap_type: e.target.value as any })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary capitalize"
                >
                  {roadmapTypes.map(t => (
                    <option key={t} value={t}>{getTypeLabel(t)}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Target Date</label>
                <input
                  type="date"
                  value={newGoal.target_date}
                  onChange={e => setNewGoal({ ...newGoal, target_date: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Hours/Day</label>
                  <input
                    type="number"
                    value={newGoal.hours_per_day}
                    onChange={e => setNewGoal({ ...newGoal, hours_per_day: parseFloat(e.target.value) || 2 })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                    min={0.5}
                    max={12}
                    step={0.5}
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Days/Week</label>
                  <input
                    type="number"
                    value={newGoal.days_per_week}
                    onChange={e => setNewGoal({ ...newGoal, days_per_week: parseFloat(e.target.value) || 5 })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                    min={1}
                    max={7}
                  />
                </div>
              </div>

              <button
                onClick={handleAddGoal}
                className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90"
              >
                Create Goal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Roadmap Editor Modal */}
      {selectedGoal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background-card border border-border rounded-xl p-4 w-full max-w-5xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Visual Roadmap</h2>
              <button onClick={() => setSelectedGoal(null)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>
            <RoadmapEditor 
              goalId={selectedGoal}
              onSave={(nodes, edges) => {
                console.log('Saving roadmap:', nodes, edges)
                supabase.from('goals').update({ nodes: nodes.map(n => n.data) }).eq('id', selectedGoal).then(() => {
                  setSelectedGoal(null)
                  fetchGoals()
                })
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}