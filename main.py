# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from routers import Drama, Hint, LevelCheck, Question, SignIn, SignUp, Websocket

app = FastAPI(root_path="/api")

app.include_router(Drama.router)
app.include_router(Hint.router)
app.include_router(LevelCheck.router)
app.include_router(Question.router)
app.include_router(SignIn.router)
app.include_router(SignUp.router)
app.include_router(Websocket.router)

@app.get("/")
async def home():
    return {"message": "Hello World"}