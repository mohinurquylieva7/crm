#!/bin/bash
set -euo pipefail

LOG=/var/log/educrm-setup.log
exec > >(tee -a "$LOG") 2>&1

echo "========================================"
echo " EduCRM Pro — Server Bootstrap"
echo " $(date)"
echo "========================================"

# ── 1. Tizim yangilash ────────────────────────────────────────────────────────
echo "[1/8] Tizim yangilanmoqda..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y
apt-get install -y --no-install-recommends \
    curl wget git unzip ca-certificates gnupg \
    lsb-release apt-transport-https software-properties-common \
    htop jq fail2ban ufw

# ── 2. Docker o'rnatish ───────────────────────────────────────────────────────
echo "[2/8] Docker o'rnatilmoqda..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker Compose (standalone) ham o'rnatamiz
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest \
    | jq -r '.tag_name' 2>/dev/null || echo "v2.27.0")
curl -SL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

systemctl enable docker
systemctl start docker

# ── 3. doctl (DigitalOcean CLI) o'rnatish ────────────────────────────────────
echo "[3/8] doctl o'rnatilmoqda..."
DOCTL_VERSION="1.107.0"
curl -sL "https://github.com/digitalocean/doctl/releases/download/v$${DOCTL_VERSION}/doctl-$${DOCTL_VERSION}-linux-amd64.tar.gz" \
    | tar -xzv -C /tmp
mv /tmp/doctl /usr/local/bin/doctl
chmod +x /usr/local/bin/doctl

# ── 4. App papkasi va .env ────────────────────────────────────────────────────
echo "[4/8] App papkasi yaratilmoqda..."
mkdir -p /opt/educrm/{media,logs,nginx,ssl}
chmod 755 /opt/educrm

cat > /opt/educrm/.env << 'ENVEOF'
DATABASE_URL=${db_url}
REDIS_URL=${redis_url}
SECRET_KEY=${secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=production
DEBUG=false
WORKERS=2
ALLOWED_ORIGINS=${allowed_origins}
MEDIA_ROOT=/opt/educrm/media
MAX_UPLOAD_SIZE_MB=5
USE_SPACES=true
DO_SPACES_KEY=${spaces_key}
DO_SPACES_SECRET=${spaces_secret}
DO_SPACES_REGION=${spaces_region}
DO_SPACES_BUCKET=${spaces_bucket}
DO_SPACES_ENDPOINT=${spaces_endpoint}
ENVEOF

chmod 600 /opt/educrm/.env

# ── 5. Nginx config ───────────────────────────────────────────────────────────
echo "[5/8] Nginx config yozilmoqda..."
cat > /opt/educrm/nginx.conf << 'NGINXEOF'
upstream api_backend {
    server api:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 10M;

    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";

    location = /health {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        access_log off;
    }

    location /media/ {
        alias /var/www/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
    }

    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }

    location /docs {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://api_backend;
    }

    location /redoc {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
    }
}
NGINXEOF

# ── 6. Xavfsizlik sozlamalari ─────────────────────────────────────────────────
echo "[6/8] Xavfsizlik sozlanmoqda..."

# UFW firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

# fail2ban SSH himoyasi
systemctl enable fail2ban
systemctl start fail2ban

# ── 7. Docker Compose prod fayli ─────────────────────────────────────────────
echo "[7/8] docker-compose.prod.yml yozilmoqda..."
cat > /opt/educrm/docker-compose.prod.yml << 'COMPOSEEOF'
version: "3.9"

services:
  api:
    image: ${registry_url}/api:latest
    container_name: educrm_api
    restart: always
    env_file: /opt/educrm/.env
    ports:
      - "8000:8000"
    volumes:
      - /opt/educrm/media:/app/media
      - /opt/educrm/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: educrm_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      api:
        condition: service_healthy
    volumes:
      - /opt/educrm/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /opt/educrm/media:/var/www/media:ro
      - /opt/educrm/ssl:/etc/nginx/ssl:ro
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "3"
COMPOSEEOF

# ── 8. Logrotate ──────────────────────────────────────────────────────────────
echo "[8/8] Logrotate sozlanmoqda..."
cat > /etc/logrotate.d/educrm << 'LOGREOF'
/opt/educrm/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
LOGREOF

echo "========================================"
echo " ✅ Server bootstrap muvaffaqiyatli!"
echo " Keyingi qadam: CI/CD pipeline ishga tushgach"
echo " docker-compose.prod.yml da image deploy bo'ladi"
echo "========================================"
