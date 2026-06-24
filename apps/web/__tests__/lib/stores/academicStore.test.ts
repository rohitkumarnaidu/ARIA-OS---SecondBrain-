import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAcademicStore } from '@/lib/stores/academicStore'

const mockListSubjects = vi.fn()
const mockListMarks = vi.fn()
const mockCreateSubject = vi.fn()
const mockCreateMark = vi.fn()
const mockDeleteSubject = vi.fn()

vi.mock('@/lib/services/academics', () => ({
  academicService: {
    listSubjects: (...args: unknown[]) => mockListSubjects(...args),
    listMarks: (...args: unknown[]) => mockListMarks(...args),
    createSubject: (...args: unknown[]) => mockCreateSubject(...args),
    createMark: (...args: unknown[]) => mockCreateMark(...args),
    deleteSubject: (...args: unknown[]) => mockDeleteSubject(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useAcademicStore.setState({ subjects: [], marks: [], loading: false, error: null })
})

describe('academicStore', () => {
  it('has correct initial state', () => {
    const s = useAcademicStore.getState()
    expect(s.subjects).toEqual([])
    expect(s.marks).toEqual([])
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetchAll loads subjects and marks', async () => {
    const subjects = [{ id: 's1', name: 'Math' }]
    const marks = [{ id: 'm1', subject_id: 's1', score: 85 }]
    mockListSubjects.mockResolvedValueOnce(subjects)
    mockListMarks.mockResolvedValueOnce(marks)
    await useAcademicStore.getState().fetchAll()
    const s = useAcademicStore.getState()
    expect(s.subjects).toEqual(subjects)
    expect(s.marks).toEqual(marks)
    expect(s.loading).toBe(false)
  })

  it('fetchAll sets error on failure', async () => {
    mockListSubjects.mockRejectedValueOnce(new Error('DB error'))
    await useAcademicStore.getState().fetchAll()
    expect(useAcademicStore.getState().error).toBe('DB error')
    expect(useAcademicStore.getState().loading).toBe(false)
  })

  it('addSubject prepends subject', async () => {
    const created = { id: 's2', name: 'Physics' }
    mockCreateSubject.mockResolvedValueOnce(created)
    await useAcademicStore.getState().addSubject({ name: 'Physics' })
    expect(useAcademicStore.getState().subjects).toEqual([created])
  })

  it('addSubject sets error on failure', async () => {
    mockCreateSubject.mockRejectedValueOnce(new Error('Validation failed'))
    await useAcademicStore.getState().addSubject({ name: '' })
    expect(useAcademicStore.getState().error).toBe('Validation failed')
  })

  it('addMark prepends mark', async () => {
    const created = { id: 'm2', subject_id: 's1', score: 92 }
    mockCreateMark.mockResolvedValueOnce(created)
    await useAcademicStore.getState().addMark({ subject_id: 's1', score: 92 })
    expect(useAcademicStore.getState().marks).toEqual([created])
  })

  it('addMark sets error on failure', async () => {
    mockCreateMark.mockRejectedValueOnce(new Error('Subject not found'))
    await useAcademicStore.getState().addMark({ subject_id: 'x', score: 0 })
    expect(useAcademicStore.getState().error).toBe('Subject not found')
  })

  it('deleteSubject removes subject and sets loading', async () => {
    useAcademicStore.setState({ subjects: [{ id: 's1', name: 'Math' }, { id: 's2', name: 'Physics' }] })
    mockDeleteSubject.mockResolvedValueOnce({})
    await useAcademicStore.getState().deleteSubject('s1')
    expect(useAcademicStore.getState().subjects).toEqual([{ id: 's2', name: 'Physics' }])
    expect(useAcademicStore.getState().loading).toBe(false)
  })

  it('deleteSubject sets error on failure', async () => {
    mockDeleteSubject.mockRejectedValueOnce(new Error('Not found'))
    await useAcademicStore.getState().deleteSubject('x')
    expect(useAcademicStore.getState().error).toBe('Not found')
  })
})
