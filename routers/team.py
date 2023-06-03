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
    beacon: str
    startTime: int
    endTime: int
    extraTime: int
    beacon: str = ""

class TeamResponse(Team):
    isStart: bool

class BeaconResolver(BaseModel):
    teamId: str
    beacon: str
    
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
    if len(team["members"]) > 4:
        raise HTTPException(status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, detail="this game's member is fulled")
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
    teamName = team.teamName[:6] if len(team.teamName) > 6 else team.teamName
    thisTeam = teamDb.setName(team.gamecode, teamName)
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



@router.post("/game-finish", response_model=UserInfo)
async def finishGame(team: Game, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(team.gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this team")
    memberIndex = teamDb.findMemberIndex(team.gamecode, user["account"])
    if memberIndex == -1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you are not in the team")
    if thisTeam["nowLevel"] != 6:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in the last level")
    if memberIndex != 0:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you are not the capton of this team")
    onWaitMembers = []
    for onWaitMember in manager.activateConnections[team.gamecode]:
        onWaitMembers.append({
            "username": userDb.getUser(onWaitMember["user"])["username"],
            "userId": onWaitMember["user"]
        })
    if len(onWaitMembers) != len(thisTeam["members"]):
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail="Could not finish the game until all members arrive the waiting page.")
    for member in thisTeam["members"]:
        userDb.UserCurrentGameFinish(member["userId"])
    teamDb.finishCurrentGame(team.gamecode)
    await manager.broadcast(team.gamecode, {"isEnd": True, "isStart": False, "team": thisTeam})
    
    return userDb.getUser(user["account"])

@router.post("/resolve-beacon")
async def checkBeacon(resolver: BeaconResolver):
    if (resolver.beacon == "tech-debt"):
        thisTeam = teamDb.getTeam(resolver.teamId)
        # brutal
        teamDb.updateNowLevel(resolver.teamId, 6)
        return teamDb.getTeam(resolver.teamId)
    nextLevel = LevelDb().getLevel(resolver.beacon)
    if not nextLevel:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not a beacon...")
    thisTeam = teamDb.getTeam(resolver.teamId)
    # if thisTeam["nowLevel"] + 1 > nextLevel["level"]:
    #     raise HTTPException(status.HTTP_403_FORBIDDEN, "not a beacon...")
    if thisTeam["nowLevel"] < nextLevel["level"]:
        teamDb.updateNowLevel(resolver.teamId, nextLevel["level"])
    return teamDb.getTeam(resolver.teamId)
    

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
            if not thisTeam["isStart"] and not thisTeam["isUsed"]:
                teamDb.deleteFromTeam(teamId, userId)
            thisTeam.update({"teamLeader": thisTeam["members"][0]["userId"]})
            await manager.broadcast(teamId, {"onWaitMember": onWaitMembers, "isStart": False, "team": thisTeam})
            if len(manager.activateConnections[teamId]) == 0:
                teamDb.setName(teamId, "")
                del(manager.activateConnections[teamId])
    