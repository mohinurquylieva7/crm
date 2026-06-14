output "load_balancer_ip" {
  description = "Load Balancer public IP — DNS A record uchun"
  value       = digitalocean_loadbalancer.main.ip
}

output "droplet_ips" {
  description = "App Droplet public IP'lari (SSH uchun)"
  value       = digitalocean_droplet.app[*].ipv4_address
}

output "droplet_private_ips" {
  description = "App Droplet private IP'lari (VPC ichida)"
  value       = digitalocean_droplet.app[*].ipv4_address_private
}

output "postgres_host" {
  description = "PostgreSQL public host (local ulanish uchun)"
  value       = digitalocean_database_cluster.postgres.host
}

output "postgres_private_host" {
  description = "PostgreSQL private host (Droplet dan ulanish uchun)"
  value       = digitalocean_database_cluster.postgres.private_host
  sensitive   = true
}

output "postgres_port" {
  description = "PostgreSQL port"
  value       = digitalocean_database_cluster.postgres.port
}

output "postgres_uri" {
  description = "To'liq PostgreSQL connection string (private)"
  value       = "postgresql+asyncpg://${var.db_user}:${var.db_password}@${digitalocean_database_cluster.postgres.private_host}:${digitalocean_database_cluster.postgres.port}/educrm_db?ssl=require"
  sensitive   = true
}

output "redis_host" {
  description = "Redis private host"
  value       = digitalocean_database_cluster.redis.private_host
  sensitive   = true
}

output "redis_uri" {
  description = "To'liq Redis URI"
  value       = "rediss://:${digitalocean_database_cluster.redis.password}@${digitalocean_database_cluster.redis.private_host}:${digitalocean_database_cluster.redis.port}"
  sensitive   = true
}

output "spaces_bucket_name" {
  description = "DO Spaces bucket nomi"
  value       = digitalocean_spaces_bucket.media.name
}

output "spaces_bucket_domain" {
  description = "Media fayllar CDN URL"
  value       = digitalocean_spaces_bucket.media.bucket_domain_name
}

output "registry_endpoint" {
  description = "DOCR endpoint — CI/CD uchun"
  value       = digitalocean_container_registry.main.server_url
}

output "registry_name" {
  description = "DOCR registry nomi"
  value       = digitalocean_container_registry.main.name
}

output "vpc_id" {
  description = "VPC UUID"
  value       = digitalocean_vpc.main.id
}

output "api_url" {
  description = "Production API URL"
  value       = "http://${digitalocean_loadbalancer.main.ip}/api/v1"
}

output "swagger_url" {
  description = "Swagger UI URL"
  value       = "http://${digitalocean_loadbalancer.main.ip}/docs"
}

output "ssh_commands" {
  description = "SSH ulanish buyruqlari"
  value       = [for ip in digitalocean_droplet.app[*].ipv4_address : "ssh root@${ip} -i ~/.ssh/educrm_deploy"]
}
