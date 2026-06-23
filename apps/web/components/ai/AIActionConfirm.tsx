'use client'

import { memo, useState } from 'react'
import { AlertTriangle, Check, X, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface AIActionConfirmProps {
  open: boolean
  title: string
  description: string
  onConfirm: () => Promise<void>
  onCancel: () => void
}

const AIActionConfirm = memo(function AIActionConfirm({ open, title, description, onConfirm, onCancel }: AIActionConfirmProps) {
  const [loading, setLoading] = useState(false)

  if (!open) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm"
        onClick={onCancel}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-sm rounded-xl border border-border-default bg-background-card p-5 shadow-2xl"
        >
          <div className="flex items-start gap-3 mb-4">
            <div className="p-2 rounded-full bg-accent-warning/10 shrink-0">
              <AlertTriangle size={18} className="text-accent-warning" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
              <p className="text-xs text-text-secondary mt-1">{description}</p>
            </div>
          </div>
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={onCancel}
              disabled={loading}
              className="btn btn-ghost btn-sm gap-1.5"
            >
              <X size={14} /> Cancel
            </button>
            <button
              onClick={async () => {
                setLoading(true)
                try { await onConfirm() } finally { setLoading(false) }
              }}
              disabled={loading}
              className="btn btn-primary btn-sm gap-1.5"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
              {loading ? 'Executing...' : 'Confirm'}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
})

export { AIActionConfirm }
