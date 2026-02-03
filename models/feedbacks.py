from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class Feedbacks(BaseModel):
    fullname: Optional[str] = None
    emailAddress: Optional[EmailStr] = None
    category: str
    feedback: str
    rating: str

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
