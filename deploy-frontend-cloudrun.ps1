# CV Analyzer - Deploy Frontend to Google Cloud Run
# This script deploys only the frontend to Google Cloud Run

$ErrorActionPreference = "Stop"

# Colors for output
function Print-Step {
    param([string]$Message)
    Write-Host "`n>>> $Message`n" -ForegroundColor Yellow
}

function Print-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "Deploy Frontend to Google Cloud Run" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Configuration
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "cv-analyzer-tlstudio" }
$REGION = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$REPOSITORY_NAME = "cv-analyzer-repo"

# Check if gcloud is installed
Print-Step "Checking prerequisites..."
try {
    $null = gcloud --version 2>&1
    Print-Success "gcloud CLI is installed"
} catch {
    Print-Error "gcloud CLI is not installed. Please install it from https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check if user is authenticated
try {
    $null = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    Print-Success "Authenticated with Google Cloud"
} catch {
    Print-Error "Not authenticated. Please run: gcloud auth login"
    exit 1
}

# Set project
Print-Step "Setting up project: $PROJECT_ID"
gcloud config set project $PROJECT_ID
Print-Success "Project set to $PROJECT_ID"

# Get backend URL
Print-Step "Getting backend URL..."
try {
    $null = gcloud run services describe cv-analyzer-backend --region $REGION 2>&1
    $BACKEND_URL = gcloud run services describe cv-analyzer-backend --region $REGION --format="value(status.url)"
    Print-Success "Backend URL: $BACKEND_URL"
} catch {
    Print-Error "Backend service 'cv-analyzer-backend' not found in region $REGION"
    $BACKEND_URL = Read-Host "Please provide the backend URL manually"
}

# Check if Artifact Registry repository exists
Print-Step "Checking Artifact Registry..."
try {
    $null = gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION 2>&1
    Print-Success "Artifact Registry repository exists"
} catch {
    Print-Error "Artifact Registry repository '$REPOSITORY_NAME' not found"
    Write-Host "Creating repository..."
    gcloud artifacts repositories create $REPOSITORY_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="CV Analyzer Docker images"
    Print-Success "Created Artifact Registry repository"
}

# Configure Docker authentication
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Get Google Analytics Measurement ID (optional)
$GA_MEASUREMENT_ID = if ($env:VITE_GA_MEASUREMENT_ID) { $env:VITE_GA_MEASUREMENT_ID } else { "" }
if (-not $GA_MEASUREMENT_ID) {
    $GA_MEASUREMENT_ID = Read-Host "Enter Google Analytics Measurement ID (leave blank to skip)"
}

if ($GA_MEASUREMENT_ID) {
    Print-Success "Using Google Analytics Measurement ID: $GA_MEASUREMENT_ID"
} else {
    Write-Host "Google Analytics Measurement ID not provided; analytics will be disabled." -ForegroundColor Yellow
}

# Build and push frontend
Print-Step "Building and pushing frontend image..."
Push-Location frontend
try {
    $dockerBuildArgs = @()
    $dockerBuildArgs += @("--build-arg", "VITE_API_URL=$BACKEND_URL")
    if ($GA_MEASUREMENT_ID) {
        $dockerBuildArgs += @("--build-arg", "VITE_GA_MEASUREMENT_ID=$GA_MEASUREMENT_ID")
    }
    $dockerBuildArgs += @("-f", "Dockerfile.cloudrun", "-t", "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest", ".")

    docker build $dockerBuildArgs
    if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
    
    docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest"
    if ($LASTEXITCODE -ne 0) { throw "Docker push failed" }
} catch {
    Print-Error "Failed to build/push frontend image: $_"
    Pop-Location
    exit 1
}
Pop-Location
Print-Success "Frontend image built and pushed"

# Deploy frontend
Print-Step "Deploying frontend to Cloud Run..."
try {
    gcloud run deploy cv-analyzer-frontend `
        --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest" `
        --platform managed `
        --region $REGION `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --max-instances 10 `
        --min-instances 0 `
        --quiet

    if ($LASTEXITCODE -ne 0) { throw "Deployment failed" }
} catch {
    Print-Error "Failed to deploy frontend: $_"
    exit 1
}

$FRONTEND_URL = gcloud run services describe cv-analyzer-frontend --region $REGION --format="value(status.url)"
Print-Success "Frontend deployed: $FRONTEND_URL"

# Update backend with correct frontend URL
Print-Step "Updating backend CORS settings..."
gcloud run services update cv-analyzer-backend `
    --region $REGION `
    --set-env-vars="FRONTEND_URL=$FRONTEND_URL" `
    --quiet 2>&1 | Out-Null

Print-Success "CORS settings updated"

# Print summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Frontend Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend URL: $FRONTEND_URL" -ForegroundColor Green
Write-Host "Backend URL:  $BACKEND_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test the application by visiting: $FRONTEND_URL"
Write-Host "2. Check logs: gcloud run services logs read cv-analyzer-frontend --region $REGION"
Write-Host ""
Print-Success "Deployment successful!"

