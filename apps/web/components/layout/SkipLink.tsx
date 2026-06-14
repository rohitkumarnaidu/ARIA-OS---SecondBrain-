'use client'

import { useState } from 'react'
import { clsx } from 'clsx'

export function SkipLink() {
  const [isFocused, setIsFocused] = useState(false)

  return (
    <a
      href="#main-content"
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      className={clsx(
        'sr-only focus:not-sr-only',
        'focus:fixed focus:top-4 focus:left-4 focus:z-tooltip',
        'focus:px-4 focus:py-2 focus:bg-background-card focus:text-text-primary',
        'focus:border focus:border-accent-primary focus:rounded-lg',
        'focus:outline-none focus:ring-2 focus:ring-accent-primary',
        'focus:text-sm focus:font-medium',
      )}
    >
      Skip to main content
    </a>
  )
}
