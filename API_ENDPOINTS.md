# JobNect API Endpoints Reference

Complete list of all 60+ API endpoints with request/response examples.

---

## Authentication Endpoints

### 1. Register User
**POST** `/api/v10/registration`

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "password": "password123",
  "password_confirmation": "password123",
  "company": "N/A"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "1234567890",
      "company": "N/A",
      "userType": "applicant",
      "profilePhoto": null
    }
  }
}
```

### 2. Login
**POST** `/api/v10/login`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:** Same as registration

### 3. Send Password Reset OTP
**POST** `/api/v10/password-reset-email-verification`

**Request:**
```json
{
  "email": "john@example.com"
}
```

### 4. Reset Password
**POST** `/api/v10/reset-password`

**Request:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "password": "newpassword123"
}
```

---

## Profile & Resume Endpoints

### 5. Get Resume Details
**GET** `/api/v10/applicant/resume/details`

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "success": true,
  "message": "Resume details retrieved",
  "data": {
    "user": {...},
    "resume": {...},
    "experiences": [...],
    "educations": [...],
    "trainings": [...],
    "languages": [...],
    "references": [...]
  }
}
```

### 6. Update Profile
**POST** `/api/v10/applicant/profile/update`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "name": "John Doe Updated",
  "email": "john@example.com",
  "phone": "1234567890",
  "company": "Tech Corp"
}
```

### 7. Update Profile Photo
**POST** `/api/v10/applicant/image/update`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "profile_photo": "https://example.com/photo.jpg"
}
```

### 8. Update Personal Info
**POST** `/api/v10/resume/update/personal-info`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "father_name": "Father Name",
  "mother_name": "Mother Name",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "religion": "Christianity",
  "marital_status": "Single",
  "nationality": "American",
  "nid": "123456789"
}
```

### 9. Update Address Info
**POST** `/api/v10/resume/update/address-info`

**Request:**
```json
{
  "present_address": "123 Main St, City",
  "permanent_address": "456 Home St, Town"
}
```

### 10. Update Career Info
**POST** `/api/v10/resume/update/career-info`

**Request:**
```json
{
  "objective": "Seeking challenging position...",
  "present_salary": "50000",
  "expected_salary": "70000",
  "job_level": "Mid-level",
  "job_nature": "Full-time"
}
```

---

## Experience Endpoints

### 11. Add Experience
**POST** `/api/v10/resume/experience/store`

**Request:**
```json
{
  "business": "Software Development",
  "employer": "Tech Company",
  "designation": "Software Engineer",
  "department": "Engineering",
  "responsibilities": "Developed web applications...",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31"
}
```

### 12. Update Experience
**POST** `/api/v10/resume/experience/update`

**Request:**
```json
{
  "id": 1,
  "business": "Software Development",
  "employer": "Tech Company",
  "designation": "Senior Software Engineer",
  ...
}
```

### 13. Delete Experience
**DELETE** `/api/v10/resume/experience/delete/{id}`

---

## Education Endpoints

### 14. Add Education
**POST** `/api/v10/resume/education/store`

**Request:**
```json
{
  "level": "Bachelor's",
  "degree": "Computer Science",
  "institution": "University Name",
  "exam": "Final Exam",
  "result": "3.8 GPA",
  "passing_year": "2019",
  "start_date": "2015-09-01",
  "end_date": "2019-06-01"
}
```

### 15. Update Education
**POST** `/api/v10/resume/education/update`

### 16. Delete Education
**DELETE** `/api/v10/resume/education/delete/{id}`

---

## Training Endpoints

### 17. Add Training
**POST** `/api/v10/resume/training/store`

**Request:**
```json
{
  "title": "Advanced Python Programming",
  "topics": "Python, Django, FastAPI",
  "institute": "Training Institute",
  "location": "Online",
  "start_date": "2023-01-01",
  "end_date": "2023-03-01"
}
```

### 18. Update Training
**POST** `/api/v10/resume/training/update`

### 19. Delete Training
**DELETE** `/api/v10/resume/training/delete/{id}`

---

## Language Endpoints

