from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deta import Deta
router = APIRouter()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
hint = deta.Base("Hint")

class Hint(BaseModel):
    token:str

@router.post("/hint")
def get_Hint(Hint:Hint):
    if Hint.token == "":
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if hint.get(Hint.token) == None:
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    hint_text = hint.get(Hint.token)["提示"]
    return {"message":hint_text}
