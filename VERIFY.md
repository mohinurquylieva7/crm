# ✅ Domain Setup Verification Checklist

## 🚀 Quick Start (After CD deployment)

### 1. SSH to Server
```bash
ssh user@your-server-ip
cd crm  # or wherever you cloned the repo
```

### 2. DuckDNS Configuration ⚠️ IMPORTANT
```bash
# Check your current public IP
curl -s http://checkip.amazonaws.com
# Output: xxx.xxx.xxx.xxx

# Go to: https://www.duckdns.org
# - Login with your account
# - Find: crm-uz
# - Update IP to match the output above
# - Click: Update
# - Wait 5-10 minutes for DNS propagation
```

### 3. Generate SSL Certificate
```bash
# Option A: Automated script
./setup-ssl.sh admin@crm-uz.duckdns.org

# Option B: Manual
mkdir -p certbot/{conf,www}
docker-compose up -d nginx
sleep 5
docker-compose run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    --email admin@crm-uz.duckdns.org \
    --agree-tos --no-eff-email \
    -d crm-uz.duckdns.org -d www.crm-uz.duckdns.org
```

### 4. Start All Services
```bash
docker-compose up -d

# Wait a few seconds
sleep 5

# Check status
docker-compose ps
```

### 5. Verify Each Component

#### A. Check DNS Resolution
```bash
nslookup crm-uz.duckdns.org
# Should show: Address: xxx.xxx.xxx.xxx (your IP)

# If not working, wait longer (DNS propagation can take 5-30 minutes)
```

#### B. Check Nginx Configuration
```bash
docker-compose exec nginx nginx -t
# Should output: successful
```

#### C. Check SSL Certificate
```bash
ls -la certbot/conf/live/crm-uz.duckdns.org/
# Should show: fullchain.pem, privkey.pem

# Check certificate validity
openssl x509 -in certbot/conf/live/crm-uz.duckdns.org/fullchain.pem -noout -dates
```

#### D. Check Service Status
```bash
docker-compose ps
# All should be "Up" or "Up (healthy)"
```

#### E. Test HTTP
```bash
curl -I http://crm-uz.duckdns.org
# Should output: HTTP/1.1 301
# And redirect to: https://crm-uz.duckdns.org
```

#### F. Test HTTPS
```bash
curl -I https://crm-uz.duckdns.org
# Should output: HTTP/1.1 200 OK
# And show certificate details
```

#### G. Test Backend
```bash
curl -I https://crm-uz.duckdns.org/docs
# Should output: HTTP/1.1 200 OK
# Shows Swagger UI documentation
```

---

## 🔍 Troubleshooting

### ❌ "nslookup: can't resolve crm-uz.duckdns.org"
**Solution:**
1. Check DuckDNS dashboard - is IP correct?
2. Wait 5-10 minutes for DNS to propagate
3. Try different DNS server: `nslookup crm-uz.duckdns.org 8.8.8.8`

### ❌ "Cannot find SSL certificate"
**Solution:**
```bash
# Regenerate certificate
./setup-ssl.sh admin@crm-uz.duckdns.org

# Restart nginx
docker-compose restart nginx
```

### ❌ "nginx: [emerg] bind() to 0.0.0.0:443 failed"
**Solution:**
```bash
# Kill process on port 443
sudo fuser -k 443/tcp

# Or restart docker
docker-compose restart nginx
```

### ❌ "curl: (60) SSL certificate problem"
**Solution:**
```bash
# Means certificate not properly installed
# Try:
docker-compose logs nginx | grep -i ssl
docker-compose logs certbot | tail -20

# Then regenerate:
./setup-ssl.sh admin@crm-uz.duckdns.org
docker-compose restart nginx
```

### ❌ "Connection refused" or timeout
**Solution:**
```bash
# Check backend
docker-compose logs crm

# Check nginx
docker-compose logs nginx

# Check ports
docker-compose ps

# Restart everything
docker-compose down
docker-compose up -d
```

---

## 📋 Working Verification

When everything is configured correctly, you should be able to:

✅ **DNS Resolution**
```bash
$ nslookup crm-uz.duckdns.org
Server: 8.8.8.8
Address: 8.8.8.8#53

Non-authoritative answer:
Name: crm-uz.duckdns.org
Address: 123.45.67.89
```

✅ **HTTP Redirect**
```bash
$ curl -I http://crm-uz.duckdns.org
HTTP/1.1 301 Moved Permanently
Location: https://crm-uz.duckdns.org/
```

✅ **HTTPS Access**
```bash
$ curl -I https://crm-uz.duckdns.org
HTTP/1.1 200 OK
Content-Type: application/json
```

✅ **SSL Certificate**
```bash
$ openssl s_client -connect crm-uz.duckdns.org:443
...
subject=CN = crm-uz.duckdns.org
issuer=C = US, O = Let's Encrypt, CN = R3
...
```

✅ **Services Running**
```bash
$ docker-compose ps
NAME     IMAGE              STATUS
crm      crm:latest         Up (healthy)
nginx    nginx:1.27-alpine  Up
certbot  certbot/certbot     Up
```

---

## 🎯 Quick Commands

```bash
# View all logs
docker-compose logs

# View specific logs
docker-compose logs crm --tail=50
docker-compose logs nginx --tail=50
docker-compose logs certbot --tail=20

# Run diagnostics
./diagnose.sh

# Restart services
docker-compose restart

# Stop everything
docker-compose stop

# Start everything
docker-compose up -d

# Full reset (careful!)
docker-compose down -v
rm -rf certbot/conf
./setup-ssl.sh admin@crm-uz.duckdns.org
docker-compose up -d
```

---

## 📞 If Still Not Working

1. **Run diagnostics:**
   ```bash
   ./diagnose.sh > diagnostics.log
   cat diagnostics.log
   ```

2. **Check firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **Check Docker:**
   ```bash
   docker ps -a
   docker images
   docker volume ls
   ```

4. **Collect error logs:**
   ```bash
   docker-compose logs > error.log
   # Share error.log for support
   ```

---

**✨ Once verified, your CRM is ready to use at: https://crm-uz.duckdns.org**

For detailed troubleshooting, see: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
