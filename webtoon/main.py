from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()
router = APIRouter()

# SQLite 연결 설정
conn = sqlite3.connect("webtoon_database.sqlite", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 라우터 정의
@router.get("/webtoons")
def get_all_webtoons():
    rows = cursor.execute("SELECT title FROM normalized_webtoon").fetchall()
    data = [dict(r) for r in rows]
    return JSONResponse(
        content={"webtoons": data},
        media_type="application/json; charset=utf-8"
    )

# 라우터 등록
app.include_router(router)