"""
Computes win probabilities for each game based on the teams' records and the home team's record.
Uses a trained logistic regression model (ml/model.joblib) when available for in-progress games.

Structured output:
{
    "game_id": {
        "home_win_prob": 0.6,
        "away_win_prob": 0.4
    }
}
"""
from pathlib import Path
from typing import Any
import re

import pandas as pd

_ML_MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "xgboost_calibrated.joblib"
_wp_model = None

def _load_wp_model():
    """Load the win-probability model once; returns None if file missing."""
    global _wp_model
    if _wp_model is not None:
        return _wp_model
    if not _ML_MODEL_PATH.is_file():
        return None
    import joblib
    _wp_model = joblib.load(_ML_MODEL_PATH)
    return _wp_model

_SEC_PER_QUARTER = 720
_SEC_TOTAL_REGULATION = 2880
_SEC_OT = 300

def parse_status(status: str) -> tuple[int | None, int | None]:
    """
    Extract (period, seconds_remaining) from status string.
    Format: "{clock} - {period}" e.g. "40.2 - 4th", "1:23 - 4th", "7:07 - 3rd"
    Period: 1-4 for quarters, 5=OT, 6=2OT, etc. Seconds: remaining in entire game.
    """
    if not status or "Final" in status:
        return 4, 0
    if "Pregame" in status or "Scheduled" in status:
        return 1, _SEC_TOTAL_REGULATION
    if "Halftime" in status:
        return 2, _SEC_TOTAL_REGULATION // 2  # 1440
    if "Overtime" in status:
        return 5, _SEC_OT
    if "End of 1st" in status:
        return 2, _SEC_PER_QUARTER * 3
    if "End of 2nd" in status:
        return 3, _SEC_PER_QUARTER * 2
    if "End of 3rd" in status:
        return 4, _SEC_PER_QUARTER
    if "End of 4th" in status:
        return 4, 0

    match = re.match(r"(.+?)\s*-\s*(.+)", status.strip())
    if not match:
        return None, None

    clock_str, period_str = match.group(1).strip(), match.group(2).strip()

    # if game hasn't started yet, return period and seconds remaining for full game
    if re.search(r"\d{1,2}:\d{2}\s*(AM|PM)?", period_str, re.I):
        return 1, _SEC_TOTAL_REGULATION

    period_str_lower = period_str.lower()
    if period_str_lower in ("1st", "1"):
        period = 1
    elif period_str_lower in ("2nd", "2"):
        period = 2
    elif period_str_lower in ("3rd", "3"):
        period = 3
    elif period_str_lower in ("4th", "4"):
        period = 4
    else:
        ot_match = re.match(r"(\d*)ot", period_str_lower)
        if ot_match:
            period = 4 + int(ot_match.group(1) or 1)
        else:
            return None, None

    if ":" in clock_str:
        parts = clock_str.split(":")
        try:
            mins, secs = int(parts[0]), int(float(parts[1]) if parts[1] else 0)
            sec_left_in_q = mins * 60 + secs
        except (ValueError, IndexError):
            return None, None
    else:
        try:
            sec_left_in_q = int(float(clock_str))
        except ValueError:
            return None, None

    if period <= 4:
        full_quarters_left = 4 - period
        seconds_remaining = sec_left_in_q + full_quarters_left * _SEC_PER_QUARTER
        return period, seconds_remaining
    else:
        return period, sec_left_in_q

def calculate(
    home_score: int,
    away_score: int,
    home_wins: int,
    home_losses: int,
    away_wins: int,
    away_losses: int,
    home_l10_wins: int,
    away_l10_wins: int,
    status: str,
) -> tuple[float, float]:
    if status == "Final":
        home_win_prob = 0.0 if home_score < away_score else 100.0
        away_win_prob = 100.0 - home_win_prob
        return home_win_prob, away_win_prob

    model = _load_wp_model()
    if model is not None:
        _, seconds_remaining = parse_status(status)
        if seconds_remaining is None:
            print("Invalid status")
            return 0, 0
        FEATURE_COLS = ["SECONDS_REMAINING", "HOME_SCORE", "AWAY_SCORE", "HOME_WINS", "HOME_LOSSES", "AWAY_WINS", "AWAY_LOSSES", "HOME_L10_WINS", "AWAY_L10_WINS"]
        X = pd.DataFrame(
            [[seconds_remaining, home_score, away_score, home_wins, home_losses, away_wins, away_losses, home_l10_wins, away_l10_wins]],
            columns=FEATURE_COLS,
        )
        proba = model.predict_proba(X)[0]
        home_win_prob = float(100 * proba[1])
        away_win_prob = float(100 - home_win_prob)
        return home_win_prob, away_win_prob

    print("No model found")
    return 0, 0

