"""
User model schemas (Pydantic).
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    experience_level: Optional[str] = "fresher"  # fresher / junior / mid / senior
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    experience_level: Optional[str] = None
