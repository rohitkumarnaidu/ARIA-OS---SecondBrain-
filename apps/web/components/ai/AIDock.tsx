'use client'

import { useState, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, X, Send, RefreshCw, ExternalLink } from 'lucide-react'
import { ThinkingIndicator } from './ThinkingIndicator'
import { StreamingText } from './StreamingText'
import { SuggestionChips } from './SuggestionChips'
import { useStreamingChat } from '@/lib/ai/hooks'
import type { SuggestionChip } from './SuggestionChips'

interface AIDockProps {
  className?: string
}

type DockState = 'idle' | 'open' | 'thinking' | 'streaming'

const thinkingMessages = [
  'ARIA Thinking...',
  'Analyzing context...',
  'Processing knowledge...',
  'Generating insights...',
]

const suggestedPrompts: SuggestionChip[] = [
  { id: 'summarize', label: 'Summarize my week' },
  { id: 'focus', label: 'What should I focus on?' },
  { id: 'related', label: 'Find related notes' },
  { id: 'draft', label: 'Draft a follow-up' },
]

export function AIDock({ className }: AIDockProps) {
  const router = useRouter()
  const [state, setState] = useState<DockState>('idle')
  const [inputValue, setInputValue] = useState('')
  const [isHovered, setIsHovered] = useState(false)
  const { messages, isStreaming, error, connectionState, sendMessage, cancelStream, clearMessages } =
    useStreamingChat()
  const stateRef = useRef(state)

  stateRef.current = state

  const streamedText = isStreaming
    ? messages
        .filter((m) => m.role === 'assistant')
        .map((m) => m.content)
        .join('')
    : ''
  const lastAssistant = messages
    .filter((m) => m.role === 'assistant')
    .map((m) => m.content)
    .join('')

  const handleSubmit = useCallback(() => {
    if (!inputValue.trim()) return
    setState('thinking')
    sendMessage(inputValue.trim()).then(() => {
      if (stateRef.current === 'thinking') setState('streaming')
    })
    setInputValue('')
  }, [inputValue, sendMessage])

  const handlePromptSelect = useCallback((id: string) => {
    const prompt = suggestedPrompts.find((p) => p.id === id)
    if (prompt) {
      setInputValue(prompt.label)
      setState('thinking')
      sendMessage(prompt.label).then(() => {
        if (stateRef.current === 'thinking') setState('streaming')
      })
    }
  }, [sendMessage])

  const handleRefresh = useCallback(() => {
    cancelStream()
    clearMessages()
    setState('open')
  }, [cancelStream, clearMessages])

  const handleClose = useCallback(() => {
    cancelStream()
    clearMessages()
    setState('idle')
    setInputValue('')
  }, [cancelStream, clearMessages])

  const isExpanded = state !== 'idle'

  return (
    <>
      {/* Collapsed button */}
      <AnimatePresence>
        {!isExpanded && (
          <motion.button
            key="dock-button"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0, transition: { duration: 0.15 } }}
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.94 }}
            onClick={() => setState('open')}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            aria-label="Open ARIA AI"
            className={clsx(
              'fixed bottom-6 right-6 z-40',
              'flex items-center justify-center',
              'w-14 h-14 rounded-full',
              'bg-background-elevated border border-border/50',
              'shadow-glow',
              'transition-shadow duration-300',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background-dark',
              className,
            )}
            style={{
              boxShadow: isHovered
                ? '0 0 20px rgba(0,255,163,0.35), 0 4px 24px rgba(0,0,0,0.4)'
                : '0 0 10px rgba(0,255,163,0.2), 0 4px 20px rgba(0,0,0,0.35)',
              border: `1px solid ${isHovered ? 'rgba(0,255,163,0.5)' : 'rgba(70,70,79,0.3)'}`,
            }}
          >
            <Sparkles size={22} style={{ color: 'var(--accent-neon)' }} aria-hidden="true" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Expanded widget */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            key="dock-widget"
            initial={{ opacity: 0, y: 16, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.95, transition: { duration: 0.15 } }}
            transition={{ type: 'spring', stiffness: 350, damping: 25 }}
            className={clsx(
              'fixed bottom-6 right-6 z-40',
              'hidden md:block',
              'w-[340px] rounded-xl overflow-hidden flex flex-col',
              className,
            )}
            style={{
              background: 'rgba(18, 18, 26, 0.96)',
              border: '1px solid rgba(70,70,79,0.25)',
              boxShadow: '0 0 30px rgba(99,102,241,0.2), 0 20px 40px rgba(0,0,0,0.45)',
              backdropFilter: 'blur(16px)',
              WebkitBackdropFilter: 'blur(16px)',
            }}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-4 py-3 shrink-0"
              style={{ borderBottom: '1px solid rgba(70,70,79,0.15)' }}
            >
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Sparkles size={16} style={{ color: 'var(--accent-neon)' }} aria-hidden="true" />
                  {(connectionState === 'connecting' || connectionState === 'streaming') && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full"
                      style={{ backgroundColor: 'var(--accent-neon)' }}
                    />
                  )}
                </div>
                <span className="text-sm font-semibold text-text-primary font-display">ARIA</span>
                {connectionState === 'connecting' && (
                  <span className="text-[11px] font-mono text-accent-neon/80 animate-pulse">
                    {thinkingMessages[0]}
                  </span>
                )}
                {connectionState === 'streaming' && (
                  <span className="text-[11px] font-mono text-accent-neon/60">responding...</span>
                )}
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => router.push('/chat')}
                  className="flex items-center justify-center w-7 h-7 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-elevated/80 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary"
                  aria-label="Open full chat"
                  title="Open full chat"
                >
                  <ExternalLink size={12} aria-hidden="true" />
                </button>
                <button
                  onClick={handleRefresh}
                  className="flex items-center justify-center w-7 h-7 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-elevated/80 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary"
                  aria-label="Refresh"
                >
                  <RefreshCw size={12} aria-hidden="true" />
                </button>
                <button
                  onClick={handleClose}
                  className="flex items-center justify-center w-7 h-7 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-elevated/80 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary"
                  aria-label="Close AI dock"
                >
                  <X size={14} aria-hidden="true" />
                </button>
              </div>
            </div>

            {/* Response area */}
            <div
              className="flex-1 px-4 py-3 min-h-[100px] max-h-[240px] overflow-y-auto scroll-smooth"
              role="log"
              aria-live="polite"
              aria-label="AI response"
            >
              <AnimatePresence mode="wait">
                {connectionState === 'connecting' && !lastAssistant && (
                  <motion.div
                    key="thinking"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <ThinkingIndicator state="thinking" messages={thinkingMessages} />
                  </motion.div>
                )}

                {(isStreaming || lastAssistant) && (
                  <motion.div
                    key="streaming"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-sm leading-relaxed font-body"
                  >
                    <StreamingText text={lastAssistant} isStreaming={isStreaming} speed={20} />
                  </motion.div>
                )}

                {error && (
                  <motion.p
                    key="error"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-sm text-accent-error"
                  >
                    {error}
                  </motion.p>
                )}

                {state === 'open' && !lastAssistant && !error && (
                  <motion.div
                    key="greeting"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="space-y-3"
                  >
                    <p className="text-xs text-text-secondary font-body">How can I help you today?</p>
                    <SuggestionChips suggestions={suggestedPrompts} onSelect={handlePromptSelect} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Input */}
            <div
              className="flex items-center gap-2 px-3 py-3 shrink-0"
              style={{ borderTop: '1px solid rgba(70,70,79,0.15)' }}
            >
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit()
                  }
                }}
                placeholder="Ask ARIA anything..."
                disabled={isStreaming}
                className={clsx(
                  'flex-1 bg-transparent outline-none text-text-primary placeholder:text-text-tertiary/50 text-sm font-body',
                  'min-h-[44px]',
                  'disabled:opacity-40 disabled:cursor-not-allowed',
                )}
                aria-label="Message input"
              />
              <button
                onClick={handleSubmit}
                disabled={!inputValue.trim() || isStreaming}
                className={clsx(
                  'flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary',
                  'disabled:opacity-40 disabled:cursor-not-allowed',
                  inputValue.trim()
                    ? 'text-white'
                    : 'text-text-secondary',
                )}
                style={{
                  backgroundColor: inputValue.trim() ? 'var(--accent-primary)' : 'rgba(70,70,79,0.15)',
                }}
                aria-label="Send message"
              >
                <Send size={12} aria-hidden="true" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export type { AIDockProps }
