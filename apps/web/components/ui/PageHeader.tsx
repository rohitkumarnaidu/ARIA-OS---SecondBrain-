import { ChevronRight } from 'lucide-react'
import { cn } from './utils'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface PageHeaderProps {
  title: string
  description?: string
  breadcrumb?: BreadcrumbItem[]
  actions?: React.ReactNode
  className?: string
}

export function PageHeader({ title, description, breadcrumb, actions, className }: PageHeaderProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {breadcrumb && breadcrumb.length > 0 && (
        <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm font-body">
          {breadcrumb.map((item, index) => {
            const isLast = index === breadcrumb.length - 1
            return (
              <span key={`${item.label}-${index}`} className="flex items-center gap-1.5">
                {index > 0 && (
                  <ChevronRight size={14} className="text-text-tertiary shrink-0" aria-hidden="true" />
                )}
                {item.href && !isLast ? (
                  <a
                    href={item.href}
                    className="text-text-secondary hover:text-foreground transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded"
                  >
                    {item.label}
                  </a>
                ) : (
                  <span
                    className={cn(
                      isLast ? 'text-foreground font-medium' : 'text-text-secondary',
                    )}
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {item.label}
                  </span>
                )}
              </span>
            )
          })}
        </nav>
      )}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="space-y-1 min-w-0">
          <h1 className="text-2xl font-display font-semibold text-foreground truncate">{title}</h1>
          {description && (
            <p className="text-sm text-text-secondary font-body max-w-[600px]">{description}</p>
          )}
        </div>
        {actions && (
          <div className="flex items-center gap-2 shrink-0 min-h-touch">
            {actions}
          </div>
        )}
      </div>
    </div>
  )
}
