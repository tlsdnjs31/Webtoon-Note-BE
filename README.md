# webtoon-note-BE

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
| `422` | Validation fails (missing fields, rating out of range, empty content, etc.). | FastAPI validation payload detailing the offending field. |
| `500` | Unexpected server/database errors (transaction rollbacks are logged; a generic message is returned). | `{"detail": "Internal Server Error"}` |

### Notes

- `likes` is returned to support future “like review” features but currently always starts at zero.
- Additional moderation (profanity filtering, spam detection) can be layered on top of the service without changing the contract.
