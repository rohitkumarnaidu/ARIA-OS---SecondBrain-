'use client'

import { memo, useMemo } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/components/ui/utils'

const routeLabels: Record<string, string> = {
  'dashboard': 'Dashboard',
  'tasks': 'Tasks',
  'courses': 'Courses',
  'habits': 'Habits',
  'goals': 'Goals',
  'income': 'Income',
  'projects': 'Projects',
  'ideas': 'Ideas',
  'resources': 'Resources',
  'opportunities': 'Opportunities',
  'sleep': 'Sleep',
  'time': 'Time',
  'chat': 'Chat',
  'analytics': 'Analytics',
  'settings': 'Settings',
  'academics': 'Academics',
  'learning': 'Learning',
  'knowledge': 'Knowledge',
  'youtube': 'YouTube',
  'youtube-vault': 'YouTube Vault',
  'briefing': 'Briefing',
  'review': 'Review',
  'automation': 'Automation',
  'monitoring': 'Monitoring',
  'prompt-playground': 'Prompt Playground',
  'agents': 'Agents',
  'memory': 'Memory',
  'focus': 'Focus',
  'nudges': 'Nudges',
  'roadmap': 'Roadmap',
  'flags': 'Flags',
  'skills': 'Skills',
  'offline': 'Offline',
}

interface BreadcrumbItem {
  label: string
  href: string
}

interface BreadcrumbsProps {
  overrides?: Record<string, string>
  className?: string
  showHome?: boolean
}

export const Breadcrumbs = memo(function Breadcrumbs({
  overrides,
  className,
  showHome = true,
}: BreadcrumbsProps) {
  const pathname = usePathname()

  const items = useMemo(() => {
    const segments = pathname.split('/').filter(Boolean)
    const result: BreadcrumbItem[] = []

    if (showHome) {
      result.push({ label: 'Home', href: '/dashboard' })
    }

    let accumulated = ''
    for (const segment of segments) {
      accumulated += `/${segment}`
      const label =
        overrides?.[segment] ??
        routeLabels[segment] ??
        segment.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
      result.push({ label, href: accumulated })
    }

    return result
  }, [pathname, overrides, showHome])

  if (items.length <= 1 && !showHome) {
    return null
  }

  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center gap-1.5 text-sm font-body', className)}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        return (
          <span key={item.href} className="flex items-center gap-1.5">
            {index > 0 && (
              <ChevronRight
                size={14}
                className="text-text-tertiary shrink-0"
                aria-hidden="true"
              />
            )}
            {isLast ? (
              <span
                className="text-foreground font-medium"
                aria-current="page"
              >
                {item.label}
              </span>
            ) : (
              <Link
                href={item.href}
                className="text-text-secondary hover:text-foreground transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded"
              >
                {item.label}
              </Link>
            )}
          </span>
        )
      })}
    </nav>
  )
})
