# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from routers import user, team

app = FastAPI(root_path="/api")

app.include_router(user.router)
app.include_router(team.router)


@app.get("/")
async def home():
    return {"message": "Hello World"}