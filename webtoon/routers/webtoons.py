from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from webtoon.database import get_db

router = APIRouter(
    tags=["webtoons"]
)

conn, cursor = get_db()
PAGE_SIZE = 16

# 라우터 정의
@router.get("/")
def say_hi():
    return {"message": "Server is running!"}

# 라우터 정의
@router.get("/webtoons")
def get_all_webtoons(
    webtoon_id: str | None = Query(
        None, min_length=1, description="특정 웹툰 ID로 필터 (예: kakao_1000)"
    ),
    page: int = Query(1, ge=1, description="조회할 페이지 번호 (1부터 시작)"),
):
    where_clause = ""
    params: list = []

    if webtoon_id:
        where_clause = " WHERE id = ?"
        params.append(webtoon_id)

    total_row = cursor.execute(
        f"SELECT COUNT(*) AS cnt FROM normalized_webtoon{where_clause}",
        params,
    ).fetchone()
    total = total_row["cnt"] if total_row is not None else 0

    rows = cursor.execute(
        f"""SELECT 
            id,
            thumbnail,
            title,
            updateDays,
            authors,
            tags
        FROM normalized_webtoon{where_clause}
        ORDER BY id
        LIMIT ? OFFSET ?""",
        (*params, PAGE_SIZE, (page - 1) * PAGE_SIZE),
    ).fetchall()
    data: list[dict] = []
    for r in rows:
        item = dict(r)
        item["webtoon_id"] = item["id"]
        data.append(item)
    return JSONResponse(
        content={
            "page": page,
            "page_size": PAGE_SIZE,
            "total": total,
            "total_pages": (total + PAGE_SIZE - 1) // PAGE_SIZE,
            "webtoons": data,
        },
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
    data: list[dict] = []
    for r in rows:
        item = dict(r)
        item["webtoon_id"] = item["id"]
        data.append(item)

    return JSONResponse(
        content={"count": len(data), "webtoons": data},
        media_type="application/json; charset=utf-8"
    )


@router.get("/webtoons/sample")
def get_sample_webtoons(
    limit: int = Query(5, ge=1, le=50, description="가져올 테스트용 웹툰 개수 (기본 5)")
):
    """
    테스트용으로 소량의 웹툰만 조회하는 엔드포인트.
    """
    rows = cursor.execute(
        """
        SELECT
            id,
            thumbnail,
            title,
            updateDays,
            authors,
            tags
        FROM normalized_webtoon
        ORDER BY id
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    data: list[dict] = []
    for r in rows:
        item = dict(r)
        item["webtoon_id"] = item["id"]
        data.append(item)
    return JSONResponse(
        content={"count": len(data), "webtoons": data},
        media_type="application/json; charset=utf-8",
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
