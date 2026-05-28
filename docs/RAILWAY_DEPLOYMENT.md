# Railway Deployment Guide

## Overview
This project is configured to deploy automatically to Railway using GitHub Actions.

## Setup Steps

### 1. Create Railway Account & Project
```bash
# Login to Railway at https://railway.app
# Create a new project
```

### 2. Get Your Railway Token
1. Go to https://railway.app/account/tokens
2. Create a new API token
3. Copy the token

### 3. Set GitHub Secrets
In your GitHub repository:
1. Go to **Settings → Secrets and variables → Actions**
2. Add these secrets:
   - `RAILWAY_TOKEN`: Your Railway API token
   - `RAILWAY_PROJECT_ID`: Your Railway project ID (found in project settings)

### 4. Configure Railway Project
In Railway dashboard:
1. Create a new service
2. Connect your GitHub repository
3. Set root directory to `backend/`
4. Add environment variables (if needed):
   ```
   DATABASE_URL=your_db_url
   API_KEY=your_api_key
   ```

### 5. Deploy
Simply push to main branch:
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

## Manual Deployment (Alternative)

If you prefer manual deployment from CLI:

```bash
cd backend

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

## Environment Variables

Railway will use these from `.env` or GitHub secrets:
- `PORT`: Automatically set by Railway (defaults to 3000 or 8000)
- `DATABASE_URL`: Your database connection string
- Any custom variables defined in your app

## Monitoring

View logs and status:
```bash
railway logs
railway status
railway open
```

## Railway Configuration

The deployment uses `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

## Benefits vs Render

✅ **Always On** - No spin-down on free tier
✅ **$5/month free credit** - Usually covers small projects
✅ **Better scaling** - Easier to upgrade when needed
✅ **GitHub integration** - Auto-deploy on push
✅ **Simple configuration** - Uses standard files

## Troubleshooting

### Build fails
Check logs: `railway logs --service <service-name>`

### Environment variables not set
Ensure they're added in Railway dashboard → Variables

### Port not configured
Railway sets `$PORT` automatically. Use it in your app:
```python
port = int(os.getenv("PORT", 8000))
app.run(host="0.0.0.0", port=port)
```

## References
- [Railway Docs](https://docs.railway.com)
- [Railway CLI Docs](https://docs.railway.com/cli/installation)
- [GitHub Actions Integration](https://docs.railway.com/deploy/github)
