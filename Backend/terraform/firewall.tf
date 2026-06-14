# ─── App Droplet Firewall ─────────────────────────────────────────────────────
resource "digitalocean_firewall" "app" {
  name        = "${var.project_name}-app-fw"
  droplet_ids = digitalocean_droplet.app[*].id

  # ── Kiruvchi: HTTP/HTTPS ──────────────────────────────────────────────────
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # ── Kiruvchi: SSH — faqat admin IP dan ───────────────────────────────────
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = [var.admin_ip]
  }

  # ── Kiruvchi: App port — faqat Load Balancer dan ─────────────────────────
  inbound_rule {
    protocol                  = "tcp"
    port_range                = "8000"
    source_load_balancer_uids = [digitalocean_loadbalancer.main.id]
  }

  # ── Kiruvchi: VPC ichida o'zaro muloqot ──────────────────────────────────
  inbound_rule {
    protocol         = "tcp"
    port_range       = "all"
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

  # ── Chiquvchi: hamma joyga ────────────────────────────────────────────────
  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
