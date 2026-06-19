'use client'

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react'

type Theme = 'dark' | 'light'
type AccentColor = 'indigo' | 'emerald' | 'amber' | 'rose'
type Contrast = 'normal' | 'high'

interface ThemeContextValue {
  theme: Theme
  accent: AccentColor
  contrast: Contrast
  setTheme: (t: Theme) => void
  setAccent: (a: AccentColor) => void
  setContrast: (c: Contrast) => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'dark'
  const stored = localStorage.getItem('aria-theme')
  if (stored === 'light' || stored === 'dark') return stored
  return 'dark'
}

function getInitialAccent(): AccentColor {
  if (typeof window === 'undefined') return 'indigo'
  const stored = localStorage.getItem('aria-accent')
  if (stored === 'indigo' || stored === 'emerald' || stored === 'amber' || stored === 'rose') return stored
  return 'indigo'
}

function getInitialContrast(): Contrast {
  if (typeof window === 'undefined') return 'normal'
  const stored = localStorage.getItem('aria-contrast')
  if (stored === 'high' || stored === 'normal') return stored
  return 'normal'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('dark')
  const [accent, setAccentState] = useState<AccentColor>('indigo')
  const [contrast, setContrastState] = useState<Contrast>('normal')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setThemeState(getInitialTheme())
    setAccentState(getInitialAccent())
    setContrastState(getInitialContrast())
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
    root.setAttribute('data-theme', theme)
    root.setAttribute('data-accent', accent)
    root.classList.toggle('high-contrast', contrast === 'high')
  }, [mounted, theme, accent, contrast])

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t)
    localStorage.setItem('aria-theme', t)
  }, [])

  const setAccent = useCallback((a: AccentColor) => {
    setAccentState(a)
    localStorage.setItem('aria-accent', a)
  }, [])

  const setContrast = useCallback((c: Contrast) => {
    setContrastState(c)
    localStorage.setItem('aria-contrast', c)
  }, [])

  return (
    <ThemeContext.Provider value={{ theme, accent, contrast, setTheme, setAccent, setContrast }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return ctx
}
