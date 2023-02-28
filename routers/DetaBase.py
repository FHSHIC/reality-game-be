from fastapi import APIRouter
from deta import Deta


async def detaBase(access_token: AccessToken):
    router = APIRouter()

    deta = Deta("c01qtCTDXhh4_KZmeWaZrF5u2WJjFReeKNxTQh5X79BiU")

    leveldb = deta.Base("Level")
    dramadb = deta.Base("drama")
    hintdb = deta.Base("Hint")
    leveldb = deta.Base("Level")
    userdb = deta.Base("User") 
    playerdb = deta.Base("players")
    gamecodedb = deta.Base("gamecodes")



