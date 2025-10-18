# Cloud Run Deployment Files - Reference

This document lists all the files created for Google Cloud Run deployment and their purposes.

## 📋 Deployment Files Overview

### Core Deployment Files

| File                            | Purpose                                | When to Use                   |
| ------------------------------- | -------------------------------------- | ----------------------------- |
| `backend/Dockerfile.cloudrun`   | Production-ready backend Docker image  | Builds backend for Cloud Run  |
| `frontend/Dockerfile.cloudrun`  | Production-ready frontend Docker image | Builds frontend for Cloud Run |
| `frontend/nginx.conf`           | Nginx configuration for frontend       | Serves React SPA efficiently  |
| `frontend/docker-entrypoint.sh` | Frontend container startup script      | Configures nginx at runtime   |
| `cloudbuild.yaml`               | Cloud Build CI/CD configuration        | Automated deployments         |
| `deploy-cloudrun.sh`            | Bash deployment script (Linux/Mac)     | Quick deployment automation   |
| `deploy-cloudrun.bat`           | Batch deployment script (Windows)      | Quick deployment automation   |
| `cloudrun.env.example`          | Environment variable template          | Configuration reference       |

### Documentation Files

| File                                  | Purpose                   | Audience                          |
| ------------------------------------- | ------------------------- | --------------------------------- |
| `docs/GOOGLE_CLOUD_RUN_DEPLOYMENT.md` | Complete deployment guide | Detailed, step-by-step deployment |
| `docs/QUICK_START_CLOUDRUN.md`        | Quick start guide         | Fast deployment in 15 mins        |
| `docs/CLOUDRUN_DEPLOYMENT_FILES.md`   | This file                 | Reference and overview            |

---

## 📄 File Details

### 1. `backend/Dockerfile.cloudrun`

**Purpose**: Production-optimized Docker image for the FastAPI backend.

**Key Features**:

- Based on Python 3.11 slim
- Includes Gunicorn with Uvicorn workers
- Optimized for Cloud Run (PORT environment variable)
- Includes Cloud Storage client for file handling
- Production-ready with proper process management

**Usage**:

```bash
docker build -f backend/Dockerfile.cloudrun -t backend:latest ./backend
```

**Differences from Development Dockerfile**:

- Uses Gunicorn instead of Uvicorn directly
- Adds google-cloud-storage dependency
- Optimized layer caching
- Smaller image size

---

### 2. `frontend/Dockerfile.cloudrun`

**Purpose**: Multi-stage Docker build for optimized React frontend.

**Key Features**:

- Multi-stage build (builder + production)
- Uses Node.js 18 for building
- Nginx Alpine for production (small footprint)
- Build-time API URL injection
- Custom entrypoint for dynamic port configuration

**Usage**:

```bash
docker build \
  --build-arg VITE_API_URL=https://your-backend-url.com \
  -f frontend/Dockerfile.cloudrun \
  -t frontend:latest \
  ./frontend
```

**Build Arguments**:

- `VITE_API_URL`: Backend API URL (required at build time)

---

### 3. `frontend/nginx.conf`

**Purpose**: Production-ready Nginx configuration for serving the React SPA.

**Features**:

- Optimized for Cloud Run (listens on port 8080)
- Gzip compression enabled
- Static asset caching (1 year for immutable assets)
- SPA fallback routing (for client-side routing)
- Health check endpoint at `/health`
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

**Notes**:

- Automatically updated by entrypoint script if PORT is set
- Optimized for performance and security

---

### 4. `frontend/docker-entrypoint.sh`

**Purpose**: Runtime configuration script for the frontend container.

**What it does**:

- Dynamically updates Nginx port based on Cloud Run's PORT env var
- Executed before Nginx starts
- Ensures compatibility with Cloud Run's dynamic port assignment

**Permissions**:

```bash
chmod +x frontend/docker-entrypoint.sh
```

---

### 5. `cloudbuild.yaml`

**Purpose**: Automated CI/CD pipeline configuration for Cloud Build.

**Workflow**:

