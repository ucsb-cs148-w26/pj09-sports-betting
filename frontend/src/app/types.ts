export interface Game {
  game_id: string;
  status: string;

  home_team: string;
  home_city: string;
  home_abbreviation: string;
  home_wins: number;
  home_losses: number;
  home_score: number;
  home_q1: number | null;
  home_q2: number | null;
  home_q3: number | null;
  home_q4: number | null;
  home_leader_pts_name: string | null;
  home_leader_pts_val: string | null;
  home_leader_reb_name: string | null;
  home_leader_reb_val: string | null;
  home_leader_ast_name: string | null;
  home_leader_ast_val: string | null;
  home_reb: string | null;
  home_ast: string | null;
  home_fga: string | null;
  home_fgm: string | null;
  home_fta: string | null;
  home_ftm: string | null;
  home_points: string | null;
  home_3pa: string | null;
  home_3pm: string | null;

  away_team: string;
  away_city: string;
  away_abbreviation: string;
  away_wins: number;
  away_losses: number;
  away_score: number;
  away_q1: number | null;
  away_q2: number | null;
  away_q3: number | null;
  away_q4: number | null;
  away_leader_pts_name: string | null;
  away_leader_pts_val: string | null;
  away_leader_reb_name: string | null;
  away_leader_reb_val: string | null;
  away_leader_ast_name: string | null;
  away_leader_ast_val: string | null;
  away_reb: string | null;
  away_ast: string | null;
  away_fga: string | null;
  away_fgm: string | null;
  away_fta: string | null;
  away_ftm: string | null;
  away_points: string | null;
  away_3pa: string | null;
  away_3pm: string | null;

  home_win_prob?: number | null;
  away_win_prob?: number | null;
}

export type ConnectionStatus =
  | "connected"
  | "disconnected"
  | "connecting"
  | "error";
