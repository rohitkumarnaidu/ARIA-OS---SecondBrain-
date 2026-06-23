import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { Rate, Trend } from 'k6/metrics'

const errorRate = new Rate('errors')
const aiDuration = new Trend('ai_duration')
const predictDuration = new Trend('predict_duration')
const nlpDuration = new Trend('nlp_duration')

export const options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '3m', target: 30 },
    { duration: '2m', target: 50 },
    { duration: '2m', target: 50 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000', 'p(99)<15000'],
    http_req_failed: ['rate<0.05'],
    errors: ['rate<0.10'],
    nlp_duration: ['p(95)<500'],
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
  return { token: loginRes.status === 200 ? loginRes.json('access_token') : AUTH_TOKEN }
}

export default function (data) {
  const headers = getHeaders(data.token)

  group('NLP Parsing', () => {
    const queries = [
      'create a task review PR by friday at 5pm',
      'add todo buy milk tomorrow',
      'remind me to call dentist on monday',
      'schedule study session for 2 hours',
    ]
    for (const q of queries) {
      const res = http.post(`${BASE_URL}/api/v1/nlp/parse`, JSON.stringify({ text: q }), { headers })
      nlpDuration.add(res.timings.duration)
      check(res, { 'nlp parsed': (r) => r.status === 200 })
      errorRate.add(res.status !== 200)
      sleep(0.2)
    }
  })

  group('NLP Execute', () => {
    const res = http.post(`${BASE_URL}/api/v1/nlp/execute`, JSON.stringify({
      text: 'create a task k6 load test task',
    }), { headers })
    nlpDuration.add(res.timings.duration)
    check(res, { 'nlp executed': (r) => r.status === 200 })
    errorRate.add(res.status !== 200)
  })

  group('Predictions', () => {
    const res = http.get(`${BASE_URL}/api/v1/predictions/tasks`, { headers })
    predictDuration.add(res.timings.duration)
    check(res, { 'predictions loaded': (r) => r.status === 200 })

    const habitRes = http.get(`${BASE_URL}/api/v1/predictions/habits`, { headers })
    check(habitRes, { 'habit predictions loaded': (r) => r.status === 200 })

    const sleepRes = http.get(`${BASE_URL}/api/v1/predictions/sleep`, { headers })
    check(sleepRes, { 'sleep predictions loaded': (r) => r.status === 200 })
  })

  group('Feedback', () => {
    const res = http.post(`${BASE_URL}/api/v1/feedback/`, JSON.stringify({
      source: 'chat',
      target_id: `k6-test-${Date.now()}`,
      rating: 5,
    }), { headers })
    check(res, { 'feedback submitted': (r) => r.status === 201 })
  })

  group('Memory', () => {
    const list = http.get(`${BASE_URL}/api/v1/memory/?limit=10`, { headers })
    check(list, { 'memories loaded': (r) => r.status === 200 })

    const consolidate = http.post(`${BASE_URL}/api/v1/memory/consolidate`, {}, { headers })
    check(consolidate, { 'memory consolidated': (r) => r.status === 200 })
  })

  group('Orchestrator', () => {
    for (const agent of ['plan', 'execute']) {
      const res = http.post(`${BASE_URL}/api/v1/automation/${agent}`, JSON.stringify({
        query: 'review my tasks and suggest improvements',
      }), { headers })
      aiDuration.add(res.timings.duration)
      check(res, { [`orchestrator ${agent}`]: (r) => r.status === 200 })
      errorRate.add(res.status !== 200)
      sleep(0.5)
    }
  })

  group('Chat', () => {
    const res = http.post(`${BASE_URL}/api/v1/chat/`, JSON.stringify({
      message: 'What is my top priority today?',
    }), { headers })
    check(res, { 'chat response': (r) => r.status === 200 })
    errorRate.add(res.status !== 200)
  })

  group('Monitoring', () => {
    const res = http.get(`${BASE_URL}/api/v1/monitoring/token-usage/summary`, { headers })
    check(res, { 'monitoring loaded': (r) => r.status === 200 })
  })
}
