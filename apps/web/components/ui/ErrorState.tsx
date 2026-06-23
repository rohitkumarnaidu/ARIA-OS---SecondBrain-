'use client'

import { memo,  useState, useEffect  } from 'react'
import { AlertTriangle, Ban, Clock, ServerCrash, ArrowLeft, RefreshCw, Mail } from 'lucide-react'
import { cn } from './utils'

type ErrorStatus = 400 | 404 | 429 | 500

interface ErrorStateProps {
  status?: ErrorStatus
  title?: string
  description?: string
  icon?: React.ReactNode
  resource?: string
  onRetry?: () => void
  onGoBack?: () => void
  compact?: boolean
  className?: string
}

const statusMeta: Record<ErrorStatus, { defaultTitle: string; defaultDesc: string; icon: React.ReactNode }> = {
  400: {
    defaultTitle: 'Invalid Request',
    defaultDesc: 'Please check your input and try again.',
    icon: <Ban size={28} />,
  },
  404: {
    defaultTitle: 'Not Found',
    defaultDesc: "The {resource} you're looking for doesn't exist or has been moved.",
    icon: <AlertTriangle size={28} />,
  },
  429: {
    defaultTitle: 'Rate Limited',
    defaultDesc: "You've made too many requests. Please wait {seconds}s before trying again.",
    icon: <Clock size={28} />,
  },
  500: {
    defaultTitle: 'Server Error',
    defaultDesc: 'Something went wrong on our end. Please try again.',
    icon: <ServerCrash size={28} />,
  },
}

export const ErrorState = memo(function ErrorState({
  status = 500,
  title,
  description,
  icon,
  resource = 'page',
  onRetry,
  onGoBack,
  compact,
  className,
}: ErrorStateProps) {
  const [countdown, setCountdown] = useState(30)

  useEffect(() => {
    if (status !== 429) return
    setCountdown(30)
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval)
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [status])

  const meta = statusMeta[status]
  const resolvedTitle = title || meta.defaultTitle
  const resolvedDesc = (description || meta.defaultDesc)
    .replace(/\{resource\}/g, resource)
    .replace(/\{seconds\}/g, String(countdown))

  const errorIcon = icon || (
    <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-accent-error/10 border border-accent-error/20">
      <span className="text-accent-error" aria-hidden="true">{meta.icon}</span>
    </div>
  )

  const containerClass = compact
    ? cn('flex flex-col items-center py-8 px-4 text-center', className)
    : cn(
        'flex-1 flex flex-col items-center justify-center p-8 min-h-0 relative',
        className,
      )

  const frameClass = compact
    ? 'w-full max-w-[400px] flex flex-col items-center text-center'
    : 'relative w-full max-w-[520px] rounded-2xl flex flex-col items-center justify-center py-20 px-10 text-center border border-dashed border-border'

  return (
    <div className={containerClass} role="alert">
      {!compact && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse 60% 40% at 50% 50%, rgba(239,68,68,0.04) 0%, transparent 70%)',
          }}
        />
      )}
      <div className={frameClass}>
        {errorIcon}
        <h2 className={cn('text-foreground font-display font-semibold', compact ? 'text-lg mt-4 mb-1' : 'text-2xl mt-6 mb-3')}>
          {resolvedTitle}
        </h2>
        <p className={cn('text-text-secondary font-body leading-relaxed', compact ? 'text-sm max-w-[280px]' : 'text-sm max-w-[360px] mb-6')}>
          {resolvedDesc}
          {status === 429 && countdown > 0 && (
            <span className="inline-flex items-center gap-1 ml-1.5 font-mono text-accent-warning">
              <Clock size={14} />
              {countdown}s
            </span>
          )}
        </p>
        <div className="flex items-center gap-3 flex-wrap justify-center">
          {(status === 400 || status === 500) && onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className={cn(
                'inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium font-body',
                'transition-all duration-200 ease-out',
                'hover:opacity-90 active:scale-[0.98]',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                'bg-accent-primary text-white shadow-glow-sm',
              )}
            >
              <RefreshCw size={16} aria-hidden="true" />
              Try Again
            </button>
          )}
          {(status === 429 || status === 404) && onGoBack && (
            <button
              type="button"
              onClick={onGoBack}
              className={cn(
                'inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium font-body',
                'transition-all duration-200 ease-out',
                'hover:bg-background-elevated active:scale-[0.98]',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                'bg-background-elevated text-text-secondary border border-border',
              )}
            >
              <ArrowLeft size={16} aria-hidden="true" />
              Go Back
            </button>
          )}
          {status === 500 && (
            <a
              href="mailto:support@secondbrain-os.com"
              className={cn(
                'inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium font-body',
                'transition-all duration-200 ease-out',
                'hover:bg-background-elevated active:scale-[0.98]',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                'bg-background-elevated text-text-secondary border border-border',
              )}
            >
              <Mail size={16} aria-hidden="true" />
              Contact Support
            </a>
          )}
        </div>
        {!compact && (
          <div className="absolute bottom-4 right-4 text-[10px] opacity-30 tracking-[0.8px] font-mono text-text-secondary select-none">
            ERROR_{status}
          </div>
        )}
      </div>
    </div>
  )
})
