"""
Initialize subscription plans in the database
"""
from app.database import SessionLocal, engine, Base
from app.models import SubscriptionPlan, JobCategory

def init_subscription_plans():
    db = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Check if plans already exist
        existing = db.query(SubscriptionPlan).count()
        if existing > 0:
            print(f"✓ Subscription plans already exist ({existing} plans)")
            return
        
        # Create subscription plans
        plans = [
            SubscriptionPlan(
                name="Low Tier Subscription",
                tier="low",
                price=3000.0,
                duration_months=2,
                description="Access to low-tier jobs (Teacher, Driver, Cleaner, etc.) for 2 months. Companies can post low-tier jobs. Job seekers can apply to low-tier jobs.",
                is_active=True
            ),
            SubscriptionPlan(
                name="High Tier Subscription",
                tier="high",
                price=8000.0,
                duration_months=2,
                description="Full access to all jobs (both low and high-tier) for 2 months. Companies can post any job. Job seekers can apply to any job.",
                is_active=True
            )
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        print("✓ Subscription plans created successfully!")
        print(f"  - Low Tier: ₦3,000 for 2 months")
        print(f"  - High Tier: ₦8,000 for 2 months")
        
        # Update job categories with tier information
        print("\n✓ Updating job categories with tier information...")
        
        # Low-tier categories (₦3,000)
        low_tier_categories = [
            "Teacher", "Driver", "Cleaner", "Security Guard", "Cook", 
            "Waiter", "Waitress", "Receptionist", "Sales Assistant", 
            "Customer Service", "Cashier", "Delivery", "Warehouse", 
            "Factory Worker", "Retail", "Hospitality", "Housekeeper",
            "Gardener", "Nanny", "Caregiver"
        ]
        
        # High-tier categories (₦8,000)
        high_tier_categories = [
            "Technology", "Software", "Engineering", "Finance", 
            "Management", "Healthcare", "Medical", "Legal", 
            "Marketing", "Design", "Accounting", "Banking",
            "Architecture", "Consulting", "Data Science", "IT",
            "Project Management", "Business Development", "HR",
            "Executive"
        ]
        
        categories = db.query(JobCategory).all()
        for category in categories:
            # Check if category name matches low or high tier
            if any(low in category.name for low in low_tier_categories):
                category.tier = "low"
            elif any(high in category.name for high in high_tier_categories):
                category.tier = "high"
            else:
                # Default to low tier
                category.tier = "low"
        
        db.commit()
        print("✓ Job categories updated with tier information")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing subscription plans...")
    init_subscription_plans()
    print("\nDone!")
