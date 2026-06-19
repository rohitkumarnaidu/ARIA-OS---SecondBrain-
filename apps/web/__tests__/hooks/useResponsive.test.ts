import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useResponsive } from '@/hooks/useResponsive'

describe('useResponsive', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("returns 'desktop' as SSR fallback", () => {
    const { result } = renderHook(() => useResponsive())
    expect(result.current.breakpoint).toBe('desktop')
    expect(result.current.isDesktop).toBe(true)
    expect(result.current.isMobile).toBe(false)
  })

  it("returns 'mobile' breakpoint for mobile width", () => {
    window.innerWidth = 500
    window.innerHeight = 800
    const { result } = renderHook(() => useResponsive())
    act(() => {
      window.dispatchEvent(new Event('resize'))
      vi.advanceTimersByTime(150)
    })
    expect(result.current.breakpoint).toBe('mobile')
    expect(result.current.isMobile).toBe(true)
    expect(result.current.isDesktop).toBe(false)
  })

  it("returns 'tablet' breakpoint for tablet width", () => {
    window.innerWidth = 900
    window.innerHeight = 1024
    const { result } = renderHook(() => useResponsive())
    act(() => {
      window.dispatchEvent(new Event('resize'))
      vi.advanceTimersByTime(150)
    })
    expect(result.current.breakpoint).toBe('tablet')
    expect(result.current.isTablet).toBe(true)
    expect(result.current.isMobile).toBe(false)
  })

  it("returns 'desktop' breakpoint for desktop width", () => {
    window.innerWidth = 1440
    window.innerHeight = 900
    const { result } = renderHook(() => useResponsive())
    act(() => {
      window.dispatchEvent(new Event('resize'))
      vi.advanceTimersByTime(150)
    })
    expect(result.current.breakpoint).toBe('desktop')
    expect(result.current.isDesktop).toBe(true)
    expect(result.current.isTablet).toBe(false)
  })
})
