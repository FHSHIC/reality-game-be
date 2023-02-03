# -*- coding: UTF-8 -*-
from fastapi import FastAPI
import apis

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Hello World"}