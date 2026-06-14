# 🚀 CRM Deployment Guide

## Domain & SSL Setup for crm-uz.duckdns.org

### Prerequisites
- Docker & Docker Compose installed
- SSH access to your server
- Domain properly configured (DuckDNS DNS pointing to your server IP)

### Step 1: Prepare Your Server

```bash
# SSH into your server
ssh user@your-server-ip

# Clone the repository
git clone https://github.com/mohinurquylieva7/crm.git
cd crm

# Create necessary directories
mkdir -p certbot/{conf,www}
chmod -R 755 certbot
```

### Step 2: Configure Environment Variables

Create `.env` file:

```bash
cat > .env << 'EOF'
SECRET_KEY=your-super-secret-key-here-minimum-32-chars
DOMAIN=crm-uz.duckdns.org
ADMIN_EMAIL=admin@crm-uz.duckdns.org
EOF

chmod 600 .env
```

### Step 3: Get SSL Certificate from Let's Encrypt

**Option A: Using automated script (Recommended)**

```bash
# Linux/Mac
chmod +x setup-ssl.sh
./setup-ssl.sh admin@crm-uz.duckdns.org

# Windows
setup-ssl.bat admin@crm-uz.duckdns.org
```

**Option B: Manual setup**

```bash
# Start only nginx
docker-compose up -d nginx

# Wait for nginx to be ready
sleep 5

# Request certificate
docker-compose run --rm certbot certonly \
    --webroot \
    -w /var/www/certbot \
    --email admin@crm-uz.duckdns.org \
    --agree-tos \
    --no-eff-email \
    -d crm-uz.duckdns.org \
    -d www.crm-uz.duckdns.org
```

### Step 4: Start All Services

```bash
# Start the full stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Verify SSL Setup

```bash
# Check certificate validity
docker-compose exec certbot certbot certificates

# Test HTTPS
curl -I https://crm-uz.duckdns.org

# Test with verbose output
curl -Iv https://crm-uz.duckdns.org
```

## Troubleshooting

### Certificate is not being renewed
```bash
# Check certbot logs
docker-compose logs certbot

# Manually renew (test mode)
docker-compose run --rm certbot certbot renew --dry-run

# Manually renew (production)
docker-compose run --rm certbot certbot renew
```

### Nginx not starting
```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# View nginx logs
docker-compose logs nginx
```

### Domain not resolving
```bash
# Check DuckDNS configuration
nslookup crm-uz.duckdns.org

# Wait for DNS propagation (can take 5-30 minutes)
# Check your DuckDNS dashboard: https://www.duckdns.org
```

### Rate limiting (429 Too Many Requests)
If you get too many requests from Let's Encrypt:
- Wait 1 hour before retrying
- Use `--dry-run` flag to test certificate generation

## File Structure After Setup

```
crm/
├── docker-compose.yaml          # Main docker configuration
├── nginx.conf                   # Nginx reverse proxy config
├── setup-ssl.sh                 # SSL setup script (Linux/Mac)
├── setup-ssl.bat                # SSL setup script (Windows)
├── Dockerfile
├── app/                         # Your application
├── certbot/
│   ├── conf/                    # SSL certificates (auto-generated)
│   │   └── live/
│   │       └── crm-uz.duckdns.org/
│   │           ├── fullchain.pem
│   │           └── privkey.pem
│   └── www/                     # ACME challenge directory
└── .env                         # Environment variables
```

## Services Running

1. **CRM Backend** - FastAPI application on port 8000 (internal only)
2. **Nginx** - Reverse proxy on ports 80 & 443
3. **Certbot** - SSL certificate auto-renewal

## SSL Certificate Auto-Renewal

- Certbot automatically checks for renewal daily
- Renewal happens when certificates are 30 days before expiration
- Renewed certificates are automatically picked up by nginx
- No manual intervention needed

## Monitoring

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs crm
docker-compose logs nginx
docker-compose logs certbot

# Real-time logs
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50
```

## Maintenance

### Update application
```bash
git pull origin main
docker-compose up -d --build
```

### Restart services
```bash
docker-compose restart
```

### Stop services
```bash
docker-compose stop
```

### Remove everything and start fresh
```bash
docker-compose down -v
docker-compose up -d
```

## Security Tips

1. **Keep secrets safe** - Never commit `.env` to git
2. **Use strong SECRET_KEY** - Minimum 32 characters
3. **Enable SSH key authentication** - Disable password auth
4. **Configure firewall** - Only allow ports 80, 443, and SSH
5. **Monitor logs** - Check for suspicious activity regularly
6. **Update containers** - Pull latest images regularly

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Verify DNS: `nslookup crm-uz.duckdns.org`
- Test SSL: `openssl s_client -connect crm-uz.duckdns.org:443`
- Contact: admin@crm-uz.duckdns.org

---

**Your CRM is now running securely at:** https://crm-uz.duckdns.org
