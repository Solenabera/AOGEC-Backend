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

class SaveNewAbbreviationRequest(BaseModel):
    abbreviation: str
    description: str
    emailAddress: Optional[EmailStr] = None  # optional

class FetchMyAOAbbreviationTasksRequest(BaseModel):
    emailAddress: EmailStr

class UpdateAOAbrreviationTaskRequest(BaseModel):
    id: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    emailAddress: Optional[EmailStr] = None
    
class DeleteAOAbrreviationTaskRequest(BaseModel):
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

@router.post("/save_new_abbreviation")
async def save_new_sentence(payload: SaveNewAbbreviationRequest):
    abbreviation = payload.abbreviation.strip()
    description = payload.description.strip()
    email = payload.emailAddress.lower().strip() if payload.emailAddress else None

    result = await tasks_management_service.save_new_abbreviation(
        abbreviation,
        description,
        email,
    )

    return {
        "status": "success",
        "msg": "Abbreviation saved successfully.",
        "data": result
    }

@router.post("/fetch_my_ao_abbreviation_tasks")
async def fetch_my_ao_abbreviation_tasks(payload: FetchMyAOAbbreviationTasksRequest):
    result = await tasks_management_service.fetch_my_ao_abbreviation_tasks(
        emailAddress=payload.emailAddress
    )

    return {
        "status": "success",
        "msg": "Abbrevations fetched successfully.",
        "data": result
    }

@router.put("/update_ao_abbreviation_task")
async def update_ao_abbreviation_task(payload: UpdateAOAbrreviationTaskRequest):
    result = await tasks_management_service.update_ao_abbreviation_task(
        _id=payload.id,   # <-- use id here
        abbreviation=payload.abbreviation,
        description=payload.description,
        emailAddress=payload.emailAddress,
    )
    return {"status": "success", "msg": "Task updated successfully.", "data": result}

@router.delete("/delete_ao_abbreviation_task")
async def delete_ao_abbreviation_task(payload: DeleteAOAbrreviationTaskRequest):
    result = await tasks_management_service.delete_ao_abbreviation_task(
        _id=payload.id
    )

    return {
        "status": "success",
        "msg": "Task deleted successfully.",
        "data": result
    }
