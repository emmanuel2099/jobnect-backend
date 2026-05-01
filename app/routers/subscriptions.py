from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, SubscriptionPlan, Subscription, Payment
from app.subscription_service import SubscriptionService
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# Schemas
class SubscriptionPlanResponse(BaseModel):
    id: int
    name: str
    tier: str
    price: float
    duration_months: int
    description: Optional[str]
    
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    id: int
    plan_id: Optional[int]
    status: str
    start_date: datetime
    end_date: datetime
    is_trial: bool
    jobs_posted: int
    plan: Optional[SubscriptionPlanResponse]
    
    class Config:
        from_attributes = True

class CheckAccessRequest(BaseModel):
    category_id: Optional[int] = None
    job_id: Optional[int] = None

class InitiatePaymentRequest(BaseModel):
    plan_id: int
    payment_method: str = "card"

class VerifyPaymentRequest(BaseModel):
    transaction_reference: str
    plan_id: int

# Get all subscription plans
@router.get("/plans")
def get_subscription_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available subscription plans with user-specific pricing"""
    from app.models import JobSeeker, CompanyUser
    
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    
    # Determine user type
    is_company = isinstance(current_user, CompanyUser) or (hasattr(current_user, 'user_type') and current_user.user_type == "company")
    
    # Apply pricing based on user type
    result = []
    for plan in plans:
        plan_dict = {
            "id": plan.id,
            "name": plan.name,
            "tier": plan.tier,
            "duration_months": plan.duration_months,
            "description": plan.description,
            "is_active": plan.is_active
        }
        
        # Set price based on user type
        # Companies: Low ₦10,000, High ₦20,000
        # Job Seekers: Low ₦3,000, High ₦10,000
        if is_company:
            plan_dict["price"] = 20000.0 if plan.tier == "high" else 10000.0
        else:  # job seeker/applicant
            plan_dict["price"] = 10000.0 if plan.tier == "high" else 3000.0
        
        result.append(plan_dict)
    
    return result

# Get user's current subscription
@router.get("/my-subscription", response_model=Optional[SubscriptionResponse])
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's active subscription"""
    subscription = SubscriptionService.get_active_subscription(db, current_user.id)
    if not subscription:
        # Check for trial
        trial = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.is_trial == True
        ).first()
        return trial
    return subscription

# Create subscription tables (admin endpoint)
@router.post("/create-tables")
def create_subscription_tables(db: Session = Depends(get_db)):
    """Create subscription tables in the database"""
    
    try:
        # Create tables using SQLAlchemy
        from app.models import Base
        Base.metadata.create_all(bind=db.get_bind(), tables=[SubscriptionPlan.__table__, Subscription.__table__])
        
        return {
            "success": True,
            "message": "Subscription tables created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tables: {str(e)}")

