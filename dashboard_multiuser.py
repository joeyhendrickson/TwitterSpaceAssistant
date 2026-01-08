"""
Multi-User Audio Assistant Dashboard
"""
import streamlit as st
import os
from dotenv import load_dotenv
import sys
import importlib.util
from auth.user_auth import init_auth, login_required
from models.user import SUBSCRIPTION_LIMITS

# Load environment variables
load_dotenv()

# Initialize authentication
init_auth()

# Page configuration
st.set_page_config(
    page_title="AI Conversation Assistant Hub - Multi-User",
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
    .subscription-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .subscription-free { background: #e9ecef; color: #6c757d; }
    .subscription-pro { background: #d4edda; color: #155724; }
    .subscription-enterprise { background: #cce5ff; color: #004085; }
</style>
""", unsafe_allow_html=True)

def show_login_page():
    """Show login/register page"""
    st.markdown("""
    <div class="main-header">
        <h1>🎤 AI Conversation Assistant Hub</h1>
        <p>Multi-User Audio Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if email and password:
                user = st.session_state.auth.authenticate_user(email, password)
                if user:
                    session_token = st.session_state.auth.create_session(user.id)
                    st.session_state.user = user
                    st.session_state.session_token = session_token
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.error("Please enter both email and password")
    
    with tab2:
        st.subheader("Create New Account")
        new_email = st.text_input("Email", key="register_email")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Register"):
            if new_email and new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    try:
                        user = st.session_state.auth.create_user(new_email, new_username, new_password)
                        st.success("Registration successful! Please log in.")
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
            else:
                st.error("Please fill in all fields")

def show_user_dashboard():
    """Show the main user dashboard"""
    user = st.session_state.user
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="main-header">
            <h1>🎤 AI Conversation Assistant Hub</h1>
            <p>Welcome back, {username}!</p>
        </div>
        """.format(username=user.username), unsafe_allow_html=True)
    
    with col2:
        subscription_class = f"subscription-{user.subscription_tier}"
        st.markdown(f"""
        <div class="subscription-badge {subscription_class}">
            {user.subscription_tier.upper()}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Logout"):
            st.session_state.auth.logout_user(st.session_state.session_token)
            st.session_state.user = None
            st.session_state.session_token = None
            st.success("Logged out successfully!")
            st.rerun()
    
    # Usage statistics
    limits = SUBSCRIPTION_LIMITS.get(user.subscription_tier, SUBSCRIPTION_LIMITS["free"])
    
    st.subheader("📊 Usage Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Audio Minutes", f"{user.audio_minutes_used:.1f}/{limits['audio_minutes']}")
    
    with col2:
        st.metric("Storage Used", f"{user.storage_mb_used:.1f}MB/{limits['storage_mb']}MB")
    
    with col3:
        st.metric("API Calls", f"{user.api_calls_used}/{limits['api_calls']}")
    
    with col4:
        if user.subscription_expires:
            st.metric("Subscription Expires", user.subscription_expires.strftime("%Y-%m-%d"))
        else:
            st.metric("Subscription", "Active")
    
    # App selection
    st.subheader("🚀 Choose Your Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="app-card">
            <div class="app-icon">🐦</div>
            <h3>Twitter Spaces Assistant</h3>
            <p>Real-time audio recording and intelligent question generation for Twitter Spaces conversations.</p>
            <div class="feature-list">
                <strong>Features:</strong>
                <ul>
                    <li>Live audio recording</li>
                    <li>Whisper AI transcription</li>
                    <li>Context-aware questions</li>
                    <li>RAG-powered insights</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Twitter Spaces Assistant", key="twitter_btn"):
            st.session_state.selected_app = "twitter_spaces"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-card">
            <div class="app-icon">💼</div>
            <h3>LinkedIn Calls Assistant</h3>
            <p>Professional conversation enhancement for LinkedIn audio calls and meetings.</p>
            <div class="feature-list">
                <strong>Features:</strong>
                <ul>
                    <li>Professional audio recording</li>
                    <li>Meeting transcription</li>
                    <li>Follow-up question generation</li>
                    <li>Business context analysis</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch LinkedIn Calls Assistant", key="linkedin_btn"):
            st.session_state.selected_app = "linkedin_calls"
            st.rerun()

def render_selected_app():
    """Render the selected app based on session state"""
    selected_app = st.session_state.get("selected_app")
    
    # Back to dashboard button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_app = None
        st.rerun()
    
    if selected_app == "twitter_spaces":
        # Import and run Twitter Spaces app with user context
        try:
            from pages.twitter_spaces_multiuser import main as twitter_main
            twitter_main()
        except ImportError as e:
            st.error(f"Error loading Twitter Spaces Assistant: {e}")
            st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"selected_app": None}))
    
    elif selected_app == "linkedin_calls":
        # Import and run LinkedIn Calls app with user context
        try:
            from pages.linkedin_calls_multiuser import main as linkedin_main
            linkedin_main()
        except ImportError as e:
            st.error(f"Error loading LinkedIn Call Assistant: {e}")
            st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"selected_app": None}))

def main():
    # Check if user is logged in
    if not st.session_state.get("user"):
        show_login_page()
        return
    
    # Check if an app is selected
    if st.session_state.get("selected_app"):
        render_selected_app()
        return
    
    # Show main dashboard
    show_user_dashboard()

if __name__ == "__main__":
    main()



