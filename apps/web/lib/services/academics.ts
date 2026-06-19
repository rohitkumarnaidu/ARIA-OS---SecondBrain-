import { api } from '@/lib/api'
import type { Subject, SubjectCreate, Mark, MarkCreate } from '@/lib/types'

const BASE = '/api/v1/academics'

export const academicService = {
  listSubjects: () => api.get<Subject[]>(`${BASE}/subjects`),
  createSubject: (data: SubjectCreate) => api.post<Subject>(`${BASE}/subjects`, data),
  deleteSubject: (id: string) => api.delete<{ message: string }>(`${BASE}/subjects/${id}`),
  listMarks: () => api.get<Mark[]>(`${BASE}/marks`),
  createMark: (data: MarkCreate) => api.post<Mark>(`${BASE}/marks`, data),
  deleteMark: (id: string) => api.delete<{ message: string }>(`${BASE}/marks/${id}`),
}
