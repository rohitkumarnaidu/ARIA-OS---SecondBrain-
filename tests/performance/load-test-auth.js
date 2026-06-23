import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { Rate } from 'k6/metrics'

const errorRate = new Rate('errors')

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 30 },
    { duration: '1m', target: 50 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<3000'],
    http_req_failed: ['rate<0.02'],
    errors: ['rate<0.05'],
  },
}

const BASE_URL = __ENV.API_URL || 'http://localhost:8000'

export default function () {
  group('Health & Auth', () => {
    const health = http.get(`${BASE_URL}/health`)
    check(health, { 'health ok': (r) => r.status === 200 })
    errorRate.add(health.status !== 200)

    const ready = http.get(`${BASE_URL}/health/ready`)
    check(ready, { 'ready ok': (r) => r.status === 200 })

    const login = http.post(`${BASE_URL}/api/v1/auth/login`, {
      email: 'perf-test@secondbrain-os.com',
      password: 'PerfTest123!',
    })
    check(login, { 'login handled': (r) => r.status === 200 || r.status === 401 })
  })

  group('Protected Endpoints', () => {
    const headers = { 'Content-Type': 'application/json' }

    const noAuth = http.get(`${BASE_URL}/api/v1/tasks/`, { headers })
    check(noAuth, { 'no-auth blocked': (r) => r.status === 401 || r.status === 403 })
    errorRate.add(noAuth.status < 400 && noAuth.status !== 200)

    const briefings = http.get(`${BASE_URL}/api/v1/briefings/`, { headers })
    check(briefings, { 'briefings no-auth blocked': (r) => r.status === 401 || r.status === 403 })

    const reviews = http.get(`${BASE_URL}/api/v1/reviews/`, { headers })
    check(reviews, { 'reviews no-auth blocked': (r) => r.status === 401 || r.status === 403 })
  })

  sleep(1)
}
