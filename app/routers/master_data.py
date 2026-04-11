from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JobCategory, City, Skill, Designation, JobType, JobLevel, EducationLevel, AppSetting, AppSlider

router = APIRouter()

@router.get("/job-category")
async def get_job_categories(db: Session = Depends(get_db)):
    """Get all job categories"""
    
    categories = db.query(JobCategory).filter(JobCategory.is_active == True).all()
    
    categories_data = [{
        "id": cat.id,
        "name": cat.name,
        "icon": cat.icon,
        "description": cat.description
    } for cat in categories]
    
    return {
        "success": True,
        "message": "Job categories retrieved",
        "data": {"categories": categories_data}
    }

@router.get("/categories")
async def get_categories_for_filter(db: Session = Depends(get_db)):
    """Get categories for filtering (same as job-category)"""
    
    categories = db.query(JobCategory).filter(JobCategory.is_active == True).all()
    
    categories_data = [{
        "id": cat.id,
        "name": cat.name,
        "icon": cat.icon
    } for cat in categories]
    
    return {
        "success": True,
        "message": "Categories retrieved",
        "data": {"categories": categories_data}
    }

@router.get("/cities")
async def get_cities(db: Session = Depends(get_db)):
    """Get all cities"""
    
    cities = db.query(City).filter(City.is_active == True).all()
    
    cities_data = [{
        "id": city.id,
        "name": city.name,
        "state": city.state,
        "country": city.country
    } for city in cities]
    
    return {
        "success": True,
        "message": "Cities retrieved",
        "data": {"cities": cities_data}
    }

@router.get("/skills")
async def get_skills(db: Session = Depends(get_db)):
    """Get all skills"""
    
    skills = db.query(Skill).filter(Skill.is_active == True).all()
    
    skills_data = [{
        "id": skill.id,
        "name": skill.name,
        "category": skill.category
    } for skill in skills]
    
    return {
        "success": True,
        "message": "Skills retrieved",
        "data": {"skills": skills_data}
    }

@router.get("/designations")
async def get_designations(db: Session = Depends(get_db)):
    """Get all designations"""
    
    designations = db.query(Designation).filter(Designation.is_active == True).all()
    
    designations_data = [{
        "id": des.id,
        "name": des.name
    } for des in designations]
    
    return {
        "success": True,
        "message": "Designations retrieved",
        "data": {"designations": designations_data}
    }

@router.get("/job-types")
async def get_job_types(db: Session = Depends(get_db)):
    """Get all job types"""
    
    job_types = db.query(JobType).filter(JobType.is_active == True).all()
    
    job_types_data = [{
        "id": jt.id,
        "name": jt.name,
        "description": jt.description
    } for jt in job_types]
    
    return {
        "success": True,
        "message": "Job types retrieved",
        "data": {"job_types": job_types_data}
    }

@router.get("/job-types-filter")
async def get_job_types_for_filter(db: Session = Depends(get_db)):
    """Get job types for filtering (same as job-types)"""
    
    job_types = db.query(JobType).filter(JobType.is_active == True).all()
    
    job_types_data = [{
        "id": jt.id,
        "name": jt.name
    } for jt in job_types]
    
    return {
        "success": True,
        "message": "Job types retrieved",
        "data": {"job_types": job_types_data}
    }

@router.get("/job-levels")
async def get_job_levels(db: Session = Depends(get_db)):
    """Get all job levels"""
    
    job_levels = db.query(JobLevel).filter(JobLevel.is_active == True).all()
    
    job_levels_data = [{
        "id": jl.id,
        "name": jl.name,
        "description": jl.description
    } for jl in job_levels]
    
    return {
        "success": True,
        "message": "Job levels retrieved",
        "data": {"job_levels": job_levels_data}
    }

@router.get("/education-levels")
async def get_education_levels(db: Session = Depends(get_db)):
    """Get all education levels"""
    
    education_levels = db.query(EducationLevel).filter(EducationLevel.is_active == True).all()
    
    education_levels_data = [{
        "id": el.id,
        "name": el.name,
        "description": el.description
    } for el in education_levels]
    
    return {
        "success": True,
        "message": "Education levels retrieved",
        "data": {"education_levels": education_levels_data}
    }

@router.get("/settings")
async def get_app_settings(db: Session = Depends(get_db)):
    """Get app settings"""
    
    settings = db.query(AppSetting).all()
    
    settings_dict = {setting.key: setting.value for setting in settings}
    
    return {
        "success": True,
        "message": "App settings retrieved",
        "data": {"settings": settings_dict}
    }

@router.get("/app-sliders")
async def get_app_sliders(db: Session = Depends(get_db)):
    """Get app sliders/banners"""
    
    sliders = db.query(AppSlider).filter(AppSlider.is_active == True).all()
    
    sliders_data = [{
        "id": slider.id,
        "title": slider.title,
        "image": slider.image,
        "link": slider.link,
        "order": slider.order
    } for slider in sliders]
    
    return {
        "success": True,
        "message": "App sliders retrieved",
        "data": {"sliders": sliders_data}
    }

@router.get("/app-languages")
async def get_app_languages(db: Session = Depends(get_db)):
    """Get available app languages"""
    
    # Return default languages
    languages = [
        {"code": "en", "name": "English", "is_default": True},
        {"code": "es", "name": "Spanish", "is_default": False},
        {"code": "fr", "name": "French", "is_default": False}
    ]
    
    return {
        "success": True,
        "message": "Languages retrieved",
        "data": {"languages": languages}
    }

@router.get("/app-language/terms")
async def get_app_language_terms(language_code: str = Query("en"), db: Session = Depends(get_db)):
    """Get app text translations for a language"""
    
    # Return default English terms (in production, load from database)
    terms = {
        "welcome": "Welcome",
        "login": "Login",
        "signup": "Sign Up",
        "email": "Email",
        "password": "Password",
        "forgot_password": "Forgot Password?",
        "home": "Home",
        "jobs": "Jobs",
        "companies": "Companies",
        "profile": "Profile",
        "apply_now": "Apply Now",
        "search": "Search",
        "filter": "Filter",
        "recent_jobs": "Recent Jobs",
        "popular_jobs": "Popular Jobs",
        "featured_companies": "Featured Companies"
    }
    
    return {
        "success": True,
        "message": "Language terms retrieved",
        "data": {"terms": terms, "language_code": language_code}
    }
