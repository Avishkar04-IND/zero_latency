from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Core Identification
    brand_name = Column(String(200), nullable=False, index=True)
    generic_name = Column(String(250), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # Analgesic, Antibiotic, Antidiabetic, etc.
    manufacturer = Column(String(250), nullable=False)
    dosage_form = Column(String(50), default="Tablet", nullable=False)  # Tablet, Capsule, Syrup, etc.
    strength = Column(String(100), nullable=False)  # e.g., "650 mg", "500 mg / 125 mg"
    
    # Tablet Content & Chemical Composition (as specified)
    # Stored as JSON string: [{"name": "Paracetamol IP", "strength": "650", "unit": "mg", "purpose": "Active Ingredient"}]
    active_ingredients = Column(Text, nullable=False)
    # Stored as JSON list: ["Microcrystalline Cellulose", "Povidone K-30", "Magnesium Stearate", "Colloidal Silicon Dioxide"]
    inactive_excipients = Column(Text, nullable=True)
    
    # Physical Specifications of the Tablet
    tablet_shape = Column(String(50), default="Round", nullable=True)  # Round, Oblong, Capsule-shaped, Oval
    tablet_color = Column(String(50), default="White", nullable=True)
    score_line = Column(String(100), default="None", nullable=True)  # Single score, Bi-sected, None
    coating_type = Column(String(100), default="Film-coated", nullable=True)  # Film-coated, Enteric, Uncoated, Dispersible
    
    # Clinical Information & Safety
    indications = Column(Text, nullable=False)  # What the tablet treats
    dosage_instructions = Column(Text, nullable=False)
    warnings_and_precautions = Column(Text, nullable=False)
    side_effects = Column(Text, nullable=True)
    storage_conditions = Column(String(255), default="Store below 30°C in a dry place. Protect from light.", nullable=True)
    schedule_type = Column(String(100), default="Schedule H", nullable=True)  # Schedule H (Prescription), OTC, Schedule G
    
    # Accessibility Voice Summaries (Voice-ready text for screen readers & Flutter TTS)
    voice_summary_en = Column(Text, nullable=True)
    voice_summary_hi = Column(Text, nullable=True)
    voice_summary_mr = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    organization = relationship("Organization", back_populates="medicines")
    batches = relationship("Batch", back_populates="medicine", cascade="all, delete-orphan")
    localizations = relationship("Localization", back_populates="medicine", cascade="all, delete-orphan")
