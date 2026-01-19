from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class WordSuggestion(BaseModel):
    suggestionWord: str
    fromIPAddress: str
    emailAddress: EmailStr
    approvalStatus: str = "Pending"

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
