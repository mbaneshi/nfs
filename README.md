# NSF - AI Automation Stack

A modern full-stack application combining Next.js, FastAPI, self-hosted n8n, and Supabase for AI-powered automation workflows.

## 🚀 Tech Stack

- **Frontend**: Next.js 14+ (App Router)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL)
- **Automation**: Self-hosted n8n
- **AI Integration**: OpenAI API, Anthropic Claude
- **Deployment**: Docker & Docker Compose

## 📋 Prerequisites

- Node.js 18+ 
- Python 3.11+
- Docker & Docker Compose
- Git

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
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **n8n Dashboard**: http://localhost:5678
- **Supabase Studio**: http://localhost:54323

## 📁 Project Structure

```
nsf/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── n8n/              # n8n workflows and configs
├── supabase/         # Database migrations and configs
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Development

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
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

## 🤖 AI Features

- **Workflow Automation**: n8n-powered automation
- **AI Integration**: OpenAI & Claude API integration
- **Smart Triggers**: Event-driven automation
- **Data Processing**: Real-time data pipelines

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
