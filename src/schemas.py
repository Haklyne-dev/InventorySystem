from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import EventType

# Part Events


class PartEventCreate(BaseModel):
    type: EventType
    quantity: Optional[int] = None
    note: Optional[str] = None


class PartEvent(PartEventCreate):
    id: int
    part_id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Parts


class PartCreate(BaseModel):
    name: str
    quantity: int = 0
    location: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    min_quantity: int = 0


class PartUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    min_quantity: Optional[int] = None


class Part(PartCreate):
    id: int
    history: list[PartEvent] = []

    class Config:
        from_attributes = True


# Users


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: str


class User(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# Authentication


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    invite_code: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    status: str
    message: str


class LogoutRequest(BaseModel):
    token: str


class APIKeyCreate(BaseModel):
    name: str

class APIKeyCreateResponse(BaseModel):
    id: int
    name: str
    key: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class APIKey(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True