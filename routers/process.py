from pydantic import BaseModel
from fastapi import APIRouter, Depends
from utils.dependencies import verifyUploadSecret
from utils.database import TeamDb

router = APIRouter(
    prefix="/process",
    dependencies=[Depends(verifyUploadSecret)]
)

class UploadGamecode(BaseModel):
    gamecode: str
    
teamDb = TeamDb()

@router.post("/upload/gamecode")
async def uploadTeams(upload: UploadGamecode):
    return_data = {
        "success": True,
    }
    if teamDb.createNewGamecode(upload.gamecode) is None:
            return_data["success"] = False
    return return_data

@router.get("/gamecodes")
async def checkTeams():
    return_data = dict()
    teams = teamDb.getTeams()
    for team in teams:
        if not team["isUsed"]:
            return_data.update({team["gamecode"]: {"status": "尚未使用", "members": team["members"]}})
            continue
        if not team["isStart"]:
            return_data.update({team["gamecode"]: {"status": "已經通關", "members": team["members"]}})
            continue
        return_data.update({team["gamecode"]: {"status": "正在闖關", "members": team["members"]}})
    return return_data