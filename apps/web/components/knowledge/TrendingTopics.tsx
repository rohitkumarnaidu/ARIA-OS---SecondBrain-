'use client'

import { TrendingUp, TrendingDown } from 'lucide-react'
import { motion } from 'framer-motion'

interface Topic {
  tag: string
  count: number
  growth: number
}

interface TrendingTopicsProps {
  topics: Topic[]
}

export function TrendingTopics({ topics }: TrendingTopicsProps) {
  if (topics.length === 0) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Trending Topics</h3>
        <span className="text-[10px] text-text-tertiary">Based on recent activity</span>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
        {topics.map((topic, i) => (
          <motion.div
            key={topic.tag}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className="shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-background-card hover:border-accent-primary/20 transition-colors cursor-default"
          >
            <span className="text-xs font-medium text-text-primary">{topic.tag}</span>
            <span className="text-[10px] text-text-tertiary">({topic.count})</span>
            <span
              className={`flex items-center gap-0.5 text-[10px] font-medium ${
                topic.growth >= 0 ? 'text-accent-success' : 'text-accent-error'
              }`}
            >
              {topic.growth >= 0 ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
              {Math.abs(topic.growth)}%
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
