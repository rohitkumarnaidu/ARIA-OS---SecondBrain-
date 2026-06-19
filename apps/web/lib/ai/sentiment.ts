export function computeSentiment(params: {
  taskAtRisk: number
  habitAtRisk: number
  sleepTrend: string
  avgSleepScore: number
}) {
  const signals: string[] = []
  let severity = 0

  if (params.taskAtRisk > 3) {
    signals.push('task-overload')
    severity++
  }
  if (params.habitAtRisk > 2) {
    signals.push('habit-slip')
    severity++
  }
  if (params.sleepTrend === 'declining') {
    signals.push('sleep-decline')
    severity++
  }
  if (params.avgSleepScore > 0 && params.avgSleepScore < 60) {
    signals.push('poor-sleep')
    severity++
  }

  if (severity === 0) return null
  if (severity >= 3) return { level: 'high', message: 'Things feel heavy right now. Focus on 1-2 essential tasks and give yourself permission to rest.', signals }
  if (severity >= 2) return { level: 'medium', message: 'A few things need attention. Maybe start with a single small win to rebuild momentum.', signals }
  return { level: 'low', message: 'A couple of areas could use a boost. Check your at-risk items for quick wins.', signals }
}
