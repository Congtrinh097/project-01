# Free Database Options for CV Analyzer

This guide explores free and low-cost database alternatives to Cloud SQL for the CV Analyzer application.

## 🆓 Completely Free Options

### Option 1: PostgreSQL on Compute Engine f1-micro (Always Free)

**Pros**:

- ✅ Permanently free (Google Cloud Always Free tier)
- ✅ Full control over PostgreSQL
- ✅ Can install pgvector extension
- ✅ 30 GB storage included

**Cons**:

- ❌ Manual setup and maintenance
- ❌ No automatic backups
- ❌ Limited resources (0.6 GB RAM, shared CPU)
- ❌ You manage OS updates and security

**Setup Guide**:

```bash
# Create f1-micro instance (Always Free in us-central1, us-west1, us-east1)
gcloud compute instances create cv-analyzer-db \
  --zone=us-central1-a \
  --machine-type=f1-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --tags=postgres

# Allow PostgreSQL port
gcloud compute firewall-rules create allow-postgres \
  --allow=tcp:5432 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=postgres

# SSH into the instance
gcloud compute ssh cv-analyzer-db --zone=us-central1-a

# Install PostgreSQL and pgvector
sudo apt update
sudo apt install -y postgresql postgresql-contrib build-essential git postgresql-server-dev-14

# Install pgvector
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE cv_analyzer;
CREATE USER cvuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cv_analyzer TO cvuser;
\c cv_analyzer
CREATE EXTENSION vector;
\q

# Allow external connections (edit pg_hba.conf and postgresql.conf)
sudo nano /etc/postgresql/14/main/postgresql.conf
# Change: listen_addresses = '*'

sudo nano /etc/postgresql/14/main/pg_hba.conf
# Add: host all all 0.0.0.0/0 md5

sudo systemctl restart postgresql
```

**Connection from Cloud Run**:

```bash
# Use external IP or set up Cloud SQL Proxy equivalent
export DB_HOST=<VM_EXTERNAL_IP>
export DB_PORT=5432
export DB_USER=cvuser
export DB_PASSWORD=your_password
export DB_NAME=cv_analyzer
```

**Estimated Cost**: **$0/month** (within Always Free limits)

---

### Option 2: Supabase (Free Tier)

**Pros**:

- ✅ Fully managed PostgreSQL
- ✅ Built-in pgvector support
- ✅ 500 MB database (free tier)
- ✅ API and real-time features included
- ✅ No credit card required

**Cons**:

- ❌ Limited to 500 MB storage
- ❌ Projects pause after 1 week of inactivity (free tier)
- ❌ 2 projects limit on free tier

**Setup**:

1. Sign up at https://supabase.com
2. Create a new project
3. Get connection string from Settings → Database
4. Enable pgvector (pre-installed)

**Connection String**:

```bash
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

**For Cloud Run**:

```bash
gcloud run services update cv-analyzer-backend \
  --set-env-vars="DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
