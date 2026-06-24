import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useCommandCenter } from '@/hooks/useCommandCenter'

describe('useCommandCenter', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should return isOpen as false initially', () => {
    const { result } = renderHook(() => useCommandCenter())
    expect(result.current.isOpen).toBe(false)
  })

  it('should set isOpen to true when open is called', () => {
    const { result } = renderHook(() => useCommandCenter())
    act(() => { result.current.open() })
    expect(result.current.isOpen).toBe(true)
  })

  it('should set isOpen to false when close is called', () => {
    const { result } = renderHook(() => useCommandCenter())
    act(() => { result.current.open() })
    expect(result.current.isOpen).toBe(true)
    act(() => { result.current.close() })
    expect(result.current.isOpen).toBe(false)
  })

  it('should toggle isOpen when toggle is called', () => {
    const { result } = renderHook(() => useCommandCenter())
    act(() => { result.current.toggle() })
    expect(result.current.isOpen).toBe(true)
    act(() => { result.current.toggle() })
    expect(result.current.isOpen).toBe(false)
  })

  it('should toggle isOpen on Cmd+K keydown', () => {
    renderHook(() => useCommandCenter())
    act(() => {
      document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true })
      )
    })
  })

  it('should toggle isOpen on Ctrl+K keydown', () => {
    renderHook(() => useCommandCenter())
    act(() => {
      document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true })
      )
    })
  })

  it('should not toggle on other key combos', () => {
    const { result } = renderHook(() => useCommandCenter())
    act(() => {
      document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'j', metaKey: true, bubbles: true })
      )
    })
    expect(result.current.isOpen).toBe(false)
  })

  it('should not toggle on K without modifier', () => {
    const { result } = renderHook(() => useCommandCenter())
    act(() => {
      document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'k', bubbles: true })
      )
    })
    expect(result.current.isOpen).toBe(false)
  })

  it('should prevent default on Cmd+K / Ctrl+K', () => {
    renderHook(() => useCommandCenter())
    const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true, cancelable: true })
    const preventDefaultSpy = vi.spyOn(event, 'preventDefault')
    document.dispatchEvent(event)
    expect(preventDefaultSpy).toHaveBeenCalled()
  })

  it('should remove keyboard listener on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener')
    const { unmount } = renderHook(() => useCommandCenter())
    unmount()
    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))
  })
})
