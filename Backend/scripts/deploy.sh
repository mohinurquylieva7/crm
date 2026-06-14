#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
#  EduCRM Pro — Manual Production Deploy Script
#  CI/CD yo'q yoki shoshilinch hotfix kerak bo'lganda ishlatiladi.
#
#  Ishga tushirish:
#    bash scripts/deploy.sh
#    bash scripts/deploy.sh --tag v1.2.3    (aniq versiyani deploy qilish)
#    bash scripts/deploy.sh --rollback      (oldingi versiyaga qaytish)
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()     { echo -e "${CYAN}[$(date '+%H:%M:%S')] → $*${RESET}"; }
success() { echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓ $*${RESET}"; }
warn()    { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠  $*${RESET}"; }
error()   { echo -e "${RED}[$(date '+%H:%M:%S')] ✗ $*${RESET}" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TF_DIR="$ROOT_DIR/terraform"
SECRETS_FILE="$ROOT_DIR/.deploy_secrets"

IMAGE_TAG="latest"
ROLLBACK=false

# ── Argumentlarni parse qilish ────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag)      IMAGE_TAG="$2"; shift 2 ;;
        --rollback) ROLLBACK=true; shift ;;
        *) error "Noto'g'ri argument: $1" ;;
    esac
done

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║   EduCRM Pro — Production Deploy         ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ── Bog'liqliklar ─────────────────────────────────────────────────────────────
command -v docker    &>/dev/null || error "Docker o'rnatilmagan"
command -v terraform &>/dev/null || error "Terraform o'rnatilmagan"
command -v doctl     &>/dev/null || error "doctl o'rnatilmagan"

# ── Maxfiy ma'lumotlarni yuklash ───────────────────────────────────────────────
[ -f "$SECRETS_FILE" ] || error ".deploy_secrets topilmadi. setup_infra.sh ni ishga tushiring"
# shellcheck disable=SC1090
source "$SECRETS_FILE"

# ── Terraform output ──────────────────────────────────────────────────────────
log "Infra ma'lumotlari olinmoqda..."
cd "$TF_DIR"

DROPLET_IP=$(terraform output -json droplet_ips 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0] if d else '')" 2>/dev/null || echo "")
REGISTRY_NAME=$(terraform output -raw registry_name 2>/dev/null || echo "")
REGISTRY_URL="registry.digitalocean.com/${REGISTRY_NAME}"

[ -n "$DROPLET_IP" ]   || error "Droplet IP topilmadi. 'make infra-apply' ni tekshiring"
[ -n "$REGISTRY_NAME" ] || error "Registry nomi topilmadi"

cd "$ROOT_DIR"

log "Deploy target:"
echo "  Server:   $DROPLET_IP"
echo "  Registry: $REGISTRY_URL"
echo "  Tag:      $IMAGE_TAG"
echo "  Rollback: $ROLLBACK"
echo ""

# ── Rollback ──────────────────────────────────────────────────────────────────
if [ "$ROLLBACK" = true ]; then
    warn "ROLLBACK rejimi — oldingi versiyaga qaytilmoqda..."
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "root@$DROPLET_IP" << 'ENDSSH'
        cd /opt/educrm
        PREV_TAG=$(docker images --format "{{.Tag}}" registry.digitalocean.com/*/api \
            | grep -v latest | sort -V | tail -2 | head -1)
        if [ -z "$PREV_TAG" ]; then
            echo "Oldingi versiya topilmadi!"
            exit 1
        fi
        echo "Rollback → $PREV_TAG"
        export IMAGE_TAG="$PREV_TAG"
        docker compose -f docker-compose.prod.yml up -d --no-build
        sleep 10
        curl -sf http://localhost/health && echo "✓ Rollback OK" || echo "✗ Health check failed"
ENDSSH
    success "Rollback bajarildi"
    exit 0
fi

# ── Docker build & push ───────────────────────────────────────────────────────
log "STEP 1/4: Docker image build qilinmoqda..."
docker build -t "${REGISTRY_URL}/api:${IMAGE_TAG}" -t "${REGISTRY_URL}/api:latest" .
success "Build OK"

log "STEP 2/4: DOCR ga login..."
doctl auth init --access-token "$DO_TOKEN"
doctl registry login
success "DOCR login OK"

log "STEP 3/4: Image push qilinmoqda..."
docker push "${REGISTRY_URL}/api:${IMAGE_TAG}"
[ "$IMAGE_TAG" != "latest" ] && docker push "${REGISTRY_URL}/api:latest"
success "Push OK: ${REGISTRY_URL}/api:${IMAGE_TAG}"

# ── Server deploy ─────────────────────────────────────────────────────────────
log "STEP 4/4: Server ga deploy..."

ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "root@$DROPLET_IP" \
    IMAGE_TAG="$IMAGE_TAG" REGISTRY="$REGISTRY_URL" \
    << 'ENDSSH'
    set -e
    echo "=== Server deploy ==="
    cd /opt/educrm

    # Registry login
    doctl registry login

    # Image pull
    echo "Image pull..."
    docker pull "${REGISTRY}/api:${IMAGE_TAG}"
    docker tag "${REGISTRY}/api:${IMAGE_TAG}" "${REGISTRY}/api:latest"

    # Migratsiya
    echo "Alembic migratsiya..."
    docker run --rm \
        --env-file /opt/educrm/.env \
        "${REGISTRY}/api:latest" \
        alembic upgrade head

    # Zero-downtime restart (rolling update simulation)
    echo "Konteynerni yangilanmoqda..."
    export IMAGE_TAG REGISTRY
    docker compose -f docker-compose.prod.yml up -d --no-build

    # Health check — 5 urinish
    echo "Health check..."
    for i in $(seq 1 5); do
        sleep 5
        if curl -sf http://localhost/health > /dev/null 2>&1; then
            echo "✓ Health check muvaffaqiyatli (urinish $i)"
            break
        fi
        echo "  Urinish $i/5 — kutilmoqda..."
        if [ "$i" -eq 5 ]; then
            echo "✗ Health check muvaffaqiyatsiz!"
            docker logs educrm_api --tail=50
            exit 1
        fi
    done

    # Eski imaglarni tozalash
    docker image prune -f
    echo "=== Deploy muvaffaqiyatli ==="
ENDSSH

# ── Deploy tekshirish ─────────────────────────────────────────────────────────
log "Deploy tekshirilmoqda..."
LB_IP=$(cd "$TF_DIR" && terraform output -raw load_balancer_ip 2>/dev/null || echo "$DROPLET_IP")

HEALTH_RESPONSE=$(curl -sf "http://${LB_IP}/health" || echo "")
if echo "$HEALTH_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('db')=='connected' else 1)" 2>/dev/null; then
    success "Production health OK"
else
    error "Health check muvaffaqiyatsiz: $HEALTH_RESPONSE"
fi

# ── Xulosa ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${GREEN}║   Deploy muvaffaqiyatli!                 ║${RESET}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  URL:     ${CYAN}http://${LB_IP}${RESET}"
echo -e "  Docs:    ${CYAN}http://${LB_IP}/docs${RESET}"
echo -e "  Health:  ${CYAN}http://${LB_IP}/health${RESET}"
echo -e "  Tag:     ${CYAN}${IMAGE_TAG}${RESET}"
echo ""
echo "  Rollback kerak bo'lsa:"
echo "  bash scripts/deploy.sh --rollback"
echo ""
