from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database.session import Base


class UserProfile(Base):

    __tablename__ = "user_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    key = Column(
        String,
        unique=True,
        index=True
    )

    value = Column(
        String
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class EventMemory(Base):

    __tablename__ = "event_memories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_type = Column(
        String
    )

    description = Column(
        Text
    )

    related_doc = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )