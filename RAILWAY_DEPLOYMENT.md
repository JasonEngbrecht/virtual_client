# 🚂 Railway Deployment Guide

## Overview
This guide covers deploying the Virtual Client MVP to Railway for external testing.

**Estimated Cost**: $15-20/month
- PostgreSQL database: ~$5-10/month
- Web service: ~$10/month

## 🎯 Deployment Architecture
- **Single Service**: All interfaces (teacher, student, admin) + FastAPI
- **Database**: Railway PostgreSQL addon
- **Default Interface**: Teacher interface (for initial testing)
- **Access URLs**: All interfaces accessible via different service configurations

## 📋 Pre-Deployment Checklist
- [x] Railway account created
- [x] Payment method added
- [x] Requirements.txt updated with Streamlit + PostgreSQL
- [x] Procfile created
- [x] app_launcher.py created
- [x] railway_init.py created
- [x] railway.json configuration
- [x] Environment validation scripts

## 🚀 Deployment Steps

### 1. Create Railway Project
```bash
# Option A: From Railway Dashboard
1. Go to railway.app
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Connect your repository

# Option B: Railway CLI (if installed)
railway login
railway init
railway link [project-id]
```

### 2. Add PostgreSQL Database
```bash
# In Railway dashboard:
1. Click "+ New" in your project
2. Select "Database"
3. Choose "PostgreSQL"
4. Wait for provisioning (~2-3 minutes)
```

### 3. Set Environment Variables
In Railway dashboard, go to your service Variables tab:

**Required Variables:**
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
```

**Optional Variables (use defaults if not set):**
```
RAILWAY_SERVICE=teacher
APP_ENV=production
DEBUG=false
PORT=8000
```

### 4. Deploy
```bash
# Push to main branch (if connected to GitHub)
git add .
git commit -m "Railway deployment setup"
git push origin main

# Or use Railway CLI
railway up
```

## 🔧 Service Configuration

### Available Services
Configure via `RAILWAY_SERVICE` environment variable:

- **teacher**: Teacher interface (default)
- **student**: Student practice interface  
- **admin**: Admin monitoring dashboard
- **api**: FastAPI server only
- **multi**: API + Teacher interface

### URLs After Deployment
- **Main Interface**: https://your-app.railway.app
- **Access Other Interfaces**: Change `RAILWAY_SERVICE` env var and redeploy

## 🧪 Testing Deployment

### 1. Check Service Health
```bash
# Test the health endpoint
curl https://your-app.railway.app/

# Check database initialization
# Look for "Database initialized successfully" in Railway logs
```

### 2. Test Each Interface
1. **Teacher Interface** (default):
   - Should load client creation form
   - Create a test client
   - Start a test conversation

2. **Student Interface**:
   - Set `RAILWAY_SERVICE=student`
   - Redeploy
   - Should show available clients

3. **Admin Dashboard**:
   - Set `RAILWAY_SERVICE=admin`
   - Redeploy
   - Should show metrics and active sessions

### 3. Database Verification
Check Railway logs for:
```
✅ Database tables created successfully!
✅ All expected tables created!
✅ Railway sample data added successfully!
```

## 🔍 Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify PostgreSQL addon is running
- Check DATABASE_URL environment variable
- Look for connection errors in logs

**Anthropic API Errors**
- Verify ANTHROPIC_API_KEY is set correctly
- Check API key has sufficient credits
- Test key locally first

**Import Errors**
- Check that PYTHONPATH=/app is set
- Verify all dependencies in requirements.txt
- Check Python version compatibility

**Streamlit Not Loading**
- Verify PORT environment variable
- Check Procfile is correct
- Look for Streamlit startup errors in logs

### Log Analysis
```bash
# View logs in Railway dashboard or CLI
railway logs

# Look for these success indicators:
# 🚂 Initializing Railway database...
# ✅ Database tables created successfully!
# 🎓 Starting teacher interface...
# Local URL: http://0.0.0.0:8000
```

## 📊 Monitoring Deployment

### Key Metrics to Watch
- **Database connections**: Should stay under 20
- **API response times**: Should be under 2 seconds
- **Memory usage**: Should stay under 512MB
- **Token usage**: Monitor costs in admin dashboard

### Cost Monitoring
- Check Railway billing dashboard daily
- Use admin interface to monitor token costs
- Set up alerts for high usage

## 🔄 Making Changes

### Code Updates
```bash
# 1. Make changes locally
git add .
git commit -m "Update description"
git push origin main

# 2. Railway auto-deploys from GitHub
# 3. Monitor logs for successful deployment
```

### Configuration Changes
1. Update environment variables in Railway dashboard
2. Railway will automatically restart the service
3. Monitor logs for successful restart

### Switching Interfaces
1. Change `RAILWAY_SERVICE` environment variable
2. Railway restarts automatically
3. New interface will be available at same URL

## 🎯 External Testing Setup

### For External Testers
Send testers:
1. **Teacher Interface URL**: https://your-app.railway.app
2. **Instructions**: "Use the interface to create clients and test conversations"
3. **Feedback Form**: [Create a simple feedback form]

### Test Scenarios
1. **Teacher Workflow**:
   - Create 2-3 different client profiles
   - Test conversations with each
   - Export conversation history

2. **Cost Monitoring**:
   - Track tokens and costs
   - Aim for <$0.01 per conversation
   - Monitor via admin dashboard

3. **Quality Assessment**:
   - Test conversation realism
   - Check client personality consistency
   - Evaluate educational value

## 🚨 Emergency Procedures

### Stop Service
```bash
# In Railway dashboard:
1. Go to Settings tab
2. Click "Remove Service"
# Or pause deployment temporarily
```

### Reset Database
```bash
# Delete and recreate PostgreSQL addon
# All data will be lost!
```

### Rollback Deployment
```bash
# In Railway dashboard:
1. Go to Deployments tab
2. Click on previous successful deployment
3. Click "Redeploy"
```

## 📈 Success Metrics
- [ ] All 3 interfaces accessible
- [ ] Database properly initialized
- [ ] Sample conversations working
- [ ] Costs under $0.01 per conversation
- [ ] External testers can access and use
- [ ] No critical errors in logs

## 🔗 Useful Links
- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app/
- **PostgreSQL Addon**: https://docs.railway.app/addons/postgresql
- **Support**: contact@railway.app (if issues)
