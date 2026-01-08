#!/bin/bash

echo "🎤 Installing Twitter_Spaces_Assistant..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    read -p "Press Enter to continue..."
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
pip3 install streamlit openai pinecone-client keyring PyPDF2 numpy

# Create desktop shortcut
echo "🖥️  Creating desktop shortcut..."
cp "Twitter_Spaces_Assistant.app" ~/Desktop/

echo "✅ Twitter_Spaces_Assistant installed successfully!"
echo "🚀 You can now double-click Twitter_Spaces_Assistant.app on your Desktop"
echo ""
echo "📋 First time setup:"
echo "   1. Double-click Twitter_Spaces_Assistant.app"
echo "   2. Enter your API keys when prompted"
echo "   3. Keys are stored securely on your Mac"
echo ""
read -p "Press Enter to continue..."
