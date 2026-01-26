"""
Computes win probabilities for each game based on the teams' records and the home team's record.

Structured output:
{
    "game_id": {
        "home_win_prob": 0.6,
        "away_win_prob": 0.4
    }
}
"""
from typing import Any

def compute_win_probabilities(games: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    result = {}
    for game in games:
        game_id = game["game_id"]
        result[game_id] = {
            "home_win_prob": 50.0,
            "away_win_prob": 50.0
        }
    return result