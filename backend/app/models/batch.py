from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    batch_no = Column(String(100), nullable=False, index=True)
    mfg_date = Column(Date, nullable=False)
    exp_date = Column(Date, nullable=False, index=True)
    quantity = Column(Integer, default=10000, nullable=False)
    mrp = Column(Float, default=50.0, nullable=False)  # Maximum Retail Price in INR
    status = Column(String(50), default="active", nullable=False)  # active, expired, recalled, quarantined
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    medicine = relationship("Medicine", back_populates="batches")
    branch = relationship("Branch", back_populates="batches")
    codes = relationship("Code", back_populates="batch", cascade="all, delete-orphan")
