# ─── Managed PostgreSQL ───────────────────────────────────────────────────────
resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project_name}-postgres"
  engine     = "pg"
  version    = "15"
  size       = "db-s-1vcpu-1gb"
  # Prod upgrade: db-s-1vcpu-2gb ($50/oy) yoki db-s-2vcpu-4gb ($100/oy)
  region     = var.region
  node_count = 1
  # Prod da node_count = 2 (hot standby + failover)

  private_network_uuid = digitalocean_vpc.main.id
  tags                 = [var.project_name]
}

# Database
resource "digitalocean_database_db" "educrm" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "educrm_db"
}

# App foydalanuvchisi
resource "digitalocean_database_user" "app_user" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_user
}

# Faqat app Droplet'lardan ulanishga ruxsat
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id

  dynamic "rule" {
    for_each = digitalocean_droplet.app
    content {
      type  = "droplet"
      value = rule.value.id
    }
  }
}

# ─── Managed Redis ────────────────────────────────────────────────────────────
resource "digitalocean_database_cluster" "redis" {
  name       = "${var.project_name}-redis"
  engine     = "redis"
  version    = "7"
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1

  private_network_uuid = digitalocean_vpc.main.id
  tags                 = [var.project_name]
}

resource "digitalocean_database_firewall" "redis" {
  cluster_id = digitalocean_database_cluster.redis.id

  dynamic "rule" {
    for_each = digitalocean_droplet.app
    content {
      type  = "droplet"
      value = rule.value.id
    }
  }
}
