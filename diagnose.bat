@echo off
REM CRM Domain & Nginx Diagnostika Script for Windows

echo.
echo 🔍 CRM Domain ^& Nginx Diagnostika
echo ===================================
echo.

REM 1. Docker services status
echo 1️⃣ Docker Services Status...
docker-compose ps
echo.

REM 2. Nginx configuration test
echo 2️⃣ Nginx Configuration Test...
docker-compose exec nginx nginx -t
echo.

REM 3. SSL Certificate status
echo 3️⃣ SSL Certificate Status...
if exist "certbot\conf\live\crm-uz.duckdns.org\fullchain.pem" (
    echo ✅ Certificate exists
    openssl x509 -in certbot\conf\live\crm-uz.duckdns.org\fullchain.pem -noout -dates
) else (
    echo ❌ Certificate NOT FOUND!
    echo Run: setup-ssl.bat admin@crm-uz.duckdns.org
)
echo.

REM 4. Port accessibility
echo 4️⃣ Port Accessibility...
echo Checking port 80 (HTTP)...
curl -I http://localhost:80/ 2>&1 | findstr /R "^HTTP"
echo.
echo Checking port 443 (HTTPS)...
curl -Iv https://localhost:443/ 2>&1 | findstr /R "^HTTP" || echo ⚠️ SSL connection test failed
echo.

REM 5. Nginx logs
echo 5️⃣ Nginx Logs (last 10 lines)...
docker-compose logs nginx --tail=10
echo.

REM 6. Test via domain name (HTTP)
echo 6️⃣ Test via Domain (HTTP)...
curl -I http://crm-uz.duckdns.org 2>&1 | findstr /R "^HTTP"
echo.

REM 7. Test via domain name (HTTPS)
echo 7️⃣ Test via Domain (HTTPS)...
curl -Iv https://crm-uz.duckdns.org 2>&1 | findstr /R "^HTTP" || echo ⚠️ HTTPS test failed
echo.

REM 8. Backend health
echo 8️⃣ Backend Health...
docker-compose exec -T crm python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000')" && echo ✅ Backend is responding || echo ⚠️ Backend not responding
echo.

echo ✨ Diagnostika completed!
echo.
echo 📋 Troubleshooting:
echo - If DNS fails: Wait for DuckDNS propagation (5-10 minutes)
echo - If Certificate missing: Run setup-ssl.bat admin@crm-uz.duckdns.org
echo - If HTTPS fails: Check firewall allows port 443
echo - If Backend fails: Check docker-compose logs crm
pause
