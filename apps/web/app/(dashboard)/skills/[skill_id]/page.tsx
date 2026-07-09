'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  ArrowLeft, Brain, Target, TrendingUp, Award, BookOpen,
  BarChart3, DollarSign, Lightbulb, Activity,
  ExternalLink, Plus, Clock, CheckCircle, Zap, Star,
  LineChart, Compass, FileText, Layers
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Tabs } from '@/components/ui/Tabs'
import type { Tab } from '@/components/ui/Tabs'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkillRadarChart } from '@/components/analytics/SkillRadarChart'
import { useSkillStore } from '@/lib/stores/skillStore'

const LEVEL_LABELS = ['Novice', 'Beginner', 'Intermediate', 'Proficient', 'Advanced', 'Expert']
const STATE_COLORS: Record<string, string> = {
  planned: 'bg-yellow-500/20 text-yellow-400',
  learning: 'bg-blue-500/20 text-blue-400',
  practicing: 'bg-indigo-500/20 text-indigo-400',
  active: 'bg-green-500/20 text-green-400',
  reviewing: 'bg-purple-500/20 text-purple-400',
  archived: 'bg-gray-500/20 text-gray-400',
}

export default function SkillDetailPage() {
  const params = useParams()
  const router = useRouter()
  const skillId = params.skill_id as string

  const {
    skills, userSkills, evidence, targets, assessments, marketData,
    income, certifications, topics, resources, learningPaths,
    recommendations, activity, externalMappings, forecasts,
    loading, fetchSkills, fetchUserSkills, fetchEvidence, fetchTargets,
    fetchAssessments, fetchMarketData, fetchIncome, fetchCertifications,
    fetchTopics, fetchResources, fetchLearningPaths, fetchRecommendations,
    fetchActivity, fetchExternalMappings, fetchForecasts,
    addEvidence, addTarget, addAssessment, acceptRecommendation,
  } = useSkillStore()

  const skill = skills.find(s => s.skill_id === skillId)
  const userSkill = userSkills.find(us => us.skill_id === skillId)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchSkills()
    fetchUserSkills()
    fetchEvidence()
    fetchTargets()
    fetchAssessments()
    fetchMarketData()
    fetchIncome()
    fetchCertifications()
    fetchTopics()
    fetchResources()
    fetchLearningPaths()
    fetchRecommendations()
    fetchActivity()
    fetchExternalMappings()
    fetchForecasts()
  }, [])

  const skillEvidence = evidence.filter(e => e.user_skill_id === userSkill?.user_skill_id)
  const skillTargets = targets.filter(t => t.user_skill_id === userSkill?.user_skill_id)
  const skillAssessments = assessments.filter(a => a.user_skill_id === userSkill?.user_skill_id)
  const skillMarket = marketData.filter(m => m.skill_id === skillId)
  const skillIncome = income.filter(i => i.skill_id === skillId)
  const skillCerts = certifications.filter(c => c.skill_id === skillId)
  const skillTopics = topics.filter(t => t.skill_id === skillId)
  const skillResources = resources.filter(r => r.skill_id === skillId)
  const skillPaths = learningPaths.filter(p => p.target_skill_id === skillId)
  const skillRecs = recommendations.filter(r => r.user_skill_id === userSkill?.user_skill_id || !r.user_skill_id)
  const skillActivity = activity.filter(a => a.user_skill_id === userSkill?.user_skill_id || !a.user_skill_id)
  const skillMappings = externalMappings.filter(m => m.skill_id === skillId)
  const skillForecasts = forecasts.filter(f => f.skill_id === skillId)

  if (loading && !skill) {
    return (
      <div className="min-h-screen bg-background-page p-8 max-w-7xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!skill) {
    return (
      <div className="min-h-screen bg-background-page p-8">
        <EmptyState icon={<Brain size={24} />} title="Skill not found" description="This skill does not exist or has been removed" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <PageHeader
          title={skill.name}
          description={skill.description}
          breadcrumb={[{ label: 'Skills', href: '/skills' }, { label: skill.name }]}
          actions={
            <div className="flex gap-2">
              {userSkill && (
                <Badge className={STATE_COLORS[userSkill.state] || ''}>
                  {userSkill.state}
                </Badge>
              )}
              <Button variant="ghost" onClick={() => router.push('/skills')}>
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
              </Button>
            </div>
          }
        />

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <Card className="text-center p-4">
            <Brain className="w-5 h-5 text-accent-primary mx-auto mb-2" />
            <div className="text-2xl font-bold">{userSkill ? LEVEL_LABELS[userSkill.level] : '-'}</div>
            <div className="text-xs text-text-secondary">Current Level</div>
          </Card>
          <Card className="text-center p-4">
            <Target className="w-5 h-5 text-accent-neon mx-auto mb-2" />
            <div className="text-2xl font-bold">{skillTargets.length > 0 ? `${skillTargets[0].target_level}` : '-'}</div>
            <div className="text-xs text-text-secondary">Target Level</div>
          </Card>
          <Card className="text-center p-4">
            <Zap className="w-5 h-5 text-accent-warning mx-auto mb-2" />
            <div className="text-2xl font-bold">{userSkill?.confidence_score ?? '-'}</div>
            <div className="text-xs text-text-secondary">Confidence</div>
          </Card>
          <Card className="text-center p-4">
            <TrendingUp className="w-5 h-5 text-accent-secondary mx-auto mb-2" />
            <div className="text-2xl font-bold">{skillMarket[0]?.demand_trend ?? '-'}</div>
            <div className="text-xs text-text-secondary">Market Demand</div>
          </Card>
        </div>

        <Tabs
          tabs={[
            { value: 'overview', label: 'Overview' },
            { value: 'evidence', label: 'Evidence' },
            { value: 'market', label: 'Market' },
            { value: 'learning', label: 'Learning' },
            { value: 'forecasts', label: 'Forecasts' },
            { value: 'activity', label: 'Activity' },
          ]}
          value={activeTab}
          onChange={setActiveTab}
        />

          {activeTab === 'overview' && <div className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Target className="w-4 h-4 text-accent-primary" />
                    Targets & Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillTargets.length === 0 ? (
                    <EmptyState icon={<Target size={24} />} title="No targets" description="Set a skill target to track progress" />
                  ) : (
                    <div className="space-y-3">
                      {skillTargets.map(t => (
                        <div key={t.target_id} className="flex items-center justify-between p-3 rounded-lg bg-background-card">
                          <div>
                            <div className="text-sm font-medium">Level {t.target_level}</div>
                            <div className="text-xs text-text-secondary">
                              Due: {new Date(t.target_date).toLocaleDateString()}
                            </div>
                          </div>
                          <Badge variant={t.status === 'achieved' ? 'success' : t.status === 'missed' ? 'error' : 'outline'}>
                            {t.status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Award className="w-4 h-4 text-accent-neon" />
                    Certifications
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillCerts.length === 0 ? (
                    <EmptyState icon={<Award size={24} />} title="No certifications" description="Add certifications for this skill" />
                  ) : (
                    <div className="space-y-3">
                      {skillCerts.map(c => (
                        <div key={c.certification_id} className="flex items-center justify-between p-3 rounded-lg bg-background-card">
                          <div>
                            <div className="text-sm font-medium">{c.name}</div>
                            <div className="text-xs text-text-secondary">{c.issuer}</div>
                          </div>
                          {c.is_verified && <CheckCircle className="w-4 h-4 text-accent-neon" />}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Layers className="w-4 h-4 text-accent-primary" />
                    Topics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillTopics.length === 0 ? (
                    <EmptyState icon={<Layers size={24} />} title="No topics" description="No subtopics defined for this skill" />
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {skillTopics.map(t => (
                        <Badge key={t.topic_id} variant="outline">{t.name}</Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <ExternalLink className="w-4 h-4 text-accent-secondary" />
                    External Mappings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillMappings.length === 0 ? (
                    <EmptyState icon={<ExternalLink size={24} />} title="No mappings" description="No external system mappings" />
                  ) : (
                    <div className="space-y-2">
                      {skillMappings.map(m => (
                        <div key={m.mapping_id} className="flex items-center justify-between p-2 rounded bg-background-card">
                          <div>
                            <span className="text-sm font-medium">{m.external_name}</span>
                            <span className="text-xs text-text-secondary ml-2">({m.external_system})</span>
                          </div>
                          {m.external_url && (
                            <a href={m.external_url} target="_blank" rel="noreferrer" className="text-accent-primary hover:underline text-xs">
                              Open <ExternalLink className="w-3 h-3 inline" />
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Lightbulb className="w-4 h-4 text-accent-warning" />
                  AI Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                {skillRecs.length === 0 ? (
                  <EmptyState icon={<Lightbulb size={24} />} title="No recommendations" description="AI recommendations will appear here" />
                ) : (
                  <div className="space-y-3">
                    {skillRecs.map(r => (
                      <div key={r.recommendation_id} className="flex items-start justify-between p-3 rounded-lg bg-background-card">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{r.title}</span>
                            <Badge variant="outline">{r.recommendation_type}</Badge>
                          </div>
                          <p className="text-xs text-text-secondary mt-1">{r.description}</p>
                        </div>
                        {!r.is_accepted && (
                          <Button size="sm" variant="ghost" onClick={() => acceptRecommendation(r.recommendation_id)}>
                            <CheckCircle className="w-3 h-3 mr-1" /> Accept
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>}

          {activeTab === 'evidence' && <div className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <FileText className="w-4 h-4 text-accent-primary" />
                  Evidence Log
                </CardTitle>
              </CardHeader>
              <CardContent>
                {skillEvidence.length === 0 ? (
                  <EmptyState icon={<FileText size={24} />} title="No evidence" description="Log evidence of skill application" />
                ) : (
                  <div className="space-y-3">
                    {skillEvidence.map(e => (
                      <div key={e.evidence_id} className="flex items-start justify-between p-3 rounded-lg bg-background-card">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{e.title}</span>
                            <Badge variant="outline">{e.evidence_type}</Badge>
                          </div>
                          <p className="text-xs text-text-secondary mt-1">{e.description}</p>
                          {e.source_url && (
                            <a href={e.source_url} target="_blank" rel="noreferrer" className="text-xs text-accent-primary hover:underline mt-1 inline-block">
                              View source
                            </a>
                          )}
                        </div>
                        <div className="text-right text-xs text-text-secondary">
                          <div>{new Date(e.occurred_at).toLocaleDateString()}</div>
                          <div className={e.confidence_delta >= 0 ? 'text-accent-neon' : 'text-accent-danger'}>
                            {e.confidence_delta >= 0 ? '+' : ''}{e.confidence_delta}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>}

          {activeTab === 'market' && <div className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <TrendingUp className="w-4 h-4 text-accent-primary" />
                    Market Data
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillMarket.length === 0 ? (
                    <EmptyState icon={<TrendingUp size={24} />} title="No market data" description="Market intelligence will appear here" />
                  ) : (
                    <div className="space-y-4">
                      {skillMarket.map(m => (
                        <div key={m.skill_id} className="space-y-3">
                          <div className="grid grid-cols-2 gap-3">
                            <div className="p-3 rounded-lg bg-background-card text-center">
                              <div className="text-sm text-text-secondary">Salary Range</div>
                              <div className="text-lg font-bold text-accent-neon">
                                ${m.salary_range_min?.toLocaleString() ?? '-'} - ${m.salary_range_max?.toLocaleString() ?? '-'}
                              </div>
                            </div>
                            <div className="p-3 rounded-lg bg-background-card text-center">
                              <div className="text-sm text-text-secondary">Growth Rate</div>
                              <div className="text-lg font-bold text-accent-primary">{m.growth_rate ?? '-'}%</div>
                            </div>
                          </div>
                          <div className="p-3 rounded-lg bg-background-card text-center">
                            <div className="text-sm text-text-secondary">Job Postings</div>
                            <div className="text-lg font-bold text-accent-secondary">{m.job_posting_count?.toLocaleString() ?? '-'}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <DollarSign className="w-4 h-4 text-accent-neon" />
                    Income Data
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillIncome.length === 0 ? (
                    <EmptyState icon={<DollarSign size={24} />} title="No income data" description="Track income generated from this skill" />
                  ) : (
                    <div className="space-y-3">
                      {skillIncome.map(i => (
                        <div key={i.income_id} className="flex items-center justify-between p-3 rounded-lg bg-background-card">
                          <div>
                            <div className="text-sm font-medium">{i.project_name ?? 'Income'}</div>
                            <div className="text-xs text-text-secondary">{new Date(i.income_date).toLocaleDateString()}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-accent-neon">
                              {i.currency} {i.amount.toLocaleString()}
                            </div>
                            {i.hourly_rate && <div className="text-xs text-text-secondary">${i.hourly_rate}/hr</div>}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>}

          {activeTab === 'learning' && <div className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <BookOpen className="w-4 h-4 text-accent-primary" />
                    Learning Paths
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillPaths.length === 0 ? (
                    <EmptyState icon={<BookOpen size={24} />} title="No learning paths" description="Create a learning path for this skill" />
                  ) : (
                    <div className="space-y-3">
                      {skillPaths.map(p => (
                        <div key={p.path_id} className="p-3 rounded-lg bg-background-card">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{p.name}</span>
                            <Badge variant="outline">{p.difficulty}</Badge>
                          </div>
                          <p className="text-xs text-text-secondary mt-1">{p.description}</p>
                          <div className="text-xs text-text-secondary mt-2">
                            <Clock className="w-3 h-3 inline mr-1" />{p.estimated_days} days
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Star className="w-4 h-4 text-accent-warning" />
                    Resources
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {skillResources.length === 0 ? (
                    <EmptyState icon={<Star size={24} />} title="No resources" description="Add learning resources for this skill" />
                  ) : (
                    <div className="space-y-3">
                      {skillResources.map(r => (
                        <div key={r.resource_id} className="flex items-center justify-between p-3 rounded-lg bg-background-card">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium">{r.title}</span>
                              <Badge variant="outline">{r.resource_type}</Badge>
                            </div>
                            {r.rating && (
                              <div className="flex items-center gap-1 mt-1">
                                {Array.from({ length: 5 }).map((_, i) => (
                                  <Star key={i} className={`w-3 h-3 ${i < Math.round(r.rating!) ? 'text-accent-warning' : 'text-gray-600'}`} />
                                ))}
                              </div>
                            )}
                          </div>
                          {r.url && (
                            <a href={r.url} target="_blank" rel="noreferrer" className="text-accent-primary hover:underline text-xs">
                              Open
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>}

          {activeTab === 'forecasts' && <div className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <LineChart className="w-4 h-4 text-accent-primary" />
                  Skill Forecasts
                </CardTitle>
              </CardHeader>
              <CardContent>
                {skillForecasts.length === 0 ? (
                  <EmptyState icon={<LineChart size={24} />} title="No forecasts" description="AI-generated forecasts will appear here" />
                ) : (
                  <div className="space-y-3">
                    {skillForecasts.map(f => (
                      <div key={f.forecast_id} className="flex items-center justify-between p-3 rounded-lg bg-background-card">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{f.metric}</span>
                            <Badge variant="outline">{f.model_name}</Badge>
                          </div>
                          <div className="text-xs text-text-secondary">
                            {new Date(f.forecast_date).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-accent-primary">{f.predicted_value}</div>
                          {f.confidence_interval_lower != null && (
                            <div className="text-xs text-text-secondary">
                              CI: [{f.confidence_interval_lower}, {f.confidence_interval_upper}]
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>}

          {activeTab === 'activity' && <div className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Activity className="w-4 h-4 text-accent-primary" />
                  Activity Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                {skillActivity.length === 0 ? (
                  <EmptyState icon={<Activity size={24} />} title="No activity" description="Activity logs will appear here" />
                ) : (
                  <div className="space-y-3">
                    {skillActivity.map(a => (
                      <div key={a.activity_id} className="flex items-start gap-3 p-3 rounded-lg bg-background-card">
                        <div className="w-2 h-2 mt-2 rounded-full bg-accent-primary flex-shrink-0" />
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{a.description}</span>
                            <Badge variant="outline">{a.activity_type}</Badge>
                          </div>
                          <div className="text-xs text-text-secondary mt-1">
                            {new Date(a.created_at).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>}
      </div>
    </div>
  )
}
