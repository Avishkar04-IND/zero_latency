from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Localization(Base):
    __tablename__ = "localizations"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(10), nullable=False, index=True)  # en, hi, mr
    brand_name_local = Column(String(200), nullable=True)
    generic_name_local = Column(String(250), nullable=True)
    indications_local = Column(Text, nullable=True)
    dosage_local = Column(Text, nullable=True)
    warnings_local = Column(Text, nullable=True)
    voice_script = Column(Text, nullable=True)  # Natural TTS script

    # Relationships
    medicine = relationship("Medicine", back_populates="localizations")
