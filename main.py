# main.py (Updated with full CRUD operations for profiles)

from fastapi import FastAPI, HTTPException, Body, Response, status
from typing import List
from models import StudentProfile, StudentProfileCreate, Internship
from database import student_collection, internship_collection
from bson import ObjectId
import re
from fastapi.middleware.cors import CORSMiddleware
from models import User, UserCreate # <-- Add User and UserCreate
from database import user_collection # <-- Add user_collection
from security import get_password_hash 
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models import Token # <-- Import our new Token model
from security import verify_password, create_access_token 

from security import decode_access_token 
from fastapi.security import OAuth2PasswordBearer 

from fastapi import FastAPI, Depends, HTTPException






app = FastAPI(
    title="Internship Recommendation API",
    description="An API with multi-factor recommendations.",
    version="2.0.0"
)




origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- HELPER FUNCTIONS for parsing data from the database ---
def parse_stipend(stipend_str: str) -> int:
    if not isinstance(stipend_str, str): return 0
    numbers = re.findall(r'\d{1,3}(?:,\d{3})*|\d+', stipend_str)
    if numbers:
        return int(numbers[0].replace(',', ''))
    return 0

def parse_duration(duration_str: str) -> int:
    if not isinstance(duration_str, str): return 0
    numbers = re.findall(r'\d+', duration_str)
    if numbers:
        return int(numbers[0])
    return 0

# main.py (add this new function)

# --- Security Dependency ---

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency function to get the current user from a token.
    This will be used to protect our routes.
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

# --- STUDENT PROFILE CRUD ENDPOINTS ---

@app.post("/profile", response_model=StudentProfile, status_code=status.HTTP_201_CREATED)
async def create_student_profile(
    student: StudentProfileCreate = Body(...),
    current_user: dict = Depends(get_current_user) # <-- THIS IS THE LOCK
):
    """
    Creates a new student profile for the currently logged-in user.
    """
    # 1. Check if a profile already exists for this user
    existing_profile = student_collection.find_one({"owner_username": current_user["username"]})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A profile for this user already exists. You can update it at /profile/{student_id}."
        )

    # 2. Create the new profile dictionary and link it to the user
    student_dict = student.dict()
    student_dict["owner_username"] = current_user["username"]

    # 3. Insert into the database
    result = student_collection.insert_one(student_dict)
    new_student = student_collection.find_one({"_id": result.inserted_id})
    if new_student:
        return new_student
    
    raise HTTPException(status_code=500, detail="Error creating student profile")

# main.py (add this new function)

# --- USER AUTHENTICATION ENDPOINTS ---

@app.post("/users/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate = Body(...)):
    """
    Registers a new user in the database.
    """
    # Check if user already exists
    existing_user = user_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash the password before storing it
    hashed_password = get_password_hash(user_data.password)

    # Create a new user document
    new_user_data = {
        "username": user_data.username,
        "hashed_password": hashed_password
    }

    # Insert the new user into the database
    result = user_collection.insert_one(new_user_data)

    # Retrieve and return the newly created user (without the password)
    created_user = user_collection.find_one({"_id": result.inserted_id})

    return created_user

# --- NEW: Endpoint to GET a single student profile ---
@app.get("/profile/{student_id}", response_model=StudentProfile)
async def get_student_profile(student_id: str):
    try:
        student = student_collection.find_one({"_id": ObjectId(student_id)})
        if student:
            return student
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")

# --- NEW: Endpoint to UPDATE a student profile ---
@app.put("/profile/{student_id}", response_model=StudentProfile)
async def update_student_profile(student_id: str, student_update: StudentProfileCreate = Body(...)):
    try:
        update_data = student_update.dict(exclude_unset=True)
        result = student_collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": update_data}
        )
        if result.matched_count == 1:
            updated_student = student_collection.find_one({"_id": ObjectId(student_id)})
            return updated_student
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")

# --- NEW: Endpoint to DELETE a student profile ---
@app.delete("/profile/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_profile(student_id: str):
    try:
        result = student_collection.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- RECOMMENDATION ENDPOINT ---

@app.get("/recommendations/{student_id}", response_model=List[Internship])
async def get_recommendations(student_id: str):
    # This function remains the same as before
    try:
        student = student_collection.find_one({"_id": ObjectId(student_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    # ... (rest of the function is unchanged)
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

    scored_internships = []
    for intern in filtered_internships:
        score = 0
        student_skills = set(s.lower() for s in student_profile.skills)
        intern_skills = set(s.lower().strip() for s in str(intern.get("Skills", "")).split(','))
        matching_skills = student_skills.intersection(intern_skills)
        score += len(matching_skills) * 10
        
        student_locations = set(l.lower() for l in student_profile.preferred_locations)
        intern_location = str(intern.get("Location", "")).lower()
        if any(loc in intern_location for loc in student_locations):
            score += 50
        
        student_types = set(t.lower() for t in student_profile.preferred_intern_types)
        intern_type = str(intern.get("Intern Type", "")).lower()
        if any(itype in intern_type for itype in student_types):
            score += 20
            
        if score > 0:
            scored_internships.append({"internship": intern, "score": score})

    sorted_recommendations = sorted(scored_internships, key=lambda x: x["score"], reverse=True)
    top_internships = [Internship(**rec["internship"]) for rec in sorted_recommendations[:5]]
    
    return top_internships

@app.get("/")
def read_root():
    return {"message": "Welcome! Go to /docs for the API documentation."}


# main.py (add this new function)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user and returns an access token.
    """
    # 1. Find the user in the database
    user = user_collection.find_one({"username": form_data.username})

    # 2. Check if user exists and if the password is correct
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. If password is correct, create an access token
    access_token = create_access_token(
        data={"sub": user["username"]}
    )

    # 4. Return the token
    return {"access_token": access_token, "token_type": "bearer"}