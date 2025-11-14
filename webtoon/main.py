# webtoon/main.py
from fastapi import FastAPI

from webtoon.db import init_db
from webtoon.routers.search import router as search_router
from webtoon.routers.webtoons import router as webtoons_router


app = FastAPI()
init_db()

# 라우터 등록
app.include_router(webtoons_router)
app.include_router(search_router)
