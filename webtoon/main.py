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

@router.get("/webtoons/{day}")
def get_webtoons_by_day(day: str):
    valid_days = ["MON", "TUE", "WED", "THR", "FRI", "SAT", "SUN"]
    if day not in valid_days:
        return JSONResponse(
            content={"error": "Invalid day parameter. Use one of: MON, TUE, WED, THR, FRI, SAT, SUN"},
            status_code=400
        )

    query = "SELECT title FROM normalized_webtoon WHERE updateDays = ?"
    rows = cursor.execute(query, (day,)).fetchall()
    data = [dict(r) for r in rows]

    return JSONResponse(
        content={"count": len(data), "webtoons": data},
        media_type="application/json; charset=utf-8"
    )

# 라우터 등록
app.include_router(router)