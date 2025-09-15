#!/bin/bash

# RAG News Chatbot Deployment Script
echo "🚀 Deploying RAG News Chatbot..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# API Keys (Required)
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Optional: Customize settings
PORT=5000
HOST=0.0.0.0
EOF
    echo "⚠️  Please edit .env file and add your API keys!"
    echo "   - Get Gemini API key: https://makersuite.google.com/app/apikey"
    echo "   - Qdrant API key is optional for local deployment"
    read -p "Press Enter after adding your API keys..."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.production.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.production.yml ps

# Run news ingestion
echo "📰 Ingesting news articles..."
docker-compose -f docker-compose.production.yml exec backend python news_ingestion.py

# Setup embeddings
echo "🧠 Setting up embeddings..."
docker-compose -f docker-compose.production.yml exec backend python rag_pipeline_simple.py

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your app is now available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Gateway: http://localhost:5000"
echo ""
echo "📊 To view logs:"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "🛑 To stop the app:"
echo "   docker-compose -f docker-compose.production.yml down"
