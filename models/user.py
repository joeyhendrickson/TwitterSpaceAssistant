"""
User Management Models for Multi-User Audio Assistant
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    subscription_tier = Column(String, default=SubscriptionTier.FREE.value)
    subscription_expires = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Usage tracking
    audio_minutes_used = Column(Float, default=0.0)
    storage_mb_used = Column(Float, default=0.0)
    api_calls_used = Column(Integer, default=0)
    
    # Reset usage monthly
    usage_reset_date = Column(DateTime, default=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    app_type = Column(String, nullable=False)  # twitter_spaces, linkedin_calls, in_person
    action = Column(String, nullable=False)  # audio_recording, file_upload, question_generation
    duration_minutes = Column(Float, default=0.0)
    file_size_mb = Column(Float, default=0.0)
    api_calls = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

# Subscription tier limits
SUBSCRIPTION_LIMITS = {
    SubscriptionTier.FREE.value: {
        "audio_minutes": 30,
        "storage_mb": 100,
        "api_calls": 100,
        "price": 0
    },
    SubscriptionTier.PRO.value: {
        "audio_minutes": 300,
        "storage_mb": 1000,
        "api_calls": 1000,
        "price": 9.99
    },
    SubscriptionTier.ENTERPRISE.value: {
        "audio_minutes": 1440,  # 24 hours
        "storage_mb": 10000,
        "api_calls": 10000,
        "price": 29.99
    }
}

