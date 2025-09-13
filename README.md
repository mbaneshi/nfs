# NSF - Multi-Platform AI Automation Template

A comprehensive full-stack template combining React, React Native CLI, FastAPI, self-hosted n8n, and Supabase for AI-powered automation workflows across web and mobile platforms.

## 🚀 Tech Stack

- **Web Frontend**: React 18+ with Vite
- **Mobile Frontend**: React Native CLI (iOS & Android)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL)
- **Automation**: Self-hosted n8n
- **AI Integration**: OpenAI API, Anthropic Claude
- **Deployment**: Docker & Docker Compose
- **State Management**: Redux Toolkit / Zustand
- **Styling**: Tailwind CSS (Web) / NativeWind (Mobile)

## 📋 Prerequisites

- Node.js 18+ 
- Python 3.11+
- Docker & Docker Compose
- Git
- **Mobile Development**:
  - Xcode (iOS development)
  - Android Studio (Android development)
  - React Native CLI: `npm install -g @react-native-community/cli`

## 🛠️ Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd nsf
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individually
make dev
```

### 4. Access Applications
- **Web Frontend**: http://localhost:3000
- **Mobile App**: Metro bundler on http://localhost:8081
- **Backend API**: http://localhost:8000
- **n8n Dashboard**: http://localhost:5678
- **Supabase Studio**: http://localhost:54323

## 📁 Project Structure

```
nsf/
├── web/                    # React web application
├── mobile/                 # React Native mobile application
├── backend/                # FastAPI with Clean Architecture
│   ├── app/
│   │   ├── domain/         # Business logic (Entities, Value Objects, Domain Services)
│   │   ├── application/    # Use cases (Commands, Queries, Handlers)
│   │   ├── infrastructure/ # External concerns (Repositories, Event Bus, AI Clients)
│   │   └── presentation/  # API layer (FastAPI routes, middleware)
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
├── shared/                # Shared utilities and types
├── n8n/                   # n8n workflows and configs
├── supabase/              # Database migrations and configs
├── docs/                  # Documentation and guides
├── scripts/               # Development and deployment scripts
├── .github/               # GitHub workflows and templates
├── docker-compose.yml     # Complete orchestration
├── env.template           # Parameterized configuration
├── .cursorrules           # Cursor AI behavior rules
└── README.md
```

## 🔧 Development

### Web Frontend (React + Vite)
```bash
cd web
npm install
npm run dev
```

### Mobile Frontend (React Native CLI)
```bash
cd mobile
npm install
# iOS
npx react-native run-ios
# Android
npx react-native run-android
```

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### n8n Workflows
- Access n8n dashboard at http://localhost:5678
- Create automation workflows
- Integrate with AI services

### Supabase
- Database migrations in `supabase/migrations/`
- Edge functions in `supabase/functions/`

## 🎯 Template Features

This repository serves as a **comprehensive template** for future projects with:

- **Multi-Platform Support**: Web (React) + Mobile (React Native CLI)
- **AI-Powered Automation**: n8n workflows with AI integration
- **Clean Architecture**: Domain-Driven Design (DDD) with CQRS pattern
- **Event-Driven Architecture**: Asynchronous communication between services
- **Modern Development Practices**: TDD, CI/CD, automated testing
- **Professional Workflow**: Git best practices, code review, documentation
- **Scalable Architecture**: Microservices-ready, SOLID principles, design patterns
- **Production Ready**: Docker deployment, monitoring, error handling

## 🚀 Template Usage

### For New Projects:
1. Use this repository as a template
2. Customize project name and configuration
3. Update environment variables
4. Start development with established patterns

### Customization Points:
- Project name and branding
- Database schema and migrations
- API endpoints and business logic
- UI/UX design and components
- n8n workflow templates

## 🚀 Deployment

### Production Setup
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
Key environment variables needed:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `N8N_BASIC_AUTH_ACTIVE`

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - FastAPI auto-generated docs
- [n8n Documentation](https://docs.n8n.io/) - Official n8n docs
- [Supabase Documentation](https://supabase.com/docs) - Official Supabase docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Create an issue in this repository
- Check the documentation links above
- Review Docker logs: `docker-compose logs [service-name]`
