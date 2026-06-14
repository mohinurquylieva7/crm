#!/bin/bash

# CRM SSL Certificate Setup Script
# Usage: ./setup-ssl.sh

set -e

DOMAIN="crm-uz.duckdns.org"
EMAIL="${1:-admin@crm-uz.duckdns.org}"
CERT_DIR="./certbot/conf"
WEBROOT_DIR="./certbot/www"

echo "🔐 CRM SSL Certificate Setup"
echo "================================"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Create necessary directories
mkdir -p "$CERT_DIR"
mkdir -p "$WEBROOT_DIR"

echo "📁 Directories created"

# Step 1: Check if certificate already exists
if [ -f "$CERT_DIR/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ Certificate already exists for $DOMAIN"
    echo "Certificate path: $CERT_DIR/live/$DOMAIN/"
    exit 0
fi

echo ""
echo "🚀 Starting nginx for ACME challenge..."

# Step 2: Start nginx to handle ACME challenges
docker-compose up -d nginx

echo "⏳ Waiting for nginx to start..."
sleep 5

echo ""
echo "📜 Requesting SSL certificate from Let's Encrypt..."

# Step 3: Generate certificate using Certbot
docker-compose run --rm certbot certonly \
    --webroot \
    -w /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo ""
echo "✅ SSL Certificate obtained successfully!"
echo ""
echo "📍 Certificate location: $CERT_DIR/live/$DOMAIN/"
echo ""
echo "🔄 Restarting services..."
docker-compose down
docker-compose up -d

echo ""
echo "✨ SSL setup completed!"
echo "Your CRM is now available at: https://$DOMAIN"
echo ""
echo "Note: Certificate will auto-renew before expiration."
