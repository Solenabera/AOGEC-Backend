from fastapi import Request, HTTPException
from app.services import auth_service

async def check_db_connection(request: Request, call_next):
    if auth_service.client is None:
        # Try to re-init if not connected
        await auth_service.init_db()
        if auth_service.client is None:
            raise HTTPException(status_code=500, detail="Database connection error")

    response = await call_next(request)
    return response
