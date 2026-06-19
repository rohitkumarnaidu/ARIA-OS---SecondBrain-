'use client'

import { useState, useEffect, useCallback } from 'react'
import { LayoutGrid, Eye, EyeOff, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'

const STORAGE_KEY = 'dashboard-widget-visibility'

interface WidgetDef {
  id: string
  label: string
}

const DEFAULT_WIDGETS: WidgetDef[] = [
  { id: 'morning-briefing', label: 'Morning Briefing' },
  { id: 'stats-grid', label: 'Stats Grid' },
  { id: 'kpi-strip', label: 'KPI Strip' },
  { id: 'predictions', label: 'AI Predictions' },
  { id: 'arias-pick', label: "ARIA's Pick" },
  { id: 'task-preview', label: 'Task Preview & Quick Actions' },
  { id: 'activity-matrix', label: 'Activity Matrix' },
]

function loadVisibility(): Record<string, boolean> {
  if (typeof window === 'undefined') return {}
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch { /* ignore */ }
  return {}
}

export function useWidgetVisibility() {
  const [visibility, setVisibility] = useState<Record<string, boolean>>(loadVisibility)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(visibility))
  }, [visibility])

  const isVisible = useCallback((id: string) => visibility[id] !== false, [visibility])

  const toggle = useCallback((id: string) => {
    setVisibility(prev => ({ ...prev, [id]: prev[id] === false }))
  }, [])

  return { visibility, isVisible, toggle }
}

interface WidgetToggleProps {
  visibility: Record<string, boolean>
  onToggle: (id: string) => void
}

export function WidgetToggle({ visibility, onToggle }: WidgetToggleProps) {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open])

  return (
    <div className="relative">
      <Button
        onClick={() => setOpen(o => !o)}
        variant="ghost" className="gap-1.5"
        aria-label="Toggle dashboard widgets"
        aria-expanded={open}
      >
        <LayoutGrid size={16} />
        Widgets
      </Button>

      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} aria-hidden="true" />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -8 }}
              transition={{ duration: 0.15 }}
              className="absolute right-0 top-full mt-2 z-50 w-64 rounded-xl bg-background-card border border-border shadow-lg overflow-hidden"
              role="menu"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                <span className="text-sm font-medium text-text-primary">Show Widgets</span>
                <button
                  onClick={() => setOpen(false)}
                  className="p-1 hover:bg-background-elevated rounded-lg"
                  aria-label="Close widget menu"
                >
                  <X size={14} className="text-text-tertiary" />
                </button>
              </div>
              <div className="p-2 space-y-1">
                {DEFAULT_WIDGETS.map(w => {
                  const isVis = visibility[w.id] !== false
                  return (
                    <button
                      key={w.id}
                      onClick={() => onToggle(w.id)}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-background-elevated transition-colors text-left"
                      role="menuitemcheckbox"
                      aria-checked={isVis}
                    >
                      <span className="text-sm text-text-primary">{w.label}</span>
                      {isVis ? (
                        <Eye size={14} className="text-accent-primary" />
                      ) : (
                        <EyeOff size={14} className="text-text-tertiary" />
                      )}
                    </button>
                  )
                })}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
