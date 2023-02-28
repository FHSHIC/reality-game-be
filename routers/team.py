from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from utils.dependencies import verifyAcessToken
from utils.database import TeamDb
from utils.WebSocketManager import ConnectManager

router = APIRouter(
    prefix="/team"
)

teamDb = TeamDb()
manager = ConnectManager()

class Game(BaseModel):
    code: str

class TeamName(BaseModel):
    gamecode: str
    name: str

class Team(TeamName):
    members: list
    nowLevelId: str
    
@router.get("/{gamecode}", response_model=Team)
async def getTeam(gamecode: str, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gamecode)
    if not team:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't reach the team...")
    if user["account"] not in team["members"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you are not in the team...")
    
    return team

@router.post("/gamecode", response_model=Team)
async def postGamecode(gameCode: Game, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gameCode)
    if not team:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't use this game code...")
    if team["isUsed"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't use this game code...")
    
    return teamDb.memberJoin(gameCode, user["account"])
    

@router.post("/set-team")
async def setTeamName(team: TeamName, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't set team name")
    if user["account"] != thisTeam["members"][0]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't set team name")
    
    return teamDb.setName(team.gamecode, team.name)

@router.post("/leave-team")
async def leaveFromTeam(team: TeamName, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't set team name")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    
    return teamDb.deleteFromTeam(team.gamecode, user["account"])

@router.websocket("/waiting/{teamId}/{userId}")
async def teamWait(websocket: WebSocket, teamId: str, userId: str):
    thisTeam = teamDb.getTeam(teamId)
    if not thisTeam:
        return
    if userId not in thisTeam["members"]:
        return
    await manager.connect(websocket, teamId, userId)
    await manager.broadcast(teamId, {"members": [member["user"] for member in manager.activateConnections[teamId]]})
    try:
        while True:
            data = await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(websocket, teamId, userId)
    