'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Lightbulb, Trash2, X, Search, ArrowRight } from 'lucide-react'

interface Idea {
  id: string
  title: string
  description?: string
  status: string
  market_research?: string
  competitors?: string
  feasibility_notes?: string
  validation_plan?: string
  created_at: string
}

const statuses = ['raw', 'researching', 'validating', 'building', 'archived'] as const

export default function IdeasPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null)
  const [mounted, setMounted] = useState(false)

  const [newIdea, setNewIdea] = useState({
    title: '',
    description: '',
  })

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchIdeas()
    }
  }, [user, authLoading, router])

  const fetchIdeas = async () => {
    setLoading(true)
    const { data, error } = await supabase
      .from('ideas')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (!error && data) {
      setIdeas(data)
    }
    setLoading(false)
  }

  const handleAddIdea = async () => {
    if (!newIdea.title.trim()) return
    
    const { data, error } = await supabase
      .from('ideas')
      .insert({
        ...newIdea,
        status: 'raw',
      })
      .select()
    
    if (!error && data) {
      setIdeas([data[0], ...ideas])
      setNewIdea({ title: '', description: '' })
      setShowAddModal(false)
    }
  }

  const handleUpdateStatus = async (id: string, status: string) => {
    const { data, error } = await supabase
      .from('ideas')
      .update({ status })
      .eq('id', id)
      .select()
    
    if (!error && data) {
      setIdeas(ideas.map(i => i.id === id ? data[0] : i))
    }
  }

  const handleDeleteIdea = async (id: string) => {
    const { error } = await supabase
      .from('ideas')
      .delete()
      .eq('id', id)
    
    if (!error) {
      setIdeas(ideas.filter(i => i.id !== id))
    }
  }

  const rawIdeas = ideas.filter(i => i.status === 'raw')
  const researchingIdeas = ideas.filter(i => i.status === 'researching')
  const validatingIdeas = ideas.filter(i => i.status === 'validating')
  const buildingIdeas = ideas.filter(i => i.status === 'building')
  const archivedIdeas = ideas.filter(i => i.status === 'archived')

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'raw': return 'bg-text-muted'
      case 'researching': return 'bg-accent-info'
      case 'validating': return 'bg-accent-warning'
      case 'building': return 'bg-accent-primary'
      case 'archived': return 'bg-text-muted/50'
      default: return 'bg-background-elevated'
    }
  }

  const getStatusLabel = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1)
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
          <h1 className="text-2xl font-bold text-text-primary">Ideas</h1>
          <p className="text-text-secondary">Capture and validate your startup ideas</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90"
        >
          <Plus size={20} />
          Capture Idea
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{rawIdeas.length}</div>
          <div className="text-text-secondary text-sm">Raw</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{researchingIdeas.length}</div>
          <div className="text-text-secondary text-sm">Researching</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{validatingIdeas.length}</div>
          <div className="text-text-secondary text-sm">Validating</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{buildingIdeas.length}</div>
          <div className="text-text-secondary text-sm">Building</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{archivedIdeas.length}</div>
          <div className="text-text-secondary text-sm">Archived</div>
        </div>
      </div>

      {/* Ideas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {ideas.map(idea => (
          <div 
            key={idea.id} 
            className="bg-background-card border border-border rounded-xl p-4 cursor-pointer hover:border-accent-primary/50"
            onClick={() => setSelectedIdea(idea)}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="w-10 h-10 rounded-lg bg-accent-warning/20 flex items-center justify-center">
                <Lightbulb size={20} className="text-accent-warning" />
              </div>
              <span className={`text-xs px-2 py-1 rounded text-white ${getStatusColor(idea.status)}`}>
                {getStatusLabel(idea.status)}
              </span>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">{idea.title}</h3>
            {idea.description && (
              <p className="text-text-muted text-sm line-clamp-2">{idea.description}</p>
            )}
            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs text-text-muted">
                {new Date(idea.created_at).toLocaleDateString()}
              </span>
              <ArrowRight size={16} className="text-text-muted" />
            </div>
          </div>
        ))}
      </div>

      {ideas.length === 0 && (
        <div className="text-center py-12">
          <Lightbulb size={48} className="text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No ideas yet</p>
          <p className="text-text-muted text-sm">Capture your first idea!</p>
        </div>
      )}

      {/* Add Idea Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Capture Idea</h2>
              <button onClick={() => setShowAddModal(false)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-text-secondary text-sm mb-1">Idea Title *</label>
                <input
                  type="text"
                  value={newIdea.title}
                  onChange={e => setNewIdea({ ...newIdea, title: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  placeholder="What's your idea?"
                />
              </div>

              <div>
                <label className="block text-text-secondary text-sm mb-1">Description</label>
                <textarea
                  value={newIdea.description}
                  onChange={e => setNewIdea({ ...newIdea, description: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  rows={4}
                  placeholder="Describe your idea..."
                />
              </div>

              <button
                onClick={handleAddIdea}
                className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90"
              >
                Capture Idea
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Idea Detail Modal */}
      {selectedIdea && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">{selectedIdea.title}</h2>
              <button onClick={() => setSelectedIdea(null)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>

            {selectedIdea.description && (
              <p className="text-text-secondary mb-4">{selectedIdea.description}</p>
            )}

            {/* Status Pipeline */}
            <div className="mb-4">
              <label className="block text-text-secondary text-sm mb-2">Status</label>
              <div className="flex gap-2 flex-wrap">
                {statuses.map(s => (
                  <button
                    key={s}
                    onClick={() => handleUpdateStatus(selectedIdea.id, s)}
                    className={`px-3 py-1 rounded-lg text-sm ${
                      selectedIdea.status === s 
                        ? 'bg-accent-primary text-white' 
                        : 'bg-background-elevated text-text-secondary hover:bg-border'
                    }`}
                  >
                    {getStatusLabel(s)}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t border-border">
              <button
                onClick={() => {
                  handleDeleteIdea(selectedIdea.id)
                  setSelectedIdea(null)
                }}
                className="text-accent-error text-sm hover:underline"
              >
                Delete Idea
              </button>
              <button
                onClick={() => setSelectedIdea(null)}
                className="text-accent-primary text-sm hover:underline"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}