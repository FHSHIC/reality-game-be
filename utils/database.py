from typing import List
from pydantic import BaseModel
from utils.mockDb import MockDb

dramaDb = MockDb("dramas")
levelDb = MockDb("levels")
hintDb = MockDb("hints")

class DbUser(BaseModel):
    account: str
    password: str
    username: str
    accessToken: str
    expiredTime: str
    gameHistory: list
    userState: dict
    

class UserDb:
    def __init__(self):
        self.db = MockDb("users")
    
    def getUser(self, userId):
        return self.db.find_one(userId)
    
    def registUser(self, user:dict):
        user = DbUser(**user).dict()
        user.update({
            "_id": user["account"]
        })
        return self.db.insert_one(user)
    
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
        return user[0] if len(user) > 0 else None


class DbTeam(BaseModel):
    gamecode: str
    teamName: str
    members: list
    isUsed: bool
    isStart: bool
    nowDramaId: str

class TeamDb:
    def __init__(self):
        self.db = MockDb("teams")
    
    def getTeam(self, teamId: str):
        return self.db.find_one(teamId)
    
    def activeTeam(self, teamId: str):
        self.db.update_one(teamId, {
            "isUsed": True,
        })
        return self.db.find_one(teamId)
    
    def setName(self, teamId: str, teamName: str):
        self.db.update_one(teamId,{
            "teamName": teamName,
        })
        return self.db.find_one(teamId)
    
    def memberJoin(self, teamId: str, userId: str):
        team = self.db.find_one(teamId)
        team["members"].append(userId)
        self.db.update_one(teamId, {
            "members": team["members"]
        })
        return self.db.find_one(teamId)
    
    def deleteFromTeam(self, teamId: str, userId: str):
        team = self.db.find_one(teamId)
        # for i, member in team["members"]:
        #     if member != userId:
        #         continue
        #     del(team["members"][i])
        #     break
        team["member"].remove(userId)
        self.db.update_one(teamId, {
            "members": team["members"]
        })
        return self.db.find_one(teamId)
    
    def updateNowDramaId(self, teamId: str, newDramaId: str):
        team = self.getTeam(teamId)
        if not team:
            return None
        self.db.update_one(teamId, {
            "nowDramaId": newDramaId
        })
        return self.db.find_one(teamId)
        
        
class DbDrama(BaseModel):
    level: str
    levelId: str
    nextDramaId: str
    dramaContent: list

class DramaDb:
    def __init__(self):
        self.db = MockDb("dramas")
        
    def getDrama(self, dramaId: str):
        return self.db.find_one(dramaId)

class DbHint(BaseModel):
    hintContent: str
    
class HintDb:
    def __init__(self):
        self.db = MockDb("hints")
    
    def getHint(self, hintId: str):
        return self.db.find_one(hintId)

class DbLevel(BaseModel):
    answer: str
    hints: list
    nextDramaId: str

class LevelDb:
    def __init__(self):
        self.db = MockDb("levels")
    
    def getLevel(self, levelId: str):
        return self.db.find_one(levelId)
    