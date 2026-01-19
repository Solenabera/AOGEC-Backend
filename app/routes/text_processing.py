from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services import text_processing_service

router = APIRouter()

class TextRequest(BaseModel):
    userInputText: str

@router.get("/test")
def test_backend():
    return {"message": "Hello! This is test from the backend!"}

@router.post("/check-user-text")
def check_user_text(payload: TextRequest):
    text = payload.userInputText.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No Text to Process!")

    corrected = text_processing_service.check_and_correct("grammar: " + text)
    return {
        "status": "success",
        "data": {"inputText": text, "predictedText": corrected},
        "msg": "Text Processed Successfully!"
    }

@router.post("/process-user-text")
def process_user_text(payload: TextRequest):
    text = payload.userInputText.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No Text to Process!")

    final_result = text_processing_service.process_text(text)
    return {
        "status": "success",
        "data": final_result,
        "msg": "Text Processed Successfully!"
    }

@router.get("/autocomplete")
def autocomplete_api(q: str = Query(default="")):
    return {"suggestions": text_processing_service.autocomplete_suggestions(q)}
