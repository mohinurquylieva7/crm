#!/bin/bash
# Run this ONCE on the server to authorize the GitHub Actions deploy key
# Usage: paste this in DigitalOcean web console or after first SSH access
set -e

DEPLOY_PUBKEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAII/0aqVzIbSm8CqYjO+1e10+/Zn9HFLJHDnAAzyK6npU educrm-deploy@github-actions"

mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add key if not already present
if ! grep -qF "$DEPLOY_PUBKEY" ~/.ssh/authorized_keys 2>/dev/null; then
    echo "$DEPLOY_PUBKEY" >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    echo "Deploy key added to authorized_keys"
else
    echo "Deploy key already present"
fi

# Create app directory structure
mkdir -p /opt/educrm/{media,logs}
mkdir -p /var/www/certbot

echo "Server ready for GitHub Actions deployment"
