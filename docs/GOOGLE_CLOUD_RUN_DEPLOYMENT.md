# Google Cloud Run Deployment Guide

## Overview

This guide walks you through deploying the CV Analyzer application to Google Cloud Run. The application consists of:

- **Backend**: Python FastAPI service
- **Frontend**: React (Vite) application
- **Database**: PostgreSQL with pgvector extension (Cloud SQL)

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK (gcloud CLI)** installed
   ```bash
   # Install from: https://cloud.google.com/sdk/docs/install
   # Or use Cloud Shell (already has gcloud)
   ```
3. **Docker** installed locally
4. **Project setup**:

   ```bash
   # Login to Google Cloud
   gcloud auth login

   # Create a new project or use existing one
   gcloud projects create cv-analyzer-tlstudio --name="CV Analyzer"

   # Set the project
   gcloud config set project cv-analyzer-tlstudio

   # Enable required APIs
   gcloud services enable \
     run.googleapis.com \
     sqladmin.googleapis.com \
     artifactregistry.googleapis.com \
     cloudbuild.googleapis.com \
     secretmanager.googleapis.com
   ```

---

## Step 1: Setup Cloud SQL (PostgreSQL with pgvector)

### 1.1 Create Cloud SQL Instance

```bash
# Create PostgreSQL instance (adjust region as needed)
gcloud sql instances create cv-analyzer-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_STRONG_PASSWORD_HERE

# Note: Use db-f1-micro for testing, upgrade to db-n1-standard-1 or higher for production
```

### 1.2 Create Database

```bash
# Create the database
gcloud sql databases create cv_analyzer \
  --instance=cv-analyzer-db

# Get the instance connection name (save this for later)
gcloud sql instances describe cv-analyzer-db --format="value(connectionName)"
# Output will be like: cv-analyzer-tlstudio:us-central1:cv-analyzer-db
```

### 1.3 Install pgvector Extension

```bash
# Connect to the database using Cloud SQL Proxy or directly
gcloud sql connect cv-analyzer-db --user=postgres --database=cv_analyzer

# Then run in the SQL prompt:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

Or upload and run the migration files:

```bash
# Upload migration files
gcloud sql import sql cv-analyzer-db gs://your-bucket/migrations/000_init_pgvector.sql \
  --database=cv_analyzer

gcloud sql import sql cv-analyzer-db gs://your-bucket/migrations/001_add_embedding_support.sql \
  --database=cv_analyzer
```

---

## Step 2: Setup Secret Manager (for API Keys)

```bash
# Create secrets for sensitive data
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_OPENAI_EMBED_API_KEY" | gcloud secrets create openai-embed-api-key --data-file=-
echo -n "YOUR_DATABASE_PASSWORD" | gcloud secrets create db-password --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe cv-analyzer-tlstudio --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding openai-embed-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 3: Prepare Backend for Cloud Run

### 3.1 Update Backend Dockerfile (Production Ready)

Create `backend/Dockerfile.cloudrun`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/outputs/resumes /app/outputs/cvs

# Cloud Run sets PORT environment variable
ENV PORT=8080

# Use Gunicorn for production
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app
```

### 3.2 Update requirements.txt

Add Gunicorn to `backend/requirements.txt`:

```txt
gunicorn==21.2.0
```

### 3.3 Update Backend Config for Cloud Run

Update `backend/config.py` to support Cloud SQL connection:

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "cv_analyzer")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    # Cloud SQL connection (Cloud Run specific)
    CLOUD_SQL_CONNECTION_NAME: str = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBED_API_KEY: str = os.getenv("OPENAI_EMBED_API_KEY", "")

    # CORS settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "*")

    @property
    def DATABASE_URL(self) -> str:
        if self.CLOUD_SQL_CONNECTION_NAME:
            # Use Unix socket for Cloud SQL
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?host=/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
        else:
            # Use standard connection
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Step 4: Build and Push Backend to Artifact Registry

### 4.1 Create Artifact Registry Repository

```bash
# Create repository
gcloud artifacts repositories create cv-analyzer-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="CV Analyzer Docker images"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 4.2 Build and Push Backend Image

```bash
# Navigate to backend directory
cd backend

# Build the image using Cloud Build (recommended) or locally
gcloud builds submit --tag us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/backend:latest

# Or build locally and push
docker build -f Dockerfile.cloudrun -t us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/backend:latest .
docker push us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/backend:latest

cd ..
```

---

## Step 5: Deploy Backend to Cloud Run

