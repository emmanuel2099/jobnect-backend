from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

# Job Seeker Model
class JobSeeker(Base):
    __tablename__ = "job_seekers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile_photo = Column(Text)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    is_deactivated = Column(Boolean, default=False)
    deactivated_at = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="job_seeker", uselist=False, cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job_seeker", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="job_seeker", cascade="all, delete-orphan")
    # notifications = relationship("Notification", back_populates="job_seeker", cascade="all, delete-orphan")  # Temporarily disabled
    social_links = relationship("SocialLink", back_populates="job_seeker", cascade="all, delete-orphan")
    kyc = relationship("KYC", back_populates="job_seeker", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="job_seeker")
    subscriptions = relationship("Subscription", back_populates="job_seeker", cascade="all, delete-orphan")

# Company User Model  
class CompanyUser(Base):
    __tablename__ = "company_users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    company_logo = Column(Text)
    profile_photo = Column(Text)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    is_deactivated = Column(Boolean, default=False)
    deactivated_at = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="company_user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="company_user", cascade="all, delete-orphan")
    social_links = relationship("SocialLink", back_populates="company_user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="company_user", cascade="all, delete-orphan")

# Legacy User Model (kept for backward compatibility)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    company = Column(String(255))
    company_logo = Column(Text)
    user_type = Column(String(50), default="applicant")
    profile_photo = Column(Text)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    is_deactivated = Column(Boolean, default=False)
    deactivated_at = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="user", uselist=False, cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    social_links = relationship("SocialLink", back_populates="user", cascade="all, delete-orphan")
    kyc = relationship("KYC", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

# Resume Model (unified)
class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"), unique=True)
    
    # Personal Info
    father_name = Column(String(255))
    mother_name = Column(String(255))
    date_of_birth = Column(Date)
    age = Column(Integer)  # Age field for Google Play compliance
    gender = Column(String(50))
    religion = Column(String(100))
    marital_status = Column(String(50))
    nationality = Column(String(100))
    nid = Column(String(100))
    
    # Address Info
    present_address = Column(Text)
    permanent_address = Column(Text)
    
    # Career Info
    designation = Column(String(255))  # Job title/bio
    city = Column(String(255))  # City/location
    objective = Column(Text)
    present_salary = Column(String(100))
    expected_salary = Column(String(100))
    job_level = Column(String(100))
    job_nature = Column(String(100))
    
    # Skills (stored as JSON array)
    skills = Column(Text)  # JSON array of skill names
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resume")
    job_seeker = relationship("JobSeeker", back_populates="resume")
    experiences = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    trainings = relationship("Training", back_populates="resume", cascade="all, delete-orphan")
    languages = relationship("Language", back_populates="resume", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="resume", cascade="all, delete-orphan")

# Experience Model
class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    business = Column(String(255), nullable=False)
    employer = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    department = Column(String(255))
    responsibilities = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="experiences")

# Education Model
class Education(Base):
    __tablename__ = "educations"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    level = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    exam = Column(String(255))
    result = Column(String(100))
    passing_year = Column(String(10))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="educations")

# Training Model
class Training(Base):
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    topics = Column(Text)
    institute = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="trainings")

# Language Model
class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    language = Column(String(100), nullable=False)
    reading = Column(String(50), nullable=False)
    writing = Column(String(50), nullable=False)
    speaking = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="languages")

# Reference Model
class Reference(Base):
    __tablename__ = "references"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    relation = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="references")

# Company Model
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    company_user_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    logo = Column(Text)
    description = Column(Text)
    industry = Column(String(255))
    website = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    location = Column(String(255))
    founded_year = Column(Integer)
    company_size = Column(String(100))
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="company")
    company_user = relationship("CompanyUser", back_populates="company")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="company")

# Job Category Model
class JobCategory(Base):
    __tablename__ = "job_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    icon = Column(Text)
    description = Column(Text)
    tier = Column(String(50), default="low")  # "low" or "high" - determines subscription requirement
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="category")

# City Model
class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(255))
    country = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="city_rel")

# Skill Model
class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Designation Model
class Designation(Base):
    __tablename__ = "designations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Job Type Model
class JobType(Base):
    __tablename__ = "job_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="job_type")

# Job Level Model
class JobLevel(Base):
    __tablename__ = "job_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="job_level")

