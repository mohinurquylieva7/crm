#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
#  EduCRM Pro — GitHub Secrets Auto Setup
#  Terraform output dan qiymatlarni olib, GitHub repo ga secrets qo'shadi.
#
#  Talablar: gh (GitHub CLI), terraform
#  Ishga tushirish: bash scripts/setup_secrets.sh
#            yoki: make secrets
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()     { echo -e "${CYAN}→ $*${RESET}"; }
success() { echo -e "${GREEN}✓ $*${RESET}"; }
warn()    { echo -e "${YELLOW}⚠  $*${RESET}"; }
error()   { echo -e "${RED}✗ $*${RESET}" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TF_DIR="$ROOT_DIR/terraform"
SECRETS_FILE="$ROOT_DIR/.deploy_secrets"
SSH_KEY_PATH="${HOME}/.ssh/educrm_deploy"

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║   EduCRM Pro — GitHub Secrets Setup      ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── Bog'liqliklarni tekshirish ─────────────────────────────────────────────────
command -v gh        &>/dev/null || error "GitHub CLI o'rnatilmagan: brew install gh"
command -v terraform &>/dev/null || error "Terraform o'rnatilmagan"

# ── GitHub autentifikatsiya ────────────────────────────────────────────────────
log "GitHub autentifikatsiya tekshirilmoqda..."
if ! gh auth status &>/dev/null; then
    warn "GitHub ga login qilinmagan"
    gh auth login
fi
success "GitHub autentifikatsiya OK"

# ── Repo aniqlash ─────────────────────────────────────────────────────────────
log "GitHub repository aniqlashmoqda..."
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [ -z "$REPO" ]; then
    echo ""
    read -rp "  GitHub repo (format: username/repo-name): " REPO
fi
[ -n "$REPO" ] || error "Repo ko'rsatilmadi"
success "Repo: $REPO"

# ── Terraform output dan qiymatlar ────────────────────────────────────────────
log "Terraform output dan qiymatlar olinmoqda..."

cd "$TF_DIR"
TF_INITIALIZED=$(terraform workspace list 2>/dev/null | head -1 || echo "")
if [ -z "$TF_INITIALIZED" ]; then
    error "Terraform init qilinmagan. Avval: make infra-apply"
fi

DO_TOKEN=""
REGISTRY_NAME=""

if [ -f "$SECRETS_FILE" ]; then
    # shellcheck disable=SC1090
    source "$SECRETS_FILE"
fi

# Terraform output dan
REGISTRY_NAME=$(terraform output -raw registry_name 2>/dev/null || echo "")
[ -n "$REGISTRY_NAME" ] || {
    warn "Terraform output topilmadi"
    read -rp "  DOCR registry nomi (terraform output registry_name): " REGISTRY_NAME
}

# DO Token
[ -n "$DO_TOKEN" ] || {
    read -rsp "  DigitalOcean API Token: " DO_TOKEN
    echo ""
}

# SSH Private Key
SSH_PRIVATE_KEY=""
if [ -f "$SSH_KEY_PATH" ]; then
    SSH_PRIVATE_KEY=$(cat "$SSH_KEY_PATH")
    success "SSH key topildi: $SSH_KEY_PATH"
else
    warn "SSH key topilmadi: $SSH_KEY_PATH"
    read -rp "  SSH private key fayl yo'li: " custom_key_path
    SSH_PRIVATE_KEY=$(cat "$custom_key_path")
fi

cd "$ROOT_DIR"

# ── Secrets yozish ─────────────────────────────────────────────────────────────
echo ""
log "GitHub Secrets yozilmoqda..."

set_secret() {
    local name="$1"
    local value="$2"
    echo -n "  Setting $name ... "
    echo "$value" | gh secret set "$name" --repo "$REPO" --body -
    echo -e "${GREEN}✓${RESET}"
}

set_secret "DO_TOKEN"           "$DO_TOKEN"
set_secret "DO_SSH_PRIVATE_KEY" "$SSH_PRIVATE_KEY"
set_secret "DO_REGISTRY_NAME"   "$REGISTRY_NAME"

echo ""
success "Barcha secrets GitHub ga yozildi!"

# ── CD pipeline tekshirish ────────────────────────────────────────────────────
echo ""
log "Mavjud secrets ro'yxati:"
gh secret list --repo "$REPO"

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${GREEN}║   Secrets sozlandi! Keyingi qadam:       ║${RESET}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo "  git add ."
echo "  git commit -m 'feat: initial production deploy'"
echo "  git push origin main"
echo ""
echo -e "  CD pipeline kuzating:"
echo -e "  ${CYAN}https://github.com/$REPO/actions${RESET}"
echo ""
