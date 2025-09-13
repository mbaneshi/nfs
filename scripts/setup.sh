#!/bin/bash

# NSF Multi-Platform AI Automation Template - Complete Setup Script
# This script sets up the entire development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists node; then
        missing_deps+=("node")
    fi
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and run this script again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.template .env
        print_warning "Please edit .env file with your configuration before running again"
        print_warning "Key variables to set:"
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
    
    print_success "Environment file is ready"
}

# Function to setup web application
setup_web() {
    print_status "Setting up web application..."
    
    cd web
    
    if [ ! -d node_modules ]; then
        print_status "Installing web dependencies..."
        npm install
    fi
    
    cd ..
    print_success "Web application setup complete"
}

# Function to setup mobile application
setup_mobile() {
    print_status "Setting up mobile application..."
    
    cd mobile
    
    if [ ! -d node_modules ]; then
        print_status "Installing mobile dependencies..."
        npm install
    fi
    
    cd ..
    print_success "Mobile application setup complete"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    if [ ! -d venv ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    cd ..
    print_success "Backend setup complete"
}

# Function to start services
start_services() {
    print_status "Starting all services..."
    
    # Load environment variables
    export $(cat .env | grep -v '^#' | xargs)
    
    # Start Docker services
    docker-compose up --build -d
    
    print_success "All services started successfully!"
}

# Function to wait for services
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend API is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Backend API failed to start within expected time"
            exit 1
        fi
        
        print_status "Waiting for backend API... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Function to display access information
show_access_info() {
    print_success "🎉 NSF Multi-Platform AI Automation Template is ready!"
    echo ""
    echo "🌐 Access your applications:"
    echo "   Web App:      https://app.edcopo.info"
    echo "   Mobile App:   Metro bundler on http://localhost:8081"
    echo "   API:          https://api.edcopo.info"
    echo "   API Docs:     https://api.edcopo.info/docs"
    echo "   n8n:          https://automation.edcopo.info"
    echo "   Supabase:     https://db.edcopo.info"
    echo "   Health Check: https://health.edcopo.info"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs:    docker-compose logs -f [service_name]"
    echo "   Stop all:     docker-compose down"
    echo "   Restart:      docker-compose restart [service_name]"
    echo "   Mobile dev:   cd mobile && npm run android/ios"
    echo "   Web dev:      cd web && npm run dev"
    echo ""
    echo "🔧 Development:"
    echo "   Backend:      cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "   Web:          cd web && npm run dev"
    echo "   Mobile:       cd mobile && npm run android/ios"
    echo ""
    echo "📚 Documentation:"
    echo "   README:       ./README.md"
    echo "   API Docs:     https://api.edcopo.info/docs"
    echo "   n8n Docs:     https://docs.n8n.io"
    echo "   Supabase:     https://supabase.com/docs"
}

# Main execution
main() {
    echo "🚀 NSF Multi-Platform AI Automation Template Setup"
    echo "=================================================="
    echo ""
    
    check_prerequisites
    setup_environment
    setup_web
    setup_mobile
    setup_backend
    start_services
    wait_for_services
    show_access_info
}

# Run main function
main "$@"
