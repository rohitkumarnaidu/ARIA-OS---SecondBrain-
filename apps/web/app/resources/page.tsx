'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, FileText, Trash2, ExternalLink, X, Tag } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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

  if (!mounted || authLoading || loading) return (
    <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
      <div className="relative">
        <div className="w-12 h-12 border-2 border-accent-primary/30 rounded-full" />
        <div className="absolute inset-0 w-12 h-12 border-2 border-transparent border-t-accent-primary rounded-full animate-spin" />
        <div className="absolute inset-1 w-10 h-10 border border-accent-info/50 rounded-full animate-pulse-glow" />
      </div>
      <span className="sr-only">Loading...</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-text-primary text-gradient bg-gradient-to-r from-accent-primary via-accent-info to-accent-success">
            Resource Library
          </h1>
          <p className="text-text-secondary">Save articles, books, tools, and more</p>
        </div>
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowAddModal(true)} 
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={20} /> Add Resource
        </motion.button>
      </motion.div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Active', value: activeResources.length },
          { label: 'Archived', value: archivedResources.length },
          { label: 'Total', value: resources.length }
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div className="text-2xl font-bold text-text-primary">{stat.value}</div>
            <div className="text-text-secondary text-sm">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence mode="popLayout">
          {activeResources.map((resource, index) => (
            <motion.div
              key={resource.id}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: index * 0.05 }}
              className="card"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="w-10 h-10 rounded-lg bg-accent-info/20 flex items-center justify-center">
                  <FileText size={20} className="text-accent-info" />
                </div>
                <motion.button 
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => handleDelete(resource.id)}
                >
                  <Trash2 size={16} className="text-accent-error" />
                </motion.button>
              </div>
              <h3 className="text-text-primary font-semibold mb-1">{resource.title}</h3>
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <span className="text-xs px-2 py-0.5 bg-background-elevated rounded text-text-secondary capitalize">
                  {resource.resource_type}
                </span>
                {resource.tags?.map((tag, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 bg-accent-primary/20 rounded text-accent-primary">
                    {tag}
                  </span>
                ))}
              </div>
              <a 
                href={resource.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-accent-primary text-sm hover:underline flex items-center gap-1"
              >
                <ExternalLink size={14} /> Open
              </a>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {activeResources.length === 0 && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <FileText size={48} className="text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No resources saved yet</p>
        </motion.div>
      )}

      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-text-primary">Add Resource</h2>
                <motion.button 
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setShowAddModal(false)}
                >
                  <X size={24} className="text-text-muted" />
                </motion.button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Title *</label>
                  <input 
                    type="text" 
                    value={newResource.title} 
                    onChange={e => setNewResource({ ...newResource, title: e.target.value })} 
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" 
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">URL *</label>
                  <input 
                    type="url" 
                    value={newResource.url} 
                    onChange={e => setNewResource({ ...newResource, url: e.target.value })} 
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" 
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Type</label>
                  <select 
                    value={newResource.resource_type} 
                    onChange={e => setNewResource({ ...newResource, resource_type: e.target.value })} 
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary capitalize"
                  >
                    {resourceTypes.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Tags (comma separated)</label>
                  <input 
                    type="text" 
                    value={newResource.tags} 
                    onChange={e => setNewResource({ ...newResource, tags: e.target.value })} 
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" 
                    placeholder="react, python, ai" 
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Notes</label>
                  <textarea 
                    value={newResource.notes} 
                    onChange={e => setNewResource({ ...newResource, notes: e.target.value })} 
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" 
                    rows={2} 
                  />
                </div>
                <motion.button 
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleAddResource} 
                  className="btn btn-primary w-full"
                >
                  Save Resource
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}