import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from mock_data import MOCK_GAMES
from nba_api.live.nba.endpoints import scoreboard

from probabilities import compute_win_probabilities
import state as app_state

def fetch_games_from_nba() -> list[dict[str, Any]]:
    """Sync: fetch scoreboard, transform to our game shape. Uses mock when no games."""
    raw = scoreboard.ScoreBoard().get_dict()
    games = raw.get("scoreboard", {}).get("games", [])
    result = []
    for g in games:
        home = g["homeTeam"]
        away = g["awayTeam"]
        result.append({
            "game_id": g["gameId"],
            "home_team": home["teamName"],
            "away_team": away["teamName"],
            "home_score": home["score"],
            "away_score": away["score"],
            "home_record": f'{home["wins"]}-{home["losses"]}',
            "away_record": f'{away["wins"]}-{away["losses"]}',
            "status": g["gameStatusText"],
        })
    if not result:
        result = MOCK_GAMES
    return result

def merge_gp(g: list[dict[str, Any]], p: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    """
    Merge games and probabilities into a single list of dictionaries.

    Structured output:
    [
        {
            "game_id": "game-123",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "home_score": 123,
            "away_score": 123,
            "home_record": "28-16",
            "away_record": "26-18",
            "status": "Final",
            "home_win_prob": 0.6,
            "away_win_prob": 0.4,
        },
        ...
    ]
    """
    result = []
    for game in g:
        game_id = game["game_id"]
        row = {**game, "home_win_prob": None, "away_win_prob": None}
        if game_id in p:
            row["home_win_prob"] = p[game_id]["home_win_prob"]
            row["away_win_prob"] = p[game_id]["away_win_prob"]
        result.append(row)
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

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"health": "healthy"}


@app.get("/stats")
def stats():
    return {"Home score": "125"}


# Live Games Route
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
