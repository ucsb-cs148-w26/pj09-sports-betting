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

# NBA stats API TeamID -> ESPN-style abbreviation (for matching scoreboard teams)
_NBA_TEAM_ID_TO_ABBREV = {
    1610612737: "ATL", 1610612738: "BOS", 1610612751: "BKN", 1610612766: "CHA",
    1610612741: "CHI", 1610612739: "CLE", 1610612742: "DAL", 1610612743: "DEN",
    1610612765: "DET", 1610612744: "GSW", 1610612745: "HOU", 1610612754: "IND",
    1610612746: "LAC", 1610612747: "LAL", 1610612763: "MEM", 1610612748: "MIA",
    1610612749: "MIL", 1610612750: "MIN", 1610612740: "NOP", 1610612752: "NYK",
    1610612760: "OKC", 1610612753: "ORL", 1610612755: "PHI", 1610612756: "PHX",
    1610612757: "POR", 1610612758: "SAC", 1610612759: "SAS", 1610612761: "TOR",
    1610612762: "UTA", 1610612764: "WAS",
}


def _parse_l10(l10_str: str) -> tuple[int, int]:
    """Parse L10 string like '7-3' or '4-6' into (wins, losses). Returns (0, 0) on failure."""
    if not l10_str or "-" not in l10_str:
        return 0, 0
    parts = l10_str.strip().split("-")
    if len(parts) != 2:
        return 0, 0
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return 0, 0


def _current_nba_season() -> str:
    """e.g. Oct 2025 -> '2025-26'; July 2025 -> '2025-26'."""
    today = date.today()
    year = today.year
    if today.month >= 10:
        return f"{year}-{str(year + 1)[-2:]}"
    return f"{year - 1}-{str(year)[-2:]}"


def fetch_standings_l10() -> dict[str, tuple[int, int]]:
    """
    Fetch league standings from NBA stats API and return mapping
    abbreviation -> (l10_wins, l10_losses). Uses current season.
    """
    abbrev_to_l10: dict[str, tuple[int, int]] = {}
    try:
        season = _current_nba_season()
        response = leaguestandings.LeagueStandings(season_nullable=season)
        data = response.get_dict()
        rs = data.get("resultSets") or []
        if not rs:
            return abbrev_to_l10
        headers = rs[0].get("headers") or []
        rows = rs[0].get("rowSet") or []
        team_id_idx = headers.index("TeamID") if "TeamID" in headers else -1
        l10_idx = headers.index("L10") if "L10" in headers else -1
        if team_id_idx < 0 or l10_idx < 0:
            return abbrev_to_l10
        for row in rows:
            if team_id_idx < len(row) and l10_idx < len(row):
                team_id = row[team_id_idx]
                l10_str = row[l10_idx] if isinstance(row[l10_idx], str) else ""
                abbrev = _NBA_TEAM_ID_TO_ABBREV.get(team_id)
                if abbrev:
                    abbrev_to_l10[abbrev] = _parse_l10(l10_str)
    except Exception as e:
        print(f"Standings L10 fetch failed: {e}")
    return abbrev_to_l10


def fetch_games_from_nba() -> list[dict[str, Any]]:
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    raw = resp.json()
    events = raw.get("events", [])
    result = []
    l10_by_abbrev = fetch_standings_l10()
    for event in events:
        payload = parse_game_data(event)
        if payload:
            home_abbrev = payload.get("home_abbreviation", "") or ""
            away_abbrev = payload.get("away_abbreviation", "") or ""
            h_w, h_l = l10_by_abbrev.get(home_abbrev, (0, 0))
            a_w, a_l = l10_by_abbrev.get(away_abbrev, (0, 0))
            payload["home_l10_wins"] = h_w
            payload["away_l10_wins"] = a_w
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
