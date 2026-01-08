import streamlit as st
import os
from dotenv import load_dotenv
import sys
import importlib.util

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Conversation Assistant Hub",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .app-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #1da1f2;
        transition: transform 0.2s;
    }
    .app-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .app-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-list {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def render_selected_app():
    """Render the selected app based on session state"""
    selected_app = st.session_state.get("selected_app")
    
    # Back to dashboard button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_app = None
        st.rerun()
    
    if selected_app == "twitter_spaces":
        # Import and run Twitter Spaces app
        try:
            from pages.twitter_spaces import main as twitter_main
            twitter_main()
        except ImportError as e:
            st.error(f"Error loading Twitter Spaces Assistant: {e}")
            st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"selected_app": None}))
    
    elif selected_app == "linkedin_calls":
        # Import and run LinkedIn Calls app
        try:
            from pages.linkedin_calls import main as linkedin_main
            linkedin_main()
        except ImportError as e:
            st.error(f"Error loading LinkedIn Call Assistant: {e}")
            st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"selected_app": None}))
    
    elif selected_app == "interview_prep":
        # Import and run Interview Prep app
        try:
            from pages.interview_prep import main as interview_main
            interview_main()
        except ImportError as e:
            st.error(f"Error loading Interview Preparation Assistant: {e}")
            st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"selected_app": None}))

def main():
    # Check if an app is selected
    if st.session_state.get("selected_app"):
        render_selected_app()
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 AI Conversation Assistant Hub</h1>
        <p>Choose your conversation enhancement tool</p>
    </div>
    """, unsafe_allow_html=True)
    
    # App selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="app-card">
            <div class="app-icon">🐦</div>
            <h2>Twitter Spaces Assistant</h2>
            <p>Enhance your live Twitter Spaces conversations with real-time AI-powered insights and intelligent follow-up questions.</p>
            <div class="feature-list">
                <strong>Features:</strong>
                <ul>
                    <li>Real-time audio transcription</li>
                    <li>Context-aware question generation</li>
                    <li>PDF document integration</li>
                    <li>Topic-based conversation memory</li>
                    <li>Smart conversation summaries</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch Twitter Spaces Assistant", key="twitter_spaces", use_container_width=True):
            st.session_state.selected_app = "twitter_spaces"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-card">
            <div class="app-icon">💼</div>
            <h2>LinkedIn Call Assistant</h2>
            <p>Prepare for professional calls by analyzing LinkedIn profiles and social media to generate personalized conversation insights.</p>
            <div class="feature-list">
                <strong>Features:</strong>
                <ul>
                    <li>LinkedIn profile analysis</li>
                    <li>Social media personality insights</li>
                    <li>Personalized conversation prompts</li>
                    <li>Call goal integration</li>
                    <li>Real-time question generation</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch LinkedIn Call Assistant", key="linkedin_calls", use_container_width=True):
            st.session_state.selected_app = "linkedin_calls"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="app-card">
            <div class="app-icon">🎯</div>
            <h2>Interview Preparation</h2>
            <p>Analyze your resume and get personalized interview preparation with practice questions and strategic insights.</p>
            <div class="feature-list">
                <strong>Features:</strong>
                <ul>
                    <li>Resume analysis and extraction</li>
                    <li>Interview question generation</li>
                    <li>STAR method examples</li>
                    <li>Strengths and weaknesses analysis</li>
                    <li>Job-specific preparation</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch Interview Prep", key="interview_prep", use_container_width=True):
            st.session_state.selected_app = "interview_prep"
            st.rerun()
    
    # Additional info
    st.markdown("---")
    st.markdown("""
    ### 🎯 How It Works
    
    **Twitter Spaces Assistant**: Perfect for live streaming, podcasting, and public speaking. 
    Upload context documents, set your topic, and get real-time intelligent questions during your conversation.
    
    **LinkedIn Call Assistant**: Ideal for sales calls, networking, and professional meetings.
    Analyze your contact's digital footprint to create personalized conversation strategies.
    
    **Interview Preparation**: Upload your resume and get comprehensive interview preparation including practice questions, 
    STAR method examples, and strategic talking points tailored to your experience and target job.
    
    All assistants use advanced AI to help you sound more informed and engaging in any conversation.
    """)

if __name__ == "__main__":
    main() 