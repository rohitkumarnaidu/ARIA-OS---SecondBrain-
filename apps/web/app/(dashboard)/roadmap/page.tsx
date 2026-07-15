'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Check, Clock, Target, BookOpen, Code, Database, Cpu, GitBranch, Users, Lightbulb, X, RefreshCw, ChevronDown, Zap, Brain } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { cn } from '@/components/ui/utils'
import { useRoadmapStore } from '@/lib/stores'
import { useAIAgents, useAIAction } from '@/lib/ai/hooks'
import { AIInsightCard, ConfidenceBadge } from '@/components/ai'

type SkillStatus = 'not_started' | 'in_progress' | 'completed' | 'on_hold'
type SkillCategory = 'Frontend' | 'Backend' | 'AI/ML' | 'DSA' | 'System Design' | 'DevOps' | 'Soft Skills'

interface Milestone {
  id: string
  skill: string
  category: SkillCategory
  targetDate: string
  progress: number
  status: SkillStatus
  isRecommended: boolean
}

interface AiSuggestion {
  id: string
  message: string
}

interface SkillInventory {
  name: string
  level: number
  category: SkillCategory
}

const CATEGORIES: SkillCategory[] = ['Frontend', 'Backend', 'AI/ML', 'DSA', 'System Design', 'DevOps', 'Soft Skills']



const STATUS_CONFIG: Record<SkillStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline' }> = {
  not_started: { label: 'Not Started', variant: 'outline' },
  in_progress: { label: 'In Progress', variant: 'info' },
  completed: { label: 'Completed', variant: 'success' },
  on_hold: { label: 'On Hold', variant: 'warning' },
}

