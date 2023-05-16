from fastapi import APIRouter, Depends
from utils.dependencies import verifyUploadSecret

router = APIRouter(
    prefix="/upload",
    dependencies=[Depends(verifyUploadSecret)]
)


@router.post("/dramas")
async def uploadDrama(dramas: list):
    pass