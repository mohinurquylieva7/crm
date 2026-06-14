/**
 * EduCRM Pro — Stress Test (D.M4)
 *
 * CI/CD, Load Balancer, va optimallashtirish qo'shilgandan KEYIN ishlatiladi.
 * Maqsad: tizimning chidamliligi va "breaking point" ni aniqlash.
 *
 * Ishga tushirish:
 *   k6 run k6/stress_test.js -e BASE_URL=http://<LB_IP>
 *
 * Natijalarni saqlash:
 *   k6 run k6/stress_test.js \
 *       -e BASE_URL=http://<LB_IP> \
 *       --out json=k6/results_after.json \
 *       --summary-export k6/summary_after.json
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const errorRate     = new Rate('stress_error_rate');
const responseTrend = new Trend('stress_response_ms', true);
const reqCounter    = new Counter('stress_total_requests');

export const options = {
  stages: [
    { duration: '30s', target: 10  },   // Isish
    { duration: '1m',  target: 50  },   // Normal
    { duration: '2m',  target: 100 },   // Yuqori yuk
    { duration: '1m',  target: 150 },   // Ortiqcha yuk — breaking point
    { duration: '1m',  target: 200 },   // Haddan oshiq
    { duration: '1m',  target: 100 },   // Tushish
    { duration: '30s', target: 0   },   // Sovish
  ],
  thresholds: {
    // Stress paytida kengaytirilgan SLA
    http_req_duration:  ['p(95)<5000', 'p(99)<10000'],
    http_req_failed:    ['rate<0.15'],   // < 15% xatolik ruxsat
    stress_error_rate:  ['rate<0.15'],
  },
  userAgent: 'EduCRM-k6-StressTest/1.0',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost';

export function setup() {
  const res = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({ email: 'admin@educrm.uz', password: 'Admin1234!' }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(res, { 'setup login ok': (r) => r.status === 200 });
  return {
    token: res.json('access_token'),
    refreshToken: res.json('refresh_token'),
  };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  // Stress paytida turli endpoint'larni aralash test qilish
  const scenario = Math.floor(Math.random() * 5);

  switch (scenario) {
    case 0:
      // Dashboard — eng og'ir
      group('Dashboard', () => {
        const res = http.get(`${BASE_URL}/api/v1/reports/dashboard`, { headers });
        const ok = check(res, { 'dashboard ok': (r) => r.status === 200 });
        errorRate.add(!ok);
        responseTrend.add(res.timings.duration);
        reqCounter.add(1);
      });
      break;

    case 1:
      // O'quvchilar search
      group('Students search', () => {
        const searches = ['A', 'B', 'Ahmad', 'Ali', 'Ma'];
        const q = searches[Math.floor(Math.random() * searches.length)];
        const res = http.get(
          `${BASE_URL}/api/v1/students/?search=${q}&page=1&size=20`,
          { headers }
        );
        const ok = check(res, { 'students ok': (r) => r.status === 200 });
        errorRate.add(!ok);
        responseTrend.add(res.timings.duration);
        reqCounter.add(1);
      });
      break;

    case 2:
      // Davomat
      group('Attendance', () => {
        const res = http.get(
          `${BASE_URL}/api/v1/attendance/?page=1&size=10`,
          { headers }
        );
        const ok = check(res, { 'attendance ok': (r) => r.status < 500 });
        errorRate.add(!ok);
        responseTrend.add(res.timings.duration);
        reqCounter.add(1);
      });
      break;

    case 3:
      // Revenue report
      group('Revenue report', () => {
        const res = http.get(
          `${BASE_URL}/api/v1/reports/revenue`,
          { headers }
        );
        const ok = check(res, { 'revenue ok': (r) => r.status < 500 });
        errorRate.add(!ok);
        responseTrend.add(res.timings.duration);
        reqCounter.add(1);
      });
      break;

    default:
      // Health check — eng yengil
      group('Health', () => {
        const res = http.get(`${BASE_URL}/health`);
        check(res, { 'health ok': (r) => r.status === 200 });
        reqCounter.add(1);
      });
  }

  // Stress paytida kamroq uxlash
  sleep(0.1 + Math.random() * 0.3);
}

export function teardown(data) {
  if (data?.token && data?.refreshToken) {
    http.post(
      `${BASE_URL}/api/v1/auth/logout`,
      JSON.stringify({ refresh_token: data.refreshToken }),
      {
        headers: {
          'Authorization': `Bearer ${data.token}`,
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

export function handleSummary(data) {
  return {
    'k6/summary_stress.json': JSON.stringify(data, null, 2),
    stdout: stressSummary(data),
  };
}

function stressSummary(data) {
  const { metrics } = data;
  const errRate = (metrics.http_req_failed?.values?.rate || 0) * 100;
  const p95 = metrics.http_req_duration?.values?.['p(95)'] || 0;
  const maxRPS = metrics.http_reqs?.values?.rate || 0;

  const lines = [
    '',
    '════════════════════════════════════════════════',
    ' EduCRM Pro — Stress Test Natijalar (D.M4)',
    '════════════════════════════════════════════════',
    `  Jami so'rovlar:    ${metrics.http_reqs?.values?.count || 0}`,
    `  Max RPS:           ${maxRPS.toFixed(1)} req/s`,
    `  Xatolik:           ${errRate.toFixed(2)}%`,
    `  p50:               ${(metrics.http_req_duration?.values?.['p(50)'] || 0).toFixed(0)}ms`,
    `  p95:               ${p95.toFixed(0)}ms`,
    `  p99:               ${(metrics.http_req_duration?.values?.['p(99)'] || 0).toFixed(0)}ms`,
    `  Max:               ${(metrics.http_req_duration?.values?.max || 0).toFixed(0)}ms`,
    '────────────────────────────────────────────────',
    `  SLA p95 < 5000ms:  ${p95 < 5000 ? '✅ O\'tdi' : '❌ Muvaffaqiyatsiz'}`,
    `  Xatolik < 15%:     ${errRate < 15 ? '✅ O\'tdi' : '❌ Muvaffaqiyatsiz'}`,
    '════════════════════════════════════════════════',
    '',
    '  Taqqoslash uchun:',
    '  Before: k6/summary_before.json',
    '  After:  k6/summary_after.json',
    '',
  ];
  return lines.join('\n');
}
