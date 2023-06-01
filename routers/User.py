import hashlib

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel


from utils.dependencies import verifyAcessToken
from utils.database import UserDb
from utils.dateTime import TimeDate


router = APIRouter(prefix="/user")

userDb = UserDb()

datetime = TimeDate()
defaultExpiredSeconds = 86500

class UserLogin(BaseModel):
    account: str
    password: str

class UserRegist(UserLogin):
    username: str

class UserInfo(BaseModel):
    account: str
    username: str
    accessToken: str
    gameHistory: list
    userState: dict

def generateAccessToken(account, expiredTime):
    return hashlib.sha256(f"{account}-{expiredTime}".encode()).hexdigest()

def generateHashPassword(password):
    return hashlib.sha256(password.encode()).hexdigest()

@router.get("/me", response_model=UserInfo)
async def getCurrentUser(user = Depends(verifyAcessToken)):
    return user

@router.post("/login", response_model=UserInfo)
async def login(user: UserLogin):
    findUser = userDb.getUser(user.account)
    if not findUser:
        raise HTTPException(404, detail="the account or password error...")
    if findUser["password"] != generateHashPassword(user.password):
        raise HTTPException(404, detail="the account or password error...")
    expiredTime = datetime.format(datetime.deltaTime("now", defaultExpiredSeconds))
    accessToken = generateAccessToken(user.account, expiredTime)
    newUser = userDb.updateUserAccessToken(user.account, accessToken, expiredTime)
    return newUser 

@router.post("/regist", response_model=UserInfo)
async def regist(user: UserRegist):
    oldUser = userDb.getUser(user.account)
    if oldUser:
        raise HTTPException(403, detail="user has been registed")
    if user.account == "" or user.password == "" or user.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="user account or password can't be blank.")
    theUser = user.dict()
    expiredTime = datetime.format(datetime.deltaTime("now", defaultExpiredSeconds))
    accessToken = generateAccessToken(user.account, expiredTime)
    theUser.update({
        "password": generateHashPassword(user.password),
        "accessToken": accessToken,
        "expiredTime": expiredTime,
        "gameHistory": [],
        "userState": {
            "gamecode": "",
            "isActive": False,
        }
    })
    print(theUser)
    return userDb.registUser(theUser)