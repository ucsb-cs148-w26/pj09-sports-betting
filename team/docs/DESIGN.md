## Architecture Diagram

```mermaid
flowchart TB
    U[User Browser]
    FE[Next.js Frontend<br/>Games / Game Details / Props / Info]
    BE[FastAPI Backend]
    WS[WebSocket /ws Topics<br/>games, game:{id}, props]
    MEM[In-Memory App State<br/>games, probs, history, props snapshot]
    DB[(PostgreSQL<br/>past_game_info, past_game_stats,<br/>game_probability_history)]
    ESPN[ESPN APIs<br/>scoreboard, summary, standings, roster]
    NBA[nba_api<br/>season/player tables]
    ODDS[SportsGameOdds API<br/>player prop odds]
    MODELS[Local Models<br/>wp_lr.joblib, pts/reb/ast joblib]

    U --> FE
    FE -->|HTTP REST| BE
    FE <-->|WebSocket| WS
    WS --> BE

    BE --> MEM
    BE --> DB
    DB --> BE

    BE --> ESPN
    BE --> NBA
    BE --> ODDS
    BE --> MODELS
    MODELS --> BE
```

## Overview of System Architecture

### Frontend (Next.js/React)

- The frontend is built with Next.js + React + TypeScript and includes:
  - Live games dashboard (`/`)
  - Date-based games view (`/on/[id]`)
  - Per-game detail page with live probability graph (`/games/[id]`)
  - Live props page (`/props`)
  - Info/help page (`/info`)
- The frontend consumes backend data through:
  - HTTP for initial page data and historical/date queries
  - WebSockets for real-time updates (`games`, `game:{id}`, and `props` topics)
- A shared client-side provider manages live game list updates and standings state.

### Backend (FastAPI)

- The backend serves REST endpoints for games, standings, game details, lineups, game history, props snapshot, and odds lookup.
- The backend manages topic-based WebSocket subscriptions at `/ws`.
- On startup, the backend runs background poll loops:
  - Dashboard game updates every 5 seconds
  - Detailed subscribed game updates every 5 seconds
  - Player props snapshot updates every 30 seconds
- Data is sourced from ESPN APIs, `nba_api`, SportsGameOdds, and local ML model artifacts.

### Database (PostgreSQL on Render)

- PostgreSQL stores historical completed game data and win-probability timeline snapshots.
- Current live state is primarily maintained in memory for low-latency updates.
- Historical endpoints pull from Postgres first (with ESPN fallback in some flows).

### ML Models

- Win probability predictions use a locally loaded model (`wp_lr.joblib`).
- Live props projections use stat-specific models (`pts_model.joblib`, `reb_model.joblib`, `ast_model.joblib`).
- Model training and experimentation assets are kept in the `ml/` notebooks/scripts.

## Summary of Important Team Decisions

- Chose Next.js + React + TypeScript for a fast UI development workflow and straightforward Vercel deployment.
- Chose FastAPI for clean REST APIs and simple WebSocket support for live updates.
- Implemented topic-based WebSocket streams to avoid over-sending detailed game data to all clients.
- Used ESPN APIs as the primary live game feed, while still using `nba_api` where useful (season/player table fallbacks and related features).
- Added background polling architecture in backend to keep frontend clients lightweight and stateless.
- Used Postgres persistence for completed games and probability history, while keeping active game state in memory.
- Deployed frontend to Vercel and backend/database to Render.

## UX Considerations

### User Flow

- The user lands on the Games page and sees live/upcoming matchups with current scores and win probabilities.
- The user can open a specific game to view deeper stats, leaders, quarter breakdowns, and the win-probability timeline.
- The user can browse by date to inspect past/future schedules (`/on/[id]`).
- The user can open Props to view projected PTS/REB/AST values and inspect available sportsbook odds by player.
- Standings and status indicators are visible to provide context while comparing games and props.

### Real-Time Behavior

- Live game cards and standings refresh through a combination of initial HTTP fetch + WebSocket updates.
- Detailed game pages subscribe to game-specific topics for focused updates.
- Props page subscribes to the `props` topic and reflects the latest backend snapshot.
