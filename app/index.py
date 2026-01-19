from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config import settings

from app.routes import text_processing, auth, tasks, word_suggestion

from app.services import auth_service, word_suggestion_service, tasks_management_service

# -----------------------
# FastAPI App
# -----------------------
app = FastAPI(
    title="AOGEC Backend",
    description="Grammar and Spelling Correction API",
    version="1.0.0"
)

# -----------------------
# Startup Event
# -----------------------
@app.on_event("startup")
async def startup_event():
    await auth_service.init_db()    
    await word_suggestion_service.init_db()    
    await tasks_management_service.init_db()
    print("MongoDB client initialized")

# -----------------------
# CORS Middleware
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Include routers
# -----------------------
app.include_router(auth.router, prefix="/api")
app.include_router(text_processing.router, prefix="/api")
app.include_router(word_suggestion.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")

# if __name__ == "__main__":
#     # print(f"Starting AOGEC Backend on http://127.0.0.1:{settings.PORT}")
#     uvicorn.run("app.index:app", host="0.0.0.0", port=settings.PORT, reload=True)
