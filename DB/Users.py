from typing import List, Union
from pydantic import BaseModel
from __DetaDB import DataBase

class UserDB:
    def __init__(self):
        return DataBase().Base("users")