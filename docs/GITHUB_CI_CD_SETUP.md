# GitHub CI/CD Setup Guide

This guide shows you how to set up automated deployment to Google Cloud Run using GitHub Actions. The workflow will automatically deploy your application when code is merged into the `main` branch.

## Prerequisites

1. GitHub repository with your code
2. Google Cloud Project (`cv-analyzer-tlstudio`)
3. Google Cloud service account with necessary permissions
4. GitHub repository secrets configured

## Step 1: Create Service Account

Create a service account in Google Cloud with the necessary permissions:

```bash
# Set variables
export PROJECT_ID="cv-analyzer-tlstudio"
export SA_NAME="github-actions-deployer"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions Deployer" \
  --project=$PROJECT_ID

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL \
  --project=$PROJECT_ID

echo "Service account key saved to github-actions-key.json"
echo "Keep this file secure and delete it after adding to GitHub Secrets!"
```

## Step 2: Configure GitHub Secrets

Go to your GitHub repository: **Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

### 1. GCP_SA_KEY (Required)

- **Name:** `GCP_SA_KEY`
- **Value:** Contents of `github-actions-key.json` file (the entire JSON)
- **How to get:** Copy the entire contents of `github-actions-key.json` file

```bash
# On Linux/Mac
cat github-actions-key.json | pbcopy  # Mac
cat github-actions-key.json | xclip   # Linux

# On Windows
type github-actions-key.json
# Then copy the entire output
```

### 2. CLOUD_SQL_CONNECTION_NAME (Required)

- **Name:** `CLOUD_SQL_CONNECTION_NAME`
- **Value:** `cv-analyzer-tlstudio:us-central1:cv-analyzer-db`
- **How to get:**
  ```bash
  gcloud sql instances describe cv-analyzer-db --format="value(connectionName)"
  ```

### 3. VITE_GA_MEASUREMENT_ID (Optional)

- **Name:** `VITE_GA_MEASUREMENT_ID`
- **Value:** Your Google Analytics Measurement ID (e.g., `G-XXXXXXXXXX`)
- **Note:** Leave empty if you don't use Google Analytics

## Step 3: Verify Workflow File

Ensure the workflow file exists at `.github/workflows/deploy.yml` in your repository root.

The workflow will:

1. Trigger on pushes to `main`/`master` branch
2. Trigger on PR merges to `main`/`master` branch
3. Build and push Docker images for backend and frontend
4. Deploy to Cloud Run
5. Update CORS settings automatically

## Step 4: Test the Workflow

### Option A: Push to Main Branch

```bash
# Make a small change
echo "# Test deployment" >> README.md

# Commit and push
git add README.md
git commit -m "test: trigger deployment"
git push origin main
```

### Option B: Merge a Pull Request

1. Create a new branch:

   ```bash
   git checkout -b test/deployment-trigger
   echo "# Test PR deployment" >> README.md
   git add README.md
   git commit -m "test: trigger deployment via PR"
   git push origin test/deployment-trigger
   ```

2. Create a Pull Request on GitHub

3. Merge the PR into `main`

4. The workflow will automatically start

## Step 5: Monitor Deployment

### View Workflow Runs

1. Go to your GitHub repository
2. Click on **Actions** tab
3. Click on the latest workflow run to see progress
4. Check each step for details

### View Deployment Logs

```bash
# Backend logs
gcloud run services logs read cv-analyzer-backend \
  --region us-central1 \
  --limit 50

# Frontend logs
gcloud run services logs read cv-analyzer-frontend \
  --region us-central1 \
  --limit 50
```

### Check Service Status

```bash
# Get service URLs
gcloud run services describe cv-analyzer-frontend \
  --region us-central1 \
  --format="value(status.url)"

gcloud run services describe cv-analyzer-backend \
  --region us-central1 \
  --format="value(status.url)"
```

## Workflow Configuration

### Triggers

The workflow triggers on:

- **Push** to `main` or `master` branch
- **Pull Request** merged into `main` or `master` branch

### Build Process

1. **Backend:**

   - Builds Docker image from `backend/Dockerfile.cloudrun`
   - Tags with `latest` and commit SHA
   - Pushes to Artifact Registry
   - Deploys to Cloud Run with secrets and environment variables

2. **Frontend:**

   - Gets backend URL from deployed service
   - Builds Docker image from `frontend/Dockerfile.cloudrun`
   - Includes backend URL as build argument
   - Tags with `latest` and commit SHA
   - Pushes to Artifact Registry
   - Deploys to Cloud Run

3. **CORS Update:**
   - Updates backend with frontend URL for CORS

## Customization

### Change Target Branch

Edit `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches:
      - production # Change to your target branch
```

### Deploy Only Frontend

Create a separate workflow file (e.g., `.github/workflows/deploy-frontend.yml`) and remove backend steps.

### Add Additional Steps

You can add steps like:

- Running tests before deployment
- Sending deployment notifications
- Running database migrations
- Invalidating CDN cache

Example:

```yaml
- name: Run tests
  run: |
    cd backend
    pytest

- name: Run database migrations
  run: |
    gcloud run jobs execute run-migrations \
      --region ${{ env.REGION }}
```

## Troubleshooting

### Issue: Workflow not triggering

**Solution:**

- Ensure workflow file is in `.github/workflows/` directory
- Check that the branch name matches (`main` or `master`)
- Verify file syntax is correct (YAML)

### Issue: Authentication failed

**Solution:**

- Verify `GCP_SA_KEY` secret is correctly set (full JSON content)
- Check service account has necessary permissions
- Ensure service account key hasn't expired

### Issue: Build fails

**Solution:**

- Check Dockerfile syntax
- Verify all required files are in repository
- Check build logs in GitHub Actions

### Issue: Deployment fails

**Solution:**

- Verify Cloud Run service names are correct
- Check that secrets exist in Secret Manager
- Ensure service account has `run.admin` permission
- Check Cloud Run quotas/limits

### Issue: CORS errors after deployment

**Solution:**

- Verify frontend URL is correctly set in backend
- Check backend logs for CORS configuration
- Ensure `FRONTEND_URL` environment variable is set

## Security Best Practices

1. **Never commit service account keys** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Rotate service account keys** periodically
4. **Use least privilege principle** for service account permissions
5. **Monitor service account usage** in Cloud Console
6. **Delete old service account keys** after creating new ones

## Cost Considerations

- GitHub Actions: Free tier includes 2,000 minutes/month for private repos
- Cloud Run: Pay only for requests and compute time
- Artifact Registry: Free tier includes 500MB/month

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

## Cleanup

To remove the CI/CD setup:

1. Delete the workflow file:

   ```bash
   rm .github/workflows/deploy.yml
   ```

2. Remove GitHub secrets (optional, if not used elsewhere)

3. Delete service account (optional):

   ```bash
   gcloud iam service-accounts delete github-actions-deployer@cv-analyzer-tlstudio.iam.gserviceaccount.com
   ```

4. Delete service account key file:
   ```bash
   rm github-actions-key.json
   ```
