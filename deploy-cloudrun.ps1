# CV Analyzer - Google Cloud Run Deployment Script (PowerShell)
# This script automates the deployment of the CV Analyzer application to Google Cloud Run

# Configuration
$PROJECT_ID = "cv-analyzer-tlstudio"
$REGION = "us-central1"
$DB_INSTANCE_NAME = "cv-analyzer-db"
$DB_NAME = "cv_analyzer"
$REPOSITORY_NAME = "cv-analyzer-repo"

Write-Host "========================================"
Write-Host "CV Analyzer - Google Cloud Run Deployment"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Function to print step
function Print-Step {
    param([string]$message)
    Write-Host "`n>>> $message" -ForegroundColor Yellow
    Write-Host ""
}

# Function to print success
function Print-Success {
    param([string]$message)
    Write-Host "[OK] $message" -ForegroundColor Green
}

# Function to print error
function Print-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if gcloud is installed
Print-Step "Checking prerequisites..."
try {
    $null = Get-Command gcloud -ErrorAction Stop
    Print-Success "gcloud CLI is installed"
} catch {
    Print-Error "gcloud CLI is not installed. Please install it from https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check if user is authenticated
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $activeAccount) {
    Print-Error "Not authenticated. Please run: gcloud auth login"
    exit 1
}
Print-Success "Authenticated with Google Cloud ($activeAccount)"

# Set project
Print-Step "Setting up project: $PROJECT_ID"
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Print-Success "Project set to $PROJECT_ID"

# Enable required APIs
Print-Step "Enabling required APIs..."
gcloud services enable `
    run.googleapis.com `
    sqladmin.googleapis.com `
    artifactregistry.googleapis.com `
    cloudbuild.googleapis.com `
    secretmanager.googleapis.com `
    --quiet 2>&1 | Out-Null

Print-Success "APIs enabled"

# Check if secrets exist
Print-Step "Checking secrets..."
$secretMissing = $false

$secrets = @("openai-api-key", "db-password")
foreach ($secret in $secrets) {
    try {
        gcloud secrets describe $secret --format="value(name)" 2>&1 | Out-Null
    } catch {
        Print-Error "Secret '$secret' not found. Please create it first:"
        Write-Host "  echo YOUR_VALUE | gcloud secrets create $secret --data-file=-"
        $secretMissing = $true
    }
}

if ($secretMissing) {
    Print-Error "Please create missing secrets and run this script again"
    exit 1
}

Print-Success "All required secrets exist"

# Create Artifact Registry repository if it doesn't exist
Print-Step "Setting up Artifact Registry..."
$repoExists = gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION --format="value(name)" 2>$null
if (-not $repoExists) {
    gcloud artifacts repositories create $REPOSITORY_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="CV Analyzer Docker images" 2>&1 | Out-Null
    Print-Success "Created Artifact Registry repository"
} else {
    Print-Success "Artifact Registry repository already exists"
}

# Configure Docker authentication
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet 2>&1 | Out-Null

# Check database configuration (Cloud SQL or Supabase)
Print-Step "Checking database configuration..."
$CLOUD_SQL_CONNECTION_NAME = $null
$USE_SUPABASE = $false

