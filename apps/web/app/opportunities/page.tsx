'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Radar, Trash2, ExternalLink, X, Briefcase, Code, Heart, DollarSign, Trophy } from 'lucide-react'

interface Opportunity {
  id: string
  title: string
  company?: string
  url: string
  opportunity_type: string
  description?: string
  skills_required: string[]
  deadline?: string
  skill_match?: number
  status: string
  created_at: string
}

const opportunityTypes = ['internship', 'hackathon', 'open_source', 'fellowship', 'freelance', 'competition']

const typeIcons = { internship: Briefcase, hackathon: Code, open_source: Code, fellowship: Heart, freelance: DollarSign, competition: Trophy }

export default function OpportunitiesPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [filter, setFilter] = useState('all')
  const [mounted, setMounted] = useState(false)

  const [newOpp, setNewOpp] = useState({ title: '', company: '', url: '', opportunity_type: 'internship', description: '', deadline: '' })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchOpportunities()
  }, [user, authLoading, router])

  const fetchOpportunities = async () => {
    setLoading(true)
    const { data } = await supabase.from('opportunities').select('*').order('created_at', { ascending: false })
    if (data) setOpportunities(data)
    setLoading(false)
  }

  const handleAdd = async () => {
    if (!newOpp.title.trim() || !newOpp.url.trim()) return
    await supabase.from('opportunities').insert({ ...newOpp, status: 'new' })
    setNewOpp({ title: '', company: '', url: '', opportunity_type: 'internship', description: '', deadline: '' })
    setShowAddModal(false)
    fetchOpportunities()
  }

  const handleDelete = async (id: string) => {
    await supabase.from('opportunities').delete().eq('id', id)
    setOpportunities(opportunities.filter(o => o.id !== id))
  }

  const handleUpdateStatus = async (id: string, status: string) => {
    await supabase.from('opportunities').update({ status }).eq('id', id)
    setOpportunities(opportunities.map(o => o.id === id ? { ...o, status } : o))
  }

  const filtered = filter === 'all' ? opportunities : opportunities.filter(o => o.opportunity_type === filter)
  const newCount = opportunities.filter(o => o.status === 'new').length
  const appliedCount = opportunities.filter(o => o.status === 'applied').length

  if (!mounted || authLoading || loading) return (
    <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
      <div className="animate-pulse-glow w-12 h-12 border-2 border-accent-primary border-t-transparent rounded-full" />
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
          <h1 className="text-2xl font-bold text-gradient">Opportunity Radar</h1>
          <p className="text-text-secondary">Internships, hackathons, fellowships and more</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn btn-primary flex items-center gap-2">
          <Plus size={20} /> Add Opportunity
        </button>
      </motion.div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { count: newCount, label: 'New' },
          { count: appliedCount, label: 'Applied' },
          { count: opportunities.filter(o => o.status === 'accepted').length, label: 'Accepted' },
          { count: opportunities.length, label: 'Total' }
        ].map((stat, i) => (
          <motion.div 
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div className="text-2xl font-bold text-text-primary">{stat.count}</div>
            <div className="text-text-secondary text-sm">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <div className="flex gap-2 flex-wrap">
        <button onClick={() => setFilter('all')} className={`px-3 py-1 rounded-lg text-sm ${filter === 'all' ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}>All</button>
        {opportunityTypes.map(t => (<button key={t} onClick={() => setFilter(t)} className={`px-3 py-1 rounded-lg text-sm capitalize ${filter === t ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}>{t.replace('_', ' ')}</button>))}
      </div>

      <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence>
          {filtered.map(opp => {
            const Icon = typeIcons[opp.opportunity_type as keyof typeof typeIcons] || Radar
            return (
              <motion.div 
                key={opp.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="card"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="w-10 h-10 rounded-lg bg-accent-warning/20 flex items-center justify-center"><Icon size={20} className="text-accent-warning" /></div>
                  <button onClick={() => handleDelete(opp.id)}><Trash2 size={16} className="text-accent-error" /></button>
                </div>
                <h3 className="text-text-primary font-semibold mb-1">{opp.title}</h3>
                {opp.company && <p className="text-text-muted text-sm mb-2">{opp.company}</p>}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="text-xs px-2 py-0.5 bg-background-elevated rounded text-text-secondary capitalize">{opp.opportunity_type.replace('_', ' ')}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${opp.status === 'applied' ? 'bg-accent-info text-white' : opp.status === 'accepted' ? 'bg-accent-secondary text-white' : 'bg-accent-warning text-black'}`}>{opp.status}</span>
                </div>
                <div className="flex items-center justify-between">
                  <a href={opp.url} target="_blank" rel="noopener noreferrer" className="text-accent-primary text-sm hover:underline flex items-center gap-1"><ExternalLink size={14} /> Apply</a>
                  <select value={opp.status} onChange={e => handleUpdateStatus(opp.id, e.target.value)} className="text-xs bg-background-elevated rounded px-2 py-1 text-text-secondary">
                    <option value="new">New</option><option value="saved">Saved</option><option value="applied">Applied</option><option value="rejected">Rejected</option><option value="accepted">Accepted</option>
                  </select>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </motion.div>

      {filtered.length === 0 && <div className="text-center py-12"><Radar size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No opportunities found</p></div>}

      <AnimatePresence>
        {showAddModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 backdrop-blur-sm bg-black/50 flex items-center justify-center z-50"
          >
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="card p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-text-primary">Add Opportunity</h2>
                <button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button>
              </div>
              <div className="space-y-4">
                <div><label className="block text-text-secondary text-sm mb-1">Title *</label><input type="text" value={newOpp.title} onChange={e => setNewOpp({ ...newOpp, title: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Company</label><input type="text" value={newOpp.company} onChange={e => setNewOpp({ ...newOpp, company: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">URL *</label><input type="url" value={newOpp.url} onChange={e => setNewOpp({ ...newOpp, url: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Type</label><select value={newOpp.opportunity_type} onChange={e => setNewOpp({ ...newOpp, opportunity_type: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary capitalize">{opportunityTypes.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}</select></div>
                <div><label className="block text-text-secondary text-sm mb-1">Description</label><textarea value={newOpp.description} onChange={e => setNewOpp({ ...newOpp, description: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" rows={2} /></div>
                <button onClick={handleAdd} className="btn btn-primary w-full">Add Opportunity</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
