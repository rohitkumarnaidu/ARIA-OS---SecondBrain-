'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, FileText, Trash2, ExternalLink, X, Tag } from 'lucide-react'

interface Resource {
  id: string
  title: string
  url: string
  resource_type: string
  tags: string[]
  notes?: string
  ai_summary?: string
  is_archived: boolean
  created_at: string
}

const resourceTypes = ['article', 'book', 'github', 'tool', 'paper', 'thread', 'other']

export default function ResourcesPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newResource, setNewResource] = useState({ title: '', url: '', resource_type: 'article', tags: '', notes: '' })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchResources()
  }, [user, authLoading, router])

  const fetchResources = async () => {
    setLoading(true)
    const { data } = await supabase.from('resources').select('*').order('created_at', { ascending: false })
    if (data) setResources(data)
    setLoading(false)
  }

  const handleAddResource = async () => {
    if (!newResource.title.trim() || !newResource.url.trim()) return
    await supabase.from('resources').insert({
      title: newResource.title,
      url: newResource.url,
      resource_type: newResource.resource_type,
      tags: newResource.tags.split(',').map(t => t.trim()).filter(Boolean),
      notes: newResource.notes || null,
    })
    setNewResource({ title: '', url: '', resource_type: 'article', tags: '', notes: '' })
    setShowAddModal(false)
    fetchResources()
  }

  const handleDelete = async (id: string) => {
    await supabase.from('resources').delete().eq('id', id)
    setResources(resources.filter(r => r.id !== id))
  }

  const activeResources = resources.filter(r => !r.is_archived)
  const archivedResources = resources.filter(r => r.is_archived)

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Resource Library</h1>
          <p className="text-text-secondary">Save articles, books, tools, and more</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Plus size={20} /> Add Resource
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{activeResources.length}</div><div className="text-text-secondary text-sm">Active</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{archivedResources.length}</div><div className="text-text-secondary text-sm">Archived</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{resources.length}</div><div className="text-text-secondary text-sm">Total</div></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {activeResources.map(resource => (
          <div key={resource.id} className="bg-background-card border border-border rounded-xl p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="w-10 h-10 rounded-lg bg-accent-info/20 flex items-center justify-center"><FileText size={20} className="text-accent-info" /></div>
              <button onClick={() => handleDelete(resource.id)}><Trash2 size={16} className="text-accent-error" /></button>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">{resource.title}</h3>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="text-xs px-2 py-0.5 bg-background-elevated rounded text-text-secondary capitalize">{resource.resource_type}</span>
              {resource.tags?.map((tag, i) => (<span key={i} className="text-xs px-2 py-0.5 bg-accent-primary/20 rounded text-accent-primary">{tag}</span>))}
            </div>
            <a href={resource.url} target="_blank" rel="noopener noreferrer" className="text-accent-primary text-sm hover:underline flex items-center gap-1"><ExternalLink size={14} /> Open</a>
          </div>
        ))}
      </div>

      {activeResources.length === 0 && <div className="text-center py-12"><FileText size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No resources saved yet</p></div>}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Add Resource</h2>
              <button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button>
            </div>
            <div className="space-y-4">
              <div><label className="block text-text-secondary text-sm mb-1">Title *</label><input type="text" value={newResource.title} onChange={e => setNewResource({ ...newResource, title: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              <div><label className="block text-text-secondary text-sm mb-1">URL *</label><input type="url" value={newResource.url} onChange={e => setNewResource({ ...newResource, url: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              <div><label className="block text-text-secondary text-sm mb-1">Type</label><select value={newResource.resource_type} onChange={e => setNewResource({ ...newResource, resource_type: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary capitalize">{resourceTypes.map(t => <option key={t} value={t}>{t}</option>)}</select></div>
              <div><label className="block text-text-secondary text-sm mb-1">Tags (comma separated)</label><input type="text" value={newResource.tags} onChange={e => setNewResource({ ...newResource, tags: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="react, python, ai" /></div>
              <div><label className="block text-text-secondary text-sm mb-1">Notes</label><textarea value={newResource.notes} onChange={e => setNewResource({ ...newResource, notes: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" rows={2} /></div>
              <button onClick={handleAddResource} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Save Resource</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}