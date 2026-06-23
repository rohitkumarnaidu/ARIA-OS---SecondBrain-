'use client'

import { memo,  type ReactNode, type HTMLAttributes  } from 'react'
import { cn } from './utils'

interface ToolbarProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'surface' | 'ghost'
  children: ReactNode
}

const Toolbar = memo(function Toolbar({ variant = 'surface', className, children, ...props }: ToolbarProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-1 rounded-lg px-2 py-1.5',
        variant === 'surface' && 'bg-[var(--surface-secondary)] border border-border',
        className,
      )}
      role="toolbar"
      aria-orientation="horizontal"
      {...props}
    >
      {children}
    </div>
  )
})

interface ToolbarSeparatorProps {
  className?: string
}

const ToolbarSeparator = memo(function ToolbarSeparator({ className }: ToolbarSeparatorProps) {
  return (
    <div
      className={cn('w-px h-6 mx-1 shrink-0', className)}
      style={{ background: 'var(--border)' }}
      role="separator"
      aria-orientation="vertical"
    />
  )
})

ToolbarSeparator.displayName = 'ToolbarSeparator'
Toolbar.displayName = 'Toolbar'

export { Toolbar, ToolbarSeparator }
export type { ToolbarProps, ToolbarSeparatorProps }
