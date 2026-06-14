@echo off
REM CRM SSL Certificate Setup Script for Windows
REM Usage: setup-ssl.bat [email]

setlocal enabledelayedexpansion

set DOMAIN=crm-uz.duckdns.org
set EMAIL=%1
if "!EMAIL!"=="" (
    set EMAIL=admin@crm-uz.duckdns.org
)

set CERT_DIR=certbot\conf
set WEBROOT_DIR=certbot\www

echo.
echo 🔐 CRM SSL Certificate Setup
echo ================================
echo Domain: %DOMAIN%
echo Email: %EMAIL%
echo.

REM Create directories
if not exist "%CERT_DIR%" mkdir "%CERT_DIR%"
if not exist "%WEBROOT_DIR%" mkdir "%WEBROOT_DIR%"

echo 📁 Directories created
echo.

REM Check if certificate exists
if exist "%CERT_DIR%\live\%DOMAIN%\fullchain.pem" (
    echo ✅ Certificate already exists for %DOMAIN%
    echo Certificate path: %CERT_DIR%\live\%DOMAIN%\
    goto :eof
)

echo 🚀 Starting nginx for ACME challenge...
docker-compose up -d nginx

echo ⏳ Waiting for nginx to start...
timeout /t 5 /nobreak

echo.
echo 📜 Requesting SSL certificate from Let's Encrypt...

REM Generate certificate
docker-compose run --rm certbot certonly ^
    --webroot ^
    -w /var/www/certbot ^
    --email %EMAIL% ^
    --agree-tos ^
    --no-eff-email ^
    -d %DOMAIN% ^
    -d www.%DOMAIN%

if errorlevel 1 (
    echo ❌ Certificate generation failed!
    exit /b 1
)

echo.
echo ✅ SSL Certificate obtained successfully!
echo.
echo 📍 Certificate location: %CERT_DIR%\live\%DOMAIN%\
echo.
echo 🔄 Restarting services...
docker-compose down
docker-compose up -d

echo.
echo ✨ SSL setup completed!
echo Your CRM is now available at: https://%DOMAIN%
echo.
echo Note: Certificate will auto-renew before expiration.
