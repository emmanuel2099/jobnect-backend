from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Resume, Experience, Education, Training, Language, Reference
from app.schemas import (
    ProfileUpdate, ImageUpdate, PersonalInfoUpdate, AddressInfoUpdate, CareerInfoUpdate,
    ExperienceCreate, ExperienceUpdate, EducationCreate, EducationUpdate,
    TrainingCreate, TrainingUpdate, LanguageCreate, LanguageUpdate,
    ReferenceCreate, ReferenceUpdate, SkillsUpdate
)
from app.auth import get_current_user

router = APIRouter()

@router.get("/applicant/resume/details")
async def get_resume_details(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get complete resume details"""
    
    # Get or create resume
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    # Get all related data
    experiences = db.query(Experience).filter(Experience.resume_id == resume.id).all()
    educations = db.query(Education).filter(Education.resume_id == resume.id).all()
    trainings = db.query(Training).filter(Training.resume_id == resume.id).all()
    languages = db.query(Language).filter(Language.resume_id == resume.id).all()
    references = db.query(Reference).filter(Reference.resume_id == resume.id).all()
    
    # Parse skills from JSON
    import json
    skills = []
    if resume.skills:
        try:
            skills = json.loads(resume.skills)
        except:
            skills = []
    
    return {
        "success": True,
        "message": "Resume details retrieved",
        "data": {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone,
                "company": current_user.company,
                "profilePhoto": current_user.profile_photo
            },
            "resume": {
                "id": resume.id,
                "designation": resume.designation,
                "city": resume.city,
                "father_name": resume.father_name,
                "mother_name": resume.mother_name,
                "date_of_birth": str(resume.date_of_birth) if resume.date_of_birth else None,
                "gender": resume.gender,
                "religion": resume.religion,
                "marital_status": resume.marital_status,
                "nationality": resume.nationality,
                "nid": resume.nid,
                "present_address": resume.present_address,
                "permanent_address": resume.permanent_address,
                "objective": resume.objective,
                "present_salary": resume.present_salary,
                "expected_salary": resume.expected_salary,
                "job_level": resume.job_level,
                "job_nature": resume.job_nature,
                "skills": skills
            },
            "experiences": [
                {
                    "id": exp.id,
                    "business": exp.business,
                    "employer": exp.employer,
                    "designation": exp.designation,
                    "department": exp.department,
                    "responsibilities": exp.responsibilities,
                    "start_date": str(exp.start_date),
                    "end_date": str(exp.end_date) if exp.end_date else None
                } for exp in experiences
            ],
            "educations": [
                {
                    "id": edu.id,
                    "level": edu.level,
                    "degree": edu.degree,
                    "institution": edu.institution,
                    "exam": edu.exam,
                    "result": edu.result,
                    "passing_year": edu.passing_year,
                    "start_date": str(edu.start_date),
                    "end_date": str(edu.end_date) if edu.end_date else None
                } for edu in educations
            ],
            "trainings": [
                {
                    "id": tr.id,
                    "title": tr.title,
                    "topics": tr.topics,
                    "institute": tr.institute,
                    "location": tr.location,
                    "start_date": str(tr.start_date),
                    "end_date": str(tr.end_date) if tr.end_date else None
                } for tr in trainings
            ],
            "languages": [
                {
                    "id": lang.id,
                    "language": lang.language,
                    "reading": lang.reading,
                    "writing": lang.writing,
                    "speaking": lang.speaking
                } for lang in languages
            ],
            "references": [
                {
                    "id": ref.id,
                    "name": ref.name,
                    "organization": ref.organization,
                    "designation": ref.designation,
                    "address": ref.address,
                    "phone": ref.phone,
                    "email": ref.email,
                    "relation": ref.relation
                } for ref in references
            ]
        }
    }

@router.post("/applicant/profile/update")
async def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile"""
    
    current_user.name = data.name
    current_user.email = data.email
    current_user.phone = data.phone
    if data.company:
        current_user.company = data.company
    
    db.commit()
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone,
                "company": current_user.company
            }
        }
    }

