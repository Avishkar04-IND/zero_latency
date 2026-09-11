from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.medicine import Medicine
from backend.app.schemas.accessibility import VoiceScriptResponse
from backend.app.services.accessibility_engine import build_voice_script

router = APIRouter(prefix="/accessibility", tags=["Accessibility & Voice"])


@router.get("/medicine/{id}/voice", response_model=VoiceScriptResponse)
def get_medicine_voice_script(
    id: int,
    lang: str = Query("en", description="Language code: 'en' (English), 'hi' (Hindi), or 'mr' (Marathi)"),
    db: Session = Depends(get_db)
):
    """
    Returns voice-ready text strings specifically formatted for Text-to-Speech (TTS),
    TalkBack screen readers, and conversational voice queries.
    Prioritizes English, Hindi, and Marathi.
    """
    med = db.query(Medicine).filter(Medicine.id == id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    return build_voice_script(medicine=med, language=lang)
