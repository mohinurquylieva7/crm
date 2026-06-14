#!/bin/bash

echo "🔍 CRM Domain & Nginx Diagnostika"
echo "==================================="
echo ""

# 1. DNS Resolution
echo "1️⃣ DNS Resolution Tekshirish..."
if command -v nslookup &> /dev/null; then
    nslookup crm-uz.duckdns.org
    echo "✅ DNS query completed"
elif command -v dig &> /dev/null; then
    dig crm-uz.duckdns.org
    echo "✅ DNS query completed"
else
    echo "⚠️ DNS tools not available"
fi
echo ""

# 2. Docker services status
echo "2️⃣ Docker Services Status..."
docker-compose ps
echo ""

# 3. Nginx configuration test
echo "3️⃣ Nginx Configuration Test..."
docker-compose exec nginx nginx -t
echo ""

# 4. SSL Certificate status
echo "4️⃣ SSL Certificate Status..."
if [ -f "certbot/conf/live/crm-uz.duckdns.org/fullchain.pem" ]; then
    echo "✅ Certificate exists"
    openssl x509 -in certbot/conf/live/crm-uz.duckdns.org/fullchain.pem -noout -dates
    openssl x509 -in certbot/conf/live/crm-uz.duckdns.org/fullchain.pem -noout -subject
else
    echo "❌ Certificate NOT FOUND!"
    echo "Run: ./setup-ssl.sh admin@crm-uz.duckdns.org"
fi
echo ""

# 5. Backend connectivity
echo "5️⃣ Backend Connectivity (Docker network)..."
docker-compose exec nginx ping -c 2 crm || echo "⚠️ Backend ping failed"
echo ""

# 6. Port accessibility
echo "6️⃣ Port Accessibility..."
echo "Checking port 80 (HTTP)..."
curl -I http://localhost:80/ 2>&1 | head -5
echo ""
echo "Checking port 443 (HTTPS)..."
curl -Iv https://localhost:443/ 2>&1 | head -10 || echo "⚠️ SSL connection test failed"
echo ""

# 7. Nginx error log
echo "7️⃣ Nginx Error Log (last 20 lines)..."
docker-compose logs nginx --tail=20 | grep -i error || echo "No errors found"
echo ""

# 8. Nginx access log sample
echo "8️⃣ Nginx Access Log (last 5 lines)..."
docker-compose logs nginx --tail=5
echo ""

# 9. Test via domain name
echo "9️⃣ Test via Domain Name (crm-uz.duckdns.org)..."
echo "HTTP test:"
curl -I http://crm-uz.duckdns.org 2>&1 | head -5
echo ""
echo "HTTPS test:"
curl -Iv https://crm-uz.duckdns.org 2>&1 | head -10
echo ""

# 10. Backend health check
echo "🔟 Backend Health Check..."
docker-compose exec -T crm python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" && echo "✅ Backend is healthy" || echo "⚠️ Backend health check failed"
echo ""

echo "✨ Diagnostika completed!"
echo ""
echo "📋 Summary:"
echo "- If DNS shows correct IP: ✅ DuckDNS working"
echo "- If Certificate exists: ✅ SSL ready"
echo "- If all services running: ✅ Docker OK"
echo "- If nginx -t passes: ✅ Config valid"
echo ""
echo "❌ If domain still not working:"
echo "1. Wait 5-10 minutes for DNS propagation"
echo "2. Check firewall ports 80/443 are open"
echo "3. Check backend logs: docker-compose logs crm"
echo "4. Verify DuckDNS shows your correct IP"
