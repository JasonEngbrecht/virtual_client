# Virtual Client - Deployment Guide

## 🚀 Deployment Strategy

### Overview
Our deployment approach prioritizes simplicity during development:
1. **Local Development** - Use during initial MVP development
2. **Railway Deployment** - When ready for external testers (~$10-20/month)
3. **Production Scaling** - After MVP validation

## 📍 Local Development (Current Phase)

### Setup
```bash
# Environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment variables (.env file)
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./virtual_client.db
ENVIRONMENT=development
```

### Running Services
```bash
# Start FastAPI backend
python start_server.py

# In another terminal - Start Streamlit UI
streamlit run mvp/teacher_test.py
```

### Database
- Using SQLite for simplicity
- Data stored in `virtual_client.db`
- No additional setup required

## 🚂 Railway Deployment (When Ready for External Testing)

### Why Railway?
- **Simple** - Works with existing codebase without changes
- **Affordable** - ~$10-20/month for MVP testing
- **PostgreSQL included** - Scales better than SQLite
- **Auto-deploy** - Push to GitHub = deployed
- **Environment variables** - Secure API key storage

### Setup Steps

#### 1. Create Railway Account
Sign up at [railway.app](https://railway.app)

#### 2. Install Railway CLI
```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (use npm)
npm install -g @railway/cli
```

#### 3. Initialize Project
```bash
# In project root
railway login
railway init
```

#### 4. Add PostgreSQL
```bash
railway add
# Select PostgreSQL from menu
```

#### 5. Configure Environment
```bash
# Set environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set ENVIRONMENT=production
```

#### 6. Create Configuration File
```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python start_server.py"

# If running both FastAPI and Streamlit
[[services]]
name = "api"
startCommand = "python start_server.py"

[[services]]
name = "streamlit"  
startCommand = "streamlit run mvp/teacher_test.py --server.port $PORT"
```

#### 7. Deploy
```bash
railway up
```

### Database Configuration

Update your database connection to work both locally and on Railway:

```python
# backend/services/database.py
import os
from sqlalchemy import create_engine

def get_database_url():
    """Get database URL based on environment"""
    if os.getenv("RAILWAY_ENVIRONMENT"):
        # Use Railway's PostgreSQL
        return os.getenv("DATABASE_URL")
    else:
        # Use local SQLite
        return "sqlite:///./virtual_client.db"

# Use this URL for engine creation
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
```

### Accessing Your Deployment

After deployment:
```bash
# Get your app URL
railway open

# View logs
railway logs

# SSH into container (for debugging)
railway shell
```

Your app will be available at:
- API: `https://your-app.up.railway.app`
- Streamlit: `https://your-app.up.railway.app` (if using multi-service)

## 🔐 Security Considerations

### API Keys
- Never commit `.env` files
- Use Railway's environment variables
- Rotate keys if exposed

### Database
- Railway provides SSL connections automatically
- Backups available in paid tiers
- Connection strings are secure

### Access Control
- Railway provides basic authentication
- Can add custom domain with SSL
- Rate limiting should be implemented in app

## 📊 Cost Management

### Estimated Costs
- **Starter Plan**: $5/month (includes $5 usage)
- **PostgreSQL**: ~$5/month for starter
- **Expected Total**: $10-20/month for MVP

### Monitoring Usage
```bash
# Check current usage
railway status

# View metrics in dashboard
railway open
```

## 🔄 Deployment Workflow

### Development Cycle
1. **Local Development** - Make changes locally
2. **Test Locally** - Ensure everything works
3. **Commit Changes** - Push to GitHub
4. **Auto Deploy** - Railway deploys automatically
5. **Monitor** - Check logs and metrics

### Rollback if Needed
```bash
# View deployment history
railway deployments

# Rollback to previous version
railway rollback
```

## 🚨 Troubleshooting

### Common Issues

#### Port Configuration
```python
# Ensure your apps use Railway's PORT
import os

# For FastAPI
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)

# For Streamlit (handled by --server.port $PORT)
```

#### Database Migrations
```python
# Detect environment and handle accordingly
if os.getenv("RAILWAY_ENVIRONMENT"):
    # PostgreSQL might need migrations
    print("Running on Railway with PostgreSQL")
else:
    # SQLite creates tables automatically
    print("Running locally with SQLite")
```

#### Memory Issues
- Starter plan has 512MB RAM limit
- Monitor usage in Railway dashboard
- Optimize if needed (pagination, caching)

## 📝 Environment Variables Reference

### Required for All Environments
```bash
ANTHROPIC_API_KEY=sk-ant-...  # Your Anthropic API key
```

### Auto-Provided by Railway
```bash
DATABASE_URL=postgresql://...  # PostgreSQL connection
RAILWAY_ENVIRONMENT=production  # Environment name
PORT=xxxx                      # Port for web services
```

### Optional Configuration
```bash
ENVIRONMENT=development|production
MAX_TOKENS_PER_SESSION=10000
RATE_LIMIT_PER_HOUR=100
LOG_LEVEL=INFO
```

## 🎯 Next Steps

### After Successful Railway Deployment
1. Share URL with test users
2. Monitor logs and costs
3. Gather feedback
4. Iterate based on learnings

### Scaling Beyond MVP
- Consider Redis for caching
- Add monitoring (Sentry, LogRocket)
- Implement proper CI/CD
- Evaluate need for CDN
- Plan for horizontal scaling

---

*This deployment guide focuses on simplicity for MVP development. Local development is perfect for initial building, and Railway provides an easy transition when ready for external testing.*