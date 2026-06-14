/**
 * EduCRM Pro — Normal Load Test (C.M3)
 *
 * Ishga tushirish:
 *   k6 run k6/load_test.js -e BASE_URL=http://<LB_IP>
 *
 * Natijalarni saqlash:
 *   k6 run k6/load_test.js \
 *       -e BASE_URL=http://<LB_IP> \
 *       --out json=k6/results_before.json \
 *       --summary-export k6/summary_before.json
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';

// ── Maxsus metrikalar ──────────────────────────────────────────────────────
const errorRate       = new Rate('custom_error_rate');
const responseTimeTrend = new Trend('custom_response_ms', true);
const reqCounter      = new Counter('custom_total_requests');
const activeUsers     = new Gauge('custom_active_users');

// ── Test konfiguratsiyasi ──────────────────────────────────────────────────
export const options = {
  stages: [
    { duration: '1m',  target: 5  },   // Isish
    { duration: '3m',  target: 30 },   // Normal yuk
    { duration: '2m',  target: 60 },   // Yuqori yuk
    { duration: '1m',  target: 0  },   // Sovish
  ],
  thresholds: {
    // SLA talablari
    http_req_duration:      ['p(50)<500', 'p(95)<2000', 'p(99)<5000'],
    http_req_failed:        ['rate<0.05'],   // < 5% xatolik
    custom_error_rate:      ['rate<0.05'],
    custom_response_ms:     ['p(95)<2000'],
  },
  // Har bir virtual foydalanuvchi uchun max ulanish
  userAgent: 'EduCRM-k6-LoadTest/1.0',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost';

// ── Setup: bir marta login ─────────────────────────────────────────────────
export function setup() {
  const loginRes = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({ email: 'admin@educrm.uz', password: 'Admin1234!' }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(loginRes, {
    'login muvaffaqiyatli (200)': (r) => r.status === 200,
    'access_token mavjud': (r) => !!r.json('access_token'),
  });

  if (loginRes.status !== 200) {
    console.error(`Login xatosi: ${loginRes.status} — ${loginRes.body}`);
  }

  return {
    token: loginRes.json('access_token'),
    refreshToken: loginRes.json('refresh_token'),
  };
}

// ── Asosiy test ────────────────────────────────────────────────────────────
export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  activeUsers.add(1);

  // ── Dashboard (eng og'ir so'rov) ────────────────────────────────────────
  group('Dashboard', () => {
    const res = http.get(`${BASE_URL}/api/v1/reports/dashboard`, { headers });
    const ok = check(res, {
      'dashboard 200': (r) => r.status === 200,
      'json qaytdi':   (r) => r.headers['Content-Type']?.includes('application/json'),
      'active_students mavjud': (r) => {
        try { return r.json('active_students') !== undefined; }
        catch { return false; }
      },
    });
    errorRate.add(!ok);
    responseTimeTrend.add(res.timings.duration);
    reqCounter.add(1);
  });

  sleep(0.5);

  // ── O'quvchilar ro'yxati ────────────────────────────────────────────────
  group("O'quvchilar", () => {
    const res = http.get(
      `${BASE_URL}/api/v1/students/?page=1&size=20`,
      { headers }
    );
    const ok = check(res, {
      'students 200': (r) => r.status === 200,
      'paginated': (r) => {
        try { return r.json('total') !== undefined && Array.isArray(r.json('items')); }
        catch { return false; }
      },
    });
    errorRate.add(!ok);
    responseTimeTrend.add(res.timings.duration);
    reqCounter.add(1);
  });

  sleep(0.3);

  // ── Guruhlar ────────────────────────────────────────────────────────────
  group('Guruhlar', () => {
    const res = http.get(
      `${BASE_URL}/api/v1/groups/?status=active&page=1&size=10`,
      { headers }
    );
    const ok = check(res, {
      'groups 200': (r) => r.status === 200,
      'items array': (r) => {
        try { return Array.isArray(r.json('items')); }
        catch { return false; }
      },
    });
    errorRate.add(!ok);
    responseTimeTrend.add(res.timings.duration);
    reqCounter.add(1);
  });

  sleep(0.3);

  // ── To'lovlar ────────────────────────────────────────────────────────────
  group("To'lovlar", () => {
    const res = http.get(
      `${BASE_URL}/api/v1/payments/?page=1&size=10`,
      { headers }
    );
    const ok = check(res, {
      'payments 200': (r) => r.status === 200,
    });
    errorRate.add(!ok);
    responseTimeTrend.add(res.timings.duration);
    reqCounter.add(1);
  });

  sleep(0.3);

  // ── Health check ─────────────────────────────────────────────────────────
  group('Health', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health 200': (r) => r.status === 200,
      'db connected': (r) => {
        try { return r.json('db') === 'connected'; }
        catch { return false; }
      },
    });
    reqCounter.add(1);
  });

  sleep(1);
  activeUsers.add(-1);
}

// ── Teardown ──────────────────────────────────────────────────────────────
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

// ── Natijalar ─────────────────────────────────────────────────────────────
export function handleSummary(data) {
  return {
    'k6/summary_load.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, opts) {
  const { metrics } = data;
  const lines = [
    '',
    '════════════════════════════════════════════════',
    ' EduCRM Pro — Load Test Natijalar',
    '════════════════════════════════════════════════',
    `  Jami so'rovlar:    ${metrics.http_reqs?.values?.count || 0}`,
    `  Xatolik darajasi:  ${((metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%`,
    `  p50 vaqt:          ${(metrics.http_req_duration?.values?.['p(50)'] || 0).toFixed(0)}ms`,
    `  p95 vaqt:          ${(metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(0)}ms`,
    `  p99 vaqt:          ${(metrics.http_req_duration?.values?.['p(99)'] || 0).toFixed(0)}ms`,
    `  Max vaqt:          ${(metrics.http_req_duration?.values?.max || 0).toFixed(0)}ms`,
    '════════════════════════════════════════════════',
    '',
  ];
  return lines.join('\n');
}
