'''
This script pulls all the games from the 2022-2023, 2023-2024, and 2024-2025 NBA seasons
and pulls the game IDs from every reagular season game from the perspective of the home
team (nba_api -> leaguegamefinder). Then for every game we pull the play by play data
directly from the nba.com CDN (content delivery network) playbyplay endpoint and for each
play we store a row in our final dataset that contains:
  
  GAME_ID | SEASON | PERIOD | SECONDS_REMAINING | HOME_SCORE | AWAY_SCORE | POINT_DIFF | HOME_WINS | HOME_LOSSES | AWAY_WINS | AWAY_LOSSES | HOME_L10_WINS | HOME_L10_LOSSES | AWAY_L10_WINS | AWAY_L10_LOSSES | HOME_WIN

The data for each game is then stored in a CSV in ml/datasets
This data is intended to be use to train the win probability model with the 2 seasons intended
to be training data and the last season to be test data.

  GAME_ID, SEASON = Identifiers
  PERIOD, SECONDS_REMAINING, HOME_SCORE, AWAY_SCORE, PINT_DIFF = Features
  HOME_WIN = Target (label)
'''

import os
import time

import pandas as pd
import requests
from nba_api.stats.endpoints import leaguegamefinder
import threading

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
}


def parse_clock_to_seconds(clock: str | None) -> int | None:
    if not clock:
        return None
    s = str(clock).strip()
    if s.startswith("PT") and s.endswith("S"):
        # PT11M32.00S
        s = s[2:-1]
        minutes = 0
        seconds = 0
        if "M" in s:
            mins, rest = s.split("M", 1)
            minutes = int(mins) if mins.isdigit() else 0
            s = rest
        if s:
            try:
                seconds = int(float(s))
            except ValueError:
                seconds = 0
        return minutes * 60 + seconds
    if ":" in s:
        try:
            mins, secs = s.split(":", 1)
            return int(mins) * 60 + int(float(secs))
        except ValueError:
            return None
    return None


def build_training_table(
    game_id: str,
    season: str,
    home_win: int,
    home_record: tuple[int, int],
    away_record: tuple[int, int],
    home_l10: tuple[int, int],
    away_l10: tuple[int, int],
) -> pd.DataFrame:
    url = f"https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{game_id}.json"
    print(url)
    exit()
    data = requests.get(url, headers=HEADERS, timeout=20).json()
    print(data)
    
    pbp_df = pd.DataFrame(data["game"]["actions"])
    pbp_df["PERIOD"] = pd.to_numeric(pbp_df["period"], errors="coerce")
    pbp_df["CLOCK_SEC"] = pbp_df["clock"].apply(parse_clock_to_seconds)

    pbp_df["HOME_SCORE"] = pd.to_numeric(pbp_df["scoreHome"], errors="coerce").ffill()
    pbp_df["AWAY_SCORE"] = pd.to_numeric(pbp_df["scoreAway"], errors="coerce").ffill()

    def total_seconds_remaining(row: pd.Series) -> int | None:
        if pd.isna(row["PERIOD"]) or pd.isna(row["CLOCK_SEC"]):
            return None
        period = int(row["PERIOD"])
        clock_sec = int(row["CLOCK_SEC"])
        if period <= 4:
            return (4 - period) * 12 * 60 + clock_sec
        return clock_sec

    pbp_df["SECONDS_REMAINING"] = pbp_df.apply(total_seconds_remaining, axis=1)
    pbp_df["POINT_DIFF"] = pbp_df["HOME_SCORE"] - pbp_df["AWAY_SCORE"]

    out = pbp_df[
        ["PERIOD", "SECONDS_REMAINING", "HOME_SCORE", "AWAY_SCORE", "POINT_DIFF"]
    ].copy()
    out.insert(0, "GAME_ID", game_id)
    out.insert(1, "SEASON", season)
    out["HOME_WIN"] = int(home_win)
    out["HOME_WINS"], out["HOME_LOSSES"] = home_record[0], home_record[1]
    out["AWAY_WINS"], out["AWAY_LOSSES"] = away_record[0], away_record[1]
    out["HOME_L10_WINS"], out["HOME_L10_LOSSES"] = home_l10[0], home_l10[1]
    out["AWAY_L10_WINS"], out["AWAY_L10_LOSSES"] = away_l10[0], away_l10[1]
    return out.dropna(
        subset=["PERIOD", "SECONDS_REMAINING", "HOME_SCORE", "AWAY_SCORE"]
    )


