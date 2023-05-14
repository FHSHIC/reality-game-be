from pydantic import BaseModel
from pymongo import MongoClient
import os

dbUrl = os.environ["DB_URL"]
dbUsername = os.environ["DB_USERNAME"]
dbPassword = os.environ["DB_PASSWORD"]
dbAuthSource = os.environ["DB_AUTH_SOURCE"]

class DataBase():
    def __init__(self, dbName):
        self.__client = MongoClient(dbUrl, username=dbUsername, password=dbPassword, authSource=dbAuthSource)
        self.db = self.__client[dbName]
    
    def getCollection(self, collectionName):
        return self.db[collectionName]

db = DataBase(os.environ["DB_NAME"])
    

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
        self.db = db.getCollection("users")
    
    def getUser(self, userId):
        return self.db.find_one(userId)
    
    def registUser(self, user:dict):
        user = DbUser(**user).dict()
        user.update({
            "_id": user["account"]
        })
        self.db.insert_one(user)
        return self.getUser(user["account"])
    
    def updateUserAccessToken(self, userId, userAccessToken, userExpiredTime):
        self.db.update_one({"_id": userId}, {"$set":{"accessToken": userAccessToken, "expiredTime": userExpiredTime}})
        return self.db.find_one(userId)
    
    def updateUserActiveState(self, userId, partGameCode, isActivate):
        if not isActivate:
            user = self.db.find_one(userId)
            user["gameHistory"].append(partGameCode)
            self.db.update_one({"_id": userId}, {"$set": {"gameHistory": user["gameHistory"]}})
        self.db.update_one({"_id": userId}, {"$set": {"userState": {"gamecode": partGameCode, "isActivate": isActivate}}})
        return self.db.find_one(userId)
    
    def UserCurrentGameFinish(self, userId):
        user = self.getUser(userId)
        user["gameHistory"].append(user["userState"]["gamecode"])
        self.db.update_one({"_id": userId}, {"$set": {"userState": {}, "gameHistory": user["gameHistory"]}})
        return self.db.find_one(userId)
    
    def findAcessToken(self, accessToken):
        user = list(self.db.find({"accessToken": accessToken}))
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
        self.db = db.getCollection("teams")
    
    def getTeam(self, teamId: str):
        return self.db.find_one(teamId)
    
    def activeTeam(self, teamId: str):
        self.db.update_one({"_id": teamId}, {"$set": {
            "isUsed": True,
            "isStart": True,
        }})
        return self.db.find_one(teamId)
    
    def setName(self, teamId: str, teamName: str):
        self.db.update_one({"_id": teamId},{"$set": {
            "teamName": teamName,
        }})
        return self.db.find_one(teamId)
    
    def memberJoin(self, teamId: str, userId: str):
        team = self.db.find_one(teamId)
        team["members"].append(userId)
        self.db.update_one({"_id": teamId}, {"$set": {
            "members": team["members"]
        }})
        return self.db.find_one(teamId)
    
    def deleteFromTeam(self, teamId: str, userId: str):
        team = self.db.find_one(teamId)
        team["member"].remove(userId)
        self.db.update_one({"_id": teamId}, {"$set": {
            "members": team["members"]
        }})
        return self.db.find_one(teamId)
    
    def updateNowDramaId(self, teamId: str, newDramaId: str):
        team = self.getTeam(teamId)
        if not team:
            return None
        self.db.update_one({"_id": teamId}, {"$set": {
            "nowDramaId": newDramaId
        }})
        return self.db.find_one(teamId)
    
    def finishCurrentGame(self, teamId: str):
        team = self.getTeam(teamId)
        if not team:
            return None
        self.db.update_one({"_id": teamId}, {"$set": {
            "isStart": False
        }})
        
        
class DbDrama(BaseModel):
    level: str
    levelId: str
    nextDramaId: str
    dramaContent: list

class DramaDb:
    def __init__(self):
        self.db = db.getCollection("dramas")
        
    def getDrama(self, dramaId: str):
        return self.db.find_one(dramaId)
    
    def getDramas(self):
        return list(self.db.find({}))

class DbHint(BaseModel):
    hintContent: str
    
class HintDb:
    def __init__(self):
        self.db = db.getCollection("hints")
    
    def getHint(self, hintId: str):
        return self.db.find_one(hintId)
    
    def getHints(self):
        return list(self.db.find())

class DbLevel(BaseModel):
    answer: str
    hints: list
    nextDramaId: str

class LevelDb:
    def __init__(self):
        self.db = db.getCollection("levels")
    
    def getLevel(self, levelId: str):
        return self.db.find_one(levelId)
    