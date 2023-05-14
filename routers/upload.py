from fastapi import APIRouter
from utils.dependencies import verifyUploadSecret

router = APIRouter(
    prefix="/upload",
    dependencies=[verifyUploadSecret]
)


@router.post("/dramas")
async def uploadDrama(dramas: list):
    pass