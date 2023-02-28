# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import user, team, drama

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(team.router)
app.include_router(drama.router)


@app.get("/")
async def home():
    return {"message": "Hello World"}