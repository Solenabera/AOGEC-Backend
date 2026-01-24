from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
from services import word_suggestion_service

router = APIRouter()

# -------------------------
# Request body models
# -------------------------
class SuggestNewWordRequest(BaseModel):
    newWord: str
    IPAddress: str
    emailAddress: Optional[EmailStr] = None  # optional now

# -------------------------
# Endpoints
# -------------------------
@router.post("/suggest_new_word")
async def suggest_new_word(payload: SuggestNewWordRequest):
    result = await word_suggestion_service.suggest_new_word(
        payload.newWord,
        payload.IPAddress,
        payload.emailAddress,  # may be None
    )
    return {
        "status": "success",
        "msg": "New Word Suggested successfully.",
        "data": result
    }
