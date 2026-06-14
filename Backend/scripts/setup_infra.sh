#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
#  EduCRM Pro — Infrastructure Setup
#  Terraform o'zgaruvchilarini interaktiv ravishda sozlaydi va
#  terraform.tfvars faylini yaratadi, so'ng infrani deploy qiladi.
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Ranglar ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()     { echo -e "${CYAN}→ $*${RESET}"; }
success() { echo -e "${GREEN}✓ $*${RESET}"; }
warn()    { echo -e "${YELLOW}⚠  $*${RESET}"; }
error()   { echo -e "${RED}✗ $*${RESET}" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TF_DIR="$ROOT_DIR/terraform"
TFVARS="$TF_DIR/terraform.tfvars"
SSH_KEY_PATH="$HOME/.ssh/educrm_deploy"

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║   EduCRM Pro — Infra Setup Wizard        ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Bog'liqliklarni tekshirish ─────────────────────────────────────────────
log "Bog'liqliklarni tekshirish..."

check_tool() {
    command -v "$1" &>/dev/null || error "$1 o'rnatilmagan. Qo'llanma: $2"
}

check_tool terraform "https://developer.hashicorp.com/terraform/install"
check_tool doctl     "https://docs.digitalocean.com/reference/doctl/how-to/install/"
check_tool openssl   "brew install openssl"
check_tool curl      "brew install curl"

success "Barcha bog'liqliklar mavjud"

# ── 2. DigitalOcean token ─────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[1/5] DigitalOcean API Token${RESET}"
echo "  DO Console → API → Tokens → Generate New Token (Read+Write)"
echo ""
read -rsp "  DO API Token: " DO_TOKEN
echo ""
[ -n "$DO_TOKEN" ] || error "Token bo'sh bo'lishi mumkin emas"

# Token tekshirish
log "Token tekshirilmoqda..."
if ! curl -sf -H "Authorization: Bearer $DO_TOKEN" \
        "https://api.digitalocean.com/v2/account" > /dev/null; then
    error "Token noto'g'ri yoki ruxsat yo'q"
fi
success "Token tasdiqlandi"

# doctl sozlash
doctl auth init --access-token "$DO_TOKEN" 2>/dev/null || true

# ── 3. SSH Key ────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[2/5] SSH Key${RESET}"

if [ -f "$SSH_KEY_PATH" ]; then
    warn "SSH key mavjud: $SSH_KEY_PATH"
    read -rp "  Qayta yaratishni xohlaysizmi? (y/N): " recreate
    recreate="${recreate:-N}"
else
    recreate="y"
fi

if [[ "$recreate" =~ ^[Yy]$ ]]; then
    log "SSH key yaratilmoqda..."
    ssh-keygen -t ed25519 -C "educrm-deploy-$(date +%Y%m%d)" \
        -f "$SSH_KEY_PATH" -N "" -q
    success "SSH key yaratildi: $SSH_KEY_PATH"
fi

# DO ga yuklash
log "SSH key DigitalOcean ga yuklanmoqda..."
KEY_NAME="educrm-deploy"
EXISTING=$(doctl compute ssh-key list --format Name --no-header 2>/dev/null | grep -c "^${KEY_NAME}$" || true)

if [ "$EXISTING" -eq 0 ]; then
    doctl compute ssh-key import "$KEY_NAME" --public-key-file "${SSH_KEY_PATH}.pub"
    success "SSH key DO ga yuklandi"
else
    warn "SSH key '$KEY_NAME' DO da allaqachon mavjud"
fi

# ── 4. Parollar generatsiya ───────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[3/5] Xavfsiz parollar generatsiyasi${RESET}"

log "Kriptografik parollar yaratilmoqda..."
DB_PASSWORD="$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 20)Pp1!"
JWT_SECRET="$(openssl rand -hex 32)"
success "Parollar tayyor"

# ── 5. Email ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[4/5] Alert Email${RESET}"
read -rp "  Email (monitoring uchun): " ALERT_EMAIL
[ -n "$ALERT_EMAIL" ] || error "Email bo'sh bo'lishi mumkin emas"

# ── 6. Joriy IP ──────────────────────────────────────────────────────────────
echo ""
log "Joriy IP aniqlashmoqda..."
MY_IP="$(curl -sf https://ifconfig.me || curl -sf https://api.ipify.org || echo "0.0.0.0")"
ADMIN_IP="${MY_IP}/32"
success "Admin IP: $ADMIN_IP"

# ── 7. terraform.tfvars yaratish ─────────────────────────────────────────────
echo ""
echo -e "${BOLD}[5/5] terraform.tfvars yaratilmoqda${RESET}"

cat > "$TFVARS" << EOF
# ══════════════════════════════════════════════════════════════════
#  terraform.tfvars — AUTO GENERATED $(date '+%Y-%m-%d %H:%M:%S')
#  DIQQAT: Bu fayl .gitignore da! Hech qachon commit qilmang!
# ══════════════════════════════════════════════════════════════════

do_token       = "${DO_TOKEN}"
ssh_key_name   = "educrm-deploy"
admin_ip       = "${ADMIN_IP}"
db_password    = "${DB_PASSWORD}"
jwt_secret_key = "${JWT_SECRET}"
alert_email    = "${ALERT_EMAIL}"
EOF

chmod 600 "$TFVARS"
success "terraform.tfvars yaratildi (chmod 600)"

# ── 8. Maxfiy ma'lumotlarni saqlash ──────────────────────────────────────────
SECRETS_FILE="$ROOT_DIR/.deploy_secrets"
cat > "$SECRETS_FILE" << EOF
# EduCRM Deploy Secrets — $(date '+%Y-%m-%d %H:%M:%S')
# SAQLAB QOYING — keyingi qadamlarda kerak bo'ladi
DO_TOKEN=${DO_TOKEN}
DB_PASSWORD=${DB_PASSWORD}
JWT_SECRET=${JWT_SECRET}
SSH_KEY_PATH=${SSH_KEY_PATH}
ADMIN_IP=${ADMIN_IP}
EOF
chmod 600 "$SECRETS_FILE"
warn "Maxfiy ma'lumotlar saqlandi: .deploy_secrets (gitignore da)"

# ── Xulosa ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${GREEN}║   Setup tugadi! Keyingi qadamlar:        ║${RESET}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo "  1. make infra-init    — Terraform init"
echo "  2. make infra-plan    — Ko'rib chiqing"
echo "  3. make infra-apply   — Infra yaratish (~5-8 daqiqa)"
echo "  4. make secrets       — GitHub Secrets sozlash"
echo "  5. git push origin main → CD pipeline"
echo ""
echo -e "  SSH key: ${CYAN}$SSH_KEY_PATH${RESET}"
echo -e "  DB:      ${CYAN}$DB_PASSWORD${RESET}"
echo -e "  JWT:     ${CYAN}$JWT_SECRET${RESET}"
echo ""
