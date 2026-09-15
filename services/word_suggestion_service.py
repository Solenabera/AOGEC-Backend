import certifi
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from config import settings

# -----------------------
# MongoDB setup
# -----------------------
client = None
db = None
word_suggestions_collection = None

async def init_db():
    global client, db, word_suggestions_collection
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    word_suggestions_collection = db["wordsuggestions"]

# -----------------------
# Suggest New Word
# -----------------------
async def suggest_new_word(
    newWord: str,
    IPAddress: str,
    emailAddress: str | None = None
):
    if word_suggestions_collection is None:
        raise HTTPException(
            status_code=500,
            detail="Database not initialized"
        )

    normalized_word = newWord.strip().lower()

    existing = await word_suggestions_collection.find_one({
        "suggestionWord": normalized_word
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "This word is already suggested.",
                "data": {}
            }
        )

    word = {
        "suggestionWord": normalized_word,
        "fromIPAddress": IPAddress,
        "emailAddress": emailAddress.lower() if emailAddress else None,
        "approvalStatus": "Pending",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }

    await word_suggestions_collection.insert_one(word)

    return {"message": "Word suggested successfully."}
