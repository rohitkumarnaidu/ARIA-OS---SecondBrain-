import { useRealtime } from './useRealtime'
import { useTaskStore } from '@/lib/stores/taskStore'
import { useHabitStore } from '@/lib/stores/habitStore'

export function useStoreSync(userId?: string) {
  const taskFetch = useTaskStore(s => s.fetchTasks)

  useRealtime({
    table: 'tasks',
    userId: userId || '',
    onInsert: () => taskFetch(),
    onUpdate: () => taskFetch(),
    onDelete: () => taskFetch(),
  })

  const habitFetch = useHabitStore(s => s.fetch)

  useRealtime({
    table: 'habits',
    userId: userId || '',
    onInsert: () => habitFetch(),
    onUpdate: () => habitFetch(),
    onDelete: () => habitFetch(),
  })

  useRealtime({
    table: 'habit_logs',
    userId: userId || '',
    onInsert: () => habitFetch(),
    onUpdate: () => habitFetch(),
    onDelete: () => habitFetch(),
  })
}
