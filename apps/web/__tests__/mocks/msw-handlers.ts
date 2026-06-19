import { http, HttpResponse } from 'msw'
import { buildTask } from '@/__tests__/factories'

const SUPABASE_URL = 'https://placeholder-project.supabase.co'

const handlers = [
  http.get(`${SUPABASE_URL}/rest/v1/tasks`, ({ request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id')?.replace('eq.', '')

    return HttpResponse.json([
      buildTask({ user_id: userId ?? 'test-user' }),
      buildTask({ user_id: userId ?? 'test-user', status: 'completed' }),
    ])
  }),

  http.post(`${SUPABASE_URL}/rest/v1/tasks`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json(buildTask(body as Partial<ReturnType<typeof buildTask>>), { status: 201 })
  }),

  http.patch(`${SUPABASE_URL}/rest/v1/tasks`, async ({ request }) => {
    const url = new URL(request.url)
    const id = url.searchParams.get('id')?.replace('eq.', '')
    return HttpResponse.json(buildTask({ id: id ?? undefined }))
  }),

  http.delete(`${SUPABASE_URL}/rest/v1/tasks`, () =>
    HttpResponse.json({}, { status: 204 }),
  ),

  http.get(`${SUPABASE_URL}/rest/v1/courses`, () =>
    HttpResponse.json([
      buildTask({ title: 'Math 101', status: 'completed' }),
      buildTask({ title: 'Physics 201' }),
    ]),
  ),

  http.get(`${SUPABASE_URL}/rest/v1/goals`, () =>
    HttpResponse.json([buildTask({ title: 'Learn Rust' })]),
  ),

  http.get(`${SUPABASE_URL}/rest/v1/habits`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/sleep_logs`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/income_entries`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/ideas`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/resources`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/opportunities`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/time_entries`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/projects`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/chat_messages`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/users`, () =>
    HttpResponse.json([{ id: 'test-user', email: 'test@example.com', display_name: 'Test User' }]),
  ),

  http.get(`${SUPABASE_URL}/rest/v1/daily_briefings`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/weekly_reviews`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/habit_logs`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/learning_progress`, () => HttpResponse.json([])),

  http.get(`${SUPABASE_URL}/rest/v1/memory`, () => HttpResponse.json([])),
]

export { handlers }
