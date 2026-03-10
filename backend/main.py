import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

import requests
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from util import (
    compute_win_probabilities,
    merge_gp,
    fetch_espn_lineups,
    fetch_standings_from_espn,
    fetch_full_game_stats,
    fetch_dashboard_games,
    get_player_props as fetch_player_props,

)
import state as app_state
from datetime import date as date_type, datetime
from zoneinfo import ZoneInfo
from database import (
    fetch_game_history,
    save_completed_games_to_db,
    past_game_row_to_dashboard_game,
    get_historical_team_stats,
    get_probability_history,
    append_probability_history,
    is_game_final,
)
from services.live_props.poller import props_poll_loop
from services.live_props.service import compute_live_props_snapshot
from services.live_props.store import get_snapshot, set_snapshot

async def update_games_and_probabilities():
    """
    Update the games and probabilities in the in-memory store and broadcast to WebSocket clients.
    Uses lightweight dashboard data for efficiency.
    """
    today = _today_isoformat_la()
    games = fetch_dashboard_games(game_date=today)
    probabilities = compute_win_probabilities(games)
    app_state.GAMES_STATE.clear()
    app_state.GAMES_STATE.extend(games)
    app_state.PROBABILITIES_STATE.clear()
    app_state.PROBABILITIES_STATE.update(probabilities)

    # Accumulate probability snapshots for win-probability graph
    for game in games:
        game_id = str(game["game_id"])
        if game_id not in probabilities:
            continue
        probs = probabilities[game_id]
        snapshot = {
            "clock": game.get("status", ""),
            "home_score": int(game.get("home_score", 0) or 0),
            "away_score": int(game.get("away_score", 0) or 0),
            "home_win_prob": probs["home_win_prob"],
            "away_win_prob": probs["away_win_prob"],
        }
        history = app_state.PROBABILITY_HISTORY.setdefault(game_id, [])
        # Skip exact duplicate consecutive snapshots
        if not history or history[-1] != snapshot:
            history.append(snapshot)
            # Cap history size
            if len(history) > app_state.MAX_PROB_HISTORY:
                del history[0]

    # Persist only snapshots added since last successful persistence.
    for game in games:
        game_id = str(game["game_id"])
        history = app_state.PROBABILITY_HISTORY.get(game_id, [])
        if not history:
            continue

        last_idx = app_state.LAST_PERSISTED_PROB_INDEX_BY_GAME.get(game_id, 0)
        # If history was capped, reset cursor safely.
        if last_idx > len(history):
            last_idx = len(history)

        if len(history) <= last_idx:
            continue

        new_snaps = history[last_idx:]
        await append_probability_history(game_id, new_snaps)
        app_state.LAST_PERSISTED_PROB_INDEX_BY_GAME[game_id] = len(history)

    result = merge_gp(games, probabilities)
    games_targets = manager.topic_connection_labels("games")
    print(
        f"[broadcast] topic=games payload=GameWithProbability[] games={len(result)} "
        f"subscribers={len(games_targets)} active_total={len(manager.active_connections)} "
        f"targets={games_targets}"
    )
    # Broadcast to games dashboard
    await manager.broadcast_to_topic("games", result)

    # Only add games if they are final and not already saved
    newly_final = [g for g in result if is_game_final(g) and g["game_id"] not in app_state.SAVED_FINAL_GAME_IDS]

    if newly_final:
        # get full game stats
        g = fetch_full_game_stats()
        probs = compute_win_probabilities(g)
        all_games_stats = merge_gp(g, probs)
        newly_final_ids = {str(g["game_id"]) for g in newly_final}
        
        # save full game stats only for newly final games
        to_save = [m for m in all_games_stats if str(m.get("game_id")) in newly_final_ids]
        print(f"to_save: {to_save}")
        await save_completed_games_to_db(to_save)

        # update in-memory store with finished game IDs
        for g in newly_final:
            app_state.SAVED_FINAL_GAME_IDS.add(g["game_id"])