def fetch_games_for_season(season: str) -> pd.DataFrame:
    # stats.nba.com can reset connections; add headers and retry.
    for attempt in range(1, 4):
        try:
            lgf = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable="Regular Season",
                league_id_nullable="00",
            )
            return lgf.get_data_frames()[0]
        except Exception as exc:
            print(f"LeagueGameFinder failed (attempt {attempt}/3): {exc}")
            time.sleep(2 * attempt)
    raise RuntimeError("LeagueGameFinder failed after 3 attempts.")

all_rows = []
lock = threading.Lock()

def scrape_season(season: str) -> None:
    games_df = fetch_games_for_season(season)
    games_df["SEASON"] = season
    games_df["IS_HOME"] = games_df["MATCHUP"].str.contains("vs", case=False, na=False)

    # Get home teams, rename TEAM_ID to HOME_TEAM_ID
    home_teams = games_df[games_df["IS_HOME"]][["GAME_ID", "TEAM_ID"]].rename(
        columns={"TEAM_ID": "HOME_TEAM_ID"}
    )
    # Get away teams, rename TEAM_ID to AWAY_TEAM_ID
    away_teams = games_df[~games_df["IS_HOME"]][["GAME_ID", "TEAM_ID"]].rename(
        columns={"TEAM_ID": "AWAY_TEAM_ID"}
    )
    # Merge home and away teams on GAME_ID
    games_with_teams = home_teams.merge(away_teams, on="GAME_ID")

    home_rows = games_df[games_df["IS_HOME"]].copy()
    home_rows["HOME_WIN"] = (home_rows["WL"] == "W").astype(int)
    games_index = home_rows.merge(games_with_teams, on="GAME_ID")[
        ["GAME_ID", "SEASON", "GAME_DATE", "HOME_WIN", "HOME_TEAM_ID", "AWAY_TEAM_ID"]
    ].drop_duplicates("GAME_ID")
    games_index["GAME_DATE"] = pd.to_datetime(games_index["GAME_DATE"])
    games_index = games_index.sort_values("GAME_DATE").reset_index(drop=True)

    # Cumulative W-L and last-10: records each team had *before* this game
    team_records: dict[int, tuple[int, int]] = {}
    team_l10: dict[int, list[int]] = {}  # 1=win, 0=loss, oldest to newest
    total_games = len(games_index)
    print(f"\nSeason {season}: {total_games} games (sorted by date)")

    for idx, row in games_index.iterrows():
        game_id = row["GAME_ID"]
        home_id = int(row["HOME_TEAM_ID"])
        away_id = int(row["AWAY_TEAM_ID"])
        home_record = team_records.get(home_id, (0, 0))
        away_record = team_records.get(away_id, (0, 0))
        home_recent = team_l10.get(home_id, [])
        away_recent = team_l10.get(away_id, [])
        home_l10_record = (sum(home_recent), len(home_recent) - sum(home_recent))
        away_l10_record = (sum(away_recent), len(away_recent) - sum(away_recent))

        print(f"[{idx + 1}/{total_games}] Fetching {game_id}")
        try:
            training_df = build_training_table(
                game_id=game_id,
                season=row["SEASON"],
                home_win=int(row["HOME_WIN"]),
                home_record=home_record,
                away_record=away_record,
                home_l10=home_l10_record,
                away_l10=away_l10_record,
            )
            if not training_df.empty:
                with lock:
                    all_rows.append(training_df)
        except Exception as exc:
            print(f"Failed {game_id}: {exc}")

        # Update cumulative records after this game
        hw, hl = team_records.get(home_id, (0, 0))
        aw, al = team_records.get(away_id, (0, 0))
        if row["HOME_WIN"]:
            team_records[home_id] = (hw + 1, hl)
            team_records[away_id] = (aw, al + 1)
        else:
            team_records[home_id] = (hw, hl + 1)
            team_records[away_id] = (aw + 1, al)

        # Update last-10 (append result, keep only last 10)
        home_result = 1 if row["HOME_WIN"] else 0
        away_result = 0 if row["HOME_WIN"] else 1
        team_l10[home_id] = (team_l10.get(home_id, []) + [home_result])[-10:]
        team_l10[away_id] = (team_l10.get(away_id, []) + [away_result])[-10:]


if __name__ == "__main__":
    seasons = ["2021-22", "2022-23", "2023-24", "2024-25"]
    output_csv = "../datasets/training_dataset_4szn_wp.csv"

    threads = []
    for season in seasons:
        thread = threading.Thread(target=scrape_season, args=(season,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    if all_rows:
        full_df = pd.concat(all_rows, ignore_index=True)
        full_df = full_df.sort_values(["SEASON", "GAME_ID"]).reset_index(drop=True)
        os.makedirs("../datasets", exist_ok=True)
        full_df.to_csv(output_csv, index=False)
        print(f"Saved {len(full_df)} rows to {output_csv}")
    else:
        print("No rows generated.")
