# CV Analyzer - GitHub CI/CD Setup Script (PowerShell)
# This script helps set up GitHub Actions for automated deployment to Cloud Run

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
Write-Host "GitHub CI/CD Setup for Cloud Run" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Configuration
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "cv-analyzer-tlstudio" }
$SA_NAME = "github-actions-deployer"
$SA_EMAIL = "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

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

# Check if service account already exists
Print-Step "Checking service account..."
try {
    $null = gcloud iam service-accounts describe $SA_EMAIL 2>&1
    Print-Success "Service account already exists: $SA_EMAIL"
    $CREATE_KEY = Read-Host "Do you want to create a new key? (y/n)"
    if ($CREATE_KEY -ne "y") {
        Write-Host "Skipping key creation. Exiting..."
        exit 0
    }
} catch {
    # Create service account
    Print-Step "Creating service account..."
    gcloud iam service-accounts create $SA_NAME `
        --display-name="GitHub Actions Deployer" `
        --project=$PROJECT_ID `
        --quiet
    
    Print-Success "Service account created: $SA_EMAIL"
}

# Grant permissions
Print-Step "Granting permissions..."

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${SA_EMAIL}" `
    --role="roles/run.admin" `
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${SA_EMAIL}" `
    --role="roles/artifactregistry.writer" `
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${SA_EMAIL}" `
    --role="roles/iam.serviceAccountUser" `
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:${SA_EMAIL}" `
    --role="roles/secretmanager.secretAccessor" `
    --quiet

Print-Success "Permissions granted"

# Create and download key
Print-Step "Creating service account key..."
gcloud iam service-accounts keys create github-actions-key.json `
    --iam-account=$SA_EMAIL `
    --project=$PROJECT_ID

Print-Success "Service account key created: github-actions-key.json"

# Get Cloud SQL connection name
Print-Step "Getting Cloud SQL connection name..."
try {
    $CLOUD_SQL_CONNECTION = gcloud sql instances describe cv-analyzer-db --format="value(connectionName)" 2>&1
    if (-not $CLOUD_SQL_CONNECTION) { throw }
    Print-Success "Cloud SQL connection: $CLOUD_SQL_CONNECTION"
} catch {
    Print-Error "Cloud SQL instance 'cv-analyzer-db' not found"
    $CLOUD_SQL_CONNECTION = Read-Host "Enter Cloud SQL connection name manually (format: PROJECT:REGION:INSTANCE)"
}

# Display summary and instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "1. Add GitHub Secrets:"
Write-Host "   Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
Write-Host "   Click 'New repository secret' and add:"
Write-Host ""
Write-Host "   GCP_SA_KEY" -ForegroundColor Yellow
Write-Host "   - Name: GCP_SA_KEY"
Write-Host "   - Value: Copy the entire contents of github-actions-key.json"
Write-Host "   - Command: Get-Content github-actions-key.json | Set-Clipboard"
Write-Host ""
Write-Host "   CLOUD_SQL_CONNECTION_NAME" -ForegroundColor Yellow
Write-Host "   - Name: CLOUD_SQL_CONNECTION_NAME"
Write-Host "   - Value: $CLOUD_SQL_CONNECTION"
Write-Host ""
Write-Host "   VITE_GA_MEASUREMENT_ID (Optional)" -ForegroundColor Yellow
Write-Host "   - Name: VITE_GA_MEASUREMENT_ID"
Write-Host "   - Value: Your Google Analytics Measurement ID (if used)"
Write-Host ""
Write-Host "2. Verify workflow file exists:"
Write-Host "   .github/workflows/deploy.yml"
Write-Host ""
Write-Host "3. Commit and push:"
Write-Host "   git add .github/workflows/deploy.yml"
Write-Host "   git commit -m 'feat: add GitHub Actions CI/CD'"
Write-Host "   git push origin main"
Write-Host ""
Write-Host "4. Test deployment:"
Write-Host "   - Make a change and push to main branch"
Write-Host "   - Or merge a pull request into main"
Write-Host "   - Check Actions tab in GitHub to see the workflow run"
Write-Host ""
Write-Host "⚠️  IMPORTANT:" -ForegroundColor Red
Write-Host "   - Keep github-actions-key.json secure"
Write-Host "   - Delete it after adding to GitHub Secrets"
Write-Host "   - Never commit this file to git!"
Write-Host ""
Print-Success "Setup script completed!"

