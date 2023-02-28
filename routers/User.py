from fastapi import APIRouter

router = APIRouter(prefix="/user")

@router.get("/me")
async def getCurrentUser():
    return {"user": "me"}