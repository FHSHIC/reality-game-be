from typing import List, Union
from pydantic import BaseModel
from __DetaDB import DataBase

class UserInfo(BaseModel):
    username: str
    email: str
    password: str
    accessToken: Union[None, str] = None
    signInTime: Union[None, str] = None
    expiredTime: Union[None, str] = None
    teams: Union[None, List] = None

class UserDB:
    def __init__(self):
        self.users = DataBase().Base("users")
        return self.users