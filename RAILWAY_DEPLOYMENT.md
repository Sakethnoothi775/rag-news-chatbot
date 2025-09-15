# 🚀 Deploy RAG News Chatbot to Railway.app

## 📋 Prerequisites
- GitHub account
- Railway.app account (free)
- Gemini API key

## 🎯 Step-by-Step Deployment

### Step 1: Prepare Your Code
```bash
# 1. Push your code to GitHub
git init
git add .
git commit -m "Initial commit: RAG News Chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rag-news-chatbot.git
git push -u origin main
```

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `rag-news-chatbot` repository

### Step 3: Configure Services
Railway will automatically detect your `docker-compose.production.yml` and create these services:

- **Backend** (Python FastAPI)
- **Frontend** (React)
- **Gateway** (Node.js)
- **Qdrant** (Vector Database)
- **Redis** (Session Storage)

### Step 4: Add Environment Variables
In Railway dashboard, go to each service and add:

#### Backend Service:
```
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
```

#### Frontend Service:
```
REACT_APP_API_URL=https://your-gateway-url.railway.app/api
```

#### Gateway Service:
```
BACKEND_URL=http://backend:8000
```

### Step 5: Deploy
1. Railway will automatically build and deploy
2. Wait for all services to be "Healthy"
3. Get your public URLs from the dashboard

## 🔧 Railway Configuration Files

### railway.json (Already created)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "docker-compose -f docker-compose.production.yml up",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Docker Compose for Railway
Railway will use your `docker-compose.production.yml` file.

## 🌐 After Deployment

### Your App URLs:
- **Frontend**: `https://your-frontend-url.railway.app`
- **Backend API**: `https://your-backend-url.railway.app`
- **Gateway**: `https://your-gateway-url.railway.app`

### Initialize the App:
1. Go to your backend URL
2. Run: `/ingest` endpoint to load news
3. Run: `/setup-embeddings` to create vectors
4. Start chatting!

## 🔑 Getting API Keys

### Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Add to Railway environment variables

### Qdrant API Key (Optional):
- Leave empty for Railway's managed Qdrant
- Or get from [Qdrant Cloud](https://cloud.qdrant.io)

## 📊 Monitoring

### View Logs:
1. Go to Railway dashboard
2. Click on each service
3. View "Logs" tab

### Check Health:
1. Services should show "Healthy" status
2. Check individual service URLs
3. Monitor resource usage

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check Dockerfile syntax
   - Verify all files are committed
   - Check Railway logs

2. **Services Not Starting**:
   - Verify environment variables
   - Check service dependencies
   - Review startup commands

3. **No News Articles**:
   - Call `/ingest` endpoint manually
   - Check news ingestion logs
   - Verify RSS feed URLs

4. **Frontend Can't Connect**:
   - Check `REACT_APP_API_URL` variable
   - Verify gateway service is running
   - Check CORS settings

### Debug Commands:
```bash
# Check service status
railway status

# View logs
railway logs

# Connect to service
railway shell
```

## 💰 Railway Pricing

### Free Tier:
- ✅ 500 hours/month
- ✅ 1GB RAM per service
- ✅ 1GB storage
- ✅ Perfect for development/testing

### Pro Tier ($5/month):
- ✅ Unlimited hours
- ✅ More resources
- ✅ Better performance
- ✅ Production ready

## 🚀 Production Tips

### 1. Custom Domain:
- Add custom domain in Railway
- Update `REACT_APP_API_URL` accordingly

### 2. Database Persistence:
- Railway provides persistent storage
- Data survives deployments

### 3. Environment Management:
- Use Railway's environment variables
- Keep secrets secure

### 4. Monitoring:
- Set up alerts
- Monitor resource usage
- Check error rates

## 🎉 Success!

Once deployed, your RAG news chatbot will be:
- ✅ Publicly accessible
- ✅ Always online
- ✅ Auto-updating
- ✅ Scalable

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Create issue in your repo

## 🔄 Updates

To update your app:
1. Push changes to GitHub
2. Railway auto-deploys
3. New version goes live

That's it! Your RAG news chatbot is now live on Railway! 🚀
