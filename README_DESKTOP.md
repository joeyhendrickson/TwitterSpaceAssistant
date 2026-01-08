# 🎤 Audio Assistant Desktop Apps

Three standalone desktop applications for real-time audio recording and intelligent conversation enhancement.

## 📱 Apps Included

### 🐦 **Twitter Spaces Assistant**
- Real-time audio recording for Twitter Spaces conversations
- AI-powered question generation
- Context-aware insights
- PDF document upload for background context

### 💼 **LinkedIn Calls Assistant**
- Professional conversation enhancement for LinkedIn calls
- Business-focused question generation
- Follow-up action tracking
- Meeting summary generation

### 🤝 **In-Person Meeting Assistant**
- Meeting facilitation and enhancement
- Action item tracking
- Comprehensive meeting summaries
- Project document context

## 🚀 Quick Start (Mac)

### Prerequisites
- **Python 3.8+** - [Download from python.org](https://python.org)
- **Homebrew** - [Install Homebrew](https://brew.sh)
- **API Keys**:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Pinecone API Key](https://app.pinecone.io/)

### Installation

1. **Clone or download the apps**
   ```bash
   # If you have git
   git clone <repository-url>
   cd audio-assistant-apps
   
   # Or download the files directly
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup_mac.sh
   ./setup_mac.sh
   ```

3. **Get your API keys**
   - **OpenAI**: Go to [platform.openai.com](https://platform.openai.com/api-keys) and create an API key
   - **Pinecone**: Go to [app.pinecone.io](https://app.pinecone.io/) and create an API key

4. **Launch any app**
   ```bash
   # Twitter Spaces Assistant
   python3 -m streamlit run twitter_spaces_app.py
   
   # LinkedIn Calls Assistant
   python3 -m streamlit run linkedin_calls_app.py
   
   # In-Person Meeting Assistant
   python3 -m streamlit run in_person_meeting_app.py
   ```

5. **First-time setup**
   - The app will prompt you to enter your API keys
   - Keys are stored securely on your Mac using the keychain
   - You won't need to enter them again

## 🔧 Manual Installation

If the setup script doesn't work, install manually:

### 1. Install System Dependencies
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install audio dependencies
brew install portaudio ffmpeg
```

### 2. Install Python Dependencies
```bash
pip3 install -r requirements_desktop.txt
```

### 3. Make Apps Executable
```bash
chmod +x twitter_spaces_app.py
chmod +x linkedin_calls_app.py
chmod +x in_person_meeting_app.py
```

## 🎯 How to Use

### First Time Setup
1. **Launch any app** using the commands above
2. **Enter your API keys** when prompted
3. **Keys are stored securely** - you won't need to enter them again

### Using the Apps

#### 🐦 Twitter Spaces Assistant
1. **Set topic** - Enter a conversation topic for organization
2. **Upload context** (optional) - Add PDF documents for background
3. **Start recording** - Click "Start Recording" and speak
4. **Get questions** - AI generates intelligent follow-up questions
5. **Save/export** - Save to knowledge base or export transcript

#### 💼 LinkedIn Calls Assistant
1. **Set meeting type** - Choose from networking, business development, etc.
2. **Upload documents** (optional) - Add resumes, company info, etc.
3. **Start recording** - Record your LinkedIn call
4. **Get insights** - Professional questions and follow-up actions
5. **Export summary** - Download comprehensive meeting report

#### 🤝 In-Person Meeting Assistant
1. **Set meeting details** - Topic, type, and participants
2. **Upload documents** (optional) - Agendas, project docs, etc.
3. **Start recording** - Record your in-person meeting
4. **Get facilitation** - Meeting questions and action items
5. **Export report** - Download complete meeting summary

## 🔒 Security & Privacy

### API Key Storage
- **Secure storage**: Keys are stored in your Mac's keychain
- **Local only**: No keys are sent to external servers
- **App-specific**: Each app has its own secure storage

### Data Privacy
- **Local processing**: Audio is processed on your device
- **Your Pinecone**: Each app creates its own Pinecone index
- **No data sharing**: Your conversations stay private

## 🛠️ Troubleshooting

### Audio Recording Issues
```bash
# Check microphone permissions
System Preferences > Security & Privacy > Microphone

# Test audio recording
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

### API Key Issues
```bash
# Reset stored keys (if needed)
python3 -c "import keyring; keyring.delete_password('app_name', 'openai_api_key')"
```

### Python/Pip Issues
```bash
# Update pip
pip3 install --upgrade pip

# Install with user flag
pip3 install --user -r requirements_desktop.txt
```

### Homebrew Issues
```bash
# Update Homebrew
brew update

# Install specific versions
brew install portaudio@19
```

## 📋 System Requirements

- **OS**: macOS 10.14+ (Mojave or later)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Required for AI API calls

## 🎉 Features

### All Apps Include
- ✅ **Real-time audio recording** with microphone access
- ✅ **Whisper AI transcription** for accurate speech-to-text
- ✅ **OpenAI GPT integration** for intelligent responses
- ✅ **Pinecone vector database** for context storage
- ✅ **PDF document upload** for background context
- ✅ **Secure key storage** using Mac keychain
- ✅ **Export capabilities** for transcripts and summaries
- ✅ **Topic organization** for multiple conversations

### App-Specific Features
- **Twitter Spaces**: Social media conversation optimization
- **LinkedIn Calls**: Professional networking enhancement
- **In-Person Meetings**: Meeting facilitation and action tracking

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Verify your API keys** are correct and have sufficient credits
3. **Ensure microphone permissions** are granted
4. **Check your internet connection** for API calls

## 🔄 Updates

To update the apps:
1. Download the latest files
2. Run the setup script again
3. Your API keys will be preserved

---

**Enjoy your AI-powered conversation assistants!** 🎤✨



