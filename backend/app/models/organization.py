from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    licence_no = Column(String(100), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    medicines = relationship("Medicine", back_populates="organization", cascade="all, delete-orphan")
