#!/bin/bash

# Railway Deployment Script for RAG News Chatbot
echo "🚀 Deploying RAG News Chatbot to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed."
    echo "📥 Installing Railway CLI..."
    
    # Install Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install railway
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        echo "Please install Railway CLI manually: https://docs.railway.app/develop/cli"
        exit 1
    fi
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project
echo "📦 Creating Railway project..."
railway new

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set GEMINI_API_KEY="your_gemini_api_key_here"
railway variables set QDRANT_API_KEY=""
railway variables set REDIS_URL="redis://redis:6379"
railway variables set QDRANT_URL="http://qdrant:6333"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at the Railway URL"
echo "📊 Monitor at: https://railway.app/dashboard"
