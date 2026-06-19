'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Play, Pause, RotateCw, Sparkles, RefreshCw, Code2,
  FileText, Lightbulb, X, Clock, Hash, BookOpen, Timer, Target,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/components/ui/utils'
import { FocusTimer } from './FocusTimer'
import { FocusCompletion } from './FocusCompletion'
import type { FocusSessionStatus, FocusPhase } from '@/types/focus'

const MAX_CYCLES = 4
const DEFAULT_WORK_MINUTES = 25
const DEFAULT_BREAK_MINUTES = 5

interface ExitModalState {
  open: boolean
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}

export function FocusMode(): JSX.Element {
  const router = useRouter()

  const [status, setStatus] = useState<FocusSessionStatus>('idle')
  const [phase, setPhase] = useState<FocusPhase>('work')
  const [workMinutes, setWorkMinutes] = useState(DEFAULT_WORK_MINUTES)
  const [breakMinutes] = useState(DEFAULT_BREAK_MINUTES)
  const [objective, setObjective] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [remainingSeconds, setRemainingSeconds] = useState(DEFAULT_WORK_MINUTES * 60)
  const [cyclesCompleted, setCyclesCompleted] = useState(0)
  const [workDescription, setWorkDescription] = useState('')
  const [workTitle, setWorkTitle] = useState('')
  const [showExitModal, setShowExitModal] = useState(false)
  const [showCompletion, setShowCompletion] = useState(false)
  const [sessionStartTime] = useState<number>(Date.now())
  const [aiSuggestion, setAiSuggestion] = useState<string | null>(null)
  const [aiInput, setAiInput] = useState('')
  const [lineCount, setLineCount] = useState(1)

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lineNumbersRef = useRef<HTMLDivElement>(null)
  const tagInputRef = useRef<HTMLInputElement>(null)

  const sessionDuration = Math.floor((Date.now() - sessionStartTime) / 1000)

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const startTimer = useCallback(() => {
    if (intervalRef.current) return
    intervalRef.current = setInterval(() => {
      setRemainingSeconds((prev) => {
        const next = prev - 1
        if (next <= 0) {
          clearTimer()
          setStatus('completed')
          return 0
        }
        return next
      })
    }, 1000)
  }, [clearTimer])

  const handleStart = useCallback(() => {
    if (status === 'idle' || status === 'paused') {
      setStatus('running')
      startTimer()
    }
  }, [status, startTimer])

  const handlePause = useCallback(() => {
    if (status === 'running') {
      clearTimer()
      setStatus('paused')
    }
  }, [status, clearTimer])

  const handleReset = useCallback(() => {
    clearTimer()
    const target = phase === 'work' ? workMinutes * 60 : breakMinutes * 60
    setRemainingSeconds(target)
    setStatus('paused')
  }, [phase, workMinutes, breakMinutes, clearTimer])

  const handleInitiateExit = useCallback(() => {
    clearTimer()
    setShowExitModal(true)
  }, [clearTimer])

  const handleConfirmExit = useCallback(() => {
    setShowExitModal(false)
    clearTimer()
    setTimeout(() => router.back(), 300)
  }, [clearTimer, router])

  const handleResumeExit = useCallback(() => {
    setShowExitModal(false)
    if (status === 'paused' || status === 'idle') {
      setStatus('running')
      startTimer()
    } else if (status === 'running') {
      startTimer()
    }
  }, [status, startTimer])

  const handleCompleteCycle = useCallback(() => {
    const nextCycles = cyclesCompleted + 1
    setCyclesCompleted(nextCycles)

    if (nextCycles >= MAX_CYCLES) {
      clearTimer()
      setStatus('completed')
      setShowCompletion(true)
      return
    }

    if (phase === 'work') {
      setPhase('break')
      setRemainingSeconds(breakMinutes * 60)
    } else {
      setPhase('work')
      setRemainingSeconds(workMinutes * 60)
    }

    if (status === 'running') {
      startTimer()
    }
  }, [phase, cyclesCompleted, workMinutes, breakMinutes, status, startTimer, clearTimer])

  useEffect(() => {
    if (status === 'completed' && remainingSeconds <= 0) {
      handleCompleteCycle()
    }
  }, [status, remainingSeconds, handleCompleteCycle])

  useEffect(() => {
    return () => clearTimer()
  }, [clearTimer])

  const handleTagAdd = useCallback(() => {
    const trimmed = tagInput.trim()
    if (trimmed && !tags.includes(trimmed)) {
      setTags((prev) => [...prev, trimmed])
      setTagInput('')
    }
    if (tagInputRef.current) tagInputRef.current.focus()
  }, [tagInput, tags])

  const handleTagKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault()
        handleTagAdd()
      }
    },
    [handleTagAdd],
  )

  const handleRemoveTag = useCallback((tag: string) => {
    setTags((prev) => prev.filter((t) => t !== tag))
  }, [])

  const handleTextareaChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setWorkDescription(e.target.value)
      const lines = e.target.value.split('\n').length
      setLineCount(Math.max(1, lines))
    },
    [],
  )

  const handleTextareaScroll = useCallback(() => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop
    }
  }, [])

  const handleResetSession = useCallback(() => {
    clearTimer()
    setStatus('idle')
    setPhase('work')
    setRemainingSeconds(workMinutes * 60)
    setCyclesCompleted(0)
    setShowCompletion(false)
    setWorkTitle('')
    setWorkDescription('')
    setAiSuggestion(null)
    setAiInput('')
  }, [workMinutes, clearTimer])

  const handleReviewSession = useCallback(() => {
    setShowCompletion(false)
  }, [])

  const handleAiAction = useCallback((action: string): void => {
    setAiSuggestion(`AI ${action} suggestion for "${workTitle || 'your work'}" will appear here.`)
  }, [workTitle])

  const handleAiSend = useCallback((): void => {
    if (aiInput.trim()) {
      setAiSuggestion(`AI: "${aiInput}" — Processing your request...`)
      setAiInput('')
    }
  }, [aiInput])

  const minutePresets = [15, 25, 30, 45, 60]

  const totalElapsedSeconds = workMinutes * 60 - remainingSeconds

  return (
    <div className="fixed inset-0 z-50 flex flex-col overflow-hidden bg-[var(--background)]">
      <motion.div
        className="pointer-events-none absolute inset-0"
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        aria-hidden="true"
      >
        <div
          className="absolute -inset-40"
          style={{
            background:
              'radial-gradient(ellipse 60% 50% at 50% 30%, var(--accent-primary) 0%, transparent 70%)',
            filter: 'blur(100px)',
            opacity: 0.25,
          }}
        />
        <div
          className="absolute -inset-40"
          style={{
            background:
              'radial-gradient(ellipse 40% 40% at 70% 70%, var(--accent-secondary) 0%, transparent 60%)',
            filter: 'blur(100px)',
            opacity: 0.15,
          }}
        />
      </motion.div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 flex flex-1 flex-col"
      >
        <motion.header
          variants={itemVariants}
          className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4"
        >
          <div className="flex items-center gap-4">
            <h1 className="font-display text-xl font-semibold text-[var(--text-primary)]">
              Deep Focus
            </h1>
            <Badge
              variant="success"
              className={cn(
                'transition-all duration-300',
                status === 'running' && 'animate-pulse-glow',
              )}
            >
              {status === 'idle' && 'Ready'}
              {status === 'running' && phase === 'work' && 'Focus Protocol Active'}
              {status === 'running' && phase === 'break' && 'Break Time'}
              {status === 'paused' && 'Paused'}
              {status === 'completed' && 'Complete'}
            </Badge>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleInitiateExit}
            aria-label="Exit focus mode"
          >
            <X size={16} />
            Exit Mode
          </Button>
        </motion.header>

        <div className="flex flex-1 flex-col overflow-hidden lg:flex-row">
          <motion.aside
            variants={itemVariants}
            className="flex w-full flex-col gap-4 border-r border-[var(--border)] p-5 lg:w-72"
          >
            <div>
              <label
                htmlFor="focus-objective"
                className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]"
              >
                <Target size={14} className="mr-1.5 inline-block text-[var(--accent-primary)]" />
                Objective
              </label>
              <input
                id="focus-objective"
                type="text"
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                placeholder="What do you want to accomplish?"
                className={cn(
                  'w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-3 py-2',
                  'text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]',
                  'focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]/30',
                  'transition-colors duration-200',
                )}
                disabled={status === 'running'}
              />
            </div>

            <div>
              <label className="mb-1.5 flex items-center gap-1.5 text-sm font-medium text-[var(--text-secondary)]">
                <Hash size={14} className="text-[var(--accent-primary)]" />
                Tags
              </label>
              <div className="mb-2 flex flex-wrap gap-1.5">
                {tags.map((tag) => (
                  <Badge key={tag} variant="info" className="gap-1 pr-1">
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-0.5 rounded-full p-0.5 text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
                      aria-label={`Remove tag ${tag}`}
                    >
                      <X size={10} />
                    </button>
                  </Badge>
                ))}
              </div>
              <div className="flex gap-1">
                <input
                  ref={tagInputRef}
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  placeholder="Add tag..."
                  className={cn(
                    'flex-1 rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-3 py-1.5',
                    'text-xs text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]',
                    'focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]/30',
                    'transition-colors duration-200',
                  )}
                  disabled={status === 'running'}
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleTagAdd}
                  disabled={!tagInput.trim() || status === 'running'}
                  aria-label="Add tag"
                >
                  +
                </Button>
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-[var(--text-secondary)]">
                <Timer size={14} className="mr-1.5 inline-block text-[var(--accent-primary)]" />
                Session Duration
              </label>
              <div className="flex flex-wrap gap-1.5">
                {minutePresets.map((m) => (
                  <button
                    key={m}
                    onClick={() => {
                      if (status === 'idle') {
                        setWorkMinutes(m)
                        setRemainingSeconds(m * 60)
                      }
                    }}
                    disabled={status !== 'idle'}
                    className={cn(
                      'rounded-lg border px-2.5 py-1 text-xs font-medium transition-all duration-200',
                      workMinutes === m && status === 'idle'
                        ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]'
                        : 'border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--text-tertiary)]',
                      status !== 'idle' && 'cursor-not-allowed opacity-50',
                    )}
                    aria-label={`Set session to ${m} minutes`}
                  >
                    {m}m
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface-primary)] p-5">
              <FocusTimer
                remainingSeconds={remainingSeconds}
                status={status}
                phase={phase}
              />

              {phase === 'break' && (
                <span className="rounded-full bg-[var(--accent-success)]/10 px-3 py-0.5 text-xs font-medium text-[var(--accent-success)]">
                  Break — {breakMinutes} min
                </span>
              )}

              <div className="flex items-center gap-2">
                {(status === 'idle' || status === 'paused') && (
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={handleStart}
                    icon={<Play size={20} />}
                    aria-label={status === 'idle' ? 'Start focus session' : 'Resume session'}
                  >
                    {status === 'idle' ? 'Start' : 'Resume'}
                  </Button>
                )}
                {status === 'running' && (
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={handlePause}
                    icon={<Pause size={20} />}
                    aria-label="Pause session"
                  >
                    Pause
                  </Button>
                )}
                {status !== 'idle' && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleReset}
                    aria-label="Reset timer"
                  >
                    <RotateCw size={18} />
                  </Button>
                )}
              </div>

              <div className="flex items-center gap-1.5 text-xs text-[var(--text-tertiary)]">
                <Clock size={12} />
                Cycle {cyclesCompleted + 1} of {MAX_CYCLES}
                <div className="ml-1 flex items-center gap-1">
                  {Array.from({ length: MAX_CYCLES }).map((_, i) => (
                    <span
                      key={i}
                      className={cn(
                        'size-1.5 rounded-full transition-colors duration-300',
                        i < cyclesCompleted
                          ? 'bg-[var(--accent-success)]'
                          : i === cyclesCompleted
                            ? 'bg-[var(--accent-primary)]'
                            : 'bg-[var(--surface-tertiary)]',
                      )}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] p-3">
              <div className="flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)]">
                <BookOpen size={14} />
                Linked Resources
              </div>
              <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                Connect tasks from your task list to track deeper.
              </p>
            </div>
          </motion.aside>

          <motion.main
            variants={itemVariants}
            className="flex flex-1 flex-col overflow-hidden"
          >
            <div className="flex flex-col gap-3 p-5">
              <label
                htmlFor="work-title"
                className="text-xs font-medium uppercase tracking-wider text-[var(--text-tertiary)]"
              >
                What are you working on?
              </label>
              <input
                id="work-title"
                type="text"
                value={workTitle}
                onChange={(e) => setWorkTitle(e.target.value)}
                placeholder="e.g. Implement authentication middleware"
                className={cn(
                  'w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5',
                  'text-base text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]',
                  'focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]/30',
                  'transition-colors duration-200',
                )}
              />
            </div>

            <div className="flex flex-1 overflow-hidden border-t border-[var(--border)]">
              <div
                ref={lineNumbersRef}
                className="w-10 flex-shrink-0 select-none overflow-hidden border-r border-[var(--border)] bg-[var(--surface-primary)] py-3 text-right"
                aria-hidden="true"
              >
                {Array.from({ length: lineCount }).map((_, i) => (
                  <div
                    key={i}
                    className="px-2 leading-6 text-[var(--text-tertiary)] font-mono text-xs"
                  >
                    {i + 1}
                  </div>
                ))}
              </div>

              <textarea
                ref={textareaRef}
                value={workDescription}
                onChange={handleTextareaChange}
                onScroll={handleTextareaScroll}
                placeholder="Start writing your thoughts, code, or notes here..."
                className={cn(
                  'flex-1 resize-none border-0 bg-[var(--background)] p-3',
                  'font-mono text-sm leading-6 text-[var(--text-primary)]',
                  'placeholder:text-[var(--text-tertiary)] placeholder:font-body',
                  'focus:outline-none focus:ring-0',
                  'scrollbar-thin scrollbar-thumb-[var(--surface-secondary)]',
                )}
                spellCheck={false}
                aria-label="Work editor content"
              />
            </div>
          </motion.main>

          <motion.aside
            variants={itemVariants}
            className="flex w-full flex-col border-l border-[var(--border)] bg-[var(--surface-primary)] lg:w-72"
          >
            <div className="flex items-center gap-2 border-b border-[var(--border)] px-4 py-3">
              <Sparkles size={16} className="text-[var(--accent-primary)]" />
              <h2 className="text-sm font-semibold text-[var(--text-primary)]">AI Copilot</h2>
            </div>

            <div className="flex flex-col gap-1.5 p-3">
              <Button
                variant="ghost"
                size="sm"
                className="justify-start gap-3 text-left"
                icon={<RefreshCw size={15} />}
                onClick={() => handleAiAction('Regenerate')}
              >
                Regenerate
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="justify-start gap-3 text-left"
                icon={<Code2 size={15} />}
                onClick={() => handleAiAction('Refactor')}
              >
                Refactor
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="justify-start gap-3 text-left"
                icon={<FileText size={15} />}
                onClick={() => handleAiAction('Document')}
              >
                Document
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="justify-start gap-3 text-left"
                icon={<Lightbulb size={15} />}
                onClick={() => handleAiAction('Explain')}
              >
                Explain
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto border-t border-[var(--border)] p-3">
              <AnimatePresence mode="wait">
                {aiSuggestion ? (
                  <motion.div
                    key={aiSuggestion}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 text-xs text-[var(--text-secondary)] leading-relaxed"
                  >
                    {aiSuggestion}
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-2"
                  >
                    {[1, 2, 3].map((i) => (
                      <motion.div
                        key={i}
                        className="h-14 animate-pulse rounded-lg bg-[var(--surface-tertiary)]/50"
                        style={{ animationDelay: `${i * 150}ms` }}
                      />
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="border-t border-[var(--border)] p-3">
              <div className="relative">
                <input
                  type="text"
                  value={aiInput}
                  onChange={(e) => setAiInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleAiSend()
                  }}
                  placeholder="Ask AI anything..."
                  className={cn(
                    'w-full rounded-lg border border-[var(--border)] bg-[var(--background)] py-2 pl-3 pr-8',
                    'text-xs text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]',
                    'focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]/30',
                    'transition-colors duration-200',
                  )}
                  aria-label="Ask AI anything"
                />
                <button
                  onClick={handleAiSend}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors"
                  aria-label="Send AI request"
                >
                  <Sparkles size={14} />
                </button>
              </div>
            </div>
          </motion.aside>
        </div>
      </motion.div>

      <AnimatePresence>
        {showExitModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[70] flex items-center justify-center p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="exit-modal-title"
          >
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={handleResumeExit}
              aria-hidden="true"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className={cn(
                'relative w-full max-w-sm rounded-2xl border border-[var(--border)] p-6',
                'bg-[var(--glass-heavy)] backdrop-blur-2xl',
                'shadow-[var(--shadow-glow)]',
              )}
            >
              <h2
                id="exit-modal-title"
                className="mb-1 font-display text-lg font-semibold text-[var(--text-primary)]"
              >
                End Session?
              </h2>
              <p className="mb-5 text-sm text-[var(--text-secondary)]">
                Your session is in progress. Here&rsquo;s what you&rsquo;ve done:
              </p>

              <div className="mb-6 space-y-2">
                <div className="flex items-center justify-between rounded-lg bg-[var(--surface-secondary)]/50 px-3 py-2 text-sm">
                  <span className="text-[var(--text-secondary)]">Duration</span>
                  <span className="font-medium text-[var(--text-primary)]">
                    {Math.floor(sessionDuration / 60)}m {sessionDuration % 60}s
                  </span>
                </div>
                <div className="flex items-center justify-between rounded-lg bg-[var(--surface-secondary)]/50 px-3 py-2 text-sm">
                  <span className="text-[var(--text-secondary)]">Cycles</span>
                  <span className="font-medium text-[var(--text-primary)]">
                    {cyclesCompleted} / {MAX_CYCLES}
                  </span>
                </div>
                {objective && (
                  <div className="flex items-center justify-between rounded-lg bg-[var(--surface-secondary)]/50 px-3 py-2 text-sm">
                    <span className="text-[var(--text-secondary)]">Objective</span>
                    <span className="max-w-[180px] truncate font-medium text-[var(--text-primary)]">
                      {objective}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={handleResumeExit}
                >
                  Resume
                </Button>
                <Button
                  variant="ghost"
                  className="flex-1 text-[var(--accent-error)]"
                  onClick={handleConfirmExit}
                >
                  End Session
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showCompletion && (
          <FocusCompletion
            totalSeconds={
              cyclesCompleted * workMinutes * 60 +
              totalElapsedSeconds
            }
            cyclesCompleted={cyclesCompleted}
            objective={objective}
            onStartAnother={handleResetSession}
            onReviewSession={handleReviewSession}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
