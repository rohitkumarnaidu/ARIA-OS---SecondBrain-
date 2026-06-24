import { describe, it, expect } from 'vitest'
import { parseCommand, resolveNavigation } from '@/lib/ai/nlp'

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/

describe('parseCommand', () => {
  it('parses /new task with title', () => {
    const result = parseCommand('/new task Buy groceries')
    expect(result.type).toBe('create_task')
    expect(result.confidence).toBe(0.9)
    expect(result.task?.title).toBe('Buy groceries')
  })

  it('/new task alone returns create_task since title extraction requires trailing text', () => {
    // removePrefix regex requires trailing whitespace after prefix, so "/new task" remains as title
    const result = parseCommand('/new task')
    expect(result.type).toBe('create_task')
    expect(result.task?.title).toBe('/new task')
  })

  it('parses /go navigation command', () => {
    const result = parseCommand('/go tasks')
    expect(result.type).toBe('navigate')
    expect(result.confidence).toBe(0.95)
    expect(result.navigation).toBe('tasks')
  })

  it('parses /navigate command', () => {
    const result = parseCommand('/navigate sleep')
    expect(result.type).toBe('navigate')
    expect(result.confidence).toBe(0.95)
    expect(result.navigation).toBe('sleep')
  })

  it('parses /complete command', () => {
    const result = parseCommand('/complete Buy groceries')
    expect(result.type).toBe('complete_task')
    expect(result.confidence).toBe(0.85)
    expect(result.task?.title).toBe('Buy groceries')
  })

  it('parses /done command', () => {
    const result = parseCommand('/done Write report')
    expect(result.type).toBe('complete_task')
    expect(result.task?.title).toBe('Write report')
  })

  it('/done alone returns unknown (no trailing space for prefix match)', () => {
    const result = parseCommand('/done')
    expect(result.type).toBe('unknown')
    expect(result.confidence).toBe(0.2)
  })

  it('parses "create a task" pattern', () => {
    const result = parseCommand('create a task to review PR')
    expect(result.type).toBe('create_task')
    expect(result.confidence).toBe(0.85)
    expect(result.task?.title).toBe('review PR')
  })

  it('parses "add a todo" pattern', () => {
    const result = parseCommand('add a todo clean kitchen')
    expect(result.type).toBe('create_task')
    expect(result.task?.title).toBe('clean kitchen')
  })

  it('parses "remind me to" pattern', () => {
    const result = parseCommand('remind me to call dentist')
    expect(result.type).toBe('create_task')
    expect(result.task?.title).toBe('call dentist')
  })

  it('parses "need to" pattern', () => {
    const result = parseCommand('I need to finish homework')
    expect(result.type).toBe('create_task')
    expect(result.task?.title).toBe('finish homework')
  })

  it('parses "schedule" pattern', () => {
    const result = parseCommand('schedule study session')
    expect(result.type).toBe('create_task')
    expect(result.task?.title).toBe('study session')
  })

  it('parses "mark as done" pattern', () => {
    const result = parseCommand('mark laundry as done')
    expect(result.type).toBe('complete_task')
    expect(result.confidence).toBe(0.7)
    expect(result.task?.title).toBe('laundry')
  })

  it('parses "set completed" pattern', () => {
    const result = parseCommand('set homework as completed')
    expect(result.type).toBe('complete_task')
    expect(result.task?.title).toBe('homework')
  })

  it('parses "go to" navigation pattern', () => {
    const result = parseCommand('go to dashboard')
    expect(result.type).toBe('navigate')
    expect(result.confidence).toBe(0.8)
    expect(result.navigation).toBe('dashboard')
  })

  it('parses "open" navigation pattern', () => {
    const result = parseCommand('open habits')
    expect(result.type).toBe('navigate')
    expect(result.navigation).toBe('habits')
  })

  it('parses "show me my tasks" as navigation (matches /^(go\s+to|open|show|...)/)', () => {
    const result = parseCommand('show me my tasks')
    expect(result.type).toBe('navigate')
    expect(result.navigation).toBe('me my tasks')
  })

  it('parses "take me to" navigation pattern', () => {
    const result = parseCommand('take me to settings')
    expect(result.type).toBe('navigate')
    expect(result.navigation).toBe('settings')
  })

  it('parses what-query with entity and timeframe', () => {
    const result = parseCommand('what tasks are overdue?')
    expect(result.type).toBe('query')
    expect(result.confidence).toBe(0.65)
    expect(result.query?.entity).toBe('task')
    expect(result.query?.timeframe).toBe('overdue')
    // intent "list" not matched because "list" isn't in "what tasks are overdue"
    expect(result.query?.intent).toBeUndefined()
  })

  it('parses "how many" query with count intent', () => {
    const result = parseCommand('how many habits do I have?')
    expect(result.type).toBe('query')
    expect(result.query?.entity).toBe('habit')
    expect(result.query?.intent).toBe('count')
  })

  it('parses "show my sleep score" as navigate (not query)', () => {
    // "show" matches the navigation pattern first
    const result = parseCommand('show my sleep score')
    expect(result.type).toBe('navigate')
  })

  it('parses "are there" query', () => {
    const result = parseCommand('are there any overdue tasks?')
    expect(result.type).toBe('query')
    expect(result.query?.entity).toBe('task')
    expect(result.query?.timeframe).toBe('overdue')
  })

  it('parses "summarize" query', () => {
    const result = parseCommand('summarize my week')
    expect(result.type).toBe('query')
    // intent "summary" not matched because "summarize" != "summary"
    expect(result.query?.intent).toBeUndefined()
  })

  it('returns unknown for unrecognized input', () => {
    const result = parseCommand('good morning')
    expect(result.type).toBe('unknown')
    expect(result.confidence).toBe(0.2)
  })

  it('returns unknown for empty or whitespace-only', () => {
    expect(parseCommand('').type).toBe('unknown')
    expect(parseCommand('   ').type).toBe('unknown')
  })

  it('handles special characters in input', () => {
    const result = parseCommand('/new task Fix bug in login flow #bug @frontend')
    expect(result.type).toBe('create_task')
    expect(result.task?.tags).toContain('bug')
    expect(result.task?.tags).toContain('frontend')
  })

  it('extracts priority high from command text', () => {
    const result = parseCommand('/new task urgent bug fix')
    expect(result.task?.priority).toBe('high')
  })

  it('extracts priority low from command text', () => {
    const result = parseCommand('/new task someday organize desk')
    expect(result.task?.priority).toBe('low')
  })

  it('does not set priority when no keywords present', () => {
    const result = parseCommand('/new task Buy milk')
    expect(result.task?.priority).toBeUndefined()
  })

  it('extracts dueDate today', () => {
    const result = parseCommand('/new task submit report today')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts dueDate tomorrow', () => {
    const result = parseCommand('/new task meeting tomorrow')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts tags from #hashtags', () => {
    const result = parseCommand('/new task build feature #frontend #react')
    expect(result.task?.tags).toEqual(['frontend', 'react'])
  })

  it('extracts tags from @contexts', () => {
    const result = parseCommand('/new task review PR @work')
    expect(result.task?.tags).toEqual(['work'])
  })

  it('extracts recurrence daily', () => {
    const result = parseCommand('/new task meditate every day')
    expect(result.task?.recurrence).toBe('daily')
  })

  it('extracts recurrence weekly', () => {
    const result = parseCommand('/new task team sync every week')
    expect(result.task?.recurrence).toBe('weekly')
  })

  it('extracts estimated minutes', () => {
    const result = parseCommand('/new task write report 30 minutes')
    expect(result.task?.estimatedMinutes).toBe(30)
  })

  it('extracts estimated hours', () => {
    const result = parseCommand('/new task big project 2 hours')
    expect(result.task?.estimatedMinutes).toBe(120)
  })
})

