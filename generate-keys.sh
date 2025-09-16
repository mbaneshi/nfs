#!/bin/bash
# generate-keys.sh - Generate secure keys for environment configuration

echo "🔑 Generating environment keys..."
echo ""
echo "Copy these values to your .env file:"
echo "=================================="

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)
echo "JWT_SECRET_KEY=$JWT_SECRET"

# Generate database password
DB_PASSWORD=$(openssl rand -base64 32)
echo "SUPABASE_DB_PASSWORD=$DB_PASSWORD"

# Generate encryption key
ENC_KEY=$(openssl rand -hex 32)
echo "SUPABASE_DB_ENC_KEY=$ENC_KEY"

# Generate secret key base
SECRET_BASE=$(openssl rand -hex 64)
echo "SUPABASE_SECRET_KEY_BASE=$SECRET_BASE"

# Generate n8n encryption key
N8N_KEY=$(openssl rand -base64 32)
echo "N8N_ENCRYPTION_KEY=$N8N_KEY"

# Generate n8n admin password
N8N_PASS=$(openssl rand -base64 16)
echo "N8N_BASIC_AUTH_PASSWORD=$N8N_PASS"

echo ""
echo "✅ Keys generated! Copy these to your .env file"
echo "📝 Don't forget to change MinIO credentials from defaults!"
