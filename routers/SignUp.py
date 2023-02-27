import base64
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr
from deta import Deta
from typing import Union
from datetime import datetime, timedelta

deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
db = deta.Base("users")
router = APIRouter()

def utc8() -> datetime:
    return datetime.utcnow() + timedelta(hours=8)

def token(email: str, expiredTime: str) -> str:
    hash = hashlib.sha256()
    hash.update(f"{email}/{expiredTime}".encode())
    return hash.hexdigest()

class User(BaseModel):
    email:EmailStr
    username:str
    password:str
    accessToken:str
    teamId:str


@router.post("/signup")
async def sign_up(SignUp:User):
    user = db.get(SignUp.email)
    if user:
        raise HTTPException(status_code=403, detail="帳號已註冊")
    newUser = {"key": SignUp.email}
    newUser.update(SignUp.dict())   
    pwdHash = hashlib.sha256()
    pwdHash.update(SignUp.password.encode())
    newUser["password"] = pwdHash.hexdigest()
    now = utc8()
    expired = now + timedelta(days=1)
    newUser["signInTime"] = now.isoformat(timespec="seconds")
    newUser["expiredTime"] = expired.isoformat(timespec="seconds")
    newUser["accessToken"] = token(newUser["email"], newUser["expiredTime"])
    db.put(newUser)
    return {"message":"註冊成功"}