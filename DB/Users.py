from typing import List, Union
from pydantic import BaseModel
import hashlib
from __DetaDB import DataBase

class UserDB:
    def __init__(self):
        return DataBase().Base("users")
    
    @staticmethod
    def generateAccessToken(email: str, expiredTime: str):
        access = hashlib.sha256()
        access.update(f"{email}-{expiredTime}")
        return access.hexdigest()