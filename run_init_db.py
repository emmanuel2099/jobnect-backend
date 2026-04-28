"""
Simple script to run database initialization
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db

if __name__ == "__main__":
    print("🚀 Initializing database with master data...")
    init_db()
    print("✅ Database initialization complete!")