1. Build backend Docker image
2. Push to Artifact Registry
3. Deploy backend to Cloud Run
4. Get backend URL
5. Build frontend with backend URL
6. Push frontend to Artifact Registry
7. Deploy frontend to Cloud Run
8. Update backend CORS with frontend URL

**Substitution Variables**:

- `_REGION`: Deployment region (default: us-central1)
- `_CLOUD_SQL_CONNECTION_NAME`: Cloud SQL instance connection name

**Usage**:

```bash
gcloud builds submit --config cloudbuild.yaml
```

**Setup Trigger** (for Git integration):

```bash
gcloud beta builds triggers create github \
  --repo-name=cv-analyzer \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

---

### 6. `deploy-cloudrun.sh` (Linux/Mac)

**Purpose**: Automated deployment script for Unix-based systems.

**What it does**:

1. ✅ Validates gcloud CLI and authentication
2. ✅ Enables required Google Cloud APIs
3. ✅ Checks for required secrets
4. ✅ Creates Artifact Registry repository
5. ✅ Verifies Cloud SQL instance (optionally creates it)
6. ✅ Builds and pushes backend image
7. ✅ Deploys backend to Cloud Run
8. ✅ Builds and pushes frontend image (with backend URL)
9. ✅ Deploys frontend to Cloud Run
10. ✅ Updates backend CORS configuration
11. ✅ Displays deployment summary

**Prerequisites**:

- gcloud CLI installed and authenticated
- Docker installed
- Secrets created (openai-api-key, db-password)

**Usage**:

```bash
chmod +x deploy-cloudrun.sh
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
./deploy-cloudrun.sh
```

**Environment Variables**:

- `GCP_PROJECT_ID`: Google Cloud project ID (default: cv-analyzer-tlstudio)
- `GCP_REGION`: Deployment region (default: us-central1)

---

### 7. `deploy-cloudrun.bat` (Windows)

**Purpose**: Automated deployment script for Windows systems.

**Functionality**: Same as the bash version, adapted for Windows batch scripting.

**Usage**:

```batch
set GCP_PROJECT_ID=your-project-id
set GCP_REGION=us-central1
deploy-cloudrun.bat
```

**Note**: Requires gcloud CLI to be in PATH.

---

### 8. `cloudrun.env.example`

**Purpose**: Template and reference for environment variables.

**Sections**:

- **Google Cloud Configuration**: Project ID, region
- **Cloud SQL Configuration**: Database connection details
- **API Keys**: Secret Manager references
- **Cloud Storage**: Bucket configuration
- **Docker Registry**: Artifact Registry settings
- **Resource Limits**: Memory, CPU, scaling settings

**Usage**:

1. Copy to `cloudrun.env`
2. Update values for your deployment
3. Use as reference when configuring Cloud Run services

**Security Note**: Never commit this file with real values to Git.

---

### 9. `docs/GOOGLE_CLOUD_RUN_DEPLOYMENT.md`

**Purpose**: Comprehensive, step-by-step deployment guide.

**Contents**:

- Prerequisites and setup
- Cloud SQL configuration
- Secret Manager setup
- Backend deployment
- Frontend deployment
- Cloud Storage setup
- Database migrations
- Monitoring and testing
- Cost optimization
- Troubleshooting
- Production checklist
- CI/CD pipeline setup

**Target Audience**: Anyone deploying for the first time or needing detailed instructions.

**Length**: ~500 lines with detailed explanations.

---

### 10. `docs/QUICK_START_CLOUDRUN.md`

**Purpose**: Fast-track deployment guide for experienced users.

**Contents**:

- 5-step quick deployment
- Essential commands only
- Common issues and quick fixes
- Cost estimates
- Monitoring basics
- Cleanup instructions

**Target Audience**: Developers familiar with Google Cloud who want to deploy quickly.

**Length**: ~300 lines with streamlined instructions.

---

## 🔄 Deployment Workflow

### Option 1: Automated Script (Recommended)

```bash
# Linux/Mac
./deploy-cloudrun.sh

# Windows
deploy-cloudrun.bat
```

### Option 2: Cloud Build (CI/CD)

```bash
# One-time setup
gcloud builds submit --config cloudbuild.yaml

