import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000/api/v1/skills';
const TOKEN = __ENV.AUTH_TOKEN || 'test-token';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json',
};

const errorRate = new Rate('errors');
const skillsListTrend = new Trend('skills_list_duration');
const skillsCreateTrend = new Trend('skills_create_duration');
const skillsDetailTrend = new Trend('skills_detail_duration');

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    errors: ['rate<0.05'],
    skills_list_duration: ['p(95)<2000'],
    skills_create_duration: ['p(95)<3000'],
    skills_detail_duration: ['p(95)<2000'],
    http_req_duration: ['p(95)<5000'],
  },
};

const SKILL_IDS = ['skill-1', 'skill-2', 'skill-3', 'skill-4', 'skill-5'];

export default function () {
  group('Skills API Load Test', () => {
    group('List Endpoints', () => {
      const endpoints = [
        { name: 'categories', url: `${BASE_URL}/categories` },
        { name: 'skills', url: `${BASE_URL}/` },
        { name: 'user-skills', url: `${BASE_URL}/user-skills` },
        { name: 'market-data', url: `${BASE_URL}/market-data` },
        { name: 'certifications', url: `${BASE_URL}/certifications` },
        { name: 'topics', url: `${BASE_URL}/topics` },
        { name: 'resources', url: `${BASE_URL}/resources` },
        { name: 'learning-paths', url: `${BASE_URL}/learning-paths` },
        { name: 'recommendations', url: `${BASE_URL}/recommendations` },
        { name: 'external-mappings', url: `${BASE_URL}/external-mappings` },
        { name: 'forecasts', url: `${BASE_URL}/forecasts` },
        { name: 'income', url: `${BASE_URL}/income` },
      ];

      const idx = Math.floor(Math.random() * endpoints.length);
      const ep = endpoints[idx];
      const res = http.get(ep.url, { headers });

      check(res, {
        [`list ${ep.name} status 200`]: (r) => r.status === 200,
      }) || errorRate.add(1);

      skillsListTrend.add(res.timings.duration);
    });

    group('Skill Detail', () => {
      const skillId = SKILL_IDS[Math.floor(Math.random() * SKILL_IDS.length)];
      const res = http.get(`${BASE_URL}/${skillId}`, { headers });

      check(res, {
        'skill detail status 200 or 404': (r) => r.status === 200 || r.status === 404,
      }) || errorRate.add(1);

      skillsDetailTrend.add(res.timings.duration);
    });

    group('Create User Skill', () => {
      const payload = JSON.stringify({
        skill_id: SKILL_IDS[Math.floor(Math.random() * SKILL_IDS.length)],
        level: 0,
        state: 'planned',
      });
      const res = http.post(`${BASE_URL}/user-skills`, payload, { headers });

      check(res, {
        'create user-skill status 201 or 409': (r) => r.status === 201 || r.status === 409,
      }) || errorRate.add(1);

      skillsCreateTrend.add(res.timings.duration);
    });
  });

  sleep(1);
}
