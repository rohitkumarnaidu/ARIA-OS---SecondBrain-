'use client'

import { Sparkles, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

interface DailyNudgeProps {
  insight?: string
}

export function DailyNudge({ insight }: DailyNudgeProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="relative overflow-hidden rounded-xl border border-border/60"
      style={{
        background: 'linear-gradient(135deg, var(--background-card) 0%, var(--background-elevated) 100%)',
        boxShadow: '0 0 30px rgba(0, 255, 163, 0.06), 0 4px 24px rgba(0, 0, 0, 0.2)',
        backdropFilter: 'blur(20px)',
      }}
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px]"
        style={{
          background: 'linear-gradient(180deg, var(--accent-neon), var(--accent-primary))',
        }}
      />
      <div className="absolute top-0 right-0 w-40 h-40 bg-accent-success/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

      <div className="relative p-4 pl-6">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-accent-success/10 flex items-center justify-center">
            <Sparkles size={16} className="text-accent-neon" />
          </div>
          <div>
            <p className="text-xs font-semibold text-accent-neon uppercase tracking-wider font-display">
              Daily Knowledge Nudge
            </p>
            <p className="text-[10px] text-text-tertiary">ARIA&apos;s insight for today</p>
          </div>
        </div>

        <p className="text-sm text-text-secondary leading-relaxed mb-3">
          {insight || "Review your recent notes on machine learning — there are 3 new connections to explore."}
        </p>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent-primary/10 text-accent-secondary">
            machine-learning
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent-info/10 text-accent-info">
            python
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent-warning/10 text-accent-warning">
            nlp
          </span>
        </div>

        <motion.button
          whileHover={{ x: 4 }}
          className="mt-3 flex items-center gap-1 text-xs font-medium text-accent-primary hover:text-accent-primaryHover transition-colors group"
        >
          Explore
          <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
        </motion.button>
      </div>
    </motion.div>
  )
}
