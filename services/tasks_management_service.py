from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from bson import ObjectId
from config import settings

# -----------------------
# MongoDB setup
# -----------------------
client = None
db = None
sentences_collection = None
abbreviations_collection = None

async def init_db():
    global client, db, sentences_collection, abbreviations_collection
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    sentences_collection = db["sentences"]
    abbreviations_collection = db["abbreviations"]

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
async def save_new_sentence(
    correctSentence: str,
    incorrectSentence: str,
    errorType: str,
    emailAddress: str | None = None
):
    if sentences_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    normalized_sentence = correctSentence.strip().lower()

    existing = await sentences_collection.find_one({"correctSentence": normalized_sentence})
    if existing:
        raise HTTPException(status_code=400, detail="This sentence is already saved.")

    newSentence = {
        "correctSentence": correctSentence.strip(),
        "incorrectSentence": incorrectSentence.strip(),
        "errorType": errorType.strip(),
        "approvalStatus": "Pending",
        "paymentStatus": "Pending",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    if emailAddress:
        newSentence["emailAddress"] = emailAddress.lower()

    result = await sentences_collection.insert_one(newSentence)
    return {"id": str(result.inserted_id)}

# -----------------------
# Update GEC Task
# -----------------------
async def update_my_gec_task( 
    _id: str, 
    correctSentence: str | None = None, 
    incorrectSentence: str | None = None, 
    errorType: str | None = None, 
    emailAddress: str | None = None 
):
    if sentences_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    existing_task = await sentences_collection.find_one({"_id": ObjectId(_id)})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found.")

    if correctSentence:
        duplicate = await sentences_collection.find_one({
            "correctSentence": correctSentence.strip(),
            "_id": {"$ne": ObjectId(_id)}
        })
        if duplicate:
            raise HTTPException(status_code=409, detail="This sentence is already registered!")

    update_fields = {}
    if correctSentence: update_fields["correctSentence"] = correctSentence.strip()
    if incorrectSentence: update_fields["incorrectSentence"] = incorrectSentence.strip()
    if errorType: update_fields["errorType"] = errorType.strip()
    if emailAddress: update_fields["emailAddress"] = emailAddress.lower()
    update_fields["updatedAt"] = datetime.utcnow()

    await sentences_collection.update_one({"_id": ObjectId(_id)}, {"$set": update_fields})
    return {"id": _id}

# -----------------------
# Fetch My GEC Tasks
# -----------------------
async def fetch_my_gec_tasks(emailAddress: str):
    if sentences_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    tasks_cursor = sentences_collection.find({"emailAddress": emailAddress.lower()})
    tasks = await tasks_cursor.to_list(length=None)

    if len(tasks) == 0:
        raise HTTPException(status_code=404, detail="You have no saved tasks!")

    return serialize_docs(tasks)

# -----------------------
# Delete My GEC Task
# -----------------------
async def delete_my_gec_task(_id: str):
    if sentences_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    result = await sentences_collection.delete_one({"_id": ObjectId(_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No Task available with this ID!")

    return {"id": _id}

# -----------------------
# Save AO Abbreviation Task
# -----------------------
async def save_new_abbreviation(
    abbreviation: str,
    description: str,
    emailAddress: str | None = None
):
    if abbreviations_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    normalized_abbreviation = abbreviation.strip().lower()

    existing = await abbreviations_collection.find_one({"abbreviation": normalized_abbreviation})
    if existing:
        raise HTTPException(status_code=400, detail="This Abbreviation is already saved.")

    newAbbreviation = {
        "abbreviation": abbreviation.strip(),
        "description": description.strip(),
        "approvalStatus": "Pending",
        "paymentStatus": "Pending",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    if emailAddress:
        newAbbreviation["emailAddress"] = emailAddress.lower()

    result = await abbreviations_collection.insert_one(newAbbreviation)
    return {"id": str(result.inserted_id)}

# -----------------------
# Fetch AO Abbreviation Tasks
# -----------------------
async def fetch_my_ao_abbreviation_tasks(emailAddress: str):
    if abbreviations_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    tasks_cursor = abbreviations_collection.find({"emailAddress": emailAddress.lower()})
    tasks = await tasks_cursor.to_list(length=None)

    if len(tasks) == 0:
        raise HTTPException(status_code=404, detail="You have no saved tasks!")

    return serialize_docs(tasks)

# -----------------------
# Update Abbreviation Task
# -----------------------
async def update_ao_abbreviation_task( 
    _id: str, 
    abbreviation: str | None = None, 
    description: str | None = None, 
    emailAddress: str | None = None 
):
    if abbreviations_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    existing_task = await abbreviations_collection.find_one({"_id": ObjectId(_id)})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found.")

    if abbreviation:
        duplicate = await abbreviations_collection.find_one({
            "abbreviation": abbreviation.strip(),
            "_id": {"$ne": ObjectId(_id)}
        })
        if duplicate:
            raise HTTPException(status_code=409, detail="This Abbreviation is already registered!")

    update_fields = {}
    if abbreviation: update_fields["abbreviation"] = abbreviation.strip()
    if description: update_fields["description"] = description.strip()
    if emailAddress: update_fields["emailAddress"] = emailAddress.lower()
    update_fields["updatedAt"] = datetime.utcnow()

    await abbreviations_collection.update_one({"_id": ObjectId(_id)}, {"$set": update_fields})
    return {"id": _id}

# -----------------------
# Delete Abbreviation Task
# -----------------------
async def delete_ao_abbreviation_task(_id: str):
    if abbreviations_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    result = await abbreviations_collection.delete_one({"_id": ObjectId(_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No Task available with this ID!")

    return {"id": _id}