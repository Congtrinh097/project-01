# Quick Start: Deploy to Google Cloud Run

This guide gets you up and running on Google Cloud Run in ~15 minutes.

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed ([Install here](https://cloud.google.com/sdk/docs/install))
- Docker installed locally
- OpenAI API key

## 🚀 Quick Deploy (5 Steps)

### Step 1: Setup Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create and set project (or use existing)
export PROJECT_ID="cv-analyzer-tlstudio"
gcloud projects create $PROJECT_ID --name="CV Analyzer"
gcloud config set project $PROJECT_ID

# Enable billing (required - do this in Cloud Console)
# https://console.cloud.google.com/billing

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Create Secrets

```bash
# Store your API keys in Secret Manager
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_OPENAI_EMBED_API_KEY" | gcloud secrets create openai-embed-api-key --data-file=-
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
for secret in openai-api-key openai-embed-api-key db-password; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Step 3: Setup Database

**Important**: Cloud SQL is **NOT free**. The `db-f1-micro` tier costs ~$7-15/month.

**FREE Alternatives**:

- ✅ **Supabase** (recommended, free tier, pgvector included) - [See FREE_DATABASE_OPTIONS.md](FREE_DATABASE_OPTIONS.md)
- ✅ **Neon** (serverless PostgreSQL, free tier)
- ✅ **Compute Engine f1-micro** (Always Free, manual setup)
- ✅ **Google Cloud $300 free trial** (90 days)

#### Option A: Cloud SQL (~$7-15/month)

```bash
# Get database password from secret
DB_PASSWORD=$(gcloud secrets versions access latest --secret="db-password")

# Create PostgreSQL instance (takes ~5 minutes)
gcloud sql instances create cv-analyzer-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password="$DB_PASSWORD"

# Create database
gcloud sql databases create cv_analyzer --instance=cv-analyzer-db

# Install pgvector extension
gcloud sql connect cv-analyzer-db --user=postgres
```

In the SQL prompt:

```sql
\c cv_analyzer
CREATE EXTENSION IF NOT EXISTS vector;

-- Create CVs table
CREATE TABLE IF NOT EXISTS cvs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    extracted_text TEXT,
    summary_pros TEXT,
    summary_cons TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding vector(1536)
);

-- Create index for vector similarity search
CREATE INDEX ON cvs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

\q
```

#### Option B: Supabase (FREE - Recommended)

```bash
# 1. Sign up at https://supabase.com (no credit card required)
# 2. Create a new project (choose region close to us-central1)
# 3. Wait ~2 minutes for provisioning

# 4. In Supabase SQL Editor, run:
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE cvs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    extracted_text TEXT,
    summary_pros TEXT,
    summary_cons TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding vector(1536)
);

CREATE INDEX ON cvs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

# 5. Get connection string from Settings → Database → Connection string (URI)
# Format: postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres

# 6. Store as secret
echo -n "YOUR_SUPABASE_CONNECTION_STRING" | gcloud secrets create database-url --data-file=-

# Grant access to secret
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**For Supabase**: When deploying, use `--set-secrets="DATABASE_URL=database-url:latest"` instead of Cloud SQL configuration.

### Step 4: Run Automated Deployment

#### On Linux/Mac:

```bash
# Make script executable
chmod +x deploy-cloudrun.sh

# Run deployment
./deploy-cloudrun.sh
```

#### On Windows:

```powershell
# Run deployment script
deploy-cloudrun.bat
```

#### Or Manual Deployment:

```bash
# Set variables
export PROJECT_ID="cv-analyzer-tlstudio"
export REGION="us-central1"
export CLOUD_SQL_CONNECTION=$(gcloud sql instances describe cv-analyzer-db --format="value(connectionName)")

# Create Artifact Registry
gcloud artifacts repositories create cv-analyzer-repo \
  --repository-format=docker \
  --location=$REGION

# Authenticate Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and deploy backend
cd backend
docker build -f Dockerfile.cloudrun -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/backend:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/backend:latest

gcloud run deploy cv-analyzer-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/backend:latest \
  --region $REGION \
  --allow-unauthenticated \
  --add-cloudsql-instances $CLOUD_SQL_CONNECTION \
  --set-env-vars="DB_USER=postgres,DB_NAME=cv_analyzer,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION" \
  --set-secrets="DB_PASSWORD=db-password:latest,OPENAI_API_KEY=openai-api-key:latest,OPENAI_EMBED_API_KEY=openai-embed-api-key:latest" \
  --memory 1Gi

# Get backend URL
BACKEND_URL=$(gcloud run services describe cv-analyzer-backend --region $REGION --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"

# Build and deploy frontend
cd ../frontend
docker build \
  --build-arg VITE_API_URL=$BACKEND_URL \
  -f Dockerfile.cloudrun \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/frontend:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/frontend:latest

gcloud run deploy cv-analyzer-frontend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/frontend:latest \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe cv-analyzer-frontend --region $REGION --format="value(status.url)")
echo "Frontend URL: $FRONTEND_URL"

# Update backend CORS
gcloud run services update cv-analyzer-backend \
  --region $REGION \
  --set-env-vars="FRONTEND_URL=$FRONTEND_URL"
```

### Step 5: Test Your Deployment

