from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deta import Deta
app = FastAPI()
deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")
hint = deta.Base("Hint")

class Hint(BaseModel):
    _id:str = None
    hintName:str = None
    hintContent:str = None
    token:str

@app.post("/hint")
def get_Hint(Hint:Hint):
    if Hint.token == "":
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    if hint.get(Hint.token) == None:
        raise HTTPException(status_code=403, detail="請檢查token是否輸入正確")
    hint_text =hint.get(Hint.token)["提示"]
    return {"message":hint_text}
