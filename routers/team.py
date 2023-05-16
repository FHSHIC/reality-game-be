from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from utils.dependencies import verifyAcessToken
from utils.database import TeamDb, UserDb, LevelDb
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
    nowLevel: int
    isTeamLeader: bool = False
    beacon: list = []

class TeamResponse(Team):
    isStart: bool
    
@router.get("/{gamecode}", response_model=TeamResponse)
async def getTeam(gamecode: str, user: dict = Depends(verifyAcessToken)):
    team = teamDb.getTeam(gamecode)
    if not team:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't reach the team...")
    memberIndex = teamDb.findMemberIndex(gamecode, user["account"])
    if memberIndex == -1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in the team...")
    if memberIndex == 0:
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
    memberIndex = teamDb.findMemberIndex(gameCode.gamecode, user["account"])
    if memberIndex != -1:
        if memberIndex == 0:
            team.update({
                "isTeamLeader": True
            })
        return team
    
    team = teamDb.memberJoin(gameCode.gamecode, user["account"])
    memberIndex = teamDb.findMemberIndex(gameCode.gamecode, user["account"])
    if memberIndex == 0:
        team.update({
            "isTeamLeader": True
        })
    
    return team


@router.post("/set-team-name")
async def setTeamName(team: TeamInfo, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't set team name")
    memberIndex = teamDb.findMemberIndex(team.gamecode, user["account"])
    if memberIndex != 0:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't set team name")
    thisTeam = teamDb.setName(team.gamecode, team.teamName)
    if memberIndex == 0:
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
    memberIndex = teamDb.findMemberIndex(team.gamecode, user["account"])
    if memberIndex == -1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    if not manager.findUser(team.gamecode, user["account"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the waiting line")
    if memberIndex != 0:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you can't start the game")
    teamDb.activeTeam(team.gamecode)
    for member in thisTeam["members"]:
        userDb.updateUserActiveState(member["userId"], team.gamecode, True)
    await manager.broadcast(team.gamecode, {"isStart": True, "nowLevel": thisTeam["nowLevel"]})
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

@router.get("/resolve-beacon")
async def checkBeacon(teamId: str, beacon: str):
    nextLevel = LevelDb().getLevel(beacon)
    if not nextLevel:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not a beacon...")
    thisTeam = teamDb.getTeam(teamId)
    if thisTeam["nowLevel"] + 1 != nextLevel["level"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not a beacon...")
    teamDb.updateNowLevel(teamId, nextLevel["level"])
    return teamDb.getTeam(teamId)
    

@router.websocket("/waiting/{teamId}/{userId}")
async def teamWait(websocket: WebSocket, teamId: str, userId: str):
    thisTeam = teamDb.getTeam(teamId)
    
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="you can't reach this team.")
    memberIndex = teamDb.findMemberIndex(teamId, userId)
    if memberIndex == -1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in the team.")
    await manager.connect(websocket, teamId, userId)
    onWaitMembers = []
    for member in manager.activateConnections[teamId]:
        onWaitMembers.append({
            "username": userDb.getUser(member["user"])["username"],
            "userId": member["user"]
        })
    thisTeam.update({"teamLeader": thisTeam["members"][0]["userId"]})
    await manager.broadcast(teamId, {"onWaitMember": onWaitMembers, "isStart": False, "team": thisTeam})
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(websocket, teamId, userId)
        thisTeam = teamDb.getTeam(teamId)
        if thisTeam["isStart"]:
            await manager.broadcast(teamId, {"onWaitMember": onWaitMembers, "isStart": True, "team": thisTeam})
        else:
            onWaitMembers = []
            for member in manager.activateConnections[teamId]:
                onWaitMembers.append({
                    "username": userDb.getUser(member["user"])["username"],
                    "userId": member["user"],
                })
            teamDb.deleteFromTeam(teamId, userId)
            thisTeam.update({"teamLeader": thisTeam["members"][0]["userId"]})
            await manager.broadcast(teamId, {"onWaitMember": onWaitMembers, "isStart": False, "team": thisTeam})
            if len(manager.activateConnections[teamId]) == 0:
                teamDb.setName(teamId, "")
                del(manager.activateConnections[teamId])
    