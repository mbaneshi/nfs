# 🚀 NSF Multi-Platform AI Automation - Setup Guide

## 📋 **Quick Start**

### **1. Clone and Setup**
```bash
git clone <your-repo-url>
cd nfs
```

### **2. Generate Environment Keys**
```bash
# Generate secure keys
./generate-keys.sh

# Copy example environment file
cp env.example .env
```

### **3. Edit Environment Configuration**
```bash
# Edit .env file with your generated keys
nano .env
```

### **4. Start Services**
```bash
make start
```

## 🔑 **Required Environment Variables**

### **CRITICAL - Must be set before starting:**

```bash
# JWT Secret (32+ characters)
JWT_SECRET_KEY=your-generated-jwt-secret

# Database Password
SUPABASE_DB_PASSWORD=your-generated-db-password

# Database Encryption Key
SUPABASE_DB_ENC_KEY=your-generated-enc-key

# Secret Key Base
SUPABASE_SECRET_KEY_BASE=your-generated-secret-base

# n8n Encryption Key
N8N_ENCRYPTION_KEY=your-generated-n8n-key

# n8n Admin Password
N8N_BASIC_AUTH_PASSWORD=your-generated-n8n-password
```

### **IMPORTANT - Should be changed from defaults:**

```bash
# MinIO Credentials (change from defaults!)
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key
```

### **OPTIONAL - For full functionality:**

```bash
# AI API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# SMTP for email verification
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## 🛠️ **Setup Steps**

### **Step 1: Generate Keys**
```bash
./generate-keys.sh
```

This will output something like:
```
JWT_SECRET_KEY=abc123...
SUPABASE_DB_PASSWORD=def456...
SUPABASE_DB_ENC_KEY=ghi789...
SUPABASE_SECRET_KEY_BASE=jkl012...
N8N_ENCRYPTION_KEY=mno345...
N8N_BASIC_AUTH_PASSWORD=pqr678...
```

### **Step 2: Create .env File**
```bash
cp env.example .env
```

### **Step 3: Edit .env File**
Replace the placeholder values with your generated keys:

```bash
# Replace these in .env:
JWT_SECRET_KEY=abc123...  # From generate-keys.sh
SUPABASE_DB_PASSWORD=def456...  # From generate-keys.sh
SUPABASE_DB_ENC_KEY=ghi789...  # From generate-keys.sh
SUPABASE_SECRET_KEY_BASE=jkl012...  # From generate-keys.sh
N8N_ENCRYPTION_KEY=mno345...  # From generate-keys.sh
N8N_BASIC_AUTH_PASSWORD=pqr678...  # From generate-keys.sh

# Change MinIO credentials:
MINIO_ACCESS_KEY=my-minio-user
MINIO_SECRET_KEY=my-minio-password

# Add AI keys if you have them:
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key
```

### **Step 4: Start Services**
```bash
make start
```

### **Step 5: Verify Setup**
```bash
# Check service health
make health

# View logs if needed
make logs-supabase
make logs-minio
make logs-kong
```

## 🌐 **Access Points**

Once started, access your services at:

- **Web App**: https://app.edcopo.info
- **API**: https://api.edcopo.info
- **n8n Automation**: https://automation.edcopo.info
- **Supabase Studio**: https://studio.edcopo.info
- **MinIO Console**: https://storage.edcopo.info
- **Health Check**: https://health.edcopo.info

## 🔧 **Troubleshooting**

### **Services won't start:**
```bash
# Check logs
make logs

# Check specific service
make logs-supabase
make logs-minio
```

### **Database connection issues:**
```bash
# Check if database is ready
docker-compose exec supabase-db pg_isready -U postgres
```

### **MinIO access issues:**
```bash
# Check MinIO health
docker-compose exec minio curl -f http://localhost:9000/minio/health/live
```

### **Kong gateway issues:**
```bash
# Check Kong status
docker-compose exec kong curl -s http://localhost:8001/status
```

## 📝 **Default Credentials**

### **Database:**
- **User**: postgres
- **Password**: (from SUPABASE_DB_PASSWORD)
- **Database**: postgres

### **MinIO:**
- **Access Key**: (from MINIO_ACCESS_KEY)
- **Secret Key**: (from MINIO_SECRET_KEY)
- **Console**: https://storage.edcopo.info

### **n8n:**
- **Username**: admin
- **Password**: (from N8N_BASIC_AUTH_PASSWORD)
- **URL**: https://automation.edcopo.info

### **Supabase Studio:**
- **URL**: https://studio.edcopo.info
- **No login required** (development mode)

## 🚨 **Security Notes**

1. **Never commit .env file** - it's in .gitignore
2. **Change default MinIO credentials** in production
3. **Use strong passwords** for all services
4. **Rotate keys regularly** in production
5. **Enable HTTPS** in production (already configured for local)

## 🔄 **Development Workflow**

```bash
# Start development
make start

# View logs
make logs-web
make logs-api

# Check health
make health

# Stop services
make stop

# Clean restart
make clean
make start
```

## 📚 **Next Steps**

After successful setup:

1. **Phase 2**: Backend implementation
2. **Phase 3**: Frontend development
3. **Phase 4**: Testing implementation
4. **Phase 5**: Automation workflows

## 🆘 **Need Help?**

- Check logs: `make logs-<service>`
- Check health: `make health`
- Restart services: `make restart`
- Clean restart: `make clean && make start`
