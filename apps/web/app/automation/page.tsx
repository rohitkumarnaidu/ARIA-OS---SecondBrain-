'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Play, Zap, Target, Clock, RefreshCw, CheckCircle, XCircle, Settings } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function AutomationPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [running, setRunning] = useState<string | null>(null)
  const [results, setResults] = useState<any>(null)
  const [mounted, setMounted] = useState(false)
  const [enabledAutomations, setEnabledAutomations] = useState({
    briefing: true,
    radar: true,
    weekly: true
  })

  useEffect(() => { setMounted(true) }, [])
  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
  }, [user, authLoading, router])

  const runAutomation = async (type: string) => {
    setRunning(type)
    setResults(null)
    
    try {
      const endpoint = type === 'briefing' 
        ? '/api/automation/trigger/briefing'
        : type === 'radar'
        ? '/api/automation/trigger/radar'
        : '/api/automation/trigger/weekly-review'
      
      const response = await fetch(endpoint, {
        headers: { 'Content-Type': 'application/json' }
      })
      
      const data = await response.json()
      setResults(data)
    } catch (error) {
      setResults({ status: 'error', message: 'Failed to run automation' })
    }
    
    setRunning(null)
  }

  const toggleAutomation = (id: string) => {
    setEnabledAutomations(prev => ({
      ...prev,
      [id]: !prev[id as keyof typeof prev]
    }))
  }

  const automations = [
    { id: 'briefing', name: 'Daily Briefing', description: 'Generate your morning briefing with top tasks, goals, and ARIA pick', icon: Zap, schedule: '7 AM daily' },
    { id: 'radar', name: 'Opportunity Radar', description: 'Scan for internships, hackathons, open source, and freelance opportunities', icon: Target, schedule: '6 AM daily' },
    { id: 'weekly', name: 'Weekly Review', description: 'Get a summary of your week: tasks completed, courses progress, income', icon: Clock, schedule: 'Sunday 8 PM' },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  if (!mounted || authLoading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="w-12 h-12 rounded-full border-4 border-accent-primary border-t-transparent animate-pulse-glow"
        />
        <span className="sr-only">Loading...</span>
      </div>
    )
  }

  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-6"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-2xl font-bold text-gradient">Automation Center</h1>
        <p className="text-text-secondary">Run AI agents and cron jobs manually</p>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {automations.map(automation => {
          const Icon = automation.icon
          const isRunning = running === automation.id
          const isEnabled = enabledAutomations[automation.id as keyof typeof enabledAutomations]
          
          return (
            <motion.div 
              key={automation.id}
              whileHover={{ scale: 1.02 }}
              className="card"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                  <Icon className="text-accent-primary" size={20} />
                </div>
                <div>
                  <h3 className="text-text-primary font-semibold">{automation.name}</h3>
                  <p className="text-text-muted text-xs">{automation.schedule}</p>
                </div>
              </div>
              
              <p className="text-text-secondary text-sm mb-4">{automation.description}</p>
              
              <button
                onClick={() => runAutomation(automation.id)}
                disabled={isRunning || !isEnabled}
                className={`w-full flex items-center justify-center gap-2 py-2 rounded-lg ${
                  isRunning 
                    ? 'bg-background-elevated text-text-muted cursor-not-allowed'
                    : isEnabled
                    ? 'btn btn-primary'
                    : 'bg-background-elevated text-text-muted cursor-not-allowed'
                }`}
              >
                {isRunning ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play size={16} />
                    Run Now
                  </>
                )}
              </button>
            </motion.div>
          )
        })}
      </motion.div>

      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`card border ${
              results.status === 'success' ? 'border-accent-secondary' : 'border-accent-error'
            }`}
          >
            <div className="flex items-center gap-2 mb-4">
              {results.status === 'success' ? (
                <CheckCircle className="text-accent-secondary" size={20} />
              ) : (
                <XCircle className="text-accent-error" size={20} />
              )}
              <h3 className="text-text-primary font-semibold">
                {results.status === 'success' ? 'Success' : 'Error'}
              </h3>
            </div>
            
            <pre className="text-text-secondary text-sm overflow-x-auto">
              {JSON.stringify(results, null, 2)}
            </pre>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div variants={itemVariants}>
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Settings className="text-accent-primary" size={20} />
            <h3 className="text-text-primary font-semibold">Automation Settings</h3>
          </div>
          
          <div className="space-y-3">
            {automations.map(automation => {
              const Icon = automation.icon
              const isEnabled = enabledAutomations[automation.id as keyof typeof enabledAutomations]
              
              return (
                <motion.div 
                  key={automation.id}
                  className="flex items-center justify-between p-3 bg-background-elevated rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="text-accent-primary" size={18} />
                    <span className="text-text-primary">{automation.name}</span>
                  </div>
                  <button
                    onClick={() => toggleAutomation(automation.id)}
                    className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${
                      isEnabled ? 'bg-accent-primary' : 'bg-background-border'
                    }`}
                    role="switch"
                    aria-checked={isEnabled}
                  >
                    <motion.span
                      animate={{ x: isEnabled ? 24 : 2 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow"
                    />
                  </button>
                </motion.div>
              )
            })}
          </div>
        </div>
      </motion.div>

      <motion.div variants={itemVariants}>
        <div className="card">
          <h3 className="text-text-primary font-semibold mb-4">Scheduled Automations</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
              <div className="flex items-center gap-3">
                <Zap className="text-accent-primary" size={18} />
                <span className="text-text-primary">Daily Briefing</span>
              </div>
              <span className="text-text-muted text-sm">7:00 AM daily</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
              <div className="flex items-center gap-3">
                <Target className="text-accent-primary" size={18} />
                <span className="text-text-primary">Opportunity Radar</span>
              </div>
              <span className="text-text-muted text-sm">6:00 AM daily</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-background-elevated rounded-lg">
              <div className="flex items-center gap-3">
                <Clock className="text-accent-primary" size={18} />
                <span className="text-text-primary">Weekly Review</span>
              </div>
              <span className="text-text-muted text-sm">Sunday 8:00 PM</span>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
