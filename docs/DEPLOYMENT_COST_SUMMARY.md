# CV Analyzer - Deployment Cost Summary

Quick reference for deployment costs and database options.

## 🆓 Can I Deploy for FREE?

**YES!** Here's how:

### Best FREE Option: Supabase + Cloud Run

| Component        | Service               | Cost              |
| ---------------- | --------------------- | ----------------- |
| **Database**     | Supabase Free Tier    | **$0**            |
| **Backend API**  | Cloud Run (free tier) | **$0-3**          |
| **Frontend**     | Cloud Run (free tier) | **$0-2**          |
| **File Storage** | Cloud Run included    | **$0**            |
| **Total**        |                       | **$0-5/month** 🎉 |

**Setup Time**: ~15 minutes  
**Perfect For**: Learning, development, small personal projects  
**Guide**: [FREE_DATABASE_OPTIONS.md](FREE_DATABASE_OPTIONS.md)

---

## Database Options Comparison

| Database               | Cost/Month | Storage   | Setup Time | Maintenance | Best For                       |
| ---------------------- | ---------- | --------- | ---------- | ----------- | ------------------------------ |
| **Supabase**           | $0         | 500 MB    | 5 mins     | None        | Development, small projects    |
| **Neon**               | $0         | 3 GB      | 5 mins     | None        | Development, personal projects |
| **GCE f1-micro**       | $0         | 30 GB     | 30 mins    | Manual      | Long-term free, advanced users |
| **GC Free Trial**      | $0\*       | Unlimited | 10 mins    | None        | Testing Cloud SQL (90 days)    |
| **Cloud SQL f1**       | $7-15      | 10+ GB    | 10 mins    | None        | Production (small scale)       |
| **Cloud SQL standard** | $50-100    | 100+ GB   | 10 mins    | None        | Production (medium scale)      |

\*Uses $300 credit, valid for 90 days

---

## Quick Decision Tree

### Are you learning or building a personal project?

→ **Use Supabase Free Tier** ($0/month)

### Do you need a production-ready solution?

→ Is budget tight?

- Yes → **Use Supabase Pro** ($25/month)
- No → **Use Cloud SQL db-f1-micro** ($7-15/month)

### Do you want permanent free hosting?

→ **Use Compute Engine f1-micro** (manual setup, $0/month)

### Do you want to test Cloud SQL first?

→ **Use Google Cloud $300 free trial** (90 days free)

---

## Detailed Cost Breakdown

### Option 1: FREE (Supabase)

```
Database (Supabase):    $0
Backend (Cloud Run):    $0-3
Frontend (Cloud Run):   $0-2
Storage:                $0
----------------------
Total:                  $0-5/month ✅
```

**Pros**: Completely free, easy setup, pgvector included  
**Cons**: 500 MB storage limit, projects pause after 1 week inactivity (free tier)

### Option 2: Low-Cost (Cloud SQL db-f1-micro)

```
Database (Cloud SQL):   $7-15
Backend (Cloud Run):    $5-10
Frontend (Cloud Run):   $2-5
Storage:                $1-3
----------------------
Total:                  $15-33/month
```

**Pros**: Fully managed, automatic backups, scalable  
**Cons**: Not free, limited resources on f1-micro

### Option 3: Production (Cloud SQL standard)

```
Database (Cloud SQL):   $50-100
Backend (Cloud Run):    $20-50
Frontend (Cloud Run):   $10-20
Storage:                $5-10
CDN:                    $5-15
----------------------
Total:                  $90-195/month
```

**Pros**: Production-ready, high performance, highly available  
**Cons**: Higher cost

### Option 4: Permanent Free (GCE f1-micro)

```
Database (GCE f1-micro): $0 (Always Free)
Backend (Cloud Run):     $0-3
Frontend (Cloud Run):    $0-2
Storage:                 $0
----------------------
Total:                   $0-5/month ✅
```

**Pros**: Permanently free, full control  
**Cons**: Manual setup and maintenance, limited resources

---

## Cloud SQL is NOT Free ❌

**Important Clarification**:

- `db-f1-micro` is the **cheapest** Cloud SQL tier
- It costs **~$7-15/month** (not free)
- There is NO "Always Free" tier for Cloud SQL

**Free Alternatives**:

