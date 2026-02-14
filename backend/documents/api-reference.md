# API Reference

Base URL (local): `http://127.0.0.1:8000`

## Health and Utility

### `GET /`
Returns a basic placeholder response.

Response:
```json
{"Hello":"World"}
```

### `GET /health`
Returns service health indicator.

Response:
```json
{"health":"healthy"}
```

### `GET /stats`
Placeholder endpoint.

Response:
```json
{"Home score":"125"}
```

## Live Games

### `GET /api/games`
Returns live games with merged win probabilities.

Behavior:
- Reads from in-memory state (`state.games`, `state.probabilities`).
- If cache is empty, performs one immediate ESPN fetch + probability computation.
- Poll loop refreshes this data every 5 seconds in the background.

Response: `GameWithProbability[]`

```json
[
  {
    "game_id": "401706123",
    "status": "Q3 05:11",
    "home_team": "Lakers",
    "home_city": "Los Angeles",
    "home_abbreviation": "LAL",
    "home_wins": 12,
    "home_losses": 7,
    "home_score": 77,
    "home_q1": 28,
    "home_q2": 24,
    "home_q3": 25,
    "home_q4": null,
    "home_leader_pts_name": "LeBron James",
    "home_leader_pts_val": "22 PTS",
    "home_leader_reb_name": "Anthony Davis",
    "home_leader_reb_val": "10 REB",
    "home_leader_ast_name": "D'Angelo Russell",
    "home_leader_ast_val": "7 AST",
    "home_reb": "35",
    "home_ast": "19",
    "home_fga": "62",
    "home_fgm": "31",
    "home_fta": "14",
    "home_ftm": "11",
    "home_points": "77",
    "home_3pa": "22",
    "home_3pm": "8",
    "away_team": "Warriors",
    "away_city": "Golden State",
    "away_abbreviation": "GSW",
    "away_wins": 11,
    "away_losses": 8,
    "away_score": 70,
    "away_q1": 25,
    "away_q2": 20,
    "away_q3": 25,
    "away_q4": null,
    "away_leader_pts_name": "Stephen Curry",
    "away_leader_pts_val": "24 PTS",
    "away_leader_reb_name": "Kevon Looney",
    "away_leader_reb_val": "9 REB",
    "away_leader_ast_name": "Chris Paul",
    "away_leader_ast_val": "8 AST",
    "away_reb": "30",
    "away_ast": "18",
    "away_fga": "60",
    "away_fgm": "28",
    "away_fta": "13",
    "away_ftm": "10",
    "away_points": "70",
    "away_3pa": "24",
    "away_3pm": "9",
    "home_win_prob": 68.12,
    "away_win_prob": 31.88
  }
]
```

## Game Detail

### `GET /api/games/stats/{game_id}`
Returns one game from in-memory live cache with probabilities.

Path params:
- `game_id` (`string`): ESPN game id.

Success response: `GameWithProbability`

Current error behavior:
- If `game_id` not found, code returns `({"error": "Invalid game_id"}, 404)` instead of raising `HTTPException`.
- This can produce a non-standard FastAPI response shape/status and should be treated as a backend bug.

## Standings

### `GET /api/standings`
Returns conference-grouped standings from `nba_api.stats.endpoints.leaguestandings.LeagueStandings()`.

Response: `LeagueStandingsResponse`

```json
[
  {
    "east_standings": [
      {
        "team_id": 1610612738,
        "team_city": "Boston",
        "team_name": "Celtics",
        "conference": "East",
        "rank": 1,
        "record": "48-13",
        "win_pct": 0.787,
        "team_L10": "8-2",
        "curr_streak": "W3"
      }
    ],
    "west_standings": [
      {
        "team_id": 1610612743,
        "team_city": "Denver",
        "team_name": "Nuggets",
        "conference": "West",
        "rank": 1,
        "record": "43-20",
        "win_pct": 0.683,
        "team_L10": "7-3",
        "curr_streak": "W2"
      }
    ]
  }
]
```

## Games Stats Aggregation Endpoint (Broken)

### `GET /api/games/stats?game_date=YYYY-MM-DD`
Intended to return full stats for a given date.

Current implementation issue:
- Route calls `fetch_games_with_stats(game_date=game_date)` but no such function exists in `backend/main.py` or imports.
- Calling this endpoint will raise a `NameError` at runtime.

Frontend guidance:
- Do not depend on this endpoint until backend implementation is completed.

## WebSocket

### `WS /ws`
Push channel for live game snapshots.

Behavior:
- Server accepts connection and stores socket in a connection manager.
- On each 5-second poll, server broadcasts full array payload (same shape as `GET /api/games`).
- In the websocket handler loop, server waits for incoming text from client (`await websocket.receive_text()`).

Client requirement:
- Send heartbeat text periodically or keepalive messages to avoid idle disconnect in environments that require activity.

Message payload shape:
- JSON-encoded `GameWithProbability[]`.

## CORS

Allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `https://pj09-sports-betting.vercel.app`

Methods/headers:
- All methods and headers allowed.

Credentials:
- `allow_credentials=True`
