'use client'

import { useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { Button } from '@/components/ui/Button'

interface AriasPickProps {
  insight?: string
}

export function AriasPick({ insight }: AriasPickProps) {
  const router = useRouter()

  const handleChat = useCallback(() => {
    router.push('/chat')
  }, [router])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="card relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" aria-hidden="true" />

      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-neon p-0.5">
          <div className="w-full h-full rounded-xl bg-background-card flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
        </div>
        <h3 className="text-lg font-display font-semibold text-text-primary">
          ARIA&apos;s Pick
        </h3>
      </div>

      <div className="relative p-4 rounded-xl bg-background-elevated/50 border border-border/50 border-l-accent-neon">
        <p className="text-xs font-medium text-accent-neon uppercase tracking-wider mb-2">
          ARIA says
        </p>
        <p className="text-text-secondary text-sm leading-relaxed">
          {insight || "You're on a 3-day streak with your morning routine. Keep it up!"}
        </p>
      </div>

      <Button
        onClick={handleChat}
        variant="secondary"
        className="mt-4 w-full text-sm justify-between group"
        aria-label="Chat with ARIA"
      >
        <span>Chat with ARIA</span>
        <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
      </Button>
    </motion.div>
  )
}
