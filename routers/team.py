from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from utils.dependencies import verifyAcessToken
from utils.database import TeamDb, UserDb
from routers.user import UserInfo
from utils.WebSocketManager import ConnectManager

router = APIRouter(
    prefix="/team"
)

teamDb = TeamDb()
userDb = UserDb()
manager = ConnectManager()

class Game(BaseModel):
    gamecode: str

class TeamInfo(BaseModel):
    gamecode: str
    teamName: str

class Team(TeamInfo):
    members: list
    nowDramaId: str
    isTeamLeader: bool = False

class TeamResponse(Team):
    isStart: bool
    
@router.get("/{gamecode}", response_model=TeamResponse)
async def getTeam(gamecode: str, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gamecode)
    if not team:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't reach the team...")
    if user["account"] not in team["members"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in the team...")
    if user["account"] == team["members"][0]:
        team.update({
            "isTeamLeader": True
        })
    
    return team

@router.post("/join-team", response_model=Team)
async def joinTeam(gameCode: Game, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gameCode.gamecode)
    if not team:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't use this game code...")
    if team["isUsed"]:
        raise HTTPException(status.HTTP_423_LOCKED, detail="this game code has already used")
    if team["isStart"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="this game is on.")
    if user["account"] in team["members"]:
        if user["account"] == team["members"][0]:
            team.update({
                "isTeamLeader": True
            })
        return team
    team = teamDb.memberJoin(gameCode.gamecode, user["account"])
    if user["account"] == team["members"][0]:
        team.update({
            "isTeamLeader": True
        })
    
    return team
    


@router.post("/set-team-name")
async def setTeamName(team: TeamInfo, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't set team name")
    if user["account"] != thisTeam["members"][0]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't set team name")
    thisTeam = teamDb.setName(team.gamecode, team.teamName)
    if user["account"] == thisTeam["members"][0]:
        thisTeam.update({
            "isTeamLeader": True
        })
    return thisTeam

@router.post("/leave-team")
async def leaveFromTeam(team: Game, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    
    return teamDb.deleteFromTeam(team.gamecode, user["account"])

@router.post("/start-game", response_model=TeamResponse)
async def startGame(team: Game, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    if not manager.findUser(team.gamecode, user["account"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the waiting line")
    if user["account"] != thisTeam["members"][0]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't start the game")
    teamDb.activeTeam(team.gamecode)
    for memberId in thisTeam["members"]:
        userDb.updateUserActiveState(memberId, team.gamecode, True)
    await manager.broadcast(team.gamecode, {"isStart": True, "nowDramaId": thisTeam["nowDramaId"]})
    return thisTeam


@router.post("/game-continue", response_model=TeamResponse)
async def continueGame(team:Game, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    if not manager.findUser(team.gamecode, user["account"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the waiting line")
    if user["account"] != thisTeam["members"][0]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't continue the game")
    await manager.broadcast(team.gamecode, {"isStart": True, "nowDramaId": thisTeam["nowDramaId"]})
    return thisTeam

@router.post("/game-finish", response_model=UserInfo)
async def finishGame(team: Game, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    if user["account"] not in thisTeam["members"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    if thisTeam["nowDramaId"] != "fin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in the last level")
    userDb.UserCurrentGameFinish(user["account"])
    if user["account"] != thisTeam["members"][0]:
        return userDb.getUser(user["account"])
    teamDb.finishCurrentGame(team.gamecode)
    return userDb.getUser(user["account"])
    

@router.websocket("/waiting/{teamId}/{userId}")
async def teamWait(websocket: WebSocket, teamId: str, userId: str):
    thisTeam = teamDb.getTeam(teamId)
    
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't reach this team.")
    if userId not in thisTeam["members"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in the team.")
    await manager.connect(websocket, teamId, userId)
    onWaitMembers = []
    for member in manager.activateConnections[teamId]:
        onWaitMembers.append(userDb.getUser(member["user"])["username"])
    members = []
    for member in thisTeam["members"]:
        members.append(userDb.getUser(member)["username"])
    await manager.broadcast(teamId, {"members": members,"onWaitMember": onWaitMembers, "isStart": False, "teamName": thisTeam["teamName"]})
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(websocket, teamId, userId)
        onWaitMembers = []
        for member in manager.activateConnections[teamId]:
            onWaitMembers.append(userDb.getUser(member["user"])["username"])
        await manager.broadcast(teamId, {"members": members,"onWaitMember": onWaitMembers, "isStart": False, "teamName": thisTeam["teamName"]})
        if len(manager.activateConnections[teamId]) == 0:
            del(manager.activateConnections[teamId])
    