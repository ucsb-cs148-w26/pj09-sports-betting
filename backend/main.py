from fastapi import FastAPI
from nba_api.live.nba.endpoints import scoreboard
from mock_data import MOCK_GAMES
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

# Backend health route
@app.get("/health")
def health():
    return {"health": "healthy"}

# Game stats route
@app.get("/stats")
def stats():
    return{"Home score": "125"}

# Live Games Route
@app.get("/api/games")
def games():
    """
    Returns a list of todays NBA Games

    Each game includes:
    - game_id: Unique game id
    - home_team: Home team name
    - away_team: Away team name
    - home_score: Home team score
    - away_score: Away team score
    - home_record: Home team record (w-l)
    - away_record: Away team record (w-l)
    - status: Current game status
    - quarter: Current quarter
    - clock - Time remaining on the quarter
    - hitChance - Team 1's chance of winning

    If there are no live games, there is mock data that is sent when the api is called
    """
    data = scoreboard.ScoreBoard()
    data = data.get_dict()

    games = data["scoreboard"]["games"]


    result = []
    for game in games:
        home = game["homeTeam"]
        away = game["awayTeam"]

        result.append(
            {
                "game_id": game["gameId"],
                "home_team": home["teamName"],
                "away_team": away["teamName"],
                "home_score": home["score"],
                "away_score": away["score"],
                "home_record": f'{home["wins"]}-{home["losses"]}',
                "away_record": f'{away["wins"]}-{away["losses"]}',
                "status": game["gameStatusText"],
                "quarter": game.get("period"),
                "clock": game.get("gameClock"),
                "hitChance": random.uniform(0, 1),  # Placeholder for hit chance
            }
        )

    if len(result) == 0:
        result = MOCK_GAMES
    
    return result