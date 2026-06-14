'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Lightbulb, Trash2, X, Search, ArrowRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
        <motion.div
          className="relative w-12 h-12"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        >
          <div className="absolute inset-0 rounded-full border-2 border-accent-primary/30" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-accent-primary animate-pulse-glow" />
        </motion.div>
        <span className="sr-only">Loading...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div 
        className="flex items-center justify-between"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div>
          <h1 className="text-2xl font-bold text-gradient bg-gradient-to-r from-accent-primary via-accent-warning to-accent-primary bg-[length:200%_auto] animate-pulse">
            Ideas
          </h1>
          <p className="text-text-secondary">Capture and validate your startup ideas</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Capture Idea
        </button>
      </motion.div>

      {/* Stats */}
      <motion.div 
        className="grid grid-cols-5 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <motion.div 
          className="card bg-background-card border border-border rounded-xl p-4"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <div className="text-2xl font-bold text-text-primary">{rawIdeas.length}</div>
          <div className="text-text-secondary text-sm">Raw</div>
        </motion.div>
        <motion.div 
          className="card bg-background-card border border-border rounded-xl p-4"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <div className="text-2xl font-bold text-text-primary">{researchingIdeas.length}</div>
          <div className="text-text-secondary text-sm">Researching</div>
        </motion.div>
        <motion.div 
          className="card bg-background-card border border-border rounded-xl p-4"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <div className="text-2xl font-bold text-text-primary">{validatingIdeas.length}</div>
          <div className="text-text-secondary text-sm">Validating</div>
        </motion.div>
        <motion.div 
          className="card bg-background-card border border-border rounded-xl p-4"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <div className="text-2xl font-bold text-text-primary">{buildingIdeas.length}</div>
          <div className="text-text-secondary text-sm">Building</div>
        </motion.div>
        <motion.div 
          className="card bg-background-card border border-border rounded-xl p-4"
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <div className="text-2xl font-bold text-text-primary">{archivedIdeas.length}</div>
          <div className="text-text-secondary text-sm">Archived</div>
        </motion.div>
      </motion.div>

      {/* Ideas Grid */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <AnimatePresence mode="popLayout">
          {ideas.map(idea => (
            <motion.div 
              key={idea.id}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
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
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {ideas.length === 0 && (
        <motion.div 
          className="text-center py-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <Lightbulb size={48} className="text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No ideas yet</p>
          <p className="text-text-muted text-sm">Capture your first idea!</p>
        </motion.div>
      )}

      {/* Add Idea Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
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
                  className="btn btn-primary w-full"
                >
                  Capture Idea
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Idea Detail Modal */}
      <AnimatePresence>
        {selectedIdea && (
          <motion.div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedIdea(null)}
          >
            <motion.div
              className="bg-background-card border border-border rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
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
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
