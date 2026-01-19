import jwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from passlib.context import CryptContext
from app.config import settings

# -----------------------
# Password hashing setup
# -----------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password[:72], hashed)

# -----------------------
# MongoDB setup
# -----------------------
client = None
db = None
users_collection = None

async def init_db():
    global client, db, users_collection
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    users_collection = db["userinfos"]

# -----------------------
# JWT setup
# -----------------------
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

# -----------------------
# Register User
# -----------------------
async def register_user(
    email: str,
    password: str,
    first_name: str,
    middleName: str,
    last_name: str,
    phone_number: str
):
    print(email)
    existing = await users_collection.find_one({"emailAddress": email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_pw = hash_password(password)

    user = {
        "firstName": first_name,
        "middleName": middleName,
        "lastName": last_name,
        "phoneNumber": phone_number,
        "emailAddress": email.lower(),
        "password": hashed_pw,
        "status": "Active",
        "loginAttempt": 0,
        "createdAt": datetime.utcnow(),
        "lastLogin": None,
    }

    await users_collection.insert_one(user)
    return {"message": "User registered successfully."}

# -----------------------
# Login User
# -----------------------
async def login_with_email_password(email: str, password: str):
    user = await users_collection.find_one({"emailAddress": email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="No account found for this Email.")

    if user["status"] == "Restricted":
        raise HTTPException(
            status_code=403,
            detail="Account is restricted due to multiple failed login attempts."
        )

    if user["status"] == "Pending":
        raise HTTPException(
            status_code=403,
            detail="Account is pending. Please complete registration."
        )

    # Verify password
    if not verify_password(password, user["password"]):
        login_attempt = user.get("loginAttempt", 0) + 1
        update = {"loginAttempt": login_attempt}

        if login_attempt >= 5:
            update["status"] = "Restricted"

        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": update}
        )

        raise HTTPException(status_code=401, detail="Incorrect password.")

    # Reset login attempt and update last login
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"loginAttempt": 0, "lastLogin": datetime.utcnow()}}
    )

    # Generate JWT
    token = jwt.encode(
        {
            "sub": str(user["_id"]),
            "emailAddress": user["emailAddress"],
            "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "token": token,
        "personalInfo": {
            "firstName": user["firstName"],
            "middleName": user["middleName"],
            "lastName": user["lastName"],
            "phoneNumber": user["phoneNumber"],
            "emailAddress": user["emailAddress"],
        }
    }
