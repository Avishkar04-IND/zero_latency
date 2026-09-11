import json
from typing import Dict, Any
from backend.app.models.medicine import Medicine
from backend.app.schemas.accessibility import VoiceScriptResponse


def build_voice_script(medicine: Medicine, language: str = "en") -> VoiceScriptResponse:
    """
    Builds a voice-synthesizer-optimized payload in English, Hindi, or Marathi
    for Flutter TTS, TalkBack, and hands-free voice navigation.
    """
    lang = language.lower().strip()
    if lang not in ["en", "hi", "mr"]:
        lang = "en"

    # Parse active ingredients list
    ingredients_str = ""
    try:
        ingredients = json.loads(medicine.active_ingredients)
        parts = [f"{item.get('name', '')} {item.get('strength', '')} {item.get('unit', '')}" for item in ingredients]
        ingredients_str = ", ".join(parts)
    except Exception:
        ingredients_str = medicine.strength

    if lang == "hi":
        # Hindi voice payload
        summary = medicine.voice_summary_hi or (
            f"यह दवा {medicine.brand_name} है। इसका जेनेरिक नाम {medicine.generic_name} है। "
            f"यह {medicine.indications} के उपचार के लिए उपयोग की जाती है।"
        )
        sections = {
            "overview": f"दवा का नाम: {medicine.brand_name}, ताकत: {medicine.strength}।",
            "composition": f"सक्रिय सामग्री: {ingredients_str}। गोलियों का प्रकार: {medicine.dosage_form}।",
            "dosage": f"खुराक: {medicine.dosage_instructions}।",
            "warnings": f"चेतावनी: {medicine.warnings_and_precautions}।",
            "storage": f"रखरखाव: {medicine.storage_conditions}।"
        }
    elif lang == "mr":
        # Marathi voice payload
        summary = medicine.voice_summary_mr or (
            f"हे औषध {medicine.brand_name} आहे. याचे जेनेरिक नाव {medicine.generic_name} आहे. "
            f"हे {medicine.indications} च्या उपचारासाठी वापरले जाते."
        )
        sections = {
            "overview": f"औषधाचे नाव: {medicine.brand_name}, क्षमता: {medicine.strength}।",
            "composition": f"घटक: {ingredients_str}। प्रकार: {medicine.dosage_form}।",
            "dosage": f"डोस: {medicine.dosage_instructions}।",
            "warnings": f"सावधानता: {medicine.warnings_and_precautions}।",
            "storage": f"साठवण: {medicine.storage_conditions}।"
        }
    else:
        # Default English voice payload
        summary = medicine.voice_summary_en or (
            f"Medicine: {medicine.brand_name}, generic name {medicine.generic_name}, strength {medicine.strength}. "
            f"Used for {medicine.indications}."
        )
        sections = {
            "overview": f"Medicine: {medicine.brand_name}. Generic: {medicine.generic_name}. Strength: {medicine.strength}.",
            "composition": f"Active contents: {ingredients_str}. Physical form: {medicine.tablet_shape}, {medicine.coating_type} tablet.",
            "dosage": f"Dosage directions: {medicine.dosage_instructions}",
            "warnings": f"Important precautions: {medicine.warnings_and_precautions}",
            "storage": f"Storage: {medicine.storage_conditions}"
        }

    return VoiceScriptResponse(
        language=lang,
        medicine_id=medicine.id,
        brand_name=medicine.brand_name,
        generic_name=medicine.generic_name,
        full_spoken_summary=summary,
        sections=sections
    )
