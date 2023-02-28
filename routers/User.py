from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/user")

class UserLogin(BaseModel):
    account: str
    password: str

@router.get("/me")
async def getCurrentUser():
    return {"user": "me"}

@router.post("/login")
async def login(user: UserLogin):
    return user.dict()