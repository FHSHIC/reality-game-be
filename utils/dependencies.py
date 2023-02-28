from fastapi import HTTPException, status
from utils.dateTime import TimeDate
from utils.database import UserDb

userDb = UserDb()
datetime = TimeDate()

async def verifyAcessToken(accessToken):
    user = UserDb.findAcessToken(accessToken)
    if not user:
        raise HTTPException(401, detail="bad token")
    now = datetime.now()
    userExpiredTime = datetime.toDateTime(user["expiredTime"])
    if datetime.compareAThanB(now, userExpiredTime):
        raise HTTPException(401, detail="token expired")
    return user