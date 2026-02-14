# Database Reference

This backend includes a PostgreSQL helper module and a SQL schema file.

## Code Usage Status

- Connection/query utilities exist in `backend/database.py`.
- Current `backend/main.py` routes do not directly use database queries for live endpoints.
- Live game and probability data is currently in-memory.

## Connection Configuration

`backend/database.py` supports two modes:

1. Render-style URL:
- `DATABASE_URL` (parsed into host/port/database/user/password)

2. Local env vars fallback:
- `DB_HOST` (default `localhost`)
- `DB_PORT` (default `5432`)
- `DB_NAME` (default `sports_betting`)
- `DB_USER` (default `junhyungyoon`)
- `DB_PASSWORD` (default empty)

## SQL Schema (`backend/sports-betting-db.sql`)

### `user_info`
- `user_id INT PRIMARY KEY`
- `username VARCHAR(50) UNIQUE NOT NULL`
- `email VARCHAR(50) UNIQUE NOT NULL`
- `user_password VARCHAR(255) NOT NULL`
- `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

### `player_overall_info`
- `player_id INT PRIMARY KEY`
- Basic profile fields + season averages (`ppg`, `rpg`, `apg`, `spg`, `bpg`, shooting percentages)

### `current_game_info`
- `game_id INT PRIMARY KEY`
- Team names/scores, elapsed time, stadium, and win probabilities

### `past_game_info`
- Historical completed games with same shape as `current_game_info`

### `game_probability_history`
- `probability_id SERIAL PRIMARY KEY`
- `game_id`, `calculation_timestamp`, time context, score, home/away probabilities, model version
- Index: `idx_game_timestamp (game_id, calculation_timestamp)`

### `player_in_game_info`
- `player_in_game_id INT PRIMARY KEY`
- FK to `player_overall_info.player_id`
- FK to `current_game_info.game_id`
- Per-game counting stats

## Data Type Caveat

- Live API `game_id` in FastAPI responses is string-based (from ESPN payload).
- SQL schema defines game ids as `INT`.
- If persistence is added for ESPN ids, normalize id type consistently first.

## Helper API Surface (`database.py`)

- `execute_query(query, params=None, fetch_one=False)`
- `execute_insert(query, params=None)`
- `execute_update(query, params=None)`
- `test_connection()`
