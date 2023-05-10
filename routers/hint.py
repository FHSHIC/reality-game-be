from fastapi import APIRouter
from utils.database import HintDb

router = APIRouter(
    prefix="/hint"
)

hintDb = HintDb()

@router.get("/{hintId}")
async def getHint(hintId: str):
    return hintDb.getHint(hintId)

@router.get("/all")
async def getHints():
    return hintDb.getHints()