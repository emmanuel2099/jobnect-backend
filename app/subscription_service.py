from sqlalchemy.orm import Session
from app.models import Subscription, SubscriptionPlan, User, JobCategory, Job
from datetime import datetime, timedelta
from typing import Optional

class SubscriptionService:
    
    @staticmethod
    def get_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
        """Get user's active subscription"""
        return db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.end_date > datetime.utcnow()
        ).first()
    
    @staticmethod
    def has_active_subscription(db: Session, user_id: int) -> bool:
        """Check if user has active subscription"""
        subscription = SubscriptionService.get_active_subscription(db, user_id)
        return subscription is not None
    
    @staticmethod
    def can_post_job(db: Session, user_id: int, category_id: int) -> dict:
        """
        Check if company can post a job in this category
        Returns: {"allowed": bool, "reason": str, "requires_payment": bool, "plan_needed": str}
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.user_type != "company":
            return {"allowed": False, "reason": "User is not a company", "requires_payment": False}
        
        # Get job category tier
        category = db.query(JobCategory).filter(JobCategory.id == category_id).first()
        if not category:
            return {"allowed": False, "reason": "Invalid category", "requires_payment": False}
        
        job_tier = category.tier  # "low" or "high"
        
        # Check for active subscription
        subscription = SubscriptionService.get_active_subscription(db, user_id)
        
        if not subscription:
            # Check if they're in free trial
            trial_sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_trial == True
            ).first()
            
            if not trial_sub:
                # Create free trial
                trial_sub = Subscription(
                    user_id=user_id,
                    plan_id=None,
                    status="active",
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=365),  # Long expiry for trial
                    is_trial=True,
                    jobs_posted=0
                )
                db.add(trial_sub)
                db.commit()
                db.refresh(trial_sub)
            
            # Check trial limits
            if trial_sub.jobs_posted >= 3:
                plan_needed = "high" if job_tier == "high" else "low"
                # Company pricing: Low ₦10,000, High ₦20,000
                amount = 20000 if job_tier == "high" else 10000
                return {
                    "allowed": False,
                    "reason": "Free trial limit reached (3 jobs). Please subscribe to continue posting.",
                    "requires_payment": True,
                    "plan_needed": plan_needed,
                    "amount": amount
                }
            
            # Allow posting and increment counter
            trial_sub.jobs_posted += 1
            db.commit()
            return {"allowed": True, "reason": f"Free trial: {3 - trial_sub.jobs_posted} jobs remaining", "requires_payment": False}
        
        # Has active subscription - check tier
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
        if not plan:
            return {"allowed": False, "reason": "Invalid subscription plan", "requires_payment": False}
        
        # High tier can post both low and high jobs
        if plan.tier == "high":
            return {"allowed": True, "reason": "Active high-tier subscription", "requires_payment": False}
        
        # Low tier can only post low tier jobs
        if plan.tier == "low" and job_tier == "low":
            return {"allowed": True, "reason": "Active low-tier subscription", "requires_payment": False}
        
        # Low tier trying to post high tier job
        if plan.tier == "low" and job_tier == "high":
            return {
                "allowed": False,
                "reason": "Your current subscription doesn't allow posting high-tier jobs. Please upgrade to high-tier subscription.",
                "requires_payment": True,
                "plan_needed": "high",
                "amount": 20000  # Company high-tier price
            }
        
        return {"allowed": False, "reason": "Unknown error", "requires_payment": False}
    
    @staticmethod
    def can_apply_to_job(db: Session, user_id: int, job_id: int) -> dict:
        """
        Check if job seeker can apply to this job
        Returns: {"allowed": bool, "reason": str, "requires_payment": bool, "plan_needed": str}
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.user_type != "applicant":
            return {"allowed": False, "reason": "User is not a job seeker", "requires_payment": False}
        
        # Get job and its category tier
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"allowed": False, "reason": "Invalid job", "requires_payment": False}
        
        category = db.query(JobCategory).filter(JobCategory.id == job.category_id).first()
        if not category:
            return {"allowed": False, "reason": "Invalid job category", "requires_payment": False}
        
        job_tier = category.tier  # "low" or "high"
        
        # Check for active subscription
        subscription = SubscriptionService.get_active_subscription(db, user_id)
        
        if not subscription:
            # No subscription - must pay
            plan_needed = "high" if job_tier == "high" else "low"
            # Job seeker pricing: Low ₦3,000, High ₦10,000
            amount = 10000 if job_tier == "high" else 3000
            return {
                "allowed": False,
                "reason": f"You need a subscription to apply for jobs. Please subscribe to {'high-tier' if job_tier == 'high' else 'low-tier'} plan.",
                "requires_payment": True,
                "plan_needed": plan_needed,
                "amount": amount
            }
        
        # Has active subscription - check tier
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
        if not plan:
            return {"allowed": False, "reason": "Invalid subscription plan", "requires_payment": False}
        
        # High tier can apply to both low and high jobs
        if plan.tier == "high":
            return {"allowed": True, "reason": "Active high-tier subscription", "requires_payment": False}
        
        # Low tier can only apply to low tier jobs
        if plan.tier == "low" and job_tier == "low":
            return {"allowed": True, "reason": "Active low-tier subscription", "requires_payment": False}
        
        # Low tier trying to apply to high tier job
        if plan.tier == "low" and job_tier == "high":
            return {
                "allowed": False,
                "reason": "This is a high-tier job. Please upgrade to high-tier subscription to apply.",
                "requires_payment": True,
                "plan_needed": "high",
                "amount": 10000  # Job seeker high-tier price
            }
        
        return {"allowed": False, "reason": "Unknown error", "requires_payment": False}
    
    @staticmethod
    def create_subscription(db: Session, user_id: int, plan_id: int, transaction_ref: str) -> Subscription:
        """Create a new subscription after successful payment"""
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Invalid plan")
        
        # Deactivate any existing subscriptions
        existing = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).all()
        for sub in existing:
            sub.status = "expired"
        
        # Create new subscription
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_months * 30)
        
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            start_date=start_date,
            end_date=end_date,
            is_trial=False
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def check_and_expire_subscriptions(db: Session):
        """Background task to expire old subscriptions"""
        expired = db.query(Subscription).filter(
            Subscription.status == "active",
            Subscription.end_date <= datetime.utcnow()
        ).all()
        
        for sub in expired:
            sub.status = "expired"
        
        db.commit()
        return len(expired)
