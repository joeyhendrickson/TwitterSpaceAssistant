import os
import streamlit as st
import whisper
import sounddevice as sd
import numpy as np
import time
from uuid import uuid4
from PyPDF2 import PdfReader
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

# --- LOAD .env VARIABLES ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV", "us-east-1")

# --- INIT OPENAI + PINECONE ---
client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)

# Twitter Space specific index - use shared index with namespace
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

# --- CONFIG ---
RECORD_DURATION = 5
ROLLING_BUFFER_LIMIT = 12
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
        }], namespace=f"twitter-space-{topic}")

def query_context(query, topic):
    vector = get_embedding(query)
    response = index.query(vector=vector, top_k=5, include_metadata=True, namespace=f"twitter-space-{topic}")
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
    full_prompt = f"""
You are an expert assistant listening to a live conversation. Your goal is to generate 7 intelligent, context-specific questions that will help the speaker (me) sound informed and drive the conversation forward.

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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt.strip()}]
    )
    return response.choices[0].message.content.strip()

# --- STREAMLIT UI ---
st.title("Twitter Space AI Assistant")

topic = st.text_input("Enter topic (used as namespace)", value="default")

if st.button("Clear Previous Data for This Topic"):
    index.delete(delete_all=True, namespace=f"twitter-space-{topic}")
    st.success(f"Namespace '{topic}' cleared.")

uploaded_file = st.file_uploader("Upload Context PDF", type="pdf")
if uploaded_file:
    pdf = PdfReader(uploaded_file)
    raw_text = "\n".join([page.extract_text() for page in pdf.pages])
    embed_and_upsert(raw_text, topic)
    st.success("PDF uploaded and embedded.")

custom_prompt = st.text_area("Optional prompt (will guide question generation)", height=150)

start_button = st.button("Start Listening")

transcript_display = st.empty()
question_display = st.empty()

rolling_buffer = []
all_transcripts = []

if start_button:
    st.session_state.listening = True

if st.session_state.get("listening", False):
    try:
        while True:
            st.markdown("**Recording...**")
            audio = sd.rec(int(RECORD_DURATION * 16000), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            audio_np = np.squeeze(audio)
            result = whisper_model.transcribe(audio_np, fp16=False)
            text = result["text"].strip()
            all_transcripts.append(text)
            rolling_buffer.append(text)
            if len(rolling_buffer) > ROLLING_BUFFER_LIMIT:
                rolling_buffer.pop(0)
            joined_text = " ".join(rolling_buffer)
            transcript_display.markdown("**Latest Transcript:**\n" + joined_text)

            if len(all_transcripts) % ROLLING_BUFFER_LIMIT == 0:
                summarize_and_append(joined_text, topic)
                questions = generate_questions(joined_text, topic, custom_prompt)
                question_display.markdown("**Smart Questions:**\n" + questions)

            time.sleep(1)
    except KeyboardInterrupt:
        st.session_state.listening = False
        st.success("Stopped listening.")