export type AISettings = {
  model: 'ollama' | 'claude'
  temperature: number
  briefingTime: string
  agentToggles: Record<string, boolean>
}

export type NotificationSettings = {
  task: boolean
  learning: boolean
  opportunity: boolean
  goal: boolean
  habit: boolean
  system: boolean
  ai: boolean
  priorityThreshold: number
}

export type PrivacySettings = {
  aiUsage: boolean
  analyticsOptOut: boolean
  memoryVisibility: boolean
}

export type AppearanceSettings = {
  sidebarMode: 'default' | 'compact' | 'icons'
  fontSize: number
  reducedMotion: boolean
  compactMode: boolean
}

export type SystemInfo = {
  version: string
  buildDate: string
  storageUsed: string
  storageTotal: string
  integrations: { name: string; status: 'connected' | 'disconnected' | 'error'; icon: string }[]
}

export type UserProfileData = {
  name: string
  email: string
  avatar_url: string | null
  college: string
  year: number
  bio: string
}
