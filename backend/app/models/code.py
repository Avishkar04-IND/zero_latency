from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    code_hash = Column(String(128), nullable=False, index=True)  # SHA-256 HMAC for anti-tamper validation
    qr_data_url = Column(Text, nullable=True)  # Base64 PNG data URI for immediate UI rendering
    qr_svg = Column(Text, nullable=True)  # Scalable vector graphic for print assets
    datamatrix_code = Column(String(255), nullable=True)  # GS1 standard format string
    status = Column(String(50), default="active", nullable=False)  # active, revoked, scratched, recalled
    scan_count = Column(Integer, default=0, nullable=False)
    first_scanned_at = Column(DateTime, nullable=True)
    last_scanned_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    batch = relationship("Batch", back_populates="codes")
    scans = relationship("Scan", back_populates="code", cascade="all, delete-orphan")
