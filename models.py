# models.py (Updated for Comprehensive Matching)

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from bson import ObjectId
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema
from typing_extensions import Annotated

# This is our robust PyObjectId type. It stays the same.
PyObjectId = Annotated[
    ObjectId,
    PlainSerializer(str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
    BeforeValidator(lambda v: ObjectId(v) if isinstance(v, str) else v),
]

# --- Internship Models ---
# This model now accurately reflects the fields from your new dataset
class InternshipBase(BaseModel):
    Role: str = Field(..., alias='Role')
    CompanyName: str = Field(..., alias='Company Name')
    Location: str = Field(..., alias='Location')
    Duration: str = Field(..., alias='Duration')
    Stipend: str = Field(..., alias='Stipend')
    InternType: Optional[str] = Field(alias='Intern Type') # Made optional as some might be missing
    Skills: Optional[str] = Field(alias='Skills')
    Perks: Optional[str] = Field(alias='Perks')

class Internship(InternshipBase):
    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# --- Student Profile Models ---
class StudentProfileBase(BaseModel):
    name: str
    major: str
    skills: List[str] = []
    
    # --- NEW COMPREHENSIVE PREFERENCE FIELDS ---
    preferred_locations: List[str] = []
    min_expected_stipend: int = 0
    max_duration_months: int = 12 # Default to a year
    preferred_intern_types: List[str] = []
    preferred_perks: List[str] = []

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfile(StudentProfileBase):
    id: PyObjectId = Field(alias="_id")
    owner_username: str
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# models.py (additions at the bottom)

# --- User Models ---

# Base model for a user's common attributes
class UserBase(BaseModel):
    username: str

# Model for creating a new user (receives a plain password)
class UserCreate(UserBase):
    password: str

# Model for the final user response (never includes the password)
class User(UserBase):
    id: PyObjectId = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )



# models.py (add this at the bottom)

# --- Token Model ---

class Token(BaseModel):
    access_token: str
    token_type: str