'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Play, Zap, Target, Clock, RefreshCw, CheckCircle, XCircle } from 'lucide-react'

export default function AutomationPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [running, setRunning] = useState<string | null>(null)
  const [results, setResults] = useState<any>(null)
  const [mounted, setMounted] = useState(false)

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

  const automations = [
    { id: 'briefing', name: 'Daily Briefing', description: 'Generate your morning briefing with top tasks, goals, and ARIA pick', icon: Zap },
    { id: 'radar', name: 'Opportunity Radar', description: 'Scan for internships, hackathons, open source, and freelance opportunities', icon: Target },
    { id: 'weekly', name: 'Weekly Review', description: 'Get a summary of your week: tasks completed, courses progress, income', icon: Clock },
  ]

  if (!mounted || authLoading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Automation Center</h1>
        <p className="text-text-secondary">Run AI agents and cron jobs manually</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {automations.map(automation => {
          const Icon = automation.icon
          const isRunning = running === automation.id
          
          return (
            <div key={automation.id} className="bg-background-card border border-border rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                  <Icon className="text-accent-primary" size={20} />
                </div>
                <div>
                  <h3 className="text-text-primary font-semibold">{automation.name}</h3>
                  <p className="text-text-muted text-xs">
                    {automation.id === 'briefing' && 'Runs at 7 AM daily'}
                    {automation.id === 'radar' && 'Runs at 6 AM daily'}
                    {automation.id === 'weekly' && 'Runs Sunday 8 PM'}
                  </p>
                </div>
              </div>
              
              <p className="text-text-secondary text-sm mb-4">{automation.description}</p>
              
              <button
                onClick={() => runAutomation(automation.id)}
                disabled={isRunning}
                className={`w-full flex items-center justify-center gap-2 py-2 rounded-lg ${
                  isRunning 
                    ? 'bg-background-elevated text-text-muted cursor-not-allowed'
                    : 'bg-accent-primary text-white hover:bg-accent-primary/90'
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
            </div>
          )
        })}
      </div>

      {results && (
        <div className={`bg-background-card border rounded-xl p-6 ${
          results.status === 'success' ? 'border-accent-secondary' : 'border-accent-error'
        }`}>
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
        </div>
      )}

      <div className="bg-background-card border border-border rounded-xl p-6">
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
    </div>
  )
}