# Frontend Contracts

This document defines frontend-facing contracts derived from current backend implementation.

## TypeScript Types

```ts
export interface GameWithProbability {
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

  home_win_prob: number | null; // percent scale [0,100]
  away_win_prob: number | null; // percent scale [0,100]
}

export interface TeamStanding {
  team_id: number;
  team_city: string;
  team_name: string;
  conference: "East" | "West";
  rank: number;
  record: string;
  win_pct: number;
  team_L10: string;
  curr_streak: string;
}

export interface LeagueStandingsItem {
  east_standings: TeamStanding[];
  west_standings: TeamStanding[];
}

export type LeagueStandingsResponse = LeagueStandingsItem[];
```

## REST Contracts

### `GET /api/games`
- Response: `GameWithProbability[]`
- Poll-safe for frontend refresh.

### `GET /api/games/stats/{game_id}`
- Response on success: `GameWithProbability`
- Response on missing `game_id`: non-standard error behavior; frontend should defensively handle unexpected response shape.

### `GET /api/standings`
- Response: `LeagueStandingsResponse`

## WebSocket Contract

### Endpoint
- `ws://<host>/ws`

### Server-to-client event
- Message type: text frame containing JSON string.
- Parsed payload: `GameWithProbability[]`

### Client-to-server expectation
- Backend currently waits for incoming text frames in a loop.
- Frontend should send periodic heartbeat text (for example every 20-30s) to keep connection behavior predictable.

## Contract Caveats

- `home_win_prob`/`away_win_prob` use percentage scale (`0` to `100`), not normalized probability (`0` to `1`).
- Some stats/leader fields may be `null` when source feed omits data.
- `game_id` is treated as string in responses.
- `/api/games/stats?game_date=...` is currently non-functional and should not be integrated.
