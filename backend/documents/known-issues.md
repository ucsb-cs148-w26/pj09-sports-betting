# Known Backend Issues

This file tracks implementation gaps found in current backend code.

## 1) Undefined function in `/api/games/stats`

Location: `backend/main.py`

Issue:
- Endpoint calls `fetch_games_with_stats(game_date=game_date)`.
- Function is not defined/imported in backend code.

Impact:
- Calling `GET /api/games/stats` raises runtime `NameError`.

## 2) Non-standard error response in `/api/games/stats/{game_id}`

Location: `backend/main.py`

Issue:
- Returns `({"error": "Invalid game_id"}, 404)` instead of `HTTPException(status_code=404, ...)`.

Impact:
- Error payload/status may not follow expected FastAPI response handling.

## 3) Schema mismatch in `services/data_transform.py`

Location: `backend/services/data_transform.py` and `backend/models/schemas.py`

Issue:
- `transform_data` constructs `Game(..., status=...)`.
- `Game` model does not define a `status` field.

Impact:
- If executed, this can raise Pydantic validation errors.

## 4) Probability fallback behavior can produce `0,0`

Location: `backend/util.py`

Issue:
- When `ml/model.joblib` is missing, non-final games return `home_win_prob=0` and `away_win_prob=0`.

Impact:
- Frontend can display impossible probability totals.

## 5) Type mismatch risk for `game_id`

Location: API payload vs SQL schema

Issue:
- Live API uses string game ids.
- SQL schema defines `game_id INT` in multiple tables.

Impact:
- Persistence layer may fail or require type conversion when integrating live API ids.
