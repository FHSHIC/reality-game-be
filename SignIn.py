# -*- coding: UTF-8 -*-
import hashlib

from fastapi import FastAPI,HTTPException, Header
from typing import Union
from pydantic import BaseModel, EmailStr, constr
from deta import Deta
from datetime import datetime, timedelta

app = FastAPI()

deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
db = deta.Base("users") 
drama = deta.Base("drama")
puzzle = deta.Base("puzzle")
def utc8() -> datetime:
    return datetime.utcnow() + timedelta(hours=8)

def token(email: str, expiredTime: str) -> str:
    hash = hashlib.sha256()
    hash.update(f"{email}/{expiredTime}".encode())
    return hash.hexdigest()

class SignUp(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=16)
class SignIn(BaseModel):
    email: str
    password: str
# Team {
#     String _id = self.gameCode
#     String gameCode
#     String teamName
#     String spendingTime
#     String teamStatus: ["pending", "fin", "alive"]
#     String nowLevelId
#     Array[User._id] member
# }

@app.post("/signup")
async def sign_up(SignUp: SignUp):
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

@app.post("/signin")
async def sign_in(SignIn: SignIn,access_token:str = Header(None)):
    if access_token != db.get(SignIn.email)["accessToken"]:
         raise HTTPException(status_code=401, detail="驗證失敗")
    #檢驗access_token是否存在
    users = db.fetch({"email":SignIn.email})
    # #聲明user是db裡的SingIn.email
    if users.items == []:
        raise HTTPException(status_code=403, detail="請檢查email是否輸入正確")
    # #如果找不到email，回傳錯誤訊息
    password_hash = hashlib.sha256(SignIn.password.encode('utf-8')).hexdigest()
    pwd_hash = db.fetch({"password":password_hash})
    if pwd_hash.items == []:
        raise HTTPException(status_code=403, detail="請檢查密碼是否輸入正確")
    return {"message":"登入成功"}