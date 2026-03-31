'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, GraduationCap, Trash2, X, Calculator } from 'lucide-react'

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
    if (!authLoading && !user) router.push('/login')
    if (user) fetchData()
  }, [user, authLoading, router])

  const fetchData = async () => {
    setLoading(true)
    const [subjectsRes, marksRes] = await Promise.all([
      supabase.from('subjects').select('*').order('name'),
      supabase.from('marks').select('*').order('date', { ascending: false })
    ])
    if (subjectsRes.data) setSubjects(subjectsRes.data)
    if (marksRes.data) setMarks(marksRes.data)
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
    const totalCredits = subjects.reduce((sum, s) => sum + (s.credits || 3), 0)
    return 0
  }

  const getSubjectMarks = (subjectId: string) => marks.filter(m => m.subject_id === subjectId)
  const getSubjectAverage = (subjectId: string) => {
    const subjectMarks = getSubjectMarks(subjectId)
    if (subjectMarks.length === 0) return 0
    const total = subjectMarks.reduce((sum, m) => sum + (m.marks_obtained / m.max_marks) * 100, 0)
    return Math.round(total / subjectMarks.length)
  }

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Academic Planner</h1>
          <p className="text-text-secondary">Track subjects, marks, and CGPA</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowAddSubjectModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90"><Plus size={20} /> Add Subject</button>
          <button onClick={() => setShowAddMarkModal(true)} className="flex items-center gap-2 bg-background-card border border-border text-text-primary px-4 py-2 rounded-lg hover:bg-background-elevated"><Calculator size={20} /> Log Marks</button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{subjects.length}</div><div className="text-text-secondary text-sm">Subjects</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{marks.length}</div><div className="text-text-secondary text-sm">Marks Logged</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-primary">{calculateCGPA().toFixed(2)}</div><div className="text-text-secondary text-sm">Current CGPA</div></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {subjects.map(subject => {
          const avg = getSubjectAverage(subject.id)
          return (
            <div key={subject.id} className="bg-background-card border border-border rounded-xl p-4">
              <div className="flex items-start justify-between mb-2">
                <div><h3 className="text-text-primary font-semibold">{subject.name}</h3>{subject.code && <span className="text-xs text-text-muted">{subject.code}</span>}</div>
                <button onClick={() => handleDeleteSubject(subject.id)}><Trash2 size={16} className="text-accent-error" /></button>
              </div>
              <div className="flex items-center gap-4 mb-2">
                <span className="text-xs text-text-muted">{subject.credits} credits</span>
                {subject.exam_date && <span className="text-xs text-text-muted">Exam: {subject.exam_date}</span>}
              </div>
              <div className="h-2 bg-background-elevated rounded-full overflow-hidden"><div className={`h-full rounded-full ${avg >= 60 ? 'bg-accent-secondary' : avg >= 40 ? 'bg-accent-warning' : 'bg-accent-error'}`} style={{ width: `${Math.min(100, avg)}%` }} /></div>
              <div className="text-right text-xs text-text-muted mt-1">{avg}% average</div>
            </div>
          )
        })}
      </div>

      {subjects.length === 0 && <div className="text-center py-12"><GraduationCap size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No subjects added yet</p></div>}

      {showAddSubjectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4"><h2 className="text-xl font-semibold text-text-primary">Add Subject</h2><button onClick={() => setShowAddSubjectModal(false)}><X size={24} className="text-text-muted" /></button></div>
            <div className="space-y-4">
              <div><label className="block text-text-secondary text-sm mb-1">Subject Name *</label><input type="text" value={newSubject.name} onChange={e => setNewSubject({ ...newSubject, name: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">Code</label><input type="text" value={newSubject.code} onChange={e => setNewSubject({ ...newSubject, code: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Credits</label><input type="number" value={newSubject.credits} onChange={e => setNewSubject({ ...newSubject, credits: parseInt(e.target.value) || 3 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <button onClick={handleAddSubject} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Add Subject</button>
            </div>
          </div>
        </div>
      )}

      {showAddMarkModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4"><h2 className="text-xl font-semibold text-text-primary">Log Marks</h2><button onClick={() => setShowAddMarkModal(false)}><X size={24} className="text-text-muted" /></button></div>
            <div className="space-y-4">
              <div><label className="block text-text-secondary text-sm mb-1">Subject</label><select value={selectedSubject} onChange={e => setSelectedSubject(e.target.value)} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary">{subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select></div>
              <div className="grid grid-cols-3 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">Type</label><select value={newMark.exam_type} onChange={e => setNewMark({ ...newMark, exam_type: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"><option value="assignment">Assignment</option><option value="midterm">Midterm</option><option value="final">Final</option><option value="practical">Practical</option></select></div>
                <div><label className="block text-text-secondary text-sm mb-1">Marks</label><input type="number" value={newMark.marks_obtained} onChange={e => setNewMark({ ...newMark, marks_obtained: parseFloat(e.target.value) || 0 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Max</label><input type="number" value={newMark.max_marks} onChange={e => setNewMark({ ...newMark, max_marks: parseFloat(e.target.value) || 100 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <button onClick={handleAddMark} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Log Marks</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}