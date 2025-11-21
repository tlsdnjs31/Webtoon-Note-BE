# webtoon-note-BE

## Webtoon List API

| Endpoint | Method |
| --- | --- |
| `/webtoons` | GET |

### Query Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `page` | integer | No | 1부터 시작하는 페이지 번호 (기본 1, 페이지 크기 16으로 고정). |
| `webtoon_id` | string | No | 특정 ID로 필터 (예: `kakao_1000`). |

### Response `200 OK`

```json
{
  "page": 1,
  "page_size": 16,
  "total": 320,
  "total_pages": 20,
  "webtoons": [
    {
      "id": "kakao_1000",
      "thumbnail": "https://.../thumb.png",
      "title": "웹툰 제목",
      "updateDays": "MON",
      "authors": "작가명",
      "tags": "태그 리스트",
      "webtoon_id": "kakao_1000"
    }
  ]
}
```

## Anonymous ID API

| Endpoint | Method |
| --- | --- |
| `/auth/anonymous` | GET |

### Request

`GET /auth/anonymous`

### Response `200 OK`

- New issuance

```json
{
  "anon_id": "d9f2a417-5cb1-4df3-b28f-56c7137e75c9",
  "status": "new"
}
```

- Existing cookie

```json
{
  "anon_id": "a38f8a13-43df-4e8b-bbda-991db3f7fcb7",
  "status": "existing"
}
```

### Failure Responses

| Status | When | Body |
| --- | --- | --- |
| `500` | UUID generation or cookie handling fails unexpectedly. | `{"detail": "Internal Server Error"}` |

### Notes

- The endpoint reuses the `anon_id` cookie logic used by review-related APIs.
- When a cookie is missing, a new UUID is minted and returned with `Set-Cookie` (HttpOnly, SameSite=Lax, max-age 1 year).
- When a cookie is present, it is simply echoed back with `status: "existing"`.
- `anon_id` is used for review creation limits and duplicate-like prevention, and can later map to a logged-in `user_id`.

## Review Creation API

| Endpoint | Method |
| --- | --- |
| `/webtoons/review/` | POST |

### Query Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `webtoon_id` | string | Yes | Target webtoon ID from `normalized_webtoon.id` (e.g., `kakao_1000`). |

### Request Body

```json
{
  "content": "스토리가 정말 흥미진진해요!",
  "rating": 4.5
}
```

### Validation Rules

- `content`: 1–2000 characters, Unicode text permitted.
- `rating`: floating point between 0 and 5 inclusive (FastAPI/Pydantic reject anything outside the range).

### Response `201 Created`

```json
{
  "id": 15,
  "webtoon_id": "kakao_1000",
  "content": "스토리가 정말 흥미진진해요!",
  "rating": 4.5,
  "likes": 0,
  "created_at": "2025-11-12T18:40:00",
  "updated_at": "2025-11-12T18:40:00",
  "anonymous_user_id": "a38f8a13-41be-4ebe-9fc7-3f79bfb652f5"
}
```

### Cookie Policy

- The API reads the `anon_id` cookie to attribute reviews to anonymous visitors.
- When the cookie is missing, a new UUID is minted and returned in the response headers with:
  - `HttpOnly` flag set.
  - `SameSite=Lax`.
  - `max-age` of one year.

### Side Effects after Successful Review Creation

- The review is persisted in `reviews` with `likes` defaulting to `0`.
- Corresponding entry in `webtoon_rating_stats` is inserted/updated to keep the aggregate review count and average rating in sync (`average = (prev_sum + new_rating) / new_count`).

### Failure Responses

| Status | When | Body |
| --- | --- | --- |
| `404` | `webtoon_id` does not exist in `normalized_webtoon`. | `{"detail": "해당 웹툰을 찾을 수 없습니다."}` |
| `409` | `anon_id` already has a review for the specified `webtoon_id`. | `{"detail": "이미 해당 웹툰에 대한 리뷰를 작성했습니다."}` |
| `422` | Validation fails (missing fields, rating out of range, empty content, etc.). | FastAPI validation payload detailing the offending field. |
| `500` | Unexpected server/database errors (transaction rollbacks are logged; a generic message is returned). | `{"detail": "Internal Server Error"}` |

### Notes

- `likes` is returned to support future “like review” features but currently always starts at zero.
- Additional moderation (profanity filtering, spam detection) can be layered on top of the service without changing the contract.

## Review Update API

| Endpoint | Method |
| --- | --- |
| `/webtoons/{webtoon_id}/reviews` | PUT |

### Path Parameters

| Name | Type | Description |
| --- | --- | --- |
| `webtoon_id` | string | ID of the webtoon whose review should be updated (e.g., `kakao_1000`). |

### Request Body

```json
{
  "content": "초반보다 후반이 훨씬 재밌어요!",
  "rating": 4.8
}
```

### Response `200 OK`

```json
{
  "id": 15,
  "webtoon_id": "kakao_1000",
  "content": "초반보다 후반이 훨씬 재밌어요!",
  "rating": 4.8,
  "likes": 0,
  "created_at": "2025-11-12T18:40:00",
  "updated_at": "2025-11-12T21:10:00",
  "anonymous_user_id": "a38f8a13-41be-4ebe-9fc7-3f79bfb652f5"
}
```

### Additional Rules

- Ownership is verified using the `anon_id` cookie; only the author can update their review.
- The review is identified through the combination of `webtoon_id` and `anon_id`. An attempt to edit someone else’s review returns `403`.
- Average star rating is recalculated automatically after an update.
- `updated_at` captures the most recent modification timestamp.

### Failure Responses

| Status | When | Body |
| --- | --- | --- |
| `403` | Review exists for the `webtoon_id` but belongs to a different `anon_id`. | `{"detail": "You can only update your own review"}` |
| `404` | `webtoon_id` does not exist or the stat entry cannot be located during recalculation. | `{"detail": "해당 웹툰을 찾을 수 없습니다."}` |
| `422` | Validation fails (missing fields, rating out of range, empty content, etc.). | FastAPI validation payload detailing the offending field. |

## Review Like API

| Endpoint | Method |
| --- | --- |
| `/reviews/{review_id}/like` | POST |

### Path Parameters

| Name | Type | Description |
| --- | --- | --- |
| `review_id` | integer | Identifier of the review to like. |

### Request Example

`POST /reviews/27/like` with cookie `anon_id=<uuid>`

### Response `200 OK`

```json
{
  "review_id": 27,
  "likes": 4
}
```

### Failure Responses

| Status | When | Body |
| --- | --- | --- |
| `400` | The anon user already liked the review. | `{"detail": "이미 좋아요를 누른 사용자입니다."}` |
| `404` | Review ID does not exist. | `{"detail": "존재하지 않는 리뷰입니다."}` |
| `500` | Unexpected server/database errors. | `{"detail": "Internal Server Error"}` |

### Notes

- Likes are keyed by `(anon_id, review_id)` and cannot be undone.
- Each successful call increments the review's `likes` field atomically.
