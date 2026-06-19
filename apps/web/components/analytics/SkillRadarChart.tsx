'use client'

import { useState, useCallback } from 'react'
import { Brain } from 'lucide-react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
} from 'recharts'
import { cn } from '@/components/ui/utils'
import type { SkillDimension } from '@/types/analytics'

interface SkillRadarChartProps {
  data: SkillDimension[]
}

export function SkillRadarChart({ data }: SkillRadarChartProps) {
  const [activeSkill, setActiveSkill] = useState<string | null>(null)

  const handleMouseEnter = useCallback((props: unknown) => {
    const skill = (props as Record<string, unknown>).skill as string | undefined
    if (skill) setActiveSkill(skill)
  }, [])

  const handleMouseLeave = useCallback(() => {
    setActiveSkill(null)
  }, [])

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
          <Brain size={20} className="text-accent-secondary" />
        </div>
        <div>
          <h2 className="text-lg font-display font-semibold text-text-primary">Skill Radar</h2>
          <p className="text-xs text-text-tertiary">6-dimension performance profile</p>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
            <PolarGrid
              stroke="var(--border)"
              strokeDasharray="3 3"
            />
            <PolarAngleAxis
              dataKey="skill"
              tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
              tickLine={false}
            />
            <Radar
              name="Skills"
              dataKey="value"
              stroke="var(--accent-primary)"
              fill="var(--accent-primary)"
              fillOpacity={activeSkill ? 0.15 : 0.25}
              strokeWidth={2}
              activeDot={{ r: 6, fill: 'var(--accent-primary)', stroke: 'var(--background-card)', strokeWidth: 2 }}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-2">
        {data.map((d) => (
          <div
            key={d.skill}
            className={cn(
              'flex items-center gap-2 px-2 py-1.5 rounded-lg transition-all duration-200',
              activeSkill === d.skill
                ? 'bg-accent-primary/10 text-accent-primary'
                : 'text-text-tertiary',
            )}
            onMouseEnter={() => setActiveSkill(d.skill)}
            onMouseLeave={() => setActiveSkill(null)}
          >
            <div className="flex-1 text-[11px] font-medium truncate">{d.skill}</div>
            <div className="text-xs font-bold font-mono">{d.value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
