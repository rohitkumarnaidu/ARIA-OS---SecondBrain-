'use client'

import { useEffect, useState } from 'react'

interface LiveRegionProps {
  message: string
  politeness?: 'polite' | 'assertive'
}

export function LiveRegion({ message, politeness = 'polite' }: LiveRegionProps) {
  const [current, setCurrent] = useState(message)
  useEffect(() => { setCurrent(message) }, [message])
  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {current}
    </div>
  )
}
