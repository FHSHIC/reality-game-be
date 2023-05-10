from fastapi import WebSocket


class ConnectManager():
    def __init__(self):
        self.activateConnections: dict = {}

    async def connect(self, websocket: WebSocket, groupId: str, userId: str):
        await websocket.accept()
        if not self.activateConnections.get(groupId):
            self.activateConnections[groupId] = []
        self.activateConnections[groupId].append({"websocket":websocket, "user": userId})
    
    def findUser(self, groupId: str, userId: str):
        filterResult = list(filter(lambda x: userId == x["user"], self.activateConnections[groupId]))
        if len(filterResult) == 0:
            return None
        return filterResult[0]

    def disconnect(self, websocket: WebSocket, groupId: str, userId: str):
        self.activateConnections[groupId].remove({"websocket": websocket, "user": userId})

    async def broadcast(self, groupId: str, messages: dict ):
        for connection in self.activateConnections[groupId]:
            await connection["websocket"].send_json(messages)
            
    async def send(self, websocket: WebSocket, messages: dict):
        await websocket.send_json(messages)