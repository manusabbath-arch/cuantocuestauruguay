# Deployment Guide

This guide covers deploying PreciosRegulados.uy to production using Railway.app (backend) and Cloudflare Pages (frontend).

## Prerequisites

- GitHub account
- Railway.app account (free tier available)
- Cloudflare account (free tier available)
- Your repository pushed to GitHub

## Part 1: Deploy Backend to Railway.app

### 1. Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### 2. Configure Backend Service

1. Railway will detect the Dockerfile in `/backend`
2. Set the root directory to `backend`
3. Add environment variables:

```
DATABASE_URL=<will be auto-configured>
CORS_ORIGINS=https://your-domain.pages.dev
DEBUG=False
CKAN_API_URL=https://catalogodatos.gub.uy/api/3/action
CKAN_COMBUSTIBLES_RESOURCE_ID=62bacbab-9bae-4316-af56-7c1bf468f546
ETL_SCHEDULE_HOUR=2
ETL_SCHEDULE_MINUTE=0
```

### 3. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL`

### 4. Run Migrations

After deployment, run migrations using Railway CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run alembic upgrade head
```

### 5. Get Your Backend URL

Railway will provide a URL like: `https://your-backend.up.railway.app`

## Part 2: Deploy Frontend to Cloudflare Pages

### 1. Create Cloudflare Pages Project

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to "Pages"
3. Click "Create a project"
4. Connect to your GitHub repository

### 2. Configure Build Settings

```
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
Root directory: /
```

### 3. Add Environment Variables

```
VITE_API_URL=https://your-backend.up.railway.app
```

### 4. Deploy

Cloudflare will automatically build and deploy your frontend.
Your site will be available at: `https://your-project.pages.dev`

## Part 3: Configure Custom Domain (Optional)

### Backend (Railway)

1. Go to your Railway project settings
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Frontend (Cloudflare Pages)

1. Go to your Pages project
2. Click "Custom domains"
3. Add your domain
4. Cloudflare will automatically configure DNS

## Part 4: Enable CORS

Update `CORS_ORIGINS` in Railway backend environment variables:

```
CORS_ORIGINS=https://your-domain.pages.dev,https://your-custom-domain.com
```

## Part 5: Setup Automated ETL

The backend includes APScheduler that will run ETL daily at 2 AM.
To manually trigger ETL:

```bash
# Using Railway CLI
railway run python -c "from app.etl.combustibles import CombustiblesETL; from app.core.database import SessionLocal; import asyncio; db = SessionLocal(); etl = CombustiblesETL(db); asyncio.run(etl.run())"

# Or via API (after deploying)
curl -X POST https://your-backend.up.railway.app/api/v1/etl/run
```

## Part 6: Monitoring & Maintenance

### Setup Sentry (Optional)

1. Create a Sentry account at [sentry.io](https://sentry.io)
2. Create a new project
3. Add `SENTRY_DSN` to Railway environment variables
4. Redeploy

### Monitor Logs

**Railway:**
- View logs in Railway dashboard
- Use `railway logs` command

**Cloudflare Pages:**
- View build logs in Cloudflare dashboard
- Use Cloudflare Analytics

### Database Backups

Railway provides automatic PostgreSQL backups.
To create manual backup:

```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

## Part 7: CI/CD with GitHub Actions

The included `.github/workflows/ci.yml` will:

1. Run tests on every push
2. Build Docker images
3. Ensure code quality

To enable automatic deployments:

**Railway:** Automatically deploys on push to main branch

**Cloudflare Pages:** Automatically deploys on push to main branch

## Costs

### Free Tier Limits

**Railway.app:**
- $5 free credit per month
- Enough for small projects
- PostgreSQL included

**Cloudflare Pages:**
- Unlimited bandwidth
- Unlimited requests
- 500 builds per month

### Estimated Monthly Costs

- **Development:** $0 (free tiers)
- **Small traffic:** $0-5 (Railway free tier)
- **Medium traffic:** $5-20 (Railway paid plan)

## Troubleshooting

### Backend won't start
- Check Railway logs
- Verify DATABASE_URL is set
- Ensure migrations have run

### Frontend can't connect to backend
- Verify CORS_ORIGINS includes your frontend URL
- Check VITE_API_URL is correctly set
- Ensure backend is running

### ETL not running
- Check backend logs for scheduler errors
- Verify CKAN API is accessible
- Manually trigger ETL to test

### Database connection issues
- Verify DATABASE_URL format
- Check PostgreSQL service is running
- Review Railway database logs

## Security Best Practices

1. **Never commit `.env` files**
2. **Use environment variables for secrets**
3. **Enable HTTPS only** (automatic on Railway/Cloudflare)
4. **Regular security updates:** `pip install --upgrade` and `npm update`
5. **Monitor for vulnerabilities:** Use Dependabot
6. **Rate limiting:** Add to API if needed
7. **Authentication:** Add to admin endpoints

## Updates & Maintenance

### Update Dependencies

**Backend:**
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm update
npm audit fix
```

### Database Migrations

When changing models:

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Push changes, and Railway will auto-deploy.

## Support

- **Documentation:** See README.md
- **Issues:** GitHub Issues
- **Railway Support:** support@railway.app
- **Cloudflare Support:** Cloudflare Community

---

🎉 **Congratulations!** Your application is now live in production!

Visit your frontend URL to see it in action.
