import hashlib
from fastapi import APIRouter,HTTPException, Header, exceptions
from typing import Union
from pydantic import BaseModel, EmailStr, constr
from deta import Deta
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
import DetaBase

class SignIn(BaseModel):
    username:str
    email: str
    password: str

@router.post("/signin")
async def sign_in(signIn: SignIn,access_token:str = Header(None)):
    if access_token != userdb.get(signIn.email)["accessToken"]:
        raise HTTPException(status_code=401, detail="verification failed")
    users = userdb.fetch({"email":signIn.email})
    if users.items == []:
        raise HTTPException(status_code=403, detail="請檢查email是否輸入正確")
    password_hash = hashlib.sha256(signIn.password.encode('utf-8')).hexdigest()
    pwd_hash = userdb.fetch({"password":password_hash})
    if pwd_hash.items == []:
        raise HTTPException(status_code=403, detail="請檢查密碼是否輸入正確")
    return {"message":"登入成功"}