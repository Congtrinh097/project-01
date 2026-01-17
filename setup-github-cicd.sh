#!/bin/bash

# CV Analyzer - GitHub CI/CD Setup Script
# This script helps set up GitHub Actions for automated deployment to Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"cv-analyzer-tlstudio"}
SA_NAME="github-actions-deployer"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GitHub CI/CD Setup for Cloud Run${NC}"
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

# Check if service account already exists
print_step "Checking service account..."
if gcloud iam service-accounts describe $SA_EMAIL &> /dev/null; then
    print_success "Service account already exists: $SA_EMAIL"
    read -p "Do you want to create a new key? (y/n): " CREATE_KEY
    if [ "$CREATE_KEY" != "y" ]; then
        echo "Skipping key creation. Exiting..."
        exit 0
    fi
else
    # Create service account
    print_step "Creating service account..."
    gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions Deployer" \
        --project=$PROJECT_ID \
        --quiet
    
    print_success "Service account created: $SA_EMAIL"
fi

# Grant permissions
print_step "Granting permissions..."

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

print_success "Permissions granted"

# Create and download key
print_step "Creating service account key..."
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

print_success "Service account key created: github-actions-key.json"

# Get Cloud SQL connection name
print_step "Getting Cloud SQL connection name..."
CLOUD_SQL_CONNECTION=$(gcloud sql instances describe cv-analyzer-db \
    --format="value(connectionName)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONNECTION" ]; then
    print_error "Cloud SQL instance 'cv-analyzer-db' not found"
    read -p "Enter Cloud SQL connection name manually (format: PROJECT:REGION:INSTANCE): " CLOUD_SQL_CONNECTION
fi

print_success "Cloud SQL connection: $CLOUD_SQL_CONNECTION"

# Display summary and instructions
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Add GitHub Secrets:"
echo "   Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "   Click 'New repository secret' and add:"
echo ""
echo "   ${YELLOW}GCP_SA_KEY${NC}"
echo "   - Name: GCP_SA_KEY"
echo "   - Value: Copy the entire contents of github-actions-key.json"
echo "   - Command: cat github-actions-key.json | pbcopy  (Mac)"
echo "   - Command: cat github-actions-key.json | xclip  (Linux)"
echo ""
echo "   ${YELLOW}CLOUD_SQL_CONNECTION_NAME${NC}"
echo "   - Name: CLOUD_SQL_CONNECTION_NAME"
echo "   - Value: $CLOUD_SQL_CONNECTION"
echo ""
echo "   ${YELLOW}VITE_GA_MEASUREMENT_ID${NC} (Optional)"
echo "   - Name: VITE_GA_MEASUREMENT_ID"
echo "   - Value: Your Google Analytics Measurement ID (if used)"
echo ""
echo "2. Verify workflow file exists:"
echo "   .github/workflows/deploy.yml"
echo ""
echo "3. Commit and push:"
echo "   git add .github/workflows/deploy.yml"
echo "   git commit -m 'feat: add GitHub Actions CI/CD'"
echo "   git push origin main"
echo ""
echo "4. Test deployment:"
echo "   - Make a change and push to main branch"
echo "   - Or merge a pull request into main"
echo "   - Check Actions tab in GitHub to see the workflow run"
echo ""
echo -e "${RED}⚠️  IMPORTANT:${NC}"
echo "   - Keep github-actions-key.json secure"
echo "   - Delete it after adding to GitHub Secrets"
echo "   - Never commit this file to git!"
echo ""
print_success "Setup script completed!"

