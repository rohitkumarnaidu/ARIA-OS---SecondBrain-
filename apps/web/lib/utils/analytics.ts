export function trackEvent(name: string, properties?: Record<string, unknown>) {
  try {
    if (typeof window !== 'undefined') {
      const posthog = (window as any).posthog
      if (posthog?.capture) {
        posthog.capture(name, properties)
      }
    }
  } catch {
    // Analytics must never throw
  }
}

export function trackPageView(path: string) {
  trackEvent('$pageview', { path })
}
