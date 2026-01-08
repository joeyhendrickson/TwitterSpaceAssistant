#!/bin/bash

# Change to the directory where this script is located
cd "$(dirname "$0")"

echo "💼 LinkedIn Calls Assistant"
echo "==========================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    read -p "Press Enter to continue..."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Running setup first..."
    echo ""
    if [ -f "setup_mac.sh" ]; then
        chmod +x setup_mac.sh
        ./setup_mac.sh
        echo ""
        echo "✅ Setup complete! Now launching LinkedIn Calls Assistant..."
        echo ""
    else
        echo "❌ Setup script not found. Please run setup manually first."
        read -p "Press Enter to continue..."
        exit 1
    fi
fi

# Launch LinkedIn Calls Assistant
echo "🚀 Launching LinkedIn Calls Assistant..."
python3 -m streamlit run linkedin_calls_app.py

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ An error occurred. Check the output above."
    read -p "Press Enter to close..."
fi



