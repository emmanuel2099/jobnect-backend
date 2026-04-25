#!/usr/bin/env python3
"""
Add realistic payment test data with different amounts and dates
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Payment
from sqlalchemy import text

def add_realistic_payments():
    db = SessionLocal()
    
    try:
        print("🔄 Adding realistic payment test data...")
        
        # Clear existing test payments (optional)
        print("🗑️  Clearing existing payments...")
        db.execute(text("DELETE FROM payments"))
        db.commit()
        
        # Create realistic payment data
        payment_data = [
            # This month - completed payments
            {"amount": 15000, "status": "completed", "method": "card", "days_ago": 2},
            {"amount": 25000, "status": "completed", "method": "bank_transfer", "days_ago": 5},
            {"amount": 8000, "status": "completed", "method": "card", "days_ago": 8},
            {"amount": 12000, "status": "completed", "method": "card", "days_ago": 12},
            {"amount": 30000, "status": "completed", "method": "bank_transfer", "days_ago": 15},
            {"amount": 18000, "status": "completed", "method": "card", "days_ago": 18},
            {"amount": 22000, "status": "completed", "method": "card", "days_ago": 20},
            {"amount": 35000, "status": "completed", "method": "bank_transfer", "days_ago": 25},
            
            # Last month - completed payments
            {"amount": 20000, "status": "completed", "method": "card", "days_ago": 35},
            {"amount": 28000, "status": "completed", "method": "bank_transfer", "days_ago": 40},
            {"amount": 16000, "status": "completed", "method": "card", "days_ago": 45},
            {"amount": 24000, "status": "completed", "method": "card", "days_ago": 50},
            
            # Pending payments (should not count in revenue)
            {"amount": 15000, "status": "pending", "method": "card", "days_ago": 1},
            {"amount": 20000, "status": "pending", "method": "bank_transfer", "days_ago": 3},
            {"amount": 12000, "status": "pending", "method": "card", "days_ago": 4},
            
            # Failed payments (should not count in revenue)
            {"amount": 18000, "status": "failed", "method": "card", "days_ago": 6},
            {"amount": 25000, "status": "failed", "method": "bank_transfer", "days_ago": 10},
        ]
        
        user_id = 1  # Assuming user ID 1 exists
        
        for i, data in enumerate(payment_data, 1):
            payment_date = datetime.now() - timedelta(days=data["days_ago"])
            
            payment = Payment(
                user_id=user_id,
                amount=data["amount"],
                currency="NGN",
                payment_method=data["method"],
                transaction_reference=f"TXN_{payment_date.strftime('%Y%m%d')}_{i:03d}",
                status=data["status"],
                payment_date=payment_date,
                created_at=payment_date
            )
            
            db.add(payment)
            print(f"✅ Added: ₦{data['amount']:,} - {data['status']} - {data['method']} ({data['days_ago']} days ago)")
        
        db.commit()
        
        # Calculate and display summary
        print("\n📊 Payment Summary:")
        print("=" * 50)
        
        completed = db.execute(text("SELECT * FROM payments WHERE status = 'completed'")).fetchall()
        pending = db.execute(text("SELECT * FROM payments WHERE status = 'pending'")).fetchall()
        failed = db.execute(text("SELECT * FROM payments WHERE status = 'failed'")).fetchall()
        
        total_revenue = sum(row[2] for row in completed)  # amount is column 2
        
        # This month revenue
        current_month = datetime.now().month
        current_year = datetime.now().year
        this_month_completed = [row for row in completed 
                               if row[7] and row[7].month == current_month and row[7].year == current_year]  # created_at is column 7
        monthly_revenue = sum(row[2] for row in this_month_completed)
        
        # This week revenue (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        this_week_completed = [row for row in completed 
                              if row[7] and row[7] >= week_ago]
        weekly_revenue = sum(row[2] for row in this_week_completed)
        
        print(f"💰 Total Revenue (Completed): ₦{total_revenue:,}")
        print(f"📅 This Month Revenue: ₦{monthly_revenue:,}")
        print(f"📆 This Week Revenue: ₦{weekly_revenue:,}")
        print(f"✅ Completed Payments: {len(completed)}")
        print(f"⏳ Pending Payments: {len(pending)}")
        print(f"❌ Failed Payments: {len(failed)}")
        
        if len(completed) > 0:
            avg_payment = total_revenue / len(completed)
            print(f"📊 Average Payment: ₦{avg_payment:,.0f}")
        
        print(f"\n🎉 Successfully added {len(payment_data)} realistic payments!")
        print("💡 Now your admin dashboard will show different amounts for each time period.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    add_realistic_payments()