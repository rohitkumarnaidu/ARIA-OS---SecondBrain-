'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore } from '@/lib/taskStore'
import { 
  Clock, Target, TrendingUp, Calendar, 
  CheckCircle, BookOpen, Lightbulb, Zap, 
  ChevronRight, Sparkles, Brain, Activity
} from 'lucide-react'
import { motion } from 'framer-motion'

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth()
  const { tasks, fetchTasks } = useTaskStore()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchTasks()
  }, [user, authLoading, router, fetchTasks])

  if (!mounted || authLoading) {
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

  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const completedTasks = tasks.filter(t => t.status === 'completed')
  const today = new Date().toISOString().split('T')[0]
  const todayTasks = tasks.filter(t => t.due_date?.startsWith(today))
  
  const productivityScore = tasks.length > 0 
    ? Math.round((completedTasks.length / tasks.length) * 100)
    : 0

  const topTasks = pendingTasks.slice(0, 4)

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  const getPriorityStyles = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-priority-urgent/10 text-priority-urgent border-priority-urgent/20'
      case 'high': return 'bg-priority-high/10 text-priority-high border-priority-high/20'
      case 'medium': return 'bg-priority-medium/10 text-priority-medium border-priority-medium/20'
      default: return 'bg-priority-low/10 text-priority-low border-priority-low/20'
    }
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Hero Section with Gradient */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-background-card via-background-elevated to-background-card border border-border">
        {/* Animated background grid */}
        <div className="absolute inset-0 bg-grid opacity-50" />
        
        <div className="relative p-6 md:p-8">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2"
              >
                <Sparkles size={16} className="text-accent-neon" />
                <span className="text-xs font-medium text-text-tertiary tracking-wider uppercase">
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                </span>
              </motion.div>
              <motion.h1 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-3xl md:text-4xl font-display font-bold"
              >
                <span className="text-gradient">{getGreeting()}</span>
                <span className="text-text-primary">,</span>
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-text-secondary max-w-md"
              >
                Your AI-powered productivity command center. Let's make today count.
              </motion.p>
            </div>
            
            {/* ARIA Avatar */}
            <motion.div 
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="hidden md:block relative"
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-primary to-accent-neon p-0.5">
                <div className="w-full h-full rounded-2xl bg-background-card flex items-center justify-center">
                  <Brain size={28} className="text-accent-primary" />
                </div>
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-accent-neon rounded-full animate-pulse" />
            </motion.div>
          </div>
        </div>
      </div>

      {/* Stats Grid - Cyber Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Productivity', value: `${productivityScore}%`, sub: `${completedTasks.length} completed`, icon: Zap, color: 'accent-primary', glow: 'glow-primary' },
          { label: 'Tasks Today', value: todayTasks.length || '0', sub: `${pendingTasks.length} pending`, icon: CheckCircle, color: 'accent-secondary', glow: 'glow-success' },
          { label: 'Active Courses', value: '0', sub: '0 completed', icon: BookOpen, color: 'accent-info', glow: '' },
          { label: 'Active Goals', value: '0', sub: '0 completed', icon: Target, color: 'accent-neon', glow: 'glow-success' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            className={`card group hover:border-${stat.color}/30 transition-all duration-300`}
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">{stat.label}</span>
              <stat.icon size={18} className={`text-${stat.color} opacity-60 group-hover:opacity-100 transition-opacity`} />
            </div>
            <div className="text-2xl font-display font-bold text-text-primary mb-1">{stat.value}</div>
            <div className="text-xs text-text-tertiary">{stat.sub}</div>
            {stat.glow && (
              <div className={`absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none ${stat.glow}`} />
            )}
          </motion.div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tasks Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 card"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
                <Activity size={20} className="text-accent-primary" />
              </div>
              <div>
                <h2 className="text-lg font-display font-semibold text-text-primary">Priority Tasks</h2>
                <p className="text-xs text-text-tertiary">Your focus list for today</p>
              </div>
            </div>
            <button 
              onClick={() => router.push('/tasks')}
              className="btn btn-ghost text-sm gap-1.5"
            >
              View all <ChevronRight size={16} />
            </button>
          </div>
          
          {topTasks.length > 0 ? (
            <div className="space-y-3">
              {topTasks.map((task, index) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  onClick={() => router.push('/tasks')}
                  className="group flex items-center gap-4 p-4 rounded-xl bg-background-elevated/50 border border-transparent hover:border-accent-primary/20 hover:bg-background-elevated transition-all duration-200 cursor-pointer"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-primary/5 flex items-center justify-center text-accent-primary font-display font-semibold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-text-primary font-medium truncate group-hover:text-accent-primary transition-colors">{task.title}</div>
                    <div className="text-xs text-text-tertiary flex items-center gap-2">
                      <span className="capitalize">{task.category}</span>
                      <span className="w-1 h-1 rounded-full bg-text-tertiary" />
                      <span>{task.estimated_minutes || 30} min</span>
                    </div>
                  </div>
                  <div className={`px-2.5 py-1 rounded-md text-xs font-medium border ${getPriorityStyles(task.priority)}`}>
                    {task.priority}
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-10">
              <div className="w-16 h-16 rounded-2xl bg-accent-success/10 flex items-center justify-center mx-auto mb-4">
                <CheckCircle size={32} className="text-accent-success" />
              </div>
              <p className="text-text-primary font-medium">All caught up!</p>
              <p className="text-text-tertiary text-sm mt-1">Add a task to get started</p>
              <button 
                onClick={() => router.push('/tasks')}
                className="btn btn-primary mt-4 text-sm"
              >
                Add Task
              </button>
            </div>
          )}
        </motion.div>

        {/* ARIA's Pick & Quick Actions */}
        <div className="space-y-6">
          {/* ARIA's Pick */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="card relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-neon p-0.5">
                <div className="w-full h-full rounded-xl bg-background-card flex items-center justify-center">
                  <Sparkles size={18} className="text-white" />
                </div>
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary">ARIA's Pick</h3>
            </div>
            
            <div className="relative p-4 rounded-xl bg-background-elevated/50 border border-border/50">
              <p className="text-text-secondary text-sm leading-relaxed">
                {topTasks.length > 0 
                  ? `Start with "${topTasks[0].title}" — it's your highest priority and will set a productive tone for the day.`
                  : 'Add tasks and let ARIA help you prioritize what matters most.'
                }
              </p>
            </div>

            <button 
              onClick={() => router.push('/chat')}
              className="mt-4 w-full btn btn-secondary text-sm justify-between group"
            >
              <span>Chat with ARIA</span>
              <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>

          {/* Quick Actions */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <h3 className="text-sm font-medium text-text-tertiary uppercase tracking-wider mb-4">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { icon: Clock, label: 'Add Task', path: '/tasks', color: 'accent-primary' },
                { icon: Lightbulb, label: 'Capture Idea', path: '/ideas', color: 'accent-warning' },
                { icon: BookOpen, label: 'Track Course', path: '/courses', color: 'accent-info' },
                { icon: Target, label: 'Set Goal', path: '/goals', color: 'accent-secondary' },
              ].map((action) => (
                <button 
                  key={action.label}
                  onClick={() => router.push(action.path)}
                  className="w-full flex items-center gap-3 p-3 rounded-xl bg-background-elevated/50 border border-transparent hover:border-border hover:bg-background-elevated transition-all duration-200 group"
                >
                  <div className={`w-9 h-9 rounded-lg bg-${action.color}/10 flex items-center justify-center`}>
                    <action.icon size={18} className={`text-${action.color}`} />
                  </div>
                  <span className="text-text-secondary group-hover:text-text-primary text-sm font-medium transition-colors">{action.label}</span>
                  <ChevronRight size={16} className="ml-auto text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Activity Heatmap */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
              <TrendingUp size={20} className="text-accent-secondary" />
            </div>
            <div>
              <h2 className="text-lg font-display font-semibold text-text-primary">Activity Matrix</h2>
              <p className="text-xs text-text-tertiary">Your productivity over time</p>
            </div>
          </div>
          <div className="text-xs text-text-tertiary">Last 30 days</div>
        </div>
        
        <div className="flex gap-1.5 overflow-x-auto pb-2 no-scrollbar">
          {Array.from({ length: 30 }, (_, i) => {
            const intensity = Math.random()
            const getColor = () => {
              if (intensity > 0.8) return 'bg-accent-neon shadow-neon-sm'
              if (intensity > 0.6) return 'bg-accent-secondary/60'
              if (intensity > 0.3) return 'bg-accent-primary/40'
              return 'bg-background-elevated'
            }
            return (
              <div 
                key={i}
                className={`w-5 h-8 rounded-sm ${getColor()} transition-all duration-300 hover:scale-110 cursor-pointer`}
                title={`Day ${i + 1}: ${Math.round(intensity * 100)}% activity`}
              />
            )
          })}
        </div>
        
        <div className="flex items-center gap-2 mt-4 text-xs text-text-tertiary">
          <span>Less</span>
          <div className="w-4 h-4 bg-background-elevated rounded-sm" />
          <div className="w-4 h-4 bg-accent-primary/40 rounded-sm" />
          <div className="w-4 h-4 bg-accent-secondary/60 rounded-sm" />
          <div className="w-4 h-4 bg-accent-neon shadow-neon-sm rounded-sm" />
          <span className="ml-1">More</span>
        </div>
      </motion.div>
    </div>
  )
}