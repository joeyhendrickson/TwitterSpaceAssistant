# 🚀 Railway Deployment Guide - Multi-User Audio Assistant

This guide will help you deploy your multi-user audio assistant to Railway with full functionality including real-time audio recording, user management, and subscription tiers.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **API Keys**: You'll need OpenAI and Pinecone API keys

## 🏗️ Step 1: Prepare Your Repository

### File Structure
Your repository should have this structure:
```
├── dashboard_multiuser.py      # Main multi-user dashboard
├── pages/
│   ├── twitter_spaces_multiuser.py
│   └── linkedin_calls_multiuser.py
├── models/
│   ├── __init__.py
│   └── user.py
├── auth/
│   ├── __init__.py
│   └── user_auth.py
├── migrations/
│   └── create_tables.py
├── Dockerfile
├── railway.json
├── requirements-multiuser.txt
└── README.md
```

### Update Requirements
Make sure `requirements-multiuser.txt` contains all necessary packages:
```txt
streamlit>=1.28.0
streamlit-authenticator>=0.2.3
sounddevice>=0.4.6
whisper>=1.1.10
pyaudio>=0.2.11
numpy>=1.24.0
openai>=1.3.0
pinecone-client>=2.2.4
psycopg2-binary>=2.9.7
sqlalchemy>=2.0.0
redis>=5.0.0
PyPDF2>=3.0.1
bcrypt>=4.0.1
python-dotenv>=1.0.0
```

## 🚀 Step 2: Deploy to Railway

### 2.1 Connect Repository
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect the Dockerfile

### 2.2 Configure Environment Variables
In your Railway project dashboard, go to the "Variables" tab and add:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://username:password@host:port

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=us-east-1

# App Configuration
PORT=8501
```

### 2.3 Add PostgreSQL Database
1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set the `DATABASE_URL` variable

### 2.4 Add Redis Database
1. In Railway dashboard, click "New"
2. Select "Database" → "Redis"
3. Railway will automatically set the `REDIS_URL` variable

## 🗄️ Step 3: Initialize Database

### 3.1 Run Migration Script
After deployment, you need to initialize the database:

1. Go to your Railway project
2. Click on your app service
3. Go to "Deployments" tab
4. Click on the latest deployment
5. Go to "Logs" tab
6. Run the migration script:

```bash
python migrations/create_tables.py
```

### 3.2 Verify Database Setup
The migration script will:
- Create all necessary tables (users, user_sessions, usage_logs)
- Create database indexes for performance
- Create sample users for testing

## 🔧 Step 4: Configure Domain

### 4.1 Custom Domain (Optional)
1. In Railway dashboard, go to your app service
2. Click "Settings" tab
3. Under "Domains", add your custom domain
4. Configure DNS records as instructed

### 4.2 Railway Domain
Railway provides a default domain like: `https://your-app-name.railway.app`

## 🧪 Step 5: Test Your Deployment

### 5.1 Access Your App
1. Go to your Railway app URL
2. You should see the login/register page

### 5.2 Test Sample Users
Use these sample credentials created by the migration script:
- **Admin**: `admin@example.com` / `admin123`
- **User**: `user@example.com` / `user123`

### 5.3 Test Audio Recording
1. Log in with a sample account
2. Go to Twitter Spaces Assistant
3. Click "Start Recording"
4. Allow microphone access
5. Speak into your microphone
6. Verify transcription appears

## 📊 Step 6: Monitor and Scale

### 6.1 Monitor Usage
- **Railway Dashboard**: Monitor resource usage
- **Database**: Check user growth and usage patterns
- **Logs**: Monitor for errors and performance issues

### 6.2 Scaling Options
Railway automatically scales based on usage, but you can:
- **Manual Scaling**: Adjust resources in Railway dashboard
- **Auto-scaling**: Railway handles this automatically
- **Custom Domains**: Add multiple domains for different regions

## 🔒 Step 7: Security Considerations

### 7.1 Environment Variables
- Never commit API keys to your repository
- Use Railway's built-in secrets management
- Rotate API keys regularly

### 7.2 User Data
- All user data is isolated by user ID
- Pinecone namespaces prevent data leakage
- Session tokens are securely managed

### 7.3 Audio Processing
- Audio is processed in memory, not stored permanently
- Transcripts are stored in user-specific Pinecone namespaces
- File uploads are processed securely

## 💰 Step 8: Billing and Costs

### 8.1 Railway Pricing
- **Free Tier**: Limited resources, good for testing
- **Pro Plan**: $5/month for more resources
- **Usage-based**: Pay for what you use

### 8.2 Cost Optimization
- Monitor resource usage in Railway dashboard
- Use appropriate instance sizes
- Consider caching strategies for frequently accessed data

## 🐛 Troubleshooting

### Common Issues

#### 1. Audio Recording Not Working
**Problem**: Microphone access denied or no audio recorded
**Solution**: 
- Check browser permissions
- Ensure HTTPS is enabled (required for microphone access)
- Verify audio libraries are installed in Docker container

#### 2. Database Connection Errors
**Problem**: "DATABASE_URL not set" or connection failures
**Solution**:
- Verify DATABASE_URL is set in Railway variables
- Check PostgreSQL service is running
- Ensure database migration script ran successfully

#### 3. API Key Errors
**Problem**: OpenAI or Pinecone API errors
**Solution**:
- Verify API keys are correct in Railway variables
- Check API key permissions and quotas
- Ensure services are accessible from Railway's network

#### 4. Memory Issues
**Problem**: App crashes or slow performance
**Solution**:
- Increase Railway instance memory
- Optimize Whisper model size (use "tiny" instead of "base")
- Implement better resource management

### Getting Help
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Create issues in your repository

## 🎉 Success!

Your multi-user audio assistant is now deployed on Railway with:
- ✅ Real-time audio recording and transcription
- ✅ User authentication and session management
- ✅ Subscription tier management
- ✅ Usage tracking and limits
- ✅ Secure data isolation
- ✅ Scalable infrastructure

## 📈 Next Steps

1. **Add Payment Processing**: Integrate Stripe for subscription payments
2. **Add Analytics**: Track user engagement and feature usage
3. **Add Email Notifications**: Send usage reports and subscription reminders
4. **Add Admin Panel**: Manage users and monitor system health
5. **Add More Apps**: Expand with additional conversation assistants

---

**Need help?** Check the troubleshooting section or reach out to the Railway community!



