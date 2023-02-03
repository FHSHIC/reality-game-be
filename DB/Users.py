from typing import List, Union
from pydantic import BaseModel
import hashlib
from DetaDB import DetaBase

class UserDB:
    def __init__(self):
        deta = DetaBase()
        self.__user = deta.Base("users")
        return self.__user
    
    def fetchAccessToken(self, accessToken) -> List or None:
        match = self.__user.fetch({"accessToken": accessToken})
        return match.items if match.count > 0 else None
    
    @staticmethod
    def generateAccessToken(email: str, expiredTime: str):
        access = hashlib.sha256()
        access.update(f"{email}-{expiredTime}")
        return access.hexdigest()