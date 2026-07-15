'use client'

import { useState, useEffect, useCallback, useRef, useId } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  User,
  Cpu,
  Bell,
  Shield,
  Palette,
  Monitor,
  Download,
  Trash2,
  Check,
  Camera,
  Sun,
  Moon,
  Save,
  RefreshCw,
  Wifi,
  Cloud,
  Github,
  Clock,
  BrainCircuit,
  Sparkles,
  BookOpen,
  Target,
  Zap,
  Lightbulb,
  Eye,
  BarChart3,
  Settings,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { useTheme } from '@/components/theme/ThemeProvider'
import type {
  UserProfileData,
  AISettings,
  NotificationSettings,
  PrivacySettings,
  AppearanceSettings,
  SystemInfo,
} from '@/types/settings'

/* ──────── Storage Helpers ──────── */

const STORAGE_KEYS = {
  profile: 'aria-settings-profile',
  ai: 'aria-settings-ai',
  notifications: 'aria-settings-notifications',
  privacy: 'aria-settings-privacy',
  appearance: 'aria-settings-appearance',
} as const

function loadFromStorage<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback
  try {
    const raw = localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function saveToStorage<T>(key: string, value: T) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* storage full or unavailable */
  }
}

/* ──────── Defaults ──────── */

const DEFAULT_PROFILE: UserProfileData = {
  name: 'Aria User',
  email: 'user@secondbrain.ai',
  avatar_url: null,
  college: '',
  year: 1,
  bio: '',
}

const DEFAULT_AI: AISettings = {
  model: 'ollama',
  temperature: 50,
  briefingTime: '07:00',
  agentToggles: {
    planner: true,
    memory: true,
    learning: true,
    reminder: true,
    career: false,
    opportunity: true,
    analytics: true,
    briefing: true,
    weekly_review: true,
    sleep: true,
  },
}

const DEFAULT_NOTIFICATIONS: NotificationSettings = {
  task: true,
  learning: true,
  opportunity: true,
  goal: true,
  habit: true,
  system: false,
  ai: true,
  priorityThreshold: 2,
}

const DEFAULT_PRIVACY: PrivacySettings = {
  aiUsage: true,
  analyticsOptOut: false,
  memoryVisibility: true,
}

const DEFAULT_APPEARANCE: AppearanceSettings = {
  sidebarMode: 'default',
  fontSize: 15,
  reducedMotion: false,
  compactMode: false,
}

const DEFAULT_SYSTEM_INFO: SystemInfo = {
  version: '4.0.0',
  buildDate: '2026-06-14',
  storageUsed: '342 MB',
  storageTotal: '1 GB',
  integrations: [
    { name: 'Supabase', status: 'connected', icon: 'database' },
    { name: 'Ollama', status: 'connected', icon: 'bot' },
    { name: 'Claude API', status: 'disconnected', icon: 'sparkles' },
    { name: 'GitHub', status: 'connected', icon: 'github' },
    { name: 'Google Calendar', status: 'disconnected', icon: 'calendar' },
    { name: 'Resend', status: 'disconnected', icon: 'mail' },
  ],
}

/* ──────── Agent Registry ──────── */

const AGENTS: { id: string; name: string; Icon: LucideIcon; description: string }[] = [
  { id: 'planner', name: 'Planner', Icon: BrainCircuit, description: 'Task planning & scheduling' },
  { id: 'memory', name: 'Memory', Icon: RefreshCw, description: 'Context & recollection' },
  { id: 'learning', name: 'Learning', Icon: BookOpen, description: 'Pattern detection & insights' },
  { id: 'reminder', name: 'Reminder', Icon: Bell, description: 'Timely notifications' },
  { id: 'career', name: 'Career', Icon: Target, description: 'Career opportunity tracking' },
  { id: 'opportunity', name: 'Opportunity', Icon: Lightbulb, description: 'Opportunity matching' },
  { id: 'analytics', name: 'Analytics', Icon: BarChart3, description: 'Usage & performance stats' },
  { id: 'briefing', name: 'Briefing', Icon: Sparkles, description: 'Daily morning briefings' },
  { id: 'weekly_review', name: 'Weekly Review', Icon: Clock, description: 'Weekly summary & insights' },
  { id: 'sleep', name: 'Sleep', Icon: Moon, description: 'Sleep tracking & wind-down' },
]

/* ──────── Tab Config ──────── */

