from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("codes.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scanned_serial = Column(String(100), nullable=False, index=True)
    verification_result = Column(String(50), nullable=False, index=True)  # GENUINE, EXPIRED, SUSPICIOUS, INVALID, REVOKED
    risk_score = Column(Integer, default=0, nullable=False)  # 0 to 100
    risk_reasons = Column(Text, nullable=True)  # JSON formatted reasons
    ip_address = Column(String(64), nullable=True)
    device_info = Column(String(255), nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    code = relationship("Code", back_populates="scans")
    user = relationship("User", back_populates="scans")
