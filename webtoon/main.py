# webtoon/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webtoon.db import Base, engine
from webtoon.routers.auth import router as auth_router
from webtoon.routers.reviews import router as reviews_router
from webtoon.routers.search import router as search_router
from webtoon.routers.webtoons import router as webtoons_router

app = FastAPI()


@app.on_event("startup")
def ensure_tables_exist() -> None:
    """Create ORM-managed tables if they don't already exist."""

    from webtoon import models  # noqa: F401  (import registers models with Base)

    Base.metadata.create_all(bind=engine)


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 모든 도메인 허용
    allow_credentials=True,         # 쿠키, 인증 정보 허용
    allow_methods=["*"],            # 모든 HTTP 메서드 허용
    allow_headers=["*"],            # 모든 헤더 허용
)

# 라우터 등록
app.include_router(webtoons_router)
app.include_router(search_router)
app.include_router(reviews_router)
app.include_router(auth_router)
