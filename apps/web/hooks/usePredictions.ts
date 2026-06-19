'use client'

import { useState, useEffect } from 'react'
import { predictive } from '@/lib/ai'
import type {
  TaskCompletionForecast,
  HabitCompletionForecast,
  SleepInsight,
  SmartSlotResponse,
} from '@/lib/types'

export function usePredictions() {
  const [tasks, setTasks] = useState<TaskCompletionForecast | null>(null)
  const [habits, setHabits] = useState<HabitCompletionForecast | null>(null)
  const [sleep, setSleep] = useState<SleepInsight | null>(null)
  const [slots, setSlots] = useState<SmartSlotResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    Promise.allSettled([
      predictive.taskCompletion(),
      predictive.habits(),
      predictive.sleep(),
      predictive.smartSlots(),
    ]).then(([tasksRes, habitsRes, sleepRes, slotsRes]) => {
      if (cancelled) return
      if (tasksRes.status === 'fulfilled') setTasks(tasksRes.value)
      if (habitsRes.status === 'fulfilled') setHabits(habitsRes.value)
      if (sleepRes.status === 'fulfilled') setSleep(sleepRes.value)
      if (slotsRes.status === 'fulfilled') setSlots(slotsRes.value)
      const errors = [tasksRes, habitsRes, sleepRes, slotsRes]
        .filter((r): r is PromiseRejectedResult => r.status === 'rejected')
        .map(r => r.reason?.message || 'Prediction failed')
      if (errors.length > 0) setError(errors.join('; '))
      setLoading(false)
    })

    return () => { cancelled = true }
  }, [])

  return { tasks, habits, sleep, slots, loading, error }
}
