from pydantic import BaseModel
from fastapi import APIRouter, Depends
from utils.dependencies import verifyUploadSecret
from utils.database import TeamDb

router = APIRouter(
    prefix="/process",
    dependencies=[Depends(verifyUploadSecret)]
)

class UploadGamecodes(BaseModel):
    gamecodes: list
    
teamDb = TeamDb()

@router.post("/upload/gamecodes")
async def uploadTeams(upload: UploadGamecodes):
    return_data = {
        "success": [],
        "failure": [],
    }
    for gamecode in upload.gamecodes:
        if teamDb.createNewGamecode(gamecode=gamecode) is None:
            return_data["failure"].append(gamecode)
        else:
            return_data["success"].append(gamecode)
    return return_data

@router.get("/gamecodes")
async def checkTeams():
    return_data = dict()
    teams = teamDb.getTeams()
    for team in teams:
        if not team["isUsed"]:
            return_data.update({team["gamecode"]: "尚未使用"})
            continue
        if not team["isStart"]:
            return_data.update({team["gamecode"]: "已經通關"})
            continue
        return_data.update({team["gamecode"]: "正在闖關"})
    return return_data