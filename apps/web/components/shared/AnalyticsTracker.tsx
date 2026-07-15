'use client'

import { useEffect, useRef } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { analytics } from '@/lib/analytics'

export function AnalyticsTracker() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const prevPath = useRef<string>()

  useEffect(() => {
    if (pathname !== prevPath.current) {
      analytics.trackPageView({
        path: pathname,
        title: document.title,
        referrer: prevPath.current ?? document.referrer,
      })
      prevPath.current = pathname
    }
  }, [pathname, searchParams])

  return null
}
