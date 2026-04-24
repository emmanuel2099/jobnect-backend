"""
Complete setup script for payment system
Run this after deploying to initialize everything
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import SubscriptionPlan, JobCategory

def setup_payment_system():
    """Complete setup for payment system"""
    
    print("=" * 60)
    print("🚀 JOBNECT PAYMENT SYSTEM SETUP")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Step 1: Create tables
        print("\n📋 Step 1: Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Step 2: Create subscription plans
        print("\n💰 Step 2: Setting up subscription plans...")
        
        existing_plans = db.query(SubscriptionPlan).count()
        if existing_plans > 0:
            print(f"✓ Subscription plans already exist ({existing_plans} plans)")
        else:
            plans = [
                SubscriptionPlan(
                    name="Low Tier Subscription",
                    tier="low",
                    price=3000.0,
                    duration_months=2,
                    description="Access to low-tier jobs for 2 months. ₦3,000",
                    is_active=True
                ),
                SubscriptionPlan(
                    name="High Tier Subscription",
                    tier="high",
                    price=8000.0,
                    duration_months=2,
                    description="Full access to all jobs for 2 months. ₦8,000",
                    is_active=True
                )
            ]
            
            for plan in plans:
                db.add(plan)
            
            db.commit()
            print("✅ Subscription plans created:")
            print("   - Low Tier: ₦3,000 for 2 months")
            print("   - High Tier: ₦8,000 for 2 months")
        
        # Step 3: Add job categories
        print("\n📂 Step 3: Adding job categories...")
        
        categories_to_add = [
            # Low Tier
            {"name": "Delivery Driver", "tier": "low", "icon": "🚗"},
            {"name": "Warehouse Worker", "tier": "low", "icon": "📦"},
            {"name": "Factory Worker", "tier": "low", "icon": "🏭"},
            {"name": "Retail Sales", "tier": "low", "icon": "🛍️"},
            {"name": "Hospitality", "tier": "low", "icon": "🏨"},
            {"name": "Housekeeper", "tier": "low", "icon": "🧹"},
            {"name": "Gardener", "tier": "low", "icon": "🌱"},
            {"name": "Nanny/Caregiver", "tier": "low", "icon": "👶"},
            {"name": "Cashier", "tier": "low", "icon": "💰"},
            {"name": "Food Service", "tier": "low", "icon": "🍽️"},
            
            # High Tier
            {"name": "Software Development", "tier": "high", "icon": "💻"},
            {"name": "Data Science", "tier": "high", "icon": "📊"},
            {"name": "IT Support", "tier": "high", "icon": "🖥️"},
            {"name": "Project Management", "tier": "high", "icon": "📋"},
            {"name": "Business Development", "tier": "high", "icon": "📈"},
            {"name": "Human Resources", "tier": "high", "icon": "👥"},
            {"name": "Accounting", "tier": "high", "icon": "🧮"},
            {"name": "Banking", "tier": "high", "icon": "🏦"},
            {"name": "Architecture", "tier": "high", "icon": "🏗️"},
            {"name": "Consulting", "tier": "high", "icon": "💼"},
            {"name": "Medical/Healthcare", "tier": "high", "icon": "⚕️"},
            {"name": "Executive/Management", "tier": "high", "icon": "👔"},
        ]
        
        added = 0
        updated = 0
        
        for cat_data in categories_to_add:
            existing = db.query(JobCategory).filter(
                JobCategory.name == cat_data["name"]
            ).first()
            
            if existing:
                if existing.tier != cat_data["tier"]:
                    existing.tier = cat_data["tier"]
                    existing.icon = cat_data["icon"]
                    updated += 1
            else:
                category = JobCategory(
                    name=cat_data["name"],
                    tier=cat_data["tier"],
                    icon=cat_data["icon"],
                    description=f"{cat_data['name']} jobs",
                    is_active=True
                )
                db.add(category)
                added += 1
        
        # Update existing categories with tier
        low_tier_keywords = [
            "Teacher", "Driver", "Cleaner", "Security", "Cook", 
            "Waiter", "Receptionist", "Sales", "Customer"
        ]
        
        high_tier_keywords = [
            "Technology", "Engineering", "Finance", "Management", 
            "Healthcare", "Legal", "Marketing", "Design"
        ]
        
        all_categories = db.query(JobCategory).all()
        for cat in all_categories:
            if not hasattr(cat, 'tier') or not cat.tier:
                # Assign tier based on name
                is_low = any(keyword.lower() in cat.name.lower() for keyword in low_tier_keywords)
                is_high = any(keyword.lower() in cat.name.lower() for keyword in high_tier_keywords)
                
                if is_high:
                    cat.tier = "high"
                    updated += 1
                elif is_low:
                    cat.tier = "low"
                    updated += 1
                else:
                    cat.tier = "low"  # Default to low
                    updated += 1
        
        db.commit()
        
        print(f"✅ Categories updated:")
        print(f"   Added: {added} new categories")
        print(f"   Updated: {updated} existing categories")
        
        # Step 4: Show summary
        print("\n" + "=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        
        total_plans = db.query(SubscriptionPlan).count()
        total_categories = db.query(JobCategory).count()
        low_tier_cats = db.query(JobCategory).filter(JobCategory.tier == "low").count()
        high_tier_cats = db.query(JobCategory).filter(JobCategory.tier == "high").count()
        
        print(f"\n✅ Subscription Plans: {total_plans}")
        print(f"   - Low Tier (₦3,000): 2 months access to low-tier jobs")
        print(f"   - High Tier (₦8,000): 2 months access to all jobs")
        
        print(f"\n✅ Job Categories: {total_categories}")
        print(f"   - Low Tier: {low_tier_cats} categories")
        print(f"   - High Tier: {high_tier_cats} categories")
        
        print("\n✅ Free Trial: Companies get 3 free job posts")
        print("✅ Job Seekers: Must subscribe to apply")
        
        print("\n" + "=" * 60)
        print("🎉 PAYMENT SYSTEM READY!")
        print("=" * 60)
        
        print("\n📝 Next Steps:")
        print("1. Test API endpoints:")
        print("   GET /api/v10/subscriptions/plans")
        print("   POST /api/v10/subscriptions/check-access")
        print("\n2. Configure Flutterwave webhook:")
        print("   URL: https://your-backend.com/api/v10/subscriptions/webhook/flutterwave")
        print("\n3. Test payment flow with test cards")
        print("\n4. Implement Flutter UI for payments")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_payment_system()
