from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from deta import Deta
app = FastAPI()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
leveldb = deta.Base("Answer")

class Answercheck(BaseModel):
    Answer:str
    token:str

# class Level(BaseModel): 
#     _id:str
#     levelName:strˋ
#     # Array[Hint._id] levelHints:List
#     answer:str
#     levelToken:str
#     nextLevelToken:str

@app.post("/Answer")
def get_Answer(Answercheck:Answercheck):
    if Answercheck.token == "":
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if leveldb.get(Answercheck.token) == None:
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if Answercheck.Answer != leveldb.get(Answercheck.token)["答案"]:
        raise HTTPException(status_code=403, detail="請檢查答案是否輸入正確")
    return {"message":"答案正確"}
    
@app.post("/token")
def get_token():
    return {"message":"token已發送"}
