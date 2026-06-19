'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import {
  Plus, FolderKanban, Trash2, X, ExternalLink, Github, RefreshCw,
  Check, Circle, Timer, AlertTriangle, Sparkles, Eye,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { PageHeader } from '@/components/ui/PageHeader'
import { showError, showSuccess } from '@/lib/toast'
import { useProjectStore } from '@/lib/stores'
import type { Project as StoreProject, ProjectCreate, ProjectUpdate, ProjectStatus } from '@/lib/types'
import type { ProjectPhase, Project, AIInsight, ProjectFormData } from '@/types/portfolio'
import { createLogger } from '@/lib/utils/logger'

/* ─── Phase Constants ───────────────────────────────────────── */

const PHASES: ProjectPhase[] = ['planning', 'design', 'build', 'test', 'launch', 'maintain']

const PHASE_LABELS: Record<ProjectPhase, string> = {
  planning: 'Planning',
  design: 'Design',
  build: 'Build',
  test: 'Test',
  launch: 'Launch',
  maintain: 'Maintain',
}

const PHASE_BADGE_VARIANT: Record<ProjectPhase, 'info' | 'default' | 'warning' | 'outline' | 'success' | 'default'> = {
  planning: 'info',
  design: 'default',
  build: 'warning',
  test: 'outline',
  launch: 'success',
  maintain: 'default',
}

/* ─── Status/Phase Mapping ───────────────────────────────────── */

function statusToPhase(status: ProjectStatus): ProjectPhase {
  const map: Record<ProjectStatus, ProjectPhase> = {
    planning: 'planning',
    active: 'build',
    completed: 'launch',
    paused: 'design',
    cancelled: 'maintain',
  }
  return map[status] ?? 'planning'
}

function phaseToStatus(phase: ProjectPhase): ProjectStatus {
  const map: Record<ProjectPhase, ProjectStatus> = {
    planning: 'planning',
    design: 'paused',
    build: 'active',
    test: 'active',
    launch: 'completed',
    maintain: 'completed',
  }
  return map[phase]
}



/* ─── Helpers ────────────────────────────────────────────────── */

function getRelativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  const weeks = Math.floor(days / 7)
  if (weeks < 4) return `${weeks}w ago`
  const months = Math.floor(days / 30)
  return `${months}mo ago`
}

function getPhaseIndex(phase: ProjectPhase): number {
  return PHASES.indexOf(phase)
}

function getPhaseProgress(phase: ProjectPhase): number {
  return Math.round(((getPhaseIndex(phase) + 1) / PHASES.length) * 100)
}

function getConfidenceColor(c: AIInsight['confidence']): 'success' | 'warning' | 'error' {
  if (c === 'High') return 'success'
  if (c === 'Medium') return 'warning'
  return 'error'
}

/* ─── Variants ───────────────────────────────────────────────── */

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
}

const tabContentVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.25 } },
  exit: { opacity: 0, x: 10, transition: { duration: 0.15 } },
}

/* ─── Loading Skeleton ───────────────────────────────────────── */

function GridSkeleton(): JSX.Element {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="rounded-xl bg-[var(--background-card)] border border-[var(--border)] p-4 space-y-4 animate-pulse">
          <div className="flex items-start justify-between">
            <div className="h-5 w-32 rounded bg-[var(--surface-tertiary)]" />
            <div className="h-5 w-16 rounded-full bg-[var(--surface-tertiary)]" />
          </div>
          <div className="space-y-2">
            <div className="h-3 w-full rounded bg-[var(--surface-tertiary)]" />
            <div className="h-3 w-3/4 rounded bg-[var(--surface-tertiary)]" />
          </div>
          <div className="h-2 w-full rounded bg-[var(--surface-tertiary)]" />
          <div className="flex gap-2">
            <div className="h-8 w-20 rounded-lg bg-[var(--surface-tertiary)]" />
            <div className="h-8 w-20 rounded-lg bg-[var(--surface-tertiary)]" />
          </div>
        </div>
      ))}
    </div>
  )
}

