'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import {
  Sparkles,
  Brain,
  Lightbulb,
  Clock,
  Target,
  BookOpen,
  Activity,
  AlertCircle,
  CheckCircle2,
  Loader2,
  XCircle,
} from 'lucide-react'

interface Activity {
  id: string
  agentName: string
  action: string
  timestamp: string
  status: 'running' | 'completed' | 'failed'
}

interface AgentActivityFeedProps {
  activities?: Activity[]
  className?: string
}

const agentIconMap: Record<string, React.ReactNode> = {
  briefing: <Sparkles size={14} className="text-accent-primary" aria-hidden="true" />,
  memory: <Brain size={14} className="text-accent-neon" aria-hidden="true" />,
  learning: <Lightbulb size={14} className="text-accent-warning" aria-hidden="true" />,
  opportunity: <Target size={14} className="text-accent-primary" aria-hidden="true" />,
  task: <CheckCircle2 size={14} className="text-accent-success" aria-hidden="true" />,
  weekly_review: <BookOpen size={14} className="text-accent-info" aria-hidden="true" />,
  sleep: <Clock size={14} className="text-accent-neon" aria-hidden="true" />,
  nudge: <Activity size={14} className="text-accent-warning" aria-hidden="true" />,
}

const statusConfig = {
  running: {
    icon: <Loader2 size={12} className="animate-spin" aria-hidden="true" />,
    color: 'text-accent-primary',
    label: 'Running',
  },
  completed: {
    icon: <CheckCircle2 size={12} aria-hidden="true" />,
    color: 'text-accent-success',
    label: 'Completed',
  },
  failed: {
    icon: <XCircle size={12} aria-hidden="true" />,
    color: 'text-accent-error',
    label: 'Failed',
  },
}

function getAgentIcon(agentName: string): React.ReactNode {
  const key = agentName.toLowerCase().replace(/\s+/g, '_')
  return agentIconMap[key] ?? <Brain size={14} className="text-text-secondary" aria-hidden="true" />
}

function getRelativeTime(timestamp: string): string {
  const now = Date.now()
  const time = new Date(timestamp).getTime()
  const diff = now - time
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (seconds < 60) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

const listVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, x: -8 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    x: 8,
    transition: { duration: 0.2 },
  },
}

export function AgentActivityFeed({ activities = [], className }: AgentActivityFeedProps) {
  const status = statusConfig

  return (
    <div
      className={cn(
        'rounded-xl overflow-hidden',
        'bg-background-card border border-border',
        'flex flex-col',
        className,
      )}
    >
      <div
        className="flex items-center gap-2 px-4 py-3 shrink-0"
        style={{ borderBottom: '1px solid rgba(70,70,79,0.15)' }}
      >
        <Activity size={14} style={{ color: 'var(--accent-primary)' }} aria-hidden="true" />
        <span className="text-sm font-semibold text-text-primary font-display">Agent Activity</span>
        {activities.length > 0 && (
          <span
            className="ml-auto text-[11px] font-mono px-1.5 py-0.5 rounded-md"
            style={{
              background: 'rgba(99,102,241,0.1)',
              color: 'var(--accent-secondary)',
            }}
          >
            {activities.length}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto max-h-[320px] scroll-smooth">
        {activities.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 px-4">
            <div
              className="flex items-center justify-center w-10 h-10 rounded-full mb-3"
              style={{ background: 'rgba(99,102,241,0.08)' }}
            >
              <Activity size={18} style={{ color: 'var(--accent-primary)' }} aria-hidden="true" />
            </div>
            <p className="text-sm text-text-secondary font-body">No recent activity</p>
            <p className="text-xs text-text-tertiary font-body mt-1">
              Agent activity will appear here
            </p>
          </div>
        ) : (
          <motion.ul
            variants={listVariants}
            initial="hidden"
            animate="visible"
            className="divide-y divide-border/50"
          >
            <AnimatePresence mode="popLayout">
              {activities.map((activity) => {
                const s = status[activity.status]
                return (
                  <motion.li
                    key={activity.id}
                    variants={itemVariants}
                    layout
                    exit="exit"
                    className="px-4 py-3 transition-colors hover:bg-background-elevated/30"
                  >
                    <div className="flex items-start gap-3">
                      <span className="shrink-0 flex items-center justify-center w-7 h-7 rounded-lg bg-background-elevated border border-border/60 mt-0.5">
                        {getAgentIcon(activity.agentName)}
                      </span>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-text-primary truncate">
                            {activity.agentName}
                          </span>
                          <span className="text-[10px] text-text-tertiary font-mono shrink-0">
                            {getRelativeTime(activity.timestamp)}
                          </span>
                        </div>
                        <p className="text-xs text-text-secondary mt-0.5 leading-relaxed line-clamp-2">
                          {activity.action}
                        </p>
                      </div>

                      <span
                        className={cn(
                          'shrink-0 flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded-md',
                          s.color,
                        )}
                        style={{
                          background:
                            activity.status === 'running'
                              ? 'rgba(99,102,241,0.1)'
                              : activity.status === 'failed'
                                ? 'rgba(244,63,94,0.1)'
                                : 'rgba(0,255,163,0.08)',
                        }}
                      >
                        {s.icon}
                        {s.label}
                      </span>
                    </div>
                  </motion.li>
                )
              })}
            </AnimatePresence>
          </motion.ul>
        )}

        {activities.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="px-4 py-2 text-center"
            style={{ borderTop: '1px solid rgba(70,70,79,0.15)' }}
          >
            <button
              className="text-[11px] font-medium text-accent-primary hover:text-accent-primaryHover transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary rounded px-2 py-1"
              aria-label="View all activity"
            >
              View all activity
            </button>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export type { Activity, AgentActivityFeedProps }
