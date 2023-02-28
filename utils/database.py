from typing import List
from pydantic import BaseModel
from utils.mockDb import MockDb

userDb = MockDb("users")
dramaDb = MockDb("dramas")
levelDb = MockDb("levels")
hintDb = MockDb("hints")

class UserDb:
    def __init__(self):
        self.db = MockDb("users")
    
    def getUser(self, userId):
        return self.db.find_one(userId)
    
    def updateUserAccessToken(self, userId, userAccessToken, userExpiredTime):
        self.db.update_one(userId, {"accessToken": userAccessToken, "expiredTime": userExpiredTime})
        return self.db.find_one(userId)
    
    def updateUserActiveState(self, userId, partGameCode, isActivate):
        if not isActivate:
            user = self.db.find_one(userId)
            user["gameHistory"].append(partGameCode)
            self.db.update_one(userId, {"gameHistory": user["gameHistory"]})
        self.db.update_one(userId, {"userState": {"gamecode": partGameCode, "isActivate": isActivate}})
        return self.db.find_one(userId)
    
    def findAcessToken(self, accessToken):
        user = self.db.find({"accessToken": accessToken})
        return user if len(user) > 0 else None