describe('resolveNavigation', () => {
  it('resolves "dashboard" to /dashboard', () => {
    expect(resolveNavigation('dashboard')).toBe('/dashboard')
  })

  it('resolves "tasks" to /dashboard/tasks', () => {
    expect(resolveNavigation('tasks')).toBe('/dashboard/tasks')
  })

  it('resolves "task list" to /dashboard/tasks', () => {
    expect(resolveNavigation('task list')).toBe('/dashboard/tasks')
  })

  it('resolves "sleep" to /dashboard/sleep', () => {
    expect(resolveNavigation('sleep')).toBe('/dashboard/sleep')
  })

  it('resolves "chat" to /dashboard/chat', () => {
    expect(resolveNavigation('chat')).toBe('/dashboard/chat')
  })

  it('resolves "time tracking" to /dashboard/time', () => {
    expect(resolveNavigation('time tracking')).toBe('/dashboard/time')
  })

  it('resolves "knowledge graph" to /dashboard/knowledge', () => {
    expect(resolveNavigation('knowledge graph')).toBe('/dashboard/knowledge')
  })

  it('resolves "daily briefing" to /dashboard/briefing', () => {
    expect(resolveNavigation('daily briefing')).toBe('/dashboard/briefing')
  })

  it('resolves "weekly review" to /dashboard/review', () => {
    expect(resolveNavigation('weekly review')).toBe('/dashboard/review')
  })

  it('resolves "focus mode" to /dashboard/focus', () => {
    expect(resolveNavigation('focus mode')).toBe('/dashboard/focus')
  })

  it('resolves case-insensitively', () => {
    expect(resolveNavigation('TASKS')).toBe('/dashboard/tasks')
    expect(resolveNavigation('Sleep')).toBe('/dashboard/sleep')
    expect(resolveNavigation('DAILY BRIEFING')).toBe('/dashboard/briefing')
  })

  it('resolves partial matches', () => {
    expect(resolveNavigation('my tasks')).toBe('/dashboard/tasks')
    expect(resolveNavigation('goals page')).toBe('/dashboard/goals')
  })

  it('returns undefined for unknown navigation', () => {
    expect(resolveNavigation('non-existent-page')).toBeUndefined()
  })

  it('resolves trimmed whitespace', () => {
    expect(resolveNavigation('  dashboard  ')).toBe('/dashboard')
  })

  it('resolves all known route aliases', () => {
    const aliases: [string, string][] = [
      ['memory', '/dashboard/memory'],
      ['knowledge', '/dashboard/knowledge'],
      ['roadmap', '/dashboard/roadmap'],
      ['settings', '/dashboard/settings'],
      ['analytics', '/dashboard/analytics'],
      ['youtube vault', '/dashboard/youtube-vault'],
      ['automation', '/dashboard/automation'],
      ['review', '/dashboard/review'],
      ['briefing', '/dashboard/briefing'],
      ['opportunities', '/dashboard/opportunities'],
      ['projects', '/dashboard/projects'],
      ['ideas', '/dashboard/ideas'],
      ['goals', '/dashboard/goals'],
      ['courses', '/dashboard/courses'],
      ['habits', '/dashboard/habits'],
      ['income', '/dashboard/income'],
      ['resources', '/dashboard/resources'],
      ['academics', '/dashboard/academics'],
    ]
    for (const [input, expected] of aliases) {
      expect(resolveNavigation(input)).toBe(expected)
    }
  })
})