```

**Estimated Cost**: **$0/month** (free tier)

---

### Option 3: Neon (Serverless PostgreSQL - Free Tier)

**Pros**:

- ✅ Serverless PostgreSQL with branching
- ✅ 3 GB storage (free tier)
- ✅ Automatic suspend when idle
- ✅ pgvector support
- ✅ No credit card required

**Cons**:

- ❌ Compute time limits on free tier
- ❌ May have cold starts

**Setup**:

1. Sign up at https://neon.tech
2. Create a new project
3. Get connection string
4. Enable pgvector extension

**Connection String**:

```bash
postgresql://[user]:[password]@[project].neon.tech/[dbname]?sslmode=require
```

**Estimated Cost**: **$0/month** (free tier)

---

### Option 4: ElephantSQL (Free Tier)

**Pros**:

- ✅ Tiny Turtle plan is free
- ✅ 20 MB storage + 5 concurrent connections
- ✅ Managed PostgreSQL
- ✅ No credit card required

**Cons**:

- ❌ Very limited storage (20 MB)
- ❌ Not suitable for production
- ❌ No pgvector support on free tier

**Use Case**: Only for testing, not recommended for CV Analyzer due to storage limits.

**Estimated Cost**: **$0/month** (Tiny Turtle plan)

---

### Option 5: Aiven (Free Trial)

**Pros**:

- ✅ 30-day free trial
- ✅ Fully managed
- ✅ pgvector support
- ✅ Multi-cloud support

**Cons**:

- ❌ Requires credit card
- ❌ Only 30 days free
- ❌ Minimum cost ~$10/month after trial

**Estimated Cost**: **$0** for 30 days, then ~$10-30/month

---

## 💰 Low-Cost Options (Not Free, But Cheap)

### Cloud SQL db-f1-micro (Google Cloud)

**Cost**: **~$7-15/month**

**Pros**:

- ✅ Fully managed
- ✅ Automatic backups
- ✅ Integrated with Cloud Run
- ✅ High availability options
- ✅ pgvector support

**Cons**:

- ❌ Not free
- ❌ Limited resources

**Best For**: Production deployments with budget

---

### DigitalOcean Managed PostgreSQL

**Cost**: **~$15/month** (smallest tier)

**Pros**:

- ✅ Simple pricing
- ✅ Managed backups
- ✅ Daily backups included
- ✅ Easy to set up

**Cons**:

- ❌ Not free
- ❌ May need VPN for secure Cloud Run connection

---

## 🎯 Recommendations by Use Case

### For **Learning/Development** (Recommended):

**Option**: **Supabase Free Tier** or **Neon Free Tier**

- Easy setup
- No maintenance
- Completely free
- pgvector support
- Good for testing

### For **Testing/Prototyping**:

**Option**: **Google Cloud Free Trial ($300 credits)**

- Use db-f1-micro
- Test full Cloud Run + Cloud SQL integration
- 90 days of free usage

### For **Personal Projects** (Long-term):

**Option**: **Compute Engine f1-micro + PostgreSQL**

- Permanently free
- Full control
- Requires more setup but costs $0

### For **Production** (Small Scale):

**Option**: **Cloud SQL db-f1-micro**

- Only ~$7-15/month
- Fully managed
- Automatic backups
- Scalable when needed

### For **Production** (Budget-Conscious):

**Option**: **Neon** or **Supabase Paid Tier**

- Neon: Pay-as-you-go (~$5-20/month)
- Supabase Pro: $25/month with more resources

---

## 🔧 Updated Deployment for Free Options

### Using Supabase (Recommended for Free Tier)

```bash
# 1. Sign up at https://supabase.com
# 2. Create a new project
# 3. Get your connection string

# 4. Enable pgvector (already enabled by default)
# Run in Supabase SQL Editor:
CREATE EXTENSION IF NOT EXISTS vector;

# 5. Deploy backend with Supabase connection
gcloud run deploy cv-analyzer-backend \
  --image your-image \
  --set-env-vars="DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" \
  --region us-central1

# No Cloud SQL needed!
```

### Using Neon

```bash
# 1. Sign up at https://neon.tech
# 2. Create a project
# 3. Get connection string

# 4. Enable pgvector
# Run in Neon SQL Editor:
CREATE EXTENSION IF NOT EXISTS vector;

# 5. Deploy with Neon
gcloud run deploy cv-analyzer-backend \
  --image your-image \
  --set-env-vars="DATABASE_URL=postgresql://[user]:[password]@[project].neon.tech/[dbname]?sslmode=require" \
  --region us-central1
```

### Using Compute Engine f1-micro

```bash
# 1. Set up f1-micro with PostgreSQL (see setup above)
# 2. Get the external IP

# 3. Deploy with f1-micro connection
gcloud run deploy cv-analyzer-backend \
  --image your-image \
  --set-env-vars="DB_HOST=EXTERNAL_IP,DB_PORT=5432,DB_USER=cvuser,DB_NAME=cv_analyzer" \
  --set-secrets="DB_PASSWORD=db-password:latest" \
  --region us-central1

