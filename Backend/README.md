# EduCRM Pro

O'quv markazlar (tillar maktabi, repetitorlik) uchun to'liq CRM/ERP tizimi.

**Stack:** FastAPI · PostgreSQL 15 · Redis 7 · Docker · DigitalOcean · GitHub Actions CI/CD

---

## Tezkor ishga tushirish (Local Dev)

```bash
# 1. Repo clone
git clone https://github.com/your-username/educrm-backend
cd educrm-backend

# 2. .env yaratish
cp .env.example .env

# 3. Docker Compose bilan ishga tushirish
docker compose up -d

# 4. Migratsiya
docker compose exec api alembic upgrade head

# 5. Test ma'lumotlarini yuklash
docker compose exec api python -m scripts.seed

# 6. Swagger UI
open http://localhost/docs
```

| URL | Maqsad |
|-----|--------|
| `http://localhost/docs` | Swagger UI |
| `http://localhost/redoc` | ReDoc |
| `http://localhost/health` | Health check |
| `http://localhost/api/v1/` | API prefix |

**Default admin:** `admin@educrm.uz` / `Admin1234!`

---

## Arxitektura

```
Internet (foydalanuvchilar)
        │
        ▼
DigitalOcean Load Balancer        ← Public IP  :80 / :443
  Health check: /health
  Algorithm: round-robin
  Sticky sessions: cookies
        │
        ▼  (VPC private: 10.10.0.0/16)
App Droplet(lar) [Ubuntu 22.04]   ← Firewall: faqat LB dan :8000
  Nginx :80 → FastAPI :8000
  Docker Compose (api + nginx)
        │
   ┌────┴─────┐
   ▼          ▼
Managed     Managed
PostgreSQL  Redis 7             ← Faqat private network
(pg 15)     (cache + sessions)

DigitalOcean Spaces             ← Media fayllar (S3-compatible)
DOCR                            ← Docker image registry
```

---

## DigitalOcean Deploy — Qadam-ba-qadam

### Talablar

```bash
# Terraform
brew install terraform         # macOS
# yoki: https://developer.hashicorp.com/terraform/install

# doctl (DigitalOcean CLI)
brew install doctl             # macOS
# yoki: https://docs.digitalocean.com/reference/doctl/how-to/install/

# k6 (yuk testi uchun)
brew install k6                # macOS
# yoki: https://k6.io/docs/get-started/installation/
```

### 1-qadam: DO sozlamalari

```bash
# DO API tokeni bilan login
doctl auth init
# → DigitalOcean console → API → Generate New Token

# SSH key yaratish
ssh-keygen -t ed25519 -C "educrm-deploy" -f ~/.ssh/educrm_deploy
# Parol qo'ymang (CI/CD uchun)

# SSH key ni DO ga yuklash
doctl compute ssh-key import educrm-deploy \
    --public-key-file ~/.ssh/educrm_deploy.pub

# Key nomini tekshirish
doctl compute ssh-key list
```

### 2-qadam: Terraform bilan infra yaratish

```bash
cd terraform

# terraform.tfvars yaratish (gitignore da!)
cat > terraform.tfvars << EOF
do_token       = "dop_v1_your-do-api-token-here"
ssh_key_name   = "educrm-deploy"
admin_ip       = "$(curl -s ifconfig.me)/32"
db_password    = "$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 20)!"
jwt_secret_key = "$(openssl rand -hex 32)"
alert_email    = "your@email.com"
EOF

# Initialization
terraform init

# Ko'rish (hech narsa o'zgarmaydi)
terraform plan

# Infra yaratish (~5-8 daqiqa)
terraform apply
# → "yes" deb tasdiqlang

# Muhim ma'lumotlarni saqlash
terraform output load_balancer_ip
terraform output -raw postgres_uri
terraform output -raw redis_uri
```

**Terraform yaratadigan resurslar:**

