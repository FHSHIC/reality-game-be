from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from utils.dependencies import verifyAcessToken
from utils.database import TeamDb, UserDb
from utils.WebSocketManager import ConnectManager

router = APIRouter(
    prefix="/team"
)

teamDb = TeamDb()
userDb = UserDb()
manager = ConnectManager()

class Game(BaseModel):
    code: str

class TeamInfo(BaseModel):
    gamecode: str
    teamName: str

class Team(TeamInfo):
    members: list
    nowDramaId: str
    
@router.get("/{gamecode}", response_model=Team)
async def getTeam(gamecode: str, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gamecode)
    if not team:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't reach the team...")
    if user["account"] not in team["members"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you are not in the team...")
    
    return team

@router.post("/post-gamecode", response_model=Team)
async def postGamecode(gameCode: Game, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gameCode.code)
    if not team:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't use this game code...")
    if team["isUsed"] or team["isStart"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't use this game code...")
    if user["account"] in team["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you have already in this team")
    
    return teamDb.memberJoin(gameCode.code, user["account"])
    


@router.post("/set-team")
async def setTeamName(team: TeamInfo, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you can't set team name")
    if user["account"] != thisTeam["members"][0]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't set team name")
    
    return teamDb.setName(team.gamecode, team.name)

@router.post("/leave-team")
async def leaveFromTeam(team: TeamInfo, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    
    return teamDb.deleteFromTeam(team.gamecode, user["account"])

@router.post("/start-game")
async def startGame(team: TeamInfo, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    if user["account"] not in manager.activateConnections[team.gamecode]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the waiting line")
    manager.broadcast(team.gamecode, {"isStart": True})
    
    
    

@router.websocket("/waiting/{teamId}")
async def teamWait(websocket: WebSocket, teamId: str, userId: str):
    thisTeam = teamDb.getTeam(teamId)
    if not thisTeam:
        return
    if userId not in thisTeam["members"]:
        return
    await manager.connect(websocket, teamId, userId)
    members = []
    for member in manager.activateConnections[teamId]:
        member.append(userDb.getUser(member["user"])["username"])
    await manager.broadcast(teamId, {"members": members, "isStart": False})
    try:
        while True:
            data = await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(websocket, teamId, userId)
        if len(manager.activateConnections[teamId]) == 0:
            del(manager.activateConnections[teamId])
    