```bash
# Get your Cloud SQL connection name
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe cv-analyzer-db --format="value(connectionName)")

# Deploy backend service
gcloud run deploy cv-analyzer-backend \
  --image us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances $INSTANCE_CONNECTION_NAME \
  --set-env-vars="DB_USER=postgres,DB_NAME=cv_analyzer,CLOUD_SQL_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME,FRONTEND_URL=*" \
  --set-secrets="DB_PASSWORD=db-password:latest,OPENAI_API_KEY=openai-api-key:latest,OPENAI_EMBED_API_KEY=openai-embed-api-key:latest" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

# Get backend URL
BACKEND_URL=$(gcloud run services describe cv-analyzer-backend --region us-central1 --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
```

---

## Step 6: Prepare Frontend for Cloud Run

### 6.1 Update Frontend API Configuration

Update `frontend/src/services/api.js`:

```javascript
// Use environment variable for API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Rest of your API code...
```

### 6.2 Create Production Dockerfile for Frontend

Create `frontend/Dockerfile.cloudrun`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run expects the app to listen on PORT
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
```

### 6.3 Create Nginx Configuration

Create `frontend/nginx.conf`:

```nginx
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    gzip_comp_level 9;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check endpoint
    location /health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 6.4 Create Docker Entrypoint

Create `frontend/docker-entrypoint.sh`:

```bash
#!/bin/sh
set -e

# Update nginx to listen on Cloud Run PORT
if [ -n "$PORT" ]; then
  sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/conf.d/default.conf
fi

exec "$@"
```

---

## Step 7: Build and Deploy Frontend

```bash
# Navigate to frontend directory
cd frontend

# Build with backend URL
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/frontend:latest \
  --build-arg VITE_API_URL=$BACKEND_URL

# Or build locally
docker build \
  --build-arg VITE_API_URL=$BACKEND_URL \
  -f Dockerfile.cloudrun \
  -t us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/frontend:latest .
docker push us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/frontend:latest

# Deploy frontend
gcloud run deploy cv-analyzer-frontend \
  --image us-central1-docker.pkg.dev/cv-analyzer-tlstudio/cv-analyzer-repo/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe cv-analyzer-frontend --region us-central1 --format="value(status.url)")
echo "Frontend URL: $FRONTEND_URL"

cd ..
```

### 7.1 Update Backend CORS Settings

```bash
# Update backend with correct frontend URL
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --set-env-vars="FRONTEND_URL=$FRONTEND_URL"
```

---

## Step 8: Setup Cloud Storage (for CV/Resume Files)

Cloud Run containers are stateless, so we need Cloud Storage for file uploads.

### 8.1 Create Storage Bucket

```bash
# Create bucket for file storage
gsutil mb -l us-central1 gs://cv-analyzer-files

# Set CORS policy for uploads
cat > cors.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "POST"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://cv-analyzer-files
```

### 8.2 Update Backend to Use Cloud Storage

You'll need to modify `backend/services/file_processor.py` and `backend/services/pdf_generator.py` to use Cloud Storage instead of local filesystem:

```python
# Add to requirements.txt
google-cloud-storage==2.10.0

# Example usage in file_processor.py
from google.cloud import storage

def save_to_cloud_storage(file_content, filename, bucket_name="cv-analyzer-files"):
    """Save file to Google Cloud Storage"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"uploads/{filename}")
    blob.upload_from_string(file_content)
    return blob.public_url
```

---

## Step 9: Run Database Migrations

```bash
# Option 1: Connect via Cloud SQL Proxy
cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:5432 &

# Then run migrations from your local machine
psql "postgresql://postgres:YOUR_PASSWORD@localhost:5432/cv_analyzer" -f backend/migrations/000_init_pgvector.sql
psql "postgresql://postgres:YOUR_PASSWORD@localhost:5432/cv_analyzer" -f backend/migrations/001_add_embedding_support.sql

# Option 2: Use Cloud Run Job for migrations
# (Create a separate migration job that runs before deployment)
```

---

## Step 10: Testing and Monitoring

### 10.1 Test Your Deployment

```bash
# Test backend health
curl $BACKEND_URL/health

# Test frontend
curl $FRONTEND_URL

# View logs
gcloud run services logs read cv-analyzer-backend --region us-central1 --limit 50
gcloud run services logs read cv-analyzer-frontend --region us-central1 --limit 50
```

