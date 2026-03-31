'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, BookOpen, Trash2, Edit2, X, Clock, CheckCircle } from 'lucide-react'

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

export default function CoursesPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)
  const [mounted, setMounted] = useState(false)

  const [newCourse, setNewCourse] = useState({
    title: '',
    platform: 'udemy' as typeof platforms[number],
    url: '',
    total_videos: 0,
    deadline: '',
    why_enrolled: '',
  })

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchCourses()
    }
  }, [user, authLoading, router])

  const fetchCourses = async () => {
    setLoading(true)
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (!error && data) {
      setCourses(data)
    }
    setLoading(false)
  }

  const handleAddCourse = async () => {
    if (!newCourse.title.trim() || !newCourse.deadline) return
    
    const { data, error } = await supabase
      .from('courses')
      .insert({
        ...newCourse,
        deadline: new Date(newCourse.deadline).toISOString(),
        status: 'not_started',
      })
      .select()
    
    if (!error && data) {
      setCourses([data[0], ...courses])
      setNewCourse({ title: '', platform: 'udemy', url: '', total_videos: 0, deadline: '', why_enrolled: '' })
      setShowAddModal(false)
    }
  }

  const handleUpdateProgress = async (id: string, completed: number) => {
    const { data, error } = await supabase
      .from('courses')
      .update({ completed_videos: completed })
      .eq('id', id)
      .select()
    
    if (!error && data) {
      setCourses(courses.map(c => c.id === id ? data[0] : c))
    }
  }

  const handleDeleteCourse = async (id: string) => {
    const { error } = await supabase
      .from('courses')
      .delete()
      .eq('id', id)
    
    if (!error) {
      setCourses(courses.filter(c => c.id !== id))
    }
  }

  const getProgress = (course: Course) => {
    if (!course.total_videos || course.total_videos === 0) return 0
    return Math.round((course.completed_videos / course.total_videos) * 100)
  }

  const activeCourses = courses.filter(c => c.status !== 'completed' && c.status !== 'abandoned')
  const completedCourses = courses.filter(c => c.status === 'completed')

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
          <h1 className="text-2xl font-bold text-text-primary">Courses</h1>
          <p className="text-text-secondary">Track your learning progress</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90"
        >
          <Plus size={20} />
          Add Course
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{activeCourses.length}</div>
          <div className="text-text-secondary text-sm">Active</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{completedCourses.length}</div>
          <div className="text-text-secondary text-sm">Completed</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">
            {courses.reduce((acc, c) => acc + (c.completed_videos || 0), 0)}
          </div>
          <div className="text-text-secondary text-sm">Videos Watched</div>
        </div>
      </div>

      {/* Course List */}
      <div className="space-y-4">
        {activeCourses.map(course => {
          const progress = getProgress(course)
          return (
            <div key={course.id} className="bg-background-card border border-border rounded-xl p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-text-primary font-semibold">{course.title}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-2 py-0.5 bg-background-elevated rounded text-text-secondary capitalize">
                      {course.platform}
                    </span>
                    {course.deadline && (
                      <span className="text-xs text-text-muted">
                        Due: {new Date(course.deadline).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDeleteCourse(course.id)}
                    className="p-2 hover:bg-background-elevated rounded"
                  >
                    <Trash2 size={16} className="text-accent-error" />
                  </button>
                </div>
              </div>

              {course.why_enrolled && (
                <p className="text-text-muted text-sm mb-3">{course.why_enrolled}</p>
              )}

              {/* Progress Bar */}
              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-text-secondary">Progress</span>
                  <span className="text-text-primary">{progress}%</span>
                </div>
                <div className="h-2 bg-background-elevated rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {/* Video Count */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted">
                  {course.completed_videos} / {course.total_videos || '?'} videos
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleUpdateProgress(course.id, Math.max(0, course.completed_videos - 1))}
                    className="px-2 py-1 bg-background-elevated rounded hover:bg-border"
                  >
                    -
                  </button>
                  <button
                    onClick={() => handleUpdateProgress(course.id, course.completed_videos + 1)}
                    className="px-2 py-1 bg-accent-primary text-white rounded hover:bg-accent-primary/90"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          )
        })}

        {activeCourses.length === 0 && (
          <div className="text-center py-12">
            <BookOpen size={48} className="text-text-muted mx-auto mb-3" />
            <p className="text-text-secondary">No courses yet</p>
            <p className="text-text-muted text-sm">Add a course to start tracking</p>
          </div>
        )}
      </div>

      {/* Add Course Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Add Course</h2>
              <button onClick={() => setShowAddModal(false)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-text-secondary text-sm mb-1">Course Title *</label>
                <input
                  type="text"
                  value={newCourse.title}
                  onChange={e => setNewCourse({ ...newCourse, title: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  placeholder="e.g., React Complete Guide"
                />
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Platform</label>
                <select
                  value={newCourse.platform}
                  onChange={e => setNewCourse({ ...newCourse, platform: e.target.value as any })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary capitalize"
                >
                  {platforms.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Course URL</label>
                <input
                  type="url"
                  value={newCourse.url}
                  onChange={e => setNewCourse({ ...newCourse, url: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  placeholder="https://..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Total Videos</label>
                  <input
                    type="number"
                    value={newCourse.total_videos}
                    onChange={e => setNewCourse({ ...newCourse, total_videos: parseInt(e.target.value) || 0 })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                    min={0}
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Deadline *</label>
                  <input
                    type="date"
                    value={newCourse.deadline}
                    onChange={e => setNewCourse({ ...newCourse, deadline: e.target.value })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Why Enrolled?</label>
                <textarea
                  value={newCourse.why_enrolled}
                  onChange={e => setNewCourse({ ...newCourse, why_enrolled: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  rows={2}
                  placeholder="What will you learn?"
                />
              </div>

              <button
                onClick={handleAddCourse}
                className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90"
              >
                Add Course
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}