# Note: Remove --add-cloudsql-instances flag
```

---

## 📊 Cost Comparison (Monthly)

| Option                 | Cost  | Storage   | Maintenance | pgvector | Backups |
| ---------------------- | ----- | --------- | ----------- | -------- | ------- |
| **Supabase Free**      | $0    | 500 MB    | None        | ✅       | ✅      |
| **Neon Free**          | $0    | 3 GB      | None        | ✅       | ✅      |
| **GCE f1-micro**       | $0    | 30 GB     | Manual      | ✅       | Manual  |
| **GC Free Trial**      | $0\*  | Unlimited | None        | ✅       | ✅      |
| **Cloud SQL f1-micro** | $7-15 | 10 GB+    | None        | ✅       | ✅      |
| **DigitalOcean**       | $15   | 10 GB     | None        | ✅       | ✅      |
| **Supabase Pro**       | $25   | 8 GB      | None        | ✅       | ✅      |

\*Uses $300 credit (90 days only)

---

## 🚀 Quick Start with Supabase (Free)

### 1. Create Supabase Project

```bash
# Go to https://supabase.com/dashboard
# Click "New Project"
# Choose region close to your Cloud Run region
# Wait for database to provision (~2 minutes)
```

### 2. Setup Database

```sql
-- Run in Supabase SQL Editor

-- Create CVs table
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

-- Create index for vector search
CREATE INDEX ON cvs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Grant permissions (optional, for additional users)
GRANT ALL ON cvs TO postgres;
```

### 3. Get Connection String

```bash
# In Supabase Dashboard:
# Settings → Database → Connection string (Direct connection)
# Copy the URI format
```

### 4. Update Backend Config

Update `backend/config.py`:

```python
@property
def DATABASE_URL(self) -> str:
    # For Supabase or other external PostgreSQL
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")

    # Fallback to Cloud SQL or local
    if self.CLOUD_SQL_CONNECTION_NAME:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?host=/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
    else:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
```

### 5. Deploy to Cloud Run

```bash
# Store Supabase connection string as secret
echo -n "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" | \
  gcloud secrets create database-url --data-file=-

# Deploy backend
gcloud run deploy cv-analyzer-backend \
  --image us-central1-docker.pkg.dev/PROJECT_ID/cv-analyzer-repo/backend:latest \
  --region us-central1 \
  --set-secrets="DATABASE_URL=database-url:latest,OPENAI_API_KEY=openai-api-key:latest" \
  --memory 1Gi \
  --allow-unauthenticated

# No --add-cloudsql-instances needed!
```

### 6. Test Connection

```bash
# Backend will use DATABASE_URL environment variable
# No changes needed to application code
```

---

## ✅ Best Free Solution: Supabase + Cloud Run

**Total Monthly Cost**: **$0** (for low to moderate usage)

- **Database**: Supabase Free Tier ($0)
- **Backend**: Cloud Run with generous free tier ($0-5)
- **Frontend**: Cloud Run ($0-2)
- **Storage**: Cloud Run included ($0)

**Total**: **$0-7/month** 🎉

---

## 📝 Notes

1. **Always Free Tier Limits**:

   - Compute Engine f1-micro: Only in us-central1, us-west1, us-east1
   - Must be in "Always Free" eligible regions

2. **Google Cloud $300 Credit**:

   - Valid for 90 days from signup
   - Requires credit card verification
   - Perfect for testing Cloud SQL

3. **Supabase Free Tier**:

   - Projects pause after 1 week of inactivity
   - Can be reactivated instantly
   - Good for development/small projects

4. **Production Recommendation**:
   - For serious production: Use Cloud SQL db-f1-micro or higher
   - For hobby projects: Supabase or Neon free tier
   - For long-term free: Compute Engine f1-micro + manual PostgreSQL

---

## 🆘 Migration Guide

### From Cloud SQL to Supabase

```bash
# 1. Export from Cloud SQL
gcloud sql export sql cv-analyzer-db gs://your-bucket/export.sql \
  --database=cv_analyzer

# 2. Download export
gsutil cp gs://your-bucket/export.sql .

# 3. Import to Supabase
# Use Supabase SQL Editor to run the export

# 4. Update Cloud Run
gcloud run services update cv-analyzer-backend \
  --update-secrets="DATABASE_URL=supabase-url:latest"
```

---

**Last Updated**: October 2025
