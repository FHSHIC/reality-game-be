from fastapi import APIRouter, Depends
from pydantic import BaseModel
from utils.database import HintDb

router = APIRouter(
    prefix="/hint"
)

hintDb = HintDb()

@router.get("/{hintId}")
async def getHint(hintId: str):
    return hintDb.getHint(hintId)