# Backend Architecture

## Runtime Overview

The backend is a FastAPI service with a background poll loop that refreshes live game state and win probabilities every 5 seconds.

Primary flow:
1. Poll ESPN scoreboard API.
2. Parse each event into normalized game objects.
3. Compute win probabilities per game.
4. Store results in in-memory module state.
5. Broadcast full snapshot to active WebSocket clients.

## Core Modules

- `backend/main.py`
  - FastAPI app setup, CORS config, routes, websocket manager, poll lifecycle.
- `backend/util.py`
  - ESPN event parsing and win-probability computation.
  - Optional ML model load from `ml/model.joblib`.
- `backend/state.py`
  - In-memory store:
    - `games: list[dict]`
    - `probabilities: dict[game_id -> {home_win_prob, away_win_prob}]`
- `backend/standings.py`
  - Normalizes `nba_api` standings payload into east/west lists.
- `backend/database.py`
  - PostgreSQL helper layer (`psycopg2`) for query/insert/update patterns.

## External Dependencies

- ESPN API:
  - `https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`
- NBA API package:
  - `nba_api.stats.endpoints.leaguestandings`
- Optional ML model file:
  - `ml/model.joblib` (if missing, probability function currently falls back to zeros for non-final games)

## Lifespan and Polling

- App lifespan starts `poll_loop()` task via `asyncio.create_task`.
- Poll loop interval: 5 seconds.
- On shutdown, poll task is cancelled and awaited.

## State and Consistency

- In-memory state is process-local.
- No persistence for live game snapshots/probabilities.
- If multiple API workers are used, each worker will maintain its own independent state.

## WebSocket Broadcast Model

- WebSocket clients connect to `/ws`.
- On each poll tick, backend broadcasts the full games array as JSON text.
- Failed sends are currently swallowed in `broadcast_json`.

## CORS/Frontend Integration

Configured allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `https://pj09-sports-betting.vercel.app`

## Known Implementation Gaps

- `GET /api/games/stats` references an undefined function (`fetch_games_with_stats`).
- Error handling in `GET /api/games/stats/{game_id}` is non-standard for FastAPI.
- `backend/services/data_transform.py` constructs `Game` with a `status` field that is not defined in `models/schemas.py`.
