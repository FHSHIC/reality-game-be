from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
from deta import Deta
import DetaBase

class AccessToken(BaseModel):
    token: str

class HintID(BaseModel):
    id: str


@router.post("/access_token")
async def create_access_token(access_token: AccessToken):
    if hintdb.get(access_token.token):
        return {"message": "Access token created successfully!"}
    else:
        raise HTTPException(status_code=400, detail="Invalid access token!")


@router.get("/hint/{hint_id}")
async def get_hint_id(hint_id: str):
    hint = hintdb.get(hint_id)
    if hint:
        return hint
    else:
        raise HTTPException(status_code=404, detail="Hint not found!")
    
