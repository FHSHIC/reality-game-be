import hashlib

from fastapi import APIRouter,HTTPException, Header
from typing import Union
from pydantic import BaseModel, EmailStr, constr
from deta import Deta
from datetime import datetime, timedelta

router = APIRouter(prefix="/user", tags=["user"])

deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
db = deta.Base("users") 

class SignIn(BaseModel):
    email: str
    password: str

@router.post("/signin")
async def sign_in(SignIn: SignIn,access_token:str = Header(None)):
    if access_token != db.get(SignIn.email)["accessToken"]:
         raise HTTPException(status_code=401, detail="驗證失敗")
    users = db.fetch({"email":SignIn.email})
    if users.items == []:
        raise HTTPException(status_code=403, detail="請檢查email是否輸入正確")
    password_hash = hashlib.sha256(SignIn.password.encode('utf-8')).hexdigest()
    pwd_hash = db.fetch({"password":password_hash})
    if pwd_hash.items == []:
        raise HTTPException(status_code=403, detail="請檢查密碼是否輸入正確")
    return {"message":"登入成功"}