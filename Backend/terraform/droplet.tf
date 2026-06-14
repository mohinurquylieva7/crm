# ─── App Droplet(lar) ─────────────────────────────────────────────────────────
resource "digitalocean_droplet" "app" {
  count  = var.droplet_count
  name   = "${var.project_name}-app-${count.index + 1}"
  image  = "ubuntu-22-04-x64"
  size   = var.droplet_size
  region = var.region

  vpc_uuid = digitalocean_vpc.main.id
  ssh_keys = [data.digitalocean_ssh_key.admin.id]

  monitoring = true
  backups    = false  # Prod da true qiling ($0.2/GB/oy)

  user_data = templatefile("${path.module}/userdata.sh", {
    db_url          = "postgresql+asyncpg://${var.db_user}:${var.db_password}@${digitalocean_database_cluster.postgres.private_host}:${digitalocean_database_cluster.postgres.port}/educrm_db?ssl=require"
    redis_url       = "rediss://:${digitalocean_database_cluster.redis.password}@${digitalocean_database_cluster.redis.private_host}:${digitalocean_database_cluster.redis.port}"
    secret_key      = var.jwt_secret_key
    allowed_origins = var.allowed_origins
    spaces_key      = var.spaces_access_key
    spaces_secret   = var.spaces_secret_key
    spaces_region   = var.region
    spaces_bucket   = "${var.project_name}-media"
    spaces_endpoint = "https://${var.region}.digitaloceanspaces.com"
    project_name    = var.project_name
    registry_url    = "registry.digitalocean.com/${var.project_name}"
  })

  tags = [var.project_name, "app"]

  lifecycle {
    create_before_destroy = true
  }
}

# ─── CPU Alert (monitoring) ───────────────────────────────────────────────────
resource "digitalocean_monitor_alert" "cpu_high" {
  count   = var.alert_email != "" ? 1 : 0
  alerts {
    email = [var.alert_email]
  }
  window      = "5m"
  type        = "v1/insights/droplet/cpu"
  compare     = "GreaterThan"
  value       = 85
  enabled     = true
  entities    = digitalocean_droplet.app[*].id
  description = "${var.project_name} — CPU > 85%"
}

resource "digitalocean_monitor_alert" "memory_high" {
  count   = var.alert_email != "" ? 1 : 0
  alerts {
    email = [var.alert_email]
  }
  window      = "5m"
  type        = "v1/insights/droplet/memory_utilization_percent"
  compare     = "GreaterThan"
  value       = 90
  enabled     = true
  entities    = digitalocean_droplet.app[*].id
  description = "${var.project_name} — Memory > 90%"
}
