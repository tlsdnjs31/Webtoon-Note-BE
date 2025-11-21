# webtoon/routers/search.py
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from webtoon.database import get_db

router = APIRouter(
    tags=["webtoons-search"]
)

conn, cursor = get_db()

@router.get("/search")
def search_webtoons(
    q: str = Query(..., min_length=1, description="검색어 (제목/작가/태그/시놉시스 검색)"),
    day: str | None = Query(None, description="MON/TUE/WED/THR/FRI/SAT/SUN 중 선택 (선택)")
):
    """
    웹툰 검색 API
    - q: 제목, 작가, 시놉시스, 태그 전체에서 부분 검색
    - day: 요일 값이 들어오면 요일 필터까지 적용
    """
    pattern = f"%{q}%" # 검색어 패턴

    base_query = """
        SELECT
            id,
            thumbnail,
            title,
            updateDays,
            authors,
            synopsis,
            tags
        FROM normalized_webtoon
        WHERE (
            id        LIKE ?
            OR title    LIKE ?
            OR authors  LIKE ?
            OR synopsis LIKE ?
            OR tags     LIKE ?
        )
    """

    params: list[str] = [pattern, pattern, pattern, pattern, pattern]

    # day가 넘어왔으면 요일 필터 추가
    if day is not None:
        base_query += " AND updateDays = ?"
        params.append(day)

    rows = cursor.execute(base_query, params).fetchall()
    data: list[dict] = []
    for r in rows:
        item = dict(r)
        item["webtoon_id"] = item["id"]
        data.append(item)

    return JSONResponse(
        content={"count": len(data), "webtoons": data},
        media_type="application/json; charset=utf-8"
    )


@router.get("/{webtoon_id}")
def get_webtoon_by_id(webtoon_id: str):
    """
    웹툰 단일 조회 API
    - webtoon_id: 웹툰 고유 ID
    """
    row = cursor.execute(
        """
        SELECT
            id,
            thumbnail,
            title,
            updateDays,
            authors,
            synopsis,
            tags
        FROM normalized_webtoon WHERE id = ? 
        """,
        (webtoon_id,),
    ).fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Webtoon not found"},
            media_type="application/json; charset=utf-8",
        )

    data = dict(row)
    data["webtoon_id"] = data["id"]

    return JSONResponse(
        content=data,
        media_type="application/json; charset=utf-8",
    )
