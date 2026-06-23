'use client'

import { memo,  forwardRef, useState, type HTMLAttributes  } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from './utils'

const avatarSizes = {
  sm: 'size-8',
  md: 'size-10',
  lg: 'size-12',
  xl: 'size-16',
} as const

const avatarTextSizes = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-xl',
} as const

const statusDotSizes = {
  sm: 'size-2.5',
  md: 'size-3',
  lg: 'size-3.5',
  xl: 'size-4',
} as const

const statusVariants = cva('absolute bottom-0 right-0 rounded-full border-2 border-background-page', {
  variants: {
    status: {
      online: 'bg-accent-success',
      away: 'bg-accent-warning',
      busy: 'bg-accent-error',
      offline: 'bg-text-tertiary',
    },
  },
  defaultVariants: {
    status: 'offline',
  },
})

interface AvatarProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'children'>,
    VariantProps<typeof statusVariants> {
  src?: string
  alt?: string
  name: string
  size?: keyof typeof avatarSizes
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/)
  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
}

const Avatar = memo(forwardRef<HTMLDivElement, AvatarProps>(
  ({ src, alt, name, size = 'md', status, className, ...props }, ref) => {
    const [imgError, setImgError] = useState(false)
    const showImage = src && !imgError
    const initials = getInitials(name)
    const ariaLabel = alt || name

    return (
      <div
        ref={ref}
        className={cn(
          'relative inline-flex shrink-0 items-center justify-center rounded-full',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-background',
          avatarSizes[size],
          !showImage && 'bg-background-elevated text-text-secondary font-medium',
          className,
        )}
        data-slot="avatar"
        role="img"
        aria-label={ariaLabel}
        tabIndex={0}
        {...props}
      >
        {showImage ? (
          <img
            src={src}
            alt={alt || name}
            className="size-full rounded-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <span className={cn('select-none', avatarTextSizes[size])}>{initials}</span>
        )}
        {status && (
          <span
            className={cn(statusVariants({ status }), statusDotSizes[size])}
            aria-label={status}
            data-slot="avatar-status"
          />
        )}
      </div>
    )
  },
)
)
Avatar.displayName = 'Avatar'

export { Avatar }
export type { AvatarProps }
