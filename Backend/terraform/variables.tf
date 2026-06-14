variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Loyiha nomi (barcha resurs nomlarida ishlatiladi)"
  type        = string
  default     = "educrm"
}

variable "region" {
  description = "DO region"
  type        = string
  default     = "fra1"
  # Variantlar: fra1 (Frankfurt), ams3 (Amsterdam), lon1 (London)
}

variable "droplet_size" {
  description = "Droplet o'lchami"
  type        = string
  default     = "s-2vcpu-2gb"
  # s-1vcpu-1gb ($6/oy) — dev/test
  # s-2vcpu-2gb ($18/oy) — minimal prod
  # s-2vcpu-4gb ($24/oy) — kichik prod
}

variable "droplet_count" {
  description = "Nechta app Droplet (LB uchun 2+ tavsiya)"
  type        = number
  default     = 1
}

variable "ssh_key_name" {
  description = "DO da mavjud SSH key nomi"
  type        = string
}

variable "admin_ip" {
  description = "SSH ruxsat berilgan admin IP (masalan: 1.2.3.4/32)"
  type        = string
}

variable "db_user" {
  description = "PostgreSQL foydalanuvchi nomi"
  type        = string
  default     = "educrm_user"
}

variable "db_password" {
  description = "PostgreSQL paroli"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT imzolash uchun maxfiy kalit (min 32 belgi)"
  type        = string
  sensitive   = true
}

variable "allowed_origins" {
  description = "CORS uchun ruxsat etilgan originlar"
  type        = string
  default     = "http://localhost:5173"
}

variable "docker_image" {
  description = "DOCR dagi image URL (deploy paytida to'ldiriladi)"
  type        = string
  default     = ""
}

variable "spaces_access_key" {
  description = "DO Spaces access key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "spaces_secret_key" {
  description = "DO Spaces secret key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "alert_email" {
  description = "Monitoring alert email"
  type        = string
  default     = ""
}
