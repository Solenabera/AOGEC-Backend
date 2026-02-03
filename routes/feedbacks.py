from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
from services import feedback_management_service

router = APIRouter()

# -------------------------
# Request body models
# -------------------------
class SaveFeedbackRequest(BaseModel):
    category: str
    feedback: str
    rating: str
    fullname: str | None = None
    emailAddress: str | None = None
    
class FetchMyAOAbbreviationTasksRequest(BaseModel):
    emailAddress: EmailStr

# -------------------------
# Endpoints
# -------------------------

@router.post("/give_feedback")
async def save_new_sentence(payload: SaveFeedbackRequest):
    print("Received feedback payload: ", payload)
    category = payload.category.strip()
    feedback = payload.feedback.strip()
    rating = payload.rating.strip()
    fullname = payload.fullname.lower().strip() if payload.fullname else None
    emailAddress = payload.emailAddress.lower().strip() if payload.emailAddress else None

    result = await feedback_management_service.save_feedback(
        category,
        feedback,
        rating,
        fullname,
        emailAddress,
    )

    return {
        "status": "success",
        "msg": "Feedback Submitted successfully.",
        "data": result
    }

# @router.post("/fetch_my_ao_abbreviation_tasks")
# async def fetch_my_ao_abbreviation_tasks(payload: FetchMyAOAbbreviationTasksRequest):
#     result = await feedback_management_service.fetch_my_ao_abbreviation_tasks(
#         emailAddress=payload.emailAddress
#     )

#     return {
#         "status": "success",
#         "msg": "Abbrevations fetched successfully.",
#         "data": result
#     }
