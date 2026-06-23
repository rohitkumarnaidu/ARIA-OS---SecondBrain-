import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

const errorRate = new Rate('errors')

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '10s', target: 200 },
    { duration: '30s', target: 200 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'],
    http_req_failed: ['rate<0.05'],
    errors: ['rate<0.10'],
  },
}

const BASE_URL = __ENV.API_URL || 'http://localhost:8000'
const AUTH_TOKEN = __ENV.AUTH_TOKEN || ''

const headers = {
  Authorization: `Bearer ${AUTH_TOKEN}`,
  'Content-Type': 'application/json',
}

const endpoints = [
  { method: 'GET', url: '/api/v1/tasks/?limit=5' },
  { method: 'GET', url: '/api/v1/habits/?limit=5' },
  { method: 'GET', url: '/api/v1/goals/?limit=5' },
  { method: 'GET', url: '/api/v1/courses/?limit=5' },
  { method: 'GET', url: '/api/v1/sleep/?limit=5' },
  { method: 'GET', url: '/api/v1/time/?limit=5' },
  { method: 'GET', url: '/api/v1/projects/?limit=5' },
  { method: 'GET', url: '/api/v1/ideas/?limit=5' },
  { method: 'GET', url: '/api/v1/resources/?limit=5' },
  { method: 'GET', url: '/api/v1/opportunities/?limit=5' },
  { method: 'GET', url: '/api/v1/memory/?limit=5' },
  { method: 'GET', url: '/health' },
  { method: 'GET', url: '/health/ready' },
]

export default function () {
  const idx = (__VU + __ITER) % endpoints.length
  const ep = endpoints[idx]
  const res = http.get(`${BASE_URL}${ep.url}`, { headers })
  check(res, { [`${ep.url} ok`]: (r) => r.status < 500 })
  errorRate.add(res.status >= 500)

  sleep(0.1)
}
