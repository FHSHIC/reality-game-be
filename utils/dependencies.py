from fastapi import HTTPException, status, Header
from utils.dateTime import TimeDate
from utils.database import UserDb

userDb = UserDb()
datetime = TimeDate()

async def verifyAcessToken(access_token: str =  Header()):
    user = userDb.findAcessToken(access_token)
    if not user:
        raise HTTPException(401, detail="bad token")
    now = datetime.now()
    userExpiredTime = datetime.toDateTime(user["expiredTime"])
    if datetime.compareAThanB(now, userExpiredTime):
        raise HTTPException(401, detail="token expired")
    return user