import certifi
from datetime import datetime
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from bson import ObjectId
from config import settings

# -----------------------
# MongoDB setup
# -----------------------
client = None
db = None
feedback_collection = None

async def init_db():
    global client, db, feedback_collection
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    feedback_collection = db["feedbacks"]

# -----------------------
# Helpers
# -----------------------
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc["_id"] = str(doc["_id"])
    return doc

def serialize_docs(docs):
    return [serialize_doc(d) for d in docs]

# -----------------------
# Save New Sentence
# -----------------------
async def save_feedback(
    category: str,
    feedback: str,
    rating: str,
    fullname:  str | None = None,
    emailAddress: str | None = None,
):
    if feedback_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    newFeedback = {
        "fullname":  fullname.lower() if fullname else "Anonymous",
        "emailAddress":  emailAddress.lower() if emailAddress else "Anonymous",
        "category": category.strip(),
        "feedback": feedback.strip(),
        "rating": rating.strip(),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    if emailAddress:
        newFeedback["emailAddress"] = emailAddress.lower()

    result = await feedback_collection.insert_one(newFeedback)
    return {"id": str(result.inserted_id)}

# -----------------------
# Fetch My GEC Tasks
# -----------------------

async def collected_feedbacks():
    if feedback_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    tasks_cursor = feedback_collection.find()
    tasks = await tasks_cursor.to_list(length=None)

    if len(tasks) == 0:
        raise HTTPException(status_code=404, detail="You have no saved feedback!")

    return serialize_docs(tasks)

