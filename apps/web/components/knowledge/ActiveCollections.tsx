'use client'

import { FolderEdit, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { formatDistanceToNow } from 'date-fns'

interface ActiveCollection {
  id: string
  name: string
  lastEdited: string
  itemCount: number
}

interface ActiveCollectionsProps {
  collections: ActiveCollection[]
}

export function ActiveCollections({ collections }: ActiveCollectionsProps) {
  if (collections.length === 0) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Recently Edited</h3>
        <span className="text-[10px] text-text-tertiary">Collections</span>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
        {collections.map((col, i) => (
          <motion.div
            key={col.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className="shrink-0 w-48 rounded-xl p-4 border border-border bg-background-card hover:border-accent-info/20 transition-all duration-300 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-lg bg-accent-info/10 flex items-center justify-center mb-3 group-hover:bg-accent-info/20 transition-colors">
              <FolderEdit size={18} className="text-accent-info" />
            </div>
            <h4 className="text-sm font-medium text-text-primary truncate mb-1">{col.name}</h4>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <p className="text-[10px] text-text-tertiary">
                  {formatDistanceToNow(new Date(col.lastEdited), { addSuffix: true })}
                </p>
                <p className="text-[10px] text-text-tertiary">{col.itemCount} items</p>
              </div>
              <ChevronRight size={12} className="text-text-tertiary opacity-0 group-hover:opacity-100 transition-all -translate-x-1 group-hover:translate-x-0" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
