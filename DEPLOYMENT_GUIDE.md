# 🚀 Complete Deployment Guide

## Overview
This guide will help you deploy your Doctor Appointment System:
- **Backend (API + Agents)**: Render (Free Docker Container)
- **Frontend (UI)**: Streamlit Cloud (Free)

## 📋 Pre-Deployment Checklist

### 1. Required API Keys
- [ ] **GROQ_API_KEY**: Get from [console.groq.com](https://console.groq.com)
- [ ] **OPENAI_API_KEY**: Get from [platform.openai.com](https://platform.openai.com)

### 2. GitHub Repository
- [ ] Push all code to GitHub
- [ ] Ensure all files are committed
- [ ] Repository is public (for free tiers)

## 🐳 Backend Deployment (Render)

### Step 1: Test Docker Locally
```bash
cd backend
./scripts/deploy_render.sh
```

### Step 2: Deploy to Render
1. **Create Render Account**: Go to [render.com](https://render.com)
2. **Connect GitHub**: Link your repository
3. **Create Web Service**:
   - Choose "Build and deploy from a Git repository"
   - Select your repository
   - Choose "Docker" as environment
   - Set root directory to `backend`

### Step 3: Configure Environment Variables
In Render dashboard, add these environment variables:
```
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ALLOWED_ORIGINS=https://your-streamlit-app.streamlit.app,http://localhost:8501
PORT=8000
HOST=0.0.0.0
DEBUG=false
LOG_LEVEL=INFO
```

### Step 4: Add Persistent Storage
- Add a disk with 1GB storage
- Mount path: `/app/data`
- This stores chat memory

### Step 5: Verify Deployment
- Check health endpoint: `https://your-app.onrender.com/health`
- Test API: `https://your-app.onrender.com/agents/status`

## 🎨 Frontend Deployment (Streamlit Cloud)

### Step 1: Prepare UI Directory
Your UI structure should be:
```
ui/
├── enhanced_app.py
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
```

### Step 2: Deploy to Streamlit Cloud
1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Connect GitHub**: Link your repository
3. **Configure App**:
   - Repository: your-username/your-repo
   - Branch: main
   - Main file path: `backend/ui/enhanced_app.py`

### Step 3: Configure Secrets
In Streamlit Cloud dashboard, add secrets:
```toml
[api]
backend_url = "https://your-render-app.onrender.com"
request_timeout = 15

[app]
title = "Doctor Appointment System"
description = "AI-powered appointment management"
```

### Step 4: Update CORS
Update your Render backend environment variable:
```
ALLOWED_ORIGINS=https://your-streamlit-app.streamlit.app
```

## 🧪 Testing Your Deployment

### 1. Backend Tests
```bash
# Health check
curl https://your-app.onrender.com/health

# Agents status
curl https://your-app.onrender.com/agents/status
```

### 2. Frontend Tests
- Visit your Streamlit app URL
- Test chat functionality
- Try booking an appointment
- Verify memory persistence

### 3. End-to-End Test
1. Open Streamlit app
2. Enter patient ID (e.g., 12345678)
3. Send a message: "I want to book an appointment"
4. Verify the agent responds appropriately
5. Check that conversation history persists

## 🔧 Troubleshooting

### Common Issues

#### Backend Issues:
1. **Build Fails**: Check Dockerfile and requirements.txt
2. **Health Check Fails**: Verify port configuration
3. **API Keys**: Ensure they're set in Render dashboard

#### Frontend Issues:
1. **Can't Connect to Backend**: Check backend_url in secrets
2. **CORS Errors**: Update ALLOWED_ORIGINS in backend
3. **Import Errors**: Verify requirements.txt

#### Memory Issues:
1. **Chat Not Persisting**: Check persistent disk configuration
2. **Data Loss**: Ensure `/app/data` is mounted correctly

### Debug Commands
```bash
# Check Docker build locally
docker build -t test-app .
docker run -p 8000:8000 test-app

# Test API locally
curl http://localhost:8000/health
```

## 📊 Monitoring

### Render Monitoring
- View logs in Render dashboard
- Monitor resource usage
- Set up alerts for downtime

### Streamlit Monitoring
- Built-in analytics in Streamlit Cloud
- Monitor user interactions
- Track app performance

## 🔒 Security Best Practices

1. **API Keys**: Never commit to repository
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Restrict to your domains only
4. **Input Validation**: Backend validates all inputs
5. **Rate Limiting**: Consider adding rate limits

## 💰 Cost Optimization

### Free Tier Limits:
- **Render**: 750 hours/month (enough for 24/7)
- **Streamlit**: Unlimited public apps
- **Storage**: 1GB persistent disk

### Scaling Options:
- Upgrade Render plan for more resources
- Add Redis for better caching
- Implement database for production data

## 🚀 Your Live URLs

After deployment, your system will be available at:
- **Backend API**: `https://your-app-name.onrender.com`
- **User Interface**: `https://your-app-name.streamlit.app`

## 📞 Support

If you encounter issues:
1. Check the logs in both platforms
2. Verify environment variables
3. Test endpoints individually
4. Review this guide for missed steps

Your Doctor Appointment System is now production-ready! 🎉