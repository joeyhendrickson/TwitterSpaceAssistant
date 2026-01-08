#!/bin/bash

echo "🎤 Audio Assistant Desktop Apps - Mac Setup"
echo "============================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3"
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install system dependencies for audio
echo "📦 Installing system dependencies..."
if command -v brew &> /dev/null; then
    echo "Using Homebrew to install audio dependencies..."
    brew install portaudio ffmpeg
else
    echo "⚠️  Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "   Then run: brew install portaudio ffmpeg"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements_desktop.txt

# Make apps executable
echo "🔧 Making apps executable..."
chmod +x twitter_spaces_app.py
chmod +x linkedin_calls_app.py
chmod +x in_person_meeting_app.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the apps:"
echo ""
echo "🐦 Twitter Spaces Assistant:"
echo "   python3 -m streamlit run twitter_spaces_app.py"
echo ""
echo "💼 LinkedIn Calls Assistant:"
echo "   python3 -m streamlit run linkedin_calls_app.py"
echo ""
echo "🤝 In-Person Meeting Assistant:"
echo "   python3 -m streamlit run in_person_meeting_app.py"
echo ""
echo "📋 First-time setup:"
echo "   1. Get your API keys:"
echo "      - OpenAI: https://platform.openai.com/api-keys"
echo "      - Pinecone: https://app.pinecone.io/"
echo "   2. Run any app and enter your API keys when prompted"
echo "   3. Keys will be stored securely on your Mac"
echo ""
echo "🎉 Enjoy your audio assistants!"



