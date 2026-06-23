export interface ParsedCommand {
  type: 'create_task' | 'complete_task' | 'navigate' | 'query' | 'schedule' | 'unknown'
  confidence: number
  task?: {
    title: string
    dueDate?: string
    priority?: 'low' | 'medium' | 'high'
    estimatedMinutes?: number
    recurrence?: string
    tags?: string[]
  }
  navigation?: string
  query?: {
    entity?: string
    timeframe?: string
    intent?: string
  }
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
  if (/\b(tonight|this evening)\b/i.test(text)) return today
  if (/\b(this\s+)?weekend\b/i.test(text)) {
    const saturday = new Date(now)
    saturday.setDate(saturday.getDate() + ((6 - saturday.getDay() + 7) % 7))
    return saturday.toISOString().split('T')[0]
  }

  for (const [name, dayIndex] of Object.entries(dayNames)) {
    if (new RegExp(`\\b${name}\\b`, 'i').test(text)) {
      const isNext = /\bnext\b/i.test(text)
      const target = new Date(now)
      const daysUntil = ((dayIndex - target.getDay() + 7) % 7) || (isNext ? 7 : 0)
      target.setDate(target.getDate() + daysUntil + (isNext && daysUntil === 0 ? 7 : 0))
      return target.toISOString().split('T')[0]
    }
  }

  const dateMatch = text.match(/\b(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?\b/)
  if (dateMatch) {
    const [, m, d, y] = dateMatch
    const year = y ? (y.length === 2 ? `20${y}` : y) : String(now.getFullYear())
    return `${year}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`
  }

  const nextPatterns = [
    { pattern: /\bnext\s+week\b/i, days: 7 },
    { pattern: /\bnext\s+month\b/i, days: 30 },
    { pattern: /\b(in\s+)?a\s+week\b/i, days: 7 },
    { pattern: /\b(in\s+)?a\s+month\b/i, days: 30 },
  ]
  for (const { pattern, days } of nextPatterns) {
    if (pattern.test(text)) {
      const target = new Date(now)
      target.setDate(target.getDate() + days)
      return target.toISOString().split('T')[0]
    }
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

function extractRecurrence(text: string): string | undefined {
  const patterns: Array<[RegExp, string]> = [
    [/\b(every|each)\s+day\b/i, 'daily'],
    [/\b(every|each)\s+week\b/i, 'weekly'],
    [/\b(every|each)\s+month\b/i, 'monthly'],
    [/\b(every|each)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/i, 'weekly'],
    [/\b(weekdays|week days|every weekday)\b/i, 'weekdays'],
    [/\b(daily|everyday|every day)\b/i, 'daily'],
    [/\b(weekly|every week)\b/i, 'weekly'],
    [/\b(monthly|every month)\b/i, 'monthly'],
  ]
  for (const [pattern, value] of patterns) {
    if (pattern.test(text)) return value
  }
  return undefined
}

function extractPriority(text: string): 'low' | 'medium' | 'high' | undefined {
  if (/\b(urgent|critical|asap|high priority|important|p0|p1)\b/i.test(text)) return 'high'
  if (/\b(low priority|whenever|someday|optional|p3|p4)\b/i.test(text)) return 'low'
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

function extractTags(text: string): string[] | undefined {
  const tags: string[] = []
  const tagRe = /#(\w+)/g
  let m: RegExpExecArray | null
  while ((m = tagRe.exec(text)) !== null) tags.push(m[1].toLowerCase())
  const ctxRe = /@(\w+)/g
  while ((m = ctxRe.exec(text)) !== null) tags.push(m[1].toLowerCase())
  return tags.length > 0 ? tags : undefined
}

function removePrefix(text: string, prefixes: string[]): string {
  let result = text.trim()
  for (const prefix of prefixes) {
    const regex = new RegExp(`^${prefix}\\s+`, 'i')
    result = result.replace(regex, '').trim()
  }
  return result
}

function extractQueryEntity(text: string): { entity?: string; timeframe?: string; intent?: string } {
  const lower = text.toLowerCase()

  const entityPatterns: Array<[RegExp, string]> = [
    [/\b(tasks?|to-do|todo|todos)\b/, 'task'],
    [/\b(habits?)\b/, 'habit'],
    [/\b(habit streak)\b/, 'habit'],
    [/\b(sleep|bedtime)\b/, 'sleep'],
    [/\b(courses?|class|classes|subject)\b/, 'course'],
    [/\b(goals?)\b/, 'goal'],
    [/\b(projects?)\b/, 'project'],
    [/\b(ideas?)\b/, 'idea'],
    [/\b(income|earnings?)\b/, 'income'],
    [/\b(time|timesheet)\b/, 'time'],
    [/\b(resources?)\b/, 'resource'],
    [/\b(opportunit(y|ies))\b/, 'opportunity'],
    [/\b(memory|memories)\b/, 'memory'],
  ]

  let entity: string | undefined
  for (const [pattern, name] of entityPatterns) {
    if (pattern.test(lower)) { entity = name; break }
  }

  const timeframePatterns: Array<[RegExp, string]> = [
    [/\b(today)\b/, 'today'],
    [/\b(tomorrow)\b/, 'tomorrow'],
    [/\b(this week)\b/, 'this_week'],
    [/\b(next week)\b/, 'next_week'],
    [/\b(this month)\b/, 'this_month'],
    [/\b(overdue|over due|past due)\b/, 'overdue'],
    [/\b(upcoming)\b/, 'upcoming'],
  ]

  let timeframe: string | undefined
  for (const [pattern, name] of timeframePatterns) {
    if (pattern.test(lower)) { timeframe = name; break }
  }

  const intentPatterns: Array<[RegExp, string]> = [
    [/\b(count|how many|total)\b/, 'count'],
    [/\b(list|show|what are|what's)\b/, 'list'],
    [/\b(summary|overview|status)\b/, 'summary'],
    [/\b(due|deadline)\b/, 'due'],
    [/\b(trend|progress|improving|declining)\b/, 'trend'],
  ]

  let intent: string | undefined
  for (const [pattern, name] of intentPatterns) {
    if (pattern.test(lower)) { intent = name; break }
  }

  return { entity, timeframe, intent }
}

const QUERY_TRIGGERS = [
  /^(what|how|when|where|why|who|show|list|display|tell\s+me|give\s+me)\b/i,
  /^(are\s+there|is\s+there|do\s+I|does\s+my)\b/i,
  /^(count|summarize|check)\b/i,
]

export function parseCommand(text: string): ParsedCommand {
  const trimmed = text.trim()
  const lower = trimmed.toLowerCase()

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
        recurrence: extractRecurrence(title),
        tags: extractTags(title),
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

  if (lower.startsWith('/complete ') || lower.startsWith('/done ')) {
    const title = removePrefix(trimmed, ['/complete', '/done'])
    if (!title) return { type: 'unknown', confidence: 0, raw: trimmed }
    return {
      type: 'complete_task',
      confidence: 0.85,
      task: { title },
      raw: trimmed,
    }
  }

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
          recurrence: extractRecurrence(trimmed),
          tags: extractTags(trimmed),
        },
        raw: trimmed,
      }
    }
  }

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

  const navPatterns = [/^(go\s+to|open|show|take\s+me\s+to)\s+(.+)/i]
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

  for (const trigger of QUERY_TRIGGERS) {
    if (trigger.test(trimmed)) {
      return {
        type: 'query',
        confidence: 0.65,
        query: extractQueryEntity(trimmed),
        raw: trimmed,
      }
    }
  }

  return { type: 'unknown', confidence: 0.2, raw: trimmed }
}

const ROUTE_ALIASES: Record<string, string> = {
  dashboard: '/dashboard',
  tasks: '/dashboard/tasks',
  'task list': '/dashboard/tasks',
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
  'knowledge graph': '/dashboard/knowledge',
  roadmap: '/dashboard/roadmap',
  settings: '/dashboard/settings',
  analytics: '/dashboard/analytics',
  'youtube vault': '/dashboard/youtube-vault',
  'focus mode': '/dashboard/focus',
  automation: '/dashboard/automation',
  review: '/dashboard/review',
  briefing: '/dashboard/briefing',
  academics: '/dashboard/academics',
  'daily briefing': '/dashboard/briefing',
  'weekly review': '/dashboard/review',
}

export function resolveNavigation(nav: string): string | undefined {
  const key = nav.toLowerCase().trim()
  if (ROUTE_ALIASES[key]) return ROUTE_ALIASES[key]
  for (const [alias, route] of Object.entries(ROUTE_ALIASES)) {
    if (key.includes(alias) || alias.includes(key)) return route
  }
  return undefined
}