1. ✅ Supabase (free tier)
2. ✅ Neon (free tier)
3. ✅ Compute Engine f1-micro with manual PostgreSQL
4. ✅ Google Cloud $300 free trial (90 days)

---

## Google Cloud Free Tier Explained

### Always Free (Permanent)

- **Compute Engine**: 1 x f1-micro VM (us-central1, us-west1, us-east1)
- **Cloud Run**: 2 million requests/month, 360,000 GB-seconds
- **Cloud Storage**: 5 GB standard storage
- **Cloud SQL**: ❌ NOT included

### Free Trial (90 Days)

- **$300 credit** for any Google Cloud services
- Valid for 90 days from signup
- Requires credit card verification
- Perfect for testing Cloud SQL

---

## Recommended Setups by Use Case

### 🎓 Learning / Tutorial

**Setup**: Supabase + Cloud Run  
**Cost**: $0-5/month  
**Guide**: [QUICK_START_CLOUDRUN.md](QUICK_START_CLOUDRUN.md)

### 🛠️ Personal Project / Portfolio

**Setup**: Supabase Pro OR Neon  
**Cost**: $0-25/month  
**Guide**: [FREE_DATABASE_OPTIONS.md](FREE_DATABASE_OPTIONS.md)

### 🚀 Small Business / Startup (MVP)

**Setup**: Cloud SQL db-f1-micro + Cloud Run  
**Cost**: $15-50/month  
**Guide**: [GOOGLE_CLOUD_RUN_DEPLOYMENT.md](GOOGLE_CLOUD_RUN_DEPLOYMENT.md)

### 🏢 Production (Growing)

**Setup**: Cloud SQL db-n1-standard-1 + Cloud Run (min 1 instance)  
**Cost**: $100-200/month  
**Guide**: [GOOGLE_CLOUD_RUN_DEPLOYMENT.md](GOOGLE_CLOUD_RUN_DEPLOYMENT.md)

---

## How to Get Started FREE

### 1. Quick Free Deployment (Supabase)

```bash
# 1. Sign up at https://supabase.com (no credit card)
# 2. Create a project
# 3. Run this SQL in Supabase SQL Editor:

CREATE EXTENSION vector;

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

# 4. Get connection string from Settings → Database
# 5. Deploy to Cloud Run with DATABASE_URL

# Total time: ~15 minutes
# Total cost: $0/month
```

### 2. Using Google Cloud Free Trial

```bash
# 1. Sign up for Google Cloud ($300 credit)
# 2. Use Cloud SQL db-f1-micro
# 3. Deploy normally

# Available credit: $300 for 90 days
# After 90 days: ~$15-30/month
```

---

## FAQ

### Q: Is there any way to use Cloud SQL for free?

**A**: Only through the $300 free trial (90 days). After that, db-f1-micro costs ~$7-15/month.

### Q: What's the cheapest permanent free option?

**A**: Supabase free tier or Compute Engine f1-micro with manual PostgreSQL. Both are $0/month.

### Q: Can I migrate from Supabase to Cloud SQL later?

**A**: Yes! Just export your data and import to Cloud SQL. The application code doesn't need changes.

### Q: What if I exceed Supabase free tier limits?

**A**: Upgrade to Supabase Pro ($25/month) or migrate to Cloud SQL db-f1-micro ($7-15/month).

### Q: Which option is best for production?

**A**: Cloud SQL db-n1-standard-1 or higher for reliability and performance. Supabase Pro is also production-ready.

### Q: Can Cloud Run be free?

**A**: Yes! Cloud Run has generous free tier:

- 2 million requests/month
- 360,000 GB-seconds compute time
- 180,000 vCPU-seconds
  For low-traffic apps, this can be $0/month.

---

## Next Steps

1. **For FREE deployment**: Read [FREE_DATABASE_OPTIONS.md](FREE_DATABASE_OPTIONS.md)
2. **For quick start**: Follow [QUICK_START_CLOUDRUN.md](QUICK_START_CLOUDRUN.md)
3. **For detailed guide**: See [GOOGLE_CLOUD_RUN_DEPLOYMENT.md](GOOGLE_CLOUD_RUN_DEPLOYMENT.md)

---

**Last Updated**: October 2025  
**Need Help?** Check the deployment documentation or open an issue.
