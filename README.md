# 🍸 IT Martini - Technology Conversation Assistant

An AI-powered conversation partner that generates intelligent, technology-focused questions to help drive your discussions forward.

## 🌟 Features

- **Smart Question Generation**: Creates 10 intelligent questions every 30 seconds based on your conversation
- **Technology Focus**: Specialized in tech trends, challenges, solutions, and emerging technologies
- **Context Awareness**: Uses conversation history and uploaded PDFs for better question generation
- **Vector Storage**: Stores conversation context in Pinecone for intelligent retrieval
- **Web-Ready**: Optimized for cloud deployment

## 🚀 Quick Start

### Local Development
```bash
pip install -r requirements.txt
streamlit run main.py
```

### Web Deployment
The app is optimized for deployment on Streamlit Cloud.

## 🔧 Setup

1. **Environment Variables**: Set up your `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=us-east-1
   ```

2. **Install Dependencies**: `pip install -r requirements.txt`

3. **Run the App**: `streamlit run main.py`

## 📱 Usage

1. **Set Topic**: Choose a conversation topic (default: "technology-discussion")
2. **Upload Context**: Optionally upload a PDF for additional context
3. **Enter Conversation**: Type or paste your technology conversation
4. **Generate Questions**: Click "Generate Questions" to get intelligent follow-up questions
5. **Review Results**: View the generated questions and analyzed conversation

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**: Upload your code to a GitHub repository
2. **Connect to Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io)
3. **Deploy**: Connect your GitHub repo and deploy automatically
4. **Get URL**: Your app will be available at `https://your-app-name.streamlit.app`

### Environment Variables in Streamlit Cloud

Set these in your Streamlit Cloud dashboard:
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENV`

## 🛠️ Technical Details

- **Framework**: Streamlit
- **AI**: OpenAI GPT-3.5-turbo
- **Vector Database**: Pinecone
- **Language**: Python 3.8+

## 📄 License

MIT License - feel free to use and modify!

---

*IT Martini - Making technology conversations more engaging and insightful* 🍸 