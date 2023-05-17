from fastapi import APIRouter, HTTPException, status, Depends
from utils.database import TeamDb, HintDb, LevelDb
from utils.dependencies import verifyAcessToken

router = APIRouter(
    prefix="/hint"
)

hintDb = HintDb()
teamDb = TeamDb()
levelDb = LevelDb()

regularHintExtraTime = 10000
levelAnswerHintExtraTime = 2400000

@router.get("/level-answer/{gamecode}")
async def getLevelAnswer(gamecode: str, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you do not have any right to get this hint")
    memberIndex = teamDb.findMemberIndex(gamecode, user["account"])
    if memberIndex == -1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in this team")
    teamDb.addExtraTimeByUsingHint(gamecode, levelAnswerHintExtraTime)
    thisLevel = levelDb.getLevelByLevelNum(thisTeam["nowLevel"])
    return {
        "hintContent": f"正確答案是 {thisLevel['answer']}"
    }

@router.get("/get-hint/{hintId}/{gamecode}")
async def getHint(hintId: str, gamecode: str, user: dict = Depends(verifyAcessToken)):
    thisTeam = teamDb.getTeam(gamecode)
    if not thisTeam:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="you do not have any right to get this hint")
    memberIndex = teamDb.findMemberIndex(gamecode, user["account"])
    if memberIndex == -1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="you are not in this team")
    thisHint = hintDb.getHint(hintId)
    if not thisHint:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="no this hint")
    if thisHint.get("teamsWhoGetTheHint") is not None:
        if gamecode in thisHint["teamsWhoGetTheHint"]:
            return thisHint
    teamDb.addExtraTimeByUsingHint(gamecode, regularHintExtraTime)
    hintDb.updateTeamsWhoGetTheHint(hintId, gamecode)
    return thisHint

