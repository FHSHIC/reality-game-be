from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(
    prefix="/drama"
)

@router.get("/{dramaId}")
async def getDrama(dramaId: str):
    pass