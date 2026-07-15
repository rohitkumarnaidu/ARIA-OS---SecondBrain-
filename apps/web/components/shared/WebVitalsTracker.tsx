'use client'

import { useEffect } from 'react'
import { reportWebVitals } from '@/lib'

export function WebVitalsTracker() {
  useEffect(() => {
    reportWebVitals()
  }, [])
  return null
}
