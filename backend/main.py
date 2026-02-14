import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from datetime import date, datetime

import requests

from nba_api.stats.endpoints import leaguestandings, scoreboardv2

from util import compute_win_probabilities, parse_game_data, parse_dashboard_game_data, merge_gp
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

# Starting Lineups Route
@app.get("/api/v1/lineups/{game_date}")
def get_lineups(game_date: str):
    # Validate date format
    if not game_date or len(game_date) != 8 or not game_date.isdigit():
        return {
            "error": "Invalid date format. Use YYYYMMDD (e.g., '20260212')",
            "date": game_date,
            "games": []
        }
    
    # Construct URL for NBA stats endpoint
    url = f"https://stats.nba.com/js/data/leaders/00_daily_lineups_{game_date}.json"
    
    # Required headers to bypass 403 Forbidden
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
        "Connection": "keep-alive",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        raw_data = resp.json()
        
        # Parse and structure the response
        structured_lineups = parse_lineup_data(raw_data, game_date)
        return structured_lineups
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Lineups not available yet for this date
            return {
                "date": game_date,
                "message": "Starting lineups not yet available for this date. Lineups are typically posted ~30 minutes before tipoff.",
                "games": []
            }
        else:
            return {
                "error": f"HTTP {e.response.status_code}: {str(e)}",
                "date": game_date,
                "games": []
            }
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout. NBA stats server may be slow or unavailable.",
            "date": game_date,
            "games": []
        }
    except Exception as e:
        print(f"Error fetching starting lineups: {e}")
        return {
            "error": str(e),
            "date": game_date,
            "games": []
        }


def parse_lineup_data(raw_data: dict, game_date: str) -> dict:
    """
    Parse raw NBA lineup data into structured format.
    
    Args:
        raw_data: Raw JSON from NBA stats endpoint
        game_date: Date string (YYYYMMDD)
    
    Returns:
        Structured lineup data matching acceptance criteria
    """
    games = []
    
    # Extract teams data from raw response
    # NBA's structure may vary, so we handle multiple possible formats
    teams_data = raw_data.get("teams", []) or raw_data.get("resultSets", [])
    
    if isinstance(teams_data, list) and len(teams_data) > 0:
        # Group teams by game
        games_dict = {}
        
        for team_data in teams_data:
            # Extract team information
            team_info = {
                "team_name": team_data.get("team_name") or team_data.get("teamName") or "",
                "team_abbreviation": team_data.get("team_abbreviation") or team_data.get("teamTricode") or team_data.get("abbr") or "",
                "starters": []
            }
            
            # Extract starters (usually 5 players)
            starters_data = team_data.get("starters", []) or team_data.get("players", [])
            
            for player in starters_data[:5]:  # Ensure only 5 starters
                starter = {
                    "name": player.get("player_name") or player.get("playerName") or player.get("name") or "Unknown",
                    "position": player.get("position") or player.get("pos") or "",
                    "player_id": str(player.get("player_id") or player.get("playerId") or player.get("id") or "")
                }
                team_info["starters"].append(starter)
            
            # Try to extract game_id and group by matchup
            game_id = team_data.get("game_id") or team_data.get("gameId") or ""
            
            if game_id:
                if game_id not in games_dict:
                    games_dict[game_id] = {
                        "game_id": game_id,
                        "home_team": None,
                        "away_team": None
                    }
                
                # Determine if home or away (based on indicator in data)
                is_home = team_data.get("home_away") == "home" or team_data.get("isHome") == True
                
                if is_home:
                    games_dict[game_id]["home_team"] = team_info
                else:
                    games_dict[game_id]["away_team"] = team_info
        
        # Convert dict to list and filter out incomplete games
        games = [
            game for game in games_dict.values() 
            if game["home_team"] and game["away_team"]
        ]
    
    # Check for confirmed lineups status
    lineup_status = raw_data.get("LINEUP_STATUS") or raw_data.get("lineupStatus") or "unknown"
    confirmed = lineup_status.lower() == "confirmed" if isinstance(lineup_status, str) else False
    
    return {
        "date": game_date,
        "lineup_status": "confirmed" if confirmed else "projected",
        "games": games,
        "total_games": len(games)
    }


# Endpoint for specific game using game_id
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
