"""
User Authentication System for Multi-User Audio Assistant
"""
import os
import secrets
import streamlit as st
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from models.user import User, UserSession, UsageLog, SUBSCRIPTION_LIMITS
import redis

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/audio_assistant")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis for session management
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

class UserAuth:
    def __init__(self):
        self.db = SessionLocal()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_user(self, email: str, username: str, password: str) -> User:
        """Create a new user"""
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_session(self, user_id: int) -> str:
        """Create a new session for a user"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Store in database
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        
        # Store in Redis for fast access
        redis_client.setex(
            f"session:{session_token}",
            timedelta(days=7),
            str(user_id)
        )
        
        return session_token
    
    def get_user_from_session(self, session_token: str) -> User:
        """Get user from session token"""
        # Try Redis first
        user_id = redis_client.get(f"session:{session_token}")
        if user_id:
            user_id = int(user_id.decode())
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                return user
        
        # Fallback to database
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if session:
            user = self.db.query(User).filter(User.id == session.user_id).first()
            if user and user.is_active:
                # Update Redis
                redis_client.setex(
                    f"session:{session_token}",
                    timedelta(days=7),
                    str(user.id)
                )
                return user
        
        return None
    
    def logout_user(self, session_token: str):
        """Logout a user by invalidating their session"""
        # Remove from Redis
        redis_client.delete(f"session:{session_token}")
        
        # Remove from database
        self.db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).delete()
        self.db.commit()
    
    def check_usage_limits(self, user_id: int, action: str, **kwargs) -> bool:
        """Check if user has exceeded their usage limits"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Reset usage if it's a new month
        if user.usage_reset_date.month != datetime.utcnow().month:
            user.audio_minutes_used = 0.0
            user.storage_mb_used = 0.0
            user.api_calls_used = 0
            user.usage_reset_date = datetime.utcnow()
            self.db.commit()
        
        limits = SUBSCRIPTION_LIMITS.get(user.subscription_tier, SUBSCRIPTION_LIMITS["free"])
        
        # Check specific limits
        if action == "audio_recording":
            duration = kwargs.get("duration_minutes", 0)
            if user.audio_minutes_used + duration > limits["audio_minutes"]:
                return False
        
        elif action == "file_upload":
            file_size = kwargs.get("file_size_mb", 0)
            if user.storage_mb_used + file_size > limits["storage_mb"]:
                return False
        
        elif action == "api_call":
            if user.api_calls_used + 1 > limits["api_calls"]:
                return False
        
        return True
    
    def log_usage(self, user_id: int, app_type: str, action: str, **kwargs):
        """Log user usage"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        # Update user usage
        if action == "audio_recording":
            duration = kwargs.get("duration_minutes", 0)
            user.audio_minutes_used += duration
        
        elif action == "file_upload":
            file_size = kwargs.get("file_size_mb", 0)
            user.storage_mb_used += file_size
        
        elif action == "api_call":
            user.api_calls_used += 1
        
        # Log usage
        usage_log = UsageLog(
            user_id=user_id,
            app_type=app_type,
            action=action,
            duration_minutes=kwargs.get("duration_minutes", 0),
            file_size_mb=kwargs.get("file_size_mb", 0),
            api_calls=kwargs.get("api_calls", 1)
        )
        
        self.db.add(usage_log)
        self.db.commit()

# Streamlit authentication wrapper
def init_auth():
    """Initialize authentication in Streamlit session state"""
    if "auth" not in st.session_state:
        st.session_state.auth = UserAuth()
    if "user" not in st.session_state:
        st.session_state.user = None
    if "session_token" not in st.session_state:
        st.session_state.session_token = None

def login_required(func):
    """Decorator to require login for functions"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("user"):
            st.error("Please log in to access this feature.")
            return
        return func(*args, **kwargs)
    return wrapper



