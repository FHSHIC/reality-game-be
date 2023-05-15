from fastapi import APIRouter, Depends, Header, HTTPException, status

router = APIRouter(
    prefix="/team"
)

# TODO: check is user in team
def checkUserIsInTeam(userId: str):
    pass

# TODO: get team state
@router.get("/{gamecode}")
async def getTeamState(gamecode: str):
    pass

# TODO: use game code

# TODO: set team name

# TODO: waiting process using websocket

# TODO: game start with websocket broadcast to team member

# TODO: game end with websocket broadcast to team member and update team & user status