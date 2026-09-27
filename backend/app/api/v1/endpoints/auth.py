"""
Authentication endpoints: register, login, profile.
"""

import hashlib
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserLogin, UserProfile, UserUpdate
from app.core.database import get_users_collection

router = APIRouter()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(":")
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hashed
    except Exception:
        return False


@router.post("/register", response_model=UserProfile)
async def register(user: UserCreate):
    col = get_users_collection()
    existing = await col.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "name": user.name,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "target_role": None,
        "target_company": None,
        "experience_level": "fresher",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await col.insert_one(doc)
    return UserProfile(
        id=str(result.inserted_id),
        name=user.name,
        email=user.email,
        created_at=doc["created_at"],
    )


@router.post("/login")
async def login(credentials: UserLogin):
    col = get_users_collection()
    user_doc = await col.find_one({"email": credentials.email})
    if not user_doc or not verify_password(credentials.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "user_id": str(user_doc["_id"]),
        "name": user_doc["name"],
        "email": user_doc["email"],
        "target_role": user_doc.get("target_role"),
        "target_company": user_doc.get("target_company"),
        "experience_level": user_doc.get("experience_level", "fresher"),
        "message": "Login successful",
    }


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str):
    from bson import ObjectId
    col = get_users_collection()
    doc = await col.find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
        target_role=doc.get("target_role"),
        target_company=doc.get("target_company"),
        experience_level=doc.get("experience_level", "fresher"),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


@router.put("/profile/{user_id}", response_model=UserProfile)
async def update_profile(user_id: str, update: UserUpdate):
    from bson import ObjectId
    col = get_users_collection()
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    result = await col.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    doc = await col.find_one({"_id": ObjectId(user_id)})
    return UserProfile(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
        target_role=doc.get("target_role"),
        target_company=doc.get("target_company"),
        experience_level=doc.get("experience_level"),
        updated_at=doc.get("updated_at"),
    )
