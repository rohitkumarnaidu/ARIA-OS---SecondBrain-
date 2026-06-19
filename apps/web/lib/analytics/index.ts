'use client'

type EventProperties = Record<string, string | number | boolean | undefined | null>

type PageViewEvent = {
  path: string
  title: string
  referrer: string
}

type ActionEvent = {
  name: string
  properties?: EventProperties
}

const POSTHOG_API_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'
const POSTHOG_API_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY || ''

function getDistinctId(): string | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem('sb-analytics-id')
    if (stored) return stored
    const id = crypto.randomUUID()
    localStorage.setItem('sb-analytics-id', id)
    return id
  } catch {
    return null
  }
}

function sendEvent(eventName: string, properties: EventProperties = {}): void {
  if (!POSTHOG_API_KEY) return

  const distinctId = getDistinctId()
  if (!distinctId) return

  const payload = {
    api_key: POSTHOG_API_KEY,
    distinct_id: distinctId,
    event: eventName,
    properties: {
      ...properties,
      $lib: 'sb-analytics',
      $lib_version: '1.0.0',
      $session_id: typeof window !== 'undefined' ? sessionStorage.getItem('sb-session') || '' : '',
      $referrer: typeof document !== 'undefined' ? document.referrer || '' : '',
      $current_url: typeof window !== 'undefined' ? window.location.href : '',
    },
    timestamp: new Date().toISOString(),
  }

  if (process.env.NODE_ENV === 'development') {
    console.debug('[Analytics]', eventName, properties)
    return
  }

  try {
    const img = new Image()
    img.src = `${POSTHOG_API_HOST}/capture/?data=${encodeURIComponent(JSON.stringify(payload))}`
    img.width = 1
    img.height = 1
    img.style.display = 'none'
  } catch {
    // fail silently — analytics should never break the app
  }
}

function trackPageView(event: PageViewEvent): void {
  sendEvent('$pageview', {
    $pathname: event.path,
    $title: event.title,
    $referrer: event.referrer,
  })
}

function trackAction(event: ActionEvent): void {
  sendEvent(event.name, event.properties)
}

function identifyUser(userId: string, traits?: EventProperties): void {
  sendEvent('$identify', { $user_id: userId, ...traits })
}

function initSession(): void {
  if (typeof window === 'undefined') return
  try {
    if (!sessionStorage.getItem('sb-session')) {
      sessionStorage.setItem('sb-session', crypto.randomUUID())
    }
  } catch {
    // session storage unavailable
  }
}

initSession()

export const analytics = {
  trackPageView,
  trackAction,
  identifyUser,
  sendEvent,
}
