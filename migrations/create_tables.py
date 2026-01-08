"""
Database Migration Script for Multi-User Audio Assistant
"""
import os
import sys
from sqlalchemy import create_engine, text
from models.user import Base

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_database_tables():
    """Create all database tables"""
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All database tables created successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            # Check if users table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'user_sessions', 'usage_logs')
            """))
            
            tables = [row[0] for row in result]
            print(f"✅ Created tables: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def create_indexes():
    """Create database indexes for better performance"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Create indexes for better query performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)",
                "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_usage_logs_app_type ON usage_logs(app_type)"
            ]
            
            for index_sql in indexes:
                conn.execute(text(index_sql))
            
            conn.commit()
            print("✅ Database indexes created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database indexes: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        from auth.user_auth import UserAuth
        from models.user import SubscriptionTier
        
        auth = UserAuth()
        
        # Create a sample admin user
        try:
            admin_user = auth.create_user(
                email="admin@example.com",
                username="admin",
                password="admin123"
            )
            print("✅ Sample admin user created: admin@example.com / admin123")
        except Exception as e:
            print(f"⚠️ Admin user already exists or error: {e}")
        
        # Create a sample regular user
        try:
            regular_user = auth.create_user(
                email="user@example.com",
                username="demo_user",
                password="user123"
            )
            print("✅ Sample user created: user@example.com / user123")
        except Exception as e:
            print(f"⚠️ Regular user already exists or error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Multi-User Audio Assistant Database")
    print("=" * 50)
    
    # Create tables
    if create_database_tables():
        # Create indexes
        if create_indexes():
            # Create sample data
            create_sample_data()
            
            print("\n✅ Database setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Deploy to Railway")
            print("2. Set environment variables:")
            print("   - DATABASE_URL")
            print("   - REDIS_URL")
            print("   - OPENAI_API_KEY")
            print("   - PINECONE_API_KEY")
            print("   - PINECONE_ENV")
            print("3. Access your app and log in with sample credentials")
        else:
            print("❌ Failed to create database indexes")
    else:
        print("❌ Failed to create database tables")



