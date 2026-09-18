from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from database import Base


class EventType(enum.Enum):
    checkout = "checkout"
    restock = "restock"
    update = "update"
    create = "create"


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    location = Column(String, nullable=True)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    min_quantity = Column(Integer, default=0, nullable=False)

    history = relationship(
        "PartEvent", back_populates="part", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, default="member", nullable=False)
    hashed_password = Column(String, nullable=False)
    hashed_access_tokens = Column(String, default=list)

    history = relationship("PartEvent", back_populates="user")


class PartEvent(Base):
    __tablename__ = "part_events"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(Enum(EventType), nullable=False)
    quantity = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    part = relationship("Part", back_populates="history")
    user = relationship("User", back_populates="history")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User")


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, default="member", nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    api_events = relationship("APIEvent", back_populates="api_key")

    user = relationship("User")

class APIEvent(Base):
    __tablename__ = "api_events"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    origin_ip = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    api_key = relationship("APIKey", back_populates="api_events")
