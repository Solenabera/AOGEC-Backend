from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
from services import tasks_management_service

router = APIRouter()

# -------------------------
# Request body models
# -------------------------
class SaveNewSentenceRequest(BaseModel):
    correctSentence: str
    incorrectSentence: str
    errorType: str
    emailAddress: Optional[EmailStr] = None  # optional

class UpdateGECTaskRequest(BaseModel):
    id: str
    correctSentence: Optional[str] = None
    incorrectSentence: Optional[str] = None
    errorType: Optional[str] = None
    emailAddress: Optional[EmailStr] = None

class FetchMyGECTasksRequest(BaseModel):
    emailAddress: EmailStr

class DeleteGECTaskRequest(BaseModel):
    id: str

# -------------------------
# Endpoints
# -------------------------

@router.post("/save_new_sentence")
async def save_new_sentence(payload: SaveNewSentenceRequest):
    correct_sentence = payload.correctSentence.strip()
    incorrect_sentence = payload.incorrectSentence.strip()
    error_type = payload.errorType.strip()
    email = payload.emailAddress.lower().strip() if payload.emailAddress else None

    result = await tasks_management_service.save_new_sentence(
        correct_sentence,
        incorrect_sentence,
        error_type,
        email,
    )

    return {
        "status": "success",
        "msg": "Sentence saved successfully.",
        "data": result
    }

@router.put("/update_gec_task")
async def update_gec_task(payload: UpdateGECTaskRequest):
    result = await tasks_management_service.update_my_gec_task(
        _id=payload.id,   # <-- use id here
        correctSentence=payload.correctSentence,
        incorrectSentence=payload.incorrectSentence,
        errorType=payload.errorType,
        emailAddress=payload.emailAddress,
    )
    return {"status": "success", "msg": "Task updated successfully.", "data": result}

@router.post("/fetch_my_gec_tasks")
async def fetch_my_gec_tasks(payload: FetchMyGECTasksRequest):
    result = await tasks_management_service.fetch_my_gec_tasks(
        emailAddress=payload.emailAddress
    )

    return {
        "status": "success",
        "msg": "Sentences fetched successfully.",
        "data": result
    }

@router.delete("/delete_gec_task")
async def delete_gec_task(payload: DeleteGECTaskRequest):
    result = await tasks_management_service.delete_my_gec_task(
        _id=payload.id
    )

    return {
        "status": "success",
        "msg": "Task deleted successfully.",
        "data": result
    }
