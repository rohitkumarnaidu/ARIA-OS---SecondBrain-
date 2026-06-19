'use client'

import { useState, useRef, useEffect } from 'react'
import { Moon, Sun, Palette, Contrast, Check } from 'lucide-react'
import { useTheme } from './ThemeProvider'

const ACCENT_OPTIONS = [
  { value: 'indigo' as const, label: 'Indigo', color: 'var(--accent-palette-indigo)' },
  { value: 'emerald' as const, label: 'Emerald', color: 'var(--accent-palette-emerald)' },
  { value: 'amber' as const, label: 'Amber', color: 'var(--accent-palette-amber)' },
  { value: 'rose' as const, label: 'Rose', color: 'var(--accent-palette-rose)' },
]

export function ThemeSwitcher() {
  const { theme, accent, contrast, setTheme, setAccent, setContrast } = useTheme()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  useEffect(function handleEscape() {
    if (!open) return
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open])

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center justify-center w-10 h-10 rounded-lg border border-border bg-background-elevated text-text-secondary hover:text-text-primary hover:border-border-light transition-all duration-200"
        aria-label="Theme settings"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <Palette size={18} aria-hidden="true" />
      </button>

      {open && (
        <div
          className="absolute right-0 top-full mt-2 w-64 p-2 rounded-xl border border-border bg-popover shadow-lg z-popover backdrop-blur-xl"
          role="menu"
          aria-label="Theme settings menu"
        >
          {/* Theme toggle */}
          <div className="px-2 py-1.5" role="menuitem">
            <button
              type="button"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-text-primary hover:bg-muted transition-colors"
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
            </button>
          </div>

          <div className="h-px bg-border mx-2 my-1" role="separator" />

          {/* Accent color */}
          <div className="px-2 py-1.5" role="menuitem" aria-label="Accent color">
            <p className="px-3 py-1 text-xs font-medium text-text-secondary uppercase tracking-wider">
              Accent Color
            </p>
            <div className="grid grid-cols-4 gap-2 px-3 py-2">
              {ACCENT_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setAccent(opt.value)}
                  className="relative flex items-center justify-center w-full aspect-square rounded-lg border transition-all duration-200 hover:scale-110"
                  style={{
                    backgroundColor: opt.color,
                    borderColor: accent === opt.value ? 'var(--text-primary)' : 'transparent',
                    boxShadow: accent === opt.value ? 'var(--shadow-glow-sm)' : 'none',
                  }}
                  aria-label={`${opt.label} accent`}
                  aria-pressed={accent === opt.value}
                >
                  {accent === opt.value && (
                    <Check size={14} className="text-black" aria-hidden="true" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="h-px bg-border mx-2 my-1" role="separator" />

          {/* Contrast toggle */}
          <div className="px-2 py-1.5" role="menuitem">
            <button
              type="button"
              onClick={() => setContrast(contrast === 'normal' ? 'high' : 'normal')}
              className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-text-primary hover:bg-muted transition-colors"
              aria-label={`${contrast === 'normal' ? 'Enable' : 'Disable'} high contrast`}
              aria-pressed={contrast === 'high'}
            >
              <Contrast size={16} aria-hidden="true" />
              <span>High Contrast</span>
              {contrast === 'high' && (
                <span className="ml-auto">
                  <Check size={14} aria-hidden="true" />
                </span>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
