# 🚀 How to Share Your RAG News Chatbot

## 📋 Prerequisites
- Docker and Docker Compose installed
- Gemini API key (get from https://makersuite.google.com/app/apikey)

## 🎯 Quick Start (Docker - Recommended)

### For Windows Users:
1. Download the project folder
2. Double-click `deploy.bat`
3. Edit `.env` file with your API keys
4. Press Enter to continue
5. Open http://localhost:3000

### For Mac/Linux Users:
1. Download the project folder
2. Run: `chmod +x deploy.sh && ./deploy.sh`
3. Edit `.env` file with your API keys
4. Press Enter to continue
5. Open http://localhost:3000

## 🌐 Cloud Deployment Options

### Option A: Railway (Easiest)
1. Push code to GitHub
2. Connect to Railway.app
3. Add environment variables:
   - `GEMINI_API_KEY`
   - `QDRANT_API_KEY`
4. Deploy automatically

### Option B: Heroku
1. Create Heroku app
2. Add Redis and Qdrant add-ons
3. Deploy using Docker containers

### Option C: DigitalOcean App Platform
1. Connect GitHub repository
2. Configure environment variables
3. Deploy with Docker

## 📦 Manual Installation (Advanced)

### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup:
```bash
cd client
npm install
npm start
```

### Services Setup:
- Install Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
- Install Redis: `docker run -p 6379:6379 redis:alpine`

## 🔧 Configuration

### Required Environment Variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `QDRANT_API_KEY`: Optional for local deployment
- `REDIS_URL`: Redis connection string
- `QDRANT_URL`: Qdrant connection string

### Optional Settings:
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)
- `TOP_K_RESULTS`: Number of results to retrieve (default: 5)

## 🐛 Troubleshooting

### Common Issues:
1. **Port already in use**: Change ports in docker-compose.yml
2. **API key errors**: Check .env file configuration
3. **Services not starting**: Check Docker logs
4. **No news articles**: Run news ingestion manually

### Getting Help:
- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`
- Full reset: `docker-compose down -v && docker-compose up --build`

## 📱 Sharing Methods

### 1. GitHub Repository
- Push to GitHub
- Share repository link
- Include setup instructions

### 2. Docker Image
- Build Docker image
- Push to Docker Hub
- Share image name

### 3. Cloud URL
- Deploy to cloud platform
- Share public URL
- No installation required

### 4. ZIP File
- Package entire project
- Include all dependencies
- Share with instructions

## 🎉 Success!
Once deployed, users can:
- Ask questions about current news
- View chat history
- Create new sessions
- Get AI-powered news summaries

## 📞 Support
If you need help, check the logs or create an issue in the repository.
