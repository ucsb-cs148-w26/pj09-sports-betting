from typing import Dict, List

def normalize_league_standings(data: dict) -> List[Dict]:
    """
    Normalize raw NBA league standings data into structured East and West standings.

    Each team entry includes basic identifying information, ranking, record, win percentage, 
    recent performance, and current streak.

    Args:
        data (dict): Raw response dictionary from the NBA API league
            standings endpoint (`LeagueStandings.get_dict()`).

    Returns:
        List[Dict]: A list containing a single dictionary with the following keys:
            - "east_standings" (List[Dict]): Ordered list of Eastern Conference teams
            - "west_standings" (List[Dict]): Ordered list of Western Conference teams

        Each team dictionary contains:
            - team_id (int)
            - team_city (str)
            - team_name (str)
            - conference (str)
            - rank (int)
            - record (str)
            - win_pct (float)
            - team_L10 (str)
            - curr_streak (str)
    """
    data_set = data["resultSets"][0]
    headers = data_set["headers"]
    rows = data_set["rowSet"]

    teams = []
    for row in rows:
      teams.append(dict(zip(headers,row)))

    east_standings = []
    west_standings = []
    for team in teams:
        team_data = {
            "team_id": team["TeamID"],
            "team_city": team["TeamCity"],
            "team_name": team["TeamName"],
            "conference": team["Conference"],
            "rank": team["PlayoffRank"],
            "record": team["Record"],
            "win_pct": team["WinPCT"],
            "team_L10": team["L10"],
            "curr_streak": team["strCurrentStreak"]
        }

        if team_data["conference"] == "East":
           east_standings.append(team_data)
        else:
           west_standings.append(team_data)
    
    league_standings = [
       {
          "east_standings": east_standings,
          "west_standings": west_standings
       }
    ]

    return league_standings