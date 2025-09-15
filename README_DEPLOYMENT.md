# 🚀 RAG News Chatbot - Deployment Guide

## Quick Deploy (5 Minutes!)

### Windows Users:
```bash
# 1. Download the project
git clone <your-repo-url>
cd rag

# 2. Run the deployment script
deploy.bat

# 3. Add your API keys to .env file
# 4. Press Enter to continue
# 5. Open http://localhost:3000
```

### Mac/Linux Users:
```bash
# 1. Download the project
git clone <your-repo-url>
cd rag

# 2. Make script executable and run
chmod +x deploy.sh
./deploy.sh

# 3. Add your API keys to .env file
# 4. Press Enter to continue
# 5. Open http://localhost:3000
```

## 🌐 What You Get

- **Frontend**: http://localhost:3000 (React chat interface)
- **Backend**: http://localhost:8000 (Python FastAPI)
- **Gateway**: http://localhost:5000 (Node.js proxy)
- **Qdrant**: http://localhost:6333 (Vector database)
- **Redis**: http://localhost:6379 (Session storage)

## 🔑 Required API Keys

1. **Gemini API Key** (Required):
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Add to `.env` file

2. **Qdrant API Key** (Optional for local):
   - Only needed for cloud Qdrant
   - Can leave empty for local deployment

## 📦 What's Included

- ✅ Complete RAG pipeline
- ✅ News ingestion system
- ✅ Vector search with Qdrant
- ✅ AI responses with Gemini
- ✅ Session management with Redis
- ✅ Modern React frontend
- ✅ Docker containerization
- ✅ One-click deployment

## 🎯 Features

- **Smart News Retrieval**: Finds relevant news articles
- **AI-Powered Responses**: Uses Gemini for intelligent answers
- **Session Management**: Save and load chat history
- **Real-time Chat**: Modern chat interface
- **Source Citations**: Shows where information comes from
- **Confidence Scoring**: Indicates answer reliability

## 🛠️ Customization

### Change News Sources:
Edit `backend/news_ingestion.py`:
```python
self.rss_feeds = [
    'https://feeds.bbci.co.uk/news/rss.xml',
    'https://rss.cnn.com/rss/edition.rss',
    # Add your own RSS feeds here
]
```

### Modify AI Behavior:
Edit `backend/rag_pipeline_simple.py`:
```python
# Change similarity threshold
min_similarity = 0.2  # Lower = more results

# Modify prompt
prompt = f"""Your custom prompt here..."""
```

### Update UI:
Edit files in `client/src/components/` to customize the interface.

## 🚀 Production Deployment

### Railway (Recommended):
1. Push to GitHub
2. Connect to Railway.app
3. Add environment variables
4. Deploy automatically

### Heroku:
1. Create Heroku app
2. Add Redis and Qdrant add-ons
3. Deploy with Docker

### DigitalOcean:
1. Create App Platform
2. Connect GitHub
3. Configure environment variables
4. Deploy

## 📊 Monitoring

### View Logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Status:
```bash
docker-compose ps
```

### Restart Services:
```bash
docker-compose restart
```

## 🔧 Troubleshooting

### Common Issues:

1. **Port conflicts**: Change ports in `docker-compose.production.yml`
2. **API key errors**: Check `.env` file
3. **Services not starting**: Check Docker logs
4. **No news articles**: Run `python news_ingestion.py`

### Reset Everything:
```bash
docker-compose down -v
docker-compose up --build
```

## 📞 Support

- Check logs for errors
- Verify API keys are correct
- Ensure all services are running
- Check network connectivity

## 🎉 Success!

Once deployed, your RAG news chatbot will be ready to:
- Answer questions about current events
- Provide AI-powered news summaries
- Manage chat sessions
- Cite sources for transparency

Enjoy your intelligent news assistant! 🚀
