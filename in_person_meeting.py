# In-Person Meeting Assistant
# Renamed from it_martini.py to in_person_meeting.py

import os
import streamlit as st
import time
from uuid import uuid4
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json
import datetime
from collections import defaultdict

# --- STREAMLIT UI ---
st.set_page_config(
    page_title="In-Person Meeting", 
    page_icon="🤝", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    # In-Person Meeting specific index - use shared index with namespace
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
ROLLING_BUFFER_LIMIT = 6  # Generate questions every 6 conversation chunks

# --- BACKGROUND ONTOLOGY PROCESSING ---
class MeetingOntologyProcessor:
    def __init__(self):
        self.entities = defaultdict(int)
        self.topics = defaultdict(int)
        self.relationships = []
        self.conversation_flow = []
        self.question_logic = []
        self.meeting_start_time = None
        
    def extract_entities_and_topics(self, text):
        """Extract entities and topics from conversation text"""
        try:
            prompt = f"""
            Extract key entities and topics from this conversation text. Return as JSON:
            
            Text: {text}
            
            Return format:
            {{
                "entities": ["entity1", "entity2"],
                "topics": ["topic1", "topic2"],
                "key_concepts": ["concept1", "concept2"]
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Try to parse JSON, fallback to simple extraction if it fails
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # Fallback: simple keyword extraction
                words = text.lower().split()
                common_topics = ["meeting", "project", "team", "client", "budget", "timeline", "strategy"]
                found_topics = [word for word in words if word in common_topics]
                return {
                    "entities": [],
                    "topics": found_topics[:3],
                    "key_concepts": []
                }
        except Exception as e:
            # Return empty result if everything fails
            return {"entities": [], "topics": [], "key_concepts": []}
    
    def analyze_question_reasoning(self, conversation_text, generated_questions, context):
        """Analyze why specific questions were generated"""
        try:
            prompt = f"""
            Explain the reasoning behind generating these questions based on the conversation context.
            
            Conversation: {conversation_text}
            Generated Questions: {generated_questions}
            Context: {context}
            
            Return as JSON:
            {{
                "reasoning": "explanation of why these questions were chosen",
                "key_triggers": ["trigger1", "trigger2"],
                "context_usage": "how previous context influenced questions",
                "timing_factors": "why these questions at this time"
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Try to parse JSON, fallback to simple reasoning if it fails
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # Fallback: simple reasoning
                return {
                    "reasoning": f"Questions generated based on conversation about: {conversation_text[:100]}...",
                    "key_triggers": ["conversation context"],
                    "context_usage": "Previous context used to inform question generation",
                    "timing_factors": "Questions generated when conversation context was available"
                }
        except Exception as e:
            return {"reasoning": "Analysis failed", "key_triggers": [], "context_usage": "", "timing_factors": ""}
    
    def process_conversation_chunk(self, text, timestamp=None):
        """Process a conversation chunk and update ontology"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        # Extract entities and topics
        extracted = self.extract_entities_and_topics(text)
        
        # Update entity and topic counts
        for entity in extracted.get("entities", []):
            self.entities[entity] += 1
        for topic in extracted.get("topics", []):
            self.topics[topic] += 1
        
        # Add to conversation flow
        self.conversation_flow.append({
            "timestamp": timestamp.isoformat(),
            "text": text,
            "entities": extracted.get("entities", []),
            "topics": extracted.get("topics", []),
            "concepts": extracted.get("key_concepts", [])
        })
        
        # Build relationships
        entities = extracted.get("entities", [])
        topics = extracted.get("topics", [])
        for entity in entities:
            for topic in topics:
                self.relationships.append({
                    "from": entity,
                    "to": topic,
                    "relationship": "discussed_in",
                    "timestamp": timestamp.isoformat()
                })
    
    def record_question_generation(self, conversation_text, questions, context, reasoning):
        """Record question generation with reasoning"""
        self.question_logic.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "conversation_context": conversation_text,
            "generated_questions": questions,
            "background_context": context,
            "reasoning": reasoning
        })
    
    def generate_meeting_analytics(self):
        """Generate comprehensive meeting analytics"""
        return {
            "meeting_summary": {
                "start_time": self.meeting_start_time.isoformat() if self.meeting_start_time else None,
                "end_time": datetime.datetime.now().isoformat(),
                "total_chunks": len(self.conversation_flow),
                "total_questions": len(self.question_logic)
            },
            "entity_analysis": dict(self.entities),
            "topic_analysis": dict(self.topics),
            "conversation_flow": self.conversation_flow,
            "relationships": self.relationships,
            "question_logic": self.question_logic
        }
    
    def start_meeting(self):
        """Start a new meeting session"""
        self.meeting_start_time = datetime.datetime.now()
        self.entities.clear()
        self.topics.clear()
        self.relationships.clear()
        self.conversation_flow.clear()
        self.question_logic.clear()

# Initialize ontology processor
if 'ontology_processor' not in st.session_state:
    st.session_state.ontology_processor = MeetingOntologyProcessor()

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
    st.header("🎛️ In-Person Meeting Controls")
    
    topic = st.text_input("Meeting Topic", value="meeting-discussion")
    
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
    
    custom_prompt = st.text_area("Meeting Guidance (optional)", height=100, 
                                placeholder="Add any specific guidance for question generation...")
    
    st.markdown("---")
    st.markdown("### 🎙️ Meeting Input")
    st.info("💡 **Web Version**: Use the browser microphone or type conversation text")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Meeting Input")
    
    # Browser microphone input
    st.subheader("🎤 Audio Input")
    st.info("""
    **For live audio recording:**
    1. Use your device's voice-to-text feature
    2. Copy the transcribed text
    3. Paste it in the text area below
    4. Click "Generate Questions"
    """)
    
    # File uploader for audio files (alternative)
    st.subheader("📁 Upload Audio File")
    uploaded_audio = st.file_uploader(
        "Upload audio file (MP3, WAV, M4A)",
        type=['mp3', 'wav', 'm4a'],
        help="Upload an audio recording of your conversation"
    )
    
    if uploaded_audio:
        st.success(f"✅ Audio file uploaded: {uploaded_audio.name}")
        st.info("💡 Audio transcription will be added in a future update")
    
    # Manual text input as fallback
    st.subheader("📝 Manual Text Input")
    conversation_text = st.text_area(
        "Or type/paste meeting text here:",
        height=150,
        placeholder="Enter meeting text here...\n\nExample: We were discussing the project timeline and how to best allocate resources..."
    )
    
    # Process input
    if uploaded_audio or conversation_text:
        if st.button("🤝 Generate Questions", type="primary"):
            with st.spinner("Generating intelligent questions..."):
                try:
                    # For now, use manual text input
                    # TODO: Add audio transcription service
                    text_to_process = conversation_text if conversation_text else f"Audio file uploaded: {uploaded_audio.name} (transcription pending)"
                    
                    # Start meeting if not already started
                    if not st.session_state.ontology_processor.meeting_start_time:
                        st.session_state.ontology_processor.start_meeting()
                    
                    # Background ontology processing
                    st.session_state.ontology_processor.process_conversation_chunk(text_to_process)
                    
                    # Store conversation context
                    embed_and_upsert(text_to_process, topic)
                    
                    # Get context for question generation
                    context = query_context(text_to_process, topic)
                    
                    # Generate questions
                    questions = generate_questions(text_to_process, topic, custom_prompt)
                    
                    # Analyze question reasoning (background)
                    reasoning = st.session_state.ontology_processor.analyze_question_reasoning(
                        text_to_process, questions, context
                    )
                    
                    # Record question generation with reasoning
                    st.session_state.ontology_processor.record_question_generation(
                        text_to_process, questions, context, reasoning
                    )
                    
                    # Store in session state
                    st.session_state.last_questions = questions
                    st.session_state.last_conversation = text_to_process
                    
                    st.success("Questions generated successfully!")
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")

with col2:
    st.header("❓ Smart Questions")
    
    if 'last_questions' in st.session_state:
        st.markdown("**🤝 Meeting Questions:**")
        st.markdown(st.session_state.last_questions)
        
        # Show the conversation that was analyzed
        with st.expander("📝 Analyzed Meeting"):
            st.text(st.session_state.last_conversation)
    else:
        st.markdown("*Questions will appear here after you generate them...*")

# Analytics Download Section
st.markdown("---")
st.header("📊 Meeting Analytics")

if st.session_state.ontology_processor.meeting_start_time:
    st.success(f"✅ Meeting in progress since {st.session_state.ontology_processor.meeting_start_time.strftime('%H:%M:%S')}")
    
    # Show analytics summary
    analytics = st.session_state.ontology_processor.generate_meeting_analytics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Meeting Chunks", analytics["meeting_summary"]["total_chunks"])
    with col2:
        st.metric("Questions Generated", analytics["meeting_summary"]["total_questions"])
    with col3:
        st.metric("Topics Identified", len(analytics["topic_analysis"]))
    
    # Download analytics
    if st.button("📥 Download Meeting Analytics"):
        try:
            # Generate analytics data
            analytics_data = st.session_state.ontology_processor.generate_meeting_analytics()
            
            # Create JSON file for download
            analytics_json = json.dumps(analytics_data, indent=2)
            
            # Create download button
            st.download_button(
                label="📄 Download Analytics (JSON)",
                data=analytics_json,
                file_name=f"meeting_analytics_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            # Show analytics preview
            with st.expander("🔍 Analytics Preview"):
                st.json(analytics_data)
                
        except Exception as e:
            st.error(f"Error generating analytics: {str(e)}")
else:
    st.info("💡 Start generating questions to begin meeting analytics tracking")

# Footer
st.markdown("---")
st.markdown("*In-Person Meeting Assistant - Making live conversations more engaging and insightful* 🤝")

# Deployment info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Meeting Assistant")
st.sidebar.info("This app processes meeting content and generates intelligent questions based on the discussion context.")
