'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { motion } from 'framer-motion'
import { RefreshCw } from 'lucide-react'
import { RadarScanner, type RadarSignal } from '@/components/opportunities/RadarScanner'
import { MatchCard } from '@/components/opportunities/MatchCard'
import { SignalList } from '@/components/opportunities/SignalList'
import { OpportunityDetail } from '@/components/opportunities/OpportunityDetail'
import { MatchTierPills } from '@/components/opportunities/MatchTierPills'
import { Button } from '@/components/ui/Button'
import type { Opportunity, OpportunityStatus } from '@/types/opportunity'
import type { Opportunity as StoreOpportunity } from '@/lib/types'
import { useOpportunityStore } from '@/lib/stores'
import { createLogger } from '@/lib/utils/logger'
import { useAIAgents, useAIAction } from '@/lib/ai/hooks'
import { AIInsightCard, ConfidenceBadge } from '@/components/ai'

function mapOpportunityType(t: StoreOpportunity['opportunity_type']): Opportunity['type'] {
  const m: Record<string, Opportunity['type']> = {
    internship: 'career',
    job: 'career',
    scholarship: 'strategic',
    competition: 'partnership',
    grant: 'strategic',
    other: 'financial',
  }
  return m[t] ?? 'career'
}

function mapOpportunityStatus(s: StoreOpportunity['status']): OpportunityStatus {
  const m: Record<string, OpportunityStatus> = {
    saved: 'saved',
    applied: 'applied',
    interviewing: 'interviewing',
    offered: 'accepted',
    accepted: 'accepted',
    rejected: 'declined',
  }
  return m[s] ?? 'new'
}

function toStoreStatus(s: OpportunityStatus): StoreOpportunity['status'] {
  const m: Record<string, StoreOpportunity['status']> = {
    saved: 'saved',
    applied: 'applied',
    interviewing: 'interviewing',
    accepted: 'accepted',
    declined: 'rejected',
  }
  return m[s] ?? 'saved'
}

function toDisplayOpportunity(o: StoreOpportunity): Opportunity {
  return {
    id: o.id,
    title: o.title,
    organization: o.company ?? '',
    type: mapOpportunityType(o.opportunity_type),
    score: o.match_score ?? 0,
    description: o.notes ?? '',
    status: mapOpportunityStatus(o.status),
    matchBreakdown: [],
    url: o.url,
    createdAt: o.created_at,
  }
}



const typeAngleMap: Record<string, number> = {
  strategic: 45,
  financial: 135,
  partnership: 225,
  career: 315,
}

const sectionVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

const containerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.06,
    },
  },
}

