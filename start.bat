@echo off

REM CV Analyzer Startup Script for Windows

echo 🚀 Starting CV Analyzer Application...

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy env.example .env
    echo 📝 Please edit .env file and add your OpenAI API key
    echo    Then run this script again.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

echo 🐳 Building and starting services...
docker-compose up --build -d

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service health...

REM Check backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend is not responding. Check logs with: docker-compose logs backend
) else (
    echo ✅ Backend is running at http://localhost:8000
)

REM Check frontend
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend is not responding. Check logs with: docker-compose logs frontend
) else (
    echo ✅ Frontend is running at http://localhost:3000
)

echo.
echo 🎉 CV Analyzer is ready!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo To stop the application, run: docker-compose down
echo To view logs, run: docker-compose logs -f

pause

