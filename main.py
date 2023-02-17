# -*- coding: UTF-8 -*-
from fastapi import FastAPI
from routers import *

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Hello World"}