# Initialize subscription plans (admin endpoint)
@router.post("/initialize-plans")
def initialize_subscription_plans(db: Session = Depends(get_db)):
    """Initialize subscription plans with default pricing"""
    
    try:
        # Check if plans already exist
        existing_plans = db.query(SubscriptionPlan).all()
        if existing_plans:
            # Clear existing plans
            db.query(SubscriptionPlan).delete()
            db.commit()
        
        # Add new subscription plans
        plans = [
            SubscriptionPlan(
                name="Low Tier",
                tier="low", 
                price=3000.0,  # Base price for job seekers
                duration_months=1,
                description="Basic access with limited features",
                is_active=True
            ),
            SubscriptionPlan(
                name="High Tier",
                tier="high",
                price=10000.0,  # Base price for job seekers
                duration_months=1, 
                description="Premium access with all features",
                is_active=True
            )
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Subscription plans initialized successfully",
            "plans": [
                {
                    "name": "Low Tier",
                    "tier": "low",
                    "job_seeker_price": 3000,
                    "company_price": 10000,
                    "duration_months": 1
                },
                {
                    "name": "High Tier", 
                    "tier": "high",
                    "job_seeker_price": 10000,
                    "company_price": 20000,
                    "duration_months": 1
                }
            ]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to initialize plans: {str(e)}")

# Check if user can post job or apply to job
@router.post("/check-access")
def check_access(
    request: CheckAccessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can post a job (company) or apply to a job (job seeker)"""
    from app.models import JobSeeker, CompanyUser
    
    # Determine user type
    is_company = isinstance(current_user, CompanyUser) or (hasattr(current_user, 'user_type') and current_user.user_type == "company")
    is_job_seeker = isinstance(current_user, JobSeeker) or (hasattr(current_user, 'user_type') and current_user.user_type == "applicant")
    
    if is_company:
        if not request.category_id:
            raise HTTPException(status_code=400, detail="category_id required for companies")
        result = SubscriptionService.can_post_job(db, current_user.id, request.category_id)
    elif is_job_seeker:
        if not request.job_id:
            raise HTTPException(status_code=400, detail="job_id required for job seekers")
        result = SubscriptionService.can_apply_to_job(db, current_user.id, request.job_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    return result

# Health check endpoint that also fixes database
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check that also fixes database issues"""
    try:
        from sqlalchemy import text
        
        # Check if jobs_applied column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='subscriptions' AND column_name='jobs_applied';
        """))
        
        if not result.fetchone():
            # Add the missing column
            print("🔧 Adding jobs_applied column to subscriptions table...")
            db.execute(text("ALTER TABLE subscriptions ADD COLUMN jobs_applied INTEGER DEFAULT 0;"))
            db.commit()
            print("✅ jobs_applied column added successfully!")
            
            return {
                "success": True,
                "message": "Database fixed successfully - jobs_applied column added",
                "status": "healthy"
            }
        else:
            return {
                "success": True,
                "message": "Database already has jobs_applied column",
                "status": "healthy"
            }
            
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return {
            "success": False,
            "message": f"Error: {e}",
            "status": "unhealthy"
        }

# Emergency database fix endpoint
@router.get("/fix-database")
def fix_database(db: Session = Depends(get_db)):
    """Emergency fix to add missing jobs_applied column"""
    try:
        from sqlalchemy import text
        
        # Check if column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='subscriptions' AND column_name='jobs_applied';
        """))
        
        if not result.fetchone():
            # Add the missing column
            print("🔧 Adding jobs_applied column to subscriptions table...")
            db.execute(text("ALTER TABLE subscriptions ADD COLUMN jobs_applied INTEGER DEFAULT 0;"))
            db.commit()
            print("✅ jobs_applied column added successfully!")
            
            return {
                "success": True,
                "message": "Database fixed successfully - jobs_applied column added"
            }
        else:
            return {
                "success": True,
                "message": "Database already has jobs_applied column"
            }
            
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return {
            "success": False,
            "message": f"Error fixing database: {e}"
        }

