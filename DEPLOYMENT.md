# 🚀 Deployment Guide for Tech Event

This guide will help you deploy your AI Conversation Assistant Hub for your tech event using Streamlit Cloud.

## 🎯 Quick Deploy Options

### Option 1: Streamlit Cloud (Recommended for Events)
**Perfect for live demos and tech events - free hosting with automatic HTTPS**

1. **Prepare Your Repository**
   - Ensure all files are committed to a GitHub repository
   - Make sure your `.env` file is NOT in the repository (add to .gitignore)

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository and set `dashboard.py` as the main file
   - Add your environment variables (see below)
   - Click "Deploy"

3. **Environment Variables to Set**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENV=us-east-1
   ```

### Option 2: Heroku (Alternative)
**Good for longer-term hosting**

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Add Buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-ffmpeg-latest
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set PINECONE_API_KEY=your_key
   heroku config:set PINECONE_ENV=us-east-1
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: Local Network (For Offline Events)
**Perfect for events without internet access**

1. **Run Locally**
   ```bash
   streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
   ```

2. **Access from Other Devices**
   - Find your computer's IP address
   - Other devices can access via: `http://YOUR_IP:8501`

## 🎪 Event-Specific Setup

### For Live Demos
1. **Pre-load Context**: Upload relevant PDFs before the demo
2. **Test Audio**: Ensure microphone permissions work
3. **Backup Plan**: Have screenshots/videos ready in case of technical issues

### For Interactive Sessions
1. **Multiple Topics**: Create different topics for different sessions
2. **Clear Data**: Use the "Clear Previous Data" feature between sessions
3. **Custom Prompts**: Prepare industry-specific prompts

## 🔧 Troubleshooting

### Common Issues
- **Audio not working**: Check browser permissions
- **API errors**: Verify API keys are set correctly
- **Slow loading**: Whisper model takes time to load first time

### Performance Tips
- Use the "base" Whisper model (already configured)
- Clear conversation data between sessions
- Keep PDF uploads under 10MB

## 📱 Mobile Optimization

The app works on mobile devices but:
- Audio recording works best on desktop
- PDF uploads are easier on desktop
- Consider using desktop for demos

## 🔐 Security for Events

- Use temporary API keys for demos
- Monitor API usage during events
- Consider rate limiting for public demos

## 🎯 Demo Script for Tech Events

### 1. Introduction (2 minutes)
- "This is an AI-powered conversation assistant"
- "It can transcribe speech in real-time and generate intelligent questions"
- "Perfect for live streaming, podcasting, and professional calls"

### 2. Twitter Spaces Demo (3 minutes)
- Upload a relevant PDF (industry report, company info)
- Start listening and speak for 30 seconds
- Show the generated questions
- Explain how it learns from context

### 3. LinkedIn Assistant Demo (2 minutes)
- Show LinkedIn profile analysis
- Demonstrate personality insights
- Generate personalized questions

### 4. Q&A (3 minutes)
- Answer questions about the technology
- Discuss potential use cases
- Share contact information

## 🚀 Post-Event

- Collect feedback from attendees
- Monitor app usage and performance
- Consider improvements based on demo experience
- Follow up with interested parties

---

**Good luck with your tech event! 🎉**
