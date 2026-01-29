from pydantic import BaseModel
from datetime import datetime

class Game(BaseModel):
    game_id: int
    game_date: datetime
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    home_record: str
    away_record: str


# Potential schema for live game stats 
'''
class liveGameStats(BaseModel):
    game_id: int 
    quarter: int
    time_remaining: str
    home_score: int
    away_score: int
'''
