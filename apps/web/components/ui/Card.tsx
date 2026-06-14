import { clsx } from 'clsx'

interface CardProps {
  children: React.ReactNode
  className?: string
  interactive?: boolean
  onClick?: () => void
}

export function Card({ children, className, interactive, onClick }: CardProps) {
  const Component = interactive ? 'button' : 'div'

  return (
    <Component
      onClick={onClick}
      className={clsx(
        'bg-background-card border border-border rounded-xl p-4',
        'backdrop-filter backdrop-blur-[20px]',
        'shadow-[0_4px_24px_rgba(0,0,0,0.2)]',
        interactive && 'cursor-pointer transition-all duration-300 hover:border-border-light hover:shadow-lg group',
        className,
      )}
    >
      {children}
    </Component>
  )
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={clsx('flex items-center justify-between mb-4', className)}>{children}</div>
}

export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
  return <h3 className={clsx('text-lg font-semibold text-text-primary', className)}>{children}</h3>
}

export function CardContent({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={className}>{children}</div>
}