def compute_win_probabilities(games: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    result = {}
    for game in games:
        game_id = game["game_id"]
        home_score = game["home_score"]
        away_score = game["away_score"]
        status = game["status"]
        home_wins = game["home_wins"]
        home_losses = game["home_losses"]
        away_wins = game["away_wins"]
        away_losses = game["away_losses"]
        home_l10_wins = game.get("home_l10_wins", 0)
        away_l10_wins = game.get("away_l10_wins", 0)

        home_win_prob, away_win_prob = calculate(
            home_score, away_score,
            home_wins, home_losses, away_wins, away_losses,
            home_l10_wins, away_l10_wins,
            status,
        )
        result[game_id] = {
            "home_win_prob": float(home_win_prob),
            "away_win_prob": float(away_win_prob),
        }
    return result


def _get_stat(stats: list, name: str) -> str | None:
    """Get displayValue for a stat by name."""
    for s in stats or []:
        if s.get("name") == name:
            return s.get("displayValue")
    return None


def _get_leader(leaders: list, stat: str) -> tuple[str | None, str | None]:
    """Get (name, value) for points/rebounds/assists leader. Value is displayValue string."""
    for entry in leaders or []:
        if entry.get("name") == stat and entry.get("leaders"):
            leader = entry["leaders"][0]
            name = leader.get("athlete", {}).get("fullName")
            val = leader.get("displayValue")
            return name, val
    return None, None


def _quarters_from_linescores(linescores: list) -> tuple[Any, Any, Any, Any]:
    """Extract Q1-Q4 from linescores. Returns (q1, q2, q3, q4) with 0 for missing."""
    by_period = {p.get("period"): p.get("value") for p in (linescores or []) if p.get("period") <= 4}
    return (
        by_period.get(1),
        by_period.get(2),
        by_period.get(3),
        by_period.get(4),
    )


def parse_game_data(event: dict[str, Any]) -> dict[str, Any] | None:
    """
    Parse game data from ESPN scoreboard API event.
    Returns dictionary with team names, scores, points per quarter, status, team leaders, abbreviations, records.
    """
    comps = event.get("competitions") or []
    if not comps:
        return None
    comp = comps[0]
    competitors = comp.get("competitors") or []
    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
    if not home or not away:
        return None

    status_obj = comp.get("status") or {}
    status = status_obj.get("type", {}).get("shortDetail") or status_obj.get("type", {}).get("description") or ""

    def _parse_records(records: list) -> tuple[int, int]:
        rec = next((r for r in (records or []) if r.get("name") == "overall" or r.get("type") == "total"), None)
        summary = (rec or {}).get("summary", "") or ""
        parts = summary.split("-")
        if len(parts) != 2:
            return 0, 0
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except ValueError:
            return 0, 0

    def _team(c: dict) -> dict:
        t = c.get("team") or {}
        stats_list = c.get("statistics") or c.get("stats") or []
        leaders = c.get("leaders") or []
        wins, losses = _parse_records(c.get("records"))
        pts_name, pts_val = _get_leader(leaders, "points")
        reb_name, reb_val = _get_leader(leaders, "rebounds")
        ast_name, ast_val = _get_leader(leaders, "assists")
        q1, q2, q3, q4 = _quarters_from_linescores(c.get("linescores"))
        return {
            "team_name": t.get("shortDisplayName") or t.get("name", ""),
            "city": t.get("location", ""),
            "abbreviation": t.get("abbreviation", ""),
            "wins": wins,
            "losses": losses,
            "score": int(c.get("score", 0) or 0),
            "q1": q1, "q2": q2, "q3": q3, "q4": q4,
            "reb": _get_stat(stats_list, "rebounds"),
            "ast": _get_stat(stats_list, "assists"),
            "fga": _get_stat(stats_list, "fieldGoalsAttempted"),
            "fgm": _get_stat(stats_list, "fieldGoalsMade"),
            "fta": _get_stat(stats_list, "freeThrowsAttempted"),
            "ftm": _get_stat(stats_list, "freeThrowsMade"),
            "points": _get_stat(stats_list, "points"),
            "three_pa": _get_stat(stats_list, "threePointFieldGoalsAttempted"),
            "three_pm": _get_stat(stats_list, "threePointFieldGoalsMade"),
            "leader_pts_name": pts_name, "leader_pts_val": pts_val,
            "leader_reb_name": reb_name, "leader_reb_val": reb_val,
            "leader_ast_name": ast_name, "leader_ast_val": ast_val,
        }

    h, a = _team(home), _team(away)

    def _team_slice(team: dict, prefix: str) -> dict:
        return {
            f"{prefix}_team": team["team_name"],
            f"{prefix}_city": team["city"],
            f"{prefix}_abbreviation": team["abbreviation"],
            f"{prefix}_wins": team["wins"],
            f"{prefix}_losses": team["losses"],
            f"{prefix}_score": team["score"],
            f"{prefix}_q1": team["q1"], f"{prefix}_q2": team["q2"],
            f"{prefix}_q3": team["q3"], f"{prefix}_q4": team["q4"],
            f"{prefix}_leader_pts_name": team["leader_pts_name"],
            f"{prefix}_leader_pts_val": team["leader_pts_val"],
            f"{prefix}_leader_reb_name": team["leader_reb_name"],
            f"{prefix}_leader_reb_val": team["leader_reb_val"],
            f"{prefix}_leader_ast_name": team["leader_ast_name"],
            f"{prefix}_leader_ast_val": team["leader_ast_val"],
            f"{prefix}_reb": team.get("reb"),
            f"{prefix}_ast": team.get("ast"),
            f"{prefix}_fga": team.get("fga"),
            f"{prefix}_fgm": team.get("fgm"),
            f"{prefix}_fta": team.get("fta"),
            f"{prefix}_ftm": team.get("ftm"),
            f"{prefix}_points": team.get("points"),
            f"{prefix}_3pa": team.get("three_pa"),
            f"{prefix}_3pm": team.get("three_pm"),
        }

    return {
        "game_id": event.get("id", ""),
        "status": status,
        **_team_slice(h, "home"),
        **_team_slice(a, "away"),
    }

def merge_gp(g: list[dict[str, Any]], p: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    """
    Appends home_win_prob and away_win_prob to each game in the list.
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