'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Plus, Trash2, X } from 'lucide-react'
import { useIncomeStore } from '@/lib/stores'
import type { IncomeEntry } from '@/lib/types'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { createLogger } from '@/lib/utils/logger'

const sourceTypes = ['freelance', 'project', 'stipend', 'investment', 'other']

export default function IncomePage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const { items: income, loading, error, fetch: fetchIncome, create, remove } = useIncomeStore()
  const logger = createLogger('IncomePage')
  const [showAddModal, setShowAddModal] = useState(false)

  const [newIncome, setNewIncome] = useState({ source_type: 'freelance', amount: 0, platform: '', description: '', date: new Date().toISOString().split('T')[0], hours_spent: 0 })

  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (user) fetchIncome()
  }, [user, fetchIncome])

  const handleAdd = async () => {
    if (newIncome.amount <= 0) return
    logger.info('Adding income entry', { source_type: newIncome.source_type, amount: newIncome.amount, platform: newIncome.platform, hours_spent: newIncome.hours_spent })
    try {
      const rate = newIncome.hours_spent ? Math.round(newIncome.amount / newIncome.hours_spent) : undefined
      await create({ ...newIncome, effective_hourly_rate: rate })
      logger.info('Income entry created successfully', { amount: newIncome.amount, source_type: newIncome.source_type })
      setNewIncome({ source_type: 'freelance', amount: 0, platform: '', description: '', date: new Date().toISOString().split('T')[0], hours_spent: 0 })
      setShowAddModal(false)
    } catch (err) {
      logger.error('Failed to create income entry', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const handleDelete = async (id: string) => {
    logger.info('Deleting income entry', { id })
    try {
      await remove(id)
      logger.info('Income entry deleted successfully', { id })
    } catch (err) {
      logger.error('Failed to delete income entry', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const totalThisMonth = income.filter(i => i.date.startsWith(new Date().toISOString().slice(0, 7))).reduce((sum, i) => sum + i.amount, 0)
  const totalAll = income.reduce((sum, i) => sum + i.amount, 0)
  const totalHours = income.reduce((sum, i) => sum + (i.hours_spent || 0), 0)
  const avgRate = totalHours > 0 ? Math.round(totalAll / totalHours) : 0

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (authLoading || loading) return (
    <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
      <motion.div 
        className="w-12 h-12 border-4 border-accent-primary border-t-transparent rounded-full animate-pulse-glow"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
      <span className="sr-only">Loading...</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <motion.div 
        className="flex items-center justify-between"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div>
          <h1 className="text-2xl font-bold text-gradient">Income Tracker</h1>
          <p className="text-text-secondary">Track your earnings and hourly rates</p>
        </div>
        <Button variant="primary" icon={<Plus size={20} />} onClick={() => setShowAddModal(true)}>
          Log Income
        </Button>
      </motion.div>

      {error && (
        <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'This Month', value: `₹${totalThisMonth.toLocaleString()}`, color: 'text-accent-secondary' },
          { label: 'Total Earned', value: `₹${totalAll.toLocaleString()}`, color: 'text-text-primary' },
          { label: 'Total Hours', value: `${totalHours}h`, color: 'text-text-primary' },
          { label: 'Avg Rate', value: `₹${avgRate}/hr`, color: 'text-accent-primary' }
        ].map((stat, i) => (
          <motion.div 
            key={stat.label}
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i, duration: 0.4 }}
          >
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-text-secondary text-sm">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <motion.div 
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        <h2 className="text-lg font-semibold text-text-primary mb-4">Recent Income</h2>
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {income.map((entry, index) => (
              <motion.div 
                key={entry.id}
                className="flex items-center justify-between p-3 bg-background-elevated rounded-lg"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20, height: 0 }}
                transition={{ delay: index * 0.05, duration: 0.3 }}
                layout
              >
                <div>
                  <div className="text-text-primary font-medium">₹{entry.amount.toLocaleString()}</div>
                  <div className="text-text-muted text-sm">{entry.source_type} {entry.platform && `• ${entry.platform}`}</div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs text-text-muted">{entry.date}</div>
                    {entry.effective_hourly_rate && <div className="text-xs text-accent-primary">₹{entry.effective_hourly_rate}/hr</div>}
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(entry.id)}>
                    <Trash2 size={16} className="text-accent-error" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {income.length === 0 && <p className="text-text-muted text-center py-4">No income logged yet</p>}
        </div>
      </motion.div>

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
                <h2 className="text-xl font-semibold text-gradient">Log Income</h2>
                <Button variant="ghost" size="icon" onClick={() => setShowAddModal(false)}>
                  <X size={24} className="text-text-muted" />
                </Button>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><label htmlFor="income-source" className="block text-text-secondary text-sm mb-1">Source</label><select id="income-source" value={newIncome.source_type} onChange={e => setNewIncome({ ...newIncome, source_type: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary">{sourceTypes.map(s => <option key={s} value={s}>{s}</option>)}</select></div>
                  <div><label htmlFor="income-amount" className="block text-text-secondary text-sm mb-1">Amount (₹) *</label><input id="income-amount" type="number" value={newIncome.amount} onChange={e => setNewIncome({ ...newIncome, amount: parseFloat(e.target.value) || 0 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label htmlFor="income-platform" className="block text-text-secondary text-sm mb-1">Platform</label><input id="income-platform" type="text" value={newIncome.platform} onChange={e => setNewIncome({ ...newIncome, platform: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="Fiverr, Upwork..." /></div>
                  <div><label htmlFor="income-date" className="block text-text-secondary text-sm mb-1">Date</label><input id="income-date" type="date" value={newIncome.date} onChange={e => setNewIncome({ ...newIncome, date: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                </div>
                <div><label htmlFor="income-hours" className="block text-text-secondary text-sm mb-1">Hours Spent</label><input id="income-hours" type="number" value={newIncome.hours_spent} onChange={e => setNewIncome({ ...newIncome, hours_spent: parseFloat(e.target.value) || 0 })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" /></div>
                <Button variant="primary" onClick={handleAdd} className="w-full">
                  Log Income
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
