# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from routers import user

app = FastAPI(root_path="/api")

app.include_router(user.router)


@app.get("/")
async def home():
    return {"message": "Hello World"}