'use client'

import { FileText, BookOpen, Link as LinkIcon, Bookmark, ExternalLink, Grid3X3, List } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { format } from 'date-fns'
import type { Resource } from '@/types/resource'

interface ResourceGridProps {
  resources: Resource[]
  viewMode: 'grid' | 'list'
  onViewModeChange: (mode: 'grid' | 'list') => void
}

const typeIcons: Record<string, typeof FileText> = {
  resource: FileText,
  note: FileText,
  link: LinkIcon,
  bookmark: Bookmark,
  article: Bookmark,
  book: BookOpen,
  tool: LinkIcon,
  paper: FileText,
  github: BookOpen,
  thread: LinkIcon,
  other: FileText,
}

const typeColors: Record<string, string> = {
  resource: 'bg-accent-primary/20 text-accent-primary',
  note: 'bg-accent-info/20 text-accent-info',
  link: 'bg-accent-success/20 text-accent-success',
  bookmark: 'bg-accent-warning/20 text-accent-warning',
  article: 'bg-accent-warning/20 text-accent-warning',
  book: 'bg-accent-info/20 text-accent-info',
  tool: 'bg-accent-primary/20 text-accent-primary',
  paper: 'bg-accent-success/20 text-accent-success',
  github: 'bg-accent-primary/20 text-accent-primary',
  thread: 'bg-accent-neon/20 text-accent-neon',
  other: 'bg-text-secondary/20 text-text-secondary',
}

export function ResourceGrid({ resources, viewMode, onViewModeChange }: ResourceGridProps) {
  if (resources.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-16"
      >
        <FileText size={48} className="text-text-tertiary mx-auto mb-3" />
        <p className="text-text-secondary">No resources match your filters</p>
      </motion.div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-secondary">{resources.length} resources</p>
        <div className="flex items-center gap-1 bg-background-elevated rounded-lg p-1 border border-border">
          <button
            onClick={() => onViewModeChange('grid')}
            className={`p-1.5 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-accent-primary/20 text-accent-primary' : 'text-text-tertiary hover:text-text-primary'}`}
            aria-label="Grid view"
          >
            <Grid3X3 size={16} />
          </button>
          <button
            onClick={() => onViewModeChange('list')}
            className={`p-1.5 rounded-md transition-colors ${viewMode === 'list' ? 'bg-accent-primary/20 text-accent-primary' : 'text-text-tertiary hover:text-text-primary'}`}
            aria-label="List view"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      <AnimatePresence mode="popLayout">
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {resources.map((resource, i) => (
              <ResourceCard key={resource.id} resource={resource} index={i} />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {resources.map((resource, i) => (
              <ResourceListItem key={resource.id} resource={resource} index={i} />
            ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

function ResourceCard({ resource, index }: { resource: Resource; index: number }) {
  const Icon = typeIcons[resource.type] || FileText
  const typeClass = typeColors[resource.type] || typeColors.other

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ delay: index * 0.04 }}
      className="card group relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      <div className="relative z-10 space-y-3">
        <div className="flex items-start justify-between">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${typeClass}`}>
            <Icon size={20} />
          </div>
          <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${typeClass}`}>
            {resource.type}
          </span>
        </div>
        <div>
          <h3 className="font-semibold text-text-primary text-sm leading-snug mb-1 line-clamp-2">
            {resource.title}
          </h3>
          {resource.description && (
            <p className="text-xs text-text-tertiary line-clamp-2">{resource.description}</p>
          )}
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          {resource.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="text-[10px] px-1.5 py-0.5 rounded bg-accent-primary/10 text-accent-secondary"
            >
              {tag}
            </span>
          ))}
          {resource.tags.length > 3 && (
            <span className="text-[10px] text-text-tertiary">+{resource.tags.length - 3}</span>
          )}
        </div>
        <div className="flex items-center justify-between pt-1">
          <span className="text-[10px] text-text-tertiary">
            {format(new Date(resource.createdAt), 'MMM d, yyyy')}
          </span>
          {resource.url && (
            <a
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-primary hover:text-accent-primaryHover transition-colors"
              aria-label="Open resource"
            >
              <ExternalLink size={14} />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  )
}

function ResourceListItem({ resource, index }: { resource: Resource; index: number }) {
  const Icon = typeIcons[resource.type] || FileText
  const typeClass = typeColors[resource.type] || typeColors.other

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ delay: index * 0.03 }}
      className="card group relative overflow-hidden px-4 py-3"
    >
      <div className="flex items-center gap-4">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${typeClass}`}>
          <Icon size={16} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-text-primary text-sm truncate">{resource.title}</h3>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full capitalize shrink-0 ${typeClass}`}>
              {resource.type}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-[10px] text-text-tertiary">
              {format(new Date(resource.createdAt), 'MMM d, yyyy')}
            </span>
            {resource.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-accent-primary/10 text-accent-secondary">
                {tag}
              </span>
            ))}
          </div>
        </div>
        {resource.url && (
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-text-tertiary hover:text-accent-primary transition-colors shrink-0"
            aria-label="Open resource"
          >
            <ExternalLink size={14} />
          </a>
        )}
      </div>
    </motion.div>
  )
}
