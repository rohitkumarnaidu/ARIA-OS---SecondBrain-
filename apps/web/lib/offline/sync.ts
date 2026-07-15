import { offlineDb, type StoreName, type StoredRecord } from './db'
import { api } from '@/lib/api'
import type {
  Task, Habit, HabitLog, Course, Goal, Idea, IncomeEntry,
  Project, Resource, SleepLog, TimeEntry, ChatMessage,
} from '@/lib/types'

type TableRecordMap = {
  tasks: Task
  habits: Habit
  habit_logs: HabitLog
  courses: Course
  goals: Goal
  ideas: Idea
  income: IncomeEntry
  projects: Project
  resources: Resource
  sleep_logs: SleepLog
  time_entries: TimeEntry
  chat_messages: ChatMessage
}

const API_PATHS: Record<StoreName, string> = {
  tasks: '/api/v1/tasks',
  habits: '/api/v1/habits',
  habit_logs: '/api/v1/habits/logs',
  courses: '/api/v1/courses',
  goals: '/api/v1/goals',
  ideas: '/api/v1/ideas',
  income: '/api/v1/income',
  projects: '/api/v1/projects',
  resources: '/api/v1/resources',
  sleep_logs: '/api/v1/sleep',
  time_entries: '/api/v1/time',
  chat_messages: '/api/v1/chat',
  sync_queue: '',
}

const CRUD_MAP: Record<StoreName, {
  list: () => Promise<unknown[]>
  create: (data: unknown) => Promise<unknown>
  update: (id: string, data: unknown) => Promise<unknown>
  remove: (id: string) => Promise<unknown>
} | null> = {
  tasks: {
    list: () => api.get<Task[]>(API_PATHS.tasks),
    create: (d) => api.post<Task>(API_PATHS.tasks, d),
    update: (id, d) => api.put<Task>(`${API_PATHS.tasks}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.tasks}/${id}`),
  },
  habits: {
    list: () => api.get<Habit[]>(API_PATHS.habits),
    create: (d) => api.post<Habit>(API_PATHS.habits, d),
    update: (id, d) => api.put<Habit>(`${API_PATHS.habits}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.habits}/${id}`),
  },
  habit_logs: {
    list: () => api.get<HabitLog[]>(API_PATHS.habit_logs),
    create: (d) => api.post<HabitLog>(API_PATHS.habit_logs, d),
    update: (id, d) => api.put<HabitLog>(`${API_PATHS.habit_logs}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.habit_logs}/${id}`),
  },
  courses: {
    list: () => api.get<Course[]>(API_PATHS.courses),
    create: (d) => api.post<Course>(API_PATHS.courses, d),
    update: (id, d) => api.put<Course>(`${API_PATHS.courses}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.courses}/${id}`),
  },
  goals: {
    list: () => api.get<Goal[]>(API_PATHS.goals),
    create: (d) => api.post<Goal>(API_PATHS.goals, d),
    update: (id, d) => api.put<Goal>(`${API_PATHS.goals}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.goals}/${id}`),
  },
  ideas: {
    list: () => api.get<Idea[]>(API_PATHS.ideas),
    create: (d) => api.post<Idea>(API_PATHS.ideas, d),
    update: (id, d) => api.put<Idea>(`${API_PATHS.ideas}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.ideas}/${id}`),
  },
  income: {
    list: () => api.get<IncomeEntry[]>(API_PATHS.income),
    create: (d) => api.post<IncomeEntry>(API_PATHS.income, d),
    update: (id, d) => api.put<IncomeEntry>(`${API_PATHS.income}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.income}/${id}`),
  },
  projects: {
    list: () => api.get<Project[]>(API_PATHS.projects),
    create: (d) => api.post<Project>(API_PATHS.projects, d),
    update: (id, d) => api.put<Project>(`${API_PATHS.projects}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.projects}/${id}`),
  },
  resources: {
    list: () => api.get<Resource[]>(API_PATHS.resources),
    create: (d) => api.post<Resource>(API_PATHS.resources, d),
    update: (id, d) => api.put<Resource>(`${API_PATHS.resources}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.resources}/${id}`),
  },
  sleep_logs: {
    list: () => api.get<SleepLog[]>(API_PATHS.sleep_logs),
    create: (d) => api.post<SleepLog>(API_PATHS.sleep_logs, d),
    update: (id, d) => api.put<SleepLog>(`${API_PATHS.sleep_logs}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.sleep_logs}/${id}`),
  },
  time_entries: {
    list: () => api.get<TimeEntry[]>(API_PATHS.time_entries),
    create: (d) => api.post<TimeEntry>(API_PATHS.time_entries, d),
    update: (id, d) => api.put<TimeEntry>(`${API_PATHS.time_entries}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.time_entries}/${id}`),
  },
  chat_messages: {
    list: () => api.get<ChatMessage[]>(API_PATHS.chat_messages),
    create: (d) => api.post<ChatMessage>(API_PATHS.chat_messages, d),
    update: (id, d) => api.put<ChatMessage>(`${API_PATHS.chat_messages}/${id}`, d),
    remove: (id) => api.delete(`${API_PATHS.chat_messages}/${id}`),
  },
  sync_queue: null,
}

