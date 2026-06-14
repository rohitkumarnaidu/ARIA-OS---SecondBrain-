'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { WifiOff, CloudOff } from 'lucide-react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'

export default function OfflineBanner() {
  const { isOnline } = useNetworkStatus()

  return (
    <AnimatePresence>
      {!isOnline && (
        <motion.div
          initial={{ y: -48, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -48, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-accent-warning/20 via-accent-warning/10 to-accent-warning/20 border-b border-accent-warning/30 backdrop-blur-md"
          role="alert"
          aria-live="assertive"
        >
          <div className="flex items-center justify-center gap-3 px-4 py-2.5">
            <WifiOff size={16} className="text-accent-warning" aria-hidden="true" />
            <span className="text-sm font-medium text-accent-warning">
              You are offline
            </span>
            <span className="text-xs text-text-tertiary">
              — some features may be unavailable
            </span>
            <CloudOff size={14} className="text-text-tertiary" aria-hidden="true" />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
