@echo off
REM CV Analyzer - Google Cloud Run Deployment Script (Windows)
REM This script automates the deployment of the CV Analyzer application to Google Cloud Run

setlocal EnableDelayedExpansion

REM Configuration
set PROJECT_ID=cv-analyzer-tlstudio
set REGION=us-central1
set DB_INSTANCE_NAME=cv-analyzer-db
set DB_NAME=cv_analyzer
set REPOSITORY_NAME=cv-analyzer-repo

echo ========================================
echo CV Analyzer - Google Cloud Run Deployment
echo ========================================
echo.

REM Check if gcloud is installed
echo Checking prerequisites...
where gcloud >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: gcloud CLI is not installed.
    echo Please install it from https://cloud.google.com/sdk/docs/install
    exit /b 1
)
echo [OK] gcloud CLI is installed

REM Set project
echo.
echo Setting up project: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo.
echo Enabling required APIs...
gcloud services enable run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com --quiet

REM Check secrets
echo.
echo Checking secrets...
gcloud secrets describe openai-api-key >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Secret 'openai-api-key' not found
    echo Please create it: echo YOUR_API_KEY | gcloud secrets create openai-api-key --data-file=-
    exit /b 1
)

gcloud secrets describe db-password >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Secret 'db-password' not found
    echo Please create it: echo YOUR_PASSWORD | gcloud secrets create db-password --data-file=-
    exit /b 1
)

echo [OK] All required secrets exist

REM Create Artifact Registry
echo.
echo Setting up Artifact Registry...
gcloud artifacts repositories describe %REPOSITORY_NAME% --location=%REGION% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    gcloud artifacts repositories create %REPOSITORY_NAME% --repository-format=docker --location=%REGION% --description="CV Analyzer Docker images"
    echo [OK] Created Artifact Registry repository
) else (
    echo [OK] Artifact Registry repository already exists
)

gcloud auth configure-docker %REGION%-docker.pkg.dev --quiet

REM Get Cloud SQL connection name
echo.
echo Getting Cloud SQL connection name...
for /f "delims=" %%i in ('gcloud sql instances describe %DB_INSTANCE_NAME% --format="value(connectionName)"') do set CLOUD_SQL_CONNECTION_NAME=%%i
echo [OK] Cloud SQL connection: %CLOUD_SQL_CONNECTION_NAME%

REM Build and push backend
echo.
echo Building backend image...
cd backend
docker build -f Dockerfile.cloudrun -t %REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY_NAME%/backend:latest .
echo Pushing backend image...
docker push %REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY_NAME%/backend:latest
cd ..

REM Deploy backend
echo.
echo Deploying backend to Cloud Run...
gcloud run deploy cv-analyzer-backend --image %REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY_NAME%/backend:latest --platform managed --region %REGION% --allow-unauthenticated --add-cloudsql-instances %CLOUD_SQL_CONNECTION_NAME% --set-env-vars="DB_USER=postgres,DB_NAME=%DB_NAME%,CLOUD_SQL_CONNECTION_NAME=%CLOUD_SQL_CONNECTION_NAME%,FRONTEND_URL=*" --set-secrets="DB_PASSWORD=db-password:latest,OPENAI_API_KEY=openai-api-key:latest,OPENAI_EMBED_API_KEY=openai-embed-api-key:latest" --memory 1Gi --cpu 1 --timeout 300 --max-instances 10 --min-instances 0 --quiet

for /f "delims=" %%i in ('gcloud run services describe cv-analyzer-backend --region %REGION% --format="value(status.url)"') do set BACKEND_URL=%%i
echo [OK] Backend deployed: %BACKEND_URL%

REM Build and push frontend
echo.
echo Building frontend image...
cd frontend
docker build --build-arg VITE_API_URL=%BACKEND_URL% -f Dockerfile.cloudrun -t %REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY_NAME%/frontend:latest .
echo Pushing frontend image...
docker push %REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY_NAME%/frontend:latest
cd ..

REM Deploy frontend
echo.
echo Deploying frontend to Cloud Run...
gcloud run deploy cv-analyzer-frontend --image %REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY_NAME%/frontend:latest --platform managed --region %REGION% --allow-unauthenticated --memory 512Mi --cpu 1 --max-instances 10 --min-instances 0 --quiet

for /f "delims=" %%i in ('gcloud run services describe cv-analyzer-frontend --region %REGION% --format="value(status.url)"') do set FRONTEND_URL=%%i
echo [OK] Frontend deployed: %FRONTEND_URL%

REM Update backend CORS
echo.
echo Updating backend CORS settings...
gcloud run services update cv-analyzer-backend --region %REGION% --set-env-vars="FRONTEND_URL=%FRONTEND_URL%" --quiet

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Frontend URL: %FRONTEND_URL%
echo Backend URL:  %BACKEND_URL%
echo.
echo Next steps:
echo 1. Visit the frontend URL to test the application
echo 2. Upload CVs and test all features
echo 3. Check logs: gcloud run services logs read cv-analyzer-backend --region %REGION%
echo.

endlocal