export const syncManager = {
  async queueMutation(
    table: StoreName,
    operation: 'create' | 'update' | 'delete',
    recordId: string | undefined,
    data: unknown,
  ): Promise<void> {
    await offlineDb.enqueueSync(table, operation, recordId, data)
  },

  async processSyncQueue(): Promise<{ success: number; failed: number }> {
    let success = 0
    let failed = 0

    const items = await offlineDb.getSyncQueueItems()
    const pending = items
      .filter((i) => !i.failed)
      .sort((a, b) => a.timestamp - b.timestamp)

    for (const item of pending) {
      const crud = CRUD_MAP[item.table]
      if (!crud || item.id === undefined) {
        if (item.id !== undefined) await offlineDb.removeSyncItem(item.id)
        continue
      }

      try {
        switch (item.operation) {
          case 'create':
            await crud.create(item.data)
            break
          case 'update':
            if (item.recordId) {
              await crud.update(item.recordId, item.data)
            }
            break
          case 'delete':
            if (item.recordId) {
              await crud.remove(item.recordId)
            }
            break
        }
        await offlineDb.removeSyncItem(item.id)
        success++
      } catch {
        await offlineDb.updateSyncRetry(item.id)
        const updated = (await offlineDb.getSyncQueueItems()).find(
          (i) => i.id === item.id,
        )
        if (updated?.failed) {
          failed++
        }
      }
    }

    return { success, failed }
  },

  async syncTable<T>(storeName: StoreName): Promise<void> {
    const crud = CRUD_MAP[storeName]
    if (!crud) return
    const data = await crud.list() as T[]
    const now = new Date().toISOString()
    await offlineDb.putMany(
      storeName,
      data.map((d: any) => ({ id: d.id, data: d })),
      now,
    )
  },

  async syncAll(): Promise<void> {
    const tables = Object.keys(CRUD_MAP).filter(
      (k) => k !== 'sync_queue',
    ) as StoreName[]
    for (const table of tables) {
      try {
        await this.syncTable(table)
      } catch (err) {
        console.error(`[syncManager] Failed to sync ${table}:`, err)
      }
    }
  },

  async getPendingMutationCount(): Promise<number> {
    return offlineDb.getPendingSyncCount()
  },

  async getFailedMutationCount(): Promise<number> {
    return offlineDb.getFailedSyncCount()
  },

  async retryFailed(): Promise<void> {
    await offlineDb.retryFailedSyncItems()
  },

  async getLastSyncTime(): Promise<string | null> {
    return offlineDb.getAllLastSyncTime()
  },

  async getLocalData<T>(storeName: StoreName): Promise<StoredRecord<T>[]> {
    return offlineDb.getAll<T>(storeName)
  },

  async clearAll(): Promise<void> {
    await offlineDb.clearAllData()
  },
}