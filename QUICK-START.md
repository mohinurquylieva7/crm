# 🚀 CRM Deployment Quick Reference

## Initial Setup (First Time Only)

```bash
# 1. Clone repository
git clone https://github.com/mohinurquylieva7/crm.git
cd crm

# 2. Setup directories
mkdir -p certbot/{conf,www}

# 3. Create environment file
cp .env.example .env
# Edit .env with your values
nano .env

# 4. Get SSL certificate
./setup-ssl.sh admin@crm-uz.duckdns.org
# OR on Windows:
setup-ssl.bat admin@crm-uz.duckdns.org

# 5. Start services
docker-compose up -d

# 6. Verify
docker-compose ps
curl -I https://crm-uz.duckdns.org
```

## Daily Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check service status
docker-compose ps

# View specific service logs
docker-compose logs crm
docker-compose logs nginx
docker-compose logs certbot
```

## Updates & Maintenance

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Clean up unused images
docker image prune -f

# Clean up unused volumes
docker volume prune -f

# Full cleanup (careful!)
docker-compose down -v
```

## SSL Certificate Management

```bash
# Check certificate status
docker-compose exec certbot certbot certificates

# Renew certificates (manual)
docker-compose run --rm certbot certbot renew

# Renew with dry-run (safe test)
docker-compose run --rm certbot certbot renew --dry-run

# Force renewal
docker-compose run --rm certbot certbot renew --force-renewal
```

## Troubleshooting

```bash
# Test nginx configuration
docker-compose exec nginx nginx -t

# Check DNS resolution
nslookup crm-uz.duckdns.org

# Test HTTPS connection
curl -Iv https://crm-uz.duckdns.org

# Check certificate details
openssl s_client -connect crm-uz.duckdns.org:443

# View nginx error log
docker-compose logs nginx --tail=100

# View certbot log
docker-compose logs certbot --tail=50

# View application log
docker-compose logs crm --tail=50
```

## Backup & Restore

```bash
# Backup data and certificates
tar -czf crm-backup-$(date +%Y%m%d).tar.gz \
    crm-data certbot/.

# Restore from backup
tar -xzf crm-backup-YYYYMMDD.tar.gz
```

## Security Commands

```bash
# Change SECRET_KEY in .env
nano .env
# Edit: SECRET_KEY=your-new-secret-key

# Restart with new key
docker-compose up -d

# Check running containers
docker ps

# Inspect container
docker inspect container-name

# View environment variables
docker-compose exec crm env | grep SECRET
```

## Emergency Recovery

```bash
# If services won't start
docker-compose logs --all

# Force stop everything
docker-compose kill

# Remove all containers/volumes/networks
docker-compose down -v

# Fresh start
docker-compose up -d

# Wait for services
sleep 10
docker-compose ps
```

## Performance Monitoring

```bash
# CPU & Memory usage
docker stats

# Disk usage
du -sh crm-data/ certbot/

# View top processes
docker-compose exec crm top

# Network usage
netstat -i
```

## Useful Links

- **CRM URL**: https://crm-uz.duckdns.org
- **API Docs**: https://crm-uz.duckdns.org/docs
- **ReDoc**: https://crm-uz.duckdns.org/redoc
- **DuckDNS**: https://www.duckdns.org
- **Let's Encrypt**: https://letsencrypt.org
- **Nginx Docs**: https://nginx.org/en/docs/

## Production Checklist

- [ ] SSL certificate installed and auto-renewing
- [ ] Environment variables configured (.env)
- [ ] Database backups scheduled
- [ ] Log rotation configured
- [ ] Firewall rules set (80, 443, SSH)
- [ ] SSH key authentication enabled
- [ ] Password authentication disabled
- [ ] Updates applied and tested
- [ ] Monitoring alerts configured
- [ ] Disaster recovery plan documented

---

**For detailed information, see: [DEPLOYMENT.md](./DEPLOYMENT.md)**
