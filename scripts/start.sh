#!/bin/bash

# NSF Multi-Platform AI Automation Template - Startup Script
# This script sets up and starts the complete development stack

set -e

echo "🚀 Starting NSF Multi-Platform AI Automation Template..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env file with your configuration before running again"
    echo "   Key variables to set:"
    echo "   - SUPABASE_ANON_KEY"
    echo "   - SUPABASE_SERVICE_ROLE_KEY"
    echo "   - SUPABASE_DB_PASSWORD"
    echo "   - N8N_BASIC_AUTH_PASSWORD"
    echo "   - N8N_ENCRYPTION_KEY"
    echo "   - JWT_SECRET_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - CADDY_EMAIL"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "🔧 Building and starting services..."

# Start all services with Docker Compose
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."

# Wait for services to be healthy
sleep 10

echo "✅ Services started successfully!"
echo ""
echo "🌐 Access your applications:"
echo "   Web App:      https://${WEB_SUBDOMAIN:-app}.${DOMAIN:-edcopo.info}"
echo "   API:          https://${API_SUBDOMAIN:-api}.${DOMAIN:-edcopo.info}"
echo "   n8n:          https://${N8N_SUBDOMAIN:-automation}.${DOMAIN:-edcopo.info}"
echo "   Supabase:     https://${SUPABASE_SUBDOMAIN:-db}.${DOMAIN:-edcopo.info}"
echo "   Health Check: https://health.${DOMAIN:-edcopo.info}"
echo ""
echo "📊 View logs: docker-compose logs -f [service_name]"
echo "🛑 Stop all:  docker-compose down"
echo ""
echo "🎉 Happy coding!"
