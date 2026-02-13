# Backend Documentation

This folder contains implementation-focused documentation for the `backend/` service.

## Documents

- `api-reference.md`: HTTP and WebSocket endpoints, request/response shapes, and behavior.
- `frontend-contracts.md`: frontend-facing API contracts with TypeScript interfaces.
- `backend-architecture.md`: runtime architecture, polling model, state flow, and dependencies.
- `database.md`: SQL schema reference from `backend/sports-betting-db.sql` and how it maps to backend code.
- `probability.md`: win probability model behavior, status parsing, and output semantics.
- `known-issues.md`: current backend defects and integration caveats.

## Quick Start

1. Install deps:
   - `pip install -r backend/requirements.txt`
2. Run API (from `backend/`):
   - `uvicorn main:app --reload`
3. Key runtime behaviors:
   - Background poll updates live game state every 5 seconds.
   - `GET /api/games` returns merged game data + probabilities from in-memory cache.
   - `GET /api/standings` fetches live standings from `nba_api`.
   - `WS /ws` broadcasts full live game snapshots to connected clients.

## Notes

- CORS is currently configured for:
  - `http://localhost:3000`
  - `http://127.0.0.1:3000`
  - `https://pj09-sports-betting.vercel.app`
- See `api-reference.md` for known endpoint issues that frontend should guard against.
