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
import random

# TODO: Implement actual win probability calculation based on given stats
def calculate(home_score: int, away_score: int, home_record: str, away_record: str, status: str) -> tuple[float, float]:
    if status == "Final":
        home_win_prob = 0 if home_score < away_score else 100
        away_win_prob = 100 - home_win_prob
    else:
        home_win_prob = int(100 * random.random())
        away_win_prob = 100 - home_win_prob
    return home_win_prob, away_win_prob

def compute_win_probabilities(games: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    result = {}
    for game in games:
        game_id, home_score, away_score, home_record, away_record, status = game["game_id"], game["home_score"], game["away_score"], game["home_record"], game["away_record"], game["status"]
        home_win_prob, away_win_prob = calculate(home_score, away_score, home_record, away_record, status)
        result[game_id] = {
            "home_win_prob": home_win_prob,
            "away_win_prob": away_win_prob
        }
    return result