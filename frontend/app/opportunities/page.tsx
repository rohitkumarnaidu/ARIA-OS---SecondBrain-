'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Radar, Trash2, ExternalLink, X, Briefcase, Code, Heart, DollarSign } from 'lucide-react'

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

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Opportunity Radar</h1>
          <p className="text-text-secondary">Internships, hackathons, fellowships and more</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Plus size={20} /> Add Opportunity
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{newCount}</div><div className="text-text-secondary text-sm">New</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{appliedCount}</div><div className="text-text-secondary text-sm">Applied</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{opportunities.filter(o => o.status === 'accepted').length}</div><div className="text-text-secondary text-sm">Accepted</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{opportunities.length}</div><div className="text-text-secondary text-sm">Total</div></div>
      </div>

      <div className="flex gap-2 flex-wrap">
        <button onClick={() => setFilter('all')} className={`px-3 py-1 rounded-lg text-sm ${filter === 'all' ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}>All</button>
        {opportunityTypes.map(t => (<button key={t} onClick={() => setFilter(t)} className={`px-3 py-1 rounded-lg text-sm capitalize ${filter === t ? 'bg-accent-primary text-white' : 'bg-background-elevated text-text-secondary'}`}>{t.replace('_', ' ')}</button>))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(opp => {
          const Icon = typeIcons[opp.opportunity_type as keyof typeof typeIcons] || Radar
          return (
            <div key={opp.id} className="bg-background-card border border-border rounded-xl p-4">
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
            </div>
          )
        })}
      </div>

      {filtered.length === 0 && <div className="text-center py-12"><Radar size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No opportunities found</p></div>}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
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
              <button onClick={handleAdd} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Add Opportunity</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}