from pydantic import BaseModel, Field, EmailStr, field_serializer
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Updated PyObjectId for Pydantic v2
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v, info):
        if isinstance(v, ObjectId):
            return str(v)  # Accept ObjectId directly and convert to string
        if not isinstance(v, str) or not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        return {"type": "string"}  # Ensure JSON schema reflects string type

# User Models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},  # Handle ObjectId serialization
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "username": "johndoe",
                    "email": "john@example.com",
                    "role": "user",
                    "password_hash": "hashed_password",
                    "created_at": "2023-01-01T00:00:00"
                }
            ]
        }
    }

    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()

class User(UserBase):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},  # Handle ObjectId serialization
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "username": "johndoe",
                    "email": "john@example.com",
                    "role": "user",
                    "created_at": "2023-01-01T00:00:00"
                }
            ]
        }
    }

    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()

# Project Image Models
class ProjectImageBase(BaseModel):
    project_id: PyObjectId
    image_url: str

class ProjectImageCreate(ProjectImageBase):
    pass

class ProjectImageUpdate(BaseModel):
    image_url: Optional[str] = None

class ProjectImageInDB(ProjectImageBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},  # Handle ObjectId serialization
    }

class ProjectImage(ProjectImageInDB):
    pass

# Project Models
class ProjectBase(BaseModel):
    slug: str
    title: str
    body: str
    github_link: Optional[str] = None
    user_id: PyObjectId

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    github_link: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},  # Handle ObjectId serialization
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "slug": "sample-project",
                    "title": "Sample Project",
                    "body": "Sample project body content",
                    "user_id": "507f1f77bcf86cd799439022",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            ]
        }
    }

    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()

class Project(ProjectInDB):
    images: List[ProjectImage] = []

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},  # Handle ObjectId serialization
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "slug": "sample-project",
                    "title": "Sample Project",
                    "body": "Sample project body content",
                    "user_id": "507f1f77bcf86cd799439022",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "images": []
                }
            ]
        }
    }