### 10.2 Setup Monitoring

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# View metrics in Cloud Console
echo "Backend metrics: https://console.cloud.google.com/run/detail/us-central1/cv-analyzer-backend/metrics"
echo "Frontend metrics: https://console.cloud.google.com/run/detail/us-central1/cv-analyzer-frontend/metrics"
```

---

## Cost Optimization

### For Development/Testing:

- Use `--min-instances 0` (scale to zero when not in use)
- Use `db-f1-micro` for Cloud SQL
- Set `--max-instances 5`

### For Production:

- Use `--min-instances 1` to avoid cold starts
- Upgrade to `db-n1-standard-1` or higher
- Set appropriate `--max-instances` based on traffic
- Enable Cloud CDN for frontend

### Estimated Monthly Costs (Light Usage):

- Cloud Run Backend: $5-20
- Cloud Run Frontend: $2-10
- Cloud SQL (db-f1-micro): $7-15
- Cloud Storage: $1-5
- **Total: ~$15-50/month**

---

## CI/CD Pipeline (Optional)

### Using Cloud Build

Create `cloudbuild.yaml` in project root:

```yaml
steps:
  # Build backend
  - name: "gcr.io/cloud-builders/docker"
    args:
      [
        "build",
        "-f",
        "backend/Dockerfile.cloudrun",
        "-t",
        "us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/backend:$SHORT_SHA",
        "./backend",
      ]

  # Push backend
  - name: "gcr.io/cloud-builders/docker"
    args:
      [
        "push",
        "us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/backend:$SHORT_SHA",
      ]

  # Deploy backend
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    entrypoint: gcloud
    args:
      - "run"
      - "deploy"
      - "cv-analyzer-backend"
      - "--image=us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/backend:$SHORT_SHA"
      - "--region=us-central1"
      - "--platform=managed"

  # Build frontend
  - name: "gcr.io/cloud-builders/docker"
    args:
      [
        "build",
        "-f",
        "frontend/Dockerfile.cloudrun",
        "--build-arg",
        "VITE_API_URL=$_BACKEND_URL",
        "-t",
        "us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/frontend:$SHORT_SHA",
        "./frontend",
      ]

  # Deploy frontend
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    entrypoint: gcloud
    args:
      - "run"
      - "deploy"
      - "cv-analyzer-frontend"
      - "--image=us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/frontend:$SHORT_SHA"
      - "--region=us-central1"
      - "--platform=managed"

substitutions:
  _BACKEND_URL: "https://cv-analyzer-backend-xxx-uc.a.run.app"

images:
  - "us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/backend:$SHORT_SHA"
  - "us-central1-docker.pkg.dev/$PROJECT_ID/cv-analyzer-repo/frontend:$SHORT_SHA"
```

### Setup Cloud Build Trigger

```bash
# Connect your GitHub repository
gcloud beta builds triggers create github \
  --repo-name=cv-analyzer \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

---

## Troubleshooting

### Common Issues:

1. **Database Connection Failed**

   - Verify Cloud SQL connection name is correct
   - Ensure Cloud Run has Cloud SQL IAM permissions
   - Check database password in Secret Manager

2. **CORS Errors**

   - Update backend FRONTEND_URL environment variable
   - Check backend CORS configuration in `main.py`

3. **File Upload Issues**

   - Migrate to Cloud Storage (local filesystem is ephemeral)
   - Update file paths in backend services

4. **Cold Start Performance**

   - Set `--min-instances 1` for production
   - Optimize Docker image size
   - Use keep-alive requests from frontend

5. **Memory Issues**
   - Increase memory: `--memory 2Gi`
   - Monitor usage in Cloud Console
   - Optimize file processing

---

## Production Checklist

- [ ] Database backups enabled on Cloud SQL
- [ ] Secret Manager for all sensitive data
- [ ] HTTPS enabled (automatic with Cloud Run)
- [ ] Custom domain configured (optional)
- [ ] Cloud CDN enabled for frontend
- [ ] Logging and monitoring configured
- [ ] Error tracking setup (e.g., Cloud Error Reporting)
- [ ] Rate limiting implemented
- [ ] File size limits enforced
- [ ] Cloud Storage configured for uploads
- [ ] CI/CD pipeline setup
- [ ] Budget alerts configured

---

## Useful Commands

```bash
# View logs
gcloud run services logs read cv-analyzer-backend --region us-central1

# Update service
gcloud run services update cv-analyzer-backend --region us-central1 --set-env-vars="KEY=VALUE"

# Delete service
gcloud run services delete cv-analyzer-backend --region us-central1

# List services
gcloud run services list

# Database access
gcloud sql connect cv-analyzer-db --user=postgres

# View costs
gcloud beta billing accounts list
```

---

## Support and Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

---

## Next Steps

After deployment:

1. Test all features (upload, analyze, recommend, chat, generate resume)
2. Setup monitoring and alerts
3. Configure custom domain (optional)
4. Implement automated backups
5. Setup CI/CD for automatic deployments
6. Consider Cloud CDN for global performance
