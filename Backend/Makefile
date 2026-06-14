# ══════════════════════════════════════════════════════════════════════════════
#  EduCRM Pro — Makefile
#  Barcha operatsiyalar uchun yagona buyruq markazi
#  Foydalanish: make <target>
# ══════════════════════════════════════════════════════════════════════════════

.DEFAULT_GOAL := help
.PHONY: help dev stop restart logs shell migrate seed test lint fmt build \
        infra-init infra-plan infra-apply infra-destroy secrets deploy \
        load-test stress-test compare-results clean

# ── Ranglar ───────────────────────────────────────────────────────────────────
BOLD   := \033[1m
GREEN  := \033[32m
YELLOW := \033[33m
CYAN   := \033[36m
RESET  := \033[0m

# ── O'zgaruvchilar ────────────────────────────────────────────────────────────
COMPOSE        := docker compose
COMPOSE_PROD   := docker compose -f docker-compose.prod.yml
API_CONTAINER  := api
TF_DIR         := terraform
K6_DIR         := k6

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(BOLD)$(CYAN) EduCRM Pro — Buyruqlar$(RESET)"
	@echo "$(CYAN)══════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)$(YELLOW) LOCAL DEV$(RESET)"
	@echo "  $(GREEN)make dev$(RESET)            — Docker Compose bilan ishga tushirish"
	@echo "  $(GREEN)make stop$(RESET)           — Konteynerlarni to'xtatish"
	@echo "  $(GREEN)make restart$(RESET)        — API ni restart qilish"
	@echo "  $(GREEN)make logs$(RESET)           — API loglarini ko'rish (real-time)"
	@echo "  $(GREEN)make shell$(RESET)          — API konteyneriga kirish"
	@echo "  $(GREEN)make migrate$(RESET)        — Alembic migratsiya"
	@echo "  $(GREEN)make seed$(RESET)           — Test ma'lumotlarini yuklash"
	@echo ""
	@echo "$(BOLD)$(YELLOW) TEST & QUALITY$(RESET)"
	@echo "  $(GREEN)make test$(RESET)           — pytest (barcha testlar)"
	@echo "  $(GREEN)make test-cov$(RESET)       — pytest + coverage hisoboti"
	@echo "  $(GREEN)make lint$(RESET)           — ruff + mypy tekshiruv"
	@echo "  $(GREEN)make fmt$(RESET)            — ruff format (auto)"
	@echo ""
	@echo "$(BOLD)$(YELLOW) DOCKER$(RESET)"
	@echo "  $(GREEN)make build$(RESET)          — Docker image build"
	@echo "  $(GREEN)make clean$(RESET)          — Konteyner + volume + image tozalash"
	@echo ""
	@echo "$(BOLD)$(YELLOW) INFRASTRUCTURE$(RESET)"
	@echo "  $(GREEN)make infra-init$(RESET)     — Terraform init"
	@echo "  $(GREEN)make infra-plan$(RESET)     — Terraform plan (ko'rish)"
	@echo "  $(GREEN)make infra-apply$(RESET)    — Terraform apply (infra yaratish)"
	@echo "  $(GREEN)make infra-destroy$(RESET)  — Terraform destroy (o'chirish!)"
	@echo ""
	@echo "$(BOLD)$(YELLOW) DEPLOY$(RESET)"
	@echo "  $(GREEN)make secrets$(RESET)        — GitHub Secrets avtomatik sozlash"
	@echo "  $(GREEN)make deploy$(RESET)         — Manual production deploy"
	@echo ""
	@echo "$(BOLD)$(YELLOW) LOAD TESTING$(RESET)"
	@echo "  $(GREEN)make load-test$(RESET)      — C.M3 Normal yuk testi"
	@echo "  $(GREEN)make stress-test$(RESET)    — D.M4 Stress testi"
	@echo "  $(GREEN)make compare$(RESET)        — Before vs After natijalarni taqqoslash"
	@echo ""

# ══════════════════════════════════════════════════════════════════════════════
#  LOCAL DEV
# ══════════════════════════════════════════════════════════════════════════════

dev:
	@echo "$(CYAN)→ Local dev muhit ishga tushmoqda...$(RESET)"
	@[ -f .env ] || (cp .env.example .env && echo "$(YELLOW)⚠  .env yaratildi — tekshiring!$(RESET)")
	$(COMPOSE) up -d --build
	@echo ""
	@echo "$(GREEN)✓ Ishga tushdi!$(RESET)"
	@echo "  Swagger:  http://localhost/docs"
	@echo "  Health:   http://localhost/health"
	@echo "  Admin:    admin@educrm.uz / Admin1234!"

stop:
	@echo "$(CYAN)→ To'xtatilmoqda...$(RESET)"
	$(COMPOSE) down

restart:
	@echo "$(CYAN)→ API restart...$(RESET)"
	$(COMPOSE) restart $(API_CONTAINER)

logs:
	$(COMPOSE) logs -f $(API_CONTAINER)

shell:
	$(COMPOSE) exec $(API_CONTAINER) /bin/bash

migrate:
	@echo "$(CYAN)→ Migratsiya ishga tushmoqda...$(RESET)"
	$(COMPOSE) exec $(API_CONTAINER) alembic upgrade head
	@echo "$(GREEN)✓ Migratsiya bajarildi$(RESET)"

seed:
	@echo "$(CYAN)→ Seed ma'lumotlar yuklanmoqda...$(RESET)"
	$(COMPOSE) exec $(API_CONTAINER) python -m scripts.seed
	@echo "$(GREEN)✓ Seed bajarildi$(RESET)"

# ══════════════════════════════════════════════════════════════════════════════
#  TEST & QUALITY
# ══════════════════════════════════════════════════════════════════════════════

test:
	@echo "$(CYAN)→ Testlar ishga tushmoqda...$(RESET)"
	$(COMPOSE) exec $(API_CONTAINER) pytest tests/ -v --tb=short

test-cov:
	@echo "$(CYAN)→ Coverage bilan test...$(RESET)"
	$(COMPOSE) exec $(API_CONTAINER) pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-fail-under=70
	@echo "$(GREEN)✓ HTML hisobot: htmlcov/index.html$(RESET)"

lint:
	@echo "$(CYAN)→ Lint tekshiruvi...$(RESET)"
	$(COMPOSE) exec $(API_CONTAINER) ruff check app/ tests/
	$(COMPOSE) exec $(API_CONTAINER) ruff check --select I app/ tests/
	@echo "$(GREEN)✓ Lint OK$(RESET)"

fmt:
	@echo "$(CYAN)→ Kodni formatlash...$(RESET)"
	$(COMPOSE) exec $(API_CONTAINER) ruff format app/ tests/
	$(COMPOSE) exec $(API_CONTAINER) ruff check --fix app/ tests/
	@echo "$(GREEN)✓ Format OK$(RESET)"

# ══════════════════════════════════════════════════════════════════════════════
#  DOCKER
# ══════════════════════════════════════════════════════════════════════════════

build:
	@echo "$(CYAN)→ Docker image build...$(RESET)"
	docker build -t educrm-api:local .
	@echo "$(GREEN)✓ Build OK: educrm-api:local$(RESET)"

clean:
	@echo "$(YELLOW)⚠  Konteyner, volume va image tozalanmoqda...$(RESET)"
	$(COMPOSE) down -v --remove-orphans
	docker image prune -f
	@echo "$(GREEN)✓ Tozalandi$(RESET)"

# ══════════════════════════════════════════════════════════════════════════════
#  INFRASTRUCTURE (Terraform)
# ══════════════════════════════════════════════════════════════════════════════

infra-init:
	@echo "$(CYAN)→ Terraform init...$(RESET)"
	cd $(TF_DIR) && terraform init
	@echo "$(GREEN)✓ Init OK$(RESET)"

infra-plan:
	@echo "$(CYAN)→ Terraform plan...$(RESET)"
	@[ -f $(TF_DIR)/terraform.tfvars ] || \
		(echo "$(YELLOW)⚠  terraform.tfvars topilmadi! scripts/setup_infra.sh ni ishga tushiring$(RESET)" && exit 1)
	cd $(TF_DIR) && terraform plan -out=tfplan
	@echo ""
	@echo "$(GREEN)✓ Plan tayyor. 'make infra-apply' bilan tasdiqlang$(RESET)"

infra-apply:
	@echo "$(CYAN)→ Terraform apply — DigitalOcean resurslar yaratilmoqda...$(RESET)"
	@[ -f $(TF_DIR)/tfplan ] || (cd $(TF_DIR) && terraform plan -out=tfplan)
	cd $(TF_DIR) && terraform apply tfplan
	@echo ""
	@echo "$(GREEN)✓ Infra tayyor!$(RESET)"
	@cd $(TF_DIR) && terraform output

infra-destroy:
	@echo "$(YELLOW)⚠  DIQQAT: Barcha DigitalOcean resurslari O'CHIRILADI!$(RESET)"
	@read -p "Davom etasizmi? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	cd $(TF_DIR) && terraform destroy
	@echo "$(GREEN)✓ Infra o'chirildi$(RESET)"

# ══════════════════════════════════════════════════════════════════════════════
#  DEPLOY
# ══════════════════════════════════════════════════════════════════════════════

secrets:
	@echo "$(CYAN)→ GitHub Secrets sozlanmoqda...$(RESET)"
	@bash scripts/setup_secrets.sh

deploy:
	@echo "$(CYAN)→ Production deploy...$(RESET)"
	@bash scripts/deploy.sh

# ══════════════════════════════════════════════════════════════════════════════
#  LOAD TESTING
# ══════════════════════════════════════════════════════════════════════════════

LB_IP := $(shell cd $(TF_DIR) 2>/dev/null && terraform output -raw load_balancer_ip 2>/dev/null || echo "localhost")

load-test:
	@echo "$(CYAN)→ C.M3 Normal Load Test — Target: http://$(LB_IP)$(RESET)"
	@which k6 > /dev/null 2>&1 || (echo "$(YELLOW)k6 o'rnatilmagan: brew install k6$(RESET)" && exit 1)
	k6 run $(K6_DIR)/load_test.js \
		-e BASE_URL=http://$(LB_IP) \
		--out json=$(K6_DIR)/results_before.json \
		--summary-export $(K6_DIR)/summary_before.json
	@echo "$(GREEN)✓ Natijalar: $(K6_DIR)/summary_before.json$(RESET)"

stress-test:
	@echo "$(CYAN)→ D.M4 Stress Test — Target: http://$(LB_IP)$(RESET)"
	@which k6 > /dev/null 2>&1 || (echo "$(YELLOW)k6 o'rnatilmagan: brew install k6$(RESET)" && exit 1)
	k6 run $(K6_DIR)/stress_test.js \
		-e BASE_URL=http://$(LB_IP) \
		--out json=$(K6_DIR)/results_after.json \
		--summary-export $(K6_DIR)/summary_after.json
	@echo "$(GREEN)✓ Natijalar: $(K6_DIR)/summary_after.json$(RESET)"

compare:
	@echo "$(CYAN)→ Before vs After taqqoslash$(RESET)"
	@bash scripts/compare_results.sh
