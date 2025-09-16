#!/bin/bash
# verify-setup.sh - Verify environment setup

echo "🔍 Verifying NSF Multi-Platform AI Automation Setup"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Run: cp env.example .env"
    echo "🔑 Then run: ./generate-keys.sh"
    exit 1
fi

echo "✅ .env file exists"

# Check critical variables
echo ""
echo "🔑 Checking critical environment variables..."

# Function to check if variable is set and not placeholder
check_var() {
    local var_name=$1
    local var_value=$(grep "^$var_name=" .env | cut -d'=' -f2-)
    
    if [ -z "$var_value" ]; then
        echo "❌ $var_name is not set"
        return 1
    elif [[ "$var_value" == *"your_"* ]] || [[ "$var_value" == *"here"* ]]; then
        echo "❌ $var_name still has placeholder value"
        return 1
    else
        echo "✅ $var_name is set"
        return 0
    fi
}

# Check critical variables
critical_vars=(
    "JWT_SECRET_KEY"
    "SUPABASE_DB_PASSWORD"
    "SUPABASE_DB_ENC_KEY"
    "SUPABASE_SECRET_KEY_BASE"
    "N8N_ENCRYPTION_KEY"
    "N8N_BASIC_AUTH_PASSWORD"
)

all_good=true
for var in "${critical_vars[@]}"; do
    if ! check_var "$var"; then
        all_good=false
    fi
done

echo ""
if [ "$all_good" = true ]; then
    echo "🎉 All critical variables are properly configured!"
    echo "🚀 You can now run: make start"
else
    echo "⚠️  Some variables need to be configured"
    echo "🔑 Run: ./generate-keys.sh"
    echo "📝 Then update your .env file with the generated values"
fi

# Check MinIO credentials
echo ""
echo "🔒 Checking MinIO credentials..."
minio_access=$(grep "^MINIO_ACCESS_KEY=" .env | cut -d'=' -f2-)
minio_secret=$(grep "^MINIO_SECRET_KEY=" .env | cut -d'=' -f2-)

if [ "$minio_access" = "minioadmin" ] && [ "$minio_secret" = "minioadmin123" ]; then
    echo "⚠️  MinIO is using default credentials"
    echo "🔐 Consider changing MINIO_ACCESS_KEY and MINIO_SECRET_KEY"
else
    echo "✅ MinIO credentials are customized"
fi

echo ""
echo "📚 For more help, see: SETUP.md"
