import { memo } from 'react'
import { Sparkles } from 'lucide-react'
import { cn } from './utils'

interface EmptyCanvasProps {
  icon?: React.ReactNode
  title: string
  description: string
  badge?: string
  actions?: { label: string; primary?: boolean; onClick?: () => void }[]
  className?: string
}

export const EmptyCanvas = memo(function EmptyCanvas({ icon, title, description, badge, actions, className }: EmptyCanvasProps) {
  return (
    <div className={cn('flex-1 flex flex-col items-center justify-center p-8 min-h-0 relative', className)}>
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 40% at 50% 50%, rgba(99,102,241,0.06) 0%, transparent 70%)',
        }}
      />
      <div className="relative w-full max-w-[520px] rounded-2xl flex flex-col items-center justify-center py-20 px-10 text-center border border-dashed border-border">
        <div className="flex items-center justify-center w-16 h-16 rounded-2xl mb-6 bg-accent-primary/10 border border-accent-primary/20">
          {icon || <Sparkles size={28} className="text-accent-primary" />}
        </div>
        {badge && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] mb-4 font-mono uppercase tracking-wide bg-accent-primary/10 border border-accent-primary/20 text-accent-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse" />
            {badge}
          </div>
        )}
        <h2 className="text-foreground text-2xl mb-3 font-display font-semibold">{title}</h2>
        <p className="text-text-secondary text-sm leading-relaxed mb-6 max-w-[320px] font-body">{description}</p>
        {actions && actions.length > 0 && (
          <div className="flex items-center gap-3 flex-wrap justify-center">
            {actions.map((action) =>
              action.primary ? (
                <button
                  key={action.label}
                  type="button"
                  onClick={action.onClick}
                  className={cn(
                    'px-5 py-2.5 rounded-lg text-sm font-medium font-body',
                    'transition-all duration-200 ease-out',
                    'hover:opacity-90 active:scale-[0.98]',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                    'bg-accent-primary text-white shadow-glow-sm',
                  )}
                >
                  {action.label}
                </button>
              ) : (
                <button
                  key={action.label}
                  type="button"
                  onClick={action.onClick}
                  className={cn(
                    'px-5 py-2.5 rounded-lg text-sm font-medium font-body',
                    'transition-all duration-200 ease-out',
                    'hover:bg-background-elevated active:scale-[0.98]',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                    'bg-background-elevated text-text-secondary border border-border',
                  )}
                >
                  {action.label}
                </button>
              ),
            )}
          </div>
        )}
        <div className="absolute bottom-4 right-4 text-[10px] opacity-30 tracking-[0.8px] font-mono text-text-secondary select-none">
          CANVAS_AREA
        </div>
      </div>
    </div>
  )
})