async def update_subscribed_game_stats():
    """
    Fetch full stats ONLY for subscribed games and broadcast.
    """
    game_ids = get_subscribed_game_ids()

    if not game_ids:
        return
    try:
        # Fetch full detailed game stats
        games = fetch_full_game_stats()

        # Compute win probabilities
        probabilities = compute_win_probabilities(games)

        for game_id in game_ids:
            target = next(
                (g for g in games if g["game_id"] == game_id),
                None
            )
            if not target:
                continue

            merged = merge_gp([target], probabilities)[0]
            prob_hist = app_state.PROBABILITY_HISTORY.get(game_id, [])
            if not prob_hist:
                prob_hist = get_probability_history(game_id)
            merged["probability_history"] = list(prob_hist)

            topic = f"game:{game_id}"

            # Broadcast only to subscribers
            await manager.broadcast_to_topic(topic, merged)

            print(
                f"[broadcast] detailed topic={topic} "
                f"subs={manager.topic_size(topic)}"
            )

    except Exception as e:
        print(f"detailed update error: {e}")

async def poll_loop():
    """Poll the NBA API every 5 seconds and update the games and probabilities."""
    while True:
        try:
            await update_games_and_probabilities()
        except Exception as e:
            print(f"poll error: {e}")
        
        await asyncio.sleep(5)

# New poll loop       
async def detailed_poll_loop():
    """
    Poll detailed stats for subscribed games.
    """
    while True:
        try:
            await update_subscribed_game_stats()
        except Exception as e:
            print(f"detailed poll loop error: {e}")

        await asyncio.sleep(5)


def get_subscribed_game_ids() -> list[str]:
    """
    Returns list of subscribed game_ids from topics like 'game:{id}'
    """
    ids = []

    for topic in manager.topic_connections.keys():
        if topic.startswith("game:"):
            game_id = topic.split("game:")[1]
            if game_id:
                ids.append(game_id)

    return ids

class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()
        self.topic_connections: dict[str, set[WebSocket]] = {}
        self.connection_topics: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        # Keep existing clients working by defaulting to the aggregate stream.
        await self.subscribe(websocket, "games")
        print(
            f"[ws] connected client={self.connection_label(websocket)} "
            f"active_total={len(self.active_connections)}"
        )

    async def disconnect(self, websocket: WebSocket):
        topics = list(self.connection_topics.get(websocket, set()))
        for topic in topics:
            await self.unsubscribe(websocket, topic)
        self.connection_topics.pop(websocket, None)
        self.active_connections.discard(websocket)
        print(
            f"[ws] disconnected client={self.connection_label(websocket)} "
            f"active_total={len(self.active_connections)}"
        )

    async def subscribe(self, websocket: WebSocket, topic: str):
        if not topic:
            return
        self.topic_connections.setdefault(topic, set()).add(websocket)
        self.connection_topics.setdefault(websocket, set()).add(topic)
        print(
            f"[ws] subscribe client={self.connection_label(websocket)} "
            f"topic={topic} subscribers={self.topic_size(topic)}"
        )

    async def unsubscribe(self, websocket: WebSocket, topic: str):
        subscribers = self.topic_connections.get(topic)
        if not subscribers:
            return
        subscribers.discard(websocket)
        if not subscribers:
            self.topic_connections.pop(topic, None)

        topics = self.connection_topics.get(websocket)
        if topics:
            topics.discard(topic)
            if not topics:
                self.connection_topics.pop(websocket, None)
        print(
            f"[ws] unsubscribe client={self.connection_label(websocket)} "
            f"topic={topic} subscribers={self.topic_size(topic)}"
        )

    def topic_size(self, topic: str) -> int:
        return len(self.topic_connections.get(topic, set()))

    def connection_label(self, websocket: WebSocket) -> str:
        client = websocket.client
        if client:
            return f"{client.host}:{client.port}"
        return f"ws:{id(websocket)}"

    def topic_connection_labels(self, topic: str) -> list[str]:
        return [self.connection_label(c) for c in self.topic_connections.get(topic, set())]

    async def broadcast_to_topic(self, topic: str, payload: Any):
        subscribers = list(self.topic_connections.get(topic, set()))
        if not subscribers:
            return
        txt = json.dumps(payload)
        dead_connections: list[WebSocket] = []
        for c in subscribers:
            try:
                await c.send_text(txt)
            except Exception:
                dead_connections.append(c)
        for c in dead_connections:
            await self.disconnect(c)


manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    dashboard_task = asyncio.create_task(poll_loop())
    detailed_task = asyncio.create_task(detailed_poll_loop())
    props_task = asyncio.create_task(props_poll_loop(manager))
    try:
        yield
    finally:
        dashboard_task.cancel()
        detailed_task.cancel()
        props_task.cancel()
        try:
            await dashboard_task
            await detailed_task
            await props_task
        except asyncio.CancelledError:
            pass
        
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://pj09-sports-betting.vercel.app", "https://pj09-sports-betting-2enq4id18-kevins-projects-8b1f5231.vercel.app"],
    allow_origin_regex=r"^https://pj09-sports-betting(?:-[a-z0-9-]+)?\.vercel\.app$",
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
    print("games route hit")
    g = list(app_state.GAMES_STATE)
    p = dict(app_state.PROBABILITIES_STATE)
    
    # If in-memory store is empty (e.g., on first request), fetch fresh data
    if not g:
        try:
            today = _today_isoformat_la()
            g = fetch_dashboard_games(game_date=today)
            p = compute_win_probabilities(g)
            app_state.GAMES_STATE.extend(g)
            app_state.PROBABILITIES_STATE.update(p)
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    # Gracefully handle no games scenario
    if not g:
        return []
    
    return merge_gp(g, p)

def _today_isoformat_la() -> str:
    """Today's date in America/Los_Angeles, YYYY-MM-DD (matches games_by_date format)."""
    return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()


def _parse_date_param(value: str) -> date_type | None:
    """Parse date path param; accept YYYY-MM-DD or YYYYMMDD. Returns date or None."""
    if not value or not value.strip():
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


@app.get("/api/games/{date}")
async def games_by_date(date: str):
    """
    Returns games on date {date} with dashboard-viewable data only.
    - If date is today or in the future: fetches from ESPN for that date.
    - If date is in the past: fetches from database (completed games only).
    """
    try:
        parsed = _parse_date_param(date)
        if parsed is None:
            return []
        date_yyyy_mm_dd = parsed.isoformat()
        today_la = datetime.now(ZoneInfo("America/Los_Angeles")).date()
        use_espn = parsed >= today_la

        if use_espn:
            g = fetch_dashboard_games(game_date=date_yyyy_mm_dd)
            p = compute_win_probabilities(g)
            return merge_gp(g, p)
        else:
            days = await fetch_game_history(order="asc", date=date_yyyy_mm_dd)

            if not days or not days[0].get("games"):
                g = fetch_dashboard_games(game_date=date_yyyy_mm_dd)
                if not g:
                    return []
                p = compute_win_probabilities(g)
                return merge_gp(g, p)
                
            rows = days[0]["games"]
            g = [past_game_row_to_dashboard_game(row) for row in rows]
            p = {
                str(row["past_game_id"]): {
                    "home_win_prob": float(row.get("home_win_probability") or 0),
                    "away_win_prob": float(row.get("away_win_probability") or 0),
                }
                for row in rows
            }
            return merge_gp(g, p)
    except Exception as e:
        print(f"Error in games by date: {e}")
        return []

@app.get("/api/props/odds/{player_name}")
def get_player_props_odds(player_name: str):
    """
    Returns player PTS, REB, and AST props for a certain player.
    Also includes over/under lines from different bookmakers (platforms).
    """
    player_props = fetch_player_props(player_name)
    return player_props

