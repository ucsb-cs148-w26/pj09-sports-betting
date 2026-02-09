import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from datetime import date

import requests

from nba_api.stats.endpoints import leaguestandings, scoreboardv2

from util import compute_win_probabilities, parse_game_data, parse_dashboard_game_data, merge_gp
import state as app_state

from standings import normalize_league_standings

def fetch_games_from_nba() -> list[dict[str, Any]]:
    """
    Fetch full game data from ESPN API with all stats.
    Used by /api/games/stats endpoint for detailed statistics.
    """
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    raw = resp.json()
    events = raw.get("events", [])
    result = []
    for event in events:
        payload = parse_game_data(event)
        if payload:
            result.append(payload)
    return result

def fetch_dashboard_games() -> list[dict[str, Any]]:
    """
    Fetch lightweight game data from ESPN API for dashboard display.
    Returns only: game_id, status, team names/abbr, records, scores.
    Used by /api/games endpoint.
    """
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    raw = resp.json()
    events = raw.get("events", [])
    result = []
    for event in events:
        payload = parse_dashboard_game_data(event)
        if payload:
            result.append(payload)
    return result

async def update_games_and_probabilities():
    """
    Update the games and probabilities in the in-memory store and broadcast to WebSocket clients.
    Uses lightweight dashboard data for efficiency.
    """
    games = fetch_dashboard_games()
    probabilities = compute_win_probabilities(games)
    app_state.games.clear()
    app_state.games.extend(games)
    app_state.probabilities.clear()
    app_state.probabilities.update(probabilities)
    
    result = merge_gp(games, probabilities)
    print(f"Broadcasting {len(result)} games to {len(manager.active_connections)} clients\n")
    await manager.broadcast_json(result)

async def poll_loop():
    """Poll the NBA API every 5 seconds and update the games and probabilities."""
    while True:
        try:
            await update_games_and_probabilities()
        except Exception as e:
            print(f"poll error: {e}")
        
        await asyncio.sleep(5)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, payload: Any):
        txt = json.dumps(payload)
        for c in self.active_connections:
            try:
                await c.send_text(txt)
            except Exception:
                pass


manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for the FastAPI app."""
    poll_task = asyncio.create_task(poll_loop())
    try:
        yield
    finally:
        poll_task.cancel()
        try:
            await poll_task
        except asyncio.CancelledError:
            pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://pj09-sports-betting.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"health": "healthy"}


@app.get("/stats")
def stats():
    return {"Home score": "125"}


# Live Games Route (dashboard view - lightweight)
@app.get("/api/games")
def games():
    """
    Returns current games with dashboard-viewable data only:
    - game_id, status
    - team names, abbreviations, records (wins/losses)
    - current scores
    - win probabilities
    
    Data is from in-memory store updated every 5s by background poll.
    Gracefully handles no available games by returning empty list.
    """
    g = list(app_state.games)
    p = dict(app_state.probabilities)
    
    # If in-memory store is empty (e.g., on first request), fetch fresh data
    if not g:
        try:
            g = fetch_dashboard_games()
            p = compute_win_probabilities(g)
            app_state.games.extend(g)
            app_state.probabilities.update(p)
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    # Gracefully handle no games scenario
    if not g:
        return []
    
    return merge_gp(g, p)


# Games with full stats (ScoreboardV2)
@app.get("/api/games/stats")
def games_stats(game_date: str | None = None):
    """
    Returns games with full stats (pts, reb, ast, tov, fg%, ft%, 3pt%, points per quarter).
    Optional query param: game_date (YYYY-MM-DD). Defaults to today.
    """
    results = fetch_games_with_stats(game_date=game_date)
    return {"results": results}


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

# Endpoint for specific game using game_id (returns full stats)
@app.get("/api/games/stats/{game_id}")
def single_game_stats(game_id: str):
    """
    Returns full normalized stats + win probability for ONE specific game.
    Uses full game data (not dashboard lightweight version).
    First checks in-memory dashboard store, then fetches full stats if needed.
    """
    # Check if game exists in dashboard store first
    g_dashboard = list(app_state.games)
    game_exists = any(game["game_id"] == game_id for game in g_dashboard)
    
    if not game_exists:
        return {"error": "Invalid game_id"}, 404
    
    # Fetch full stats for this specific game
    try:
        g_full = fetch_games_from_nba()
        p = compute_win_probabilities(g_full)
        
        target = next((game for game in g_full if game["game_id"] == game_id), None)
        
        if not target:
            return {"error": "Invalid game_id"}, 404
        
        result = merge_gp([target], p)
        return result[0]
    except Exception as e:
        print(f"Error fetching game stats: {e}")
        return {"error": "Failed to fetch game stats"}, 500
  
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
