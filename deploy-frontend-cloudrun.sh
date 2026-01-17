#!/bin/bash

# CV Analyzer - Deploy Frontend to Google Cloud Run
# This script deploys only the frontend to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"cv-analyzer-tlstudio"}
REGION=${GCP_REGION:-"us-central1"}
REPOSITORY_NAME="cv-analyzer-repo"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploy Frontend to Google Cloud Run${NC}"
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

# Get backend URL
print_step "Getting backend URL..."
if ! gcloud run services describe cv-analyzer-backend --region $REGION &> /dev/null; then
    print_error "Backend service 'cv-analyzer-backend' not found in region $REGION"
    echo "Please provide the backend URL manually:"
    read -p "Backend URL: " BACKEND_URL
else
    BACKEND_URL=$(gcloud run services describe cv-analyzer-backend --region $REGION --format="value(status.url)")
    print_success "Backend URL: $BACKEND_URL"
fi

# Check if Artifact Registry repository exists
print_step "Checking Artifact Registry..."
if ! gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION &> /dev/null; then
    print_error "Artifact Registry repository '$REPOSITORY_NAME' not found"
    echo "Creating repository..."
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="CV Analyzer Docker images"
    print_success "Created Artifact Registry repository"
else
    print_success "Artifact Registry repository exists"
fi

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Get Google Analytics Measurement ID (optional)
GA_MEASUREMENT_ID=${VITE_GA_MEASUREMENT_ID:-""}
if [ -z "$GA_MEASUREMENT_ID" ]; then
    read -p "Enter Google Analytics Measurement ID (leave blank to skip): " GA_MEASUREMENT_ID
fi

if [ -n "$GA_MEASUREMENT_ID" ]; then
    print_success "Using Google Analytics Measurement ID: $GA_MEASUREMENT_ID"
else
    echo "Google Analytics Measurement ID not provided; analytics will be disabled."
fi

# Build and push frontend
print_step "Building and pushing frontend image..."
cd frontend

# Build Docker image
BUILD_ARGS="--build-arg VITE_API_URL=$BACKEND_URL"
if [ -n "$GA_MEASUREMENT_ID" ]; then
    BUILD_ARGS="$BUILD_ARGS --build-arg VITE_GA_MEASUREMENT_ID=$GA_MEASUREMENT_ID"
fi

docker build \
    $BUILD_ARGS \
    -f Dockerfile.cloudrun \
    -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest .

if [ $? -ne 0 ]; then
    print_error "Docker build failed"
    cd ..
    exit 1
fi

# Push image
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/frontend:latest

if [ $? -ne 0 ]; then
    print_error "Docker push failed"
    cd ..
    exit 1
fi

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

if [ $? -ne 0 ]; then
    print_error "Deployment failed"
    exit 1
fi

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
echo -e "${GREEN}Frontend Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Frontend URL: ${GREEN}$FRONTEND_URL${NC}"
echo -e "Backend URL:  ${GREEN}$BACKEND_URL${NC}"
echo ""
echo -e "Next steps:"
echo "1. Test the application by visiting: $FRONTEND_URL"
echo "2. Check logs: gcloud run services logs read cv-analyzer-frontend --region $REGION"
echo ""
print_success "Deployment successful!"