const TABS: { id: string; label: string; Icon: LucideIcon }[] = [
  { id: 'profile', label: 'Profile', Icon: User },
  { id: 'ai', label: 'AI & Personalization', Icon: Cpu },
  { id: 'notifications', label: 'Notifications', Icon: Bell },
  { id: 'privacy', label: 'Privacy & Data', Icon: Shield },
  { id: 'appearance', label: 'Appearance', Icon: Palette },
  { id: 'system', label: 'System', Icon: Monitor },
]

/* ──────── Sub-Components ──────── */

function ToggleSwitch({
  checked,
  onChange,
  id,
  label,
}: {
  checked: boolean
  onChange: (v: boolean) => void
  id: string
  label?: string
}): JSX.Element {
  return (
    <label
      htmlFor={id}
      className={cn(
        'relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full transition-colors duration-200',
        'focus-visible-within:outline-none focus-visible-within:ring-2 focus-visible-within:ring-[var(--ring)] focus-visible-within:ring-offset-2 focus-visible-within:ring-offset-[var(--background)]',
        checked ? 'bg-[var(--accent-success)]' : 'bg-[var(--surface-tertiary)]',
      )}
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only peer"
        aria-label={label}
      />
      <span
        className={cn(
          'inline-block h-5 w-5 rounded-full bg-white shadow-sm ring-0 transition-transform duration-200',
          checked ? 'translate-x-[22px]' : 'translate-x-[2px]',
        )}
      />
    </label>
  )
}