```bash
# Get your URLs
FRONTEND_URL=$(gcloud run services describe cv-analyzer-frontend --region us-central1 --format="value(status.url)")
BACKEND_URL=$(gcloud run services describe cv-analyzer-backend --region us-central1 --format="value(status.url)")

echo "🎉 Deployment Complete!"
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"

# Test backend health
curl $BACKEND_URL/health

# Open frontend
open $FRONTEND_URL  # Mac
start $FRONTEND_URL # Windows
```

## 📊 Monitor Your Application

### View Logs

```bash
# Backend logs
gcloud run services logs read cv-analyzer-backend --region us-central1 --limit 50

# Frontend logs
gcloud run services logs read cv-analyzer-frontend --region us-central1 --limit 50

# Follow logs in real-time
gcloud run services logs tail cv-analyzer-backend --region us-central1
```

### View Metrics

- Backend: https://console.cloud.google.com/run/detail/us-central1/cv-analyzer-backend
- Frontend: https://console.cloud.google.com/run/detail/us-central1/cv-analyzer-frontend
- Cloud SQL: https://console.cloud.google.com/sql/instances

## 💰 Estimated Costs

### 🆓 COMPLETELY FREE Option (Recommended for Learning/Development):

**Using Supabase Free Tier**:

- Cloud Run Backend: $0-3/month (generous free tier)
- Cloud Run Frontend: $0-2/month (generous free tier)
- **Supabase Database: $0/month** (free tier, 500 MB, pgvector included ✅)
- Artifact Registry: $0-1/month
- **Total: $0-6/month** 🎉

**See [FREE_DATABASE_OPTIONS.md](FREE_DATABASE_OPTIONS.md) for more free alternatives!**

---

**Development/Testing** (with Cloud SQL):

- Cloud Run Backend: $5-10/month
- Cloud Run Frontend: $2-5/month
- Cloud SQL (db-f1-micro): $7-10/month
- Artifact Registry: $0.10/GB/month
- **Total: ~$15-30/month**

**Production** (moderate usage):

- Cloud Run Backend: $20-50/month
- Cloud Run Frontend: $10-20/month
- Cloud SQL (db-n1-standard-1): $50-100/month
- Cloud Storage: $5-10/month
- **Total: ~$85-180/month**

### Cost Optimization Tips:

1. **Use Supabase free tier** for learning/development (saves ~$7-15/month) 🆓
2. Set `--min-instances 0` for dev (scale to zero)
3. Use Google Cloud $300 free credit (new accounts, 90 days)
4. Enable Cloud CDN for frontend
5. Set appropriate memory/CPU limits
6. Use Cloud SQL backups wisely (7-day retention)
7. Consider Compute Engine f1-micro for permanent free database

## 🔧 Common Issues

### Issue: Database connection failed

**Solution:**

```bash
# Verify Cloud SQL connection name
gcloud sql instances describe cv-analyzer-db --format="value(connectionName)"

# Update backend with correct connection
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=PROJECT:REGION:INSTANCE"
```

### Issue: CORS errors in frontend

**Solution:**

```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe cv-analyzer-frontend --region us-central1 --format="value(status.url)")

# Update backend CORS
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --set-env-vars="FRONTEND_URL=$FRONTEND_URL"
```

### Issue: Cold starts are slow

**Solution:**

```bash
# Set minimum instances to 1 for production
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --min-instances 1
```

### Issue: Out of memory errors

**Solution:**

```bash
# Increase memory allocation
gcloud run services update cv-analyzer-backend \
  --region us-central1 \
  --memory 2Gi
```

## 🔄 Update Your Application

```bash
# Rebuild and redeploy backend
cd backend
docker build -f Dockerfile.cloudrun -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/backend:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/backend:latest
gcloud run deploy cv-analyzer-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/cv-analyzer-repo/backend:latest \
  --region us-central1

# Or use Cloud Build for automated deployment
gcloud builds submit --config cloudbuild.yaml
```

## 🧹 Cleanup (Delete Everything)

```bash
# Delete Cloud Run services
gcloud run services delete cv-analyzer-backend --region us-central1 --quiet
gcloud run services delete cv-analyzer-frontend --region us-central1 --quiet

# Delete Cloud SQL instance
gcloud sql instances delete cv-analyzer-db --quiet

# Delete Artifact Registry images
gcloud artifacts repositories delete cv-analyzer-repo --location us-central1 --quiet

# Delete secrets
gcloud secrets delete openai-api-key --quiet
gcloud secrets delete openai-embed-api-key --quiet
gcloud secrets delete db-password --quiet

# (Optional) Delete project
gcloud projects delete $PROJECT_ID --quiet
```

## 🎯 Next Steps

1. **Setup Custom Domain**: Map a custom domain to your Cloud Run service
2. **Enable Cloud CDN**: Speed up frontend delivery globally
3. **Setup CI/CD**: Automate deployments with Cloud Build triggers
4. **Add Monitoring**: Setup alerts for errors and performance
5. **Backup Strategy**: Configure Cloud SQL automated backups
6. **Security**: Implement authentication and rate limiting

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/postgres/best-practices)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)
- [Cost Optimization](https://cloud.google.com/run/docs/tips/general)

## 🆘 Need Help?

- Check logs: `gcloud run services logs read cv-analyzer-backend --region us-central1`
- View errors: https://console.cloud.google.com/errors
- Monitor costs: https://console.cloud.google.com/billing
- Stack Overflow: Tag your question with `google-cloud-run`
