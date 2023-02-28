from fastapi import WebSocket, APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from deta import Deta
import json
import DetaBase

class Player(BaseModel):
    key :str
    level: int = 0
    players: List[str] = [
            "member1",
            "member2",
            "member3",
            "member4",
    ]


@router.websocket("/ws/{gameCode}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, gameCode: str, client_id: int):
    await websocket.accept()
    while True:
        message = await websocket.receive_json()
        if message == {"message":"start"}:
            keys = playerdb.fetch({"key": gameCode})._items[0]["key"]
            updates = {"level": 1}
            playerdb.update(updates, key = keys)
            await websocket.send_json(({"message": "ok"}))

        if message == {"message":"complete"}:
            keys = playerdb.fetch({"key": gameCode})._items[0]["key"]
            updates = {"level": playerdb.util.increment(1)}
            playerdb.update(updates, key = keys)
            await websocket.send_json(({"message": "ok"}))  