function formatDate(dateStr: string): string {
  const [year, month] = dateStr.split('-')
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${months[parseInt(month, 10) - 1]} ${year}`
}

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

const sectionVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
}

export default function RoadmapPage(): JSX.Element {
  const { milestones, loading, error, fetch: fetchMilestones, add, update, remove } = useRoadmapStore()
  const [mounted, setMounted] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})

  const [newSkill, setNewSkill] = useState({ name: '', targetDate: '', category: 'Frontend' as SkillCategory })
  const { agents, updateAgent } = useAIAgents()
  const { execute: fetchRecommendations, isLoading: recsLoading } = useAIAction(async () => {
    // roadmap recommendation logic
  })

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    fetchMilestones()
  }, [fetchMilestones])

  useEffect(() => {
    updateAgent('roadmap', {
      status: 'done',
      preview: 'Focus on System Design and AI/ML to close skill gaps by Q4.',
      confidence: 0.82,
    })
  }, [updateAgent])

  const displayMilestones = milestones

  const handleAddSkill = useCallback(() => {
    if (!newSkill.name.trim() || !newSkill.targetDate) return
    const milestone: Milestone = {
      id: `m-${Date.now()}`,
      skill: newSkill.name.trim(),
      category: newSkill.category,
      targetDate: newSkill.targetDate,
      progress: 0,
      status: 'not_started',
      isRecommended: false,
    }
    add(milestone)
    setNewSkill({ name: '', targetDate: '', category: 'Frontend' })
    setShowAddModal(false)
  }, [newSkill, add])

  const handleDelete = useCallback((id: string) => {
    remove(id)
  }, [remove])

  const handleProgressChange = useCallback((id: string, progress: number) => {
    update(id, { progress: Math.min(100, Math.max(0, progress)) })
  }, [update])

  const handleAcceptSuggestion = useCallback((id: string) => {
    setCollapsed((prev) => ({ ...prev, [id]: true }))
  }, [])

  const handleDismissSuggestion = useCallback((id: string) => {
    setCollapsed((prev) => ({ ...prev, [id]: true }))
  }, [])

  const activeSuggestions = useMemo(() => {
    const derived = displayMilestones.flatMap((m) => {
      const msgs: AiSuggestion[] = []
      if (m.status === 'not_started' || m.progress < 20) {
        msgs.push({ id: `s-${m.id}-1`, message: `Consider prioritizing "${m.skill}" — it's ${m.status === 'not_started' ? 'not yet started' : 'still early in progress'}` })
      }
      if (m.isRecommended && m.progress < 50) {
        msgs.push({ id: `s-${m.id}-2`, message: `"${m.skill}" is recommended — try to allocate more time to it this week` })
      }
      if (m.status === 'completed') {
        msgs.push({ id: `s-${m.id}-3`, message: `Great job completing "${m.skill}"! Consider reviewing related skills.` })
      }
      return msgs
    })
    return derived.filter((s) => !collapsed[s.id])
  }, [displayMilestones, collapsed])

  const sortedMilestones = useMemo(() => {
    return [...displayMilestones].sort((a, b) => {
      const dateA = a.targetDate.replace('-', '')
      const dateB = b.targetDate.replace('-', '')
      return parseInt(dateA, 10) - parseInt(dateB, 10)
    })
  }, [displayMilestones])

  const completedCount = displayMilestones.filter((m) => m.status === 'completed').length
  const inProgressCount = displayMilestones.filter((m) => m.status === 'in_progress').length
  const totalCount = displayMilestones.length

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (loading && !milestones.length) {
    return (
      <div className="space-y-6 pb-8">
        <Skeleton variant="text" className="h-8 w-64" />
        <Skeleton variant="text" className="h-4 w-96" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} variant="card" className="h-24" />
            ))}
          </div>
          <div className="space-y-4">
            <Skeleton variant="card" className="h-48" />
            <Skeleton variant="card" className="h-32" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 pb-8"
    >
      <PageHeader
        title="Your Skill Roadmap"
        description="AI-optimized skill development path to reach your career goals"
        actions={
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            <Plus size={16} />
            Add Skill
          </Button>
        }
      />

      {displayMilestones.length === 0 ? (
        <motion.div variants={sectionVariants}>
          <Card className="py-16">
            <EmptyState
              icon={<Target size={48} />}
              title="No skills on your roadmap yet"
              description="Add your first skill to start tracking your learning journey"
              action={{ label: 'Add Your First Skill', onClick: () => setShowAddModal(true) }}
            />
          </Card>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <motion.div variants={sectionVariants} className="grid grid-cols-3 gap-4">
              <Card className="text-center">
                <CardContent>
                  <div className="text-3xl font-display font-bold text-[var(--accent-primary)]">
                    {totalCount}
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1 font-medium uppercase tracking-wider">
                    Total Skills
                  </div>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent>
                  <div className="text-3xl font-display font-bold text-[var(--accent-success)]">
                    {completedCount}
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1 font-medium uppercase tracking-wider">
                    Completed
                  </div>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent>
                  <div className="text-3xl font-display font-bold text-[var(--accent-info)]">
                    {inProgressCount}
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1 font-medium uppercase tracking-wider">
                    In Progress
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={sectionVariants}>
              <AIInsightCard
                type="recommendation"
                title="Roadmap Recommendations"
                description="Focus on System Design and AI/ML to close skill gaps by Q4."
              />
            </motion.div>

            <motion.div variants={sectionVariants} className="relative">
              <div className="absolute left-[19px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-[var(--accent-primary)] via-[var(--accent-secondary)] to-[var(--accent-primary)] opacity-30" />
              <AnimatePresence mode="popLayout">
                {sortedMilestones.map((milestone, index) => (
                  <motion.div
                    key={milestone.id}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20, height: 0, marginBottom: 0 }}
                    transition={{ delay: index * 0.05, type: 'spring', stiffness: 200, damping: 25 }}
                    className={cn(
                      'relative flex gap-4 pb-6 pl-12',
                      milestone.isRecommended && 'recommended'
                    )}
                  >
                    <div
                      className={cn(
                        'absolute left-[11px] top-1 w-[18px] h-[18px] rounded-full border-2 z-10 flex items-center justify-center bg-[var(--background-dark)]',
                        milestone.status === 'completed'
                          ? 'border-[var(--accent-success)] bg-[var(--accent-success)]'
                          : milestone.isRecommended
                            ? 'border-[var(--accent-primary)] shadow-[var(--shadow-glow-sm)] animate-pulse'
                            : milestone.status === 'in_progress'
                              ? 'border-[var(--accent-info)]'
                              : milestone.status === 'on_hold'
                                ? 'border-[var(--accent-warning)]'
                                : 'border-[var(--border)]'
                      )}
                      aria-label={`${milestone.skill} — ${STATUS_CONFIG[milestone.status].label}`}
                    >
                      {milestone.status === 'completed' && (
                        <Check size={10} className="text-white" />
                      )}
                    </div>

                    <Card
                      variant={milestone.isRecommended ? 'interactive' : 'default'}
                      className={cn(
                        'flex-1',
                        milestone.isRecommended && 'ring-1 ring-[var(--accent-primary)]/40'
                      )}
                    >
                      <div className="flex items-start justify-between gap-4 flex-wrap">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <h3 className="text-base font-semibold text-[var(--text-primary)]">
                              {milestone.skill}
                            </h3>
                            <Badge variant={STATUS_CONFIG[milestone.status].variant}>
                              {STATUS_CONFIG[milestone.status].label}
                            </Badge>
                            {milestone.isRecommended && (
                              <Badge variant="default">
                                <Zap size={10} className="mr-1" />
                                Recommended
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
                            <span className="flex items-center gap-1">
                              <Clock size={12} />
                              {formatDate(milestone.targetDate)}
                            </span>
                            <span className="flex items-center gap-1">
                              <BookOpen size={12} />
                              {milestone.category}
                            </span>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(milestone.id)}
                          aria-label={`Remove ${milestone.skill}`}
                        >
                          <X size={14} />
                        </Button>
                      </div>

                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-xs text-[var(--text-secondary)]">Progress</span>
                          <span className="text-xs font-medium text-[var(--accent-primary)]">
                            {milestone.progress}%
                          </span>
                        </div>
                        <div
                          className="h-2 bg-[var(--background-elevated)] rounded-full overflow-hidden cursor-pointer group/progress relative"
                          role="slider"
                          aria-valuenow={milestone.progress}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label={`${milestone.skill} progress: ${milestone.progress}%`}
                          tabIndex={0}
                          onClick={(e) => {
                            const rect = e.currentTarget.getBoundingClientRect()
                            const x = e.clientX - rect.left
                            const pct = Math.round((x / rect.width) * 100)
                            handleProgressChange(milestone.id, pct)
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'ArrowRight') {
                              handleProgressChange(milestone.id, Math.min(100, milestone.progress + 5))
                            } else if (e.key === 'ArrowLeft') {
                              handleProgressChange(milestone.id, Math.max(0, milestone.progress - 5))
                            }
                          }}
                        >
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${milestone.progress}%` }}
                            transition={{ duration: 0.6, ease: 'easeOut' }}
                            className={cn(
                              'h-full rounded-full',
                              milestone.status === 'completed'
                                ? 'bg-[var(--accent-success)]'
                                : 'bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)]'
                            )}
                          />
                          <div className="absolute inset-0 opacity-0 group-hover/progress:opacity-100 transition-opacity bg-white/5 rounded-full" />
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div variants={sectionVariants}>
              <Card className="bg-[var(--glass-light)] backdrop-blur-xl border-[var(--border)]/60">
                <CardHeader>
                  <CardTitle>
                    <div className="flex items-center gap-2">
                      <Brain size={16} className="text-[var(--accent-primary)]" />
                      <span>AI-Optimized Path</span>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <AnimatePresence mode="popLayout">
                    {activeSuggestions.length > 0 ? (
                      activeSuggestions.map((suggestion) => (
                        <motion.div
                          key={suggestion.id}
                          layout
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                          className="p-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)]"
                        >
                          <div className="flex items-start gap-2">
                            <Lightbulb size={14} className="text-[var(--accent-warning)] mt-0.5 shrink-0" />
                            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                              {suggestion.message}
                            </p>
                          </div>
                          <div className="flex gap-2 mt-2">
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleAcceptSuggestion(suggestion.id)}
                            >
                              <Check size={12} />
                              Accept
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDismissSuggestion(suggestion.id)}
                            >
                              Dismiss
                            </Button>
                          </div>
                        </motion.div>
                      ))
                    ) : (
                      <p className="text-xs text-[var(--text-tertiary)] text-center py-2">
                        All suggestions reviewed
                      </p>
                    )}
                  </AnimatePresence>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={sectionVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>
                    <div className="flex items-center gap-2">
                      <Zap size={16} className="text-[var(--accent-warning)]" />
                      <span>Time Investment</span>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-display font-bold text-[var(--text-primary)]">
                    18
                    <span className="text-sm font-normal text-[var(--text-secondary)] ml-1">hrs/week</span>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mb-4">Recommended weekly breakdown</div>
                  <div className="space-y-2.5">
                    {[
                      { label: 'Frontend', hours: 5, color: 'var(--accent-primary)' },
                      { label: 'Backend', hours: 4, color: 'var(--accent-secondary)' },
                      { label: 'DSA', hours: 3, color: 'var(--accent-warning)' },
                      { label: 'System Design', hours: 3, color: 'var(--accent-info)' },
                      { label: 'AI/ML', hours: 2, color: 'var(--accent-error)' },
                      { label: 'DevOps', hours: 1, color: 'var(--accent-success)' },
                    ].map((item) => (
                      <div key={item.label} className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                        <span className="text-xs text-[var(--text-secondary)] flex-1">{item.label}</span>
                        <span className="text-xs font-medium text-[var(--text-primary)]">{item.hours}h</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={sectionVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>
                    <div className="flex items-center gap-2">
                      <Target size={16} className="text-[var(--accent-secondary)]" />
                      <span>Skills Inventory</span>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
                    {(function deriveSkills() {
                      const skillMap = new Map<string, SkillInventory>()
                      for (const m of displayMilestones) {
                        if (!skillMap.has(m.skill)) {
                          skillMap.set(m.skill, { name: m.skill, level: Math.max(1, Math.ceil(m.progress / 25)) as 1|2|3|4|5, category: m.category as SkillCategory })
                        }
                      }
                      return Array.from(skillMap.values())
                    })().map((skill) => (
                      <div key={skill.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="text-xs text-[var(--text-primary)] truncate">{skill.name}</span>
                          <span className="text-[10px] text-[var(--text-tertiary)] hidden sm:inline">{skill.category}</span>
                        </div>
                        <div className="flex gap-0.5 shrink-0" aria-label={`${skill.name}: ${skill.level} out of 5`}>
                          {Array.from({ length: 5 }).map((_, i) => (
                            <div
                              key={i}
                              className={cn(
                                'w-1.5 h-1.5 rounded-full',
                                i < skill.level ? 'bg-[var(--accent-primary)]' : 'bg-[var(--background-elevated)]'
                              )}
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      )}

      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[var(--z-modal)] p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-skill-title"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="bg-[var(--background-card)] border border-[var(--border)] rounded-2xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 id="add-skill-title" className="text-xl font-display font-semibold text-[var(--text-primary)]">
                  Add Skill to Roadmap
                </h2>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="p-2 hover:bg-[var(--background-elevated)] rounded-lg transition-colors"
                  aria-label="Close dialog"
                >
                  <X size={20} className="text-[var(--text-tertiary)]" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label htmlFor="skill-name" className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                    Skill Name <span className="text-[var(--accent-error)]">*</span>
                  </label>
                  <input
                    id="skill-name"
                    type="text"
                    value={newSkill.name}
                    onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
                    className="w-full h-10 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                    placeholder="e.g., Next.js Advanced"
                    />
                </div>

                <div>
                  <label htmlFor="skill-category" className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                    Category
                  </label>
                  <select
                    id="skill-category"
                    value={newSkill.category}
                    onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value as SkillCategory })}
                    className="w-full h-10 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="skill-target" className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                    Target Month <span className="text-[var(--accent-error)]">*</span>
                  </label>
                  <input
                    id="skill-target"
                    type="month"
                    value={newSkill.targetDate}
                    onChange={(e) => setNewSkill({ ...newSkill, targetDate: e.target.value })}
                    className="w-full h-10 px-3 rounded-lg bg-[var(--background-elevated)] border border-[var(--border)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button variant="outline" onClick={() => setShowAddModal(false)} className="flex-1">
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleAddSkill}
                  disabled={!newSkill.name.trim() || !newSkill.targetDate}
                  className="flex-1"
                >
                  Add to Roadmap
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
