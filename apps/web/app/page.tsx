'use client'

import { useRouter } from 'next/navigation'
import { Brain, ArrowRight, Sparkles, Shield, Zap } from 'lucide-react'
import ThreeBackground from '@/components/ThreeBackground'
import { motion } from 'framer-motion'

export default function Home() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-background-dark relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <ThreeBackground />
      </div>
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-background-dark/80 via-transparent to-background-dark/90" />

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="max-w-2xl w-full text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-accent-primary to-accent-neon rounded-2xl mb-6 shadow-glow-lg">
              <Brain size={40} className="text-white" />
            </div>
            <h1 className="text-5xl md:text-6xl font-display font-bold text-text-primary mb-4">
              <span className="text-gradient">ARIA OS</span>
            </h1>
            <p className="text-lg md:text-xl text-text-secondary mb-3 max-w-lg mx-auto">
              Your personal AI productivity system
            </p>
            <p className="text-sm text-text-tertiary mb-10 max-w-md mx-auto">
              Tasks, courses, habits, goals, sleep tracking, and more — all powered by local AI.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <button
              onClick={() => router.push('/login')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-accent-primary hover:bg-accent-primaryHover text-white font-medium py-3 px-8 rounded-lg transition-all duration-200 shadow-glow-sm hover:shadow-glow"
            >
              Get Started
              <ArrowRight size={18} />
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-glass-medium hover:bg-glass-heavy text-text-primary font-medium py-3 px-8 rounded-lg border border-border transition-all duration-200"
            >
              <Zap size={18} />
              Dashboard
            </button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-lg mx-auto"
          >
            <div className="p-5 rounded-xl bg-glass-medium border border-border backdrop-blur-sm">
              <Sparkles size={20} className="text-accent-primary mb-2 mx-auto" />
              <div className="text-2xl font-display font-bold text-accent-primary mb-1">15+</div>
              <div className="text-xs text-text-tertiary">Modules</div>
            </div>
            <div className="p-5 rounded-xl bg-glass-medium border border-border backdrop-blur-sm">
              <Brain size={20} className="text-accent-neon mb-2 mx-auto" />
              <div className="text-2xl font-display font-bold text-accent-neon mb-1">AI</div>
              <div className="text-xs text-text-tertiary">Powered</div>
            </div>
            <div className="p-5 rounded-xl bg-glass-medium border border-border backdrop-blur-sm">
              <Shield size={20} className="text-accent-warning mb-2 mx-auto" />
              <div className="text-2xl font-display font-bold text-accent-warning mb-1">Free</div>
              <div className="text-xs text-text-tertiary">Forever</div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
