#!/bin/bash

echo "🚀 AI Conversation Assistant Hub - Deployment Script"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one with your API keys:"
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo "   PINECONE_API_KEY=your_pinecone_api_key_here"
    echo "   PINECONE_ENV=us-east-1"
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Streamlit Cloud (Recommended for events)"
echo "2. Heroku"
echo "3. Local Network"
echo ""

read -p "Choose deployment option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🎯 Streamlit Cloud Deployment"
        echo "============================"
        echo "1. Push your code to GitHub:"
        echo "   git add ."
        echo "   git commit -m 'Ready for deployment'"
        echo "   git push origin main"
        echo ""
        echo "2. Go to https://share.streamlit.io"
        echo "3. Sign in with GitHub"
        echo "4. Click 'New app'"
        echo "5. Select your repository"
        echo "6. Set main file to: dashboard.py"
        echo "7. Add environment variables:"
        echo "   - OPENAI_API_KEY"
        echo "   - PINECONE_API_KEY"
        echo "   - PINECONE_ENV"
        echo "8. Click 'Deploy'"
        ;;
    2)
        echo ""
        echo "🎯 Heroku Deployment"
        echo "==================="
        echo "1. Install Heroku CLI if not already installed"
        echo "2. Run these commands:"
        echo "   heroku create your-app-name"
        echo "   heroku buildpacks:add heroku/python"
        echo "   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-ffmpeg-latest"
        echo "   heroku config:set OPENAI_API_KEY=your_key"
        echo "   heroku config:set PINECONE_API_KEY=your_key"
        echo "   heroku config:set PINECONE_ENV=us-east-1"
        echo "   git push heroku main"
        ;;
    3)
        echo ""
        echo "🎯 Local Network Deployment"
        echo "=========================="
        echo "1. Find your IP address:"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "   ifconfig | grep 'inet ' | grep -v 127.0.0.1"
        else
            echo "   ip addr show | grep 'inet ' | grep -v 127.0.0.1"
        fi
        echo ""
        echo "2. Run the app:"
        echo "   streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0"
        echo ""
        echo "3. Access from other devices:"
        echo "   http://YOUR_IP_ADDRESS:8501"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment instructions completed!"
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo "🎉 Good luck with your tech event!"
