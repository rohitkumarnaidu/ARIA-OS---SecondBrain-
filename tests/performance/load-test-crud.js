import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { Rate, Trend } from 'k6/metrics'

const errorRate = new Rate('errors')
const taskDuration = new Trend('task_duration')
const habitDuration = new Trend('habit_duration')
const sleepDuration = new Trend('sleep_duration')
const timeDuration = new Trend('time_duration')

export const options = {
  stages: [
    { duration: '1m', target: 20 },
    { duration: '2m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<800', 'p(99)<3000'],
    http_req_failed: ['rate<0.02'],
    errors: ['rate<0.05'],
    task_duration: ['p(95)<500'],
    habit_duration: ['p(95)<500'],
  },
}

const BASE_URL = __ENV.API_URL || 'http://localhost:8000'
const AUTH_TOKEN = __ENV.AUTH_TOKEN || ''

function getHeaders(token) {
  return {
    Authorization: `Bearer ${token || AUTH_TOKEN}`,
    'Content-Type': 'application/json',
  }
}

export function setup() {
  const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, {
    email: 'perf-test@secondbrain-os.com',
    password: 'PerfTest123!',
  })
  const token = loginRes.status === 200 ? loginRes.json('access_token') : AUTH_TOKEN
  return { token }
}

export default function (data) {
  const headers = getHeaders(data.token)

  group('Tasks', () => {
    const list = http.get(`${BASE_URL}/api/v1/tasks/?limit=10`, { headers })
    taskDuration.add(list.timings.duration)
    check(list, { 'tasks list 200': (r) => r.status === 200 })
    errorRate.add(list.status !== 200)

    const create = http.post(`${BASE_URL}/api/v1/tasks/`, JSON.stringify({
      title: `K6 task ${Date.now()}`,
      priority: 'medium',
      status: 'pending',
    }), { headers })
    taskDuration.add(create.timings.duration)
    check(create, { 'task created 201': (r) => r.status === 201 })
    errorRate.add(create.status !== 201)

    if (create.status === 201 && create.json('id')) {
      const get = http.get(`${BASE_URL}/api/v1/tasks/${create.json('id')}`, { headers })
      check(get, { 'task get 200': (r) => r.status === 200 })

      const update = http.put(`${BASE_URL}/api/v1/tasks/${create.json('id')}`, JSON.stringify({
        status: 'completed',
      }), { headers })
      check(update, { 'task updated 200': (r) => r.status === 200 })

      const del = http.del(`${BASE_URL}/api/v1/tasks/${create.json('id')}`, null, { headers })
      check(del, { 'task deleted 204': (r) => r.status === 204 })
    }

    sleep(0.5)
  })

  group('Habits', () => {
    const list = http.get(`${BASE_URL}/api/v1/habits/?limit=10`, { headers })
    habitDuration.add(list.timings.duration)
    check(list, { 'habits list 200': (r) => r.status === 200 })

    const create = http.post(`${BASE_URL}/api/v1/habits/`, JSON.stringify({
      name: `K6 habit ${Date.now()}`,
      frequency: 'daily',
    }), { headers })
    habitDuration.add(create.timings.duration)
    check(create, { 'habit created 201': (r) => r.status === 201 })

    sleep(0.5)
  })

  group('Sleep', () => {
    const list = http.get(`${BASE_URL}/api/v1/sleep/?limit=5`, { headers })
    sleepDuration.add(list.timings.duration)
    check(list, { 'sleep list 200': (r) => r.status === 200 })
  })

  group('Time', () => {
    const list = http.get(`${BASE_URL}/api/v1/time/?limit=10`, { headers })
    timeDuration.add(list.timings.duration)
    check(list, { 'time list 200': (r) => r.status === 200 })
  })
}
