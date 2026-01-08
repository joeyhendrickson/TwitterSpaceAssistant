#!/usr/bin/env python3
"""
Twitter Spaces Assistant - Standalone Desktop App
Real-time audio recording and intelligent question generation for Twitter Spaces conversations.
"""

import os
import sys
import streamlit as st
import time
import numpy as np
import sounddevice as sd
import whisper
from uuid import uuid4
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json
import datetime
from collections import defaultdict
import keyring
import getpass

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🐦 Twitter Spaces Assistant",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #1da1f2;
    }
    .recording-indicator {
        background: #ff4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        text-align: center;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def setup_api_keys():
    """Setup API keys using keyring for secure storage"""
    
    # Check if keys are already stored
    stored_openai_key = keyring.get_password("twitter_spaces_assistant", "openai_api_key")
    stored_pinecone_key = keyring.get_password("twitter_spaces_assistant", "pinecone_api_key")
    
    if stored_openai_key and stored_pinecone_key:
        return stored_openai_key, stored_pinecone_key
    
    st.markdown("""
    <div class="main-header">
        <h1>🐦 Twitter Spaces Assistant</h1>
        <p>One-time setup required</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🔐 **First-time setup**: Please provide your API keys. These will be stored securely on your Mac.")
    
    with st.form("api_setup"):
        openai_key = st.text_input("OpenAI API Key", type="password", 
                                  help="Get your key from https://platform.openai.com/api-keys")
        pinecone_key = st.text_input("Pinecone API Key", type="password",
                                    help="Get your key from https://app.pinecone.io/")
        pinecone_env = st.selectbox("Pinecone Environment", ["us-east-1", "us-west-1", "eu-west-1"], 
                                   help="Your Pinecone environment")
        
        submitted = st.form_submit_button("Save & Continue")
        
        if submitted and openai_key and pinecone_key:
            # Store keys securely
            keyring.set_password("twitter_spaces_assistant", "openai_api_key", openai_key)
            keyring.set_password("twitter_spaces_assistant", "pinecone_api_key", pinecone_key)
            keyring.set_password("twitter_spaces_assistant", "pinecone_env", pinecone_env)
            
            st.success("✅ API keys saved securely! You won't need to enter these again.")
            time.sleep(2)
            st.rerun()
        elif submitted:
            st.error("Please enter both API keys.")
    
    st.stop()

def initialize_clients():
    """Initialize OpenAI and Pinecone clients"""
    try:
        from openai import OpenAI
        from pinecone import Pinecone
        
        # Get stored keys
        openai_api_key = keyring.get_password("twitter_spaces_assistant", "openai_api_key")
        pinecone_api_key = keyring.get_password("twitter_spaces_assistant", "pinecone_api_key")
        pinecone_env = keyring.get_password("twitter_spaces_assistant", "pinecone_env") or "us-east-1"
        
        if not openai_api_key or not pinecone_api_key:
            st.error("API keys not found. Please restart the app.")
            st.stop()
        
        client = OpenAI(api_key=openai_api_key)
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Create or get index
        index_name = "twitter-spaces-assistant"
        try:
            index = pc.Index(index_name)
        except Exception:
            # Create index if it doesn't exist
            from pinecone import ServerlessSpec
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            index = pc.Index(index_name)
        
        return client, index
        
    except Exception as e:
        st.error(f"Error initializing clients: {e}")
        st.stop()

# Configuration
RECORD_DURATION = 5  # seconds per recording chunk
ROLLING_BUFFER_LIMIT = 12  # number of chunks before generating questions
MODEL_NAME = "base"  # Whisper model size

@st.cache_resource
def load_whisper_model():
    """Load Whisper model for transcription"""
    return whisper.load_model(MODEL_NAME)

def chunk_text(text, max_tokens=500):
    """Split text into chunks for processing"""
    words = text.split()
    return [" ".join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]

def get_embedding(client, text):
    """Get embedding for text using OpenAI"""
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def embed_and_upsert(client, index, text, topic):
    """Embed text and store in Pinecone"""
    for chunk in chunk_text(text):
        vector = get_embedding(client, chunk)
        index.upsert([{
            "id": str(uuid4()),
            "values": vector,
            "metadata": {"text": chunk, "topic": topic, "app": "twitter_spaces"}
        }])

def query_context(client, index, query, topic):
    """Query context from Pinecone"""
    vector = get_embedding(client, query)
    try:
        response = index.query(
            vector=vector, 
            top_k=5, 
            include_metadata=True,
            filter={"topic": topic}
        )
        return "\n".join([match['metadata']['text'] for match in response.matches])
    except Exception:
        return ""

def summarize_and_append(client, index, transcript, topic):
    """Summarize transcript and store in vector database"""
    summary_prompt = f"Summarize this Twitter Spaces transcript:\n\n{transcript}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    summary = response.choices[0].message.content.strip()
    embed_and_upsert(client, index, summary, topic)

def generate_questions(client, index, transcript, topic, prompt_override=None):
    """Generate intelligent questions based on transcript and context"""
    context = query_context(client, index, transcript, topic)
    
    full_prompt = f"""
You are an expert assistant listening to a live Twitter Spaces conversation. Your goal is to generate 7 intelligent, context-specific questions that will help the speaker (me) sound informed and drive the conversation forward.

Put primary emphasis on the most recent transcription of the call — the most important and relevant part of the context.

Use other background information as supplemental, only if it's relevant to what was just said.

---
Live Transcript:
{transcript}

---
Relevant Background Context:
{context}

---
Generate 3 intelligent, discussion-forwarding questions:"""

    if prompt_override:
        full_prompt += f"\n\nAdditional Context: {prompt_override}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt.strip()}]
    )
    return response.choices[0].message.content.strip()

def record_audio(duration=RECORD_DURATION, sample_rate=16000):
    """Record audio from microphone"""
    try:
        # Record audio
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        
        # Convert to numpy array
        audio_np = np.squeeze(audio)
        
        return audio_np
    except Exception as e:
        st.error(f"Audio recording error: {e}")
        return None

def transcribe_audio(whisper_model, audio_np):
    """Transcribe audio using Whisper"""
    try:
        result = whisper_model.transcribe(audio_np, fp16=False)
        return result["text"].strip()
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""

def main():
    """Main Twitter Spaces Assistant function"""
    
    # Setup API keys if needed
    setup_api_keys()
    
    # Initialize clients
    client, index = initialize_clients()
    
    # Load Whisper model
    whisper_model = load_whisper_model()
    
    # Main app interface
    st.markdown("""
    <div class="main-header">
        <h1>🐦 Twitter Spaces Assistant</h1>
        <p>Real-time audio recording and intelligent question generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        topic = st.text_input("Conversation Topic", value="default", 
                             help="Used to organize your conversations")
        
        if st.button("🗑️ Clear Topic Data"):
            try:
                index.delete(filter={"topic": topic})
                st.success(f"Cleared data for topic: {topic}")
            except Exception as e:
                st.error(f"Error clearing data: {e}")
        
        st.divider()
        
        st.header("📊 Usage")
        st.info("""
        **Features:**
        - 🎤 Real-time audio recording
        - 🤖 AI transcription
        - 🧠 Context-aware questions
        - 📚 PDF context upload
        - 💾 Local data storage
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader("📄 Upload Context PDF", type="pdf")
        if uploaded_file:
            pdf = PdfReader(uploaded_file)
            raw_text = "\n".join([page.extract_text() for page in pdf.pages])
            embed_and_upsert(client, index, raw_text, topic)
            st.success("✅ PDF uploaded and embedded in your knowledge base!")
        
        # Custom prompt
        custom_prompt = st.text_area("💭 Custom Context (Optional)", 
                                   height=100,
                                   placeholder="Add any specific context or instructions for question generation...")
    
    with col2:
        # Recording controls
        st.header("🎤 Recording")
        
        col_start, col_stop = st.columns(2)
        
        with col_start:
            start_button = st.button("🔴 Start Recording", type="primary")
        
        with col_stop:
            stop_button = st.button("⏹️ Stop Recording")
        
        if st.button("🔄 Reset Session"):
            st.session_state.recording = False
            st.session_state.transcript_buffer = []
            st.session_state.all_transcripts = []
            st.rerun()
    
    # Initialize session state
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "transcript_buffer" not in st.session_state:
        st.session_state.transcript_buffer = []
    if "all_transcripts" not in st.session_state:
        st.session_state.all_transcripts = []
    
    # Recording logic
    if start_button:
        st.session_state.recording = True
    
    if stop_button:
        st.session_state.recording = False
    
    # Display areas
    transcript_display = st.empty()
    question_display = st.empty()
    status_display = st.empty()
    
    # Main recording loop
    if st.session_state.recording:
        try:
            while st.session_state.recording:
                status_display.markdown("""
                <div class="recording-indicator">
                    🔴 RECORDING - Click "Stop Recording" to stop
                </div>
                """, unsafe_allow_html=True)
                
                # Record audio
                audio_np = record_audio()
                if audio_np is not None:
                    # Transcribe audio
                    text = transcribe_audio(whisper_model, audio_np)
                    
                    if text and text.strip():
                        st.session_state.all_transcripts.append(text)
                        st.session_state.transcript_buffer.append(text)
                        
                        # Keep buffer size manageable
                        if len(st.session_state.transcript_buffer) > ROLLING_BUFFER_LIMIT:
                            st.session_state.transcript_buffer.pop(0)
                        
                        # Display current transcript
                        joined_text = " ".join(st.session_state.transcript_buffer)
                        transcript_display.markdown(f"**📝 Latest Transcript:**\n{joined_text}")
                        
                        # Generate questions periodically
                        if len(st.session_state.all_transcripts) % ROLLING_BUFFER_LIMIT == 0:
                            summarize_and_append(client, index, joined_text, topic)
                            questions = generate_questions(client, index, joined_text, topic, custom_prompt)
                            question_display.markdown(f"**🤖 Smart Questions:**\n{questions}")
                
                time.sleep(0.1)  # Small delay to prevent UI freezing
                
        except KeyboardInterrupt:
            st.session_state.recording = False
            status_display.success("✅ Recording stopped.")
    
    # Display final results
    if st.session_state.all_transcripts and not st.session_state.recording:
        st.subheader("📝 Complete Session Transcript")
        full_transcript = " ".join(st.session_state.all_transcripts)
        st.text_area("Full Transcript", full_transcript, height=200)
        
        col_save, col_export = st.columns(2)
        
        with col_save:
            if st.button("💾 Save to Knowledge Base"):
                embed_and_upsert(client, index, full_transcript, topic)
                st.success("✅ Session saved to your knowledge base!")
        
        with col_export:
            if st.button("📄 Export Transcript"):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"twitter_spaces_transcript_{topic}_{timestamp}.txt"
                
                # Create download link
                st.download_button(
                    label="📥 Download Transcript",
                    data=full_transcript,
                    file_name=filename,
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()



