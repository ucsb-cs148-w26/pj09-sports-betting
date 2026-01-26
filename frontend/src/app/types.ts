export interface Game {
  game_id: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  home_record: string;
  away_record: string;
  status: string;
  home_win_prob: number | null;
  away_win_prob: number | null;
}

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';