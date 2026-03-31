'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Wallet, Trash2, X, TrendingUp } from 'lucide-react'

interface Income {
  id: string
  source_type: string
  amount: number
  platform?: string
  description?: string
  date: string
  hours_spent?: number
  effective_hourly_rate?: number
  created_at: string
}

const sourceTypes = ['freelance', 'project', 'stipend', 'investment', 'other']

export default function IncomePage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [income, setIncome] = useState<Income[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newIncome, setNewIncome] = useState({ source_type: 'freelance', amount: 0, platform: '', description: '', date: new Date().toISOString().split('T')[0], hours_spent: 0 })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchIncome()
  }, [user, authLoading, router])

  const fetchIncome = async () => {
    setLoading(true)
    const { data } = await supabase.from('income_entries').select('*').order('date', { ascending: false })
    if (data) setIncome(data)
    setLoading(false)
  }

  const handleAdd = async () => {
    if (newIncome.amount <= 0) return
    const rate = newIncome.hours_spent ? Math.round(newIncome.amount / newIncome.hours_spent) : null
    await supabase.from('income_entries').insert({ ...newIncome, effective_hourly_rate: rate })
    setNewIncome({ source_type: 'freelance', amount: 0, platform: '', description: '', date: new Date().toISOString().split('T')[0], hours_spent: 0 })
    setShowAddModal(false)
    fetchIncome()
  }

  const handleDelete = async (id: string) => {
    await supabase.from('income_entries').delete().eq('id', id)
    setIncome(income.filter(i => i.id !== id))
  }

  const totalThisMonth = income.filter(i => i.date.startsWith(new Date().toISOString().slice(0, 7))).reduce((sum, i) => sum + i.amount, 0)
  const totalAll = income.reduce((sum, i) => sum + i.amount, 0)
  const totalHours = income.reduce((sum, i) => sum + (i.hours_spent || 0), 0)
  const avgRate = totalHours > 0 ? Math.round(totalAll / totalHours) : 0

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Income Tracker</h1>
          <p className="text-text-secondary">Track your earnings and hourly rates</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Plus size={20} /> Log Income
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-secondary">₹{totalThisMonth.toLocaleString()}</div><div className="text-text-secondary text-sm">This Month</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">₹{totalAll.toLocaleString()}</div><div className="text-text-secondary text-sm">Total Earned</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{totalHours}h</div><div className="text-text-secondary text-sm">Total Hours</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-accent-primary">₹{avgRate}/hr</div><div className="text-text-secondary text-sm">Avg Rate</div></div>
      </div>

      <div className="bg-background-card border border-border rounded-xl p-4">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Recent Income</h2>
        <div className="space-y-3">
          {income.map(entry => (
            <div key={entry.id} className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
              <div>
                <div className="text-text-primary font-medium">₹{entry.amount.toLocaleString()}</div>
                <div className="text-text-muted text-sm">{entry.source_type} {entry.platform && `• ${entry.platform}`}</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-xs text-text-muted">{entry.date}</div>
                  {entry.effective_hourly_rate && <div className="text-xs text-accent-primary">₹{entry.effective_hourly_rate}/hr</div>}
                </div>
                <button onClick={() => handleDelete(entry.id)}><Trash2 size={16} className="text-accent-error" /></button>
              </div>
            </div>
          ))}
          {income.length === 0 && <p className="text-text-muted text-center py-4">No income logged yet</p>}
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Log Income</h2>
              <button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">Source</label><select value={newIncome.source_type} onChange={e => setNewIncome({ ...newIncome, source_type: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary">{sourceTypes.map(s => <option key={s} value={s}>{s}</option>)}</select></div>
                <div><label className="block text-text-secondary text-sm mb-1">Amount (₹) *</label><input type="number" value={newIncome.amount} onChange={e => setNewIncome({ ...newIncome, amount: parseFloat(e.target.value) || 0 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-text-secondary text-sm mb-1">Platform</label><input type="text" value={newIncome.platform} onChange={e => setNewIncome({ ...newIncome, platform: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="Fiverr, Upwork..." /></div>
                <div><label className="block text-text-secondary text-sm mb-1">Date</label><input type="date" value={newIncome.date} onChange={e => setNewIncome({ ...newIncome, date: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              </div>
              <div><label className="block text-text-secondary text-sm mb-1">Hours Spent</label><input type="number" value={newIncome.hours_spent} onChange={e => setNewIncome({ ...newIncome, hours_spent: parseFloat(e.target.value) || 0 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
              <button onClick={handleAdd} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Log Income</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}