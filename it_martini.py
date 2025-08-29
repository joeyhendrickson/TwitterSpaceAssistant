import os
import streamlit as st
import time
from uuid import uuid4
from PyPDF2 import PdfReader
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

# --- STREAMLIT UI ---
st.set_page_config(page_title="IT Martini", page_icon="🍸", layout="wide")

# --- LOAD .env VARIABLES ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV", "us-east-1")
pinecone_index_name = "it-martini-web"

# --- INIT OPENAI + PINECONE ---
client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)

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
        }], namespace=topic)

def query_context(query, topic):
    vector = get_embedding(query)
    response = index.query(vector=vector, top_k=5, include_metadata=True, namespace=topic)
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
    
    # Technology-focused prompt for IT Martini
    tech_prompt = f"""
You are IT Martini, an expert technology conversation assistant. You're listening to a live technology conversation and need to generate 10 intelligent, technology-focused questions that will help drive the conversation forward.

Focus on:
- Current technology trends and innovations
- Technical challenges and solutions
- Industry insights and best practices
- Emerging technologies and their implications
- Practical applications and use cases

Put primary emphasis on the most recent transcription of the conversation — the most important and relevant part of the context.

Use other background information as supplemental, only if it's relevant to what was just said.

---
Live Transcript:
{transcript}

---
Relevant Background Context:
{context}

---
Generate 10 intelligent, technology-focused questions that will help move the conversation forward:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": tech_prompt.strip()}]
    )
    return response.choices[0].message.content.strip()

st.title("🍸 IT Martini")
st.markdown("**Your AI-powered conversation partner for technology discussions**")

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    topic = st.text_input("Conversation Topic", value="technology-discussion")
    
    if st.button("🗑️ Clear Previous Data"):
        index.delete(delete_all=True, namespace=topic)
        st.success(f"Topic '{topic}' cleared.")
    
    st.markdown("---")
    st.markdown("### 📚 Context")
    uploaded_file = st.file_uploader("Upload Context PDF", type="pdf")
    if uploaded_file:
        pdf = PdfReader(uploaded_file)
        raw_text = "\n".join([page.extract_text() for page in pdf.pages])
        embed_and_upsert(raw_text, topic)
        st.success("PDF uploaded and embedded.")
    
    custom_prompt = st.text_area("Custom Prompt (optional)", height=100, 
                                placeholder="Add any specific guidance for question generation...")
    
    st.markdown("---")
    st.markdown("### 💬 Conversation Input")
    st.info("💡 **Web Version**: Type your conversation text instead of recording audio")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Conversation Input")
    
    # Text input for conversation
    conversation_text = st.text_area(
        "Type or paste your technology conversation here:",
        height=200,
        placeholder="Enter your technology conversation text here...\n\nExample: We were discussing the impact of AI on software development and how it's changing the way teams collaborate..."
    )
    
    if st.button("🍸 Generate Questions", type="primary"):
        if conversation_text.strip():
            with st.spinner("Generating intelligent questions..."):
                # Store conversation context
                embed_and_upsert(conversation_text, topic)
                
                # Generate questions
                questions = generate_questions(conversation_text, topic, custom_prompt)
                
                # Store in session state
                st.session_state.last_questions = questions
                st.session_state.last_conversation = conversation_text
                
            st.success("Questions generated successfully!")
        else:
            st.error("Please enter some conversation text first.")

with col2:
    st.header("Generator")
    
    if 'last_questions' in st.session_state:
        st.markdown("**🍸 IT Martini Questions:**")
        st.markdown(st.session_state.last_questions)
        
        # Show the conversation that was analyzed
        with st.expander("📝 Analyzed Conversation"):
            st.text(st.session_state.last_conversation)
    else:
        st.markdown("*Questions will appear here after you generate them...*")

# Footer
st.markdown("---")
st.markdown("*IT Martini - Making technology conversations more engaging and insightful* 🍸")

# Deployment info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Web Version")
st.sidebar.info("This is the web deployment version of IT Martini. For audio recording, use the local version.")