### 20. Add Language
**POST** `/api/v10/resume/language/store`

**Request:**
```json
{
  "language": "English",
  "reading": "Fluent",
  "writing": "Fluent",
  "speaking": "Fluent"
}
```

### 21. Update Language
**POST** `/api/v10/resume/language/update`

### 22. Delete Language
**DELETE** `/api/v10/resume/language/delete/{id}`

---

## Reference Endpoints

### 23. Add Reference
**POST** `/api/v10/resume/reference/store`

**Request:**
```json
{
  "name": "Reference Name",
  "organization": "Company Name",
  "designation": "Manager",
  "address": "123 Street",
  "phone": "1234567890",
  "email": "reference@example.com",
  "relation": "Former Manager"
}
```

### 24. Update Reference
**POST** `/api/v10/resume/reference/update`

### 25. Delete Reference
**DELETE** `/api/v10/resume/reference/delete/{id}`

---

## Job Endpoints

### 26. Get Recent Jobs
**GET** `/api/v10/jobs/recent?limit=10`

**Response:**
```json
{
  "success": true,
  "message": "Recent jobs retrieved",
  "data": {
    "jobs": [
      {
        "id": 1,
        "title": "Software Engineer",
        "description": "...",
        "salary_min": 50000,
        "salary_max": 80000,
        "location": "New York",
        "deadline": "2024-12-31",
        "company": {
          "id": 1,
          "name": "Tech Corp",
          "logo": "..."
        },
        "category": {
          "id": 1,
          "name": "IT & Software"
        }
      }
    ]
  }
}
```

### 27. Get Popular Jobs
**GET** `/api/v10/jobs/popular?limit=10`

### 28. Filter Jobs
**GET** `/api/v10/jobs-filter?category_id=1&city_id=2&keyword=developer`

**Query Parameters:**
- `category_id` (optional)
- `city_id` (optional)
- `job_type_id` (optional)
- `job_level_id` (optional)
- `keyword` (optional)
- `limit` (default: 20)

### 29. Get Job Details
**GET** `/api/v10/jobs/details/{id}`

### 30. Get Company Jobs (Protected)
**GET** `/api/v10/job/index`

**Headers:** `Authorization: Bearer {token}`

### 31. Create Job (Protected)
**POST** `/api/v10/job/store`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "company_id": 1,
  "title": "Software Engineer",
  "description": "Job description...",
  "requirements": "Requirements...",
  "responsibilities": "Responsibilities...",
  "category_id": 1,
  "job_type_id": 1,
  "job_level_id": 2,
  "salary_min": 50000,
  "salary_max": 80000,
  "location": "New York",
  "city_id": 1,
  "deadline": "2024-12-31",
  "vacancies": 3,
  "experience_required": "2-3 years"
}
```

### 32. Get Job for Edit (Protected)
**GET** `/api/v10/job/edit/{id}`

### 33. Update Job (Protected)
**POST** `/api/v10/job/update`

### 34. Delete Job (Protected)
**DELETE** `/api/v10/job/delete/{id}`

---

## Application Endpoints

### 35. Apply for Job
**POST** `/api/v10/applicant/job-apply`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "job_id": 1,
  "cover_letter": "I am interested in this position...",
  "resume_file": "https://example.com/resume.pdf"
}
```

### 36. Get Applied Jobs
**GET** `/api/v10/applicant/job/applied`

**Headers:** `Authorization: Bearer {token}`

### 37. Get Bookmarked Jobs
**GET** `/api/v10/applicant/job/bookmarks`

**Headers:** `Authorization: Bearer {token}`

