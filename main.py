
# Internship Recommendation API

from fastapi import FastAPI, HTTPException, Body, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import List
from bson import ObjectId
import re
from random import sample

# --- Local imports ---
from models import (
    StudentProfile, StudentProfileCreate, Internship,
    User, UserCreate, Token
)
from database import student_collection, internship_collection, user_collection
from security import (
    get_password_hash, verify_password, create_access_token, decode_access_token
)


# -------------------------------------------------------------------
# FastAPI App Configuration
# -------------------------------------------------------------------
app = FastAPI(
    title="Internship Recommendation API",
    description="API for managing student profiles, authentication, and internship recommendations.",
    version="2.0.0"
)

# Allow CORS (so frontend apps can talk to this API)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 security scheme (used for login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def parse_stipend(stipend_str: str) -> int:
    """Extract numeric stipend value from string."""
    if not isinstance(stipend_str, str):
        return 0
    numbers = re.findall(r'\d{1,3}(?:,\d{3})*|\d+', stipend_str)
    return int(numbers[0].replace(',', '')) if numbers else 0


def parse_duration(duration_str: str) -> int:
    """Extract numeric duration (in months) from string."""
    if not isinstance(duration_str, str):
        return 0
    numbers = re.findall(r'\d+', duration_str)
    return int(numbers[0]) if numbers else 0


# -------------------------------------------------------------------
# Security Dependency
# -------------------------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Verify token and return the current logged-in user.
    Used as a dependency to protect private routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = decode_access_token(token)
    if username is None:
        raise credentials_exception

    user = user_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception

    return user


# -------------------------------------------------------------------
# Public Endpoint - Random Internships
# -------------------------------------------------------------------
@app.get("/internships/random", response_model=List[Internship])
def get_random_internships(count: int = 5):
    """
    Get a random set of internships for the homepage display.
    """
    all_internships = list(internship_collection.find({}))
    if not all_internships:
        return []
    chosen = sample(all_internships, min(count, len(all_internships)))
    return [Internship(**intern) for intern in chosen]


# -------------------------------------------------------------------
# Authentication & User Management
# -------------------------------------------------------------------
@app.post("/users/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate = Body(...)):
    """
    Register a new user (with hashed password).
    """
    existing_user = user_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user_data = {"username": user_data.username, "hashed_password": hashed_password}

    result = user_collection.insert_one(new_user_data)
    created_user = user_collection.find_one({"_id": result.inserted_id})

    return created_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - verifies user credentials and returns a JWT token.
    """
    user = user_collection.find_one({"username": form_data.username})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------------------------------------------------
# Student Profile CRUD (Private Routes)
# -------------------------------------------------------------------
@app.post("/profile", response_model=StudentProfile, status_code=status.HTTP_201_CREATED)
async def create_student_profile(
    student: StudentProfileCreate = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Create a student profile (only if not already created).
    Linked to the logged-in user.
    """
    existing_profile = student_collection.find_one({"owner_username": current_user["username"]})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )

    student_dict = student.model_dump()
    student_dict["owner_username"] = current_user["username"]

    result = student_collection.insert_one(student_dict)
    new_student = student_collection.find_one({"_id": result.inserted_id})
    return new_student


@app.get("/profile", response_model=StudentProfile)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Fetch the profile of the logged-in user.
    """
    profile = student_collection.find_one({"owner_username": current_user["username"]})
    if profile:
        return profile
    raise HTTPException(status_code=404, detail="Student profile not found.")


@app.put("/profile", response_model=StudentProfile)
async def update_my_profile(
    profile_data: StudentProfileCreate = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Update the profile of the logged-in user.
    """
    profile_dict = profile_data.model_dump()
    update_result = student_collection.update_one(
        {"owner_username": current_user["username"]},
        {"$set": profile_dict}
    )

    if update_result.matched_count > 0:
        updated_profile = student_collection.find_one({"owner_username": current_user["username"]})
        return updated_profile

    raise HTTPException(status_code=404, detail="Student profile not found.")


# -------------------------------------------------------------------
# Student Profile CRUD (Admin / Public Routes)
# -------------------------------------------------------------------
@app.get("/profile/{student_id}", response_model=StudentProfile)
async def get_student_profile(student_id: str):
    """Get a student profile by ID."""
    try:
        student = student_collection.find_one({"_id": ObjectId(student_id)})
        if student:
            return student
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")


@app.put("/profile/{student_id}", response_model=StudentProfile)
async def update_student_profile(student_id: str, student_update: StudentProfileCreate = Body(...)):
    """Update a student profile by ID."""
    try:
        update_data = student_update.model_dump(exclude_unset=True)
        result = student_collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": update_data}
        )
        if result.matched_count == 1:
            return student_collection.find_one({"_id": ObjectId(student_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")


@app.delete("/profile/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_profile(student_id: str):
    """Delete a student profile by ID."""
    try:
        result = student_collection.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------------
# Recommendation Endpoint
# -------------------------------------------------------------------
@app.get("/recommendations/{student_id}", response_model=List[Internship])
async def get_recommendations(student_id: str):
    """
    Get recommended internships for a student profile based on:
    - Skills
    - Stipend expectation
    - Preferred locations
    - Internship type
    """
    try:
        student = student_collection.find_one({"_id": ObjectId(student_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")

    student_profile = StudentProfileCreate(**student)
    all_internships = list(internship_collection.find({}))

    filtered_internships = []
    for intern in all_internships:
        stipend_val = parse_stipend(intern.get("Stipend", ""))
        duration_val = parse_duration(intern.get("Duration", ""))

        if stipend_val < student_profile.min_expected_stipend:
            continue
        if duration_val > student_profile.max_duration_months:
            continue
        filtered_internships.append(intern)

    # Score internships
    scored_internships = []
    for intern in filtered_internships:
        score = 0

        # Skill match
        student_skills = set(s.lower() for s in student_profile.skills)
        intern_skills = set(s.lower().strip() for s in str(intern.get("Skills", "")).split(','))
        score += len(student_skills.intersection(intern_skills)) * 10

        # Location match
        student_locations = set(l.lower() for l in student_profile.preferred_locations)
        if any(loc in str(intern.get("Location", "")).lower() for loc in student_locations):
            score += 50

        # Internship type match
        student_types = set(t.lower() for t in student_profile.preferred_intern_types)
        if any(itype in str(intern.get("Intern Type", "")).lower() for itype in student_types):
            score += 20

        if score > 0:
            scored_internships.append({"internship": intern, "score": score})

    sorted_recommendations = sorted(scored_internships, key=lambda x: x["score"], reverse=True)
    return [Internship(**rec["internship"]) for rec in sorted_recommendations[:5]]


# -------------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------------
@app.get("/")
def read_root():
    """Welcome message + docs link."""
    return {"message": "Welcome! Go to /docs for the API documentation."}
