#!/bin/bash

# Railway startup script for RAG News Chatbot
echo "🚀 Starting RAG News Chatbot on Railway..."

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if backend is ready
echo "🔍 Checking backend health..."
until curl -f http://backend:8000/health 2>/dev/null; do
    echo "Waiting for backend to be ready..."
    sleep 5
done

# Ingest news articles
echo "📰 Ingesting news articles..."
curl -X POST http://backend:8000/ingest

# Setup embeddings
echo "🧠 Setting up embeddings..."
curl -X POST http://backend:8000/setup-embeddings

echo "✅ RAG News Chatbot is ready!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
