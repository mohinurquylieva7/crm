# 🔧 Nginx Domain Troubleshooting Guide

## Problem: Domain not working even though services are running

### ✅ Step-by-Step Verification

#### Step 1: DNS Configuration (DuckDNS)
```bash
# 1. Check current IP
curl -s http://checkip.amazonaws.com

# 2. Go to https://www.duckdns.org
#    - Login
#    - Find crm-uz.duckdns.org domain
#    - Update IP to match above
#    - Click "Update"

# 3. Wait 5-10 minutes for DNS propagation
nslookup crm-uz.duckdns.org
# Should show your server's IP address
```

#### Step 2: SSL Certificate Setup
```bash
# Check if certificate exists
ls -la certbot/conf/live/crm-uz.duckdns.org/

# If NOT present, generate certificate:
./setup-ssl.sh admin@crm-uz.duckdns.org
# OR on Windows:
setup-ssl.bat admin@crm-uz.duckdns.org

# Verify certificate validity
openssl x509 -in certbot/conf/live/crm-uz.duckdns.org/fullchain.pem -noout -text
```

#### Step 3: Nginx Configuration
```bash
# Test nginx configuration
docker-compose exec nginx nginx -t

# If configuration error, check logs
docker-compose logs nginx

# Common errors:
# - "bind() to 0.0.0.0:443 failed" = Port already in use
# - "cannot open certificate file" = SSL cert missing
# - "directive X is not permitted" = Syntax error
```

#### Step 4: Services Status
```bash
# Check all services running
docker-compose ps

# Expected status:
# crm       | Up | Healthy
# nginx     | Up
# certbot   | Up
```

#### Step 5: Connectivity Test
```bash
# From server itself:
curl -I http://crm-uz.duckdns.org     # Should redirect to HTTPS
curl -Iv https://crm-uz.duckdns.org   # Should return 200

# Backend connectivity
curl -I http://localhost:8000/docs    # Direct backend test
```

---

## 🔴 Common Issues & Solutions

### ❌ Issue 1: SSL Certificate Error
```
Error: No such file or directory: 
'/etc/letsencrypt/live/crm-uz.duckdns.org/fullchain.pem'
```

**Solution:**
```bash
# Generate certificate first
./setup-ssl.sh admin@crm-uz.duckdns.org

# Then restart nginx
docker-compose restart nginx

# Verify certificate
docker-compose exec certbot certbot certificates
```

### ❌ Issue 2: Port Already in Use
```
Error: bind() to 0.0.0.0:443 failed
```

**Solution:**
```bash
# Kill existing process on port 443
sudo lsof -i :443
sudo kill -9 <PID>

# Or restart docker
docker-compose restart nginx
```

### ❌ Issue 3: DNS Not Resolving
```
nslookup crm-uz.duckdns.org
# Returns: Can't find crm-uz.duckdns.org
```

**Solution:**
1. Go to https://www.duckdns.org
2. Verify domain is "crm-uz"
3. Update IP address
4. Click "Update"
5. Wait 5-10 minutes (or longer for propagation)
6. Try again: `nslookup crm-uz.duckdns.org`

### ❌ Issue 4: Backend Not Responding
```
curl https://crm-uz.duckdns.org
# Returns: Connection refused
```

**Solution:**
```bash
# Check backend container
docker-compose ps crm

# Check backend logs
docker-compose logs crm --tail=50

# Check if backend is healthy
docker-compose exec crm python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000')"

# If backend not responding, rebuild
docker-compose up -d --build crm
```

### ❌ Issue 5: Self-Signed Certificate Error
```
curl https://crm-uz.duckdns.org
# Error: SSL certificate problem: self signed certificate
```

**Solution:**
```bash
# This means Let's Encrypt cert wasn't installed
# Check certificate:
ls -la certbot/conf/live/crm-uz.duckdns.org/

# If missing, run:
./setup-ssl.sh admin@crm-uz.duckdns.org

# Restart nginx
docker-compose restart nginx
```

### ❌ Issue 6: Firewall Blocking Ports
```
timeout connecting to crm-uz.duckdns.org:443
```

**Solution:**
```bash
# Check firewall rules
sudo ufw status

# Allow ports 80 and 443
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload
```

### ❌ Issue 7: Nginx Stuck in Redirect Loop
```
curl -I http://crm-uz.duckdns.org
# Returns: 301 redirect loop detected
```

**Solution:**
```bash
# Check nginx config
docker-compose exec nginx nginx -t

# Fix server_name in nginx.conf:
# Should be: crm-uz.duckdns.org www.crm-uz.duckdns.org
# NOT: $server_name variable

# Restart nginx
docker-compose restart nginx
```

---

## 🚀 Quick Diagnostic Commands

```bash
# Run full diagnostics
./diagnose.sh
# OR on Windows:
diagnose.bat

# View all logs
docker-compose logs -f

# Check specific service
docker-compose logs crm --tail=50
docker-compose logs nginx --tail=50
docker-compose logs certbot --tail=50

# Test HTTPS connection with verbose output
curl -Iv https://crm-uz.duckdns.org

# Test with certificate details
openssl s_client -connect crm-uz.duckdns.org:443

# Test DNS resolution
nslookup crm-uz.duckdns.org
dig crm-uz.duckdns.org

# Check service health
docker-compose exec crm curl http://localhost:8000/docs
docker-compose exec nginx curl http://crm:8000/docs

# Inspect volumes
docker volume ls
docker volume inspect crm-data

# Restart all services
docker-compose down -v
docker-compose up -d
```

---

## 📋 Pre-Launch Checklist

Before going to production:

- [ ] DuckDNS domain pointing to correct IP
- [ ] DNS resolves correctly: `nslookup crm-uz.duckdns.org`
- [ ] SSL certificate installed: `ls certbot/conf/live/crm-uz.duckdns.org/`
- [ ] Nginx config valid: `docker-compose exec nginx nginx -t`
- [ ] All services running: `docker-compose ps`
- [ ] Backend responding: `curl http://localhost:8000/docs`
- [ ] HTTPS works locally: `curl -I https://localhost/`
- [ ] Domain accessible: `curl -I https://crm-uz.duckdns.org`
- [ ] Certificate valid: `openssl x509 -in certbot/conf/live/.../fullchain.pem -noout -dates`
- [ ] Firewall allows 80/443: `sudo ufw status`

---

## 🆘 Still Not Working?

1. **Collect logs:**
   ```bash
   docker-compose logs > crm-logs.txt
   ```

2. **Check resource usage:**
   ```bash
   docker stats
   ```

3. **Verify configuration files:**
   - `nginx.conf` - syntax correct?
   - `docker-compose.yaml` - volumes correct?
   - `.env` - secrets set?

4. **Try fresh start:**
   ```bash
   docker-compose down -v
   rm -rf certbot/conf
   ./setup-ssl.sh admin@crm-uz.duckdns.org
   docker-compose up -d
   ```

5. **Check server requirements:**
   - CPU: Minimum 1 core
   - RAM: Minimum 512MB
   - Disk: Minimum 5GB free
   - Internet: Stable connection

---

## 📞 Support Resources

- **Let's Encrypt Status:** https://letsencrypt.status.io
- **DuckDNS:** https://www.duckdns.org
- **Nginx Docs:** https://nginx.org/en/docs/
- **Docker Docs:** https://docs.docker.com
- **Certbot:** https://certbot.eff.org
