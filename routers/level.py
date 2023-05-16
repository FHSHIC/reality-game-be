from fastapi import APIRouter, Depends, HTTPException, status
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
    levelContent: str
    hints: list

class LevelResolve(LevelNotResolve):
    beacon: str

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
    teamDb.updateNextLevelBeacon(resolve.gamecode, thisLevel["beacon"])
    return LevelResolve(**thisLevel)
    