from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class Abbreviations(BaseModel):
    abbreviation: str
    description: str
    emailAddress: EmailStr
    approvalStatus: str = "Pending"
    paymentStatus: str

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
