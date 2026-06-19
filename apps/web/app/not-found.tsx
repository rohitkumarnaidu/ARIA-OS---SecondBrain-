'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Home, Search } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background" role="alert">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full text-center space-y-6"
      >
        <div className="w-20 h-20 rounded-2xl bg-accent-warning/10 flex items-center justify-center mx-auto">
          <Search size={40} className="text-accent-warning" />
        </div>
        <div className="space-y-2">
          <h1 className="text-4xl font-display font-bold text-gradient">404</h1>
          <p className="text-text-secondary">This page doesn&apos;t exist or has been moved.</p>
        </div>
        <Link href="/dashboard" className="btn btn-primary inline-flex items-center gap-2 mx-auto">
          <Home size={16} /> Back to Dashboard
        </Link>
      </motion.div>
    </div>
  )
}
