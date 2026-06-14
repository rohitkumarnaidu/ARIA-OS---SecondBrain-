export const TEST_TIMEOUTS = {
  /** Page navigation and load */
  NAVIGATION: 30_000,
  /** Network request completion */
  NETWORK_IDLE: 10_000,
  /** Animation completion */
  ANIMATION: 2_000,
  /** PWA service worker registration */
  SERVICE_WORKER: 15_000,
  /** Offline detection */
  OFFLINE_DETECTION: 5_000,
} as const

export const ROUTES = {
  PUBLIC: {
    HOME: '/',
    LOGIN: '/login',
  },
  PROTECTED: {
    DASHBOARD: '/dashboard',
    TASKS: '/tasks',
    COURSES: '/courses',
    GOALS: '/goals',
    HABITS: '/habits',
    SLEEP: '/sleep',
    INCOME: '/income',
    PROJECTS: '/projects',
    IDEAS: '/ideas',
    RESOURCES: '/resources',
    OPPORTUNITIES: '/opportunities',
    TIME: '/time',
    CHAT: '/chat',
    AUTOMATION: '/automation',
    ACADEMICS: '/academics',
    YOUTUBE: '/youtube',
  },
} as const

export const AUTH = {
  /** Storage state path for authenticated sessions */
  STORAGE_STATE: 'e2e/.auth/user.json',
  /** Test user credentials — override via env or CI secrets */
  TEST_USER: {
    email: process.env.TEST_USER_EMAIL || 'test@secondbrain.local',
    password: process.env.TEST_USER_PASSWORD || 'TestPassword123!',
  },
} as const

export const MANIFEST_EXPECTATIONS = {
  name: 'ARIA OS — Your Second Brain',
  short_name: 'ARIA OS',
  start_url: '/dashboard',
  display: 'standalone',
  background_color: '#0A0B0F',
  theme_color: '#6366F1',
  icons: [
    { sizes: '192x192', type: 'image/png' },
    { sizes: '512x512', type: 'image/png' },
  ],
  categories: ['productivity', 'education', 'ai'],
} as const