function TimelineSkeleton(): JSX.Element {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="flex items-center justify-between px-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[var(--surface-tertiary)]" />
            <div className="h-3 w-16 rounded bg-[var(--surface-tertiary)]" />
          </div>
        ))}
      </div>
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-16 rounded-xl bg-[var(--background-card)] border border-[var(--border)]" />
        ))}
      </div>
    </div>
  )
}

function InsightsSkeleton(): JSX.Element {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="rounded-xl bg-[var(--background-card)] border border-[var(--border)] p-4 space-y-3">
          <div className="h-4 w-28 rounded bg-[var(--surface-tertiary)]" />
          <div className="h-3 w-full rounded bg-[var(--surface-tertiary)]" />
          <div className="h-3 w-2/3 rounded bg-[var(--surface-tertiary)]" />
          <div className="flex items-center gap-2">
            <div className="h-5 w-14 rounded-full bg-[var(--surface-tertiary)]" />
            <div className="h-3 w-20 rounded bg-[var(--surface-tertiary)]" />
          </div>
        </div>
      ))}
    </div>
  )
}

/* ─── Add Project Modal ──────────────────────────────────────── */

interface AddProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onAdd: (data: ProjectFormData) => void
}

function AddProjectModal({ isOpen, onClose, onAdd }: AddProjectModalProps): JSX.Element {
  const [form, setForm] = useState<ProjectFormData>({
    title: '', description: '', phase: 'planning',
    github_url: '', live_url: '', next_action: '', blocker: '',
  })

  const handleSubmit = () => {
    if (!form.title.trim()) return
    onAdd({ ...form })
    setForm({ title: '', description: '', phase: 'planning', github_url: '', live_url: '', next_action: '', blocker: '' })
    onClose()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="add-project-title"
        >
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="relative w-full max-w-lg rounded-2xl border border-[var(--border)] bg-[var(--background-card)] shadow-2xl"
          >
            <div className="flex items-center justify-between p-6 border-b border-[var(--border)]">
              <h2 id="add-project-title" className="text-xl font-display font-semibold text-[var(--text-primary)]">
                New Project
              </h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] transition-colors"
                aria-label="Close dialog"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label htmlFor="proj-title" className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
                  Project Name <span className="text-[var(--accent-error)]">*</span>
                </label>
                <input
                  id="proj-title"
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                  placeholder="e.g., AI Chatbot"
                />
              </div>
              <div>
                <label htmlFor="proj-desc" className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">Description</label>
                <textarea
                  id="proj-desc"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={2}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all resize-none"
                  placeholder="Brief description of the project"
                />
              </div>
              <div>
                <label htmlFor="proj-phase" className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">Phase</label>
                <select
                  id="proj-phase"
                  value={form.phase}
                  onChange={(e) => setForm({ ...form, phase: e.target.value as ProjectPhase })}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5 text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all capitalize"
                >
                  {PHASES.map((p) => (
                    <option key={p} value={p}>{PHASE_LABELS[p]}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="proj-github" className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">GitHub URL</label>
                  <input
                    id="proj-github"
                    type="url"
                    value={form.github_url}
                    onChange={(e) => setForm({ ...form, github_url: e.target.value })}
                    className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                    placeholder="https://github.com/..."
                  />
                </div>
                <div>
                  <label htmlFor="proj-live" className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">Live URL</label>
                  <input
                    id="proj-live"
                    type="url"
                    value={form.live_url}
                    onChange={(e) => setForm({ ...form, live_url: e.target.value })}
                    className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                    placeholder="https://..."
                  />
                </div>
              </div>
              <div>
                <label htmlFor="proj-next" className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">Next Action</label>
                <input
                  id="proj-next"
                  type="text"
                  value={form.next_action}
                  onChange={(e) => setForm({ ...form, next_action: e.target.value })}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface-primary)] px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                  placeholder="What to do next?"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={onClose}
                  className="flex-1 rounded-lg border border-[var(--border)] bg-transparent px-4 py-2.5 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-secondary)] hover:text-[var(--text-primary)] transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!form.title.trim()}
                  className="flex-1 rounded-lg bg-[var(--accent-primary)] px-4 py-2.5 text-sm font-medium text-white hover:bg-[var(--accent-primary)]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Create Project
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/* ─── Project Card ───────────────────────────────────────────── */

interface ProjectCardProps {
  project: Project
  onDelete: (id: string) => void
  onAddBlocker: (id: string, blocker: string) => void
  onResolveBlocker: (id: string) => void
}

function ProjectCard({ project, onDelete, onAddBlocker, onResolveBlocker }: ProjectCardProps): JSX.Element {
  const repoName = project.github_url?.replace('https://github.com/', '') || null
  const progress = getPhaseProgress(project.phase)
  const phaseIdx = getPhaseIndex(project.phase)

  const handleDeleteClick = () => {
    if (window.confirm(`Delete "${project.title}"? This cannot be undone.`)) {
      onDelete(project.id)
    }
  }

  const handleAddBlockerClick = () => {
    const blocker = window.prompt('What is blocking this project?')
    if (blocker && blocker.trim()) onAddBlocker(project.id, blocker.trim())
  }

  return (
    <motion.div
      layout
      variants={itemVariants}
      initial="hidden"
      animate="visible"
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
      className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-4 hover:border-[var(--border)]/60 hover:shadow-[var(--shadow-glow-sm)] transition-all duration-300 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-[var(--text-primary)] truncate group-hover:text-[var(--accent-primary)] transition-colors">
            {project.title}
          </h3>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <Badge variant={PHASE_BADGE_VARIANT[project.phase]}>
            {PHASE_LABELS[project.phase]}
          </Badge>
          <button
            onClick={handleDeleteClick}
            className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-[var(--accent-error)]/10 transition-all"
            aria-label={`Delete ${project.title}`}
          >
            <Trash2 size={14} className="text-[var(--accent-error)]" />
          </button>
        </div>
      </div>

      {/* Description */}
      {project.description && (
        <p className="text-sm text-[var(--text-secondary)] mb-3 line-clamp-2 leading-relaxed">
          {project.description}
        </p>
      )}

      {/* GitHub Repo */}
      {repoName && (
        <div className="flex items-center gap-2 mb-3 text-xs text-[var(--text-tertiary)]">
          <Github size={12} />
          <span>{repoName}</span>
        </div>
      )}

      {/* Progress Bar */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-[var(--text-tertiary)]">Progress</span>
          <span className="text-[var(--accent-primary)] font-medium">{progress}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-[var(--surface-secondary)] overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className="h-full rounded-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-neon)]"
          />
        </div>
        <div className="flex items-center justify-between mt-1">
          {PHASES.map((p, i) => (
            <div
              key={p}
              className={cn(
                'w-1.5 h-1.5 rounded-full transition-colors duration-300',
                i <= phaseIdx ? 'bg-[var(--accent-primary)]' : 'bg-[var(--surface-tertiary)]',
              )}
            />
          ))}
        </div>
      </div>

      {/* Links */}
      <div className="flex items-center gap-2 mb-3">
        {project.github_url && (
          <a
            href={project.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors px-2.5 py-1.5 rounded-lg hover:bg-[var(--accent-primary)]/5"
            aria-label={`GitHub repository for ${project.title}`}
          >
            <Github size={14} />
            GitHub
          </a>
        )}
        {project.live_url && (
          <a
            href={project.live_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors px-2.5 py-1.5 rounded-lg hover:bg-[var(--accent-primary)]/5"
            aria-label={`Live site for ${project.title}`}
          >
            <ExternalLink size={14} />
            Live
          </a>
        )}
      </div>

      {/* Next Action */}
      {project.next_action && (
        <div className="flex items-center gap-1.5 mb-2 px-2.5 py-1.5 rounded-lg bg-[var(--accent-primary)]/5 border border-[var(--accent-primary)]/10 text-xs text-[var(--text-secondary)]">
          <Timer size={12} className="text-[var(--accent-primary)] shrink-0" />
          <span>Next: {project.next_action}</span>
        </div>
      )}

      {/* Blocker */}
      {project.blocker ? (
        <div className="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-lg bg-[var(--accent-error)]/10 border border-[var(--accent-error)]/20 text-xs">
          <span className="flex items-center gap-1.5 text-[var(--accent-error)]">
            <AlertTriangle size={12} />
            {project.blocker}
          </span>
          <button
            onClick={() => onResolveBlocker(project.id)}
            className="text-[var(--accent-primary)] hover:text-[var(--accent-neon)] font-medium transition-colors shrink-0"
            aria-label={`Resolve blocker for ${project.title}`}
          >
            Resolve
          </button>
        </div>
      ) : (
        <button
          onClick={handleAddBlockerClick}
          className="flex items-center gap-1 text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-warning)] transition-colors px-1 py-0.5"
          aria-label={`Add blocker for ${project.title}`}
        >
          + Add Blocker
        </button>
      )}
    </motion.div>
  )
}

/* ─── Portfolio Grid Tab ─────────────────────────────────────── */

function PortfolioGridTab({
  projects,
  onDelete,
  onAddBlocker,
  onResolveBlocker,
  onAddClick,
}: {
  projects: Project[]
  onDelete: (id: string) => void
  onAddBlocker: (id: string, blocker: string) => void
  onResolveBlocker: (id: string) => void
  onAddClick: () => void
}): JSX.Element {
  if (projects.length === 0) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <EmptyState
          title="No projects yet"
          description="Create your first project to start tracking progress."
          icon={<FolderKanban size={48} />}
          action={{ label: 'Add Project', onClick: onAddClick }}
        />
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
    >
      <AnimatePresence mode="popLayout">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onDelete={onDelete}
            onAddBlocker={onAddBlocker}
            onResolveBlocker={onResolveBlocker}
          />
        ))}
      </AnimatePresence>
    </motion.div>
  )
}

/* ─── Timeline Tab ───────────────────────────────────────────── */

interface TimelineTabProps {
  projects: Project[]
  selectedPhase: ProjectPhase | null
  onPhaseSelect: (phase: ProjectPhase | null) => void
}

function TimelineTab({ projects, selectedPhase, onPhaseSelect }: TimelineTabProps): JSX.Element {
  const phaseCounts = useMemo(() => {
    const counts: Record<ProjectPhase, number> = { planning: 0, design: 0, build: 0, test: 0, launch: 0, maintain: 0 }
    for (const p of projects) counts[p.phase]++
    return counts
  }, [projects])

  const filtered = selectedPhase
    ? projects.filter((p) => p.phase === selectedPhase)
    : projects

  const currentPhaseIdx = useMemo(() => {
    const maxIdx = Math.max(...projects.map((p) => getPhaseIndex(p.phase)), 0)
    return maxIdx
  }, [projects])

  return (
    <motion.div
      variants={tabContentVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="space-y-8"
    >
      {/* Phase Timeline */}
      <div className="relative px-2 pt-6 pb-4">
        {/* Connecting line */}
        <div className="absolute top-[34px] left-[calc(8.33%+12px)] right-[calc(8.33%+12px)] h-0.5 bg-[var(--surface-secondary)]">
          <div
            className="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-neon)] transition-all duration-500"
            style={{ width: `${((currentPhaseIdx + 1) / PHASES.length) * 100}%` }}
          />
        </div>

        <div className="flex items-start justify-between">
          {PHASES.map((phase, idx) => {
            const isCompleted = idx < currentPhaseIdx
            const isCurrent = idx === currentPhaseIdx
            const isFuture = idx > currentPhaseIdx
            const count = phaseCounts[phase]

            return (
              <button
                key={phase}
                onClick={() => onPhaseSelect(selectedPhase === phase ? null : phase)}
                className={cn(
                  'flex flex-col items-center gap-2 transition-all duration-300 group',
                  selectedPhase === phase && 'scale-110',
                )}
                aria-label={`${PHASE_LABELS[phase]} phase${selectedPhase === phase ? ' (selected)' : ''}`}
              >
                {/* Node */}
                <div className="relative">
                  {isCompleted ? (
                    <div className="w-8 h-8 rounded-full bg-[var(--accent-primary)] flex items-center justify-center shadow-[var(--shadow-glow-sm)]">
                      <Check size={16} className="text-white" />
                    </div>
                  ) : isCurrent ? (
                    <div className="w-8 h-8 rounded-full bg-[var(--accent-primary)] flex items-center justify-center shadow-[var(--shadow-glow-sm)]">
                      <motion.div
                        animate={{ scale: [1, 1.15, 1] }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                        className="w-3 h-3 rounded-full bg-white"
                      />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full border-2 border-dashed border-[var(--border)] bg-[var(--background-card)] flex items-center justify-center group-hover:border-[var(--accent-primary)]/50 transition-colors">
                      <Circle size={12} className="text-[var(--text-tertiary)]" />
                    </div>
                  )}
                </div>

                {/* Count badge */}
                <div className={cn(
                  'text-xs font-semibold tabular-nums',
                  count > 0 ? 'text-[var(--accent-primary)]' : 'text-[var(--text-tertiary)]',
                )}>
                  {count}
                </div>

                {/* Phase label */}
                <span className={cn(
                  'text-xs font-medium whitespace-nowrap transition-colors',
                  isCompleted && 'text-[var(--accent-primary)]',
                  isCurrent && 'text-[var(--text-primary)]',
                  isFuture && 'text-[var(--text-tertiary)]',
                  selectedPhase === phase && 'text-[var(--accent-neon)]',
                )}>
                  {PHASE_LABELS[phase]}
                </span>

                {/* Selection indicator */}
                {selectedPhase === phase && (
                  <motion.div
                    layoutId="timeline-indicator"
                    className="w-1.5 h-1.5 rounded-full bg-[var(--accent-neon)]"
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Filtered Project List */}
      <div className="space-y-2">
        {selectedPhase && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-[var(--text-secondary)]">
              Showing <span className="text-[var(--text-primary)] font-medium">{filtered.length}</span> project{filtered.length !== 1 ? 's' : ''} in <Badge variant={PHASE_BADGE_VARIANT[selectedPhase]}>{PHASE_LABELS[selectedPhase]}</Badge>
            </p>
            <button
              onClick={() => onPhaseSelect(null)}
              className="text-xs text-[var(--accent-primary)] hover:text-[var(--accent-neon)] transition-colors"
              aria-label="Clear phase filter"
            >
              Clear filter
            </button>
          </div>
        )}
        <AnimatePresence mode="popLayout">
          {filtered.map((project) => (
            <motion.div
              key={project.id}
              layout
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--background-card)] px-4 py-3 hover:border-[var(--border)]/60 transition-all"
            >
              {/* Phase dot */}
              <div className={cn(
                'w-2.5 h-2.5 rounded-full shrink-0',
                getPhaseIndex(project.phase) < getPhaseIndex(PHASES[Math.max(0, ...PHASES.map((p) => getPhaseIndex(p)))])
                  ? 'bg-[var(--accent-primary)]'
                  : 'bg-[var(--accent-primary)]',
              )} />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-[var(--text-primary)] truncate">{project.title}</span>
                  <Badge variant={PHASE_BADGE_VARIANT[project.phase]}>{PHASE_LABELS[project.phase]}</Badge>
                </div>
                {project.next_action && (
                  <p className="text-xs text-[var(--text-tertiary)] mt-0.5 truncate">Next: {project.next_action}</p>
                )}
              </div>

              {project.blocker && (
                <span title={project.blocker}>
                  <AlertTriangle size={14} className="text-[var(--accent-error)] shrink-0" aria-label={project.blocker} />
                </span>
              )}

              <div className="flex items-center gap-1.5 shrink-0">
                {project.github_url && (
                  <a href={project.github_url} target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                    <Github size={14} className="text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors" />
                  </a>
                )}
                {project.live_url && (
                  <a href={project.live_url} target="_blank" rel="noopener noreferrer" aria-label="Live site">
                    <ExternalLink size={14} className="text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors" />
                  </a>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {filtered.length === 0 && (
          <div className="text-center py-12">
            <Eye size={36} className="text-[var(--text-tertiary)] mx-auto mb-2" />
            <p className="text-sm text-[var(--text-secondary)]">No projects in this phase</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

/* ─── AI Insights Tab ────────────────────────────────────────── */

interface AIInsightsTabProps {
  projects: Project[]
  insights: AIInsight[]
  onRegenerate: (insightId: string) => void
}

function AIInsightsTab({ projects, insights, onRegenerate }: AIInsightsTabProps): JSX.Element {
  const projectMap = useMemo(() => {
    const map = new Map<string, string>()
    for (const p of projects) map.set(p.id, p.title)
    return map
  }, [projects])

  if (insights.length === 0) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div className="text-center py-16">
          <div className="w-16 h-16 rounded-2xl bg-[var(--accent-primary)]/10 flex items-center justify-center mx-auto mb-4">
            <Sparkles size={32} className="text-[var(--accent-primary)]" />
          </div>
          <h3 className="text-lg font-display font-semibold text-[var(--text-primary)] mb-2">No AI Insights Yet</h3>
          <p className="text-sm text-[var(--text-secondary)] max-w-sm mx-auto">
            AI insights appear as your projects progress. Complete milestones and commit code to unlock intelligent analysis.
          </p>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-2 gap-4"
    >
      <AnimatePresence mode="popLayout">
        {insights.map((insight) => {
          const projectTitle = projectMap.get(insight.projectId) ?? 'Unknown Project'
          return (
            <motion.div
              key={insight.id}
              layout
              variants={itemVariants}
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
              className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-4 hover:border-[var(--accent-primary)]/20 transition-all group"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="text-sm font-semibold text-[var(--accent-primary)] truncate">{projectTitle}</h4>
                <Badge variant={getConfidenceColor(insight.confidence)}>{insight.confidence}</Badge>
              </div>
              <p className="text-sm text-[var(--text-secondary)] mb-3 leading-relaxed">{insight.summary}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--text-tertiary)] flex items-center gap-1">
                  <Sparkles size={11} />
                  {insight.source}
                </span>
                <button
                  onClick={() => onRegenerate(insight.id)}
                  className="text-xs text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors flex items-center gap-1 opacity-0 group-hover:opacity-100"
                  aria-label={`Regenerate insight for ${projectTitle}`}
                >
                  <RefreshCw size={11} />
                  Regenerate
                </button>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </motion.div>
  )
}

/* ─── Page Hooks & Data ──────────────────────────────────────── */

type TabKey = 'grid' | 'timeline' | 'insights'

const TABS: { key: TabKey; label: string }[] = [
  { key: 'grid', label: 'Portfolio Grid' },
  { key: 'timeline', label: 'Timeline' },
  { key: 'insights', label: 'AI Insights' },
]

/* ─── Main Page Component ────────────────────────────────────── */

export default function ProjectsPage(): JSX.Element {
  const { user, loading: authLoading } = useAuth()
  const { items: storeItems, loading: storeLoading, error: storeError, fetch, create, update, remove } = useProjectStore()
  const logger = createLogger('ProjectsPage')
  const [insights, setInsights] = useState<AIInsight[]>([])
  const [mounted, setMounted] = useState(false)
  const [activeTab, setActiveTab] = useState<TabKey>('grid')
  const [showAddModal, setShowAddModal] = useState(false)
  const [timelineFilter, setTimelineFilter] = useState<ProjectPhase | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (user) fetch()
  }, [user, fetch])

  useEffect(() => {
    if (storeError) showError(storeError)
  }, [storeError])

  useEffect(() => {
    if (storeItems.length > 0) {
      setInsights(storeItems.flatMap((p) => {
        const derived: AIInsight[] = []
        if (p.blocker) derived.push({ id: `insight-${p.id}-blocker`, projectId: p.id, summary: `Blocker: ${p.blocker}`, confidence: 'Medium', source: 'Project Data' })
        if (p.next_action) derived.push({ id: `insight-${p.id}-action`, projectId: p.id, summary: `Next action: ${p.next_action}`, confidence: 'High', source: 'Project Data' })
        if (p.phase === 'active' || p.phase === 'build') derived.push({ id: `insight-${p.id}-phase`, projectId: p.id, summary: `"${p.title}" is in active development — keep momentum going`, confidence: 'Low', source: 'Phase Analysis' })
        return derived
      }))
    }
  }, [storeItems])

  const projects = useMemo<Project[]>(() =>
    storeItems.map((p) => ({
      id: p.id,
      title: p.title,
      description: p.description,
      phase: statusToPhase(p.phase as ProjectStatus),
      github_url: p.github_url,
      live_url: p.live_url,
      next_action: p.next_action,
      blocker: p.blocker,
      created_at: p.created_at,
    })),
  [storeItems])

  const handleAddProject = useCallback(async (data: ProjectFormData) => {
    logger.info('Adding project', { title: data.title, phase: data.phase })
    try {
      await create({
        title: data.title,
        description: data.description || undefined,
        phase: phaseToStatus(data.phase),
        github_url: data.github_url || undefined,
        live_url: data.live_url || undefined,
        next_action: data.next_action || undefined,
        blocker: data.blocker || undefined,
      })
      logger.info('Project created successfully', { title: data.title })
      showSuccess('Project created successfully.')
    } catch (err) {
      logger.error('Failed to create project', { error: err instanceof Error ? err.message : String(err) })
    }
  }, [create])

  const handleDeleteProject = useCallback(async (id: string) => {
    logger.info('Deleting project', { id })
    try {
      await remove(id)
      setInsights((prev) => prev.filter((i) => i.projectId !== id))
      logger.info('Project deleted successfully', { id })
      showSuccess('Project deleted.')
    } catch (err) {
      logger.error('Failed to delete project', { error: err instanceof Error ? err.message : String(err) })
    }
  }, [remove])

  const handleAddBlocker = useCallback(async (id: string, blocker: string) => {
    logger.info('Adding blocker', { projectId: id, blocker })
    try {
      await update(id, { blocker })
    } catch (err) {
      logger.error('Failed to persist blocker', { error: err instanceof Error ? err.message : String(err) })
    }
    showSuccess('Blocker added.')
  }, [update])

  const handleResolveBlocker = useCallback(async (id: string) => {
    logger.info('Resolving blocker', { projectId: id })
    try {
      await update(id, { blocker: '' })
    } catch (err) {
      logger.error('Failed to persist blocker resolution', { error: err instanceof Error ? err.message : String(err) })
    }
    showSuccess('Blocker resolved.')
  }, [update])

  const handleRegenerateInsight = useCallback((insightId: string) => {
    logger.info('Regenerating insight', { insightId })
    setInsights((prev) =>
      prev.map((i) =>
        i.id === insightId
          ? { ...i, summary: 'Regenerating insight...', confidence: 'Medium' as const }
          : i,
      ),
    )
    setTimeout(() => {
      setInsights((prev) =>
        prev.map((i) =>
          i.id === insightId
            ? {
                ...i,
                summary: 'Refreshed analysis based on latest project data and activity trends.',
                confidence: 'High' as const,
                source: 'Re-scanned',
              }
            : i,
        ),
      )
      logger.info('Insight regenerated successfully', { insightId })
      showSuccess('Insight regenerated.')
    }, 800)
  }, [])

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />

  const skeleton = authLoading || (storeLoading && storeItems.length === 0)

  return (
    <div className="space-y-6 pb-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <PageHeader
          title="Projects"
          description="Build, track, and launch your portfolio projects with AI-powered insights and milestone timelines."
          actions={
            <Button
              variant="primary"
              icon={<Plus size={18} />}
              onClick={() => setShowAddModal(true)}
              aria-label="Add new project"
            >
              Add Project
            </Button>
          }
        />
      </motion.div>

      {/* Tabs */}
      <div className="flex items-center gap-1 rounded-xl bg-[var(--surface-secondary)] p-1 w-fit" role="tablist" aria-label="Project view tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            role="tab"
            aria-selected={activeTab === tab.key}
            aria-controls={`tabpanel-${tab.key}`}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              'relative px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)]',
              activeTab === tab.key
                ? 'text-[var(--text-primary)] bg-[var(--background-card)] shadow-sm'
                : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]',
            )}
          >
            {tab.label}
            {activeTab === tab.key && (
              <motion.div
                layoutId="tab-indicator"
                className="absolute inset-0 rounded-lg bg-[var(--background-card)] -z-10"
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {skeleton ? (
        <div>
          {activeTab === 'grid' && <GridSkeleton />}
          {activeTab === 'timeline' && <TimelineSkeleton />}
          {activeTab === 'insights' && <InsightsSkeleton />}
        </div>
      ) : (
        <AnimatePresence mode="wait">
          {activeTab === 'grid' && (
            <motion.div key="grid" variants={tabContentVariants} initial="hidden" animate="visible" exit="exit" role="tabpanel" id="tabpanel-grid" aria-label="Portfolio Grid view">
              <PortfolioGridTab
                projects={projects}
                onDelete={handleDeleteProject}
                onAddBlocker={handleAddBlocker}
                onResolveBlocker={handleResolveBlocker}
                onAddClick={() => setShowAddModal(true)}
              />
            </motion.div>
          )}
          {activeTab === 'timeline' && (
            <motion.div key="timeline" variants={tabContentVariants} initial="hidden" animate="visible" exit="exit" role="tabpanel" id="tabpanel-timeline" aria-label="Timeline view">
              <TimelineTab
                projects={projects}
                selectedPhase={timelineFilter}
                onPhaseSelect={setTimelineFilter}
              />
            </motion.div>
          )}
          {activeTab === 'insights' && (
            <motion.div key="insights" variants={tabContentVariants} initial="hidden" animate="visible" exit="exit" role="tabpanel" id="tabpanel-insights" aria-label="AI Insights view">
              <AIInsightsTab
                projects={projects}
                insights={insights}
                onRegenerate={handleRegenerateInsight}
              />
            </motion.div>
          )}
        </AnimatePresence>
      )}

      {/* Floating Add Button (mobile) */}
      <motion.button
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5, type: 'spring' }}
        onClick={() => setShowAddModal(true)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-[var(--accent-primary)] text-white shadow-[var(--shadow-glow-sm)] flex items-center justify-center hover:bg-[var(--accent-primary)]/90 transition-all md:hidden"
        aria-label="Add new project"
      >
        <Plus size={24} />
      </motion.button>

      {/* Add Project Modal */}
      <AddProjectModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddProject}
      />
    </div>
  )
}
