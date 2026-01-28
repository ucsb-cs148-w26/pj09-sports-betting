from fastapi import FastAPI
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguestandings
from mock_data import MOCK_GAMES
from standings import normalize_league_standings

app = FastAPI()

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
            }
        )

    if len(result) == 0:
        result = MOCK_GAMES
    
    return result

# Standings route
@app.get("/api/standings")
def standings():
    """
    Retrieve current NBA league standings grouped by conference.

    This endpoint fetches the latest NBA league standings using the
    `nba_api` statistics endpoint, normalizes the raw response data,
    and returns structured standings for both the Eastern and Western
    Conferences.

    The response includes team rankings, records, win percentages,
    recent performance, and current streak information, and is intended
    to be consumed by frontend components displaying standings tables.

    Returns:
        List[Dict]: A list containing a single dictionary with:
            - "east_standings" (List[Dict]): Eastern Conference standings
            - "west_standings" (List[Dict]): Western Conference standings
    """
    response = leaguestandings.LeagueStandings()
    data = response.get_dict()
    normalized_standings = normalize_league_standings(data)
    return normalized_standings