'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { showError } from '@/lib/toast'
import { Plus, GraduationCap, Trash2, X, Calculator, BookOpen, Award, AlertTriangle, Calendar } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface Subject {
  id: string
  name: string
  code?: string
  credits?: number
  semester?: string
  exam_date?: string
  target_marks?: number
}

interface Mark {
  id: string
  subject_id: string
  exam_type: string
  marks_obtained: number
  max_marks: number
  date: string
}

export default function AcademicsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [marks, setMarks] = useState<Mark[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddSubjectModal, setShowAddSubjectModal] = useState(false)
  const [showAddMarkModal, setShowAddMarkModal] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState<string>('')
  const [mounted, setMounted] = useState(false)

  const [newSubject, setNewSubject] = useState({ name: '', code: '', credits: 3, semester: '', exam_date: '', target_marks: 85 })
  const [newMark, setNewMark] = useState({ exam_type: 'assignment', marks_obtained: 0, max_marks: 100, date: new Date().toISOString().split('T')[0] })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (user) fetchData()
  }, [user])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [subjectsRes, marksRes] = await Promise.all([
        supabase.from('subjects').select('*').order('name'),
        supabase.from('marks').select('*').order('date', { ascending: false })
      ])
      if (subjectsRes.data) setSubjects(subjectsRes.data)
      if (marksRes.data) setMarks(marksRes.data)
    } catch (err) {
      console.error('Failed to fetch academics:', err)
      showError('Failed to load academics data. Please try again.')
    }
    setLoading(false)
  }

  const handleAddSubject = async () => {
    if (!newSubject.name.trim()) return
    await supabase.from('subjects').insert(newSubject)
    setNewSubject({ name: '', code: '', credits: 3, semester: '', exam_date: '', target_marks: 85 })
    setShowAddSubjectModal(false)
    fetchData()
  }

  const handleAddMark = async () => {
    if (!selectedSubject || newMark.marks_obtained < 0) return
    await supabase.from('marks').insert({ ...newMark, subject_id: selectedSubject })
    setNewMark({ exam_type: 'assignment', marks_obtained: 0, max_marks: 100, date: new Date().toISOString().split('T')[0] })
    setShowAddMarkModal(false)
    fetchData()
  }

  const handleDeleteSubject = async (id: string) => {
    await supabase.from('subjects').delete().eq('id', id)
    setSubjects(subjects.filter(s => s.id !== id))
  }

  const calculateCGPA = () => {
    if (subjects.length === 0) return 0
    let totalPoints = 0
    let totalCredits = 0
    for (const subject of subjects) {
      const avg = getSubjectAverage(subject.id)
      const credits = subject.credits || 3
      const gradePoint = getGradePoint(avg)
      totalPoints += gradePoint * credits
      totalCredits += credits
    }
    return totalCredits > 0 ? totalPoints / totalCredits : 0
  }

  const calculateProjectedCGPA = () => {
    const current = calculateCGPA()
    const atRisk = subjects.filter(s => getSubjectAverage(s.id) < 40).length
    if (atRisk > 0) return current - 0.2
    return current + 0.1
  }

  const getGradePoint = (percentage: number) => {
    if (percentage >= 90) return 10
    if (percentage >= 80) return 9
    if (percentage >= 70) return 8
    if (percentage >= 60) return 7
    if (percentage >= 50) return 6
    if (percentage >= 40) return 5
    return 0
  }

  const getAtRiskSubjects = () => subjects.filter(s => getSubjectAverage(s.id) < 40)

  const getExamCountdown = () => {
    const upcoming = subjects.filter(s => s.exam_date).map(s => ({
      name: s.name,
      days: Math.ceil((new Date(s.exam_date!).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    })).filter(s => s.days > 0).sort((a, b) => a.days - b.days)
    return upcoming.slice(0, 3)
  }

  const getSubjectMarks = (subjectId: string) => marks.filter(m => m.subject_id === subjectId)
  const getSubjectAverage = (subjectId: string) => {
    const subjectMarks = getSubjectMarks(subjectId)
    if (subjectMarks.length === 0) return 0
    const total = subjectMarks.reduce((sum, m) => sum + (m.marks_obtained / m.max_marks) * 100, 0)
    return Math.round(total / subjectMarks.length)
  }

  const getProgressColor = (avg: number) => {
    if (avg >= 60) return 'bg-accent-success'
    if (avg >= 40) return 'bg-accent-warning'
    return 'bg-accent-error'
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
            <span className="text-gradient">Academic Planner</span>
          </h1>
          <p className="text-text-secondary">Track subjects, marks, and CGPA</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowAddSubjectModal(true)} className="btn btn-primary gap-2">
            <Plus size={20} /> Add Subject
          </button>
          <button onClick={() => setShowAddMarkModal(true)} className="btn btn-secondary gap-2">
            <Calculator size={20} /> Log Marks
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-3 gap-4"
      >
        {[
          { label: 'Subjects', value: subjects.length, icon: BookOpen, color: 'accent-primary' },
          { label: 'Marks Logged', value: marks.length, icon: Calculator, color: 'accent-info' },
          { label: 'CGPA', value: calculateCGPA().toFixed(2), sub: `Proj: ${calculateProjectedCGPA().toFixed(2)}`, icon: Award, color: 'accent-neon', highlight: true },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className={`card group hover:border-accent-primary/30 transition-all duration-300 ${stat.highlight ? 'border-accent-primary/30' : ''}`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">{stat.label}</span>
              <stat.icon size={18} className={`text-${stat.color} opacity-60 group-hover:opacity-100 transition-opacity`} />
            </div>
            <div className="text-3xl font-display font-bold text-text-primary">{stat.value}</div>
            {stat.sub && <div className="text-xs text-text-tertiary mt-1">{stat.sub}</div>}
          </motion.div>
        ))}
      </motion.div>

      {/* At Risk Alert */}
      <AnimatePresence>
        {getAtRiskSubjects().length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-accent-error/10 border border-accent-error/30 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} className="text-accent-error" />
              <h3 className="text-accent-error font-semibold">At-Risk Subjects</h3>
            </div>
            <div className="flex gap-2 flex-wrap">
              {getAtRiskSubjects().map(s => (
                <span key={s.id} className="bg-accent-error/20 text-accent-error px-3 py-1 rounded-full text-sm border border-accent-error/30">
                  {s.name} ({getSubjectAverage(s.id)}%)
                </span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Exam Countdown */}
      <AnimatePresence>
        {getExamCountdown().length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="card"
          >
            <div className="flex items-center gap-2 mb-4">
              <Calendar size={18} className="text-accent-primary" />
              <h3 className="text-lg font-display font-semibold text-text-primary">Upcoming Exams</h3>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {getExamCountdown().map((exam, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-background-elevated rounded-xl p-4 text-center border border-border"
                >
                  <div className="text-3xl font-display font-bold text-accent-primary">{exam.days}</div>
                  <div className="text-xs text-text-tertiary">days until</div>
                  <div className="text-text-primary text-sm font-medium mt-2 truncate">{exam.name}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Subjects Grid */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <AnimatePresence mode="popLayout">
          {subjects.map((subject, index) => {
            const avg = getSubjectAverage(subject.id)
            return (
              <motion.div
                key={subject.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: index * 0.05 }}
                className="card card-interactive group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-text-primary group-hover:text-accent-primary transition-colors truncate">
                      {subject.name}
                    </h3>
                    {subject.code && <span className="text-xs text-text-tertiary">{subject.code}</span>}
                  </div>
                  <button 
                    onClick={() => handleDeleteSubject(subject.id)}
                    className="p-2 hover:bg-accent-error/10 rounded-lg touch-target opacity-0 group-hover:opacity-100 transition-all"
                  >
                    <Trash2 size={16} className="text-accent-error" />
                  </button>
                </div>

                <div className="flex items-center gap-3 text-sm text-text-tertiary mb-4">
                  <span className="flex items-center gap-1">
                    <Award size={14} />
                    {subject.credits} credits
                  </span>
                  {subject.exam_date && (
                    <span className="flex items-center gap-1">
                      <Calendar size={14} />
                      {subject.exam_date}
                    </span>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Average</span>
                    <span className={`font-medium ${avg >= 60 ? 'text-accent-success' : avg >= 40 ? 'text-accent-warning' : 'text-accent-error'}`}>
                      {avg}%
                    </span>
                  </div>
                  <div className="h-2 bg-background-elevated rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(100, avg)}%` }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                      className={`h-full rounded-full ${getProgressColor(avg)}`}
                    />
                  </div>
                </div>
              </motion.div>
            )
          })}

          {subjects.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="col-span-full card text-center py-16"
            >
              <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
                <GraduationCap size={40} className="text-accent-primary" />
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary mb-2">No subjects yet</h3>
              <p className="text-text-tertiary mb-6">Add your first subject</p>
              <button onClick={() => setShowAddSubjectModal(true)} className="btn btn-primary mx-auto">
                <Plus size={20} />
                Add Subject
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Add Subject Modal */}
      <AnimatePresence>
        {showAddSubjectModal && (
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
                <h2 className="text-xl font-display font-semibold text-text-primary">Add Subject</h2>
                <button onClick={() => setShowAddSubjectModal(false)} className="p-2 hover:bg-background-elevated rounded-lg touch-target">
                  <X size={20} className="text-text-tertiary" />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Name <span className="text-accent-error">*</span></label>
                  <input type="text" value={newSubject.name} onChange={e => setNewSubject({ ...newSubject, name: e.target.value })} className="input" placeholder="e.g., Data Structures" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Code</label>
                    <input type="text" value={newSubject.code} onChange={e => setNewSubject({ ...newSubject, code: e.target.value })} className="input" placeholder="CS201" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Credits</label>
                    <input type="number" value={newSubject.credits} onChange={e => setNewSubject({ ...newSubject, credits: parseInt(e.target.value) || 3 })} className="input" min={1} />
                  </div>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowAddSubjectModal(false)} className="btn btn-secondary flex-1">Cancel</button>
                <button onClick={handleAddSubject} disabled={!newSubject.name.trim()} className="btn btn-primary flex-1">Add Subject</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Add Mark Modal */}
      <AnimatePresence>
        {showAddMarkModal && (
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
                <h2 className="text-xl font-display font-semibold text-text-primary">Log Marks</h2>
                <button onClick={() => setShowAddMarkModal(false)} className="p-2 hover:bg-background-elevated rounded-lg touch-target">
                  <X size={20} className="text-text-tertiary" />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Subject</label>
                  <select value={selectedSubject} onChange={e => setSelectedSubject(e.target.value)} className="input">
                    {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Type</label>
                    <select value={newMark.exam_type} onChange={e => setNewMark({ ...newMark, exam_type: e.target.value })} className="input">
                      <option value="assignment">Assignment</option>
                      <option value="midterm">Midterm</option>
                      <option value="final">Final</option>
                      <option value="practical">Practical</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Marks</label>
                    <input type="number" value={newMark.marks_obtained} onChange={e => setNewMark({ ...newMark, marks_obtained: parseFloat(e.target.value) || 0 })} className="input" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Max</label>
                    <input type="number" value={newMark.max_marks} onChange={e => setNewMark({ ...newMark, max_marks: parseFloat(e.target.value) || 100 })} className="input" />
                  </div>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowAddMarkModal(false)} className="btn btn-secondary flex-1">Cancel</button>
                <button onClick={handleAddMark} disabled={!selectedSubject} className="btn btn-primary flex-1">Log Marks</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}