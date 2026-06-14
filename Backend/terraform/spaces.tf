# ─── DO Spaces (S3-compatible object storage) ────────────────────────────────
resource "digitalocean_spaces_bucket" "media" {
  name   = "${var.project_name}-media"
  region = var.region
  acl    = "public-read"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_origins = ["*"]
    max_age_seconds = 3600
  }

  versioning {
    enabled = false
  }

  lifecycle_rule {
    id      = "expire-temp"
    enabled = true
    prefix  = "tmp/"

    expiration {
      days = 7
    }
  }
}

# ─── Spaces CDN (optional) ────────────────────────────────────────────────────
# resource "digitalocean_cdn" "media" {
#   origin         = digitalocean_spaces_bucket.media.bucket_domain_name
#   ttl            = 3600
#   custom_domain  = "cdn.yourdomain.com"
#   certificate_name = digitalocean_certificate.main.name
# }