# Test user data endpoint
@router.get("/test-user-data")
def test_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test endpoint to check user data"""
    return {
        "success": True,
        "user_data": {
            "id": current_user.id,
            "email": current_user.email,
            "phone": current_user.phone,
            "name": current_user.name,
            "user_type": current_user.user_type,
            "is_active": current_user.is_active
        }
    }

# Initiate payment
@router.post("/initiate-payment")
def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a subscription payment with FundsVera."""
    
    try:
        print(f"🔵 Payment initiation:")
        print(f"  - Plan ID: {request.plan_id}")
        print(f"  - User ID: {current_user.id}")
        print(f"  - User type: {type(current_user).__name__}")
        
        # Get plan from database
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == request.plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        
        print(f"🔵 Plan from database: {plan.name} - ₦{plan.price:,}")
        
        # Use actual plan data from database
        plan_data = {"name": plan.name, "price": plan.price}
        amount = plan.price
        
        print(f"🔵 Amount to charge: ₦{amount:,}")
        
        # Generate transaction reference
        import uuid
        tx_ref = f"SUB-{uuid.uuid4().hex[:12].upper()}"
        
        # Get user email and phone safely
        user_email = getattr(current_user, 'email', None) or "test@example.com"
        user_phone = getattr(current_user, 'phone', None) or "1234567890"
        user_name = getattr(current_user, 'name', None) or "Test User"
        
        print(f"🔵 User details: {user_email}, {user_phone}, {user_name}")
        
        # Determine if user is job seeker or company
        from app.models import JobSeeker, CompanyUser
        is_company = isinstance(current_user, CompanyUser) or (hasattr(current_user, 'user_type') and current_user.user_type == "company")

        # Create pending payment record first (verification relies on this record).
        payment = Payment(
            user_id=None,  # Not used - we use job_seeker_id or company_user_id
            job_seeker_id=None if is_company else current_user.id,
            company_user_id=current_user.id if is_company else None,
            subscription_id=None,
            amount=amount,
            currency="NGN",
            payment_method=request.payment_method,
            transaction_reference=tx_ref,
            status="pending"
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        print(f"🔵 Payment record created: {payment.id}")

        # Initialize Flutterwave payment
        from app.flutterwave_service import flutterwave_service
        
        payment_result = flutterwave_service.initialize_payment(
            amount=amount,
            email=user_email,
            phone=user_phone,
            name=user_name,
            tx_ref=tx_ref,
            redirect_url="",
            currency="NGN"
        )
        
        print(f"🔵 Flutterwave result: {payment_result.get('success')}")
        
        if payment_result.get("success"):
            return {
                "success": True,
                "transaction_reference": tx_ref,
                "payment_link": payment_result.get("payment_link"),
                "amount": amount,
                "currency": "NGN",
                "plan_name": plan_data["name"],
                "payment_provider": "flutterwave",
                "flutterwave_public_key": flutterwave_service.public_key,
                "message": "Payment initialized. Complete payment with Flutterwave."
            }
        else:
            payment.status = "failed"
            db.commit()
            raise HTTPException(status_code=400, detail=payment_result.get("message", "Flutterwave initialization failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Payment initiation error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to mark payment as failed if it exists
        try:
            if 'payment' in locals():
                payment.status = "failed"
                db.commit()
        except:
            pass
            
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")

# Verify payment and activate subscription
@router.post("/verify-payment")
def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment with FundsVera and activate subscription."""
    
    # Find payment record - check both job_seeker_id and company_user_id
    from app.models import JobSeeker, CompanyUser
    is_company = isinstance(current_user, CompanyUser) or (hasattr(current_user, 'user_type') and current_user.user_type == "company")
    
    if is_company:
        payment = db.query(Payment).filter(
            Payment.transaction_reference == request.transaction_reference,
            Payment.company_user_id == current_user.id
        ).first()
    else:
        payment = db.query(Payment).filter(
            Payment.transaction_reference == request.transaction_reference,
            Payment.job_seeker_id == current_user.id
        ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == "completed":
        raise HTTPException(status_code=400, detail="Payment already verified")
    
    # Verify with Flutterwave
    from app.flutterwave_service import flutterwave_service

    verification_result = flutterwave_service.verify_payment_by_reference(request.transaction_reference)
    
    if not verification_result.get("success"):
        raise HTTPException(status_code=400, detail=verification_result.get("message", "Payment verification failed"))
    
    if not verification_result.get("verified"):
        raise HTTPException(status_code=400, detail="Payment not successful. Please try again.")
    
    # Verify amount matches
    if float(verification_result.get("amount", 0)) != payment.amount:
        raise HTTPException(status_code=400, detail="Payment amount mismatch")
    
    # Create subscription
    subscription = SubscriptionService.create_subscription(
        db, current_user.id, request.plan_id, request.transaction_reference
    )
    
    # Update payment
    payment.subscription_id = subscription.id
    payment.status = "completed"
    payment.payment_date = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Payment verified and subscription activated",
        "subscription": {
            "id": subscription.id,
            "status": subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date
        },
        "payment_details": {
            "amount": verification_result.get("amount"),
            "currency": verification_result.get("currency"),
            "payment_type": verification_result.get("payment_type")
        }
    }

# Get subscription history
@router.get("/history")
def get_subscription_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's subscription history"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Subscription.created_at.desc()).all()
    
    return subscriptions

# Get payment history
@router.get("/payments")
def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history"""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return payments

# FundsVera webhook endpoint
@router.post("/webhook/fundsvera")
async def fundsvera_webhook(request: dict, db: Session = Depends(get_db)):
    """Handle FundsVera payment webhooks."""
    
    event = request.get("event")
    data = request.get("data", {})
    
    if event == "payment.completed":
        tx_ref = data.get("tx_ref")
        status = data.get("status")
        amount = data.get("amount")
        
        if status == "successful":
            # Find payment record
            payment = db.query(Payment).filter(
                Payment.transaction_reference == tx_ref
            ).first()
            
            if payment and payment.status == "pending":
                # Get plan from payment amount
                plan = db.query(SubscriptionPlan).filter(
                    SubscriptionPlan.price == amount
                ).first()
                
                if plan:
                    # Create subscription
                    subscription = SubscriptionService.create_subscription(
                        db, payment.user_id, plan.id, tx_ref
                    )
                    
                    # Update payment
                    payment.subscription_id = subscription.id
                    payment.status = "completed"
                    payment.payment_date = datetime.utcnow()
                    db.commit()
                    
                    # Send notification to user
                    from app.notification_service import create_notification
                    create_notification(
                        db,
                        payment.user_id,
                        "Subscription Activated",
                        f"Your {plan.name} subscription has been activated successfully!",
                        "subscription"
                    )
    
    return {"status": "success"}
