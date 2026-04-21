from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

# Auth Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    password_confirmation: str
    company: Optional[str] = "N/A"
    company_logo: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: Optional[str]
    companyLogo: Optional[str]
    userType: str
    profilePhoto: Optional[str]
    
    class Config:
        from_attributes = True

# Profile Schemas
class ProfileUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: Optional[str]

class ImageUpdate(BaseModel):
    profile_photo: str

class PersonalInfoUpdate(BaseModel):
    father_name: Optional[str]
    mother_name: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    religion: Optional[str]
    marital_status: Optional[str]
    nationality: Optional[str]
    nid: Optional[str]

class AddressInfoUpdate(BaseModel):
    present_address: Optional[str]
    permanent_address: Optional[str]

class CareerInfoUpdate(BaseModel):
    designation: Optional[str]
    city: Optional[str]
    objective: Optional[str]
    present_salary: Optional[str]
    expected_salary: Optional[str]
    job_level: Optional[str]
    job_nature: Optional[str]

# Experience Schema
class ExperienceCreate(BaseModel):
    business: str
    employer: str
    designation: str
    department: Optional[str]
    responsibilities: Optional[str]
    start_date: date
    end_date: Optional[date]

class ExperienceUpdate(BaseModel):
    id: int
    business: str
    employer: str
    designation: str
    department: Optional[str]
    responsibilities: Optional[str]
    start_date: date
    end_date: Optional[date]

# Education Schema
class EducationCreate(BaseModel):
    level: str
    degree: str
    institution: str
    exam: Optional[str]
    result: Optional[str]
    passing_year: Optional[str]
    start_date: date
    end_date: Optional[date]

class EducationUpdate(BaseModel):
    id: int
    level: str
    degree: str
    institution: str
    exam: Optional[str]
    result: Optional[str]
    passing_year: Optional[str]
    start_date: date
    end_date: Optional[date]

# Training Schema
class TrainingCreate(BaseModel):
    title: str
    topics: Optional[str]
    institute: str
    location: Optional[str]
    start_date: date
    end_date: Optional[date]

class TrainingUpdate(BaseModel):
    id: int
    title: str
    topics: Optional[str]
    institute: str
    location: Optional[str]
    start_date: date
    end_date: Optional[date]

# Language Schema
class LanguageCreate(BaseModel):
    language: str
    reading: str
    writing: str
    speaking: str

class LanguageUpdate(BaseModel):
    id: int
    language: str
    reading: str
    writing: str
    speaking: str

# Reference Schema
class ReferenceCreate(BaseModel):
    name: str
    organization: str
    designation: str
    address: Optional[str]
    phone: str
    email: EmailStr
    relation: str

class ReferenceUpdate(BaseModel):
    id: int
    name: str
    organization: str
    designation: str
    address: Optional[str]
    phone: str
    email: EmailStr
    relation: str

# Application Schema
class JobApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    resume_file: Optional[str] = None

class BookmarkCreate(BaseModel):
    job_id: int

# KYC Schema
class KYCSubmit(BaseModel):
    first_name: str
    last_name: str
    document_type: str
    document_number: str
    document_file: str

# Social Link Schema
class SocialLinkCreate(BaseModel):
    platform: str
    url: str

class SocialLinkUpdate(BaseModel):
    id: int
    platform: str
    url: str

# Response Schemas
class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# Job Schemas
class JobCreate(BaseModel):
    company_id: int
    title: str
    description: Optional[str]
    requirements: Optional[str]
    responsibilities: Optional[str]
    category_id: Optional[int]
    job_type_id: Optional[int]
    job_level_id: Optional[int]
    salary_min: Optional[float]
    salary_max: Optional[float]
    location: Optional[str]
    city_id: Optional[int]
    deadline: Optional[str]  # Accept string and convert to date in backend
    vacancies: Optional[int] = 1
    experience_required: Optional[str]

class JobUpdate(BaseModel):
    id: int
    title: str
    description: Optional[str]
    requirements: Optional[str]
    responsibilities: Optional[str]
    category_id: Optional[int]
    job_type_id: Optional[int]
    job_level_id: Optional[int]
    salary_min: Optional[float]
    salary_max: Optional[float]
    location: Optional[str]
    city_id: Optional[int]
    deadline: Optional[str]  # Accept string and convert to date in backend
    vacancies: Optional[int]
    experience_required: Optional[str]
    is_active: Optional[bool] = True

# Skills Schema
class SkillsUpdate(BaseModel):
    skills: List[str]
