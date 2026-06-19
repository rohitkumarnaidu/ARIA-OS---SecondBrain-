'use client'

import { Folder, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import type { Collection } from '@/types/resource'

interface CollectionGroupProps {
  collections: Collection[]
  onCollectionClick: (id: string) => void
}

export function CollectionGroup({ collections, onCollectionClick }: CollectionGroupProps) {
  if (collections.length === 0) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Collections</h3>
        <button className="text-xs text-accent-primary hover:underline">View all</button>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
        {collections.map((collection, i) => (
          <motion.button
            key={collection.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            onClick={() => onCollectionClick(collection.id)}
            className="group shrink-0 w-44 rounded-xl p-4 border border-border hover:border-accent-primary/30 transition-all duration-300 hover:shadow-glow-sm text-left"
            style={{
              background: `linear-gradient(135deg, ${collection.coverColor || 'var(--background-card)'} 0%, var(--background-card) 100%)`,
            }}
          >
            <div className="w-9 h-9 rounded-lg bg-accent-primary/10 flex items-center justify-center mb-3 group-hover:bg-accent-primary/20 transition-colors">
              <Folder size={18} className="text-accent-primary" />
            </div>
            <h4 className="text-sm font-medium text-text-primary truncate mb-1">{collection.name}</h4>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-text-tertiary">{collection.itemCount} items</span>
              <ChevronRight size={12} className="text-text-tertiary opacity-0 group-hover:opacity-100 transition-all -translate-x-1 group-hover:translate-x-0" />
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
