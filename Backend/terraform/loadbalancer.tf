# ─── Load Balancer ────────────────────────────────────────────────────────────
resource "digitalocean_loadbalancer" "main" {
  name   = "${var.project_name}-lb"
  region = var.region

  droplet_tag = var.project_name
  vpc_uuid    = digitalocean_vpc.main.id

  # ── HTTP ─────────────────────────────────────────────────────────────────
  forwarding_rule {
    entry_port      = 80
    entry_protocol  = "http"
    target_port     = 8000
    target_protocol = "http"
  }

  # ── HTTPS (SSL sertifikat qo'shilgandan keyin uncomment qiling) ──────────
  # forwarding_rule {
  #   entry_port       = 443
  #   entry_protocol   = "https"
  #   target_port      = 8000
  #   target_protocol  = "http"
  #   certificate_name = digitalocean_certificate.main.name
  #   tls_passthrough  = false
  # }

  # ── HTTP → HTTPS redirect ─────────────────────────────────────────────────
  # redirect_http_to_https = true  # HTTPS yoqilgandan keyin

  # ── Health check ─────────────────────────────────────────────────────────
  healthcheck {
    port                     = 8000
    protocol                 = "http"
    path                     = "/health"
    healthy_threshold        = 2
    unhealthy_threshold      = 3
    check_interval_seconds   = 15
    response_timeout_seconds = 5
  }

  # ── Sticky sessions ───────────────────────────────────────────────────────
  sticky_sessions {
    type               = "cookies"
    cookie_name        = "educrm_lb"
    cookie_ttl_seconds = 300
  }

  # ── Algorithm ─────────────────────────────────────────────────────────────
  algorithm = "round_robin"
}

# ─── Let's Encrypt SSL (domenga bog'langan bo'lsa) ───────────────────────────
# resource "digitalocean_certificate" "main" {
#   name    = "${var.project_name}-cert"
#   type    = "lets_encrypt"
#   domains = ["yourdomain.com", "www.yourdomain.com"]
# }
