# NSF Multi-Platform AI Automation Template - Makefile

.PHONY: help start stop restart logs clean build test

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
	@echo "  make build     - Build all services"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make test      - Run tests"
	@echo "  make setup     - Initial setup"

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
