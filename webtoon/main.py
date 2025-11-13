from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import sqlite3
import os

app = FastAPI()
router = APIRouter()

# 프로젝트 루트 기준으로 DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # .../webtoon-note-BE
DB_PATH = os.path.join(BASE_DIR, "webtoon", "webtoon_database.sqlite")

# SQLite 연결 설정
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 라우터 정의
@router.get("/")
def say_hi():
    return {"message": "Server is running!"}

# 라우터 정의
@router.get("/webtoons")
def get_all_webtoons():
    rows = cursor.execute("""SELECT 
            thumbnail,
            title,
            updateDays,
            authors,
            synopsis,
            tags
        FROM normalized_webtoon""").fetchall()
    data = [dict(r) for r in rows]
    return JSONResponse(
        content={"webtoons": data},
        media_type="application/json; charset=utf-8"
    )
    
@router.get("/webtoons_title")
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
    query = """SELECT 
            thumbnail,
            title,
            updateDays,
            authors,
            synopsis,
            tags FROM normalized_webtoon WHERE updateDays = ?"""
    rows = cursor.execute(query, (day,)).fetchall()
    data = [dict(r) for r in rows]

    return JSONResponse(
        content={"count": len(data), "webtoons": data},
        media_type="application/json; charset=utf-8"
    )

@router.get("/webtoons_title/{day}")
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