from typing import List, Dict
from pydantic import BaseModel


class VoiceSection(BaseModel):
    title: str
    spoken_text: str


class VoiceScriptResponse(BaseModel):
    language: str  # en, hi, mr
    medicine_id: int
    brand_name: str
    generic_name: str
    full_spoken_summary: str
    sections: Dict[str, str]  # overview, composition, dosage, warnings, expiry
    supported_voice_commands: List[str] = [
        "Scan medicine",
        "Repeat",
        "Next",
        "Expiry",
        "Warnings",
        "Go back"
    ]
