# RAG-Powered News Chatbot

A sophisticated full-stack chatbot that answers queries over a news corpus using Retrieval-Augmented Generation (RAG) pipeline. Built with Python FastAPI backend, Node.js API gateway, and React frontend.

## 🚀 Features

- **RAG Pipeline**: Ingest ~50 news articles from RSS feeds and scrape content
- **Vector Search**: Use Jina embeddings with Qdrant vector database
- **AI Generation**: Google Gemini API for intelligent responses
- **Session Management**: Redis-based chat history with TTL
- **Real-time Chat**: WebSocket support for streaming responses
- **Modern UI**: Beautiful React interface with SCSS styling
- **Source Attribution**: Show sources and confidence scores
- **Responsive Design**: Mobile-first responsive design

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Node.js Gateway │    │  Python Backend │
│                 │    │                 │    │                 │
│  - Chat Interface│◄──►│  - API Proxy    │◄──►│  - FastAPI      │
│  - Message List │    │  - CORS         │    │  - RAG Pipeline │
│  - Sources Panel│    │  - Static Files │    │  - Session Mgmt │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │     Qdrant      │
                       │                 │    │                 │
                       │  - Chat History │    │  - Vector Store │
                       │  - Session Data │    │  - Embeddings   │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Backend (Python)
- **FastAPI**: Modern, fast web framework
- **Jina AI**: Embeddings generation
- **Qdrant**: Vector database for similarity search
- **Google Gemini**: Large language model
- **Redis**: Session management and caching
- **BeautifulSoup**: Web scraping
- **Feedparser**: RSS feed parsing

### Frontend (React + TypeScript)
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **SCSS**: Advanced styling with mixins
- **Axios**: HTTP client
- **Socket.io**: Real-time communication

### Infrastructure
- **Node.js**: API gateway and static file serving
- **Docker**: Containerization (optional)
- **Nginx**: Reverse proxy (production)

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis server
- Qdrant server
- Google Gemini API key
- Jina AI API key

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-news-chatbot
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start Qdrant (using Docker)
docker run -p 6333:6333 qdrant/qdrant

# Start Redis
redis-server

# Run news ingestion
python news_ingestion.py

# Start the FastAPI server
python main.py
```

### 3. Frontend Setup

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm start
```

### 4. API Gateway Setup

```bash
# Navigate to root directory
cd ..

# Install Node.js dependencies
npm install

# Start the API gateway
npm run server
```

### 5. Access the Application

- Frontend: http://localhost:3000
- API Gateway: http://localhost:5000
- Python Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Jina AI Embeddings
JINA_API_KEY=your_jina_api_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Session Configuration
SESSION_TTL=3600
CACHE_TTL=1800

# News Sources
NEWS_RSS_FEEDS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss,https://feeds.reuters.com/reuters/topNews
```

### Frontend Configuration

Create a `.env` file in the client directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WEBSOCKET_URL=ws://localhost:5000
```

## 📊 Usage

### 1. News Ingestion

The system automatically ingests news from configured RSS feeds:

```bash
cd backend
python news_ingestion.py
```

This will:
- Fetch articles from RSS feeds
- Scrape full article content
- Clean and process text
- Save to `data/articles.json`

### 2. Vector Indexing

After ingestion, create embeddings and index in Qdrant:

```bash
cd backend
python rag_pipeline.py
```

This will:
- Generate embeddings using Jina AI
- Chunk articles for better retrieval
- Store in Qdrant vector database

### 3. Chat Interface

Start all services and access the chat interface:

```bash
# Terminal 1: Python Backend
cd backend && python main.py

# Terminal 2: Node.js Gateway
npm run server

# Terminal 3: React Frontend
cd client && npm start
```

## 🔍 API Endpoints

### Chat Endpoints

- `POST /api/chat` - Send a message
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}/history` - Get session history
- `DELETE /api/sessions/{id}` - Clear session

### WebSocket

- `ws://localhost:5000/ws/{session_id}` - Real-time chat

### Health Check

- `GET /api/health` - System health status

## 🎨 Customization

### Adding News Sources

Edit the `NEWS_RSS_FEEDS` environment variable or modify `backend/news_ingestion.py`:

```python
self.rss_feeds = [
    'https://your-news-source.com/rss.xml',
    # Add more feeds
]
```

### Styling

The frontend uses SCSS with a comprehensive design system. Key files:

- `client/src/App.scss` - Global styles and variables
- `client/src/components/*.scss` - Component-specific styles

### RAG Configuration

Modify `backend/config.py` to adjust:

- Chunk size and overlap
- Number of retrieved results
- Embedding model
- Similarity threshold

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Setup

1. **Backend**: Deploy Python FastAPI with Gunicorn
2. **Frontend**: Build React app and serve with Nginx
3. **Database**: Use managed Redis and Qdrant services
4. **Load Balancer**: Configure Nginx for multiple instances

### Environment Variables for Production

```env
NODE_ENV=production
REDIS_URL=redis://your-redis-host:6379
QDRANT_URL=https://your-qdrant-host:6333
GEMINI_API_KEY=your-production-key
JINA_API_KEY=your-production-key
```

## 📈 Performance Optimization

### Caching Strategy

- **Redis TTL**: Session data expires after 1 hour
- **Vector Cache**: Frequently accessed embeddings cached
- **Response Cache**: Similar queries cached for 30 minutes

### Scaling Considerations

- **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
- **Database Sharding**: Partition Qdrant collections by topic
- **CDN**: Serve static assets from CDN
- **Rate Limiting**: Implement per-user rate limits

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

### Frontend Tests

```bash
cd client
npm test
```

### Integration Tests

```bash
npm run test:integration
```

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Ensure Redis server is running
   - Check connection URL in environment variables

2. **Qdrant Connection Failed**
   - Verify Qdrant server is accessible
   - Check API key and URL configuration

3. **API Key Errors**
   - Verify Gemini and Jina API keys are valid
   - Check API quotas and billing

4. **CORS Issues**
   - Ensure frontend URL is in CORS allowed origins
   - Check API gateway configuration

### Debug Mode

Enable debug logging:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom news source management
- [ ] Voice input/output
- [ ] Mobile app
- [ ] Advanced filtering and search
- [ ] User authentication
- [ ] Conversation export
- [ ] Real-time news updates
- [ ] Sentiment analysis

---

Built with ❤️ for the Voosh Full Stack Developer assignment.

