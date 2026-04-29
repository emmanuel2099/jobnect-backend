"""
Database migration script to ensure all required columns exist
This will run automatically when the app starts
"""

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations to ensure all required columns exist"""
    
    try:
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        logger.info("🔄 Running database migrations...")
        
        with engine.connect() as connection:
            # Check if jobs_applied column exists in subscriptions table
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'subscriptions' 
                AND column_name = 'jobs_applied'
            """))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                # Add the missing jobs_applied column
                logger.info("📝 Adding jobs_applied column to subscriptions table...")
                connection.execute(text("""
                    ALTER TABLE subscriptions 
                    ADD COLUMN jobs_applied INTEGER DEFAULT 0
                """))
                connection.commit()
                logger.info("✅ jobs_applied column added successfully!")
            else:
                logger.info("✅ jobs_applied column already exists")
                
            # Verify other required columns if needed
            # Add more migrations here as needed
            
        logger.info("✅ Database migrations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error running migrations: {e}")
        return False

# Auto-run migrations when this file is imported
if __name__ == "__main__":
    run_migrations()