function SliderInput({
  value,
  onChange,
  min,
  max,
  step,
  id,
  label,
  marks,
}: {
  value: number
  onChange: (v: number) => void
  min: number
  max: number
  step?: number
  id: string
  label?: string
  marks?: { value: number; label: string }[]
}): JSX.Element {
  const ratio = (value - min) / (max - min)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        {label && (
          <label htmlFor={id} className="text-sm text-text-secondary">{label}</label>
        )}
        <span className="text-sm font-mono text-text-primary">{value}</span>
      </div>
      <div className="relative">
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          step={step ?? 1}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer bg-[var(--surface-tertiary)] [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[var(--accent-primary)] [&::-webkit-slider-thumb]:shadow-glow-sm [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:duration-150 [&::-webkit-slider-thumb]:hover:scale-125 [&::-moz-range-thumb]:appearance-none [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-[var(--accent-primary)] [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:shadow-glow-sm"
          style={{
            background: `linear-gradient(to right, var(--accent-primary) 0%, var(--accent-primary) ${ratio * 100}%, var(--surface-tertiary) ${ratio * 100}%, var(--surface-tertiary) 100%)`,
          }}
          aria-label={label}
          aria-valuenow={value}
          aria-valuemin={min}
          aria-valuemax={max}
        />
        {marks && (
          <div className="flex justify-between mt-1.5">
            {marks.map((m) => (
              <button
                key={m.value}
                type="button"
                onClick={() => onChange(m.value)}
                className={cn(
                  'text-xs transition-colors duration-150 px-1',
                  value === m.value
                    ? 'text-[var(--accent-primary)] font-medium'
                    : 'text-text-tertiary hover:text-text-secondary',
                )}
                aria-label={`Set to ${m.label}`}
              >
                {m.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function SectionCard({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}): JSX.Element {
  return (
    <Card
      className={cn(
        'bg-surface-primary/60 backdrop-blur-xl border border-border',
        className,
      )}
    >
      {children}
    </Card>
  )
}

function SettingRow({
  icon: Icon,
  label,
  description,
  children,
  id,
}: {
  icon?: LucideIcon
  label: string
  description?: string
  children: React.ReactNode
  id?: string
}): JSX.Element {
  return (
    <div
      id={id}
      className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0 border-b border-border last:border-0"
    >
      <div className="flex items-start gap-3 min-w-0 flex-1">
        {Icon && (
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-surface-secondary text-text-secondary">
            <Icon size={16} aria-hidden="true" />
          </div>
        )}
        <div className="min-w-0">
          <p className="text-sm font-medium text-text-primary truncate">{label}</p>
          {description && (
            <p className="text-xs text-text-tertiary mt-0.5 line-clamp-2">{description}</p>
          )}
        </div>
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  )
}

/* ──────── Section Components ──────── */

function ProfileSection({
  data,
  onChange,
}: {
  data: UserProfileData
  onChange: (d: UserProfileData) => void
}): JSX.Element {
  const fileRef = useRef<HTMLInputElement>(null)
  const [saved, setSaved] = useState(false)

  const handleSave = useCallback(() => {
    saveToStorage(STORAGE_KEYS.profile, data)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }, [data])

  return (
    <SectionCard>
      <CardHeader className="px-6 pt-6 pb-0">
        <CardTitle className="font-display text-lg">Profile</CardTitle>
        <CardDescription>Your personal information across ARIA OS</CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        {/* Avatar */}
        <div className="flex items-center gap-5">
          <div className="relative group">
            <div className="h-20 w-20 rounded-full overflow-hidden bg-surface-secondary border-2 border-border">
              {data.avatar_url ? (
                <img
                  src={data.avatar_url}
                  alt="Avatar"
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-2xl font-display font-semibold text-text-primary">
                  {data.name.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              aria-label="Upload avatar"
            >
              <Camera size={20} className="text-white" />
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="hidden"
              aria-hidden="true"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  const reader = new FileReader()
                  reader.onload = (ev) => {
                    const url = ev.target?.result as string
                    onChange({ ...data, avatar_url: url })
                  }
                  reader.readAsDataURL(file)
                }
              }}
            />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-text-primary">{data.name}</p>
            <p className="text-xs text-text-tertiary">{data.email}</p>
          </div>
        </div>

        {/* Name */}
        <div className="space-y-1.5">
          <label htmlFor="settings-name" className="block text-sm font-medium text-text-secondary">
            Full Name
          </label>
          <input
            id="settings-name"
            type="text"
            value={data.name}
            onChange={(e) => onChange({ ...data, name: e.target.value })}
            className="w-full h-11 px-4 rounded-lg bg-surface-secondary border border-border text-text-primary placeholder:text-text-tertiary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:border-transparent text-sm"
          />
        </div>

        {/* Email (read-only) */}
        <div className="space-y-1.5">
          <span className="block text-sm font-medium text-text-secondary">Email</span>
          <div className="w-full h-11 px-4 rounded-lg bg-surface-secondary border border-border text-text-tertiary flex items-center text-sm cursor-not-allowed">
            {data.email}
          </div>
        </div>

        {/* College */}
        <div className="space-y-1.5">
          <label htmlFor="settings-college" className="block text-sm font-medium text-text-secondary">
            College / University
          </label>
          <input
            id="settings-college"
            type="text"
            value={data.college}
            onChange={(e) => onChange({ ...data, college: e.target.value })}
            placeholder="e.g. ARIA University"
            className="w-full h-11 px-4 rounded-lg bg-surface-secondary border border-border text-text-primary placeholder:text-text-tertiary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:border-transparent text-sm"
          />
        </div>

        {/* Year */}
        <div className="space-y-1.5">
          <label htmlFor="settings-year" className="block text-sm font-medium text-text-secondary">
            Year of Study
          </label>
          <select
            id="settings-year"
            value={data.year}
            onChange={(e) => onChange({ ...data, year: Number(e.target.value) })}
            className="w-full h-11 px-4 rounded-lg bg-surface-secondary border border-border text-text-primary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:border-transparent text-sm appearance-none cursor-pointer"
          >
            {[1, 2, 3, 4, 5].map((y) => (
              <option key={y} value={y}>Year {y}</option>
            ))}
          </select>
        </div>

        {/* Bio */}
        <div className="space-y-1.5">
          <label htmlFor="settings-bio" className="block text-sm font-medium text-text-secondary">
            Bio
          </label>
          <textarea
            id="settings-bio"
            value={data.bio}
            onChange={(e) => onChange({ ...data, bio: e.target.value })}
            rows={3}
            maxLength={500}
            placeholder="A short bio about yourself..."
            className="w-full resize-none px-4 py-3 rounded-lg bg-surface-secondary border border-border text-text-primary placeholder:text-text-tertiary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:border-transparent text-sm"
          />
          <p className="text-xs text-text-tertiary text-right">{data.bio.length}/500</p>
        </div>

        <div className="pt-2">
          <Button
            variant="primary"
            size="sm"
            icon={<Save size={14} />}
            onClick={handleSave}
          >
            {saved ? 'Saved!' : 'Save Profile'}
          </Button>
        </div>
      </CardContent>
    </SectionCard>
  )
}

function AISection({
  data,
  onChange,
}: {
  data: AISettings
  onChange: (d: AISettings) => void
}): JSX.Element {
  return (
    <SectionCard>
      <CardHeader className="px-6 pt-6 pb-0">
        <CardTitle className="font-display text-lg">AI & Personalization</CardTitle>
        <CardDescription>Configure how ARIA&apos;s AI agents operate</CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        {/* Model Selection */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-text-secondary">AI Model</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              {
                id: 'ollama' as const,
                label: 'Ollama (Local)',
                desc: 'Free, private, runs on your machine. Recommended.',
                icon: Cpu,
              },
              {
                id: 'claude' as const,
                label: 'Claude AI (Cloud)',
                desc: 'Cloud-powered Claude Sonnet. More capable but costs $.',
                icon: Cloud,
              },
            ].map((option) => {
              const active = data.model === option.id
              const Icon = option.icon
              return (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => onChange({ ...data, model: option.id })}
                  className={cn(
                    'relative flex flex-col gap-2 p-4 rounded-xl border text-left transition-all duration-200',
                    active
                      ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5 shadow-glow-sm'
                      : 'border-border bg-surface-secondary hover:border-[var(--border-light)]',
                  )}
                  aria-pressed={active}
                  aria-label={`Select ${option.label}`}
                >
                  {active && (
                    <span className="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded-full bg-[var(--accent-primary)]">
                      <Check size={12} className="text-white" />
                    </span>
                  )}
                  <Icon
                    size={22}
                    className={cn(
                      'shrink-0',
                      active ? 'text-[var(--accent-primary)]' : 'text-text-tertiary',
                    )}
                    aria-hidden="true"
                  />
                  <div>
                    <p className="text-sm font-medium text-text-primary">{option.label}</p>
                    <p className="text-xs text-text-tertiary mt-0.5">{option.desc}</p>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Temperature */}
        <SliderInput
          id="settings-temperature"
          label="Creativity (Temperature)"
          value={data.temperature}
          onChange={(v) => onChange({ ...data, temperature: v })}
          min={0}
          max={100}
          marks={[
            { value: 0, label: 'Conservative' },
            { value: 50, label: 'Balanced' },
            { value: 100, label: 'Creative' },
          ]}
        />

        {/* Briefing Time */}
        <div className="space-y-1.5">
          <label htmlFor="settings-briefing-time" className="block text-sm font-medium text-text-secondary">
            Daily Briefing Time
          </label>
          <div className="relative w-full max-w-[200px]">
            <Clock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary pointer-events-none" />
            <input
              id="settings-briefing-time"
              type="time"
              value={data.briefingTime}
              onChange={(e) => onChange({ ...data, briefingTime: e.target.value })}
              className="w-full h-11 pl-9 pr-4 rounded-lg bg-surface-secondary border border-border text-text-primary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:border-transparent text-sm"
            />
          </div>
        </div>

        {/* Agent Toggles */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-text-secondary">Active Agents</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {AGENTS.map((agent) => {
              const checked = data.agentToggles[agent.id] ?? true
              const Icon = agent.Icon
              return (
                <div
                  key={agent.id}
                  className={cn(
                    'flex items-center justify-between gap-3 p-3 rounded-lg border transition-all duration-200',
                    checked
                      ? 'border-[var(--border-light)] bg-surface-secondary'
                      : 'border-border bg-transparent opacity-60',
                  )}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={cn(
                        'flex h-8 w-8 shrink-0 items-center justify-center rounded-lg',
                        checked
                          ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]'
                          : 'bg-[var(--surface-tertiary)] text-text-tertiary',
                      )}
                    >
                      <Icon size={15} aria-hidden="true" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-text-primary truncate">{agent.name}</p>
                      <p className="text-xs text-text-tertiary truncate">{agent.description}</p>
                    </div>
                  </div>
                  <ToggleSwitch
                    id={`agent-${agent.id}`}
                    checked={checked}
                    onChange={(v) =>
                      onChange({
                        ...data,
                        agentToggles: { ...data.agentToggles, [agent.id]: v },
                      })
                    }
                    label={`Toggle ${agent.name} agent`}
                  />
                </div>
              )
            })}
          </div>
        </div>
      </CardContent>
    </SectionCard>
  )
}

function NotificationsSection({
  data,
  onChange,
}: {
  data: NotificationSettings
  onChange: (d: NotificationSettings) => void
}): JSX.Element {
  const categories: { key: keyof Omit<NotificationSettings, 'priorityThreshold'>; label: string; description: string; Icon: LucideIcon }[] = [
    { key: 'task', label: 'Tasks', description: 'Task reminders & deadlines', Icon: Check },
    { key: 'learning', label: 'Learning', description: 'Course & study nudges', Icon: BookOpen },
    { key: 'opportunity', label: 'Opportunities', description: 'New match alerts', Icon: Lightbulb },
    { key: 'goal', label: 'Goals', description: 'Goal progress reminders', Icon: Target },
    { key: 'habit', label: 'Habits', description: 'Habit streak alerts', Icon: Zap },
    { key: 'system', label: 'System', description: 'App updates & maintenance', Icon: Settings },
    { key: 'ai', label: 'AI Insights', description: 'Agent-generated suggestions', Icon: Sparkles },
  ]

  return (
    <SectionCard>
      <CardHeader className="px-6 pt-6 pb-0">
        <div className="flex items-center justify-between w-full">
          <div>
            <CardTitle className="font-display text-lg">Notifications</CardTitle>
            <CardDescription>Control what notifications you receive</CardDescription>
          </div>
          <Button variant="ghost" size="sm" icon={<Bell size={14} />}>
            Mark all as read
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6 space-y-5">
        <div className="space-y-1">
          {categories.map((cat) => {
            const Icon = cat.Icon
            return (
              <SettingRow
                key={cat.key}
                icon={Icon}
                label={cat.label}
                description={cat.description}
              >
                <ToggleSwitch
                  id={`notif-${cat.key}`}
                  checked={data[cat.key]}
                  onChange={(v) => onChange({ ...data, [cat.key]: v })}
                  label={`Toggle ${cat.label} notifications`}
                />
              </SettingRow>
            )
          })}
        </div>

        <div className="pt-2 border-t border-border">
          <SliderInput
            id="settings-priority-threshold"
            label="Minimum Priority for Alerts"
            value={data.priorityThreshold}
            onChange={(v) => onChange({ ...data, priorityThreshold: v })}
            min={0}
            max={4}
            marks={[
              { value: 0, label: 'P0' },
              { value: 1, label: 'P1' },
              { value: 2, label: 'P2' },
              { value: 3, label: 'P3' },
              { value: 4, label: 'P4' },
            ]}
          />
        </div>
      </CardContent>
    </SectionCard>
  )
}

function PrivacySection({
  data,
  onChange,
}: {
  data: PrivacySettings
  onChange: (d: PrivacySettings) => void
}): JSX.Element {
  const [cacheCleared, setCacheCleared] = useState(false)

  const handleClearCache = useCallback(() => {
    setCacheCleared(true)
    setTimeout(() => setCacheCleared(false), 2500)
  }, [])

  return (
    <SectionCard>
      <CardHeader className="px-6 pt-6 pb-0">
        <CardTitle className="font-display text-lg">Privacy & Data</CardTitle>
        <CardDescription>Control your data, privacy, and exports</CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-1">
        <SettingRow
          icon={Shield}
          label="AI Usage Tracking"
          description="Allow ARIA to use your interactions for personalization"
        >
          <ToggleSwitch
            id="privacy-ai-usage"
            checked={data.aiUsage}
            onChange={(v) => onChange({ ...data, aiUsage: v })}
            label="Toggle AI usage tracking"
          />
        </SettingRow>

        <SettingRow
          icon={BarChart3}
          label="Analytics Opt-Out"
          description="Prevent anonymous usage statistics collection"
        >
          <ToggleSwitch
            id="privacy-analytics"
            checked={data.analyticsOptOut}
            onChange={(v) => onChange({ ...data, analyticsOptOut: v })}
            label="Toggle analytics opt-out"
          />
        </SettingRow>

        <SettingRow
          icon={Eye}
          label="Memory Visibility"
          description="Allow agents to access your persistent memory"
        >
          <ToggleSwitch
            id="privacy-memory"
            checked={data.memoryVisibility}
            onChange={(v) => onChange({ ...data, memoryVisibility: v })}
            label="Toggle memory visibility"
          />
        </SettingRow>

        <div className="flex flex-wrap gap-3 pt-4 mt-2 border-t border-border">
          <Button variant="outline" size="sm" icon={<Download size={14} />}>
            Export My Data
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={<Trash2 size={14} />}
            onClick={handleClearCache}
            className="text-[var(--accent-error)] border-[var(--accent-error)]/30 hover:bg-[var(--accent-error)]/10"
          >
            {cacheCleared ? 'Cache Cleared!' : 'Clear Local Cache'}
          </Button>
        </div>
      </CardContent>
    </SectionCard>
  )
}

function AppearanceSection({
  data,
  onChange,
}: {
  data: AppearanceSettings
  onChange: (d: AppearanceSettings) => void
}): JSX.Element {
  const { theme, accent, contrast, setTheme, setAccent, setContrast } = useTheme()
  const fontPreviewRef = useRef<HTMLParagraphElement>(null)

  const accentBgMap: Record<string, string> = {
    indigo: 'bg-[var(--accent-primary)]',
    emerald: 'bg-[var(--accent-secondary)]',
    amber: 'bg-[var(--accent-warning)]',
    rose: 'bg-[var(--accent-error)]',
  }
  const accentBgClass = (a: string) => accentBgMap[a] ?? 'bg-[var(--accent-primary)]'

  const themeOptions: {
    t: 'dark' | 'light'
    a: 'indigo' | 'emerald' | 'amber' | 'rose'
    label: string
    isLight: boolean
  }[] = [
    { t: 'dark', a: 'indigo', label: 'Dark / Indigo', isLight: false },
    { t: 'dark', a: 'emerald', label: 'Dark / Emerald', isLight: false },
    { t: 'dark', a: 'amber', label: 'Dark / Amber', isLight: false },
    { t: 'dark', a: 'rose', label: 'Dark / Rose', isLight: false },
    { t: 'light', a: 'indigo', label: 'Light / Indigo', isLight: true },
    { t: 'light', a: 'emerald', label: 'Light / Emerald', isLight: true },
    { t: 'light', a: 'amber', label: 'Light / Amber', isLight: true },
  ]

  return (
    <SectionCard>
      <CardHeader className="px-6 pt-6 pb-0">
        <CardTitle className="font-display text-lg">Appearance</CardTitle>
        <CardDescription>Customize your visual experience</CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        {/* Theme + Accent Grid */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-text-secondary">Theme & Accent</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {themeOptions.map((opt) => {
              const active = theme === opt.t && accent === opt.a
              return (
                <button
                  key={`${opt.t}-${opt.a}`}
                  type="button"
                  onClick={() => {
                    setTheme(opt.t)
                    setAccent(opt.a)
                  }}
                  className={cn(
                    'flex flex-col items-center gap-2 p-3 rounded-xl border transition-all duration-200',
                    active
                      ? 'border-[var(--accent-primary)] shadow-glow-sm'
                      : 'border-border hover:border-[var(--border-light)]',
                  )}
                  style={{ minWidth: 0, maxWidth: 140 }}
                  aria-pressed={active}
                  aria-label={`${opt.label} theme`}
                >
                  <div
                    className={cn(
                      'w-full aspect-[3/2] rounded-lg overflow-hidden border border-border',
                      opt.isLight ? 'bg-[var(--card)]' : 'bg-[var(--background)]',
                    )}
                  >
                    <div className="flex h-full flex-col p-1.5 gap-1">
                      <div className="flex gap-1">
                        <div className={`h-1.5 w-1.5 rounded-full ${accentBgClass(opt.a)}`} />
                        <div className="h-1.5 w-1.5 rounded-full bg-white/20" />
                        <div className="h-1.5 w-1.5 rounded-full bg-white/20" />
                      </div>
                      <div className={`h-2 rounded-sm ${accentBgClass(opt.a)}`} />
                      <div className="flex gap-1">
                        <div className={`h-3 flex-1 rounded-sm ${opt.isLight ? 'bg-surface-tertiary/30' : 'bg-surface-primary'}`} />
                        <div className={`h-3 w-1 rounded-sm ${accentBgClass(opt.a)}`} />
                      </div>
                    </div>
                  </div>
                  <span
                    className={cn(
                      'text-xs truncate w-full text-center',
                      active ? 'text-[var(--accent-primary)] font-medium' : 'text-text-tertiary',
                    )}
                  >
                    {opt.t === 'dark' ? <Moon size={10} className="inline mr-1" aria-hidden="true" /> : <Sun size={10} className="inline mr-1" aria-hidden="true" />}
                    {opt.a.charAt(0).toUpperCase() + opt.a.slice(1)}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Contrast */}
        <SettingRow
          icon={Eye}
          label="High Contrast Mode"
          description="Increase contrast for better readability"
        >
          <ToggleSwitch
            id="settings-high-contrast"
            checked={contrast === 'high'}
            onChange={(v) => setContrast(v ? 'high' : 'normal')}
            label="Toggle high contrast"
          />
        </SettingRow>

        {/* Sidebar Mode */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-text-secondary">Sidebar Style</p>
          <div className="grid grid-cols-3 gap-3">
            {([
              { value: 'default' as const, label: 'Default', icon: Monitor },
              { value: 'compact' as const, label: 'Compact', icon: Zap },
              { value: 'icons' as const, label: 'Icons Only', icon: Eye },
            ]).map((opt) => {
              const active = data.sidebarMode === opt.value
              const Icon = opt.icon
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => onChange({ ...data, sidebarMode: opt.value })}
                  className={cn(
                    'flex flex-col items-center gap-2 py-4 px-3 rounded-xl border transition-all duration-200',
                    active
                      ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5 shadow-glow-sm'
                      : 'border-border bg-surface-secondary hover:border-[var(--border-light)]',
                  )}
                  aria-pressed={active}
                  aria-label={`${opt.label} sidebar`}
                >
                  <Icon
                    size={20}
                    className={active ? 'text-[var(--accent-primary)]' : 'text-text-tertiary'}
                    aria-hidden="true"
                  />
                  <span
                    className={cn(
                      'text-xs',
                      active ? 'text-[var(--accent-primary)] font-medium' : 'text-text-tertiary',
                    )}
                  >
                    {opt.label}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Font Size */}
        <SliderInput
          id="settings-font-size"
          label="Font Size"
          value={data.fontSize}
          onChange={(v) => onChange({ ...data, fontSize: v })}
          min={12}
          max={20}
          marks={[
            { value: 12, label: 'A' },
            { value: 16, label: 'A' },
            { value: 20, label: 'A' },
          ]}
        />

        {/* Font Size Preview */}
        <div className="p-4 rounded-lg bg-surface-secondary border border-border">
          <p
            ref={fontPreviewRef}
            className="text-text-primary transition-all duration-200"
            style={{ fontSize: `${data.fontSize}px` }}
          >
            The quick brown fox jumps over the lazy dog. ARIA is ready.
          </p>
        </div>

        {/* Reduced Motion */}
        <SettingRow
          icon={RefreshCw}
          label="Reduced Motion"
          description="Minimize animations and transitions"
        >
          <ToggleSwitch
            id="settings-reduced-motion"
            checked={data.reducedMotion}
            onChange={(v) => onChange({ ...data, reducedMotion: v })}
            label="Toggle reduced motion"
          />
        </SettingRow>

        {/* Compact Mode */}
        <SettingRow
          icon={Zap}
          label="Compact Mode"
          description="Reduce spacing for a denser interface"
        >
          <ToggleSwitch
            id="settings-compact"
            checked={data.compactMode}
            onChange={(v) => onChange({ ...data, compactMode: v })}
            label="Toggle compact mode"
          />
        </SettingRow>
      </CardContent>
    </SectionCard>
  )
}

function SystemSection({ info }: { info: SystemInfo }): JSX.Element {
  const STORAGE_PCT = 34.2 // 342 MB / 1 GB

  const integrationIcons: Record<string, LucideIcon> = {
    database: Cloud,
    bot: Cpu,
    sparkles: Sparkles,
    github: Github,
    calendar: Clock,
    mail: Bell,
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-[var(--accent-success)]'
      case 'disconnected': return 'bg-[var(--accent-warning)]'
      case 'error': return 'bg-[var(--accent-error)]'
      default: return 'bg-[var(--surface-tertiary)]'
    }
  }

  const statusBadgeVariant = (status: string) => {
    switch (status) {
      case 'connected': return 'success' as const
      case 'disconnected': return 'warning' as const
      case 'error': return 'error' as const
      default: return 'outline' as const
    }
  }

  return (
    <SectionCard>
      <CardHeader className="px-6 pt-6 pb-0">
        <CardTitle className="font-display text-lg">System</CardTitle>
        <CardDescription>System information and integration status</CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        {/* Storage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-text-secondary">Storage</p>
            <p className="text-xs text-text-tertiary font-mono">
              {info.storageUsed} / {info.storageTotal}
            </p>
          </div>
          <div className="h-2 rounded-full bg-[var(--surface-tertiary)] overflow-hidden">
            <div
              className="h-full rounded-full bg-[var(--accent-primary)] transition-all duration-500"
              style={{ width: `${STORAGE_PCT}%` }}
            />
          </div>
        </div>

        {/* Integrations */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-text-secondary">Integrations</p>
          <div className="space-y-1">
            {info.integrations.map((int) => {
              const Icon = integrationIcons[int.icon] ?? Cloud
              return (
                <SettingRow key={int.name} icon={Icon} label={int.name}>
                  <div className="flex items-center gap-2">
                    <span className={cn('h-2 w-2 rounded-full', statusColor(int.status))} />
                    <Badge variant={statusBadgeVariant(int.status)} className="capitalize">
                      {int.status}
                    </Badge>
                  </div>
                </SettingRow>
              )
            })}
          </div>
        </div>

        {/* About */}
        <div className="p-4 rounded-lg bg-surface-secondary border border-border space-y-2">
          <p className="text-sm font-medium text-text-primary">About ARIA OS</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <span className="text-text-tertiary">Version</span>
            <span className="text-text-primary font-mono">{info.version}</span>
            <span className="text-text-tertiary">Build Date</span>
            <span className="text-text-primary font-mono">{info.buildDate}</span>
            <span className="text-text-tertiary">Tech Stack</span>
            <span className="text-text-primary">Next.js 14, FastAPI, Supabase</span>
            <span className="text-text-tertiary">AI Engine</span>
            <span className="text-text-primary">Ollama / Claude API</span>
          </div>
        </div>
      </CardContent>
    </SectionCard>
  )
}

/* ──────── Main Settings Page ──────── */

export function SettingsPage(): JSX.Element {
  const [activeTab, setActiveTab] = useState('profile')
  const [profile, setProfile] = useState<UserProfileData>(DEFAULT_PROFILE)
  const [ai, setAi] = useState<AISettings>(DEFAULT_AI)
  const [notifications, setNotifications] = useState<NotificationSettings>(DEFAULT_NOTIFICATIONS)
  const [privacy, setPrivacy] = useState<PrivacySettings>(DEFAULT_PRIVACY)
  const [appearance, setAppearance] = useState<AppearanceSettings>(DEFAULT_APPEARANCE)
  const [system] = useState<SystemInfo>(DEFAULT_SYSTEM_INFO)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setProfile(loadFromStorage(STORAGE_KEYS.profile, DEFAULT_PROFILE))
    setAi(loadFromStorage(STORAGE_KEYS.ai, DEFAULT_AI))
    setNotifications(loadFromStorage(STORAGE_KEYS.notifications, DEFAULT_NOTIFICATIONS))
    setPrivacy(loadFromStorage(STORAGE_KEYS.privacy, DEFAULT_PRIVACY))
    setAppearance(loadFromStorage(STORAGE_KEYS.appearance, DEFAULT_APPEARANCE))
    setMounted(true)
  }, [])

  useEffect(() => { if (mounted) saveToStorage(STORAGE_KEYS.ai, ai) }, [ai, mounted])
  useEffect(() => { if (mounted) saveToStorage(STORAGE_KEYS.notifications, notifications) }, [notifications, mounted])
  useEffect(() => { if (mounted) saveToStorage(STORAGE_KEYS.privacy, privacy) }, [privacy, mounted])
  useEffect(() => { if (mounted) saveToStorage(STORAGE_KEYS.appearance, appearance) }, [appearance, mounted])

  const variants = {
    enter: { opacity: 0, y: 8 },
    center: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -8 },
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Sidebar Navigation */}
      <nav className="flex lg:flex-col gap-1 shrink-0 overflow-x-auto lg:overflow-visible pb-2 lg:pb-0 lg:w-52 scrollbar-none" aria-label="Settings sections">
        {TABS.map((tab) => {
          const Icon = tab.Icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm whitespace-nowrap transition-all duration-200 shrink-0',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background)]',
                isActive
                  ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] font-medium shadow-glow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-secondary',
              )}
              aria-current={isActive ? 'page' : undefined}
              aria-label={`${tab.label} settings`}
            >
              <Icon size={16} aria-hidden="true" />
              <span className="hidden lg:inline truncate">{tab.label}</span>
            </button>
          )
        })}
      </nav>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.2, ease: 'easeOut' }}
          >
            {activeTab === 'profile' && (
              <ProfileSection
                data={profile}
                onChange={(d) => { setProfile(d); saveToStorage(STORAGE_KEYS.profile, d) }}
              />
            )}
            {activeTab === 'ai' && <AISection data={ai} onChange={setAi} />}
            {activeTab === 'notifications' && (
              <NotificationsSection data={notifications} onChange={setNotifications} />
            )}
            {activeTab === 'privacy' && <PrivacySection data={privacy} onChange={setPrivacy} />}
            {activeTab === 'appearance' && (
              <AppearanceSection data={appearance} onChange={setAppearance} />
            )}
            {activeTab === 'system' && <SystemSection info={system} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
