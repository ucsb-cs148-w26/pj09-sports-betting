"""
In-memory store for live game state and win probabilities.

- Updated every 5s by the background poll task.
- Read by GET /games (and any other routes that need current state).
"""

from typing import Any

# Latest games list: same shape as your existing /games response.
games: list[dict[str, Any]] = []

# Win probabilities by game_id: { "game_id": { "home_win_prob": 0.6, "away_win_prob": 0.4 } }
probabilities: dict[str, dict[str, float]] = {}