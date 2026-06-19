export interface ParsedCommand {
  type: 'create_task' | 'complete_task' | 'navigate' | 'query' | 'schedule' | 'unknown'
  confidence: number
  task?: {
    title: string
    dueDate?: string
    priority?: 'low' | 'medium' | 'high'
    estimatedMinutes?: number
  }
  navigation?: string
  query?: string
  raw: string
}

function extractDate(text: string): string | undefined {
  const now = new Date()
  const today = now.toISOString().split('T')[0]

  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowStr = tomorrow.toISOString().split('T')[0]

  const dayNames: Record<string, number> = {
    sunday: 0, monday: 1, tuesday: 2, wednesday: 3, thursday: 4, friday: 5, saturday: 6,
    sun: 0, mon: 1, tue: 2, wed: 3, thu: 4, fri: 5, sat: 6,
  }

  if (/\btoday\b/i.test(text)) return today
  if (/\btomorrow\b/i.test(text)) return tomorrowStr

  for (const [name, dayIndex] of Object.entries(dayNames)) {
    if (new RegExp(`\\b${name}\\b`, 'i').test(text)) {
      const target = new Date(now)
      target.setDate(target.getDate() + ((dayIndex - target.getDay() + 7) % 7))
      return target.toISOString().split('T')[0]
    }
  }

  const dateMatch = text.match(/\b(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?\b/)
  if (dateMatch) {
    const [, m, d, y] = dateMatch
    const year = y ? (y.length === 2 ? `20${y}` : y) : String(now.getFullYear())
    return `${year}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`
  }

  const relMatch = text.match(/\b(in\s+(\d+)\s+(day|days|week|weeks))\b/i)
  if (relMatch) {
    const num = parseInt(relMatch[2])
    const unit = relMatch[3].toLowerCase()
    const target = new Date(now)
    if (unit.startsWith('week')) target.setDate(target.getDate() + num * 7)
    else target.setDate(target.getDate() + num)
    return target.toISOString().split('T')[0]
  }

  return undefined
}

function extractPriority(text: string): 'low' | 'medium' | 'high' | undefined {
  if (/\b(urgent|critical|asap|high priority|important)\b/i.test(text)) return 'high'
  if (/\b(low priority|whenever|someday|optional)\b/i.test(text)) return 'low'
  return undefined
}

function extractMinutes(text: string): number | undefined {
  const match = text.match(/\b(\d+)\s*(min|minute|minutes|hour|hours|hr|hrs)\b/i)
  if (!match) return undefined
  const num = parseInt(match[1])
  const unit = match[2].toLowerCase()
  if (unit.startsWith('hour') || unit.startsWith('hr')) return num * 60
  return num
}

function removePrefix(text: string, prefixes: string[]): string {
  let result = text.trim()
  for (const prefix of prefixes) {
    const regex = new RegExp(`^${prefix}\\s+`, 'i')
    result = result.replace(regex, '').trim()
  }
  return result
}

export function parseCommand(text: string): ParsedCommand {
  const trimmed = text.trim()
  const lower = trimmed.toLowerCase()

  // Slash command
  if (lower.startsWith('/new task')) {
    const title = removePrefix(trimmed, ['/new task'])
    if (!title) return { type: 'unknown', confidence: 0, raw: trimmed }
    return {
      type: 'create_task',
      confidence: 0.9,
      task: {
        title,
        dueDate: extractDate(title),
        priority: extractPriority(title),
        estimatedMinutes: extractMinutes(title),
      },
      raw: trimmed,
    }
  }

  if (lower.startsWith('/go ') || lower.startsWith('/navigate ')) {
    const dest = removePrefix(trimmed, ['/go', '/navigate'])
    return {
      type: 'navigate',
      confidence: 0.95,
      navigation: dest.toLowerCase(),
      raw: trimmed,
    }
  }

  // Natural language: "create task ...", "add task ...", "new task ..."
  const createPatterns = [
    /^(create|add|make)\s+(a\s+)?(task|todo|to-do)\s+(?:to\s+)?(.+)/i,
    /^remind\s+me\s+(?:to\s+)?(.+)/i,
    /^(i\s+)?need\s+to\s+(.+)/i,
    /^(schedule|plan)\s+(.+)/i,
  ]

  for (const pattern of createPatterns) {
    const match = trimmed.match(pattern)
    if (match) {
      const title = match[match.length - 1].trim()
      if (title.length < 2) continue
      return {
        type: 'create_task',
        confidence: 0.85,
        task: {
          title,
          dueDate: extractDate(trimmed),
          priority: extractPriority(trimmed),
          estimatedMinutes: extractMinutes(trimmed),
        },
        raw: trimmed,
      }
    }
  }

  // "mark ... as done/complete"
  const donePattern = /^(mark|set)\s+(.+?)\s+(as\s+)?(done|completed|complete)/i
  const doneMatch = trimmed.match(donePattern)
  if (doneMatch) {
    return {
      type: 'complete_task',
      confidence: 0.7,
      task: { title: doneMatch[2].trim() },
      raw: trimmed,
    }
  }

  // Navigation: "go to ...", "open ...", "show ..."
  const navPatterns = [
    /^(go\s+to|open|show|take\s+me\s+to)\s+(.+)/i,
  ]
  for (const pattern of navPatterns) {
    const match = trimmed.match(pattern)
    if (match) {
      return {
        type: 'navigate',
        confidence: 0.8,
        navigation: match[2].trim().toLowerCase(),
        raw: trimmed,
      }
    }
  }

  return { type: 'unknown', confidence: 0.2, raw: trimmed }
}

const ROUTE_ALIASES: Record<string, string> = {
  dashboard: '/dashboard',
  tasks: '/dashboard/tasks',
  habits: '/dashboard/habits',
  sleep: '/dashboard/sleep',
  courses: '/dashboard/courses',
  goals: '/dashboard/goals',
  chat: '/dashboard/chat',
  projects: '/dashboard/projects',
  ideas: '/dashboard/ideas',
  'time tracking': '/dashboard/time',
  time: '/dashboard/time',
  income: '/dashboard/income',
  resources: '/dashboard/resources',
  opportunities: '/dashboard/opportunities',
  memory: '/dashboard/memory',
  knowledge: '/dashboard/knowledge',
  roadmap: '/dashboard/roadmap',
  settings: '/dashboard/settings',
  analytics: '/dashboard/analytics',
  'youtube vault': '/dashboard/youtube-vault',
  'focus mode': '/dashboard/focus',
  automation: '/dashboard/automation',
  review: '/dashboard/review',
  briefing: '/dashboard/briefing',
  academics: '/dashboard/academics',
}

export function resolveNavigation(nav: string): string | undefined {
  const key = nav.toLowerCase().trim()
  if (ROUTE_ALIASES[key]) return ROUTE_ALIASES[key]
  for (const [alias, route] of Object.entries(ROUTE_ALIASES)) {
    if (key.includes(alias) || alias.includes(key)) return route
  }
  return undefined
}
