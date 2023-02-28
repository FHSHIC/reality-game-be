from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from deta import Deta
from typing import List

router = APIRouter()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
leveldb = deta.Base("Level")

class Level(BaseModel):
    levelKey:str
    levelid:str
    levelName:str
    levelHints:List
    answer:str
    levelToken:str
    nextLevelToken:str

class Answercheck(BaseModel):
    Answer:str
    token:str

@router.get("/level")
def get_Question(level:Level):
    if leveldb.levelKey == "":
        raise HTTPException(status_code=403, detail="Please check out if the key is entered correctly")
    if leveldb.get(level.levelKey) == None:
        raise HTTPException(status_code=403, detail="Please check out if the key is entered correctly")
    puzzle = leveldb.get(level.levelKey)["puzzle"]
    return {"puzzle":puzzle}
    
@router.post("/Answer")
def get_Answer(Answercheck:Answercheck):
    if Answercheck.token == "":
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if leveldb.get(Answercheck.token) == None:
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if Answercheck.Answer != leveldb.get(Answercheck.token)["answer"]:
        raise HTTPException(status_code=403, detail="請檢查答案是否輸入正確")
    return {"message":"答案正確"}
    
    



