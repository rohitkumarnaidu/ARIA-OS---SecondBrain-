'use client'

import { onCLS, onFCP, onINP, onLCP, onTTFB } from 'web-vitals'

type MetricName = 'CLS' | 'FCP' | 'INP' | 'LCP' | 'TTFB'

export function reportWebVitals() {
  onCLS((metric) => sendToAnalytics('CLS', metric.value))
  onFCP((metric) => sendToAnalytics('FCP', metric.value))
  onINP((metric) => sendToAnalytics('INP', metric.value))
  onLCP((metric) => sendToAnalytics('LCP', metric.value))
  onTTFB((metric) => sendToAnalytics('TTFB', metric.value))
}

function sendToAnalytics(name: MetricName, value: number) {
  if (process.env.NODE_ENV === 'production') {
    import('@sentry/nextjs').then((Sentry) => {
      Sentry.metrics.distribution(`web_vital.${name}`, value)
    })
  }
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Web Vitals] ${name}: ${value.toFixed(2)}`)
  }
}
