import { api } from '@/lib/api'
import type { Course, CourseCreate, CourseUpdate } from '@/lib/types'

const BASE = '/api/v1/courses'

export const courseService = {
  list: () => api.get<Course[]>(BASE),
  get: (id: string) => api.get<Course>(`${BASE}/${id}`),
  create: (data: CourseCreate) => api.post<Course>(BASE, data),
  update: (id: string, data: CourseUpdate) => api.put<Course>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
