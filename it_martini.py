import os
import streamlit as st
import whisper
import sounddevice as sd
import numpy as np
import time
from uuid import uuid4
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# --- STREAMLIT UI ---
st.set_page_config(page_title="IT Martini", page_icon="🍸", layout="wide")

# --- LOAD .env VARIABLES ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV", "us-east-1")

# Check if API keys are available
if not openai_api_key or not pinecone_api_key:
    st.error("🚨 **Configuration Error**")
    st.markdown("""
    This app requires API keys to function. Please set up the following environment variables in your Streamlit Cloud deployment:
    
    **Required Environment Variables:**
    - `OPENAI_API_KEY` - Your OpenAI API key
    - `PINECONE_API_KEY` - Your Pinecone API key
    - `PINECONE_ENV` - Your Pinecone environment (default: us-east-1)
    
    **How to set them:**
    1. Go to your Streamlit Cloud dashboard
    2. Click on your app
    3. Go to "Settings" → "Secrets"
    4. Add the environment variables
    5. Redeploy your app
    
    **Example secrets format:**
    ```
    OPENAI_API_KEY = "sk-your-openai-key-here"
    PINECONE_API_KEY = "your-pinecone-key-here"
    PINECONE_ENV = "us-east-1"
    ```
    """)
    st.stop()

# Initialize API clients
try:
    from openai import OpenAI
    from pinecone import Pinecone
    
    client = OpenAI(api_key=openai_api_key)
    pc = Pinecone(api_key=pinecone_api_key)
    
    # IT Martini specific index - use shared index with namespace
    pinecone_index_name = "conversation-assistant-shared"

    # Check if index exists, if not create it
    try:
        index = pc.Index(pinecone_index_name)
    except Exception:
        # Index doesn't exist, create it
        from pinecone import ServerlessSpec
        pc.create_index(
            name=pinecone_index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        index = pc.Index(pinecone_index_name)
        
except Exception as e:
    st.error(f"🚨 **Connection Error**: {str(e)}")
    st.markdown("""
    There was an error connecting to the AI services. Please check:
    1. Your API keys are correct
    2. Your internet connection
    3. The services are available
    """)
    st.stop()

# --- CONFIG ---
RECORD_DURATION = 5
ROLLING_BUFFER_LIMIT = 6  # Generate questions every 30 seconds (6 * 5 seconds)
MODEL_NAME = "base"

@st.cache_resource
def load_model():
    return whisper.load_model(MODEL_NAME)

whisper_model = load_model()

def chunk_text(text, max_tokens=500):
    words = text.split()
    return [" ".join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]

def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def embed_and_upsert(text, topic):
    for chunk in chunk_text(text):
        vector = get_embedding(chunk)
        index.upsert([{
            "id": str(uuid4()),
            "values": vector,
            "metadata": {"text": chunk}
        }], namespace=f"it-martini-{topic}")

def query_context(query, topic):
    vector = get_embedding(query)
    response = index.query(vector=vector, top_k=5, include_metadata=True, namespace=f"it-martini-{topic}")
    return "\n".join([match['metadata']['text'] for match in response.matches])

def summarize_and_append(transcript, topic):
    summary_prompt = f"Summarize this transcript:\n\n{transcript}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    summary = response.choices[0].message.content.strip()
    embed_and_upsert(summary, topic)

def generate_questions(transcript, topic, prompt_override=None):
    context = query_context(transcript, topic)
    
    # Meeting-focused prompt for In-Person Meeting Assistant
    meeting_prompt = f"""
You are an expert meeting assistant listening to a live conversation. You need to generate 10 intelligent, context-specific questions that will help drive the conversation forward and keep participants engaged.

Focus on:
- Building on what was just discussed
- Encouraging deeper exploration of topics
- Helping participants think critically
- Moving toward productive outcomes
- Addressing gaps or areas needing clarification
- Fostering collaboration and engagement
- Helping reach meeting objectives

Put primary emphasis on the most recent transcription of the conversation — the most important and relevant part of the context.

Use other background information as supplemental, only if it's relevant to what was just said.

---
Live Transcript:
{transcript}

---
Relevant Background Context:
{context}

---
Generate 10 intelligent, discussion-forwarding questions that will help move the conversation forward:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": meeting_prompt.strip()}]
    )
    return response.choices[0].message.content.strip()

# Main app interface
st.title("🤝 In-Person Meeting")
st.markdown("**Your AI-powered conversation partner for live meetings and discussions**")

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    topic = st.text_input("Conversation Topic", value="meeting-discussion")
    
    if st.button("🗑️ Clear Previous Data"):
        try:
            index.delete(delete_all=True, namespace=f"it-martini-{topic}")
            st.success(f"Topic '{topic}' cleared.")
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📚 Context")
    uploaded_file = st.file_uploader("Upload Context PDF", type="pdf")
    if uploaded_file:
        try:
            pdf = PdfReader(uploaded_file)
            raw_text = "\n".join([page.extract_text() for page in pdf.pages])
            embed_and_upsert(raw_text, topic)
            st.success("PDF uploaded and embedded.")
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
    
    custom_prompt = st.text_area("Custom Prompt (optional)", height=100, 
                                placeholder="Add any specific guidance for question generation...")
    
    st.markdown("---")
    st.markdown("### 🎙️ Recording")
    start_button = st.button("Start Listening", type="primary")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Live Transcript")
    transcript_display = st.empty()
    transcript_display.markdown("*Transcript will appear here when recording...*")

with col2:
    st.header("❓ Smart Questions")
    question_display = st.empty()
    question_display.markdown("*Questions will be generated every 30 seconds...*")

# Initialize session state
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'rolling_buffer' not in st.session_state:
    st.session_state.rolling_buffer = []
if 'all_transcripts' not in st.session_state:
    st.session_state.all_transcripts = []

if start_button:
    st.session_state.listening = True
    st.session_state.rolling_buffer = []
    st.session_state.all_transcripts = []

# Live recording and question generation
if st.session_state.get("listening", False):
    try:
        while st.session_state.get("listening", False):
            st.markdown("**Recording...** 🎙️")
            
            # Record audio
            audio = sd.rec(int(RECORD_DURATION * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio_np = np.squeeze(audio)
            
            # Transcribe
            result = whisper_model.transcribe(audio_np, fp16=False)
            text = result["text"].strip()
            
            if text:
                st.session_state.all_transcripts.append(text)
                st.session_state.rolling_buffer.append(text)
                
                if len(st.session_state.rolling_buffer) > ROLLING_BUFFER_LIMIT:
                    st.session_state.rolling_buffer.pop(0)
                
                joined_text = " ".join(st.session_state.rolling_buffer)
                transcript_display.markdown("**Latest Transcript:**\n" + joined_text)
                
                # Generate questions periodically
                if len(st.session_state.all_transcripts) % ROLLING_BUFFER_LIMIT == 0:
                    questions = generate_questions(joined_text, topic, custom_prompt)
                    question_display.markdown("**🤝 Meeting Questions:**\n" + questions)
                    
                    # Store in vector database
                    embed_and_upsert(joined_text, topic)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        st.session_state.listening = False
        st.success("Recording stopped.")

# Stop button
if st.session_state.get("listening", False):
    if st.button("Stop Listening"):
        st.session_state.listening = False
        st.success("Recording stopped.")
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*In-Person Meeting Assistant - Making live conversations more engaging and insightful* 🤝")

# Deployment info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Live Recording")
st.sidebar.info("This app records live audio and generates intelligent questions every 30 seconds based on the conversation context.")