| Resurs | Narx/oy |
|--------|---------|
| Droplet (s-2vcpu-2gb) | ~$18 |
| Managed PostgreSQL (db-s-1vcpu-1gb) | ~$15 |
| Managed Redis (db-s-1vcpu-1gb) | ~$15 |
| Load Balancer | ~$12 |
| Spaces (500MB) | ~$5 |
| Container Registry (basic) | Bepul |
| **Jami** | **~$65/oy** |

### 3-qadam: GitHub Secrets

GitHub repo → **Settings → Secrets → Actions → New repository secret**:

| Secret nomi | Qiymat | Qayerdan olinadi |
|-------------|--------|-----------------|
| `DO_TOKEN` | DigitalOcean API token | DO Console → API |
| `DO_SSH_PRIVATE_KEY` | SSH private key | `cat ~/.ssh/educrm_deploy` |
| `DO_REGISTRY_NAME` | Registry nomi | `terraform output registry_name` |

### 4-qadam: CI/CD ishga tushirish

```bash
# main ga push qiling → CD pipeline avtomatik ishga tushadi:
#
#  push
#   │
#   ├─ Job: test          ← pytest + ruff
#   ├─ Job: build-push    ← Docker image → DOCR
#   └─ Job: deploy        ← SSH → pull → migrate → restart → health check

git add .
git commit -m "feat: initial production deploy"
git push origin main
```

GitHub Actions → **Actions** tabida progress kuzating.

### 5-qadam: Database va seed

```bash
DROPLET_IP=$(terraform output -raw droplet_ips | head -1)

# Server ga SSH
ssh root@$DROPLET_IP -i ~/.ssh/educrm_deploy

# Migratsiya muvaffaqiyatli o'tganini tekshirish
docker logs educrm_api | grep -i alembic

# Seed data yuklash (ixtiyoriy)
docker exec educrm_api python -m scripts.seed
```

---

## Yuk Testlari (k6)

### C.M3 — Normal Load Test

```bash
LB_IP=$(cd terraform && terraform output -raw load_balancer_ip)

# Test ishlatish
k6 run k6/load_test.js -e BASE_URL=http://$LB_IP

# Natijalarni saqlash
k6 run k6/load_test.js \
    -e BASE_URL=http://$LB_IP \
    --out json=k6/results_before.json \
    --summary-export k6/summary_before.json
```

**Normal load stsenariylari:**

| Faza | Davom | Foydalanuvchilar |
|------|-------|-----------------|
| Isish | 1 min | 0 → 5 |
| Normal yuk | 3 min | 30 |
| Yuqori yuk | 2 min | 60 |
| Sovish | 1 min | 0 |

**SLA maqsadlari:**

| Metrika | Maqsad |
|---------|--------|
| p95 latency | < 2000ms |
| Error rate | < 5% |

### D.M4 — Stress Test (yaxshilanishdan keyin)

```bash
k6 run k6/stress_test.js -e BASE_URL=http://$LB_IP

# Natijalarni saqlash
k6 run k6/stress_test.js \
    -e BASE_URL=http://$LB_IP \
    --out json=k6/results_after.json \
    --summary-export k6/summary_after.json
```

**Natijalarni taqqoslash:**

```bash
# Before vs After
echo "=== BEFORE ===" && jq '.metrics.http_req_duration.values' k6/summary_before.json
echo "=== AFTER ===" && jq '.metrics.http_req_duration.values' k6/summary_after.json
```

---

## Frontend Integrasiya

```bash
# Frontend .env
VITE_API_URL=http://<LOAD_BALANCER_IP>/api/v1

# React Query o'rnatish
npm install @tanstack/react-query axios
```

`src/api/client.ts` faylini yarating:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  timeout: 10_000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401 && !err.config._retry) {
      err.config._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          localStorage.setItem('access_token', data.access_token);
          err.config.headers.Authorization = `Bearer ${data.access_token}`;
          return api(err.config);
        } catch {
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(err);
  }
);

