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
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    
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
        if current_user.user_type == "company":
            plan_dict["price"] = 20000.0 if plan.tier == "high" else 10000.0
        else:  # applicant
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
                duration_months=1,
                description="Basic access with limited features",
                is_active=True
            ),
            SubscriptionPlan(
                name="High Tier",
                tier="high",
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
    
    if current_user.user_type == "company":
        if not request.category_id:
            raise HTTPException(status_code=400, detail="category_id required for companies")
        result = SubscriptionService.can_post_job(db, current_user.id, request.category_id)
    elif current_user.user_type == "applicant":
        if not request.job_id:
            raise HTTPException(status_code=400, detail="job_id required for job seekers")
        result = SubscriptionService.can_apply_to_job(db, current_user.id, request.job_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    return result

# Initiate payment
@router.post("/initiate-payment")
def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a subscription payment with Flutterwave"""
    
    # Get plan
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == request.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Apply pricing based on user type
    # Job Seekers: Low ₦3,000, High ₦10,000
    # Companies: Low ₦10,000, High ₦20,000
    if current_user.user_type == "company":
        amount = 20000.0 if plan.tier == "high" else 10000.0
    else:  # applicant
        amount = 10000.0 if plan.tier == "high" else 3000.0
    
    # Generate transaction reference
    transaction_ref = f"SUB-{uuid.uuid4().hex[:12].upper()}"
    
    # Initialize Flutterwave payment
    from app.flutterwave_service import flutterwave_service
    
    payment_result = flutterwave_service.initialize_payment(
        amount=amount,
        email=current_user.email,
        phone=current_user.phone,
        name=current_user.name,
        tx_ref=transaction_ref,
        redirect_url="",  # Will be handled by mobile app
        currency="NGN"
    )
    
    if not payment_result.get("success"):
        raise HTTPException(status_code=400, detail=payment_result.get("message", "Payment initialization failed"))
    
    # Create pending payment record
    payment = Payment(
        user_id=current_user.id,
        subscription_id=None,  # Will be set after verification
        amount=amount,
        currency="NGN",
        payment_method=request.payment_method,
        transaction_reference=transaction_ref,
        status="pending"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {
        "success": True,
        "transaction_reference": transaction_ref,
        "payment_link": payment_result.get("payment_link"),
        "amount": amount,
        "currency": "NGN",
        "plan_name": plan.name,
        "flutterwave_public_key": flutterwave_service.public_key,
        "message": "Payment initialized. Complete payment with Flutterwave."
    }

# Verify payment and activate subscription
@router.post("/verify-payment")
def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment with Flutterwave and activate subscription"""
    
    # Find payment record
    payment = db.query(Payment).filter(
        Payment.transaction_reference == request.transaction_reference,
        Payment.user_id == current_user.id
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

# Flutterwave webhook endpoint
@router.post("/webhook/flutterwave")
async def flutterwave_webhook(request: dict, db: Session = Depends(get_db)):
    """Handle Flutterwave payment webhooks"""
    
    # Verify webhook signature
    # In production, verify the webhook hash
    
    event = request.get("event")
    data = request.get("data", {})
    
    if event == "charge.completed":
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