### 38. Toggle Bookmark
**POST** `/api/v10/applicant/job/bookmark/store`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "job_id": 1
}
```

---

## Company Endpoints

### 39. Get All Companies
**GET** `/api/v10/companies?limit=20`

### 40. Get Featured Companies
**GET** `/api/v10/featured-companies?limit=10`

### 41. Get Company Details
**GET** `/api/v10/company/details/{id}`

### 42. Get Company Jobs
**GET** `/api/v10/company/jobs/{id}`

### 43. Get Company Followers
**GET** `/api/v10/company/follower/index`

### 44. Get Company Followings
**GET** `/api/v10/company/following/index`

### 45. Get Company Payments
**GET** `/api/v10/company/payment/index`

### 46. Get Notifications
**GET** `/api/v10/notifications`

**Headers:** `Authorization: Bearer {token}`

---

## Social Links Endpoints

### 47. Get Social Links
**GET** `/api/v10/social-links/index`

**Headers:** `Authorization: Bearer {token}`

### 48. Add Social Link
**POST** `/api/v10/social-links/store`

**Request:**
```json
{
  "platform": "LinkedIn",
  "url": "https://linkedin.com/in/johndoe"
}
```

### 49. Get Social Link for Edit
**GET** `/api/v10/social-links/edit/{id}`

### 50. Update Social Link
**POST** `/api/v10/social-links/update`

**Request:**
```json
{
  "id": 1,
  "platform": "LinkedIn",
  "url": "https://linkedin.com/in/johndoe-updated"
}
```

### 51. Delete Social Link
**DELETE** `/api/v10/social-links/delete/{id}`

---

## KYC Endpoints

### 52. Submit KYC
**POST** `/api/v10/applicant/kyc/store`

**Headers:** `Authorization: Bearer {token}`

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "document_type": "Passport",
  "document_number": "AB123456",
  "document_file": "https://example.com/document.pdf"
}
```

### 53. Get KYC Status
**GET** `/api/v10/applicant/kyc/get/status`

**Headers:** `Authorization: Bearer {token}`

---

## Master Data Endpoints

### 54. Get Job Categories
**GET** `/api/v10/job-category`

**Response:**
```json
{
  "success": true,
  "message": "Job categories retrieved",
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "IT & Software",
        "icon": "💻",
        "description": "Technology jobs"
      }
    ]
  }
}
```

### 55. Get Categories (Filter)
**GET** `/api/v10/categories`

### 56. Get Cities
**GET** `/api/v10/cities`

### 57. Get Skills
**GET** `/api/v10/skills`

### 58. Get Designations
**GET** `/api/v10/designations`

### 59. Get Job Types
**GET** `/api/v10/job-types`

### 60. Get Job Types (Filter)
**GET** `/api/v10/job-types-filter`

### 61. Get Job Levels
**GET** `/api/v10/job-levels`

### 62. Get Education Levels
**GET** `/api/v10/education-levels`

### 63. Get App Settings
**GET** `/api/v10/settings`

### 64. Get App Sliders
**GET** `/api/v10/app-sliders`

### 65. Get App Languages
**GET** `/api/v10/app-languages`

### 66. Get Language Terms
**GET** `/api/v10/app-language/terms?language_code=en`

---

## Response Format

All endpoints return responses in this format:

```json
{
  "success": true,
  "message": "Operation message",
  "data": {
    // Response data
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error message",
  "data": {}
}
```

---

## Authentication

Protected endpoints require JWT token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Get the token from `/registration` or `/login` endpoints.

---

## Testing with cURL

### Example: Register and Get Resume

```bash
# 1. Register
TOKEN=$(curl -X POST http://localhost:8000/api/v10/registration \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "password": "password123",
    "password_confirmation": "password123",
    "company": "N/A"
  }' | jq -r '.data.token')

# 2. Get Resume
curl -X GET http://localhost:8000/api/v10/applicant/resume/details \
  -H "Authorization: Bearer $TOKEN"
```

---

## Endpoint Categories Summary

- **Authentication**: 4 endpoints
- **Profile & Resume**: 6 endpoints
- **Experience**: 3 endpoints (CRUD)
- **Education**: 3 endpoints (CRUD)
- **Training**: 3 endpoints (CRUD)
- **Language**: 3 endpoints (CRUD)
- **Reference**: 3 endpoints (CRUD)
- **Jobs**: 9 endpoints
- **Applications**: 4 endpoints
- **Companies**: 8 endpoints
- **Social Links**: 5 endpoints
- **KYC**: 2 endpoints
- **Master Data**: 13 endpoints

**Total: 66 endpoints**
