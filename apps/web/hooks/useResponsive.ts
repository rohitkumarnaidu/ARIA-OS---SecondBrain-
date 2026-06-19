'use client'

import { useState, useEffect } from 'react'

export type Breakpoint = 'mobile' | 'tablet' | 'desktop'

export interface ResponsiveInfo {
  breakpoint: Breakpoint
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  width: number
  height: number
  isTouchDevice: boolean
}

function getResponsiveInfo(width: number, height: number, isTouchDevice: boolean): ResponsiveInfo {
  const breakpoint: Breakpoint = width < 768 ? 'mobile' : width < 1024 ? 'tablet' : 'desktop'
  return {
    breakpoint,
    isMobile: breakpoint === 'mobile',
    isTablet: breakpoint === 'tablet',
    isDesktop: breakpoint === 'desktop',
    width,
    height,
    isTouchDevice,
  }
}

const SSR_FALLBACK: ResponsiveInfo = {
  breakpoint: 'desktop',
  isMobile: false,
  isTablet: false,
  isDesktop: true,
  width: 1024,
  height: 768,
  isTouchDevice: false,
}

export function useResponsive(): ResponsiveInfo {
  const [info, setInfo] = useState<ResponsiveInfo>(SSR_FALLBACK)

  useEffect(() => {
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0

    const updateSize = () => {
      setInfo(getResponsiveInfo(window.innerWidth, window.innerHeight, isTouchDevice))
    }

    updateSize()

    let timeoutId: ReturnType<typeof setTimeout>
    const handleResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(updateSize, 100)
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      clearTimeout(timeoutId)
    }
  }, [])

  return info
}
