export interface Game {
  gameid: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  home_record: string;
  away_record: string;
  status: string;
}

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';