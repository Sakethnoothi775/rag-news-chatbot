#!/bin/bash

echo "🚀 Setting up RAG News Chatbot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Redis is not running. Please start Redis server first."
    echo "   On macOS: brew services start redis"
    echo "   On Ubuntu: sudo systemctl start redis"
    echo "   On Windows: Start Redis from services or run redis-server"
fi

# Check if Qdrant is running
if ! curl -s http://localhost:6333/collections &> /dev/null; then
    echo "⚠️  Qdrant is not running. Starting with Docker..."
    docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest
fi

echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
cd ../client
npm install

cd ..
npm install

echo "🔧 Setting up environment..."
if [ ! -f backend/.env ]; then
    cp env.example backend/.env
    echo "📝 Please edit backend/.env with your API keys"
fi

if [ ! -f client/.env ]; then
    echo "REACT_APP_API_URL=http://localhost:5000/api" > client/.env
fi

echo "📰 Ingesting news articles..."
cd backend
python news_ingestion.py

echo "🔍 Setting up vector embeddings..."
python rag_pipeline.py

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   Terminal 1: cd backend && python main.py"
echo "   Terminal 2: npm run server"
echo "   Terminal 3: cd client && npm start"
echo ""
echo "🌐 Access the app at: http://localhost:3000"
echo "📚 API docs at: http://localhost:8000/docs"

