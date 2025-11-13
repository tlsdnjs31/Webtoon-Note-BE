from fastapi import APIRouter
from fastapi.responses import JSONResponse
from webtoon.database import get_db

router = APIRouter(
    tags=["webtoons"]
)

conn, cursor = get_db()

# 라우터 정의
@router.get("/")
def say_hi():
    return {"message": "Server is running!"}

# 라우터 정의
@router.get("/webtoons")
def get_all_webtoons():
    rows = cursor.execute("""SELECT 
            id,
            thumbnail,
            title,
            updateDays,
            authors,
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

@router.get("/webtoons/day/{day}")
def get_webtoons_by_day(day: str):
    valid_days = ["MON", "TUE", "WED", "THR", "FRI", "SAT", "SUN"]
    if day not in valid_days:
        return JSONResponse(
            content={"error": "Invalid day parameter. Use one of: MON, TUE, WED, THR, FRI, SAT, SUN"},
            status_code=400
        )
    query = """SELECT 
            id,
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

@router.get("/webtoons_title/day/{day}")
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

