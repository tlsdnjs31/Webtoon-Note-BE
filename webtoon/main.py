# webtoon/main.py
from fastapi import FastAPI
from webtoon.routers.webtoons import router as webtoons_router

app = FastAPI()

# 라우터 등록
app.include_router(webtoons_router)