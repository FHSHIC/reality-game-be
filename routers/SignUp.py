import base64
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr
from deta import Deta
from typing import Union
from datetime import datetime, timedelta
import DetaBase

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
    teamId:str = None


@router.post("/signup")
async def sign_up(signUp:User):
    user = userdb.get(signUp.email)
    if user:
        raise HTTPException(status_code=401, detail="account is already registered")
    newUser = {"key": signUp.email}
    newUser.update(signUp.dict())   
    pwdHash = hashlib.sha256()
    pwdHash.update(signUp.password.encode())
    newUser["password"] = pwdHash.hexdigest()
    now = utc8()
    expired = now + timedelta(days=1)   
    newUser["signInTime"] = now.isoformat(timespec="seconds")
    newUser["expiredTime"] = expired.isoformat(timespec="seconds")
    newUser["accessToken"] = token(newUser["email"], newUser["expiredTime"])
    userdb.put(newUser)
    return {"registration successful":True}