# Education Level Model
class EducationLevel(Base):
    __tablename__ = "education_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Job Model
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("job_categories.id", ondelete="SET NULL"))
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="SET NULL"))  # Keep for backward compatibility
    job_type_id = Column(Integer, ForeignKey("job_types.id", ondelete="SET NULL"))
    job_level_id = Column(Integer, ForeignKey("job_levels.id", ondelete="SET NULL"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    salary_min = Column(Float)
    salary_max = Column(Float)
    location = Column(String(255))
    city = Column(String(255))  # Free text city field
    currency = Column(String(10), default='USD')  # Currency: USD or NGN
    deadline = Column(Date)
    vacancies = Column(Integer, default=1)
    experience_required = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_recommended = Column(Boolean, default=False)  # For recommended jobs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    category = relationship("JobCategory", back_populates="jobs")
    city_rel = relationship("City", back_populates="jobs", foreign_keys=[city_id])  # Renamed to avoid conflict
    job_type = relationship("JobType", back_populates="jobs")
    job_level = relationship("JobLevel", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="job", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="job")

# Job Application Model
class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    cover_letter = Column(Text)
    resume_file = Column(Text)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    job_seeker = relationship("JobSeeker", back_populates="applications")
    job = relationship("Job", back_populates="applications")

# Bookmark Model
class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="bookmarks")
    job_seeker = relationship("JobSeeker", back_populates="bookmarks")
    job = relationship("Job", back_populates="bookmarks")

# Notification Model
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    company_user_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")
    # job_seeker = relationship("JobSeeker", back_populates="notifications")  # Temporarily disabled
    company_user = relationship("CompanyUser", back_populates="notifications")

# Social Link Model
class SocialLink(Base):
    __tablename__ = "social_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    company_user_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    platform = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="social_links")
    job_seeker = relationship("JobSeeker", back_populates="social_links")
    company_user = relationship("CompanyUser", back_populates="social_links")

# KYC Model
class KYC(Base):
    __tablename__ = "kyc"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"), unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)
    document_number = Column(String(255), nullable=False)
    document_file = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="kyc")
    job_seeker = relationship("JobSeeker", back_populates="kyc")

# App Setting Model
class AppSetting(Base):
    __tablename__ = "app_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# App Slider Model
class AppSlider(Base):
    __tablename__ = "app_sliders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    image = Column(Text, nullable=False)
    link = Column(String(500))
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Subscription Plan Model
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # "Low Tier" or "High Tier"
    tier = Column(String(50), nullable=False)  # "low" or "high"
    price = Column(Float, nullable=False)  # 3000 or 8000
    duration_months = Column(Integer, default=2)  # 2 months
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="plan")

# User Subscription Model
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id"), nullable=False)
    company_user_id = Column(Integer, ForeignKey("company_users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=True)
    status = Column(String(50), default="active")  # active, expired, cancelled
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_trial = Column(Boolean, default=False)
    jobs_posted = Column(Integer, default=0)
    jobs_applied = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    job_seeker = relationship("JobSeeker", back_populates="subscriptions")
    company_user = relationship("CompanyUser", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")

# Review Model
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)  # Verified by company
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    job_seeker = relationship("JobSeeker", back_populates="reviews")
    job = relationship("Job", back_populates="reviews")

# Payment Model
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    company_user_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="NGN")
    payment_method = Column(String(50))  # card, bank_transfer, etc.
    transaction_reference = Column(String(255), unique=True)
    status = Column(String(50), default="pending")  # pending, completed, failed
    payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="payments")

# Conversation Model
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker1_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    job_seeker2_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    company_user1_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    company_user2_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

# Message Model
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_seeker_sender_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    job_seeker_receiver_id = Column(Integer, ForeignKey("job_seekers.id", ondelete="CASCADE"))
    company_user_sender_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    company_user_receiver_id = Column(Integer, ForeignKey("company_users.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

# Feedback Model
class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    job_seeker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"))  # Optional: feedback about specific job
    rating = Column(Integer, nullable=False)  # 1-5 rating
    feedback_text = Column(Text, nullable=False)
    feedback_type = Column(String(50), default="general")  # general, interview, application, etc.
    is_anonymous = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # Whether feedback can be shown publicly
    status = Column(String(50), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_seeker = relationship("User", foreign_keys=[job_seeker_id])
    company = relationship("Company")
    job = relationship("Job")
