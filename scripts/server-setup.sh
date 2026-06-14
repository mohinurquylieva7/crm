#!/bin/bash
# Server first-time setup for crm.ozodbekme.dev
# Run once as root: bash server-setup.sh
set -euo pipefail

DOMAIN="crm.ozodbekme.dev"
EMAIL="sahmadjonov782@gmail.com"
APP_DIR="/opt/educrm"

echo "=== [1/6] System packages ==="
apt-get update -qq
apt-get install -y --no-install-recommends \
    docker.io docker-compose-plugin \
    certbot nginx-light \
    curl wget jq git

systemctl enable --now docker

echo "=== [2/6] App directories ==="
mkdir -p "${APP_DIR}"/{media,logs}
mkdir -p /var/www/certbot

echo "=== [3/6] SSL sertifikat olish (Let's Encrypt) ==="
# Nginx must NOT be running on port 80 yet
# certbot standalone mode
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "${EMAIL}" \
    -d "${DOMAIN}"

echo "=== [4/6] Certbot auto-renewal hook ==="
cat > /etc/cron.d/certbot-renew << 'EOF'
0 3 * * * root certbot renew --quiet --deploy-hook "docker exec educrm_nginx nginx -s reload"
EOF

echo "=== [5/6] .env fayl ==="
if [ ! -f "${APP_DIR}/.env" ]; then
    cat > "${APP_DIR}/.env" << 'ENVEOF'
# ── Database ──────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST:5432/educrm_db

# ── Redis ─────────────────────────────────────────────────────
REDIS_URL=redis://HOST:6379

# ── JWT ───────────────────────────────────────────────────────
SECRET_KEY=CHANGE-ME-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── App ───────────────────────────────────────────────────────
APP_ENV=production
DEBUG=false
WORKERS=2
ALLOWED_ORIGINS=https://crm.ozodbekme.dev

# ── File Storage ──────────────────────────────────────────────
MEDIA_ROOT=/opt/educrm/media
MAX_UPLOAD_SIZE_MB=5
USE_SPACES=false
ENVEOF
    echo "! /opt/educrm/.env faylini to'ldiring va 'bash server-setup.sh' ni qaytadan ishlatmang"
fi

echo "=== [6/6] GHCR_OWNER ni sozlash ==="
cat > "${APP_DIR}/.deploy-env" << EOF
GITHUB_OWNER=OzodbekmeW
IMAGE_TAG=latest
EOF

echo ""
echo "=== Tayyor! ==="
echo "1. /opt/educrm/.env faylini to'ldiring"
echo "2. /opt/educrm/.deploy-env da GITHUB_OWNER ni o'zgartiring"
echo "3. GitHub secrets qo'shing (SSH_PRIVATE_KEY, SSH_HOST, SSH_USER, GHCR_TOKEN)"
echo "4. main ga push qiling — deploy avtomatik boshlanadi"
echo ""
echo "SSL sertifikat: /etc/letsencrypt/live/${DOMAIN}/"
