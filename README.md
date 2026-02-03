# Sports Betting

## Description

Our app is designed to provide live win probability modeling and player performance projections for daily NBA Matchups. The system ingests live NBA game data and runs predictive models to broadcast live odds updates to all users in real time. Anyone from sports bettors to casual fans are able to perform pre-game analysis and monitor probabilities throughout each game. This design is meant to provide a clear and interactive view of probabilities and statistics in one clean dashboard.

Access the website at https://pj09-sports-betting.vercel.app/

## Audience

Our ideal users are casual NBA fans and sports bettors who want a real-time view of matchup odds and player performance projections.

## Tech Stack

This project employs frontend with Next.js due to its ease of use and compatibility with common backend services, routing, and Vercel for deployment. For our backend, we decided to use FastAPI because of its built-in support for WebSockets, which would allow real-time retrieval of game state updates to update live probabilities.

#### Frontend

- Next.js (React, TypeScript)
- Tailwind CSS

#### Backend

- FastAPI (Python)

#### Data & Modeling

- Pandas + NumPy
- scikit-learn

#### Database

- PostgreSQL
- Redis

### User Roles

#### NBA Fans and Sports Bettors

The first user role that we are targeting are NBA fans who are actively watching games in real time and want to have another layer of information that they are able to access during the games. This information would consist of live probabilities as well as player performance and projections. More specifically, these users would mainly be focused on viewing live NBA games and matchups, player performance projects for each game, and real-time win probabilities for the games as well.

The next user role would be sports bettors. They would have a similar role to your average NBA fan but would be more inclined to focusing on the player projects and the real-time win projections of the games. This would help them make a better informed decision for their bets. This platform helps users accomplish their goals by ingesting live NBA game data, running predictive models to broadcast live odds updates to all users in real time all in on dashboard. This allows users to stay up to date and informed throughout the game for all their needs.

## Group Members

| Name           | GitHub ID       |
| -------------- | --------------- |
| Logan Melgoza  | @logan-melgoza  |
| Raymond Xie    | @POWERTRICEPS   |
| Ali Shahid     | @Mala-Patke     |
| Kevin Yang     | @lem0000ns      |
| Timothy Nguyen | @timmywin       |
| Alvin Chan     | @alvinlovescode |
| Junhyung Yoon  | @Neamal         |
| Jay Yeung      | @JayYeung5      |

# Installation

## Prerequisites

Before setting up the project, make sure you have the following installed:

- **Git** (for cloning the repository)
- **Python 3.10+** (recommended for FastAPI and `nba_api`)
- **Node.js 18+** and **npm** (for the Next.js frontend)
- **pip** (comes with Python)
- _(Optional)_ Python’s built-in `venv` for virtual environments

You can verify installations with:

```bash
git --version
python3 --version
node --version
npm --version
```

## Dependencies

### Backend (Python / FastAPI)

- **FastAPI** – backend web framework
- **Uvicorn** – ASGI server for running FastAPI
- **Public ESPN API** – used to fetch NBA data (standings, games, etc.)
- **uvloop** – faster event loop (optional, used by Uvicorn)
- **pydantic** – data validation and serialization
- **PostgreSQL** - historical game data storage

### Frontend (Next.js)

- **Next.js** – React framework for frontend
- **React** – UI library
- **TypeScript** – type safety and better developer experience

All backend dependencies are listed in `backend/requirements.txt`.  
All frontend dependencies are listed in `frontend/package.json`.

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/ucsb-cs148-w26/pj09-sports-betting.git
cd pj09-sports-betting
```

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\Activate    # Windows

pip install -r requirements.txt
```

Run the backend server:

```bash
uvicorn main:app --reload
```

The backend will be available at:

```
http://localhost:8000
```

### 3. Frontend setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```
http://localhost:3000
```

# Functionality

This application provides real-time and near–real-time NBA analytics, including:

- **League Standings**
  - View current Eastern and Western Conference standings
  - Teams are ordered by conference rank
- **Live Games**
  - View active NBA games and scores
  - Backend polls NBA live data and broadcasts updates
- **(Planned) Win Probability & Player Props**
  - Live win probability modeling
  - Player over/under probability projections

Typical usage flow:

1. Start backend and frontend servers
2. Navigate to the frontend dashboard
3. View standings, live games, and evolving game data in one place

# Known Problems

- **Win Probability Modeling**  
  Win probability is not currently implemented and the numbers shown are generated randomly.

- **Blocking NBA API calls**  
  Some NBA API calls are synchronous and may briefly block the event loop during fetches.

If something breaks, check:

- `backend/main.py`
- `backend/services/`
- Network requests to ESPN API

# Contributing

Fork it!

Create your feature branch:

```bash
git checkout -b my-new-feature
```

Commit your changes:

```bash
git commit -am "Add some feature"
```

Push to the branch:

```bash
git push origin my-new-feature
```

Submit a pull request 🎉

# License

This project is licensed under the **MIT License**.