export default api;
```

---

## API Endpointlar

| Method | URL | Tavsif | Auth |
|--------|-----|--------|------|
| `GET` | `/health` | Health check | - |
| `POST` | `/api/v1/auth/login` | Login | - |
| `POST` | `/api/v1/auth/refresh` | Token yangilash | - |
| `POST` | `/api/v1/auth/logout` | Logout | JWT |
| `GET` | `/api/v1/auth/me` | Joriy foydalanuvchi | JWT |
| `GET` | `/api/v1/students/` | O'quvchilar ro'yxati | JWT |
| `POST` | `/api/v1/students/` | O'quvchi qo'shish | Admin |
| `GET` | `/api/v1/teachers/` | O'qituvchilar | JWT |
| `GET` | `/api/v1/groups/` | Guruhlar | JWT |
| `GET` | `/api/v1/attendance/` | Davomat | JWT |
| `POST` | `/api/v1/attendance/` | Davomat kiritish | Teacher+ |
| `GET` | `/api/v1/payments/` | To'lovlar | JWT |
| `POST` | `/api/v1/payments/` | To'lov qo'shish | Admin |
| `GET` | `/api/v1/reports/dashboard` | Dashboard | JWT |
| `GET` | `/api/v1/reports/revenue` | Daromad hisoboti | JWT |
| `GET` | `/api/v1/settings/` | Markaz sozlamalari | JWT |

To'liq API hujjati: `http://<SERVER>/docs`

---

## Localda test o'tkazish

```bash
# Test DB yaratish (PostgreSQL kerak)
createdb educrm_test

# Testlarni ishga tushirish
pytest tests/ -v

# Coverage bilan
pytest tests/ --cov=app --cov-report=html

# Faqat bitta fayl
pytest tests/test_auth.py -v
pytest tests/test_students.py -v
pytest tests/test_payments.py -v
pytest tests/test_reports.py -v
```

---

## Muhim buyruqlar

```bash
# Server da ishlaydigan konteynerlarni ko'rish
ssh root@<DROPLET_IP> docker ps

# API loglarini ko'rish
ssh root@<DROPLET_IP> docker logs educrm_api -f --tail=100

# Manual deploy (CI/CD o'rniga)
ssh root@<DROPLET_IP>
cd /opt/educrm
docker pull registry.digitalocean.com/<REGISTRY>/api:latest
docker compose -f docker-compose.prod.yml up -d --no-build

# Migrations
docker exec educrm_api alembic upgrade head

# Database backup (local ga)
doctl databases backups list <DB_CLUSTER_ID>

# Resurslarni o'chirish
cd terraform && terraform destroy
```

---

## Muhit o'zgaruvchilari

| Variable | Tavsif | Majburiy |
|----------|--------|----------|
| `DATABASE_URL` | PostgreSQL async URL | ✅ |
| `REDIS_URL` | Redis URL | ✅ |
| `SECRET_KEY` | JWT imzolash kaliti (32+ belgi) | ✅ |
| `ALLOWED_ORIGINS` | CORS originlar (vergul bilan) | ✅ |
| `APP_ENV` | `development` yoki `production` | ✅ |
| `DEBUG` | `true`/`false` | ✅ |
| `WORKERS` | Uvicorn worker soni | ✅ |
| `USE_SPACES` | DO Spaces yoqish/o'chirish | ✅ |
| `DO_SPACES_KEY` | Spaces access key | Spaces |
| `DO_SPACES_SECRET` | Spaces secret key | Spaces |
| `DO_SPACES_BUCKET` | Bucket nomi | Spaces |

---

## Muammolarni hal qilish

**Konteynerni restart qilish:**
```bash
docker compose restart api
```

**Migration xatosi:**
```bash
docker exec educrm_api alembic history
docker exec educrm_api alembic current
docker exec educrm_api alembic downgrade -1
```

**PostgreSQL ulanish xatosi:**
```bash
# .env dagi DATABASE_URL ni tekshiring
# SSL: ?ssl=require qo'shilganini tekshiring
docker exec educrm_api python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
async def test():
    e = create_async_engine(settings.DATABASE_URL)
    async with e.connect(): print('OK')
asyncio.run(test())
"
```

**Port band:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

---

## Litsenziya

MIT License — EduCRM Pro
