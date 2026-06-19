'use client'

import { motion } from 'framer-motion'
import { CheckSquare, Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface TaskEmptyStateProps {
  onAddTask?: () => void
}

export function TaskEmptyState({ onAddTask }: TaskEmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="card text-center py-16"
    >
      <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
        <CheckSquare size={40} className="text-accent-primary" />
      </div>
      <h3 className="text-lg font-display font-semibold text-text-primary mb-2">No tasks found</h3>
      <p className="text-text-tertiary mb-6">Start by adding your first task</p>
      {onAddTask && (
        <Button variant="primary" onClick={onAddTask}>
          <Plus size={20} />
          Add your first task
        </Button>
      )}
    </motion.div>
  )
}
