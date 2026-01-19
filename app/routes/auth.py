from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, constr
from app.services import auth_service

router = APIRouter()

# -------------------------
# Request body models
# -------------------------
class LoginRequest(BaseModel):
    emailAddress: EmailStr
    password: constr(min_length=8)

class SignupRequest(BaseModel):
    emailAddress: EmailStr
    password: constr(min_length=8)
    firstName: str
    middleName: str
    lastName: str
    phoneNumber: str

# -------------------------
# Endpoints
# -------------------------
@router.post("/login_user")
async def login_user(payload: LoginRequest):
    print("Logging in...")
    result = await auth_service.login_with_email_password(payload.emailAddress, payload.password)
    return {
        "status": "success",
        "msg": "Login successful.",
        "data": result
    }

@router.post("/register_user")
async def register_user(payload: SignupRequest):
    result = await auth_service.register_user(
        payload.emailAddress,
        payload.password,
        payload.firstName,
        payload.middleName,
        payload.lastName,
        payload.phoneNumber
    )
    return {
        "status": "success",
        "msg": "Signup successful.",
        "data": result
    }
