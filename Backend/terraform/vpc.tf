# ─── VPC — Private networking ─────────────────────────────────────────────────
resource "digitalocean_vpc" "main" {
  name     = "${var.project_name}-vpc"
  region   = var.region
  ip_range = "10.10.0.0/16"
}

# ─── DO Project — resurslarni guruhlash ──────────────────────────────────────
resource "digitalocean_project" "main" {
  name        = var.project_name
  description = "EduCRM Pro — o'quv markaz boshqaruv tizimi"
  purpose     = "Web Application"
  environment = "Production"

  resources = concat(
    [for d in digitalocean_droplet.app : d.urn],
    [
      digitalocean_loadbalancer.main.urn,
      digitalocean_database_cluster.postgres.urn,
      digitalocean_database_cluster.redis.urn,
      digitalocean_spaces_bucket.media.urn,
      digitalocean_container_registry.main.urn,
    ]
  )
}

# ─── Uptime monitoring ────────────────────────────────────────────────────────
resource "digitalocean_uptime_check" "health" {
  name    = "${var.project_name}-health"
  target  = "http://${digitalocean_loadbalancer.main.ip}/health"
  regions = ["eu_west", "us_east"]
}

resource "digitalocean_uptime_alert" "health_down" {
  name       = "${var.project_name}-down-alert"
  check_id   = digitalocean_uptime_check.health.id
  type       = "down"
  threshold  = 3
  comparison = "less_than"
  period     = "2m"

  dynamic "notifications" {
    for_each = var.alert_email != "" ? [1] : []
    content {
      email = [var.alert_email]
    }
  }
}
