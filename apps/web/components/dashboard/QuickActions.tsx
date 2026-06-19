'use client'

import { useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, FileText, Sparkles, Target, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface QuickAction {
  label: string
  icon: typeof Plus
  path: string
  description: string
}

const actions: QuickAction[] = [
  { label: 'New Task', icon: Plus, path: '/tasks', description: 'Add a new task' },
  { label: 'New Note', icon: FileText, path: '/ideas', description: 'Capture an idea' },
  { label: 'ARIA Chat', icon: Sparkles, path: '/chat', description: 'Talk to your AI' },
  { label: 'New Goal', icon: Target, path: '/goals', description: 'Set a new goal' },
]

const containerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

export function QuickActions() {
  const router = useRouter()

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="grid grid-cols-2 gap-3"
    >
      {actions.map((action) => (
        <ActionButton key={action.label} action={action} router={router} />
      ))}
    </motion.div>
  )
}

function ActionButton({ action, router }: { action: QuickAction; router: ReturnType<typeof useRouter> }) {
  const handleClick = useCallback(() => {
    router.push(action.path)
  }, [router, action.path])

  return (
    <motion.button
      variants={cardVariants}
      onClick={handleClick}
      className="group relative overflow-hidden rounded-xl p-4 bg-gradient-to-br from-background-card to-background-elevated border border-border hover:border-accent-primary/30 transition-all duration-300 hover:shadow-glow-sm text-left"
      aria-label={`Quick action: ${action.label}`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="relative z-10">
        <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center mb-3 group-hover:bg-accent-primary/20 transition-colors">
          <action.icon size={20} className="text-accent-primary group-hover:scale-110 transition-transform" />
        </div>
        <div className="text-sm font-medium text-text-primary group-hover:text-accent-primary transition-colors">
          {action.label}
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-text-tertiary">{action.description}</span>
          <ChevronRight size={14} className="text-text-tertiary opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
        </div>
      </div>
    </motion.button>
  )
}
