from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deta import Deta

router = APIRouter()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
leveldb = deta.Base("Level")

class Level(BaseModel):
    answer: str
    levelToken: str
    nextlevelToken: str

@router.post("/check_answer")
async def check_answer(levelName: str, answer: str):
    level = leveldb.get(levelName)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    expected_answer = level["answer"]
    if answer != expected_answer:
        return {"message": "請檢查答案是否輸入正確"}
    next_level_token = level["nextlevelToken"]
    return {"message": "答案正確", "nextLevelToken": next_level_token}