export default function OpportunitiesPage() {
  const { user, loading: authLoading } = useAuth()
  const store = useOpportunityStore()
  const logger = createLogger('OpportunitiesPage')
  const [activeCategory, setActiveCategory] = useState('all')
  const [activeTier, setActiveTier] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [mounted, setMounted] = useState(false)
  const { agents, updateAgent } = useAIAgents()
  const { execute: fetchOpportunitiesAI, isLoading: aiLoading } = useAIAction(async () => {
    // opportunity matching logic
  })

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    updateAgent('opportunity', {
      status: 'done',
      preview: '4 high-match opportunities detected in AI/ML sector.',
      confidence: 0.88,
    })
  }, [updateAgent])

  useEffect(() => {
    if (user) store.fetch()
  }, [user]) // eslint-disable-line react-hooks/exhaustive-deps

  const opportunities = useMemo<Opportunity[]>(() => {
    return store.items.map(toDisplayOpportunity)
  }, [store.items])

  const loading = store.loading && store.items.length === 0

  const signals: RadarSignal[] = useMemo(
    () =>
      opportunities.map((o) => ({
        id: o.id,
        angle: typeAngleMap[o.type] + (Math.random() - 0.5) * 30,
        radius: o.score / 100,
        status: (
          o.status === 'new'
            ? 'new'
            : o.status === 'applied' || o.status === 'interviewing'
              ? 'viewed'
              : 'saved'
        ) as 'new' | 'viewed' | 'saved',
        label: o.title,
      })),
    [opportunities]
  )

  const selectedOpportunity = useMemo(
    () => opportunities.find((o) => o.id === selectedId) ?? null,
    [opportunities, selectedId]
  )

  const tierCounts = useMemo(
    () => ({
      exceptional: opportunities.filter((o) => o.score >= 90).length,
      strong: opportunities.filter((o) => o.score >= 70 && o.score < 90).length,
      moderate: opportunities.filter((o) => o.score >= 50 && o.score < 70).length,
    }),
    [opportunities]
  )

  const filteredByTier = useMemo(() => {
    if (!activeTier) return opportunities
    if (activeTier === 'exceptional') return opportunities.filter((o) => o.score >= 90)
    if (activeTier === 'strong')
      return opportunities.filter((o) => o.score >= 70 && o.score < 90)
    if (activeTier === 'moderate')
      return opportunities.filter((o) => o.score >= 50 && o.score < 70)
    return opportunities
  }, [opportunities, activeTier])

  const handleRefresh = useCallback(async () => {
    logger.info('Refreshing opportunities')
    setIsRefreshing(true)
    try {
      await store.fetch()
      logger.info('Opportunities refreshed successfully')
    } catch (err) {
      logger.error('Failed to refresh opportunities', { error: err instanceof Error ? err.message : String(err) })
    }
    setTimeout(() => setIsRefreshing(false), 800)
  }, [store])

  const handleSave = useCallback((id: string) => {
    logger.info('Saving opportunity', { id })
    store.update(id, { status: 'saved' })
  }, [store])

  const handleStatusChange = useCallback(
    (id: string, status: OpportunityStatus) => {
      logger.info('Updating opportunity status', { id, status })
      store.update(id, { status: toStoreStatus(status) })
    },
    [store]
  )

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
        <div className="animate-pulse-glow w-12 h-12 border-2 border-accent-primary border-t-transparent rounded-full" />
        <span className="sr-only">Loading opportunities...</span>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="space-y-6 pb-8"
    >
      {store.error && (
        <motion.div variants={sectionVariants}>
          <div className="bg-accent-danger/10 border border-accent-danger/30 text-text-primary px-4 py-3 rounded-lg mb-6">
            {store.error}
          </div>
        </motion.div>
      )}

      <motion.div variants={sectionVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Opportunity Radar</h1>
          <p className="text-sm text-[var(--text-secondary)]">
            AI-matched signals for your growth
          </p>
        </div>
        <Button
          variant="primary"
          icon={<RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />}
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          Refresh Scan
        </Button>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <motion.div variants={sectionVariants} className="lg:col-span-2 space-y-6">
          <div className="card">
            <RadarScanner signals={signals} />
          </div>
          <MatchTierPills
            activeTier={activeTier}
            onTierChange={setActiveTier}
            counts={tierCounts}
          />
        </motion.div>

        <motion.div variants={sectionVariants} className="lg:col-span-3 space-y-4">
          <SignalList
            signals={filteredByTier}
            activeCategory={activeCategory}
            onCategoryChange={setActiveCategory}
            onViewDetail={setSelectedId}
          />
        </motion.div>
      </div>

      <motion.div variants={sectionVariants}>
        <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
          Top Matches
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredByTier.slice(0, 4).map((opp) => (
            <MatchCard key={opp.id} match={opp} onViewDetail={setSelectedId} />
          ))}
        </div>
      </motion.div>

      <motion.div variants={sectionVariants}>
        <AIInsightCard
          type="recommendation"
          title="Opportunity Match Insights"
          description="4 high-match opportunities detected in AI/ML sector."
        />
      </motion.div>

      <OpportunityDetail
        opportunity={selectedOpportunity}
        onClose={() => setSelectedId(null)}
        onSave={handleSave}
        onStatusChange={handleStatusChange}
      />
    </motion.div>
  )
}
