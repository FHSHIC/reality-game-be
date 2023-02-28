# -*- coding: UTF-8 -*-
from fastapi import FastAPI

app = FastAPI(root_path="/api")


@app.get("/")
async def home():
    return {"message": "Hello World"}