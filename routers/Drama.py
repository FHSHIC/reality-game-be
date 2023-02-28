from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from deta import Deta

router = APIRouter()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
dramadb = deta.Base("drama")

class Drama (BaseModel):
    token:str 

@router.post("/drama")
def get_drama(drama:Drama):
    if drama.token == "":
        raise HTTPException(status_code=403, detail="Please check out if the key is entered correctly")
    if dramadb.get(drama.token) == None:
        raise HTTPException(status_code=403, detail="Please check out if the key is entered correctly")
    dramaText = dramadb.get(Drama.token)["劇情"]
    return {"dramaText":dramaText}

