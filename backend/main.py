import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from datetime import date

import requests

from nba_api.stats.endpoints import leaguestandings, scoreboardv2

from util import compute_win_probabilities, parse_game_data, merge_gp
import state as app_state

from standings import normalize_league_standings

def fetch_games_from_nba() -> list[dict[str, Any]]:
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

async def update_games_and_probabilities():
    """Update the games and probabilities in the in-memory store and broadcast to the WebSocket clients."""
    games = fetch_games_from_nba()
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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


# Live Games Route (from live scoreboard)
@app.get("/api/games")
def games():
    """
    Returns current games and win probabilities (from in-memory store).
    Updated every 5s by background poll. Use for initial load + refresh.
    """
    g = list(app_state.games)
    p = dict(app_state.probabilities)
    if not g:
        g = fetch_games_from_nba()
        p = compute_win_probabilities(g)
        app_state.games.extend(g)
        app_state.probabilities.update(p)
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
  
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
