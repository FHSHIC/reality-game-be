from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
from deta import Deta

app = FastAPI()
router = APIRouter()

deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
dramadb = deta.Base("drama")


class AccessToken(BaseModel):
    token: str

class DramaID(BaseModel):
    id: str


@router.post("/access_token")
async def create_access_token(access_token: AccessToken):
    if dramadb.get(access_token.token):
        return {"message": "Access token created successfully!"}
    else:
        raise HTTPException(status_code=400, detail="Invalid access token!")


@router.get("/drama/{drama_id}")
async def get_drama_by_id(drama_id: str):
    drama = dramadb.get(drama_id)
    if drama:
        return drama
    else:
        raise HTTPException(status_code=404, detail="Drama not found!")
    
