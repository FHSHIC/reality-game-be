from fastapi import APIRouter, Depends
from pydantic import BaseModel

from utils.database import LevelDb, TeamDb
from utils.dependencies import verifyAcessToken

router = APIRouter(
    prefix="/level",
    dependencies=[Depends(verifyAcessToken)]
)

levelDb = LevelDb()
teamDb = TeamDb()

class LevelNotResolve(BaseModel):
    hints: list

class LevelResolve(LevelNotResolve):
    nextDramaId: str

class Resolve(BaseModel):
    gamecode: str
    levelId: str
    answer: str


@router.get("/{levelId}", response_model=LevelNotResolve)
async def getLevel(levelId: str):
    return levelDb.getLevel(levelId)

@router.post("/resolve")
async def checkResolve(resolve: Resolve):
    thisLevel = levelDb.getLevel(resolve.levelId)
    if thisLevel["answer"] != resolve.answer:
        return LevelNotResolve(**thisLevel)
    teamDb.updateNowDramaId(resolve.gamecode, thisLevel["nextDramaId"])
    return LevelResolve(**thisLevel)