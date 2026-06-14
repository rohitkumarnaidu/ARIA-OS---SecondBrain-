'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { showError } from '@/lib/toast'
import { Plus, BookOpen, Trash2, X, Play, Award, Clock, TrendingUp, AlertTriangle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface Course {
  id: string
  title: string
  platform: string
  url?: string
  total_videos?: number
  completed_videos: number
  deadline?: string
  why_enrolled?: string
  status: string
  daily_minutes_needed?: number
  created_at: string
}

const platforms = ['udemy', 'coursera', 'nptel', 'youtube', 'college', 'other'] as const

const platformColors: Record<string, string> = {
  udemy: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  coursera: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  nptel: 'bg-red-500/20 text-red-400 border-red-500/30',
  youtube: 'bg-red-600/20 text-red-500 border-red-600/30',
  college: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  other: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

export default function CoursesPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newCourse, setNewCourse] = useState({
    title: '',
    platform: 'udemy' as typeof platforms[number],
    url: '',
    total_videos: 0,
    deadline: '',
    why_enrolled: '',
  })

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (user) fetchCourses()
  }, [user])

  const fetchCourses = async () => {
    setLoading(true)
    try {
      const { data } = await supabase.from('courses').select('*').order('created_at', { ascending: false })
      if (data) setCourses(data)
    } catch (err) {
      console.error('Failed to fetch courses:', err)
      showError('Failed to load courses. Please try again.')
    }
    setLoading(false)
  }

  const handleAddCourse = async () => {
    if (!newCourse.title.trim() || !newCourse.deadline) return
    
    await supabase.from('courses').insert({
      ...newCourse,
      deadline: new Date(newCourse.deadline).toISOString(),
      status: 'not_started',
    })
    
    setNewCourse({ title: '', platform: 'udemy', url: '', total_videos: 0, deadline: '', why_enrolled: '' })
    setShowAddModal(false)
    fetchCourses()
  }

  const handleUpdateProgress = async (id: string, completed: number) => {
    const { data } = await supabase.from('courses').update({ completed_videos: completed }).eq('id', id).select()
    if (data) setCourses(courses.map(c => c.id === id ? data[0] : c))
  }

  const handleDeleteCourse = async (id: string) => {
    await supabase.from('courses').delete().eq('id', id)
    setCourses(courses.filter(c => c.id !== id))
  }

  const getProgress = (course: Course) => {
    if (!course.total_videos || course.total_videos === 0) return 0
    return Math.round((course.completed_videos / course.total_videos) * 100)
  }

  const calculateDailyMinutes = (course: Course) => {
    if (!course.deadline || course.completed_videos >= (course.total_videos || 0)) return 0
    const daysLeft = Math.max(1, Math.ceil((new Date(course.deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    const remaining = (course.total_videos || 0) - course.completed_videos
    return Math.ceil((remaining * 15) / daysLeft)
  }

  const activeCourses = courses.filter(c => c.status !== 'completed' && c.status !== 'abandoned')
  const completedCourses = courses.filter(c => c.status === 'completed')
  const totalDailyMinutes = activeCourses.reduce((sum, c) => sum + calculateDailyMinutes(c), 0)
  const behindSchedule = activeCourses.filter(c => c.deadline && calculateDailyMinutes(c) > 60)

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
            <span className="text-gradient">Courses</span>
          </h1>
          <p className="text-text-secondary">Track your learning journey</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn btn-primary gap-2">
          <Plus size={20} />
          Add Course
        </button>
      </motion.div>

      {/* Stats */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {[
          { label: 'Active', value: activeCourses.length, icon: Play, color: 'accent-primary' },
          { label: 'Completed', value: completedCourses.length, icon: Award, color: 'accent-success' },
          { label: 'Min/Day', value: totalDailyMinutes, icon: Clock, color: 'accent-warning' },
          { label: 'Watched', value: courses.reduce((a, c) => a + (c.completed_videos || 0), 0), icon: TrendingUp, color: 'accent-neon' },
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

      {/* Behind Schedule Alert */}
      <AnimatePresence>
        {behindSchedule.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-accent-warning/10 border border-accent-warning/30 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} className="text-accent-warning" />
              <h3 className="text-accent-warning font-semibold">Behind Schedule</h3>
            </div>
            <div className="flex gap-2 flex-wrap">
              {behindSchedule.map(c => (
                <span key={c.id} className="bg-accent-warning/20 text-accent-warning px-3 py-1 rounded-full text-sm border border-accent-warning/30">
                  {c.title}
                </span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Courses */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="space-y-4"
      >
        <AnimatePresence mode="popLayout">
          {activeCourses.map((course, index) => {
            const progress = getProgress(course)
            const dailyMin = calculateDailyMinutes(course)
            
            return (
              <motion.div
                key={course.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: index * 0.05 }}
                className="card card-interactive group"
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-text-primary group-hover:text-accent-primary transition-colors truncate">
                      {course.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-2 flex-wrap">
                      <span className={`px-2.5 py-1 rounded-md text-xs font-medium border capitalize ${platformColors[course.platform] || platformColors.other}`}>
                        {course.platform}
                      </span>
                      {course.deadline && (
                        <span className="flex items-center gap-1 text-xs text-text-tertiary">
                          <Clock size={12} />
                          Due: {new Date(course.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleDeleteCourse(course.id)}
                    className="p-2 hover:bg-accent-error/10 rounded-lg touch-target opacity-0 group-hover:opacity-100 transition-all"
                    aria-label="Delete course"
                  >
                    <Trash2 size={16} className="text-accent-error" />
                  </button>
                </div>

                {course.why_enrolled && (
                  <p className="text-sm text-text-tertiary mb-4 line-clamp-2">{course.why_enrolled}</p>
                )}

                {/* Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-text-secondary">Progress</span>
                    <span className="text-accent-primary font-medium">{progress}%</span>
                  </div>
                  <div className="h-2 bg-background-elevated rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-accent-primary to-accent-neon rounded-full"
                    />
                  </div>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-text-tertiary">
                      {course.completed_videos} / {course.total_videos || '?'} videos
                    </span>
                    {dailyMin > 0 && (
                      <span className="text-xs px-2 py-1 bg-accent-warning/10 text-accent-warning rounded-md border border-accent-warning/20">
                        {dailyMin} min/day
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleUpdateProgress(course.id, Math.max(0, course.completed_videos - 1))}
                      className="w-8 h-8 rounded-lg bg-background-elevated border border-border hover:border-border-light flex items-center justify-center text-text-secondary hover:text-text-primary transition-all"
                    >
                      -
                    </button>
                    <button
                      onClick={() => handleUpdateProgress(course.id, course.completed_videos + 1)}
                      className="w-8 h-8 rounded-lg bg-accent-primary text-white flex items-center justify-center hover:bg-accent-primaryHover transition-all"
                    >
                      +
                    </button>
                  </div>
                </div>
              </motion.div>
            )
          })}

          {activeCourses.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="card text-center py-16"
            >
              <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
                <BookOpen size={40} className="text-accent-primary" />
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary mb-2">No courses yet</h3>
              <p className="text-text-tertiary mb-6">Start your learning journey</p>
              <button onClick={() => setShowAddModal(true)} className="btn btn-primary mx-auto">
                <Plus size={20} />
                Add Course
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
              className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-lg"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-display font-semibold text-text-primary">Add New Course</h2>
                <button onClick={() => setShowAddModal(false)} className="p-2 hover:bg-background-elevated rounded-lg touch-target">
                  <X size={20} className="text-text-tertiary" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Title <span className="text-accent-error">*</span></label>
                  <input
                    type="text"
                    value={newCourse.title}
                    onChange={e => setNewCourse({ ...newCourse, title: e.target.value })}
                    className="input"
                    placeholder="e.g., React Complete Guide"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Platform</label>
                    <select
                      value={newCourse.platform}
                      onChange={e => setNewCourse({ ...newCourse, platform: e.target.value as any })}
                      className="input capitalize"
                    >
                      {platforms.map(p => (
                        <option key={p} value={p} className="capitalize">{p}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Total Videos</label>
                    <input
                      type="number"
                      value={newCourse.total_videos}
                      onChange={e => setNewCourse({ ...newCourse, total_videos: parseInt(e.target.value) || 0 })}
                      className="input"
                      min={0}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Deadline <span className="text-accent-error">*</span></label>
                  <input
                    type="date"
                    value={newCourse.deadline}
                    onChange={e => setNewCourse({ ...newCourse, deadline: e.target.value })}
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Why Enrolled?</label>
                  <textarea
                    value={newCourse.why_enrolled}
                    onChange={e => setNewCourse({ ...newCourse, why_enrolled: e.target.value })}
                    className="input min-h-[80px] resize-none"
                    placeholder="What will you learn?"
                    rows={3}
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowAddModal(false)} className="btn btn-secondary flex-1">Cancel</button>
                <button onClick={handleAddCourse} disabled={!newCourse.title.trim() || !newCourse.deadline} className="btn btn-primary flex-1">
                  Add Course
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}