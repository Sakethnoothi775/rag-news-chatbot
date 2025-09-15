@echo off
REM RAG News Chatbot Deployment Script for Windows

echo 🚀 Deploying RAG News Chatbot...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo    Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # API Keys ^(Required^)
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo QDRANT_API_KEY=your_qdrant_api_key_here
        echo.
        echo # Optional: Customize settings
        echo PORT=5000
        echo HOST=0.0.0.0
    ) > .env
    echo ⚠️  Please edit .env file and add your API keys!
    echo    - Get Gemini API key: https://makersuite.google.com/app/apikey
    echo    - Qdrant API key is optional for local deployment
    pause
)

REM Build and start services
echo 🔨 Building and starting services...
docker-compose -f docker-compose.production.yml up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose -f docker-compose.production.yml ps

REM Run news ingestion
echo 📰 Ingesting news articles...
docker-compose -f docker-compose.production.yml exec backend python news_ingestion.py

REM Setup embeddings
echo 🧠 Setting up embeddings...
docker-compose -f docker-compose.production.yml exec backend python rag_pipeline_simple.py

echo ✅ Deployment complete!
echo.
echo 🌐 Your app is now available at:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Gateway: http://localhost:5000
echo.
echo 📊 To view logs:
echo    docker-compose -f docker-compose.production.yml logs -f
echo.
echo 🛑 To stop the app:
echo    docker-compose -f docker-compose.production.yml down
pause
