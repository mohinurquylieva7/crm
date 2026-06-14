# ─── DigitalOcean Container Registry ─────────────────────────────────────────
resource "digitalocean_container_registry" "main" {
  name                   = var.project_name
  subscription_tier_slug = "basic"
  # basic  → 1 repo, 500MB free
  # starter → 5 repo, 5GB  ($5/oy)
  # professional → unlimited ($20/oy)
  region = var.region
}

# Registry docker credentials (Droplet'larda ishlatish uchun)
resource "digitalocean_container_registry_docker_credentials" "main" {
  registry_name = digitalocean_container_registry.main.name
  write         = true
  expiry_seconds = 0  # 0 = hech qachon eskirmasin
}
