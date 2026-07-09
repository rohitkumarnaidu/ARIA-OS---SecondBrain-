'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, Search, BookOpen, Brain, Target, TrendingUp, Award, BarChart3, Lightbulb, X } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkillRadarChart } from '@/components/analytics/SkillRadarChart'
import { useSkillStore, Skill, SkillCategory, UserSkill } from '@/lib/stores/skillStore'

const LEVEL_LABELS = ['L0: Novice', 'L1: Beginner', 'L2: Intermediate', 'L3: Proficient', 'L4: Advanced', 'L5: Expert']
const STATE_COLORS: Record<string, string> = {
  planned: 'bg-yellow-500/20 text-yellow-400',
  learning: 'bg-blue-500/20 text-blue-400',
  practicing: 'bg-indigo-500/20 text-indigo-400',
  active: 'bg-green-500/20 text-green-400',
  reviewing: 'bg-purple-500/20 text-purple-400',
  archived: 'bg-gray-500/20 text-gray-400',
}

export default function SkillsPage() {
  const { categories, skills, userSkills, loading, fetchCategories, fetchSkills, fetchUserSkills, addUserSkill, deleteUserSkill } = useSkillStore()
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedSkillId, setSelectedSkillId] = useState<string | null>(null)

  useEffect(() => { fetchCategories(); fetchUserSkills() }, [])

  useEffect(() => { fetchSkills(selectedCategory ?? undefined) }, [selectedCategory])

  const filteredSkills = skills.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) && !s.is_deprecated
  )

  const userSkillMap = new Map(userSkills.map(us => [us.skill_id, us]))
  const activeUserSkills = userSkills.filter(us => us.state !== 'archived' && us.state !== 'deprecated')

  const handleAddSkill = async (skillId: string) => {
    await addUserSkill({ skill_id: skillId, level: 0, state: 'planned' })
    setShowAddModal(false)
  }

  const radarData = activeUserSkills.map(us => {
    const skill = skills.find(s => s.skill_id === us.skill_id)
    return { skill: skill?.name ?? us.skill_id, value: us.level, fullMark: 5 }
  })

  return (
    <div className="min-h-screen bg-background-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Skills"
          description="Track, assess, and grow your skill portfolio with AI-powered intelligence"
          actions={
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="w-4 h-4 mr-2" /> Add Skill
            </Button>
          }
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-accent-primary" />
                Skill Inventory
              </CardTitle>
              <div className="flex gap-3 mt-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                  <Input
                    placeholder="Search skills..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <select
                  value={selectedCategory ?? ''}
                  onChange={e => setSelectedCategory(e.target.value || null)}
                  className="input w-48"
                >
                  <option value="">All Categories</option>
                  {categories.map(c => (
                    <option key={c.category_id} value={c.category_id}>{c.name}</option>
                  ))}
                </select>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">{[1,2,3,4,5].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>
              ) : filteredSkills.length === 0 ? (
                <EmptyState icon={<BookOpen size={24} />} title="No skills found" description="Try a different search or add new skills" />
              ) : (
                <div className="space-y-2">
                  {filteredSkills.map((skill, i) => {
                    const us = userSkillMap.get(skill.skill_id)
                    return (
                      <motion.div
                        key={skill.skill_id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.03 }}
                        className="flex items-center justify-between p-3 rounded-lg bg-background-card hover:bg-background-card-hover transition-colors cursor-pointer border border-border-default"
                        onClick={() => setSelectedSkillId(selectedSkillId === skill.skill_id ? null : skill.skill_id)}
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-text-primary">{skill.name}</span>
                            {us && <Badge variant="outline">{LEVEL_LABELS[us.level]}</Badge>}
                            {skill.skill_health && (
                              <span className="text-xs text-text-secondary">
                                Health: {skill.skill_health.toFixed(1)}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-text-secondary truncate max-w-md">{skill.description}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          {us ? (
                            <Badge className={STATE_COLORS[us.state] || ''}>{us.state}</Badge>
                          ) : (
                            <Button size="sm" variant="ghost" onClick={e => { e.stopPropagation(); handleAddSkill(skill.skill_id) }}>
                              <Plus className="w-3 h-3" />
                            </Button>
                          )}
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <BarChart3 className="w-4 h-4 text-accent-primary" />
                  Skill Radar
                </CardTitle>
              </CardHeader>
              <CardContent>
                {radarData.length > 0 ? (
                  <SkillRadarChart data={radarData} />
                ) : (
                  <p className="text-text-secondary text-sm text-center py-8">Add skills to see your radar chart</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Target className="w-4 h-4 text-accent-primary" />
                  Stats
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 rounded-lg bg-background-card">
                    <div className="text-2xl font-bold text-accent-primary">{activeUserSkills.length}</div>
                    <div className="text-xs text-text-secondary">Active Skills</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-background-card">
                    <div className="text-2xl font-bold text-accent-neon">
                      {activeUserSkills.length > 0
                        ? (activeUserSkills.reduce((s, us) => s + us.level, 0) / activeUserSkills.length).toFixed(1)
                        : '-'}
                    </div>
                    <div className="text-xs text-text-secondary">Avg Level</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-background-card">
                    <div className="text-2xl font-bold text-accent-secondary">{skills.length}</div>
                    <div className="text-xs text-text-secondary">Available</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-background-card">
                    <div className="text-2xl font-bold text-accent-warning">{categories.length}</div>
                    <div className="text-xs text-text-secondary">Categories</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowAddModal(false)}>
          <Card className="w-full max-w-lg mx-4" onClick={e => e.stopPropagation()}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Add Skill</CardTitle>
                <button onClick={() => setShowAddModal(false)} className="text-text-secondary hover:text-text-primary">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <Input placeholder="Search skills..." value={search} onChange={e => setSearch(e.target.value)} className="mt-2" />
            </CardHeader>
            <CardContent className="max-h-96 overflow-y-auto">
              <div className="space-y-2">
                {filteredSkills.filter(s => !userSkillMap.has(s.skill_id)).map(skill => (
                  <div key={skill.skill_id} className="flex items-center justify-between p-2 rounded hover:bg-background-card-hover">
                    <div>
                      <span className="text-sm font-medium">{skill.name}</span>
                      <p className="text-xs text-text-secondary truncate max-w-xs">{skill.description}</p>
                    </div>
                    <Button size="sm" onClick={() => handleAddSkill(skill.skill_id)}>Add</Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
