#!/bin/bash

# CV Analyzer - Google Cloud Run Deployment Script
# This script automates the deployment of the CV Analyzer application to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"cv-analyzer-tlstudio"}
REGION=${GCP_REGION:-"us-central1"}
DB_INSTANCE_NAME="cv-analyzer-db"
DB_NAME="cv_analyzer"
REPOSITORY_NAME="cv-analyzer-repo"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CV Analyzer - Google Cloud Run Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "\n${YELLOW}>>> $1${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if gcloud is installed
print_step "Checking prerequisites..."
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it from https://cloud.google.com/sdk/docs/install"
    exit 1
fi
print_success "gcloud CLI is installed"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    print_error "Not authenticated. Please run: gcloud auth login"
    exit 1
fi
print_success "Authenticated with Google Cloud"

# Set project
print_step "Setting up project: $PROJECT_ID"
gcloud config set project $PROJECT_ID
print_success "Project set to $PROJECT_ID"

# Enable required APIs
print_step "Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --quiet

print_success "APIs enabled"

# Check if secrets exist
print_step "Checking secrets..."
SECRET_MISSING=false

if ! gcloud secrets describe openai-api-key &> /dev/null; then
    print_error "Secret 'openai-api-key' not found. Please create it first:"
    echo "  echo -n 'YOUR_API_KEY' | gcloud secrets create openai-api-key --data-file=-"
    SECRET_MISSING=true
fi

if ! gcloud secrets describe db-password &> /dev/null; then
    print_error "Secret 'db-password' not found. Please create it first:"
    echo "  echo -n 'YOUR_DB_PASSWORD' | gcloud secrets create db-password --data-file=-"
    SECRET_MISSING=true
fi

if ! gcloud secrets describe openai-embed-api-key &> /dev/null; then
    print_error "Secret 'openai-embed-api-key' not found. Please create it first:"
    echo "  echo -n 'YOUR_API_KEY' | gcloud secrets create openai-embed-api-key --data-file=-"
    SECRET_MISSING=true
fi

# Optional secrets
if ! gcloud secrets describe tavily-api-key &> /dev/null; then
    print_error "Secret 'tavily-api-key' not found (optional for web search). Create it:"
    echo "  echo -n 'YOUR_API_KEY' | gcloud secrets create tavily-api-key --data-file=-"
fi

if [ "$SECRET_MISSING" = true ]; then
    print_error "Please create missing required secrets and run this script again"
    exit 1
fi

print_success "All required secrets exist"

# Create Artifact Registry repository if it doesn't exist
print_step "Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION &> /dev/null; then
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="CV Analyzer Docker images"
    print_success "Created Artifact Registry repository"
else
    print_success "Artifact Registry repository already exists"
fi

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Check if Cloud SQL instance exists
print_step "Checking Cloud SQL instance..."
if ! gcloud sql instances describe $DB_INSTANCE_NAME &> /dev/null; then
    print_error "Cloud SQL instance '$DB_INSTANCE_NAME' not found"
    echo "Would you like to create it now? (y/n)"
    read -r CREATE_DB
    if [ "$CREATE_DB" = "y" ]; then
        print_step "Creating Cloud SQL instance (this may take 5-10 minutes)..."
        
        # Get database password from secret
        DB_PASSWORD=$(gcloud secrets versions access latest --secret="db-password")
        
        gcloud sql instances create $DB_INSTANCE_NAME \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=$REGION \
            --root-password="$DB_PASSWORD" \
            --quiet
        
        # Create database
        gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
        
        print_success "Cloud SQL instance created"
        
        # Install pgvector extension
        print_step "Installing pgvector extension..."
        echo "Please connect to the database and run: CREATE EXTENSION IF NOT EXISTS vector;"
        echo "Connection command: gcloud sql connect $DB_INSTANCE_NAME --user=postgres"
    else
        print_error "Cloud SQL instance is required. Please create it manually and run this script again"
        exit 1
    fi
else
    print_success "Cloud SQL instance exists"
fi

# Get Cloud SQL connection name
CLOUD_SQL_CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")
print_success "Cloud SQL connection name: $CLOUD_SQL_CONNECTION_NAME"

# Build and push backend
print_step "Building and pushing backend image..."
cd backend
gcloud builds submit \
    --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest \
    --config=../cloudbuild-backend.yaml \
    --quiet || \
    docker build -f Dockerfile.cloudrun -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest . && \
    docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest

cd ..
print_success "Backend image built and pushed"

# Deploy backend
print_step "Deploying backend to Cloud Run..."
# Build secrets list
SECRETS="DB_PASSWORD=db-password:latest,OPENAI_API_KEY=openai-api-key:latest,OPENAI_EMBED_API_KEY=openai-embed-api-key:latest"

# Add optional TAVILY_API_KEY if secret exists
if gcloud secrets describe tavily-api-key &> /dev/null; then
    SECRETS="$SECRETS,TAVILY_API_KEY=tavily-api-key:latest"
    print_success "Tavily API key secret found, will be included in deployment"
fi

gcloud run deploy cv-analyzer-backend \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/backend:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CLOUD_SQL_CONNECTION_NAME \
    --set-env-vars="DB_USER=postgres,DB_NAME=$DB_NAME,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,FRONTEND_URL=*" \
    --set-secrets="$SECRETS" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --quiet

BACKEND_URL=$(gcloud run services describe cv-analyzer-backend --region $REGION --format="value(status.url)")
print_success "Backend deployed: $BACKEND_URL"

# Build and push frontend
print_step "Building and pushing frontend image..."
cd frontend
GA_MEASUREMENT_ID=${VITE_GA_MEASUREMENT_ID:-""}
docker build \
    --build-arg VITE_API_URL=$BACKEND_URL \
    --build-arg VITE_GA_MEASUREMENT_ID=$GA_MEASUREMENT_ID \
    -f Dockerfile.cloudrun \
    -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest .

docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest
cd ..
print_success "Frontend image built and pushed"

# Deploy frontend
print_step "Deploying frontend to Cloud Run..."
gcloud run deploy cv-analyzer-frontend \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --quiet

FRONTEND_URL=$(gcloud run services describe cv-analyzer-frontend --region $REGION --format="value(status.url)")
print_success "Frontend deployed: $FRONTEND_URL"

# Update backend with correct frontend URL
print_step "Updating backend CORS settings..."
gcloud run services update cv-analyzer-backend \
    --region $REGION \
    --set-env-vars="FRONTEND_URL=$FRONTEND_URL" \
    --quiet

print_success "CORS settings updated"

# Print summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Frontend URL: ${GREEN}$FRONTEND_URL${NC}"
echo -e "Backend URL:  ${GREEN}$BACKEND_URL${NC}"
echo ""
echo -e "Next steps:"
echo "1. Test the application by visiting the frontend URL"
echo "2. Upload some CVs to test the functionality"
echo "3. Check logs: gcloud run services logs read cv-analyzer-backend --region $REGION"
echo "4. Monitor costs in Cloud Console: https://console.cloud.google.com/billing"
echo ""
print_success "Deployment successful!"

