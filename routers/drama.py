from fastapi import APIRouter
from utils.database import DramaDb

router = APIRouter(
    prefix="/drama"
)

dramaDb = DramaDb()

@router.get("/{dramaId}")
async def getDrama(dramaId: str):
    return dramaDb.getDrama(dramaId)

@router.get("/all")
async def getDramas():
    return dramaDb.getDramas()