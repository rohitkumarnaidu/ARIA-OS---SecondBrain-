'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, FolderKanban, Trash2, X, ExternalLink, Github } from 'lucide-react'

interface Project {
  id: string
  title: string
  description?: string
  phase: string
  github_url?: string
  live_url?: string
  next_action?: string
  blocker?: string
  income_source_id?: string
  created_at: string
}

const phases = ['planning', 'design', 'build', 'test', 'launch', 'maintain']

export default function ProjectsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newProject, setNewProject] = useState({ title: '', description: '', phase: 'planning', github_url: '', live_url: '', next_action: '' })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchProjects()
  }, [user, authLoading, router])

  const fetchProjects = async () => {
    setLoading(true)
    const { data } = await supabase.from('projects').select('*').order('created_at', { ascending: false })
    if (data) setProjects(data)
    setLoading(false)
  }

  const handleAdd = async () => {
    if (!newProject.title.trim()) return
    await supabase.from('projects').insert(newProject)
    setNewProject({ title: '', description: '', phase: 'planning', github_url: '', live_url: '', next_action: '' })
    setShowAddModal(false)
    fetchProjects()
  }

  const handleDelete = async (id: string) => {
    await supabase.from('projects').delete().eq('id', id)
    setProjects(projects.filter(p => p.id !== id))
  }

  const handleUpdatePhase = async (id: string, phase: string) => {
    await supabase.from('projects').update({ phase }).eq('id', id)
    setProjects(projects.map(p => p.id === id ? { ...p, phase } : p))
  }

  const handleAddBlocker = async (id: string, blocker: string) => {
    await supabase.from('projects').update({ blocker }).eq('id', id)
    setProjects(projects.map(p => p.id === id ? { ...p, blocker } : p))
  }

  const handleResolveBlocker = async (id: string) => {
    await supabase.from('projects').update({ blocker: null }).eq('id', id)
    setProjects(projects.map(p => p.id === id ? { ...p, blocker: undefined } : p))
  }

  const phaseCounts = phases.reduce((acc, p) => ({ ...acc, [p]: projects.filter(pr => pr.phase === p).length }), {} as Record<string, number>)

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Projects</h1>
          <p className="text-text-secondary">Track your building projects</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Plus size={20} /> New Project
        </button>
      </div>

      <div className="grid grid-cols-6 gap-2">
        {phases.map(p => (<div key={p} className="bg-background-card border border-border rounded-xl p-3 text-center"><div className="text-xl font-bold text-text-primary">{phaseCounts[p]}</div><div className="text-xs text-text-muted capitalize">{p}</div></div>))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map(project => (
          <div key={project.id} className="bg-background-card border border-border rounded-xl p-4">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-text-primary font-semibold">{project.title}</h3>
              <button onClick={() => handleDelete(project.id)}><Trash2 size={16} className="text-accent-error" /></button>
            </div>
            {project.description && <p className="text-text-muted text-sm mb-3 line-clamp-2">{project.description}</p>}
            <div className="mb-3">
              <select value={project.phase} onChange={e => handleUpdatePhase(project.id, e.target.value)} className="w-full bg-background-elevated text-text-secondary text-sm rounded px-2 py-1 capitalize">
                {phases.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div className="flex gap-2">
              {project.github_url && <a href={project.github_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-text-muted hover:text-accent-primary"><Github size={14} /> GitHub</a>}
              {project.live_url && <a href={project.live_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-text-muted hover:text-accent-primary"><ExternalLink size={14} /> Live</a>}
            </div>
            {project.next_action && <div className="mt-2 p-2 bg-background-elevated rounded text-xs text-text-muted">Next: {project.next_action}</div>}
            
            {/* Blocker Section */}
            {project.blocker ? (
              <div className="mt-2 p-2 bg-accent-error/10 border border-accent-error rounded text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-accent-error">🚫 Blocked: {project.blocker}</span>
                  <button onClick={() => handleResolveBlocker(project.id)} className="text-accent-secondary text-xs">Resolve</button>
                </div>
              </div>
            ) : (
              <div className="mt-2">
                <button 
                  onClick={() => {
                    const blocker = prompt('What is blocking this project?')
                    if (blocker) handleAddBlocker(project.id, blocker)
                  }}
                  className="text-xs text-text-muted hover:text-accent-warning"
                >
                  + Add Blocker
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {projects.length === 0 && <div className="text-center py-12"><FolderKanban size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No projects yet</p></div>}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">New Project</h2>
              <button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button>
            </div>
            <div className="space-y-4">
              <div><label className="block text-text-secondary text-sm mb-1">Project Name *</label><input type="text" value={newProject.title} onChange={e => setNewProject({ ...newProject, title: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              <div><label className="block text-text-secondary text-sm mb-1">Description</label><textarea value={newProject.description} onChange={e => setNewProject({ ...newProject, description: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" rows={2} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">GitHub URL</label><input type="url" value={newProject.github_url} onChange={e => setNewProject({ ...newProject, github_url: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Live URL</label><input type="url" value={newProject.live_url} onChange={e => setNewProject({ ...newProject, live_url: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <div><label className="block text-text-secondary text-sm mb-1">Next Action</label><input type="text" value={newProject.next_action} onChange={e => setNewProject({ ...newProject, next_action: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="What to do next?" /></div>
              <button onClick={handleAdd} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Create Project</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}