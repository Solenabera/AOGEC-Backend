from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserInfo(BaseModel):
    firstName: str
    middleName: Optional[str] = None
    lastName: str
    phoneNumber: str
    emailAddress: EmailStr
    password: str
    status: str
    loginAttempt: int = 0
    lastLogin: datetime = Field(default_factory=datetime.utcnow)
