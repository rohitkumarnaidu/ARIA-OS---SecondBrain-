'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore } from '@/lib/taskStore'
import { 
  Clock, Target, TrendingUp, Calendar, 
  CheckCircle, BookOpen, Lightbulb, Zap
} from 'lucide-react'

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth()
  const { tasks, fetchTasks, loading: tasksLoading } = useTaskStore()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchTasks()
    }
  }, [user, authLoading, router, fetchTasks])

  if (!mounted || authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const completedTasks = tasks.filter(t => t.status === 'completed')
  const today = new Date().toISOString().split('T')[0]
  const todayTasks = tasks.filter(t => t.due_date?.startsWith(today))
  
  const productivityScore = tasks.length > 0 
    ? Math.round((completedTasks.length / tasks.length) * 100)
    : 0

  const topTasks = pendingTasks.slice(0, 3)

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-priority-urgent'
      case 'high': return 'text-priority-high'
      case 'medium': return 'text-priority-medium'
      default: return 'text-priority-low'
    }
  }

  return (
    <div className="space-y-6">
      {/* Morning Briefing Header */}
      <div className="bg-gradient-to-r from-accent-primary/20 to-accent-secondary/20 rounded-2xl p-6">
        <h1 className="text-2xl font-bold text-text-primary mb-2">
          {getGreeting()}! 👋
        </h1>
        <p className="text-text-secondary">
          Here's your personalized briefing for today
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Productivity Score */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-text-secondary text-sm">Productivity Score</span>
            <Zap size={18} className="text-accent-warning" />
          </div>
          <div className="text-3xl font-bold text-text-primary">{productivityScore}%</div>
          <div className="mt-2 h-2 bg-background-elevated rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full"
              style={{ width: `${productivityScore}%` }}
            />
          </div>
        </div>

        {/* Tasks Today */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-text-secondary text-sm">Tasks Today</span>
            <CheckCircle size={18} className="text-accent-secondary" />
          </div>
          <div className="text-3xl font-bold text-text-primary">{todayTasks.length || 0}</div>
          <div className="text-text-muted text-sm mt-1">
            {pendingTasks.length} pending
          </div>
        </div>

        {/* Courses Progress */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-text-secondary text-sm">Active Courses</span>
            <BookOpen size={18} className="text-accent-info" />
          </div>
          <div className="text-3xl font-bold text-text-primary">0</div>
          <div className="text-text-muted text-sm mt-1">0 completed</div>
        </div>

        {/* Active Goals */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-text-secondary text-sm">Active Goals</span>
            <Target size={18} className="text-accent-primary" />
          </div>
          <div className="text-3xl font-bold text-text-primary">0</div>
          <div className="text-text-muted text-sm mt-1">0 completed</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Tasks */}
        <div className="lg:col-span-2 bg-background-card border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">Top Tasks</h2>
            <button 
              onClick={() => router.push('/tasks')}
              className="text-accent-primary text-sm hover:underline"
            >
              View all
            </button>
          </div>
          
          {topTasks.length > 0 ? (
            <div className="space-y-3">
              {topTasks.map((task, index) => (
                <div 
                  key={task.id}
                  className="flex items-center gap-4 p-4 bg-background-elevated rounded-lg"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-primary/10 text-accent-primary flex items-center justify-center font-medium">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-text-primary font-medium truncate">{task.title}</div>
                    <div className="text-text-muted text-sm">
                      {task.category} • {task.estimated_minutes || 30} min
                    </div>
                  </div>
                  <div className={`text-sm font-medium ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircle size={48} className="text-accent-secondary mx-auto mb-3 opacity-50" />
              <p className="text-text-secondary">No pending tasks!</p>
              <p className="text-text-muted text-sm">Add a task to get started</p>
            </div>
          )}
        </div>

        {/* ARIA's Pick */}
        <div className="bg-background-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-accent-primary flex items-center justify-center">
              <span className="text-white text-sm font-bold">A</span>
            </div>
            <h2 className="text-lg font-semibold text-text-primary">ARIA's Pick</h2>
          </div>
          
          <div className="bg-background-elevated rounded-lg p-4">
            <p className="text-text-primary mb-3">
              {topTasks.length > 0 
                ? `Start with "${topTasks[0].title}" - it's your highest priority task today.`
                : 'Add some tasks and let ARIA help you prioritize!'
              }
            </p>
            <button 
              onClick={() => router.push('/chat')}
              className="text-accent-primary text-sm hover:underline"
            >
              Chat with ARIA →
            </button>
          </div>

          {/* Quick Actions */}
          <div className="mt-4 space-y-2">
            <button 
              onClick={() => router.push('/tasks')}
              className="w-full flex items-center gap-2 p-3 bg-background-elevated rounded-lg text-text-secondary hover:text-text-primary transition-colors"
            >
              <Clock size={18} />
              <span className="text-sm">Add Task</span>
            </button>
            <button 
              onClick={() => router.push('/ideas')}
              className="w-full flex items-center gap-2 p-3 bg-background-elevated rounded-lg text-text-secondary hover:text-text-primary transition-colors"
            >
              <Lightbulb size={18} />
              <span className="text-sm">Capture Idea</span>
            </button>
          </div>
        </div>
      </div>

      {/* Activity Heatmap Placeholder */}
      <div className="bg-background-card border border-border rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text-primary">Activity</h2>
          <div className="flex items-center gap-2 text-text-muted text-sm">
            <TrendingUp size={16} />
            <span>Last 6 months</span>
          </div>
        </div>
        
        {/* Simple heatmap visualization */}
        <div className="flex gap-1 overflow-x-auto pb-2">
          {Array.from({ length: 30 }, (_, i) => {
            const intensity = Math.random()
            const color = intensity > 0.7 
              ? 'bg-accent-secondary' 
              : intensity > 0.4 
                ? 'bg-accent-secondary/50' 
                : 'bg-background-elevated'
            return (
              <div 
                key={i}
                className={`w-4 h-4 rounded-sm ${color}`}
                title={`Day ${i + 1}`}
              />
            )
          })}
        </div>
        
        <div className="flex items-center gap-2 mt-4 text-text-muted text-sm">
          <span>Less</span>
          <div className="w-4 h-4 bg-background-elevated rounded-sm" />
          <div className="w-4 h-4 bg-accent-secondary/50 rounded-sm" />
          <div className="w-4 h-4 bg-accent-secondary rounded-sm" />
          <span>More</span>
        </div>
      </div>
    </div>
  )
}