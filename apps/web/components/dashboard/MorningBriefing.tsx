'use client'

import { useMemo } from 'react'
import { format, isBefore, isAfter, setHours } from 'date-fns'
import { Sun, Moon, CloudSun, Brain, Target, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

interface MorningBriefingProps {
  completedToday: number
  totalToday: number
  streak?: number
  userName?: string
}

export function MorningBriefing({ completedToday, totalToday, streak = 0, userName = 'there' }: MorningBriefingProps) {
  const greeting = useMemo(() => {
    const now = new Date()
    if (isBefore(now, setHours(now, 12)) && isAfter(now, setHours(now, 5))) return { text: 'Good morning', Icon: Sun }
    if (isBefore(now, setHours(now, 17)) && isAfter(now, setHours(now, 12))) return { text: 'Good afternoon', Icon: CloudSun }
    return { text: 'Good evening', Icon: Moon }
  }, [])

  const focusSuggestion = useMemo(() => {
    if (totalToday === 0) return { text: 'Set a task to get started', icon: Target }
    const remaining = totalToday - completedToday
    if (remaining === 0) return { text: 'All tasks done — time to plan ahead!', icon: Sparkles }
    const pct = Math.round((completedToday / totalToday) * 100)
    if (pct < 30) return { text: `${remaining} tasks remain — let's pick up the pace`, icon: Target }
    if (pct < 70) return { text: `${remaining} tasks left — you're making good progress`, icon: Brain }
    return { text: `${remaining} more to go — almost there!`, icon: Sparkles }
  }, [completedToday, totalToday])

  const GreetingIcon = greeting.Icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-accent-primary/20 via-accent-primary/5 to-background-card border border-accent-primary/20"
    >
      <div className="absolute inset-0 bg-grid opacity-30" aria-hidden="true" />
      <div className="absolute top-0 right-0 w-64 h-64 bg-accent-neon/10 rounded-full blur-3xl" aria-hidden="true" />
      <div className="relative p-6 md:p-8">
        <div className="flex items-start justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-neon p-0.5">
                <div className="w-full h-full rounded-xl bg-background-card flex items-center justify-center">
                  <GreetingIcon size={20} className="text-accent-primary" />
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">
                  {greeting.text}, <span className="text-gradient">{userName}</span>
                </p>
                <time dateTime={format(new Date(), 'yyyy-MM-dd')} className="text-xs text-text-tertiary">
                  {format(new Date(), 'EEEE, MMMM d, yyyy')}
                </time>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-background-elevated/50 border border-border/50">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-accent-success" />
                  <span className="text-sm text-text-primary font-medium">{completedToday}</span>
                  <span className="text-xs text-text-tertiary">/ {totalToday} done</span>
                </div>
              </div>

              {streak > 0 && (
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-background-elevated/50 border border-border/50">
                  <Sparkles size={14} className="text-accent-warning" />
                  <span className="text-sm text-text-primary font-medium">{streak}</span>
                  <span className="text-xs text-text-tertiary">day streak</span>
                </div>
              )}

              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-background-elevated/50 border border-border/50">
                {focusSuggestion.icon === Target && <Target size={14} className="text-accent-primary" />}
                {focusSuggestion.icon === Sparkles && <Sparkles size={14} className="text-accent-neon" />}
                {focusSuggestion.icon === Brain && <Brain size={14} className="text-accent-secondary" />}
                <span className="text-xs text-text-secondary">{focusSuggestion.text}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 w-full bg-background-elevated/50 rounded-full h-1.5 overflow-hidden" role="progressbar" aria-valuenow={totalToday > 0 ? Math.round((completedToday / totalToday) * 100) : 0} aria-valuemin={0} aria-valuemax={100}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: totalToday > 0 ? `${(completedToday / totalToday) * 100}%` : '0%' }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-full rounded-full bg-gradient-to-r from-accent-primary to-accent-neon"
          />
        </div>
      </div>
    </motion.div>
  )
}