@router.post("/applicant/image/update")
async def update_profile_image(data: ImageUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update profile photo"""
    
    current_user.profile_photo = data.profile_photo
    db.commit()
    
    return {
        "success": True,
        "message": "Profile photo updated",
        "data": {"profilePhoto": current_user.profile_photo}
    }

@router.post("/resume/update/personal-info")
async def update_personal_info(data: PersonalInfoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update resume personal information"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
    
    if data.father_name: resume.father_name = data.father_name
    if data.mother_name: resume.mother_name = data.mother_name
    if data.date_of_birth: resume.date_of_birth = data.date_of_birth
    if data.gender: resume.gender = data.gender
    if data.religion: resume.religion = data.religion
    if data.marital_status: resume.marital_status = data.marital_status
    if data.nationality: resume.nationality = data.nationality
    if data.nid: resume.nid = data.nid
    
    db.commit()
    
    return {
        "success": True,
        "message": "Personal info updated",
        "data": {}
    }

@router.post("/resume/update/address-info")
async def update_address_info(data: AddressInfoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update resume address information"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
    
    if data.present_address: resume.present_address = data.present_address
    if data.permanent_address: resume.permanent_address = data.permanent_address
    
    db.commit()
    
    return {
        "success": True,
        "message": "Address info updated",
        "data": {}
    }

@router.post("/resume/update/career-info")
async def update_career_info(data: CareerInfoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update resume career information"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
    
    if data.designation: resume.designation = data.designation
    if data.city: resume.city = data.city
    if data.objective: resume.objective = data.objective
    if data.present_salary: resume.present_salary = data.present_salary
    if data.expected_salary: resume.expected_salary = data.expected_salary
    if data.job_level: resume.job_level = data.job_level
    if data.job_nature: resume.job_nature = data.job_nature
    
    db.commit()
    
    return {
        "success": True,
        "message": "Career info updated",
        "data": {}
    }

# Experience endpoints
@router.post("/resume/experience/store")
async def add_experience(data: ExperienceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add work experience"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    experience = Experience(
        resume_id=resume.id,
        business=data.business,
        employer=data.employer,
        designation=data.designation,
        department=data.department,
        responsibilities=data.responsibilities,
        start_date=data.start_date,
        end_date=data.end_date
    )
    
    db.add(experience)
    db.commit()
    
    return {
        "success": True,
        "message": "Experience added",
        "data": {}
    }

@router.post("/resume/experience/update")
async def update_experience(data: ExperienceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update work experience"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    experience = db.query(Experience).filter(Experience.id == data.id, Experience.resume_id == resume.id).first()
    
    if not experience:
        return {"success": False, "message": "Experience not found", "data": {}}
    
    experience.business = data.business
    experience.employer = data.employer
    experience.designation = data.designation
    experience.department = data.department
    experience.responsibilities = data.responsibilities
    experience.start_date = data.start_date
    experience.end_date = data.end_date
    
    db.commit()
    
    return {
        "success": True,
        "message": "Experience updated",
        "data": {}
    }

@router.delete("/resume/experience/delete/{exp_id}")
async def delete_experience(exp_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete work experience"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    experience = db.query(Experience).filter(Experience.id == exp_id, Experience.resume_id == resume.id).first()
    
    if not experience:
        return {"success": False, "message": "Experience not found", "data": {}}
    
    db.delete(experience)
    db.commit()
    
    return {
        "success": True,
        "message": "Experience deleted",
        "data": {}
    }

# Education endpoints
@router.post("/resume/education/store")
async def add_education(data: EducationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add education"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    education = Education(
        resume_id=resume.id,
        level=data.level,
        degree=data.degree,
        institution=data.institution,
        exam=data.exam,
        result=data.result,
        passing_year=data.passing_year,
        start_date=data.start_date,
        end_date=data.end_date
    )
    
    db.add(education)
    db.commit()
    
    return {
        "success": True,
        "message": "Education added",
        "data": {}
    }

@router.post("/resume/education/update")
async def update_education(data: EducationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update education"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    education = db.query(Education).filter(Education.id == data.id, Education.resume_id == resume.id).first()
    
    if not education:
        return {"success": False, "message": "Education not found", "data": {}}
    
    education.level = data.level
    education.degree = data.degree
    education.institution = data.institution
    education.exam = data.exam
    education.result = data.result
    education.passing_year = data.passing_year
    education.start_date = data.start_date
    education.end_date = data.end_date
    
    db.commit()
    
    return {
        "success": True,
        "message": "Education updated",
        "data": {}
    }

@router.delete("/resume/education/delete/{edu_id}")
async def delete_education(edu_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete education"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    education = db.query(Education).filter(Education.id == edu_id, Education.resume_id == resume.id).first()
    
    if not education:
        return {"success": False, "message": "Education not found", "data": {}}
    
    db.delete(education)
    db.commit()
    
    return {
        "success": True,
        "message": "Education deleted",
        "data": {}
    }

# Training endpoints
@router.post("/resume/training/store")
async def add_training(data: TrainingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add training"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    training = Training(
        resume_id=resume.id,
        title=data.title,
        topics=data.topics,
        institute=data.institute,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date
    )
    
    db.add(training)
    db.commit()
    
    return {
        "success": True,
        "message": "Training added",
        "data": {}
    }

@router.post("/resume/training/update")
async def update_training(data: TrainingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update training"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    training = db.query(Training).filter(Training.id == data.id, Training.resume_id == resume.id).first()
    
    if not training:
        return {"success": False, "message": "Training not found", "data": {}}
    
    training.title = data.title
    training.topics = data.topics
    training.institute = data.institute
    training.location = data.location
    training.start_date = data.start_date
    training.end_date = data.end_date
    
    db.commit()
    
    return {
        "success": True,
        "message": "Training updated",
        "data": {}
    }

@router.delete("/resume/training/delete/{training_id}")
async def delete_training(training_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete training"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    training = db.query(Training).filter(Training.id == training_id, Training.resume_id == resume.id).first()
    
    if not training:
        return {"success": False, "message": "Training not found", "data": {}}
    
    db.delete(training)
    db.commit()
    
    return {
        "success": True,
        "message": "Training deleted",
        "data": {}
    }

# Language endpoints
@router.post("/resume/language/store")
async def add_language(data: LanguageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add language"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    language = Language(
        resume_id=resume.id,
        language=data.language,
        reading=data.reading,
        writing=data.writing,
        speaking=data.speaking
    )
    
    db.add(language)
    db.commit()
    
    return {
        "success": True,
        "message": "Language added",
        "data": {}
    }

@router.post("/resume/language/update")
async def update_language(data: LanguageUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update language"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    language = db.query(Language).filter(Language.id == data.id, Language.resume_id == resume.id).first()
    
    if not language:
        return {"success": False, "message": "Language not found", "data": {}}
    
    language.language = data.language
    language.reading = data.reading
    language.writing = data.writing
    language.speaking = data.speaking
    
    db.commit()
    
    return {
        "success": True,
        "message": "Language updated",
        "data": {}
    }

@router.delete("/resume/language/delete/{lang_id}")
async def delete_language(lang_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete language"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    language = db.query(Language).filter(Language.id == lang_id, Language.resume_id == resume.id).first()
    
    if not language:
        return {"success": False, "message": "Language not found", "data": {}}
    
    db.delete(language)
    db.commit()
    
    return {
        "success": True,
        "message": "Language deleted",
        "data": {}
    }

# Reference endpoints
@router.post("/resume/reference/store")
async def add_reference(data: ReferenceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add reference"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    reference = Reference(
        resume_id=resume.id,
        name=data.name,
        organization=data.organization,
        designation=data.designation,
        address=data.address,
        phone=data.phone,
        email=data.email,
        relation=data.relation
    )
    
    db.add(reference)
    db.commit()
    
    return {
        "success": True,
        "message": "Reference added",
        "data": {}
    }

@router.post("/resume/reference/update")
async def update_reference(data: ReferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update reference"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    reference = db.query(Reference).filter(Reference.id == data.id, Reference.resume_id == resume.id).first()
    
    if not reference:
        return {"success": False, "message": "Reference not found", "data": {}}
    
    reference.name = data.name
    reference.organization = data.organization
    reference.designation = data.designation
    reference.address = data.address
    reference.phone = data.phone
    reference.email = data.email
    reference.relation = data.relation
    
    db.commit()
    
    return {
        "success": True,
        "message": "Reference updated",
        "data": {}
    }

@router.delete("/resume/reference/delete/{ref_id}")
async def delete_reference(ref_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete reference"""
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    reference = db.query(Reference).filter(Reference.id == ref_id, Reference.resume_id == resume.id).first()
    
    if not reference:
        return {"success": False, "message": "Reference not found", "data": {}}
    
    db.delete(reference)
    db.commit()
    
    return {
        "success": True,
        "message": "Reference deleted",
        "data": {}
    }

# Skills endpoint
@router.post("/resume/skills/update")
async def update_skills(data: SkillsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update resume skills"""
    import json
    
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    
    # Store skills as JSON array
    resume.skills = json.dumps(data.skills)
    db.commit()
    
    return {
        "success": True,
        "message": "Skills updated successfully",
        "data": {"skills": data.skills}
    }