# Standings route
@app.get("/api/standings")
def standings():
    """
    Retrieve current NBA league standings grouped by conference.
    """
    try:
        return fetch_standings_from_espn()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# Starting Lineups Route (ESPN-sourced)
@app.get("/api/v1/lineups/{game_date}")
def get_lineups(game_date: str):
    # Validate date format
    if not game_date or len(game_date) != 8 or not game_date.isdigit():
        return {
            "error": "Invalid date format. Use YYYYMMDD (e.g., '20260212')",
            "date": game_date,
            "games": []
        }

    try:
        return fetch_espn_lineups(game_date)
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout. ESPN may be slow or unavailable.",
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

# Game History Route (from database)
@app.get("/api/games/history")
async def game_history(
    order: str = "desc",
    limit: int | None = None,
    date: str | None = None,
):
    """
    Returns past game results from the database, sorted by date.

    Query params:
        order: 'desc' (newest first, default) or 'asc' (oldest first)
        limit: max number of results (optional)
        date:  'YYYY-MM-DD' — return only games on this date (optional)
    """
    try:
        days = await fetch_game_history(order=order, limit=limit, date=date)
        total_games = sum(len(d["games"]) for d in days)
        return {
            "total_days": len(days),
            "total_games": total_games,
            "order": order,
            "days": days,
        }
    except Exception as e:
        print(f"Error fetching game history: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# Endpoint for specific game using game_id
@app.get("/api/games/stats/{game_id}")
def single_game_stats(game_id: str):
    """
    Returns full normalized stats + win probability for ONE specific game.
    Uses full game data (not dashboard lightweight version).
    First checks in-memory dashboard store, then fetches full stats if needed.
    """
    # Check if game exists in dashboard store first
    g_dashboard = list(app_state.GAMES_STATE)
    game_today = any(game["game_id"] == game_id for game in g_dashboard)
    
    if not game_today:
        hist = get_historical_team_stats(game_id)
        if not hist:
            return {"error": "Game not found"}, 404
        # Try in-memory first (game just finished), fall back to database
        prob_hist = app_state.PROBABILITY_HISTORY.get(game_id, [])
        if not prob_hist:
            prob_hist = get_probability_history(game_id)
        hist["probability_history"] = list(prob_hist)
        return hist
    
    # Fetch full stats for this specific game
    try:
        g_full = fetch_full_game_stats()
        p = compute_win_probabilities(g_full)
        
        target = next((game for game in g_full if game["game_id"] == game_id), None)
        
        if not target:
            return {"error": "Invalid game_id"}, 404
        
        result = merge_gp([target], p)
        prob_hist = app_state.PROBABILITY_HISTORY.get(game_id, [])
        if not prob_hist:
            prob_hist = get_probability_history(game_id)
        result[0]["probability_history"] = list(prob_hist)
        print(result[0])
        return result[0]
    except Exception as e:
        print(f"Error fetching game stats: {e}")
        return {"error": "Failed to fetch game stats"}, 500
    
@app.get("/api/props")
def props(debug: bool = False):
    """
    Returns current live props snapshot.
    """
    if debug:
        return compute_live_props_snapshot(debug=True)

    snapshot = get_snapshot()
    if not snapshot.get("projections"):
        snapshot = compute_live_props_snapshot()
        set_snapshot(snapshot)
    return snapshot

  
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if not message:
                continue

            action = None
            topic = None
            try:
                payload = json.loads(message)
                if isinstance(payload, dict):
                    action = payload.get("action") or payload.get("type")
                    topic = payload.get("topic")
            except json.JSONDecodeError:
                # Ignore non-JSON heartbeat text.
                continue

            if action == "subscribe" and isinstance(topic, str):
                await manager.subscribe(websocket, topic)
                await websocket.send_json({"ok": True, "action": "subscribe", "topic": topic})
            elif action == "unsubscribe" and isinstance(topic, str):
                await manager.unsubscribe(websocket, topic)
                await websocket.send_json({"ok": True, "action": "unsubscribe", "topic": topic})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