# Setup Git trigger for auto-deployment
gcloud beta builds triggers create github \
  --repo-name=cv-analyzer \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

### Option 3: Manual Deployment

Follow the step-by-step instructions in:

- `docs/GOOGLE_CLOUD_RUN_DEPLOYMENT.md` (detailed)
- `docs/QUICK_START_CLOUDRUN.md` (concise)

---

## 🔧 Customization Guide

### Change Deployment Region

**In deployment scripts**:

```bash
# deploy-cloudrun.sh
export GCP_REGION="europe-west1"
./deploy-cloudrun.sh
```

**In cloudbuild.yaml**:

```yaml
substitutions:
  _REGION: "europe-west1"
```

### Adjust Resource Limits

**Memory and CPU**:

```bash
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2
```

**Scaling**:

```bash
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 20
```

### Add Custom Domain

```bash
# Map domain to service
gcloud run domain-mappings create \
  --service cv-analyzer-frontend \
  --domain your-domain.com \
  --region us-central1
```

### Enable Cloud CDN

```bash
# Create load balancer with CDN
# Follow: https://cloud.google.com/run/docs/configure-cdn
```

---

## 📊 File Dependencies

```
deploy-cloudrun.sh/bat
├── backend/Dockerfile.cloudrun
│   └── backend/requirements.txt
├── frontend/Dockerfile.cloudrun
│   ├── frontend/nginx.conf
│   ├── frontend/docker-entrypoint.sh
│   └── frontend/package.json
└── cloudrun.env.example (reference)

cloudbuild.yaml
├── backend/Dockerfile.cloudrun
├── frontend/Dockerfile.cloudrun
└── Google Cloud services
```

---

## 🚀 Quick Reference Commands

### Deploy

```bash
./deploy-cloudrun.sh  # Automated deployment
```

### Update Backend

```bash
cd backend
docker build -f Dockerfile.cloudrun -t us-central1-docker.pkg.dev/PROJECT_ID/cv-analyzer-repo/backend:latest .
docker push us-central1-docker.pkg.dev/PROJECT_ID/cv-analyzer-repo/backend:latest
gcloud run deploy cv-analyzer-backend --image us-central1-docker.pkg.dev/PROJECT_ID/cv-analyzer-repo/backend:latest --region us-central1
```

### View Logs

```bash
gcloud run services logs read cv-analyzer-backend --region us-central1 --limit 50
```

### Update Environment Variable

```bash
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --set-env-vars="KEY=VALUE"
```

### Scale Service

```bash
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --min-instances 1
```

### Delete Deployment

```bash
gcloud run services delete cv-analyzer-backend --region us-central1
gcloud run services delete cv-analyzer-frontend --region us-central1
```

---

## 📝 Checklist for New Deployments

- [ ] gcloud CLI installed and authenticated
- [ ] Docker installed and running
- [ ] Google Cloud project created with billing enabled
- [ ] Required APIs enabled
- [ ] Secrets created (openai-api-key, db-password)
- [ ] Cloud SQL instance created with pgvector extension
- [ ] Artifact Registry repository created
- [ ] Environment variables configured
- [ ] Review `cloudrun.env.example` for configuration
- [ ] Run deployment script or Cloud Build
- [ ] Test frontend and backend URLs
- [ ] Verify database connection
- [ ] Check logs for errors
- [ ] Setup monitoring and alerts
- [ ] Configure backup strategy
- [ ] Document custom configurations

---

## 🆘 Troubleshooting

### Script Fails

- Check gcloud authentication: `gcloud auth list`
- Verify Docker is running: `docker ps`
- Ensure secrets exist: `gcloud secrets list`

### Build Fails

- Check Dockerfile syntax
- Verify base image availability
- Review Cloud Build logs

### Deployment Fails

- Check service quotas in Cloud Console
- Verify IAM permissions
- Review deployment logs: `gcloud run services describe SERVICE_NAME`

### Connection Issues

- Verify Cloud SQL connection name
- Check network/VPC settings
- Ensure secrets are accessible

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

---

**Last Updated**: October 2025
**Maintained By**: CV Analyzer Team