describe('extractDate (tested via parseCommand integration)', () => {
  it('extracts "today" from create_task command', () => {
    const result = parseCommand('/new task finish homework today')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "tomorrow"', () => {
    const result = parseCommand('/new task call plumber tomorrow')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "tonight" as today', () => {
    const result = parseCommand('/new task study tonight')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "next monday"', () => {
    const result = parseCommand('/new task submit form next monday')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "in 3 days"', () => {
    const result = parseCommand('/new task finish report in 3 days')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "next week"', () => {
    const result = parseCommand('/new task plan sprint next week')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "next month"', () => {
    const result = parseCommand('/new task review budget next month')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts "in 2 weeks"', () => {
    const result = parseCommand('/new task deadline in 2 weeks')
    expect(result.task?.dueDate).toMatch(ISO_DATE_RE)
  })

  it('extracts date in MM/DD format', () => {
    const result = parseCommand('/new task party 12/25')
    expect(result.task?.dueDate).toBe('2026-12-25')
  })

  it('extracts date in MM/DD/YYYY format', () => {
    const result = parseCommand('/new task deadline 06/15/2026')
    expect(result.task?.dueDate).toBe('2026-06-15')
  })

  it('extracts date in MM/DD/YY format', () => {
    const result = parseCommand('/new task deadline 12/31/25')
    expect(result.task?.dueDate).toBe('2025-12-31')
  })

  it('does not extract date when none present', () => {
    const result = parseCommand('/new task buy milk')
    expect(result.task?.dueDate).toBeUndefined()
  })
})