# Check if database-url secret exists (Supabase)
try {
    gcloud secrets describe database-url --format="value(name)" 2>&1 | Out-Null
    $USE_SUPABASE = $true
    Print-Success "Using Supabase/External database (database-url secret found)"
} catch {
    # Check if Cloud SQL instance exists
    $dbExists = gcloud sql instances describe $DB_INSTANCE_NAME --format="value(name)" 2>$null
    if (-not $dbExists) {
        Write-Host "No database configured (neither Supabase nor Cloud SQL)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Options:"
        Write-Host "1. Use Supabase (FREE) - Recommended"
        Write-Host "2. Create Cloud SQL (~`$7-15/month)"
        Write-Host ""
        $choice = Read-Host "Choose option (1 or 2)"
        
        if ($choice -eq "1") {
            Print-Error "Please setup Supabase first:"
            Write-Host "1. Sign up at https://supabase.com"
            Write-Host "2. Create a project and database"
            Write-Host "3. Run the SQL schema (see docs/FREE_DATABASE_OPTIONS.md)"
            Write-Host "4. Get connection string and create secret:"
            Write-Host "   echo 'YOUR_SUPABASE_URL' | gcloud secrets create database-url --data-file=-"
            Write-Host ""
            Write-Host "Then run this script again."
            exit 1
        } elseif ($choice -eq "2") {
            Print-Step "Creating Cloud SQL instance (this may take 5-10 minutes)..."
            
            # Get database password from secret
            $DB_PASSWORD = gcloud secrets versions access latest --secret="db-password"
            
            gcloud sql instances create $DB_INSTANCE_NAME `
                --database-version=POSTGRES_15 `
                --tier=db-f1-micro `
                --region=$REGION `
                --root-password="$DB_PASSWORD" `
                --quiet
            
            # Create database
            gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
            
            Print-Success "Cloud SQL instance created"
            Write-Host "Please connect to the database and run: CREATE EXTENSION IF NOT EXISTS vector;"
            Write-Host "Connection command: gcloud sql connect $DB_INSTANCE_NAME --user=postgres"
            
            $CLOUD_SQL_CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)"
            Print-Success "Cloud SQL connection name: $CLOUD_SQL_CONNECTION_NAME"
        } else {
            Print-Error "Invalid choice"
            exit 1
        }
    } else {
        Print-Success "Cloud SQL instance exists"
        $CLOUD_SQL_CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)"
        Print-Success "Cloud SQL connection name: $CLOUD_SQL_CONNECTION_NAME"
    }
}

# Build and push backend
Print-Step "Building and pushing backend image..."
Push-Location backend
try {
    docker build -f Dockerfile.cloudrun -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest" .
    if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
    
    docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest"
    if ($LASTEXITCODE -ne 0) { throw "Docker push failed" }
} catch {
    Print-Error "Failed to build/push backend image: $_"
    Pop-Location
    exit 1
}
Pop-Location
Print-Success "Backend image built and pushed"

# Deploy backend
Print-Step "Deploying backend to Cloud Run..."
if ($CLOUD_SQL_CONNECTION_NAME) {
    # Deploy with Cloud SQL
    gcloud run deploy cv-analyzer-backend `
        --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest" `
        --platform managed `
        --region $REGION `
        --allow-unauthenticated `
        --add-cloudsql-instances $CLOUD_SQL_CONNECTION_NAME `
        --set-env-vars="DB_USER=postgres,DB_NAME=$DB_NAME,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,FRONTEND_URL=*" `
        --set-secrets="DB_PASSWORD=db-password:latest,OPENAI_API_KEY=openai-api-key:latest,OPENAI_EMBED_API_KEY=openai-embed-api-key:latest" `
        --memory 1Gi `
        --cpu 1 `
        --timeout 300 `
        --max-instances 10 `
        --min-instances 0 `
        --quiet
} else {
    # Deploy with external database (Supabase)
    gcloud run deploy cv-analyzer-backend `
        --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest" `
        --platform managed `
        --region $REGION `
        --allow-unauthenticated `
        --set-env-vars="FRONTEND_URL=*" `
        --set-secrets="DATABASE_URL=database-url:latest,OPENAI_API_KEY=openai-api-key:latest,OPENAI_EMBED_API_KEY=openai-embed-api-key:latest" `
        --memory 1Gi `
        --cpu 1 `
        --timeout 300 `
        --max-instances 10 `
        --min-instances 0 `
        --quiet
}

$BACKEND_URL = gcloud run services describe cv-analyzer-backend --region $REGION --format="value(status.url)"
Print-Success "Backend deployed: $BACKEND_URL"

# Prepare Google Analytics measurement ID for frontend build
$GA_MEASUREMENT_ID = $env:VITE_GA_MEASUREMENT_ID
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
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend URL: " -NoNewline
Write-Host $FRONTEND_URL -ForegroundColor Green
Write-Host "Backend URL:  " -NoNewline
Write-Host $BACKEND_URL -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test the application by visiting the frontend URL"
Write-Host "2. Upload some CVs to test the functionality"
Write-Host "3. Check logs: gcloud run services logs read cv-analyzer-backend --region $REGION"
Write-Host "4. Monitor costs in Cloud Console: https://console.cloud.google.com/billing"
Write-Host ""
Print-Success "Deployment successful!"

