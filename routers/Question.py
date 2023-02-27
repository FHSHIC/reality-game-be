from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from deta import Deta
router = APIRouter()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
question = deta.Base("Question")

class Question(BaseModel):
    token:str

@router.post("/")
def get_Question(Question:Question):
    if Question.token == "":
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if question.get(Question.token) == None:
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    a = question.get(Question.token)["題目"]
    return {"message":a}
    



