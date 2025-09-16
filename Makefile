# NSF Multi-Platform AI Automation Template - Makefile

.PHONY: help start stop restart logs clean build test setup health

# Default target
help:
	@echo "NSF Multi-Platform AI Automation Template"
	@echo ""
	@echo "Available commands:"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs for all services"
	@echo "  make logs-web  - View web app logs"
	@echo "  make logs-api  - View API logs"
	@echo "  make logs-n8n  - View n8n logs"
	@echo "  make logs-supabase - View Supabase logs"
	@echo "  make logs-minio - View MinIO logs"
	@echo "  make logs-kong - View Kong logs"
	@echo "  make build     - Build all services"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make test      - Run tests"
	@echo "  make setup     - Initial setup"
	@echo "  make health    - Check service health"

# Start all services
start:
	@echo "🚀 Starting NSF Multi-Platform AI Automation Template..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp env.template .env; \
		echo "⚠️  Please edit .env file with your configuration before running again"; \
		exit 1; \
	fi
	@docker-compose up --build -d
	@echo "✅ Services started successfully!"
	@echo ""
	@echo "🌐 Access your applications:"
	@echo "   Web App:      https://app.edcopo.info"
	@echo "   API:          https://api.edcopo.info"
	@echo "   n8n:          https://automation.edcopo.info"
	@echo "   Supabase:     https://db.edcopo.info"
	@echo "   Storage:      https://storage.edcopo.info"
	@echo "   Studio:       https://studio.edcopo.info"
	@echo "   Health:       https://health.edcopo.info"

# Stop all services
stop:
	@echo "🛑 Stopping all services..."
	@docker-compose down

# Restart all services
restart: stop start

# View logs
logs:
	@docker-compose logs -f

logs-web:
	@docker-compose logs -f web

logs-api:
	@docker-compose logs -f backend

logs-n8n:
	@docker-compose logs -f n8n

logs-supabase:
	@docker-compose logs -f supabase-db supabase-auth supabase-rest supabase-realtime supabase-storage supabase-studio

logs-minio:
	@docker-compose logs -f minio

logs-kong:
	@docker-compose logs -f kong

# Build all services
build:
	@echo "🔨 Building all services..."
	@docker-compose build

# Clean up
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f

# Run tests
test:
	@echo "🧪 Running tests..."
	@docker-compose exec backend pytest
	@docker-compose exec web npm test

# Check service health
health:
	@echo "🏥 Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "🔍 Service status:"
	@docker-compose exec caddy curl -s http://localhost/health || echo "❌ Caddy not responding"
	@docker-compose exec kong curl -s http://localhost:8001/status || echo "❌ Kong not responding"
	@docker-compose exec minio curl -s http://localhost:9000/minio/health/live || echo "❌ MinIO not responding"
	@docker-compose exec supabase-db pg_isready -U postgres || echo "❌ Supabase DB not responding"

# Initial setup
setup:
	@echo "⚙️  Setting up NSF Multi-Platform AI Automation Template..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp env.template .env; \
	fi
	@echo "✅ Setup complete!"
	@echo "📝 Please edit .env file with your configuration"
	@echo "🚀 Then run 'make start' to begin"
