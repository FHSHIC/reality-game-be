from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from deta import Deta

app = FastAPI()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
drama = deta.Base("drama")

class Drama (BaseModel):
    _id:str = None
    dramaContent:List[str] = None
    dramaToken:str = None
    nextDramaId:str = None
    token:str 

@app.post("/drama")
def get_drama(Drama:Drama):
    if Drama.token == "":
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if drama.get(Drama.token) == None:
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    drama_text = drama.get(Drama.token)["劇情"]
    return {"message":drama_text}

