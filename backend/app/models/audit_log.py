from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)  # LOGIN, LOGOUT, REFRESH_TOKEN, BATCH_CREATED, etc.
    entity_type = Column(String(100), nullable=True, index=True)  # user, batch, code, layout, medicine
    entity_id = Column(String(100), nullable=True, index=True)
    
    details = Column(Text, nullable=True)  # JSON-encoded sanitized metadata
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User")
    organization = relationship("Organization")
    branch = relationship("Branch")
