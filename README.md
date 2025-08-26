# 🎤 AI Conversation Assistant Hub

A comprehensive dashboard for AI-powered conversation enhancement tools, featuring multiple specialized assistants for different use cases.

## 🚀 Features

### **Twitter Spaces Assistant** 🐦
- **Real-time Audio Transcription**: Live speech-to-text using OpenAI Whisper
- **Context-Aware Questions**: AI-generated follow-up questions based on conversation context
- **PDF Document Integration**: Upload background documents for enhanced context
- **Topic-Based Memory**: Separate conversation memory by topic/namespace
- **Smart Summaries**: Automatic conversation summarization and storage

### **LinkedIn Call Assistant** 💼
- **LinkedIn Profile Analysis**: Extract professional information and social links
- **Social Media Personality Insights**: Analyze posts for interests, personality traits, and communication style
- **Personalized Conversation Prompts**: Generate questions based on individual background
- **Call Goal Integration**: Align questions with specific call objectives
- **Real-time Question Generation**: Context-aware questions during live calls

## 🏗️ Architecture

```
AI Conversation Assistant Hub/
├── dashboard.py              # Main dashboard interface
├── pages/
│   ├── twitter_spaces.py     # Twitter Spaces Assistant
│   └── linkedin_calls.py     # LinkedIn Call Assistant
├── static/
│   └── script.js            # Frontend JavaScript (for future web interface)
├── templates/
│   └── index.html           # HTML template (for future web interface)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **AI/ML**: OpenAI GPT-3.5-turbo, OpenAI Whisper, OpenAI Embeddings
- **Vector Database**: Pinecone (for conversation memory and context)
- **Audio Processing**: SoundDevice, NumPy
- **Web Scraping**: BeautifulSoup4, Requests (for LinkedIn analysis)
- **Document Processing**: PyPDF2

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east-1
```

### 3. Run the Dashboard
```bash
streamlit run dashboard.py
```

### 4. Access the Application
Open your browser and go to: `http://localhost:8501`

## 📱 How to Use

### **Twitter Spaces Assistant**
1. Click "🚀 Launch Twitter Spaces Assistant" on the dashboard
2. Enter a topic for your conversation
3. Optionally upload context PDFs
4. Add a custom prompt to guide question generation
5. Click "Start Listening" to begin real-time transcription
6. Get AI-generated questions based on conversation context

### **LinkedIn Call Assistant**
1. Click "🚀 Launch LinkedIn Call Assistant" on the dashboard
2. Enter the person's name and LinkedIn profile URL
3. Click "🔍 Analyze LinkedIn Profile" to extract information
4. Click "🔍 Analyze Social Media Posts" to get personality insights
5. Review the auto-generated personality summary
6. Enter your call goals and agenda
7. Click "Start Listening" to begin the call with personalized questions

## 🎯 Use Cases

### **Twitter Spaces Assistant**
- Live streaming and podcasting
- Public speaking and presentations
- Group discussions and interviews
- Educational content creation
- Real-time audience engagement

### **LinkedIn Call Assistant**
- Sales calls and prospecting
- Networking conversations
- Job interviews
- Business meetings
- Professional relationship building

## 🔧 Configuration

### **Audio Settings**
- **Recording Duration**: 5 seconds per chunk
- **Sample Rate**: 16kHz
- **Rolling Buffer**: 12 segments for context

### **AI Models**
- **Transcription**: OpenAI Whisper (base model)
- **Question Generation**: GPT-3.5-turbo
- **Embeddings**: text-embedding-ada-002

### **Vector Database**
- **Dimension**: 1536
- **Metric**: Cosine similarity
- **Namespaces**: Separate for each topic/person

## 🔮 Future Enhancements

### **Planned Features**
- [ ] Web interface with WebSocket support
- [ ] Real-time collaboration features
- [ ] Advanced social media analysis
- [ ] Call recording and playback
- [ ] Analytics and insights dashboard
- [ ] Integration with CRM systems
- [ ] Multi-language support
- [ ] Custom AI model fine-tuning

### **Additional Assistants**
- [ ] **Interview Assistant**: For job interviews
- [ ] **Meeting Assistant**: For team meetings
- [ ] **Presentation Assistant**: For public speaking
- [ ] **Customer Support Assistant**: For support calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation
- Review the troubleshooting guide

## 🔐 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Regularly rotate API keys
- Monitor API usage and costs
- Follow security best practices for web scraping

---

**Built with ❤️ using Streamlit, OpenAI, and Pinecone** 