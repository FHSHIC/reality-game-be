from fastapi import APIRouter, Depends
from pydantic import BaseModel
from utils.database import DramaDb

router = APIRouter(
    prefix="/drama"
)

dramaDb = DramaDb()

@router.get("/{dramaId}")
async def getDrama(dramaId: str):
    return dramaDb.getDrama(dramaId)