@echo off
REM Quick Share Script for RAG News Chatbot
echo 🚀 Starting RAG News Chatbot for immediate sharing...

REM Check if ngrok is installed
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ngrok is not installed!
    echo 📥 Please download ngrok from: https://ngrok.com/download
    echo 📁 Extract ngrok.exe to this folder
    pause
    exit /b 1
)

REM Start the app in background
echo 🔨 Starting the application...
start /B cmd /c "deploy.bat"

REM Wait for app to start
echo ⏳ Waiting for app to start...
timeout /t 30 /nobreak >nul

REM Configure ngrok auth token
echo 🔑 Setting up ngrok authentication...
ngrok config add-authtoken 32jrMgePrKK9Y1ECQPBlyw9nLiK_2oTaRvkcmXvcgN47Qruwf

REM Start ngrok
echo 🌐 Starting ngrok tunnel...
ngrok http 3000

echo ✅ Your app is now accessible via ngrok!
echo 📱 Share the ngrok URL with your professor
echo 🎯 Example: https://abc123.ngrok.io
pause
