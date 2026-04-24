"""
Add more job categories to the database
"""
from app.database import SessionLocal, engine, Base
from app.models import JobCategory

def add_more_categories():
    db = SessionLocal()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # New categories to add
        new_categories = [
            # Low Tier Categories (₦3,000)
            {"name": "Delivery Driver", "tier": "low", "icon": "🚗", "description": "Delivery and courier services"},
            {"name": "Warehouse Worker", "tier": "low", "icon": "📦", "description": "Warehouse and logistics"},
            {"name": "Factory Worker", "tier": "low", "icon": "🏭", "description": "Manufacturing and production"},
            {"name": "Retail Sales", "tier": "low", "icon": "🛍️", "description": "Retail and shop assistant"},
            {"name": "Hospitality", "tier": "low", "icon": "🏨", "description": "Hotel and restaurant services"},
            {"name": "Housekeeper", "tier": "low", "icon": "🧹", "description": "Cleaning and housekeeping"},
            {"name": "Gardener", "tier": "low", "icon": "🌱", "description": "Gardening and landscaping"},
            {"name": "Nanny/Caregiver", "tier": "low", "icon": "👶", "description": "Childcare and elderly care"},
            {"name": "Cashier", "tier": "low", "icon": "💰", "description": "Cashier and payment processing"},
            {"name": "Food Service", "tier": "low", "icon": "🍽️", "description": "Restaurant and food service"},
            
            # High Tier Categories (₦8,000)
            {"name": "Software Development", "tier": "high", "icon": "💻", "description": "Software engineering and development"},
            {"name": "Data Science", "tier": "high", "icon": "📊", "description": "Data analysis and machine learning"},
            {"name": "IT Support", "tier": "high", "icon": "🖥️", "description": "IT and technical support"},
            {"name": "Project Management", "tier": "high", "icon": "📋", "description": "Project and program management"},
            {"name": "Business Development", "tier": "high", "icon": "📈", "description": "Business growth and strategy"},
            {"name": "Human Resources", "tier": "high", "icon": "👥", "description": "HR and recruitment"},
            {"name": "Accounting", "tier": "high", "icon": "🧮", "description": "Accounting and bookkeeping"},
            {"name": "Banking", "tier": "high", "icon": "🏦", "description": "Banking and financial services"},
            {"name": "Architecture", "tier": "high", "icon": "🏗️", "description": "Architecture and construction"},
            {"name": "Consulting", "tier": "high", "icon": "💼", "description": "Business and management consulting"},
            {"name": "Medical/Healthcare", "tier": "high", "icon": "⚕️", "description": "Medical and healthcare professionals"},
            {"name": "Executive/Management", "tier": "high", "icon": "👔", "description": "Executive and senior management"},
        ]
        
        added_count = 0
        updated_count = 0
        
        for cat_data in new_categories:
            # Check if category already exists
            existing = db.query(JobCategory).filter(JobCategory.name == cat_data["name"]).first()
            
            if existing:
                # Update tier if needed
                if existing.tier != cat_data["tier"]:
                    existing.tier = cat_data["tier"]
                    existing.icon = cat_data["icon"]
                    existing.description = cat_data["description"]
                    updated_count += 1
                    print(f"  ✓ Updated: {cat_data['name']} ({cat_data['tier']} tier)")
            else:
                # Add new category
                category = JobCategory(
                    name=cat_data["name"],
                    tier=cat_data["tier"],
                    icon=cat_data["icon"],
                    description=cat_data["description"],
                    is_active=True
                )
                db.add(category)
                added_count += 1
                print(f"  + Added: {cat_data['name']} ({cat_data['tier']} tier)")
        
        db.commit()
        
        # Show summary
        total_categories = db.query(JobCategory).count()
        low_tier = db.query(JobCategory).filter(JobCategory.tier == "low").count()
        high_tier = db.query(JobCategory).filter(JobCategory.tier == "high").count()
        
        print(f"\n✅ Categories updated successfully!")
        print(f"   Added: {added_count} new categories")
        print(f"   Updated: {updated_count} existing categories")
        print(f"\n📊 Total Categories: {total_categories}")
        print(f"   Low Tier (₦3,000): {low_tier} categories")
        print(f"   High Tier (₦8,000): {high_tier} categories")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding more job categories...\n")
    add_more_categories()
    print("\nDone!")
