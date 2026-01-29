from models.schemas import Game
from datetime import datetime

"""
Transforms raw NBA live API game dictionaries into our internal Game schema.

The NBA API returns deeply nested dictionaries with many fields we don't need.
This function extracts only the fields required by our frontend and standardizes
their names and types using the Pydantic Game model.

Input: one element from raw["scoreboard"]["games"]
Output: Game(BaseModel) used across the backend
"""

def transform_data(g: dict) -> Game:
    home = g["homeTeam"]
    away = g["awayTeam"]

    return Game(
        game_id = g["gameId"],
        game_date = datetime.fromisoformat(g["gameTimeUTC"].replace("Z", "")),
        home_team = home["teamName"],
        away_team = away["teamName"],
        home_score = int(home["score"]),
        away_score = int(away["score"]),
        home_record=f'{home["wins"]}-{home["losses"]}',
        away_record=f'{away["wins"]}-{away["losses"]}',
        status = g["gameStatusText"]

    )