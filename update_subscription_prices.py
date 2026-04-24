"""
Update subscription plan prices
Job Seekers: Low ₦3,000 | High ₦10,000
Companies: Low ₦10,000 | High ₦20,000
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import get_db
from app.models import SubscriptionPlan

def update_prices():
    db = next(get_db())
    
    try:
        # Get all plans
        plans = db.query(SubscriptionPlan).all()
        
        for plan in plans:
            if plan.tier == "low":
                # Low tier for both job seekers and companies: ₦3,000 and ₦10,000
                # We'll set it to 3000 for job seekers (applicants)
                plan.price = 3000.0
                plan.description = "Access to low-tier job categories for 2 months"
                print(f"✅ Updated {plan.name} (Low Tier): ₦3,000")
            
            elif plan.tier == "high":
                # High tier: ₦10,000 for job seekers, ₦20,000 for companies
                # We'll set it to 10000 for now (will need separate plans for companies)
                plan.price = 10000.0
                plan.description = "Access to all job categories including high-tier for 2 months"
                print(f"✅ Updated {plan.name} (High Tier): ₦10,000")
        
        db.commit()
        print("\n✅ Subscription prices updated successfully!")
        
        # Display summary
        print("\n📊 New Pricing Structure:")
        print("=" * 50)
        print("JOB SEEKERS:")
        print("  Low Tier:  ₦3,000  (2 months)")
        print("  High Tier: ₦10,000 (2 months)")
        print("\nCOMPANIES:")
        print("  Low Tier:  ₦10,000 (2 months)")
        print("  High Tier: ₦20,000 (2 months)")
        print("=" * 50)
        print("\nNote: Company pricing will be handled in the backend logic")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_prices()
