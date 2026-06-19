'use client'

import { clsx } from 'clsx'

const links = [
  { href: '#main-content', label: 'Skip to main content' },
  { href: '#main-navigation', label: 'Skip to navigation' },
  { href: '#command-center-input', label: 'Skip to search' },
] as const

export function SkipLink() {
  return (
    <div className="sr-only focus-within:not-sr-only focus-within:fixed focus-within:top-4 focus-within:left-4 focus-within:z-[9999] focus-within:flex focus-within:gap-2 focus-within:px-4 focus-within:py-2 focus-within:rounded-lg" style={{ background: 'var(--accent-primary)' }}>
      {links.map((link) => (
        <a
          key={link.href}
          href={link.href}
          className={clsx(
            'px-4 py-2 rounded-md text-sm font-medium transition-opacity text-white',
            'focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2',
          )}
        >
          {link.label}
        </a>
      ))}
    </div>
  )
}
